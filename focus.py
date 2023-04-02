import sublime
import sublime_plugin


def plugin_loaded():
    focus_settings = sublime.load_settings("Focus.sublime-settings")
    focus_settings.add_on_change("focus_mode", update_focus_mode_window_settings)

    df_settings = sublime.load_settings("Distraction Free.sublime-settings")
    df_settings.add_on_change("focus_mode", update_focus_mode_view_settings)


def plugin_unloaded():
    focus_settings = sublime.load_settings("Focus.sublime-settings")
    focus_settings.clear_on_change("focus_mode")

    df_settings = sublime.load_settings("Distraction Free.sublime-settings")
    df_settings.clear_on_change("focus_mode")

    for window in sublime.windows():
        if window.settings().has("focus_mode_state"):
            exit_focus_mode(window)


def update_focus_mode_window_settings():
    settings = sublime.load_settings("Focus.sublime-settings")

    for window in sublime.windows():
        if window.settings().has("focus_mode_state"):
            apply_focus_mode_window_settings(window, settings)


def update_focus_mode_view_settings():
    settings = sublime.load_settings("Distraction Free.sublime-settings").to_dict()

    for window in sublime.windows():
        if not window.settings().has("focus_mode_state"):
            continue
        
        for view in window.views():
            view.settings().update(settings)


def enter_focus_mode(window: sublime.Window):
    for view in window.views(include_transient=True):
        enter_view_focus_mode(view)

    window.settings()["focus_mode_state"] = {
        "minimap": window.is_minimap_visible(),
        "side_bar": window.is_sidebar_visible(),
        "status_bar": window.is_status_bar_visible(),
        "tabs": window.get_tabs_visible(),
    }

    focus_settings = sublime.load_settings("Focus.sublime-settings")
    apply_focus_mode_window_settings(window, focus_settings)


def apply_focus_mode_window_settings(window: sublime.Window, settings: sublime.Settings):
    window.set_tabs_visible(settings.get("show_tabs", False))
    window.set_status_bar_visible(settings.get("show_status_bar", False))
    window.set_sidebar_visible(settings.get("show_side_bar", False))
    window.set_minimap_visible(settings.get("show_minimap", False))


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

    focus_settings = sublime.load_settings("Distraction Free.sublime-settings").to_dict()

    view_settings["focus_mode_state"] = {
        key: view_settings.get(key) for key in focus_settings
    }

    view_settings.update(focus_settings)


def exit_view_focus_mode(view: sublime.View):
    view_settings = view.settings()

    if (pre_focus_state := view_settings.get("focus_mode_state")) is not None:
        view_settings.update(pre_focus_state)
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
