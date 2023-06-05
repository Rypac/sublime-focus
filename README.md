# Sublime Focus

A configurable, per-window Distraction Free mode plugin for Sublime Text.

## Contents

- [Installation](#installation)
- [Commands](#commands)
- [Key Bindings](#keybindings)

## Installation

### Package Control

1. Install [Package Control](https://packagecontrol.io)
2. Run `Package Control: Add Repository` in the Command Palette
3. Add the repository: `https://github.com/Rypac/sublime-focus.git`
4. Run `Package Control: Install Package` in the Command Palette
5. Install `sublime-focus`

### Manual

1. Select the `Settings > Browse Packages…` menu item
2. Browse up a directory and then into the `Installed Packages/` directory
3. Download [`Focus.sublime-package`](https://github.com/Rypac/sublime-focus/releases/latest/download/Focus.sublime-package) and copy it into the `Installed Packages/` directory

### Clone Repository

1. Select the `Settings > Browse Packages…` menu item
2. Within the `Packages/` directory, clone the repository:

    ```
    git clone https://github.com/Rypac/sublime-focus.git Focus
    ```

## Commands

| **Command**                         | **Description**                         |
| ----------------------------------- | --------------------------------------- |
| **View: Toggle Focus Mode**         | Toggle focus mode for the active window |
| **Preferences: Focus Settings**     | Edit plugin settings                    |
| **Preferences: Focus Key Bindings** | Edit plugin key bindings                |

## Key Bindings

To avoid potential conflicts, this plugin does not enable key bindings by default.

The following is an example that uses a key binding to toggle focus mode for the active window.

```json
[
    {
        "keys": ["primary+k", "primary+f"],
        "command": "toggle_focus_mode"
    }
]
```
