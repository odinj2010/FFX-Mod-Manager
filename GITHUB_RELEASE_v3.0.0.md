# FFX Mod Manager v3.0.0 - Extensible Plugin API & Dual-Game Switcher

This major release introduces a fully refactored, namespace-isolated plugin system designed for public and third-party plugin development, alongside native multi-game switching between **Final Fantasy X** and **Final Fantasy X-2**. It includes new developer hooks, dynamic UI hot-reloads, installation safety features, compiler automation, isolated paths, custom themes, and a dedicated saves and backups manager.

---

## 🚀 What's New Since v2.2.0

### 🎮 Dual-Game Partition Isolation
*   **Separated Mod Directories**: Fully separates FFX and FFX-2 mod databases and configuration tracks.
*   **Target Staging Directories**: Configured custom directories for FFX-2 (disabled mods in `data/mods_disabled_x2/` and active mods in `data/mods/ffx2_data/` for EFL compatibility).
*   **Celsius Purple Theme**: The launcher automatically switches to a Rikku-themed Purple/Magenta interface palette when targetting FFX-2.

### 🔌 Extensible Plugin API & Lifecycle Hooks
*   **Isolated Plugin Namespaces**: Plugins are loaded dynamically inside their own protected namespace (`sys.modules[f"plugin_{dir_name}"]`), allowing developers to use relative package imports without namespace collisions.
*   **Plugin Lifecycle Hooks**: Added developer API hooks like `on_unload()` (for stopping background threads and closing files/sockets cleanly) and `on_mods_refreshed()` (triggered when the mod list updates).
*   **System Cache Purging**: Purges cached modules from memory when a plugin is updated, allowing instant testing of code changes without restarting the mod manager.

### 📦 Double-Tabbed Installed Plugins Manager
*   **Notebook Switcher**: Adds a double-tabbed "Plugin Browser" containing:
    *   **Plugin Directory**: To fetch and download available community plugins from GitHub.
    *   **Installed Plugins**: Lists locally parsed active/inactive plugins on disk.
*   **Enable / Disable / Delete Toggles**: Users can now enable or disable plugins dynamically (hiding them from the sidebar) or delete them entirely with a single click.

### ⚙️ Plugin Settings Sub-Tabs & Hot-Reloading
*   **Dedicated Settings Notebooks**: Walkthrough and Achievements plugins now feature built-in Settings sub-tabs.
*   **Active HUD Customization**: Users can configure overlay positioning, opacity/transparency levels, scales, and trigger hotkeys in-app.
*   **Dynamic Setting Reloading**: Achievement overlays monitor the configuration file (`overlay_config.json`) using timestamp polling (`os.path.getmtime`), applying saved settings instantly in-game without a tracker restart.

### 🛠️ Safety Safeguards & Build Automation
*   **Process Unlocker**: The mod manager automatically terminates a plugin's background tracker process before installing, updating, or deleting it, preventing Windows file-lock errors (`PermissionError`).
*   **Auto-Discovering Compiler**: Added a compiler utility (`compile_mod_manager.py`) that searches `plugins/`, compiles trackers with PyInstaller automatically, and stages the executables for release.

### 💾 Save Game & Backups Manager
*   **Unified Backup Vault**: Added a dedicated **Saves** manager page mapping live PC save slots (`ffx_###` / `ffx2_###`) based on the active game target.
*   **Description Metadata**: Saves backups are written inside isolated local log directories under custom tag labels (e.g. *"Before Seymour"*), showing sizes, slots, and timestamps.
*   **One-Click Restore**: Supports instant swap overwrites to restore backup saves back into active Documents game storage.

### 🆕 Mod Creator Template Wizard
*   **Creation Wizard**: Replaced the basic name query with a multi-field dialog template where developers can input the Name, Author, Version, Description, and Category.
*   **Target Staging**: Pre-generates conventional virtual directories (`ffx_data/` or `ffx2_data/`) and formats folder paths inside the disabled mods repository based on the targeted game.

### 🖼️ UnX Texture Auto-Specialization
*   **Auto-Detection**: Scans imported `.zip` or `.rar` mod archives for `.dds` texture assets.
*   **Normalized Folder Wrap**: Automatically restructures loose texture files or partial paths (such as raw `textures/` or `inject/` folders) and wraps them under the correct `UnX_Res/inject/textures/` structure.

### 🎨 Expanded UI Color Themes & Dynamic Reloading
*   **Independent Theme Memory**: Refactored config logic to store chosen themes separately for each game target (`selected_theme_ffx` and `selected_theme_ffx2`). Switching between FFX and FFX-2 modes now automatically restores your preferred theme for that specific game.
*   **Dynamic JSON Presets**: Automatically parses and loads custom-themed palettes inside the `themes/` directory on boot (Midnight Dark, Yuna Summoner, Rikku Thief, Al Bhed Teal, Sin Ominous, Chocobo Yellow, Zanarkand Neon).
*   **Treeview Colorization**: Mapped all list views (`Treeview` items) to use the active theme's secondary color `text_dim` (instead of standard `text_color`) to color save files list text cleanly with each theme's accent color (e.g. Yuna Summoner's rose pink).
*   **Dynamic Notebook Tab & Scrollbar Retheming**: Fixed an issue where `ttk.Notebook` tabs and horizontal scrollbars did not update their colors immediately when the theme was changed, requiring an application restart. They now reload styles dynamically in real-time.

### 🖥️ UI Layout Enhancements & Hover Tooltips
*   **Persistent Bottom Controls**: Re-architected the Mods tab packing layout. The action control buttons frame is now anchored to the bottom first, ensuring they are always visible and clickable.
*   **Interactive Tooltips**: Added lightweight, custom-drawn hover tooltips to action buttons, the game selector, and individual mods cards, showing descriptions, creator information, and versions.
*   **Conflict Warnings**: Hovering over conflict status markers shows popups highlighting the list of conflicting mod names.
