# FFX Mod Manager Project Backlog & Brainstorm Memory

This file serves as the long-term memory for tracking feature ideas, polishes, and community requests. Items will remain here until they are either completed or explicitly discarded.

---

## 💡 Future Feature Backlog

### 1. Integrated External Tools Quick-Launcher (Proposed)
* **Goal**: Turn the mod manager into the central hub/toolkit for Spira modding.
* **Details**:
  * Add a "Toolkit" section to configure executable paths for tools like *VBF Browser*, *FFXED Save Editor*, *MemorySumChecker*, and *Farplane*.
  * Launch external utilities directly, passing active mod/save file arguments where applicable.

### 2. Advanced Conflict Resolution Matrix (Proposed)
* **Goal**: Provide visual control over overlapping file conflicts.
* **Details**:
  * Show a clean list/tree-view of colliding file paths across active mods.
  * Allow users to select which mod's version "wins" the priority override per file.

### 3. One-Click Nexus Mod Download Integration (`nxm://` protocol) (Proposed)
* **Goal**: Register the mod manager with the OS to handle Nexus link downloads.
* **Details**:
  * Command-line argument handler to download files directly via Nexus API and install them immediately.

### 4. Button Theme Colorizations (Proposed)
* **Goal**: Style the standard/TTK buttons to match the active custom themes.
* **Details**:
  * Integrate button background, foreground/text, hover, and pressed states into the JSON theme loader.
  * Define semantic button colors directly inside the theme JSON files (e.g. `themes/*.json`) so users can customize them for their own themes.
  * Implement semantic coloring categories across all tabs:
    * **Action/Accept Buttons** (`⚡ Enable`, `📥 Backup`, `⏪ Restore`, `🆕 Create`, `📥 Import`): Positive/primary colors (e.g. defined by `"btn_accept_bg"` and `"btn_accept_fg"`).
    * **Caution/Danger Buttons** (`🗑️ Delete`, `⏪ Disable`, `Safe Reset`): High-contrast warning colors (e.g. defined by `"btn_caution_bg"` and `"btn_caution_fg"`).
    * **Utility/Refresh Buttons** (`🔄 Refresh`, `📂 Open Folder`): Neutral or secondary theme colors (e.g. defined by `"btn_utility_bg"` and `"btn_utility_fg"`).

### 5. Centralized Settings & Customization for Plugins (Proposed)
* **Goal**: Give players dynamic, GUI-driven control over plugin properties and behaviors.
* **Details**:
  * Build a **Global Plugin Settings Card** in the Settings tab of FFXMM.
  * **Hotkey Rebinding**: Allow users to customize toggle keys (e.g. rebinding `F8` or `F9`) directly in the manager.
  * **Overlay Appearance**: Dynamic controls for transparency/opacity, font sizes, snapped screen positioning (Top-Right, Bottom-Left), and click-through lock.
  * **Toggle Status**: Enable/disable individual trackers on/off dynamically.

### 6. Main Manager & Plugin Inter-Process Communication (IPC) (Proposed)
* **Goal**: Sync status, notifications, and logs between background overlay processes and FFXMM.
* **Details**:
  * Implement a lightweight named pipe or socket IPC hook inside FFXMM.
  * **Real-time Status Sync**: Display live plugin stats (e.g. "Achievements: 12/50 unlocked" or "FFX.exe Connected") directly in FFXMM.
  * **Unified Logs**: Route warning/error logs from active trackers back to the Mod Manager's central console log window.

### 7. Core Game Memory Hook API (Proposed)
* **Goal**: Consolidate memory scanning and handles inside FFXMM to simplify plugin code.
* **Details**:
  * Run a master background game-hook thread in FFXMM to manage the process handle and UAC elevation checks.
  * Expose a clean, high-level wrapper API (e.g. `game.read_int()`) for plugins to scan memory without duplicating hex scanning or `ctypes` code.

### 8. Mod-to-Plugin Integrations (Proposed)
* **Goal**: Allow active mods to supply custom content directly to active plugins.
* **Details**:
  * **Mod-Specific Guides**: Retranslation or story mods can bundle `walkthrough.json` to override the overlay walkthrough dynamically when activated.
  * **Gameplay Overhaul Compatibility**: Re-balance or recipe mods can bundle custom recipe lists to automatically update the Rikku's Mix Calculator plugin database.

### 9. Open Plugin Developer SDK & Extensible Runner (Proposed)
* **Goal**: Enable any mod creator or community member to write and test plugins easily.
* **Details**:
  * **Dynamic Python Runner**: Execute raw `.py` scripts (`tracker.py` / `gui.py`) directly from the manager using a bundled Python interpreter, bypassing PyInstaller compilation requirements.
  * **Simplified UI Scaffold**: Expose simple theme-aware widgets that automatically match active theme colors and hover animations.
  * **Template Scaffolder**: A button in Settings to auto-generate a fresh, working starter plugin template for immediate modification.

---

## 💾 Done / Completed Track
* [x] **Scrollable Settings Tab & Unified Directories Layout** (Next_Release)
* [x] **Compact Mods Tab Buttons Layout** (Next_Release)
* [x] **Expanded Game-Themed UI Palettes**: custom JSON color presets (Yuna Summoner, Rikku Thief, Al Bhed Teal, Sin Ominous, Chocobo Yellow, Zanarkand Neon) parsed and loaded automatically.
* [x] **UnX Texture Mod Auto-Specialization**: detect, wrap, and normalize loose texture files under `UnX_Res/inject/textures/`.
* [x] **Dual-Game Switching**: isolated mods/configurations between FFX and FFX-2.
* [x] **Saves & Backups Manager**: automatic location, custom labels, and backup/restores.
* [x] **Mod Creator Template Form**: multi-field mod creation wizard with folder pre-generation.
* [x] **Hover Tooltips**: custom dynamic themed tooltips on active mod cards.
* [x] **Styled Plugins Tab Grouping**: dynamic sidebar container separation with highlighted borders for plugins.
