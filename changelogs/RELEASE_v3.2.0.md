# Spira Mod Manager Changelog - v3.2.0

## UI Layout and Configuration Updates

### Enhancements
*   **Split Import Button Layout**: Redesigned the mod import controls on the main dashboard to use a split button. Clicking the main button starts a standard single-file import, while clicking the arrow dropdown offers options for both single imports and bulk imports.
*   **Multi-Game Mod Wizard**: Updated the mod creation wizard dialog to support choosing the target game (FFX or FFX-2), ensuring custom mod structures are correctly prepared under their respective directory scopes (`ffx_data` or `ffx-2_data`).

## Core System & Path Operations
*   **Extensible Plugin Runner & SDK**: Added support for dotted Python class paths (`gui.Tab`), raw python scripts (`.py`), and executable binaries (`.exe`). Introduces new plugin types: `"background"` (lifecycle tied to manager), `"utility"` (toolkit items under Settings), and `"listener"` (reactive hooks triggered on game launch and close). Includes a UI scaffolder button to instantly generate template files under `plugins/starter_plugin/`.
*   **Advanced Plugin Developer SDK Features (Phase 2)**:
    *   **IPC API Bridge**: Embedded a local Socket-based JSON-RPC server (listening on `localhost:port` defaulting to `8692`) inside SpiraMM to synchronize status, post log statements, and broadcast events to external plugin processes. Added a configuration option under Directory Settings to customize this port along with hot-swapping logic to restart the socket server on the fly. To ensure plugins can dynamically locate customized ports without hardcoding, SpiraMM automatically injects the `SPIRAMM_IPC_PORT` environment variable and appends a `--ipc-port {port}` argument to any spawned plugin subprocesses.
    *   **Shared Memory Access API**: Exposed process memory reading (`read_memory`) and writing (`write_memory`) wrappers directly on the main manager class, utilizing `ReadProcessMemory` / `WriteProcessMemory` process hooks for game-interacting trainers and overlays.
    *   **Dynamic Settings UI**: Added support for schema-defined options inside `plugin.json` (types `bool`, `int`, `string`, and `select`). Configuration cards are auto-generated in the Settings panel and values are persisted in the manager's config.
    *   **Pip Dependency Auto-Installer**: Scans `"dependencies"` array in plugin manifests on load and automatically installs missing Python packages to a localized `plugins/lib` folder, keeping dependencies isolated.
    *   **Hook Event Registry & Hot-Reloading**: Built a dynamic pub/sub engine broadcasting `on_game_launch`, `on_game_close`, `on_theme_change`, and `on_mod_toggle` to listening plugins and IPC clients. Supports hot-reloading all plugins on demand.
*   **Transition to Unified `.spiramod` File Format**: Replaced the legacy `.ffxmod` metadata and active tracker extension with the unified `.spiramod` extension to reflect Spira Mod Manager's identity. 
*   **Target Game Metadata Property**: Added a `"game"` field inside the mod metadata JSON structure to explicitly denote whether a mod targets `"FFX"` or `"FFX-2"`.
*   **Backward Compatibility & Seamless Migration**: Designed a clean, fully automatic migration path. When the manager scans existing mod folders, any legacy `modinfo.ffxmod` or `{mod_id}.ffxmod` tracker files are loaded, parsed, upgraded to include the `"game"` metadata property, written as `.spiramod` files, and the old legacy files are cleanly deleted.
*   **Bulk Mod Import**: Added support for importing multiple mod archives (`.zip`, `.rar`) at once. The manager auto-names mods based on their filenames, applies defaults, and leaves metadata fields unlocked for custom editing.
*   **Dynamic Credits Lock & Directory Renaming**: Allowed custom metadata editing for bulk-imported mods with `"credits_locked": false`. Once edited and saved, the metadata locks (`"credits_locked": true`). If the display name is modified during this step, the manager physically renames the mod's folder and updates active trackers on disk.
*   **UnX Texture Path Auto-Resolution**: Enhanced relative path resolution during manual files/folders import. The manager now automatically maps path contexts containing `"unx_res/"`, `"inject/textures/"`, and `"textures/"`, as well as loose `.dds` texture files, into their corresponding subfolder targets under `UnX_Res/inject/textures/` without prompting the user.
*   **Built-in Diagnostics Showcase Utility Plugin**: Included a built-in utility plugin under `plugins/diagnostics/` that is auto-discovered under "Plugin Toolkit Actions" in Settings. It runs a diagnostics script passing setup parameters and connects back to the manager via the loopback JSON-RPC socket server to print diagnostic logs live.

## Bug Fixes
*   **Unified Conflict Detection Format Support**: Corrected the mod conflict checking algorithm (`check_for_conflicts`) to support the unified `.spiramod` metadata format instead of searching exclusively for legacy `.ffxmod` and `.json` files. This restores full functionality to the "Conflicts" tab.

## Build Tools & Scripts
*   **Native Batch Compilation Run Script (run.bat)**: Created a selection-driven `run.bat` batch script in the root directory that allows compiling individual targets (Spira Mod Manager, or Plugin Trackers) or all targets using native PyInstaller command execution and plugin auto-discovery.
*   **Removed Python Compile Script**: Deleted `compile_mod_manager.py` as its build and packaging tasks are fully replaced by the dependency-free native batch logic in `run.bat`.
