# Changelog - Spira Mod Manager (Draft Release vx.x.x)

This document contains a running log of all changes made since the official release of v3.3.1.

---

## ⚡ Key Highlights
*   **Preview Image Conflict Protection**: Fixed a bug where UI metadata and preview images (`preview.png`, `cover.png`, etc.) were treated as active game assets, preventing them from being moved to game directories or swapped between mods during conflict resolution.
*   **Nexus Mod ID & Metadata Preservation**: Fixed a bug where enabling a mod wiped its `nexus_id`, `version`, `author`, and `link` from active tracker data, ensuring update checks work seamlessly on enabled mods.
*   **Semantic Version Comparison Engine**: Rebuilt the version comparison logic to use padded numeric segments, preventing false "Update Available" prompts between equal versions (e.g. `1.0` vs `1.0.0`).
*   **Atomic Cloud Save Sync**: Safeguarded save backups against data corruption by staging copies to `.tmp` files before atomic replacement and awaiting sync thread completion on application exit.
*   **Fahrenheit Load Order Mod Rename Sync**: Ensured that renaming a mod's folder ID in metadata seamlessly updates `fahrenheit/mods/loadorder` and active load priority.
*   **Drag-and-Drop Save File Auto-Routing**: Added automatic detection for dropped save game files to route directly into the Save Import Assistant.

---

## 🔧 Changelog Details

### 🖼️ UI Preview Card & Asset Staging
*   Defined `UI_METADATA_FILES` to isolate `modinfo.*` files and cover images (`preview.png`, `cover.png`, `mod_preview.png`, `preview1.png`–`preview4.png`).
*   Filtered all indexing loops (`scan_mods`, `import_zip_mod`, `import_bulk_zips`, `create_mod_wizard`) to exclude UI metadata from `files` arrays in `modinfo.spiramod`.
*   Safeguarded `enable_mod_logic`, `disable_mod_logic`, and `find_active_file_owner` to skip UI metadata files during enable, disable, and backup restoration loops.
*   Added auto-cleansing in `scan_mods` to strip lingering UI metadata entries from active trackers on startup.
*   Added automatic metadata panel reset (`clear_metadata_fields`) upon deleting a mod from disk.

### 🌐 Nexus Mods Integration & Update Checker
*   Updated `enable_mod_logic` to preserve `nexus_id`, `version`, `author`, `description`, `link`, and `credits_locked` inside active tracking manifests (`modinfo.spiramod`).
*   Added automatic fallback in `scan_mods` to merge missing metadata keys from `data/mods_disabled/<mod_id>/` for enabled mods.
*   Updated `check_single_mod_update` to re-fetch live mod data from memory, fall back to active text box entry if currently selected, and sanitize ID strings to extract numeric digits automatically.
*   Implemented `is_newer_version(local, remote)` with regex number normalization and padded tuple comparison to eliminate false-positive update alerts.

### 💾 Save Manager & Cloud Sync
*   Upgraded `perform_cloud_save_sync` to write save files to `.tmp` staging before atomic `os.replace` replacement.
*   Added graceful cloud sync thread joining in `on_app_closing` to prevent partial/interrupted save writes on rapid manager exit.
*   Fixed save slot detection in `show_save_import_dialog` to parse numeric slot digits directly, preventing digit truncation on cross-game save imports.
*   Enabled instant drag-and-drop save file import in `handle_dropped_files`.

### ⚙️ Engine, Loader & Plugin System
*   Added automatic load order synchronization when renaming mod folder IDs in Fahrenheit mode.
*   Added dynamic Python executable discovery (`shutil.which`) for plugin script execution when running as a standalone compiled executable.
*   Added trailing separator to extraction destination paths for WinRAR/UnRAR compatibility across all WinRAR versions.
