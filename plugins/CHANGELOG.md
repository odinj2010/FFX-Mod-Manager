# Spira Mod Manager - Plugins Changelog

This changelog tracks updates, bug fixes, and feature improvements for the official Spira Mod Manager plugins (Achievements & Walkthrough overlays).

## [v1.5] - 2026-06-25

### Developer Toolkit (New Plugin)
* **Initial Release (v1.0)**: Introduced the Developer Toolkit tab plugin.
  * **Unified Layout**: Double-column panel organizing "Community Utilities" (VBF Browser, FFXED, MemorySumChecker, Farplane) and "My Custom Tools" side-by-side.
  - **Dynamic Path Auto-Detection**: Checks local configurations, downloaded self-contained binaries, and sibling development directories to resolve tool paths dynamically.
  - **Self-Contained ZIP Releases**: Downloads compiled executable `.zip` packages from GitHub Releases and extracts them into `plugins/toolkit/bin/[tool]/` without requiring Python requirements.
  - **Recursive Executable Finder**: Recursively scans extracted directories to locate target `.exe` launchers.
  - **FFX Phyre Tool Release Correction**: Updated Phyre Tool's download URL pattern to use correct underscore naming (`FFX_Phyre_Tool.zip`).
  - **Dynamic Tool Updater Engine**: Compares locally installed versions with the latest tags returned from the GitHub Releases API. If a newer release is published on GitHub, the manager warns the user and displays an **Update** button next to the launch option.
  - **Theme-Aware Status Colors**: Styled "Ready" with theme's success color and missing states with error color.
  - **Full Mousewheel Support**: Enabled scrolling list panes with the mouse wheel on hover.

## [v1.4] - 2026-06-20

### Rikku's Mix (New Plugin)
* **Initial Release (v1.0)**: Introduced the Rikku's Mix Calculator & Recipe Directory plugin.
  * **Interactive Calculator**: Pick any two mixable ingredients from drop-downs to immediately preview the resulting mix name and in-battle effects.
  * **Recipe Directory**: Searchable list of all 64 unique Mix outcomes. Select an outcome to view its description and see all ingredient combinations.
  * **Full Retheming**: Built-in support for theme switching, matching active light/dark UI palettes dynamically.
  * **Cohesive Tooltips**: Tooltips attached to dropdowns, entry bars, lists, and buttons.

## [v1.3] - 2026-06-19

### Scene Skipper (v1.1)
* **Custom QPC Speedhack**: Implemented a self-contained inline hooking mechanism for `QueryPerformanceCounter` inside target game processes, bypassing the speedup limitations of the native engine game booster and UnX speed multipliers during cutscenes.
* **Continuous Time Base Transition**: Integrated dynamic continuous time-scaling bases to prevent game crashes, timing jumps, or temporal glitches when toggling the speedhack.
* **QPC Hook Cleanup**: Added safety hook removal upon tracker exit, restoring the original 5 bytes of the target process's `QueryPerformanceCounter` function.

## [v1.2] - 2026-06-19

### Scene Skipper (New Plugin)
* **Initial Release (v1.0)**: Introduced the Scene Skipper plugin. Players can now pause FFX/FFX-2 cutscenes and press a hotkey (default: Backspace) to fast-forward past them safely using native speedup controls, returning to 1x speed instantly when normal gameplay resumes.


### Achievements Overlay
* **Clean Tracker Exit Safeguards**: Reconfigured tracker check loop to trigger `root.destroy()` and `sys.exit(0)` when the game closes to guarantee tracker processes terminate cleanly and avoid leaving zombie background tasks.

### General Plugin System Fixes
* **Persistent Background Monitoring:** Integrated a continuous, resource-efficient background process monitor thread in FFXMM that polls for game process status every 2 seconds, resolving re-initialization failures when closing and restarting the game without restarting the manager.

## [v1.1] - 2026-06-18

### Walkthrough Overlay
* **Overlay Thread Safety:** Restructured the Walkthrough overlay background tracking script (`tracker.py`) to run Tkinter safely on the main GUI thread, preventing thread lockups and ensuring the overlay automatically exits when the game process closes.
* **Process Exit Detection:** Added automatic checking to shutdown the walkthrough overlay cleanly when `FFX.exe` is closed.
* **Tkinter Click-Through Native Attributes:** Replaced unstable `GetWindowLongW`/`SetWindowLongW` API calls (which caused handle corruption or silent load failures on 64-bit platforms) with standard Tkinter `-disabled` window configuration to achieve stable click-through transparency.

### Achievements Overlay
* **Robust Overlay Hotkey Detection:** Upgraded the keyboard listener state engine to target active windows using process ID checking (`GetWindowThreadProcessId`) rather than brittle window title checks. This prevents keyboard inputs from being ignored if the game window is running under helper processes.
* **64-bit Handle Truncation Fix:** Explicitly declared `GetForegroundWindow.restype = wintypes.HWND` and `GetWindowThreadProcessId.argtypes` signatures to prevent 64-bit handle truncation errors that were blocking foreground hotkey checks.

### General Plugin System Fixes
* **Dynamic Overlay Hotkey Mapping:** Resolved a logging bug where both the Achievements and Walkthrough overlays reported F8 in the logs. FFXMM now queries the correct default hotkey (`F9` for Walkthrough, `F8` for Achievements) dynamically from plugin manifests.
* **UAC Elevation Diagnostics:** Implemented Windows dialog warnings for overlay background processes. If FFX is running elevated (as Administrator) but FFXMM is not, the tracker scripts now pop up a clear alert instructing the user to launch FFXMM as Administrator.
