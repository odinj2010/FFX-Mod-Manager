# Walkthrough Plugin Changelog

All notable changes to the Walkthrough plugin will be documented in this file.

## [1.1] - 2026-06-18
- Refactored the main UI to use a `ttk.Notebook` tab switcher, grouping checklist controls in the **Guide** tab and overlay options in the **Settings** tab.
- Added support for settings serialization into `overlay_config.json`.
- Refactored widget repaint functions to support manager theme propagation.
- Fixed PyInstaller path resolution (`_MEIPASS` lookup) using `sys.executable` to load config files correctly.
- Added dynamic default hotkey resolution from `plugin.json` fallback if `overlay_config.json` is missing.

## [1.0] - 2026-06-14
- Initial release.
- Added live FFX save-state location tracking and interactive zone checklisting.
