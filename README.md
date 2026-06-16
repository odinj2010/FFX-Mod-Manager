# FFX Mod Manager

A clean, fast, and secure standalone mod manager for Final Fantasy X/X-2 HD Remaster (Steam).

## Features
- **Move-on-Enable:** Moves files between repository and active game folder to save disk space.
- **Recursive Folder Imports:** Automatically maps and resolves nested texture/asset paths.
- **Auto-Backup:** Restores unmanaged files into managed packages.
- **Credits Lock:** Prevents modifications of mod author credits.

## How to Build
To compile the script into a standalone `.exe`, run:
`pip install -r requirements.txt`
`python -m PyInstaller FFX_Mod_Manager.spec --noconfirm`