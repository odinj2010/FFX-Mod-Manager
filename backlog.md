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
