# Scene Skipper Plugin - Changelog

This changelog tracks updates, bug fixes, and feature improvements for the Scene Skipper plugin.

## [v1.1] - 2026-06-19
*   **Custom QPC Speedhack Implementation**: Implemented a self-contained inline hooking mechanism for `QueryPerformanceCounter` inside target game processes (`FFX.exe`/`FFX-2.exe`), bypassing the speedup limitations of the native engine game booster and UnX speed multipliers during cutscenes.
*   **Continuous Time Base Transition**: Integrated dynamic continuous time-scaling bases to prevent game crashes, timing jumps, or temporal glitches when toggling the speedhack.
*   **QPC Hook Cleanup**: Added safety hook removal upon tracker exit, restoring the original 5 bytes of the target process's `QueryPerformanceCounter` function.

## [v1.0] - 2026-06-19
*   **Initial Release**: Added the Scene Skipper plugin allowing users to pause FFX/FFX-2 cutscenes and press a hotkey (default: Backspace) to fast-forward past them safely.
*   **Safe Skip via Game Boosters**: Utilizes the built-in game speed-up booster functionality dynamically to fast-forward at high speed, protecting save files and quest progression checks.
*   **Memory Cutscene Polling**: Automatically checks the FFX/FFX-2 active event state flag via process memory reading (`OpenProcess` / `ReadProcessMemory`), restoring normal 1x speed the instant the cutscene concludes.

