# Achievements Plugin Changelog

All notable changes to the Achievements plugin will be documented in this file.

## [1.4] - 2026-06-23
- Migrated configuration storage from local `overlay_config.json` to SpiraMM's central configuration manager under `plugin_settings.achievements`.
- Refactored `tracker.py` to discover the active IPC port dynamically from `--ipc-port` CLI parameter, `SPIRAMM_IPC_PORT` env var, or `spiramm_config.json` file.
- Replaced the low-level Windows process monitoring loop in `tracker.py` with reactive socket event listeners listening to `on_config_changed` and `on_theme_change` event streams.
- Replaced direct `ReadProcessMemory` calls in the `tracker.py` scanner loop with remote memory query commands `read_memory` over the local socket IPC server.
- Cleaned up unused config files and improved startup execution safety.

## [1.3] - 2026-06-19
- Upgraded process exit logic to call `destroy()` and `sys.exit(0)` to guarantee clean tracker process shutdown on game exit.

## [1.2] - 2026-06-18
- Version bump for local/unreleased fixes.

## [1.1] - 2026-06-18
- Refactored the main UI to use a `ttk.Notebook` tab switcher, grouping achievements progress cards in the **Achievements** tab and overlay settings in the **Settings** tab.
- Replaced the hardcoded F8 trigger in the RAM scanner with custom hotkey variables loaded from `overlay_config.json`.
- Implemented file modification timestamp monitoring in the tracker to support active hotkey/setting reloading in-game.
- Added dynamic position adjustments (Left-Half, Right-Half, Top-Half, Bottom-Half) and dynamic font/widget scaling based on overlay scale configs.
- Fixed PyInstaller path resolution (`_MEIPASS` lookup) using `sys.executable` to load config files correctly.
- Added dynamic default hotkey resolution from `plugin.json` fallback if `overlay_config.json` is missing.

## [1.0] - 2026-06-14
- Initial release.
- Added custom achievement conditions verification through RAM memory scanning.
