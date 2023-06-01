from __future__ import annotations

import sublime
from sublime import Settings, View, Window
from sublime_plugin import EventListener, WindowCommand
from typing import Any


FOCUS_MODE_KEY = "focus_mode_state"


focus_mode_settings: dict[str, Any] = {}
distraction_free_settings: dict[str, Any] = {}


def plugin_loaded():
    focus_settings = load_focus_settings()
    focus_settings.add_on_change("focus_mode", update_focus_mode_window_settings)

    df_settings = load_distraction_free_settings()
    df_settings.add_on_change("focus_mode", update_focus_mode_view_settings)

    focus_mode_settings.update(focus_settings.to_dict())
    distraction_free_settings.update(df_settings.to_dict())


def plugin_unloaded():
    focus_settings = load_focus_settings()
    focus_settings.clear_on_change("focus_mode")

    df_settings = load_distraction_free_settings()
    df_settings.clear_on_change("focus_mode")

    for window in sublime.windows():
        if window.template_settings().has(FOCUS_MODE_KEY):
            exit_focus_mode(window)

    focus_mode_settings.clear()
    distraction_free_settings.clear()


def load_focus_settings() -> Settings:
    return sublime.load_settings("Focus.sublime-settings")


def load_distraction_free_settings() -> Settings:
    return sublime.load_settings("Distraction Free.sublime-settings")


def update_focus_mode_window_settings():
    focus_mode_settings.clear()
    focus_mode_settings.update(load_focus_settings().to_dict())

    for window in sublime.windows():
        if window.template_settings().has(FOCUS_MODE_KEY):
            apply_focus_mode_settings(window)


def update_focus_mode_view_settings():
    distraction_free_settings.clear()
    distraction_free_settings.update(load_distraction_free_settings().to_dict())

    for window in sublime.windows():
        if not window.template_settings().has(FOCUS_MODE_KEY):
            continue

        for view in window.views():
            view.settings().update(distraction_free_settings)


def enter_focus_mode(window: Window):
    for view in window.views(include_transient=True):
        enter_view_focus_mode(view)

    window.template_settings()[FOCUS_MODE_KEY] = {
        "show_minimap": window.is_minimap_visible(),
        "show_side_bar": window.is_sidebar_visible(),
        "show_status_bar": window.is_status_bar_visible(),
        "show_tabs": window.get_tabs_visible(),
    }

    apply_focus_mode_settings(window)


def apply_focus_mode_settings(window: Window):
    settings = {
        **focus_mode_settings,
        **(window.project_data() or {}).get("settings", {}).get("Focus", {}),
    }

    window.set_minimap_visible(settings.get("show_minimap", False))
    window.set_sidebar_visible(settings.get("show_side_bar", False))
    window.set_status_bar_visible(settings.get("show_status_bar", False))
    window.set_tabs_visible(settings.get("show_tabs", False))


def exit_focus_mode(window: Window):
    for view in window.views(include_transient=True):
        exit_view_focus_mode(view)

    pre_focus_state = window.template_settings().get(FOCUS_MODE_KEY, {})

    window.set_minimap_visible(pre_focus_state.get("show_minimap", True))
    window.set_sidebar_visible(pre_focus_state.get("show_side_bar", True))
    window.set_status_bar_visible(pre_focus_state.get("show_status_bar", True))
    window.set_tabs_visible(pre_focus_state.get("show_tabs", True))

    window.template_settings().erase(FOCUS_MODE_KEY)


def enter_view_focus_mode(view: View):
    view_settings = view.settings()

    if view_settings.has(FOCUS_MODE_KEY):
        return

    view_settings[FOCUS_MODE_KEY] = {
        key: value
        for key in distraction_free_settings
        if (value := view_settings.get(key)) is not None
    }

    view_settings.update(distraction_free_settings)
    view.set_status(FOCUS_MODE_KEY, "Focus Mode")


def exit_view_focus_mode(view: View):
    view_settings = view.settings()

    if (pre_focus_state := view_settings.get(FOCUS_MODE_KEY)) is None:
        return

    view_settings.update(pre_focus_state)
    view_settings.erase(FOCUS_MODE_KEY)
    view.erase_status(FOCUS_MODE_KEY)


class FocusModeListener(EventListener):
    def on_new(self, view: View):
        if (window := view.window()) and window.template_settings().has(FOCUS_MODE_KEY):
            enter_view_focus_mode(view)

    def on_new_window(self, window: Window):
        if window.template_settings().has(FOCUS_MODE_KEY):
            exit_focus_mode(window)

    def on_load(self, view: View):
        if (window := view.window()) and window.template_settings().has(FOCUS_MODE_KEY):
            enter_view_focus_mode(view)

    def on_pre_move(self, view: View):
        if (window := view.window()) and window.template_settings().has(FOCUS_MODE_KEY):
            exit_view_focus_mode(view)

    def on_post_move(self, view: View):
        if (window := view.window()) and window.template_settings().has(FOCUS_MODE_KEY):
            enter_view_focus_mode(view)

    def on_load_project(self, window: Window):
        if window.template_settings().has(FOCUS_MODE_KEY):
            apply_focus_mode_settings(window)

    def on_post_save_project(self, window: Window):
        if window.template_settings().has(FOCUS_MODE_KEY):
            apply_focus_mode_settings(window)


class ToggleFocusModeCommand(WindowCommand):
    def run(self):
        if not self.window.template_settings().has(FOCUS_MODE_KEY):
            enter_focus_mode(self.window)
        else:
            exit_focus_mode(self.window)

    def description(self) -> str:
        return (
            "Enter Focus Mode"
            if not self.window.template_settings().has(FOCUS_MODE_KEY)
            else "Exit Focus Mode"
        )
