# Spira Mod Manager GitHub Release - v3.1.2

*   **Tag Version**: `v3.1.2`
*   **Release Title**: `Spira Mod Manager v3.1.2 - UnX Path Resolution & Conflict Fixes`

---

## Release Notes

This release resolves path-resolution issues when importing textures for the **Untitled Project X (UnX)** mod framework and restores functionality to the mod manager's Conflict Tab when using the newer `.spiramod` metadata format.

### ⚙️ Core System & Path Operations
*   **UnX Texture Path Auto-Resolution**: The manual import manager now auto-resolves paths containing `"unx_res/"`, `"inject/textures/"`, and `"textures/"`, as well as loose `.dds` files, routing them directly into `UnX_Res/inject/textures/` without manual prompts.

### 🐛 Bug Fixes
*   **Unified Conflict Detection Format Support**: Restored the "Conflicts" tab functionality for newly imported and created mods by updating the conflict detection tool to correctly look for the modern `.spiramod` metadata file type instead of searching only for legacy formats.

---

## Assets
* 📦 `SpiraModManager.exe` (Compiled executable)
* 💾 Source code (zip)
* 💾 Source code (tar.gz)
