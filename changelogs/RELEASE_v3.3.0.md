# Changelog - Spira Mod Manager (Release v3.3.0)

This document contains a running log of all changes made since the official release of v3.2.0.

---

## ⚡ Key Highlights
*   **Drag-and-Drop File Importing**: Added native Tcl-level file drag-and-drop loading using `tkinterdnd2`, allowing users to drag `.zip` or `.rar` mod files directly into the window for quick imports.
*   **Nexus Mods Integration & Update Checker**: Configure a personal Nexus Mods API Key securely in Settings to validate connection, check installed mods for updates asynchronously (background threaded), and show visual update badges linking to download pages.
*   **Mod Card Context Menu**: Right-click mod cards to access quick options (Edit Metadata, Check Update, Visit Nexus page, Enable/Disable, Delete).
*   **Local Cloud Save Auto-Sync**: Keep game save files synchronized automatically to a configured local cloud folder (OneDrive, Google Drive, Dropbox, etc.).
*   **Layout Realignment**: Realigned Settings page, placing the Nexus settings card on top and splitting Theme and Safety cards into a clean 50/50 split matching the rest of the UI.

---

## 🔧 Changelog Details

### 📥 Drag and Drop & Mod Importing
*   Implemented safe Tcl-level drag-and-drop loading support using the `tkinterdnd2` wrapper.
*   Bundled `tkdnd` binaries in the PyInstaller build specification for stand-alone distribution.
*   Enhanced ZIP & RAR auto-unwrapping with support for bulk importing multiple files simultaneously.

### 🌐 Nexus Mods & Update Checking
*   Added `"nexus_api_key"` local configuration entry.
*   Created **Nexus Mods Integration** settings panel with hidden API key inputs (`show="•"`) and background key validation.
*   Added **"Check Updates"** action in the mods list manager.
*   Implemented asynchronous background checking via official Nexus API endpoints.
*   Added custom `✨ Update: vX.Y` badges on mod cards.
*   Added right-click context menu bindings for mods tab card widgets, supporting direct metadata focusing, browser link opening, updates checking, and mod status toggle.

### 💾 Save Files & Cloud Syncing
*   Added local Cloud Save Auto-Syncing feature allowing instant, safe backups to cloud folders.
*   Fixed log window icons and TopLevel dialogs to consistently inherit the application icon.

### 🎨 Visual Theme & Settings Adjustments
*   Shifted **Nexus Mods Integration** to the top of the settings page layout.
*   Optimized settings bottom row columns (from 3 to 2) to display theme selector and safety options in a symmetric 50/50 layout.

### 📖 Backlogs & Repository Administration
*   Separated companion plugin items from `backlog.md` into `backlog_plugins.md`.
*   Moved completed roadmap items to the bottom tracks.
