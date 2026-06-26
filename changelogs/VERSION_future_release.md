# Spira Mod Manager Changelog - Future Release

This file contains staging changelogs for the upcoming releases of Spira Mod Manager.

## UI Layout and Configuration Updates

### Enhancements
*   **Multi-Game Mod Wizard**: Updated the mod creation wizard dialog to support choosing the target game (FFX or FFX-2), ensuring custom mod structures are correctly prepared under their respective directory scopes (`ffx_data` or `ffx-2_data`).

### General UI Fixes
*   *(Placeholder for interface corrections)*

## Core System & Path Operations
*   **Transition to Unified `.spiramod` File Format**: Replaced the legacy `.ffxmod` metadata and active tracker extension with the unified `.spiramod` extension to reflect Spira Mod Manager's identity. 
*   **Target Game Metadata Property**: Added a `"game"` field inside the mod metadata JSON structure to explicitly denote whether a mod targets `"FFX"` or `"FFX-2"`.
*   **Backward Compatibility & Seamless Migration**: Designed a clean, fully automatic migration path. When the manager scans existing mod folders, any legacy `modinfo.ffxmod` or `{mod_id}.ffxmod` tracker files are loaded, parsed, upgraded to include the `"game"` metadata property, written as `.spiramod` files, and the old legacy files are cleanly deleted.
*   **Extensible Plugin Runner & SDK**: Added support for dotted Python class paths (`gui.Tab`), raw python scripts (`.py`), and executable binaries (`.exe`). Introduces new plugin types: `"background"` (lifecycle tied to manager), `"utility"` (toolkit items under Settings), and `"listener"` (reactive hooks triggered on game launch and close). Includes a UI scaffolder button to instantly generate template files under `plugins/starter_plugin/`.
*   **Advanced Plugin Developer SDK Features (Phase 2)**:
    *   **IPC API Bridge**: Embedded a local Socket-based JSON-RPC server (listening on `localhost:port` defaulting to `8692`) inside SpiraMM to synchronize status, post log statements, and broadcast events to external plugin processes. Added a configuration option under Directory Settings to customize this port along with hot-swapping logic to restart the socket server on the fly. To ensure plugins can dynamically locate customized ports without hardcoding, SpiraMM automatically injects the `SPIRAMM_IPC_PORT` environment variable and appends a `--ipc-port {port}` argument to any spawned plugin subprocesses.
    *   **Shared Memory Access API**: Exposed process memory reading (`read_memory`) and writing (`write_memory`) wrappers directly on the main manager class, utilizing `ReadProcessMemory` / `WriteProcessMemory` process hooks for game-interacting trainers and overlays.
    *   **Dynamic Settings UI**: Added support for schema-defined options inside `plugin.json` (types `bool`, `int`, `string`, and `select`). Configuration cards are auto-generated in the Settings panel and values are persisted in the manager's config.
    *   **Pip Dependency Auto-Installer**: Scans `"dependencies"` array in plugin manifests on load and automatically installs missing Python packages to a localized `plugins/lib` folder, keeping dependencies isolated.
    *   **Hook Event Registry & Hot-Reloading**: Built a dynamic pub/sub engine broadcasting `on_game_launch`, `on_game_close`, `on_theme_change`, and `on_mod_toggle` to listening plugins and IPC clients. Supports hot-reloading all plugins on demand.

## Bug Fixes
*   *(Placeholder for engine/manager fixes)*

## Build Tools & Scripts
*   **Native Batch Compilation Run Script (run.bat)**: Created a selection-driven `run.bat` batch script in the root directory that allows compiling individual targets (Spira Mod Manager, or Plugin Trackers) or all targets using native PyInstaller command execution and plugin auto-discovery.
*   **Removed Python Compile Script**: Deleted `compile_mod_manager.py` as its build and packaging tasks are fully replaced by the dependency-free native batch logic in `run.bat`.

