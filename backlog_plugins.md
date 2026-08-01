# Spira Mod Manager Plugin Backlog & Companion Overlays

This file serves as the tracking and memory document for the plugin ecosystem and companion overlay features.

---

## 🧪 Plugins & Companion Overlays Backlog (Proposed)

### 1. Mod-to-Plugin Integrations (Proposed)
* **Goal**: Allow active mods to supply custom content directly to active plugins.
* **Details**:
  * **Mod-Specific Guides**: Retranslation or story mods can bundle `walkthrough.json` to override the overlay walkthrough dynamically when activated.
  * **Gameplay Overhaul Compatibility**: Re-balance or recipe mods can bundle custom recipe lists to automatically update the Rikku's Mix Calculator plugin database.

### 2. Monster Arena Capture Live Overlay (Proposed)
* **Goal**: Eliminate manual checks at the Calm Lands arena.
* **Details**: Read live game memory to render a HUD overlay tracking captures (e.g. Calm Lands: 6/10 Coeurls) for active areas.

### 3. Rikku Active Battle Mix Suggester (Proposed)
* **Goal**: Suggest the best Mixes dynamically during active turns.
* **Details**: Read in-battle inventory and target enemy vulnerabilities to overlay optimal Rikku Mix combinations.

### 4. Al Bhed Translator and Collection Companion (Proposed)
* **Goal**: Track missing primers and translate vocabulary.
* **Details**: Read save data to list missing Primers and provide a side-panel dictionary translator tool.

### 5. Blitzball Scouting and Tech Tracker (Proposed)
* **Goal**: Assist team building and tech copy alerts.
* **Details**: Track player contract timers, tech copy availability, and tournament schedules in an active HUD.

### 6. Interactive Sphere Grid Node Planner (Proposed)
* **Goal**: Design and share character path maps.
* **Details**: Render standard and expert sphere grid planners, allowing users to calculate SLvs and export build files.

### 7. Live Memory Offset Online Database Sync (Proposed)
* **Goal**: Auto-update game memory offsets if Steam patches the game.
* **Details**: Pull latest memory offset JSON maps from a remote GitHub repository to prevent plugins from breaking during game updates.

---

## 💾 Done / Completed Track
* [x] **Centralized Settings & Customization for Plugins**: GUI-driven global settings card in Settings, supporting hotkey rebinding, opacity, snapped screen layout positioning, and toggle status (Next_Release).
* [x] **Main Manager & Plugin Inter-Process Communication (IPC)**: local socket connection to sync real-time plugin stats and route console logs to manager log window (Next_Release).
* [x] **Core Game Memory Hook API**: consolidated process handling, UAC checks, and raw read/write APIs (Next_Release).
* [x] **Open Plugin Developer SDK & Extensible Runner**: support raw scripts, executables, dotted path imports, background/utility/listener categories, template generators, and python runtime execution. (Next_Release)
