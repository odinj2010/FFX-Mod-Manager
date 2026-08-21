# 🎮 Spira Mod Manager

A clean, fast, and secure standalone mod manager for **Final Fantasy X / X-2 HD Remaster** (Steam). Built with a modern dark interface, it handles installation, conflict resolution, load order, saves backups, and restores automatically while saving disk space.

---

## 📥 Direct Download & Quick Start

If you are a player looking to download the latest version, click the link below to get the ready-to-use mod manager file immediately:

### [👉 Click here to download the Newest Stable Release (v3.3.2) 👈](https://github.com/odinj2010/FFX-Mod-Manager/releases/download/v3.3.2/SpiraMM.rar)

### 🚀 Easy Installation Steps
1. **Download** the archive using the link above.
2. **Extract** the files (The entire Spira Mod Manager folder, it has the `SpiraModManager.exe`, `themes/` folder and `plugins/` folder inside it) **anywhere on your computer** (you do not have to place it inside the main game directory; you can simply select your game directory on first launch).
3. **Run** `SpiraModManager.exe` to launch the manager!

---

## ⚡ New in v3.3.2

* **Universal Preview Gallery & Zoom Viewer**: Added multi-screenshot support (`preview1`–`5`, `cover1`–`5`, `screenshot1`–`5`) across PNG, JPG, JPEG, WEBP, BMP with 3-zone click navigation (Left/Right to step, Center to zoom) and a full-resolution Pan & Zoom modal viewer.
* **Spira Modpack Engine (`.spirapack` / `.zip`)**: Package entire collections of installed mods, metadata, and load orders into shareable archives with 1-click import and automatic Profile creation.
* **Multi-Tier LIFO Conflict Registry**: Stack-based collision engine that protects pristine vanilla game files (in `data/backups/vanilla/`) and cascades previous mod layers back when disabling overlapping mods.
* **Steam Deck & Linux/Proton Auto-Detection**: Native auto-discovery of Steam game libraries and virtualized Proton Documents save folders (`compatdata/359870/pfx/...`) for zero-configuration modding on Steam Deck.
* **Official Nexus Categories & Badges**: Full category synchronization across all editors and filters with bespoke, vibrant category badges on mod cards.
* **Mod List "Sort By" Engine**: Added 1-click sorting for Name (A–Z / Z–A), Status (Enabled First), Size (Largest First), Category, and Default Order.
* **Ultra-Fast Startup & Conflict Engine**: Rebuilt active file indexing with an in-memory hash map, dropping conflict resolution latency on 10,000+ file mods from 15+ seconds down to under 2ms!
* **Quality of Life Polish**: Quick-clear search button (`✕`), double-click mod card toggle, keyboard navigation (`▲`/`▼`), metadata shortcuts (`Ctrl+S`/`Enter`), "✔️ Saved!" visual flash, dynamic list counter, and 1-click "Open Folder" in Save Manager.

---

## 🌟 Core Features

* **Native .7z Archive Support**: Drag-and-drop or import `.7z` mod archives directly into the manager. Full support across single and bulk import dialogs, routing extraction through 7-Zip, WinRAR, or Windows native `tar` engines.

* **Nexus Mods Integration & Update Checker**: Configure a personal Nexus Mods API Key securely in Settings to validate connection, check installed mods for updates asynchronously (background threaded), and show visual update badges linking to download pages.
* **Mod Card Context Menu**: Right-click mod cards to access quick options (Edit Metadata, Check Update, Visit Nexus page, Enable/Disable, Delete).
* **Local Cloud Save Auto-Sync**: Keep game save files synchronized automatically to a configured local cloud folder (OneDrive, Google Drive, Dropbox, etc.) on game exit.
* **Settings Layout Realignment**: Realigned Settings page, placing the Nexus settings card on top and splitting Theme and Safety cards into a clean 50/50 split matching the rest of the UI.
* **About SpiraMM & Live Changelog**: Added an About card footer inside the Settings tab detailing version info and update status, with an offline-compatible styled Markdown release notes popup dialog.
* **Theme-Aware Checkbuttons**: Added custom formatting for Tkinter Checkbutton widgets to dynamically update their border, checkbox, and select colors on theme swaps.
* **Fahrenheit Mod Loader Integration**: Full native compatibility with the modern Fahrenheit Modding Framework. Automatically stages manifests (`.manifest.json`), manages dynamic C# mod folders, synchronizes load order priorities, and automatically deactivates standard saves restoration in Fahrenheit mode to prevent game save conflicts.
* **Dual-Game Partition Isolation**: Fully separates FFX and FFX-2 mod databases, configuration tracks, active/disabled directories, and save directories, ensuring FFX and FFX-2 settings never overlap.
* **Space-Saving Architecture**: Moves files (cut & paste) between the inactive mod repository (`data/mods_disabled/` or `data/mods_disabled_x2/`) and active game directories on enable/disable, avoiding redundant duplicate file copies.
* **Robust Windows File Operations**: Features retry-based safety wrappers for file moves and removals to prevent transient Windows locking failures and PermissionErrors.
* **Advanced Conflict Resolution (Auto-Restore)**: Scans active mods for overlapping files and calculates active load-order priority. When an overriding mod is disabled, the manager automatically restores the previously backed-up mod files. Full support for the unified **.spiramod** format.
* **Interactive Save File Import Assistant**: Decouples save files (`ffx_###` / `ffx2_###`) from mod archives during import. Displays slot availability and lets you safely remap imported files to free slots via spinbox to prevent overwriting your personal progress.
* **Unified Saves & Backups Manager**: Creates local backups with custom labels and descriptions (e.g. *"Seymour Battle"*), showing sizes and timestamps, and supports one-click restores of slot snapshots.
* **Import Progress Indicator Modals**: Replaces frozen screens with a themed, non-blocking progress dialog showing real-time extraction tracking (progress bar, percentages, and current filenames) during archive extraction.
* **Bulk ZIP, RAR & 7Z Mod Import**: Supports importing multiple mod archives (`.zip`, `.rar`, `.7z`) at once. The manager auto-names mods based on filename, applies defaults, and leaves metadata unlocked. Folder hierarchies (such as loose textures or missing parent structures) are auto-extracted and normalized to conform to the game directory layout.
* **Automatic UnX Texture Staging**: Detects and translates loose graphics folders and `.dds` texture files, wrapping them properly inside the required `UnX_Res/inject/textures/` structure without requiring manual path corrections.
* **Live Graphics Preview Card**: Displays cover art and mod screenshots (`preview.png`, `cover.png`, etc.) directly inside the details panel with multi-image variant dropdown support.
* **Interactive Theme Engine**: Bundles 17 built-in themes (like *Celsius Purple*, *Yuna Summoner*, *Pyreflies Whimsy*) and features a Theme Creator with a 4-button live hover preview matrix for semantic button colors (Accept, Success, Caution, Utility) and independent theme memory for each game mode.
* **Modern Glassmorphism UI & Navigation**: Built with card-styled floating page panels, dynamic focus outlines, and recursive parent background walking. Features a new split import button layout on the main dashboard for quick access to single or bulk imports, and a persistent bottom action controls grid.
* **Context-Aware Relative Imports**: Resolves staging directories and assets contextually based on the active target game mode (FFX vs. FFX-2) without redundant path warnings.
* **Theme-Aware Tooltips**: Custom hover tips integrated into all settings, fields, buttons, and navigation tabs, automatically updating color palettes on theme changes, with custom hover conflict maps.
* **Safety & Diagnostics Panel**: Monitors storage space, validates write permissions, identifies registry Steam paths, and offers a 1-click safe-mode reset button to disable all mods instantly.
* **Viewable Console System Log**: Dedicated button in settings to pop out live mod manager logs into a separate, scrollable console log window.
* **Dotted Class & Python Executable Runner**: Run dotted class imports, raw scripts (`.py`), or pre-compiled binaries (`.exe`) dynamically inside the plugin system.
* **Installed Plugins Manager**: Double-tabbed notebook layout to browse remote registries or manage installed plugins, supporting toggling plug-in states (enable/disable) and clean plugin deletion.
* **IPC API Socket Bridge**: Built-in JSON-RPC server (listening on localhost:8692 or custom configured port) to stream logs, synchronize state, and broadcast events to plugins.
* **Shared Memory Access API**: Read and write game process memory hooks (`ReadProcessMemory` / `WriteProcessMemory`) for trainers, overlays, and live capture helpers.
* **Auto-Generated Settings UI**: Automatically generates configuration fields (booleans, integers, strings, selects) in the settings panel based on custom schemas defined in `plugin.json`.
* **Pip Dependency Auto-Installer**: Automatically isolates, installs, and loads required python packages to a local folder during plugin discovery.
* **Multi-Game Mod Wizard**: Auto-generates starter files, directories, and structures targeted specifically for FFX or FFX-2.
* **Bulletproof Process Unlocker**: Automatically detects and terminates active plugin processes before updating, reinstalling, or deleting to prevent Windows file lock errors.

---

## ⚙️ Fahrenheit Modding Framework Support

When the manager detects `fahrenheit/bin/fhstage0.exe` in the game folder:
1. **Status detection:** Changes the status pill to `🟢 Active Mod Loader Detected (Fahrenheit Framework)`.
2. **Launch execution:** Bypasses Steam launching and executes the game wrapper:
   ```bash
   fhstage0.exe "[absolute_path_to_game]\FFX.exe"
   ```
3. **Load Order Sorting:** Enabled mods are ordered inside the extensionless plaintext file `fahrenheit/mods/loadorder`. The manager provides **Move Up** and **Move Down** controls to physically sort mod priority on the fly.
4. **VBF Layout Mirroring:** Standard mod directories (like `ffx_ps2` or `ffx_data`) are automatically translated into Fahrenheit's virtual path structure:
   `fahrenheit/mods/{mod_id}/efl/x/FFX_Data/`
5. **PascalCase Manifests:** The manager automatically generates case-sensitive `{id}.manifest.json` files using exact properties matching Fahrenheit's C# record parser:
   ```json
   {
     "Id": "my_mod_id",
     "Name": "My Cool Mod",
     "Desc": "A short description.",
     "Authors": "Author Name",
     "Version": "1.0.0",
     "Link": "",
     "Dependencies": [],
     "LoadAfter": [],
     "Flags": "NONE"
    }
    ```

---

## 📁 Repository Structure & Workflow

The manager introduces a unified loader-agnostic layout:
* **Repository Folder:** `data/mods_disabled/` (Where all mod directories and original assets reside when inactive).
* **Enabled (Traditional loaders):** Files are moved into `data/mods/`.
* **Enabled (Fahrenheit Framework):** Files are mapped and moved into `fahrenheit/mods/{id}/efl/x/FFX_Data/`.

---

## 🖼️ Mod Visual Previewer Guide

The manager features a live graphical preview card in the mod details panel to display screenshots or covers of your mods.

### Staging Preview Images
To add visual previews to your mods:
1. Save your screenshots using any standard image format (**`.png`**, **`.jpg`**, **`.jpeg`**, **`.webp`**, **`.bmp`**).
2. Name them using any of the following supported conventions:
   * **Primary Hero Covers**: `preview.png`, `cover.png`, `mod_preview.png`
   * **Numbered Sequences (1–5)**: Up to 5 additional screenshots using `preview`, `cover`, `screenshot`, or `mod_preview`.
   * **Flexible Number Separators**: You can use an underscore (`_`), a hyphen (`-`), or no separator at all!
     * *Direct numbering*: `preview1.png`, `cover2.png`, `screenshot3.png`
     * *With underscore*: `preview_1.png`, `cover_2.png`, `screenshot_3.png`
     * *With hyphen*: `preview-1.png`, `cover-2.png`, `screenshot-3.png`
3. Place these image files **directly in the root** of your mod's directory (alongside `modinfo.spiramod`).

### Dropdown & Resolution
* **Automatic Import Resolution**: During ZIP or folder imports, the manager recognizes all standard preview image conventions and stages them at the root automatically without raising path-alignment warnings.
* **Selection Combobox**: If multiple matching preview images are found, the preview card renders a dropdown selector sorted in natural numerical and priority order, allowing users to flip between screenshots in real-time.

---

## 🛠️ Development & Building

If you are a developer looking to build or contribute to the project:

### Prerequisites
* Python 3.10+
* Tkinter (standard GUI library)

### Building Standalone Executable
To compile the Python script into a single, optimized `.exe` distribution:
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Build via the compilation script:
   ```bash
   python compile_mod_manager.py
   ```
The compiled executable will be located in the `dist/SpiraModManager.exe` directory.

### Custom Plugin Index
The **Plugin Browser** fetches from `plugins.json` in the remote repository. The format is structured as follows:
```json
[
  {
    "id": "my_custom_plugin",
    "name": "My Custom Plugin",
    "creator": "Author Name",
    "version": "1.0.0",
    "description": "Short summary of plugin.",
    "icon": "🔌",
    "download_url": "https://github.com/user/repo/archive/refs/tags/v1.0.0.zip"
  }
]
```

---

## 📄 License & Credits

Final Fantasy X / X-2 HD Remaster is a trademark of Square Enix.  
This tool is created as an open-source contribution for the Final Fantasy modding community.
