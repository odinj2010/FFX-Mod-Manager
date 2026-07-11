# Spira Mod Manager Changelog - v3.1.2

## Core System & Path Operations
*   **UnX Texture Path Auto-Resolution**: Enhanced the relative path resolution during manual files/folders import wizard. The manager now automatically maps path contexts containing `"unx_res/"`, `"inject/textures/"`, and `"textures/"`, as well as loose `.dds` texture files, into their corresponding subfolder targets under `UnX_Res/inject/textures/` without prompting the user.

## Bug Fixes
*   **Unified Conflict Detection Format Support**: Corrected the mod conflict checking algorithm (`check_for_conflicts`) to support the unified `.spiramod` metadata format instead of searching exclusively for legacy `.ffxmod` and `.json` files. This restores full functionality to the "Conflicts" tab.
