# Walkthrough Plugin Changelog

All notable changes to the Walkthrough plugin will be documented in this file.

## [1.7] - 2026-06-18
- Implemented unknown Map ID fallback to clear the walkthrough layout and display a friendly paused placeholder message.
- Upgraded process exit logic to call `destroy()` and `sys.exit(0)` to guarantee clean tracker process shutdown on game exit.

## [1.6] - 2026-06-18
- Migrated location tracking from dynamic screen Room IDs to robust high-level Zone IDs (using offset `0xD307E8` and `ZONE_MAP` lookup) for 100% correct walkthrough step tracking on PC.

## [1.5] - 2026-06-18
- Updated Room ID memory pointer offset to `0xD2CA90` to track specific screen/room maps in real-time.

## [1.4] - 2026-06-18
- Fixed Room ID reading by changing the buffer from a 4-byte `c_int` to a 2-byte `c_uint16`.

## [1.3] - 2026-06-18
- Updated Room ID memory pointer offset to `0xD307E8` to match the standard Steam FFX PC Remaster memory layout.

## [1.2] - 2026-06-18
- Implemented robust DLL base address resolution fallback using `EnumProcessModules` via `psapi` for 64-bit Python compatibility.
- Added live diagnostic warning overlays on the HUD for memory read errors or unknown room IDs to ease debugging.

## [1.1] - 2026-06-18
- Refactored the main UI to use a `ttk.Notebook` tab switcher, grouping checklist controls in the **Guide** tab and overlay options in the **Settings** tab.
- Added support for settings serialization into `overlay_config.json`.
- Refactored widget repaint functions to support manager theme propagation.
- Fixed PyInstaller path resolution (`_MEIPASS` lookup) using `sys.executable` to load config files correctly.
- Added dynamic default hotkey resolution from `plugin.json` fallback if `overlay_config.json` is missing.

## [1.0] - 2026-06-14
- Initial release.
- Added live FFX save-state location tracking and interactive zone checklisting.
