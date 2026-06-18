# FFX Mod Manager v2.2.0 - The Safety & Diagnostics Update

This release focuses on application stability, robust conflict detection based on load order priorities, extraction progress indicators, and system diagnostics safeguards.

## 🚀 Key Features

### 🛡️ Smart Load Order Conflict Tab
* **Active Priority Calculation:** The "Conflicts" tab now calculates file priority dynamically. In Fahrenheit mode, the mod placed *latest* in the load order takes override priority, flagging other mod assets as `Overridden (Inactive)` and showing the prioritized file as `Overriding (Prioritized)`.
* **Conflict Grid Overhaul:** Displays conflicts categorized by file path, showing overlapping mods and active priority status cleanly.

### 📥 Import Progress Indicator Modals
* **Non-Blocking Extraction Window:** Replaced frozen GUI screens during mod archive unwrapping with a themed `Toplevel` progress dialog.
* **Real-time Extraction Tracker:** Displays a progress bar, percentage calculations, and active filename labels dynamically during the decompression loop.

### ⚙️ Safety & System Diagnostics Panel
* **Verify Disk & Permissions:** Added a diagnostics utility in the Settings panel that performs:
  * **Write Permissions Check:** Verifies write access to the game directory (notifying users if they need to run FFXMM as Administrator).
  * **Storage Capacity Mapping:** Inspects remaining storage space on the installation drive (warning if space falls below 1GB).
  * **Registry Mapping Verification:** Displays auto-detection status of the Steam installation registry paths.
* **Safe Mode Reset:** Adds a 1-click **Disable All Active Mods** button that automatically deactivated all mods, restoring original repository files to resolve corruption, process locks, or game launch crashes safely.

### 🚀 Asynchronous Update Checker
* **Background Update Checks:** Queries GitHub Releases API in a daemon thread on startup, preventing interface lag or startup delays.
* **Download Source Selector:** Clicking "Get Update" opens a centered dialog prioritizing **Nexus Mods** (to maximize download points) with a smaller hyperlink fallback redirecting to **GitHub Releases** during emergencies or quarantine windows.
* **Case-Insensitive Version Parsing:** Upgraded the comparison engine to cleanly parse tag variables case-insensitively, handling varying format structures (like `V.2.1.0` or `v2.2.0`).

## 🔧 Improvements & Fixes
* **Hover Highlights Fix:** Bound cursor enter and leave signals directly to inner card components (labels, badges, and rows) to prevent border highlight flickering on the Available Mods list.
* **Dynamic Category Pills:** Mod cards now display custom-colored pill badges mapping to mod categories (`TEXTURE`, `AUDIO`, `SCRIPT`, `UI`, `GAMEPLAY`) alongside status indicator dots (`● Active` / `○ Disabled`).
* **FFX-2 Directory Auto-Resolution:** Added support to automatically resolve, map, and import mod assets for *Final Fantasy X-2* (mapping directories like `ffx2_ps2`, `ffx2_data`, and `ffx2/master` correctly instead of forcing them into FFX path categories).
* **FFX-2 Unmanaged File Tracking:** Updated the safety verification engine to scan for loose, unmanaged overrides inside `ffx2_data` and `ffx2_ps2` folders, keeping user staging environments clean.
* **Dual-Process Game Launch Tracking:** Upgraded the background game launcher tracker to monitor and detect both `FFX.exe` and `FFX-2.exe` execution states seamlessly. FFXMM will now skip loading FFX-specific RAM trackers (Achievements and Walkthroughs) when detecting FFX-2 gameplay to prevent memory read errors.

---
*Thank you for being part of the FFX modding community! Report any issues on our GitHub page.*
