# 🎮 Spira Mod Manager

A clean, fast, and secure standalone mod manager for **Final Fantasy X / X-2 HD Remaster** (Steam). Built with a modern dark interface, it handles installation, conflict resolution, load order, saves backups, and restores automatically while saving disk space.

---

## 📥 Direct Download & Quick Start

If you are a player looking to download the latest version, click the link below to get the ready-to-use mod manager file immediately:

### [👉 Click here to download the Newest Stable Release (v3.1.0) 👈](https://github.com/odinj2010/FFX-Mod-Manager/releases/download/v3.1.0/spiramm.zip)

### 🚀 Easy Installation Steps
1. **Download** the zip archive using the link above.
2. **Extract** the files (The entire Spira Mod Manager folder, it has the `SpiraModManager.exe`, `themes/` folder and `plugins/` folder inside it) **anywhere on your computer** (you do not have to place it inside the main game directory; you can simply select your game directory on first launch).
3. **Run** `SpiraModManager.exe` to launch the manager!

---

## 🌟 Key Features

* **Fahrenheit Framework Support:** Full native compatibility with the modern Fahrenheit Modding Framework. Installs manifests, structures assets, and edits the active load order automatically.
* **Save Games & Backups Manager:** Track and manage game saves from the dedicated **Saves** tab. Back up your active save files with custom snapshot descriptions, delete obsolete slots, and restore snapshots cleanly.
* **Backward Compatibility:** Seamlessly coexists with traditional **UnX** and **ffgriever EFL** DLL loaders. The manager auto-detects the active loader and configures itself dynamically.
* **Move-on-Enable Architecture:** Saves massive amounts of disk space. Mod packages are kept in a unified, loader-agnostic repository and moved into active game directories only when enabled.
* **ZIP & RAR Auto-Unwrapping:** Drag-and-drop support for standard `.zip` and `.rar` mod archives. Automatically extracts, normalizes VBF folder paths, and wraps loose mod files.
* **Auto-Conflict Resolution & Backups:** Detects file overwrite collisions. Overwritten active files are backed up automatically into their respective owner's repository folder and restored when the overriding mod is disabled.
* **Live Theme Creator:** RETHEME the manager's UI on the fly. Create custom palettes and preview them instantly.
* **Dynamic Plugin Browser:** Checks the remote GitHub repository index to download, install, and load external python plugins dynamically.

---

## ⚙️ Fahrenheit Modding Framework Support

When the manager detects `fahrenheit/bin/fhstage0.exe` in the game folder:
1. **Status detection:** Changes the status pill to `🟢 Active Mod Loader Detected (Fahrenheit Framework)`.
2. **Launch execution:** Bypasses Steam launching and executes the game wrapper:
   ```bash
   fhstage0.exe "[absolute_path_to_game]\FFX.exe"
   ```
3. **Load Order Sorting:** Enabled mods are ordered inside the extensionless plaintext file `fahrenheit/mods/loadorder`. The manager provides **Move Up** and **Move Down** controls to physically sort mod priority on the fly.
4. **VBF Layout Mirroring:** Standard mod directories (like `ffx_ps2` or `ffx_data`) are automatically translated into Fahrenheit's virtual path structure:
   `fahrenheit/mods/{mod_id}/efl/x/FFX_Data/`
5. **PascalCase Manifests:** The manager automatically generates case-sensitive `{id}.manifest.json` files using exact properties matching Fahrenheit's C# record parser:
   ```json
   {
     "Id": "my_mod_id",
     "Name": "My Cool Mod",
     "Desc": "A short description.",
     "Authors": "Author Name",
     "Version": "1.0.0",
     "Link": "",
     "Dependencies": [],
     "LoadAfter": [],
     "Flags": "NONE"
    }
    ```

---

## 📁 Repository Structure & Workflow

The manager introduces a unified loader-agnostic layout:
* **Repository Folder:** `data/mods_disabled/` (Where all mod directories and original assets reside when inactive).
* **Enabled (Traditional loaders):** Files are moved into `data/mods/`.
* **Enabled (Fahrenheit Framework):** Files are mapped and moved into `fahrenheit/mods/{id}/efl/x/FFX_Data/`.

---

## 🛠️ Development & Building

If you are a developer looking to build or contribute to the project:

### Prerequisites
* Python 3.10+
* Tkinter (standard GUI library)

### Building Standalone Executable
To compile the Python script into a single, optimized `.exe` distribution:
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Build via the compilation script:
   ```bash
   python compile_mod_manager.py
   ```
The compiled executable will be located in the `dist/ffxmm.exe` directory.

### Custom Plugin Index
The **Plugin Browser** fetches from `plugins.json` in the remote repository. The format is structured as follows:
```json
[
  {
    "id": "my_custom_plugin",
    "name": "My Custom Plugin",
    "creator": "Author Name",
    "version": "1.0.0",
    "description": "Short summary of plugin.",
    "icon": "🔌",
    "download_url": "https://github.com/user/repo/archive/refs/tags/v1.0.0.zip"
  }
]
```

---

## 📄 License & Credits

Final Fantasy X / X-2 HD Remaster is a trademark of Square Enix.  
This tool is created as an open-source contribution for the Final Fantasy modding community.
