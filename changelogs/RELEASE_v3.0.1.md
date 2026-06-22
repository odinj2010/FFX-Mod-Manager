# FFX Mod Manager v3.0.1 - The Hotfix Update

This release contains critical UI hotfixes and styling refinements immediately following the v3.0.0 launch.

---

## 🚀 Improvements & Fixes

### 🎨 Independent Theme Memory
*   **Game-Specific Selections**: Refactored the config loader, saver, and game mode switcher to store user-selected themes separately under `selected_theme_ffx` and `selected_theme_ffx2`. Switching between game modes (FFX / FFX-2) now correctly recalls and applies the custom theme chosen for that specific game mode, rather than forcing hardcoded defaults.
*   **Dropdown Selection Sync**: Synchronized the settings theme selector drop-down so it updates instantly when target game switches trigger auto-theming changes.

### 🖥️ Dynamic Notebook Tab & Scrollbar Retheming
*   **Dynamic Styles Application**: Fixed an issue where `ttk.Notebook` tabs (such as the Plugin Browser's "Plugin Directory" and "Installed Plugins" tabs) and horizontal scrollbars did not update their colors immediately when the theme was changed, requiring an application restart. They now reload styles dynamically in real-time.

### 💾 Game Saves & Path Settings Refinements
*   **Partitioned Game Save Paths**: Split document save folders between `saves_dir` (FFX) and `saves_dir_x2` (FFX-2) inside the configuration. The Settings tab entry field now dynamically swaps paths when switching game modes, ensuring you can manage backups for both game targets independently.
*   **Absolute Configuration Persistence**: Resolved a CWD issue where the configuration file `ffxmm_config.json` was read/written relatively. It is now resolved absolutely to the application installation directory, ensuring setting changes (such as custom game folders) persist correctly when launched via Steam or scripts.
*   **Directory Reversion Fix**: Fixed a bug where updating the game folder path in settings would immediately revert to the previous path due to early path initialization.
*   **UnX Texture Destination Specialization**: Corrected UnX texture mod installation routing to move `UnX_Res/` files directly to the root game directory (where the injector loads them) rather than storing them inside `data/mods/ffx2_data` in FFX-2 mode. Standard mods continue to install to the designated game-subfolders.
*   **Log Updates**: Added log print notifications when updating game directory configurations.

### 📥 Mod Archiving & Scanner Improvements
*   **Unified Mod Import Dialog & Expanded Fields**: Replaced the sequential, fading `simpledialog` input popup windows when importing a `.zip`/`.rar` archive with a single, custom-themed dialog matching the "Create New Mod" creation form, and expanded both dialogs to include **Category** (combobox dropdown selection), **Nexus Mod ID**, and **Mod Link** fields. These fields are written directly to `modinfo.ffxmod`. Pre-existing mod metadata fields (Credits Lock) are automatically parsed and carried forward without prompt.
*   **Direct Project Creation Imports**: Added **Import File(s)** and **Import Folder(s)** buttons directly inside the "Create New Mod Project" dialog window, allowing authors to copy required external files or full directory structures into the new mod project at initialization. Staged files are moved under the correct targeted game subfolder, and the project's metadata files registry is compiled dynamically during creation.
*   **Scoped Unmanaged Files Scanner**: Scopes the loose files importer scanner to only index directories matching the active game mode (FFX vs FFX-2). This prevents the Mod Manager from falsely prompting to import enabled FFX-2 mod files when launching or restarting in FFX mode.
