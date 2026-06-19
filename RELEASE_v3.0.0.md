# FFX Mod Manager v3.0.0 - The Extensible Plugin API & Dual-Game Switcher Update

This release introduces a fully refactored, namespace-isolated plugin system designed for public and third-party plugin development, alongside native multi-game switching between **Final Fantasy X** and **Final Fantasy X-2**. It includes new developer hooks, dynamic UI hot-reloads, installation safety features, compiler automation, isolated paths, custom themes, and a dedicated installed plugins manager.

---

## 🚀 Key Features

### 🎛️ Plugin-Specific Settings Sub-Tabs
*   **Settings Isolation**: Re-architected both the Walkthrough and Achievements plugins to support dedicated, self-contained **⚙️ Settings** sub-tabs using a `ttk.Notebook` switcher. This cleans up primary interface panels and groups options cleanly.
*   **Custom Overlay Options**: Added inputs to configure overlay positioning (Left-Half, Right-Half, Top-Half, Bottom-Half), transparency/opacity levels, HUD scale, and trigger hotkeys. All settings are serialized to a local `overlay_config.json` file.
*   **Dynamic Settings Reloading**: Upgraded the background Achievements overlay tracker to monitor `overlay_config.json` changes during gameplay using file modification timestamp polling (`os.path.getmtime`). Saved setting updates are instantly loaded and applied in-game without restarting the tracker.
*   **Overlay Scaling**: Achievements overlay text sizes, icons, cards, and canvas progress bars now scale proportionally based on the selected HUD scale value.

### 📦 Installed Plugins Manager
*   **Notebook Layout**: Refactored the Mod Manager's Plugin Browser to support a double-tabbed layout:
    *   **Plugin Directory**: Browse and download all downloadable/installable plugins from the remote registry.
    *   **Installed Plugins**: Lists all currently installed plugins parsed locally from `plugin.json` descriptors on disk, including custom or local plugins not listed in the remote directory.
*   **Toggle Enable / Disable**: Users can toggle a plugin's status (**🔴 Disable** / **🟢 Enable**) dynamically. Disabling a plugin prevents it from loading or executing at startup and removes its sidebar navigation tab while keeping its files intact.
*   **Plugin Deletion**: Added a **🗑️ Delete** action that prompts for confirmation, automatically terminates any active background overlay trackers to prevent handle locks, and cleanly removes all plugin files from disk.

### 🛠️ Isolated Plugin Namespace & Package Imports
*   **Collision Prevention**: Dynamically loads plugin modules inside a protected package namespace (`sys.modules[f"plugin_{dir_name}"]`). Developers can now safely use standard relative package imports (e.g. `from . import helper`) without crashing or clashing with other installed plugins.
*   **System Cache Purges**: Re-installing or updating a plugin now purges all corresponding cached modules from Python's memory, ensuring developers can test their code changes instantly on reload without restarting the mod manager.

### 🔄 Plugin Lifecycle Hooks & API Events
*   **Resource Cleanup Hook (`on_unload`)**: Added a lifecycle callback method `on_unload()`. When a plugin is deleted or reinstalled, it can stop daemon threads, close socket/WebSocket connections, and release global hotkey listeners to prevent memory and thread leaks.
*   **Mod Event Listener (`on_mods_refreshed`)**: Added an event callback that triggers `plugin.on_mods_refreshed()` whenever the manager scans, enables, disables, or changes the load order priority of active mods.

### 📥 Bulletproof Installation Safeguards
*   **Process Unlocker**: Before updating, reinstalling, or deleting a plugin, the manager automatically detects if the plugin's background tracker process is still active. FFXMM terminates the tracker process first to release Windows file locks, preventing silent directory deletions or `PermissionError` installation failures.

### ⚡ Auto-Discovering Tracker Compiler
*   **PyInstaller Automation**: The builder utility (`compile_mod_manager.py`) now scans the `plugins/` directory, discovers all background overlays (`tracker.py`), compiles them into standalone `tracker.exe` binaries, and copies them to both the release build folder (`dist/plugins/...`) and active development folders (`plugins/...`) for seamless testing.
*   **Out-of-the-Box Compatibility**: Both Achievements and Walkthrough overlays now ship with pre-compiled `tracker.exe` files, allowing them to run on gamers' PCs without requiring a system Python installation.

### 🎮 FFX / FFX-2 Dual-Game switcher
*   **Game Partition Separation**: Isolates mods and configuration tracks between Final Fantasy X and Final Fantasy X-2. A simple selector dropdown is available under the sidebar header.
*   **Targeted Directories**: Custom folders set up for FFX-2 (disabled mods in `data/mods_disabled_x2/` and active mods in `data/mods/ffx2_data/` for External File Loader compatibility).
*   **Auto-Wrapping**: Imported FFX-2 archives that contain loose root files are automatically normalized inside `ffx2_data/` subfolders.
*   **Celsius Purple Theme**: Rikku-themed Purple/Magenta interface palette added, which applies automatically when switching to FFX-2 mode.
*   **Launch Targeting**: Runs FFX-2.exe or FFX.exe based on active selection.

### 💬 Hover Tooltips (Option A)
*   **Contextual Assistance**: Lightweight, custom-drawn hover tooltips added to action buttons, the game selector, and individual mods cards, showing descriptions, creator information, and versions.
*   **Dynamic Theming**: Tooltip backgrounds and border colors match the selected theme instantly.
*   **Conflict Warnings**: Hovering over conflict status markers shows popups highlighting the list of conflicting mod names.

### 🆕 Built-in Mod Creator Template (Option B)
*   **Creation Wizard**: Replaced the basic name query with a multi-field dialog template where developers can input the Name, Author, Version, Description, and Category.
*   **Target Selection**: Choose the targeted game (**FFX** vs **FFX-2**). The manager automatically pre-creates conventional virtual directories (`ffx_data/` or `ffx2_data/`) and formats folder paths inside the disabled mods repository cleanly.

### 💾 Save Game & Backups Manager (Option C)
*   **Unified Backup Vault**: Added a dedicated **Saves** manager page mapping live PC save slots (`ffx_###` / `ffx2_###`) offset directly to game target filters.
*   **Description Metadata**: Backups are written inside isolated local log directories under custom tag labels (e.g. *" Seymour Battle "*), showing sizes, slots, and creation timestamps.
*   **One-Click Restore**: Supports instant swap overwrites to restore backup saves back into active Documents game storage.

### 🗂️ Styled Plugins Tab Grouping
*   **Separated Container**: Grouped dynamic plugin tabs together in an "Active Plugins" panel, keeping them separated from the default/core tools.
*   **Distinct Highlights**: The plugins panel uses a distinct, styled border highlight to clearly distinguish third-party plugins from native mod manager pages.
*   **Conditional Display**: The plugins container automatically hides itself if no plugins are currently loaded or active, maintaining a clean interface.

### 🖼️ UnX Texture Auto-Specialization
*   **Auto-Detection**: Scans imported `.zip` or `.rar` mod archives for `.dds` texture assets.
*   **Normalized Folder Wrap**: Automatically restructures loose texture files or partial paths (such as raw `textures/` or `inject/` folders) and wraps them under the correct `UnX_Res/inject/textures/` structure.
*   **Multi-Game Ready**: Runs for both FFX and FFX-2 modes, ensuring texture mods install correctly with zero manual directory setup or nesting by the player.

### 🖥️ UI Layout Enhancements & Fixes
*   **Persistent Bottom Controls**: Re-architected the Mods tab packing layout. The action control buttons frame is now anchored to the bottom first, ensuring they are always visible and clickable. The mod card lists above it will now shrink and scroll correctly when the window height is resized, rather than clipping the buttons off-screen.
*   **Dynamic Notebook Tab & Scrollbar Retheming**: Fixed an issue where `ttk.Notebook` tabs (such as the Plugin Browser's "Plugin Directory" and "Installed Plugins" tabs) and horizontal scrollbars did not update their colors immediately when the theme was changed, requiring an application restart. They now reload styles dynamically in real-time.


### 🎨 Expanded UI Color Themes
*   **Themed Presets**: Bundled new custom-themed palettes inside the `themes/` directory (plus core definitions), automatically parsed and loaded by the UI engine:
    *   **Yuna Summoner**: Crisp slate-white background and white cards with summoner azure-blue and rose-pink accents.
    *   **Rikku Thief**: Muted olive-green cards and dark green backgrounds with vibrant orange accents representing her FFX-2 thief outfit.
    *   **Al Bhed Teal**: Sleek slate-blue with techno-teal accents themed around Al Bhed machina.
    *   **Sin Ominous**: Dark charcoal with warning crimson accents themed around Sin.
    *   **Chocobo Yellow**: Bright straw background with vibrant yellow chocobo feather accents.
    *   **Zanarkand Neon**: Futuristic midnight-indigo with glowing lavender city-lights accents.

---
*Thank you for being part of the FFX modding community! Report any issues on our GitHub page.*
