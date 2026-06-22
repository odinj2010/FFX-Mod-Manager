# Spira Mod Manager Changelog - Future Release

This file contains staging changelogs for the upcoming releases of Spira Mod Manager.

## UI Layout and Configuration Updates

### Enhancements
*   *(Placeholder for upcoming visual, layout, or setting improvements)*

### General UI Fixes
*   *(Placeholder for interface corrections)*

## Core System & Path Operations
*   *(Placeholder for updates to loader support, VBF configurations, or staging routing mechanics)*

## Bug Fixes
*   **Fahrenheit Game Launch Working Directory and Parameters**: Fixed an issue where launching the game in Fahrenheit mode was set up incorrectly. The working directory has been set to the launcher's binary folder (`fahrenheit/bin`) and the relative path of the target game executable (e.g. `..\..\FFX.exe`) is passed. This allows `fhstage0.exe` and the game to correctly locate `fhstage1.dll` and dependencies during initialization.
