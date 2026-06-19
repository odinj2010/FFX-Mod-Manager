# FFX Mod Manager v3.0.1 - Theme Memory & UI Retheming Hotfix

This release resolves UI issues and theme persistence bugs introduced in v3.0.0.

---

## 🚀 Fixes & Changes

*   **Independent Theme Memory**: Switching between FFX and FFX-2 modes now correctly remembers and restores your preferred theme for each game mode (saved under `selected_theme_ffx` and `selected_theme_ffx2` in configuration), rather than resetting back to defaults.
*   **Settings Selector Dropdown Sync**: The settings theme selector combobox now updates dynamically to display the correct theme name when game target switching auto-applies a theme change.
*   **Dynamic Notebook Tab & Scrollbar Retheming**: Fixed an issue where `ttk.Notebook` tabs (such as the Plugin Browser's "Plugin Directory" and "Installed Plugins" tabs) and horizontal scrollbars did not update their colors immediately when the theme was changed, requiring an application restart. They now reload styles dynamically in real-time.
*   **Partitioned Game Save Paths**: Separated document save locations between `saves_dir` (FFX) and `saves_dir_x2` (FFX-2) inside configuration, automatically swapping save path inputs in settings upon game mode selection.
*   **Absolute Configuration Persistence**: Resolved directory configuration saving issues by resolving the `ffxmm_config.json` path absolutely to the application installation directory rather than relying on the process CWD.
*   **Settings Path Reversion Fix**: Resolved a bug where updating game directory folders in settings was immediately overridden back to older cached values.
*   **UnX Texture Destination Specialization**: Corrected FFX-2 mod path routing to install `UnX_Res/` textures directly to the root game directory where UnX reads them, while keeping standard files in the `ffx2_data` folder structure.
*   **Directory Change Logs**: Added Console Log printouts when updating the game folder path in Settings.
*   **Unified Mod Import Dialog & Expanded Fields**: Replaced fading askstring popups with a unified, custom-styled dialog modal during mod archive imports (only triggers if mod lacks pre-existing metadata to respect Credits Lock), and added **Category**, **Nexus Mod ID**, and **Mod Link** input support to both the project creation and mod import dialog windows.
*   **Direct Project Creation Imports**: Added **Import File(s)** and **Import Folder(s)** button support in the "Create New Mod Project" dialog to easily stage and copy external files/folders into the new project under correct game subdirectories automatically.
*   **Scoped Unmanaged Files Scanner**: Scopes the loose files importer scanner by active game mode to avoid false cross-game unmanaged files warnings.
