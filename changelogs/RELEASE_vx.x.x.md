# Changelog - Spira Mod Manager (Draft Release vx.x.x)

This document contains a running log of all changes made since the official release of v3.3.1.

---

## ⚡ Key Highlights
*   **Universal Preview Image & Zoom Viewer**: Integrated automatic multi-image gallery support (`preview1`–`5`, `cover1`–`5`, `screenshot1`–`5`) across PNG, JPG, JPEG, WEBP, BMP. Added responsive 3-zone preview clicking (Left/Right to step, Center to zoom) and a full-resolution Pan & Zoom modal viewer.
*   **Spira Modpack Engine (`.spirapack` / `.zip`)**: Package entire collections of enabled mods, load orders, and configurations into shareable archives. Full 1-click import with summary preview and automatic Profile creation.
*   **Multi-Tier LIFO Conflict Registry (`conflict_registry.json`)**: Built a robust collision stack engine ensuring vanilla game files are never overwritten or corrupted, and previous mod layers automatically cascade back when disabling mods.
*   **Steam Deck & Linux/Proton Auto-Detection**: Native auto-discovery of Steam game libraries and virtualized Proton Documents save folders (`compatdata/359870/pfx/...`) for zero-configuration modding on Steam Deck.
*   **Official Nexus Mods Categories & Normalization**: Fully updated all category pickers, filters, and editors to match official Nexus categories for FFX & FFX-2 HD Remaster (*Armour and Clothing*, *Body, Face, Hair*, *Models and Textures*, *Visuals and Graphics*, etc.). Added automatic aliasing (`CATEGORY_ALIASES`) to map legacy tags and eliminate double-ups.
*   **Vibrant Card Category Badges**: Added distinct, high-contrast background and text color styling for every official Nexus category badge on mod cards.
*   **Custom Windows Taskbar Icon**: Explicitly registered Windows Application User Model ID (`AppUserModelID`) and default icon cascades to ensure the custom `SpiraMM.ico` displays on the Windows taskbar instead of Python's generic Tkinter feather icon.
*   **Instant Startup & Rescan Disk Sizing**: Replaced redundant disk stat loops in `scan_mods` with direct manifest metadata size lookups, reducing app startup and list refresh time from several seconds down to under 100 milliseconds.
*   **Large Mod Performance & Instant Conflict Engine**: Rebuilt the conflict detection engine to use an in-memory hash map index (`get_active_files_index`), eliminating tens of thousands of redundant disk reads and reducing selection latency on multi-gigabyte/10,000+ file mods from 15+ seconds down to under 2 milliseconds!
*   **Mod List "Sort By" Engine**: Added 1-click sorting for *Name (A–Z / Z–A)*, *Status (Enabled First)*, *Size (Largest First)*, *Category*, and *Default Order*.
*   **Quality of Life Polish**: Added quick-clear search button (`✕`), double-click mod card toggle, keyboard navigation (`▲`/`▼`), keyboard metadata shortcuts (`Ctrl+S`/`Enter`), "✔️ Saved!" visual flash, dynamic list counter, and 1-click "Open Folder" in Save Manager.

---

## 🔧 Changelog Details

### 🖼️ UI Preview Card, Categories & Asset Staging
*   Synchronized `DEFAULT_CATEGORIES` across `cmb_category`, `cmb_mod_category`, and `create_mod` to include all official Nexus categories (*Armour and Clothing*, *Audio*, *Body, Face, Hair*, *Gameplay and Balancing*, *General*, *Miscellaneous*, *Models and Textures*, *Saved Games*, *User Interface*, *Utilities*, *Visuals and Graphics*).
*   Implemented `CATEGORY_ALIASES` and `normalize_category` to cleanly map legacy/short category names and prevent duplicate category entries.
*   Added bespoke, theme-consistent badge colors for all official Nexus categories on mod cards.
*   Registered explicit `AppUserModelID` (`SetCurrentProcessExplicitAppUserModelID`), OS Window Class icon override, and default `iconbitmap` to guarantee custom taskbar icon rendering on Windows.
*   Implemented Universal Preview Image Engine (`PREVIEW_IMAGE_PATTERNS` & `is_preview_image_filename`) supporting `preview1`–`preview5`, `cover1`–`cover5`, `screenshot1`–`screenshot5` (with `_`, `-`, or no separator) across `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, with natural numerical and priority sorting in the preview gallery combobox.
*   Defined `UI_METADATA_FILES` to isolate `modinfo.*` files and cover images.
*   Filtered all indexing loops (`scan_mods`, `import_zip_mod`, `import_bulk_zips`, `create_mod_wizard`) to exclude UI metadata from `files` arrays in `modinfo.spiramod`.
*   Safeguarded `enable_mod_logic`, `disable_mod_logic`, and `find_active_file_owner` to skip UI metadata files during enable, disable, and backup restoration loops.
*   Added auto-cleansing in `scan_mods` to strip lingering UI metadata entries from active trackers on startup.
*   Added automatic metadata panel reset (`clear_metadata_fields`) upon deleting a mod from disk.
*   Streamlined folder import in the Mod Creation Wizard to default unmapped paths to `os.path.relpath`, preventing popup prompt loops.
*   Protected tooltip timers against `TclError` window destruction race conditions during rapid tab switching.
*   Added Search Bar Quick-Clear Button (`✕`) that appears dynamically when typing to reset filters instantly.
*   Added Mod List "Sort By" Dropdown with support for *Name (A–Z / Z–A)*, *Status (Enabled First)*, *Size (Largest First)*, *Category*, and *Default Order*.
*   Added Double-Click Mod Card Toggle to quickly switch mods between Enabled and Disabled states.
*   Added Keyboard Navigation (`▲` / `▼` Arrow Keys) with auto-scrolling to step smoothly through installed mod cards.
*   Added Keyboard Shortcuts (`Enter` / `Ctrl+S`) to save mod metadata instantly from any entry field, and Arrow Keys (`◀` / `▶`) to step through screenshots.
*   Added "✔️ Saved!" Green Visual Flash on the metadata save button to provide instant confirmation of saved changes.
*   Added Dynamic Mod Counter to the list header showing live counts (`X Enabled, Y Disabled • Z Total`).
*   Added Full-Resolution Preview Zoom Popup (double-click preview image or click `🔍` zoom button) with smooth pan/scroll.
*   Added Right-Click Context Menu to Files and Conflicts treeviews (`📋 Copy Relative Path` and `📁 Open Folder Location`).
*   Implemented Spira Modpack Engine (`.spirapack` / `.zip`) allowing players to package collections of installed mods, metadata, descriptions, and Fahrenheit load order into a single portable distribution archive.
*   Added Modpack Exporter Dialog with mod checklist filters (*Select All*, *Enabled Only*, *Deselect All*), custom modpack metadata inputs (Name, Author, Version, Description), and multi-threaded zip compression with a progress bar.
*   Added Modpack Importer with auto-detection of `modpack.spiramod` manifests, preview confirmation modal, automatic multi-mod extraction, and automated profile generation.
*   Added "📦 Export Modpack" and "📦 Import Modpack" options into the Import dropdown menu (`▾`).
*   Added Live Storage Space Indicator to the sidebar footer showing available gigabytes on the active game installation drive.
*   Unified selection handling by routing `on_mod_selected` through the virtualized `select_mod` engine.

### 🌐 Nexus Mods Integration & Update Checker
*   Updated `enable_mod_logic` to preserve `nexus_id`, `version`, `author`, `description`, `link`, and `credits_locked` inside active tracking manifests (`modinfo.spiramod`).
*   Added automatic fallback in `scan_mods` to merge missing metadata keys from `data/mods_disabled/<mod_id>/` for enabled mods.
*   Updated `check_single_mod_update` to re-fetch live mod data from memory, fall back to active text box entry if currently selected, and sanitize ID strings to extract numeric digits automatically.
*   Implemented `is_newer_version(local, remote)` with regex number normalization and padded tuple comparison to eliminate false-positive update alerts.

### 💾 Save Manager & Cloud Sync
*   Added "📁 Open Folder" button to the Save Game Manager toolbar for 1-click access to the active game's save files in Windows File Explorer.
*   Implemented Steam Deck & Proton Prefix Auto-Detection Engine (`get_default_save_path`) to discover virtualized saves in `compatdata/359870/pfx/...` and SD card directories across Linux/SteamOS.
*   Upgraded `perform_cloud_save_sync` to write save files to `.tmp` staging before atomic `os.replace` replacement.
*   Added graceful cloud sync thread joining in `on_app_closing` to prevent partial/interrupted save writes on rapid manager exit.
*   Fixed save slot detection in `show_save_import_dialog` to parse numeric slot digits directly, preventing digit truncation on cross-game save imports.
*   Enabled instant drag-and-drop save file import in `handle_dropped_files`.
*   Anchored all local save backup directory paths (`load_saves_backups`, `create_save_backup`, `restore_save_backup`, `delete_save_backup`) to application root `_base_dir`.

### ⚙️ Engine, Loader & Plugin System
*   Implemented Multi-Tier LIFO Conflict Registry (`conflict_registry.json`) to track stacked file collisions across multiple overlapping mods with automatic vanilla baseline stashing (`data/backups/vanilla/`) and cascading restoration.
*   Implemented Cross-Platform Steam Auto-Detection (`get_steam_install_path`) supporting Windows Registry, alternate library drives, Linux paths, and Steam Deck microSD mounts.
*   Added high-performance in-memory active file indexing (`get_active_files_index`) to reduce conflict scanning from $O(N \times M)$ disk operations to $O(1)$ in-memory lookups.
*   Replaced file-by-file disk stat calculation in `scan_mods` with instant metadata lookup, accelerating app launch and refresh performance.
*   Added automatic load order synchronization when renaming mod folder IDs in Fahrenheit mode.
*   Added informative feedback when clicking load order priority buttons in Standard (Direct Staging) mode.
*   Added dynamic Python executable discovery (`shutil.which`) for plugin script execution when running as a standalone compiled executable.
*   Added trailing separator to extraction destination paths for WinRAR/UnRAR compatibility across all WinRAR versions.


