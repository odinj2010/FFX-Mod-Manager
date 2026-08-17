# Changelog - Spira Mod Manager (Draft Release vx.x.x)

This document contains a running log of all changes made since the official release of v3.3.1.

---

## ⚡ Key Highlights
*   **Preview Image Conflict Protection**: Fixed a bug where UI metadata and preview images (`preview.png`, `cover.png`, etc.) were treated as active game assets, preventing them from being moved to game directories or swapped between mods during conflict resolution.
*   **Nexus Mod ID & Metadata Preservation**: Fixed a bug where enabling a mod wiped its `nexus_id`, `version`, `author`, and `link` from active tracker data, ensuring update checks work seamlessly on enabled mods.

---

## 🔧 Changelog Details

### 🖼️ UI Preview Card & Asset Staging
*   Defined `UI_METADATA_FILES` to isolate `modinfo.*` files and cover images (`preview.png`, `cover.png`, `mod_preview.png`, `preview1.png`–`preview4.png`).
*   Filtered all indexing loops (`scan_mods`, `import_zip_mod`, `import_bulk_zips`, `create_mod_wizard`) to exclude UI metadata from `files` arrays in `modinfo.spiramod`.
*   Safeguarded `enable_mod_logic`, `disable_mod_logic`, and `find_active_file_owner` to skip UI metadata files during enable, disable, and backup restoration loops.
*   Added auto-cleansing in `scan_mods` to strip lingering UI metadata entries from active trackers on startup.

### 🌐 Nexus Mods Integration & Update Checker
*   Updated `enable_mod_logic` to preserve `nexus_id`, `version`, `author`, `description`, `link`, and `credits_locked` inside active tracking manifests (`modinfo.spiramod`).
*   Added automatic fallback in `scan_mods` to merge missing metadata keys from `data/mods_disabled/<mod_id>/` for enabled mods.
*   Updated `check_single_mod_update` to re-fetch live mod data from memory, fall back to active text box entry if currently selected, and sanitize ID strings to extract numeric digits automatically.
