import sublime
import sublime_plugin


def plugin_unloaded():
    for window in sublime.windows():
        if window.settings().has("focus_mode_state"):
            exit_focus_mode(window)


def enter_focus_mode(window: sublime.Window):
    for view in window.views(include_transient=True):
        enter_view_focus_mode(view)

    pre_focus_state = {
        "minimap": window.is_minimap_visible(),
        "sidebar": window.is_sidebar_visible(),
        "status_bar": window.is_status_bar_visible(),
        "tabs": window.get_tabs_visible(),
    }

    window.set_tabs_visible(False)
    window.set_status_bar_visible(False)
    window.set_sidebar_visible(False)
    window.set_minimap_visible(False)

    window.settings().set("focus_mode_state", pre_focus_state)


def exit_focus_mode(window: sublime.Window):
    for view in window.views(include_transient=True):
        exit_view_focus_mode(view)

    pre_focus_state = window.settings().get("focus_mode_state", {})

    window.set_minimap_visible(pre_focus_state.get("minimap", True))
    window.set_sidebar_visible(pre_focus_state.get("sidebar", True))
    window.set_status_bar_visible(pre_focus_state.get("status_bar", True))
    window.set_tabs_visible(pre_focus_state.get("tabs", True))

    window.settings().erase("focus_mode_state")


def enter_view_focus_mode(view: sublime.View):
    view_settings = view.settings()

    if view_settings.has("focus_mode_state"):
        return

    focus_settings = sublime.load_settings("Distraction Free.sublime-settings")

    pre_focus_state = {}

    for key, value in focus_settings.to_dict().items():
        pre_focus_state[key] = view_settings.get(key)
        view_settings.set(key, value)

    view_settings.set("focus_mode_state", pre_focus_state)


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
