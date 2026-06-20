# FFX Mod Manager Changelog - Next_Release

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

