# Spira Mod Manager GitHub Release - v3.2.0

*   **Tag Version**: `v3.2.0`
*   **Release Title**: `Spira Mod Manager v3.2.0 - Extensible Plugin SDK & Bulk Mod Import`

---

## Release Notes

This major release introduces the **Extensible Plugin Runner & SDK** for developers, adds **Bulk Mod Importing** to speed up manager staging, implements automated **UnX path resolution** for loose DDS textures, and migrates metadata tracking to the unified `.spiramod` file type.

### 🔌 Extensible Plugin SDK & Runner
*   **Dotted Path, Scripts, and Binaries**: Support for launching python classes (`gui.Tab`), raw `.py` scripts, and standalone `.exe` programs.
*   **IPC API Bridge**: Embedded socket JSON-RPC server (port `8692`) inside SpiraMM allowing background or external overlay plugins to log messages, synchronize states, and react to manager hooks (`on_game_launch`, `on_game_close`, `on_mod_toggle`).
*   **Shared Memory Hooks**: Native memory reading and writing APIs using `ReadProcessMemory` / `WriteProcessMemory` for overlay trainers.
*   **Settings UI Scaffolding**: Automatically generates configuration cards in the Settings panel based on settings defined in `plugin.json` manifests.
*   **Starter Template Generator**: Built-in template scaffolder creates files under `plugins/starter_plugin/` to help developers write plugins instantly.

### ⚙️ Core System & UI Updates
*   **Split Import Dashboard Button**: The Dashboard import widget now uses a split button (arrow dropdown) to choose between single file import and bulk import.
*   **Bulk Mod Archive Import**: Unpacks multiple archives in a single task, auto-naming them from filenames and setting metadata fields unlocked for custom editing.
*   **Dynamic Credits Lock & Directory Renaming**: Allows changing mod names and author info for bulk-imported mods. Renaming the display name automatically renames the physical folder on disk and updates active trackers.
*   **Unified `.spiramod` Format & Migration**: Legacy `.ffxmod` files are now automatically upgraded to the unified `.spiramod` metadata format, adding game specificity properties.
*   **UnX Texture Path Auto-Resolution**: Automatically maps folder contexts containing `"unx_res/"`, `"inject/textures/"`, and `"textures/"`, as well as loose `.dds` texture files, into their correct targets under `UnX_Res/inject/textures/` without prompting the user.

### 🐛 Bug Fixes
*   **Conflict Tab Format Support**: Updated the conflict checker to properly read `.spiramod` metadata files, resolving issues where mod conflicts were missing.
*   **Fahrenheit Launch Paths**: Fixed working directories and parameters when executing the launcher via Fahrenheit Mod Loader.

---

## Assets
* 📦 `SpiraModManager.exe` (Compiled executable)
* 💾 Source code (zip)
* 💾 Source code (tar.gz)
