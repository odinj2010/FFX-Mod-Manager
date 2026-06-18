# FFX Mod Manager v2.3.0 - The Extensible Plugin API Update

This release introduces a fully refactored, namespace-isolated plugin system designed for public and third-party plugin development. It includes new developer hooks, dynamic UI hot-reloads, installation safety features, and compiler automation.

---

## 🚀 Key Features

### 🛠️ Isolated Plugin Namespace & Package Imports
*   **Collision Prevention**: Dynamically loads plugin modules inside a protected package namespace (`sys.modules[f"plugin_{dir_name}"]`). Developers can now safely use standard relative package imports (e.g. `from . import helper`) without crashing or clashing with other installed plugins.
*   **System Cache Purges**: Re-installing or updating a plugin now purges all corresponding cached modules from Python's memory, ensuring developers can test their code changes instantly on reload without restarting the mod manager.

### 🔄 Plugin Lifecycle Hooks & API Events
*   **Resource Cleanup Hook (`on_unload`)**: Added a lifecycle callback method `on_unload()`. When a plugin is deleted or reinstalled, it can stop daemon threads, close socket/WebSocket connections, and release global hotkey listeners to prevent memory and thread leaks.
*   **Mod Event Listener (`on_mods_refreshed`)**: Added an event callback that triggers `plugin.on_mods_refreshed()` whenever the manager scans, enables, disables, or changes the load order priority of active mods.

### 📥 Bulletproof Installation Safeguards
*   **Process Unlocker**: Before updating or reinstalling a plugin, the manager automatically detects if the plugin's background tracker process is still active. FFXMM terminates the tracker process first to release Windows file locks, preventing silent directory deletions or `PermissionError` installation failures.

### ⚡ Auto-Discovering Tracker Compiler
*   **PyInstaller Automation**: The builder utility (`compile_mod_manager.py`) now scans the `plugins/` directory, discovers all background overlays (`tracker.py`), compiles them into standalone `tracker.exe` binaries, and moves them to their respective folders.
*   **Out-of-the-Box Compatibility**: Both Achievements and Walkthrough overlays now ship with pre-compiled `tracker.exe` files, allowing them to run on gamers' PCs without requiring a system Python installation.

---
*Thank you for being part of the FFX modding community! Report any issues on our GitHub page.*
