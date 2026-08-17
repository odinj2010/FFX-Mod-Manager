# Changelog - Spira Mod Manager (Draft Release vx.x.x)

This document contains a running log of all changes made since the official release of v3.3.1.

---

## ⚡ Key Highlights
*   **Preview Image Conflict Protection**: Fixed a bug where UI metadata and preview images (`preview.png`, `cover.png`, etc.) were treated as active game assets, preventing them from being moved to game directories or swapped between mods during conflict resolution.

---

## 🔧 Changelog Details

### 🖼️ UI Preview Card & Asset Staging
*   Defined `UI_METADATA_FILES` to isolate `modinfo.*` files and cover images (`preview.png`, `cover.png`, `mod_preview.png`, `preview1.png`–`preview4.png`).
*   Filtered all indexing loops (`scan_mods`, `import_zip_mod`, `import_bulk_zips`, `create_mod_wizard`) to exclude UI metadata from `files` arrays in `modinfo.spiramod`.
*   Safeguarded `enable_mod_logic`, `disable_mod_logic`, and `find_active_file_owner` to skip UI metadata files during enable, disable, and backup restoration loops.
*   Added auto-cleansing in `scan_mods` to strip lingering UI metadata entries from active trackers on startup.
