import sublime
import sublime_plugin


def plugin_loaded():
    load_focus_settings().add_on_change("focus_mode", update_window_settings)
    load_distraction_free_settings().add_on_change("focus_mode", update_view_settings)


def plugin_unloaded():
    load_focus_settings().clear_on_change("focus_mode")
    load_distraction_free_settings().clear_on_change("focus_mode")

    for window in sublime.windows():
        if window.settings().has("focus_mode_state"):
            exit_focus_mode(window)


def load_focus_settings() -> sublime.Settings:
    return sublime.load_settings("Focus.sublime-settings")


def load_distraction_free_settings() -> sublime.Settings:
    return sublime.load_settings("Distraction Free.sublime-settings")


def update_window_settings():
    focus_settings = load_focus_settings()

    for window in sublime.windows():
        if window.settings().has("focus_mode_state"):
            apply_focus_mode_settings(window, focus_settings)


def update_view_settings():
    distraction_free_settings = load_distraction_free_settings().to_dict()

    for window in sublime.windows():
        if not window.settings().has("focus_mode_state"):
            continue

        for view in window.views():
            view.settings().update(distraction_free_settings)


def enter_focus_mode(window: sublime.Window):
    for view in window.views(include_transient=True):
        enter_view_focus_mode(view)

    window.settings()["focus_mode_state"] = {
        "minimap": window.is_minimap_visible(),
        "side_bar": window.is_sidebar_visible(),
        "status_bar": window.is_status_bar_visible(),
        "tabs": window.get_tabs_visible(),
    }

    apply_focus_mode_settings(window, settings=load_focus_settings())


def apply_focus_mode_settings(window: sublime.Window, settings: sublime.Settings):
    window.set_minimap_visible(settings.get("show_minimap", False))
    window.set_sidebar_visible(settings.get("show_side_bar", False))
    window.set_status_bar_visible(settings.get("show_status_bar", False))
    window.set_tabs_visible(settings.get("show_tabs", False))


def exit_focus_mode(window: sublime.Window):
    for view in window.views(include_transient=True):
        exit_view_focus_mode(view)

    pre_focus_state = window.settings().get("focus_mode_state", {})

    window.set_minimap_visible(pre_focus_state.get("minimap", True))
    window.set_sidebar_visible(pre_focus_state.get("side_bar", True))
    window.set_status_bar_visible(pre_focus_state.get("status_bar", True))
    window.set_tabs_visible(pre_focus_state.get("tabs", True))

    window.settings().erase("focus_mode_state")


def enter_view_focus_mode(view: sublime.View):
    view_settings = view.settings()

    if view_settings.has("focus_mode_state"):
        return

    distraction_free_settings = load_distraction_free_settings().to_dict()

    view_settings["focus_mode_state"] = {
        key: value
        for key in distraction_free_settings
        if (value := view_settings.get(key)) is not None
    }

    view_settings.update(distraction_free_settings)


def exit_view_focus_mode(view: sublime.View):
    view_settings = view.settings()

    if (pre_focus_state := view_settings.get("focus_mode_state")) is None:
        return

    distraction_free_settings = load_distraction_free_settings().to_dict()

    for key in distraction_free_settings:
        if (value := pre_focus_state.get(key)) is not None:
            view_settings.set(key, value)
        else:
            view_settings.erase(key)

    view_settings.erase("focus_mode_state")


class FocusModeListener(sublime_plugin.EventListener):
    def on_new(self, view: sublime.View):
        if (window := view.window()) is None:
            return

        if window.settings().has("focus_mode_state"):
            enter_view_focus_mode(view)

    def on_load(self, view: sublime.View):
        if (window := view.window()) is None:
            return

        if window.settings().has("focus_mode_state"):
            enter_view_focus_mode(view)
        else:
            exit_view_focus_mode(view)


class EnterFocusModeCommand(sublime_plugin.WindowCommand):
    def run(self):
        enter_focus_mode(self.window)

    def is_visible(self) -> bool:
        return not self.window.settings().has("focus_mode_state")


class ExitFocusModeCommand(sublime_plugin.WindowCommand):
    def run(self):
        exit_focus_mode(self.window)

    def is_visible(self) -> bool:
        return self.window.settings().has("focus_mode_state")


class ToggleFocusModeCommand(sublime_plugin.WindowCommand):
    def run(self):
        if not self.window.settings().has("focus_mode_state"):
            enter_focus_mode(self.window)
        else:
            exit_focus_mode(self.window)
