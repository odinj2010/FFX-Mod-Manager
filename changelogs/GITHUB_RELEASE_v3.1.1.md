# Spira Mod Manager GitHub Release - v3.1.1

*   **Tag Version**: `v3.1.1`
*   **Release Title**: `Spira Mod Manager v3.1.1 - Fahrenheit Safeguards & Hotfixes`

---

## Release Notes

This minor hotfix release focuses on stabilizing the integration with the **Fahrenheit Mod Loader Framework**, introducing safe state handling for game saves, and correcting build compilation tools.

### ⚙️ Core System & Path Operations
* **Fahrenheit Mode Saves Manager Safeguard**: Deactivated the standard Save Game and Backup manager tab when the Fahrenheit Mod Loader is active. Added an overlay notice advising players to configure and manage their dynamically hashed load-order-aware save sets in `fahrenheit/saves/` directly in-game or via Fahrenheit configurations, preventing save game conflicts or data corruption.

### 🐛 Bug Fixes
* **Fahrenheit Game Launch Working Directory**: Fixed an issue where launching the game in Fahrenheit mode was set up incorrectly. The working directory has been set to the launcher's binary folder (`fahrenheit/bin`) and the relative path of the target game executable (e.g. `..\..\FFX.exe`) is passed. This allows `fhstage0.exe` and the game to correctly locate `fhstage1.dll` and dependencies during initialization.
* **Repository Build Script Tracking**: Removed `compile_mod_manager.py` from `.gitignore` so the packaging and tracker compilation automation utility is tracked in git and available to public developers.
* **Compiler Script Working Directory Resolution**: Updated `compile_mod_manager.py` to dynamically resolve its working directory instead of using a hardcoded FFXMM path.

---

## Assets
* 📦 `SpiraModManager.exe` (Compiled executable)
* 💾 Source code (zip)
* 💾 Source code (tar.gz)
