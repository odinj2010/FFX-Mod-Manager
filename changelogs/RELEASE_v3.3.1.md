# Changelog - Spira Mod Manager (Release v3.3.1)

This document contains a running log of all changes made since the official release of v3.3.0.

---

## ⚡ Key Highlights
*   **Native .7z Archive Support**: Added full support for `.7z` archives across Drag-and-Drop file import, single file import dialogs, and bulk archive import dialogs, routing extraction through 7-Zip, WinRAR, or Windows native `tar` engines.
*   **Executable Version Metadata Alignment**: Updated Windows compilation build metadata (`spiramm_version.txt`) to report `v3.3.1.0` in the executable's properties details window.

---

## 🔧 Changelog Details

### 📥 Mod & Save Importing (.7z Support)
*   Extended drag-and-drop file type filter (`handle_dropped_files`) to accept `.7z` files.
*   Added `.7z` filetype options to `import_zip_mod` and `import_bulk_zips` file selection dialogs.
*   Routed `.7z` decompression through the 7-Zip (`7z.exe`), WinRAR (`UnRAR.exe`), or Windows `tar` subprocess extraction pipeline.
*   Updated unsupported format error logs and hints to explicitly reference `.zip`, `.rar`, and `.7z`.

### ⚙️ Build System & Versioning
*   Bumped `APP_VERSION` in `spiramm.py` to `3.3.1`.
*   Synchronized `spiramm_version.txt` `filevers`, `prodvers`, `FileVersion`, and `ProductVersion` to `3.3.1`.
