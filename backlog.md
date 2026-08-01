# Spira Mod Manager Project Backlog & Brainstorm Memory

This file serves as the long-term memory for tracking feature ideas, polishes, and community requests for the main application.

---

## 🖥️ Main App Backlog (Proposed)

### 1. Advanced Conflict Resolution Matrix (Proposed)
* **Goal**: Provide visual control over overlapping file conflicts.
* **Details**:
  * Show a clean list/tree-view of colliding file paths across active mods.
  * Allow users to select which mod's version "wins" the priority override per file.

### 2. One-Click Nexus Mod Download Integration (`nxm://` protocol) (Proposed)
* **Goal**: Register the mod manager with the OS to handle Nexus link downloads.
* **Details**:
  * Command-line argument handler to download files directly via Nexus API and install them immediately.

### 3. Interactive Character Dashboard Profiles (Proposed)
* **Goal**: Personalize the manager with FFX/FFX-2 character styles.
* **Details**: Switch themes based on standard profiles (Tidus, Yuna, Rikku, Auron) and automatically shift the active color schemes, ambient artwork, and background details to match.

### 4. Drag-and-Drop FMOD Music Injector (Proposed)
* **Goal**: Customize soundtracks easily.
* **Details**: Convert MP3/WAV files to FMOD bank formats to swap audio files or combine original/arrange tracks.

### 5. Mod Presets and Modpack Bundling (Proposed)
* **Goal**: Share and download custom configurations.
* **Details**: Export active mod directories as single `.ffxpreset` files that automatically download and align dependencies.

### 6. Nexus Mod Update Checker (Proposed)
* **Goal**: Verify if installed mods have newer files available.
* **Details**: Query the Nexus Mods API using metadata IDs to cross-reference versions and display dynamic update notification badges.

### 7. Fahrenheit Integration & Manifest Editor (Proposed)
* **Goal**: Fully support advanced Fahrenheit manifest customization.
* **Details**: 
  * Visual manifest editor interface to configure priorities, dependencies (`LoadAfter`), and custom configuration option parameters.
  * Integrate custom manifest flags when custom flag options are defined/supported.

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
* [x] **Button Theme Colorizations**: styled standard/TTK buttons to match semantic custom themes (Action, Success, Caution, Utility) dynamically (Next_Release).
* [x] **Open Plugin Developer SDK & Extensible Runner**: support raw scripts, executables, dotted path imports, background/utility/listener categories, and a starter template generator. (Next_Release)
* [x] **Advanced Plugin Developer SDK (Phase 2)**: Dynamic schema settings UI, local socket JSON-RPC server (localhost:8692), direct memory read/write API, automated pip dependency installer, and fine-grained pub/sub events with hot-reloading. (Next_Release)
* [x] **FFX Codec String Terminator Fix**: resolved premature string cutoff when text command parameters (like colors/variables) were 0x00 (Next_Release).
* [x] **Integrated External Tools Quick-Launcher (Plugin Toolkit)**: configures and quick-launches FFX modding utilities dynamically via the Plugin Toolkit Actions card (Next_Release).
* [x] **Local Cloud Save Auto-Sync**: automatically backs up FFX/FFX-2 saves to Google Drive/OneDrive on game exit (Next_Release).
* [x] **Live Graphic Mod Asset Previewer**: parse and view texture images inside mod packages in a side panel.
