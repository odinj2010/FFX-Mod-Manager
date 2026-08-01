# Spira Mod Manager Plugin Backlog & Companion Overlays

This file serves as the tracking and memory document for the plugin ecosystem and companion overlay features.

---

## 🧪 Plugins & Companion Overlays Backlog (Proposed)

### 1. Centralized Settings & Customization for Plugins (Completed)
* **Goal**: Give players dynamic, GUI-driven control over plugin properties and behaviors.
* **Details**:
  * Build a **Global Plugin Settings Card** in the Settings tab of SpiraMM.
  * **Hotkey Rebinding**: Allow users to customize toggle keys (e.g. rebinding `F8` or `F9`) directly in the manager.
  * **Overlay Appearance**: Dynamic controls for transparency/opacity, font sizes, snapped screen positioning (Top-Right, Bottom-Left), and click-through lock.
  * **Toggle Status**: Enable/disable individual trackers on/off dynamically.

### 2. Main Manager & Plugin Inter-Process Communication (IPC) (Completed)
* **Goal**: Sync status, notifications, and logs between background overlay processes and SpiraMM.
* **Details**:
  * Implement a lightweight named pipe or socket IPC hook inside SpiraMM.
  * **Real-time Status Sync**: Display live plugin stats (e.g. "Achievements: 12/50 unlocked" or "FFX.exe Connected") directly in SpiraMM.
  * **Unified Logs**: Route warning/error logs from active trackers back to the Mod Manager's central console log window.

### 3. Core Game Memory Hook API (Completed)
* **Goal**: Consolidate memory scanning and handles inside SpiraMM to simplify plugin code.
* **Details**:
  * Run a master background game-hook thread in SpiraMM to manage the process handle and UAC elevation checks.
  * Expose a clean, high-level wrapper API (e.g. `game.read_int()`) for plugins to scan memory without duplicating hex scanning or `ctypes` code.

### 4. Mod-to-Plugin Integrations (Proposed)
* **Goal**: Allow active mods to supply custom content directly to active plugins.
* **Details**:
  * **Mod-Specific Guides**: Retranslation or story mods can bundle `walkthrough.json` to override the overlay walkthrough dynamically when activated.
  * **Gameplay Overhaul Compatibility**: Re-balance or recipe mods can bundle custom recipe lists to automatically update the Rikku's Mix Calculator plugin database.

### 5. Open Plugin Developer SDK & Extensible Runner (Completed)
* **Goal**: Enable any mod creator or community member to write and test plugins easily.
* **Details**:
  * **Dynamic Python Runner**: Execute raw `.py` scripts (`tracker.py` / `gui.py`) directly from the manager using a bundled Python interpreter, bypassing PyInstaller compilation requirements.
  * **Simplified UI Scaffold**: Expose simple theme-aware widgets that automatically match active theme colors and hover animations.
  * **Flexible Component-Based Architecture**: Make the plugin loader incredibly flexible by defining a `"type"` property inside `plugin.json` (or an array of components). This tells SpiraMM exactly how to handle and execute the plugin:
    1. **Tab Plugins (Standard)**: Renders a dedicated sidebar button and loads the UI component.
    2. **Background Service Plugins (No GUI)**: Runs background scripts automatically on manager launch/close.
    3. **Command/Utility Plugins (One-click tools)**: Adds buttons to a shared "Toolkit" panel (e.g., diagnostics, compilers).
    4. **Event Listener Plugins (Reactive scripts)**: Triggers callbacks on manager/game events.
  * **Language Portability**: Support executing binaries (`.exe`), allowing plugins to be written in C++, C#, Go, Rust, or Python.
  * **Template Scaffolder**: Auto-generates starter templates.

### 6. Monster Arena Capture Live Overlay (Proposed)
* **Goal**: Eliminate manual checks at the Calm Lands arena.
* **Details**: Read live game memory to render a HUD overlay tracking captures (e.g. Calm Lands: 6/10 Coeurls) for active areas.

### 7. Rikku Active Battle Mix Suggester (Proposed)
* **Goal**: Suggest the best Mixes dynamically during active turns.
* **Details**: Read in-battle inventory and target enemy vulnerabilities to overlay optimal Rikku Mix combinations.

### 8. Al Bhed Translator and Collection Companion (Proposed)
* **Goal**: Track missing primers and translate vocabulary.
* **Details**: Read save data to list missing Primers and provide a side-panel dictionary translator tool.

### 9. Blitzball Scouting and Tech Tracker (Proposed)
* **Goal**: Assist team building and tech copy alerts.
* **Details**: Track player contract timers, tech copy availability, and tournament schedules in an active HUD.

### 10. Interactive Sphere Grid Node Planner (Proposed)
* **Goal**: Design and share character path maps.
* **Details**: Render standard and expert sphere grid planners, allowing users to calculate SLvs and export build files.

### 11. Live Memory Offset Online Database Sync (Proposed)
* **Goal**: Auto-update game memory offsets if Steam patches the game.
* **Details**: Pull latest memory offset JSON maps from a remote GitHub repository to prevent plugins from breaking during game updates.
