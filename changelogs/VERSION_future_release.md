# Spira Mod Manager Changelog - Future Release

This file contains staging changelogs for the upcoming releases of Spira Mod Manager.

## UI Layout and Configuration Updates

### Enhancements
*   *(Placeholder for upcoming visual, layout, or setting improvements)*

### General UI Fixes
*   *(Placeholder for interface corrections)*

## Core System & Path Operations
*   **Fahrenheit Mode Saves Manager Safeguard**: Deactivated the standard Save Game and Backup manager tab when the Fahrenheit Mod Loader is active. Added an overlay notice advising players to configure and manage their dynamically hashed load-order-aware save sets in `fahrenheit/saves/` directly in-game or via Fahrenheit configurations, preventing save game conflicts or data corruption.

## Bug Fixes
*   **Repository Build Script Tracking**: Removed `compile_mod_manager.py` from `.gitignore` so the packaging and tracker compilation automation utility is tracked in git and available to public developers.
*   **Compiler Script Working Directory Resolution**: Updated `compile_mod_manager.py` to dynamically resolve its working directory instead of using a hardcoded FFXMM path.
*   **Fahrenheit Game Launch Working Directory and Parameters**: Fixed an issue where launching the game in Fahrenheit mode was set up incorrectly. The working directory has been set to the launcher's binary folder (`fahrenheit/bin`) and the relative path of the target game executable (e.g. `..\..\FFX.exe`) is passed. This allows `fhstage0.exe` and the game to correctly locate `fhstage1.dll` and dependencies during initialization.
