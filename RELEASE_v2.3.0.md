# FFX Mod Manager v2.3.0 - The Extensible Plugin API & Manager Update

This release introduces a fully refactored, namespace-isolated plugin system designed for public and third-party plugin development. It includes new developer hooks, dynamic UI hot-reloads, installation safety features, compiler automation, and a dedicated installed plugins manager.

---

## 🚀 Key Features

### 🎛️ Plugin-Specific Settings Sub-Tabs
*   **Settings Isolation**: Re-architected both the Walkthrough and Achievements plugins to support dedicated, self-contained **⚙️ Settings** sub-tabs using a `ttk.Notebook` switcher. This cleans up primary interface panels and groups options cleanly.
*   **Custom Overlay Options**: Added inputs to configure overlay positioning (Left-Half, Right-Half, Top-Half, Bottom-Half), transparency/opacity levels, HUD scale, and trigger hotkeys. All settings are serialized to a local `overlay_config.json` file.
*   **Dynamic Settings Reloading**: Upgraded the background Achievements overlay tracker to monitor `overlay_config.json` changes during gameplay using file modification timestamp polling (`os.path.getmtime`). Saved setting updates are instantly loaded and applied in-game without restarting the tracker.
*   **Overlay Scaling**: Achievements overlay text sizes, icons, cards, and canvas progress bars now scale proportionally based on the selected HUD scale value.

### 📦 Installed Plugins Manager
*   **Notebook Layout**: Refactored the Mod Manager's Plugin Browser to support a double-tabbed layout:
    *   **Plugin Directory**: Browse and download all downloadable/installable plugins from the remote registry.
    *   **Installed Plugins**: Lists all currently installed plugins parsed locally from `plugin.json` descriptors on disk, including custom or local plugins not listed in the remote directory.
*   **Toggle Enable / Disable**: Users can toggle a plugin's status (**🔴 Disable** / **🟢 Enable**) dynamically. Disabling a plugin prevents it from loading or executing at startup and removes its sidebar navigation tab while keeping its files intact.
*   **Plugin Deletion**: Added a **🗑️ Delete** action that prompts for confirmation, automatically terminates any active background overlay trackers to prevent handle locks, and cleanly removes all plugin files from disk.

### 🛠️ Isolated Plugin Namespace & Package Imports
*   **Collision Prevention**: Dynamically loads plugin modules inside a protected package namespace (`sys.modules[f"plugin_{dir_name}"]`). Developers can now safely use standard relative package imports (e.g. `from . import helper`) without crashing or clashing with other installed plugins.
*   **System Cache Purges**: Re-installing or updating a plugin now purges all corresponding cached modules from Python's memory, ensuring developers can test their code changes instantly on reload without restarting the mod manager.

### 🔄 Plugin Lifecycle Hooks & API Events
*   **Resource Cleanup Hook (`on_unload`)**: Added a lifecycle callback method `on_unload()`. When a plugin is deleted or reinstalled, it can stop daemon threads, close socket/WebSocket connections, and release global hotkey listeners to prevent memory and thread leaks.
*   **Mod Event Listener (`on_mods_refreshed`)**: Added an event callback that triggers `plugin.on_mods_refreshed()` whenever the manager scans, enables, disables, or changes the load order priority of active mods.

### 📥 Bulletproof Installation Safeguards
*   **Process Unlocker**: Before updating, reinstalling, or deleting a plugin, the manager automatically detects if the plugin's background tracker process is still active. FFXMM terminates the tracker process first to release Windows file locks, preventing silent directory deletions or `PermissionError` installation failures.

### ⚡ Auto-Discovering Tracker Compiler
*   **PyInstaller Automation**: The builder utility (`compile_mod_manager.py`) now scans the `plugins/` directory, discovers all background overlays (`tracker.py`), compiles them into standalone `tracker.exe` binaries, and copies them to both the release build folder (`dist/plugins/...`) and active development folders (`plugins/...`) for seamless testing.
*   **Out-of-the-Box Compatibility**: Both Achievements and Walkthrough overlays now ship with pre-compiled `tracker.exe` files, allowing them to run on gamers' PCs without requiring a system Python installation.

---
*Thank you for being part of the FFX modding community! Report any issues on our GitHub page.*
