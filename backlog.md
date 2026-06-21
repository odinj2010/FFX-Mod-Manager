# FFX Mod Manager Project Backlog & Brainstorm Memory

This file serves as the long-term memory for tracking feature ideas, polishes, and community requests. Items are split between the Main Application and the Plugin Ecosystem, and remain here until they are either completed or explicitly discarded.

---

## 🖥️ Main App Backlog (Proposed)

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

### 4. Modern Glassmorphism UI Overhaul (Completed)
* **Goal**: Modernize the Tkinter UI to have a sleeker, web-like premium appearance.
* **Details**: Implement semi-transparent glass card panels, rounded frame overlays, ambient glowing borders, and high-quality custom icons.

### 5. Interactive Character Dashboard Profiles (Proposed)
* **Goal**: Personalize the manager with FFX/FFX-2 character styles.
* **Details**: Switch themes based on standard profiles (Tidus, Yuna, Rikku, Auron) and automatically shift the active color schemes, ambient artwork, and background details to match.

### 6. Live Graphic Mod Asset Previewer (Proposed)
* **Goal**: View mod graphics directly in the manager before enabling.
* **Details**: Parse `.dds` or `.png` texture files inside mod packages to show visual clothing or UI previews in a side panel.

### 7. Built-in VBF Archive Explorer (Proposed)
* **Goal**: Native unpacking and editing of main game archives.
* **Details**: Add a lightweight `.vbf` parser to inspect and patch assets without requiring third-party tools.

### 8. Drag-and-Drop FMOD Music Injector (Proposed)
* **Goal**: Customize soundtracks easily.
* **Details**: Convert MP3/WAV files to FMOD bank formats to swap audio files or combine original/arrange tracks.

### 9. Visual Save Game Data Editor (Proposed)
* **Goal**: Edit player inventory and coordinates natively.
* **Details**: Embed a visual save modifier into the Saves tab to adjust Gil, stats, sphere grid nodes, and coordinates.

### 10. Mod Presets and Modpack Bundling (Proposed)
* **Goal**: Share and download custom configurations.
* **Details**: Export active mod directories as single `.ffxpreset` files that automatically download and align dependencies.

### 11. Local Cloud Save Auto-Sync (Proposed)
* **Goal**: Keep saves backed up to the cloud automatically.
* **Details**: Hook into local Google Drive/OneDrive/Dropbox folders to sync save backups upon game exit.

### 12. Steam Deck / Proton Compatibility Optimization (Proposed)
* **Goal**: Seamless Linux controller and path mapping.
* **Details**: Auto-detect Steam Deck directories and bind UI interactions to standard Proton gamepad events.

---

## 🧪 Plugins & Companion Overlays Backlog (Proposed)

### 13. Centralized Settings & Customization for Plugins (Proposed)
* **Goal**: Give players dynamic, GUI-driven control over plugin properties and behaviors.
* **Details**:
  * Build a **Global Plugin Settings Card** in the Settings tab of FFXMM.
  * **Hotkey Rebinding**: Allow users to customize toggle keys (e.g. rebinding `F8` or `F9`) directly in the manager.
  * **Overlay Appearance**: Dynamic controls for transparency/opacity, font sizes, snapped screen positioning (Top-Right, Bottom-Left), and click-through lock.
  * **Toggle Status**: Enable/disable individual trackers on/off dynamically.

### 14. Main Manager & Plugin Inter-Process Communication (IPC) (Proposed)
* **Goal**: Sync status, notifications, and logs between background overlay processes and FFXMM.
* **Details**:
  * Implement a lightweight named pipe or socket IPC hook inside FFXMM.
  * **Real-time Status Sync**: Display live plugin stats (e.g. "Achievements: 12/50 unlocked" or "FFX.exe Connected") directly in FFXMM.
  * **Unified Logs**: Route warning/error logs from active trackers back to the Mod Manager's central console log window.

### 15. Core Game Memory Hook API (Proposed)
* **Goal**: Consolidate memory scanning and handles inside FFXMM to simplify plugin code.
* **Details**:
  * Run a master background game-hook thread in FFXMM to manage the process handle and UAC elevation checks.
  * Expose a clean, high-level wrapper API (e.g. `game.read_int()`) for plugins to scan memory without duplicating hex scanning or `ctypes` code.

### 16. Mod-to-Plugin Integrations (Proposed)
* **Goal**: Allow active mods to supply custom content directly to active plugins.
* **Details**:
  * **Mod-Specific Guides**: Retranslation or story mods can bundle `walkthrough.json` to override the overlay walkthrough dynamically when activated.
  * **Gameplay Overhaul Compatibility**: Re-balance or recipe mods can bundle custom recipe lists to automatically update the Rikku's Mix Calculator plugin database.

### 17. Open Plugin Developer SDK & Extensible Runner (Proposed)
* **Goal**: Enable any mod creator or community member to write and test plugins easily.
* **Details**:
  * **Current State & Limitations**:
    * Right now, the manager's loader has a specific expectation: it reads `plugin.json` and parses `entry_point` in the format `module_name.class_name` (like `gui.RikkuMixTab`), imports the module, instantiates the class, and passes a Tkinter Frame (`tab_frame`) for the plugin to draw its interface. The `tracker.py` (compiled to `tracker.exe`) is then launched from the GUI class as a background helper process.
    * If a developer wants to make a plugin that doesn't need a UI tab (like a Discord Rich Presence status updater, an automatic save backup script, or a hotkey overlay that runs completely in the background), they are currently forced to write a dummy Tkinter UI class just to make the manager happy.
  * **Dynamic Python Runner**: Execute raw `.py` scripts (`tracker.py` / `gui.py`) directly from the manager using a bundled Python interpreter, bypassing PyInstaller compilation requirements.
  * **Simplified UI Scaffold**: Expose simple theme-aware widgets that automatically match active theme colors and hover animations.
  * **Flexible Component-Based Architecture**: Make the plugin loader incredibly flexible by defining a `"type"` property inside `plugin.json` (or an array of components). This tells FFXMM exactly how to handle and execute the plugin:
    1. **Tab Plugins (Standard)**:
       * Manifest: `{"name": "Rikku's Mix Calculator", "type": "tab", "entry_point": "gui.RikkuMixTab"}`
       * Behavior: FFXMM renders a dedicated sidebar button and loads the UI component.
    2. **Background Service Plugins (No GUI)**:
       * Manifest: `{"name": "Discord Rich Presence", "type": "background", "entry_point": "presence.py"}`
       * Behavior: FFXMM doesn't create a sidebar tab. Instead, it spins up `presence.py` as an asynchronous background thread or process the moment the manager launches and shuts it down when FFXMM closes.
    3. **Command/Utility Plugins (One-click tools)**:
       * Manifest: `{"name": "Save Game Decryptor", "type": "utility", "entry_point": "decrypt.py", "button_text": "🔓 Decrypt Selected Save"}`
       * Behavior: FFXMM adds the action button automatically to a shared "Toolkit" panel. Clicking it simply runs `decrypt.py` with active game context.
    4. **Event Listener Plugins (Reactive scripts)**:
       * Manifest: `{"name": "Game Launch Optimizer", "type": "listener", "entry_point": "optimize.py", "events": ["on_game_launch", "on_game_exit"]}`
       * Behavior: FFXMM imports the script and triggers its callback functions when the specified events occur.
  * **Language Portability**: If the entry point is an executable (e.g. `entry_point: "my_tool.exe"`), FFXMM can spawn it as a subprocess, allowing plugins to be written in C++, C#, Go, Rust, or Python.
  * **Zero Boilerplate**: If a developer just wants to run a background Python script, their entire plugin is just `plugin.json` and a single script file—no Tkinter code, no GUI wrapping, and no compilers required.
  * **Legacy Compatibility**: Gracefully auto-wrap older single-entry point plugin manifests into a standard single-tab component internally.
  * **Template Scaffolder**: A button in Settings to auto-generate a fresh, working starter plugin template for immediate modification.

### 18. Monster Arena Capture Live Overlay (Proposed)
* **Goal**: Eliminate manual checks at the Calm Lands arena.
* **Details**: Read live game memory to render a HUD overlay tracking captures (e.g. Calm Lands: 6/10 Coeurls) for active areas.

### 19. Rikku Active Battle Mix Suggester (Proposed)
* **Goal**: Suggest the best Mixes dynamically during active turns.
* **Details**: Read in-battle inventory and target enemy vulnerabilities to overlay optimal Rikku Mix combinations.

### 20. Al Bhed Translator and Collection Companion (Proposed)
* **Goal**: Track missing primers and translate vocabulary.
* **Details**: Read save data to list missing Primers and provide a side-panel dictionary translator tool.

### 21. Blitzball Scouting and Tech Tracker (Proposed)
* **Goal**: Assist team building and tech copy alerts.
* **Details**: Track player contract timers, tech copy availability, and tournament schedules in an active HUD.

### 22. Interactive Sphere Grid Node Planner (Proposed)
* **Goal**: Design and share character path maps.
* **Details**: Render standard and expert sphere grid planners, allowing users to calculate SLvs and export build files.

### 23. Live Memory Offset Online Database Sync (Proposed)
* **Goal**: Auto-update game memory offsets if Steam patches the game.
* **Details**: Pull latest memory offset JSON maps from a remote GitHub repository to prevent plugins from breaking during game updates.

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
* [x] **Modern Glassmorphism UI Overhaul**: reorganize page frames as floating cards with dynamic 1px glowing/accent borders, subframe dynamic styling, and theme compatibility (Next_Release).
