# Spira Mod Manager Changelog - Next_Release

## UI Layout and Configuration Updates

### Settings Tab Enhancements
*   **Unified Directory Card**: Consolidated "Game Directory Settings" and "Saves Location Configuration" into a single, cohesive **Directory Settings** card.
*   **Logical Config Order**: Positioned the "FFX&X2 Game Folder" path picker at the top, immediately followed by the "Saves Directory" configuration path.
*   **Removed Duplicate Launch Button**: Removed the duplicate "Launch FFX" button from the settings tab.
*   **Mod Loader Status Banner Placement**: Positioned the Mod Loader Diagnostic Banner at the very top of the Settings tab.
*   **Side-by-Side Theme & Safety Cards**: Housed both "Appearance Theme Settings" and "Safety & Diagnostics Controls" side-by-side in a single row container at the bottom, compacting their overall widths and button sizes.
*   **Syntax Corrections**: Patched syntax errors in mouse scroll wheel event hooks and Open Themes folder action handler.

### Mods Tab Details Layout
*   **Compact Action Button Grid**: Re-arranged mod list actions into a space-efficient 2-row grid featuring single-word labels:
    *   Row 1: `⚡ Enable`, `⏪ Disable`, `🆕 Create`, and `📥 Import`.
    *   Row 2: `🗑️ Delete` and `🔄 Refresh`.
*   **Mod Metadata Field Locking**: Populated metadata details entry fields (Creator, Version, Link, Description, Nexus ID) are now dynamically locked as `readonly` in the GUI if they contain values, and the Mod Name is locked unconditionally as `readonly`. The version check placeholder has been updated from `1.0` to `0.0` so that mods with version `1.0` are correctly locked. Values are also enforced securely during metadata save operations.

### General UI Fixes
*   **Decoupled Console Log Window**: Completely removed the bottom-pinned console log panels from the main container.
*   **Settings Tab Integration**: Renamed the Safety settings card to `"Safety & Diagnostics"` and embedded a `"📜 View Console Log"` button that launches the log history in a new floating `Toplevel` window.
*   **Saves Tab Button Compaction**: Shortened Saves action buttons to single-word labels (`📥 Backup`, `⏪ Restore`, `🗑️ Delete`, `🔄 Refresh`) to align with the compact and square layout theme.
*   **2-Column Plugin Browser Layout**: Restructured both the "Plugin Directory" and "Installed Plugins" tabs to render cards in a side-by-side, 2-column grid layout, making them much more compact and squarer. Set description text wraps to 350px.
*   **Plugin Signature Placement**: Shuffled the plugin creator name label from the header row down below the action buttons as a right-aligned signature.
*   **Dynamic Sidebar Logo Text**: Exposed the sidebar logo label and updated it to dynamically switch between "FFX MODS" and "FFX-2 MODS" based on the selected game mode.
*   **Thematic Application Renaming**: Renamed the application window title from "FFX Mod Manager" to "Spira Mod Manager", dynamically suffixing the active game mode (e.g., "Spira Mod Manager - FFX Mode"). Also updated the System Log window to "📜 Spira Mod Manager - System Log".

### Theme System & Button Colorizations
*   **Customizable Semantic Button Colors**: Added customizable theme properties for semantic button categories: Action/Accept, Caution/Danger, Success/Enable, and Utility/Default.
*   **Theme Creator Dialog Restructure**: Re-arranged the Theme Creator UI into a side-by-side two-column grid ("Base Colors" and "Button Colors"), widening the dialog container to `920x560` to accommodate all 21 color properties cleanly.
*   **Theme Creator Previews**: Replaced the single preview button with **four distinct buttons** representing each semantic style (Accept, Success, Caution, Utility) and bound dynamic hover events to display the custom hover color changes in real-time.
*   **Backward Compatibility Fallbacks**: Implemented automatic fallbacks so that any legacy or user-made themes without the new button keys continue to load and look correct.

### UI Hover Tooltips
*   **Comprehensive Hover Tooltips**: Added informative, custom hover tooltips to key inputs, filters, buttons, tabs, and settings across the entire interface. This includes:
    *   Sidebar navigation tabs (`Mods`, `Saves`, `Plugin Browser`, `Settings`, and dynamic plugin panels).
    *   Search filter input, Category filter combobox, Profile selection dropdown, and Profile action buttons (`Apply`, `Save`, `Delete`).
    *   Mod metadata fields (`Name`, `Creator`, `Version`, `Description`, `Category`, `Nexus ID`, `Link`), "Visit Link" button, and "Save Metadata" button.
    *   Files tab operations (`Import File`, `Import Folder`, `Open Folder Location`).
    *   Settings directory paths (`Game Directory`, `Saves Directory`), theme options (`Theme Selector`, `Create Theme`, `Open Themes Folder`), and Safety & Diagnostics panel (`Safe Reset`, `Verify Permissions`, `View Console Log`).
    *   Plugin directory refresh and installed plugins refresh buttons.
*   **Dynamic Theme Integration**: All new tooltips dynamically inherit and follow the active theme's colors.

### Modern Glassmorphism UI Overhaul
*   **Floating Card Containers**: Refactored the four main page frames to float within the content window as isolated glass card panels using a 1px solid border (`highlightthickness=1`, `bd=0`) mapped to the active theme's borders.
*   **Recursive Parent Background Inheritance**: Programmed a dynamic parent-walking routine inside the widget styling updater to automatically match backgrounds of inner subframes, textareas, and canvases to their enclosing card's colors.
*   **TTK Card Styles**: Introduced new custom style hooks `Card.TFrame` and `Card.TPanedwindow` for nested containers and paned sections to seamlessly blend card backdrops across the entire mods, saves, settings, and plugins layouts.
*   **Active Accent Outlines**: Mapped widget focus states to the active theme's glowing accent colors, giving a premium active glowing outline effect to treeviews, textboxes, and entry fields when selected.

## Save File Management
*   **Save File Import Assistant**: Added automatic scanning and extraction support for extensionless game save files (`ffx_###` / `ffx2_###`) inside imported ZIP/RAR archives.
*   **Interactive Renaming & Conflict Resolution Dialog**: If save files are detected, a custom styled interactive assistant window pops up to show slot availability and let users assign custom destination slot numbers using a spinbox (auto-suggesting the first available slot to avoid overwriting current saves).
*   **Decoupled Saves/Mods Extraction**: If a package contains both mod files and save files, the mod manager safely separates them, deploying the mod to repository storage while routing and renaming the saves directly into the active game saves directory.

## Bug Fixes
*   **Mod Staging Directory Path Resolution (FFX & FFX-2)**: Resolved staging directory path nesting bugs by cleanly separating active tracker `.ffxmod` files from the target deployment directories. Mod tracker files are stored isolated inside `data/mods/ffx_data` and `data/mods/ffx2_data` respectively, while the actual mod assets are written directly to `data/mods` without redundant nesting.
*   **Mod Creation Blank Directory Fix**: Fixed an issue where creating a mod that includes files within the `ffx_ps2` structure would also generate an empty, unused `ffx_data` directory alongside it. Default game directories are now only pre-created when initializing a blank mod.
*   **Mod List Tooltip Metadata Fix**: Fixed a bug where hovering over a mod card in the mod list showed "No description provided." and "Version: 1.0" in the tooltip even when custom description and version metadata existed. Description, version, link, and nexus_id fields are now cached properly in memory when scanning mods.
*   **Loose Folder Mod Restructuring & Path Correction**: Added automated restructuring during ZIP/archive imports and fallback path resolution for loose `ffx/` and `ffx2/` folders. If an imported mod has its assets located at the root of a loose `ffx` or `ffx2` folder (missing the required parent `ffx_ps2` wrapper), the manager automatically relocates and wraps the directory structure into `ffx_ps2/ffx/` or `ffx_ps2/ffx2/` respectively, ensuring correct deployment under the external file loader.
*   **Legacy FFX-2 Mod Restructuring (ZIP Import)**: Added automatic detection and renaming for legacy FFX-2 mod folders named `ffx2_data` or `ffx2_ps2` inside imported ZIP archives. The manager now restructures them to `ffx-2_data` and `ffx_ps2/ffx2` directly during extract staging to prevent nested duplicate directories.
*   **Legacy FFX-2 Path Translation (Manual Import)**: Updated the relative path resolver to intercept file paths containing `ffx2_data/` or `ffx2_ps2/` and map them to their correct target folders (`ffx-2_data/` and `ffx_ps2/ffx2/`), avoiding manual relative path entries.
*   **Fahrenheit Manifest Metadata Mapping**: Expanded the Fahrenheit manifest fallback reader (`.manifest.json`) to parse and populate mod description, project link, and Nexus Mod ID fields in the details panel and hover tooltips.
