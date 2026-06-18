import shutil
import os

src_base = r"c:\Users\jonat\Desktop\Modding\Final Fantasy X&X2 Modding\FFX Tools"
dst_base = r"C:\Users\jonat\Desktop\FFX-Mod-Manager"

# Files/Folders to copy (Source Path relative to src_base, Destination Path relative to dst_base)
sync_map = [
    # Main scripts & spec
    ("FFX_Mod_Manager.py", "FFX_Mod_Manager.py"),
    ("FFX_Mod_Manager.spec", "FFX_Mod_Manager.spec"),
    ("ffx_codec.py", "ffx_codec.py"),
    ("ffx_mod_manager_version.txt", "ffx_mod_manager_version.txt"),
    ("README.md", "README.md"),
    
    # Custom themes and plugins directories
    ("themes", "themes"),
    ("plugins", "plugins"),
    
    # Compiled distribution executables & folders (for packaging releases)
    ("dist/FFX Mod Manager.exe", "dist/FFX Mod Manager.exe"),
    ("dist/themes", "dist/themes"),
    ("dist/plugins", "dist/plugins"),
]

print("Starting sync to GitHub repository folder...", flush=True)

for src_rel, dst_rel in sync_map:
    src_path = os.path.join(src_base, src_rel)
    dst_path = os.path.join(dst_base, dst_rel)
    
    if not os.path.exists(src_path):
        print(f"Warning: Source path does not exist: {src_path}", flush=True)
        continue
        
    # Handle directories
    if os.path.isdir(src_path):
        # Remove destination directory if it exists to ensure a clean copy
        if os.path.exists(dst_path):
            try:
                shutil.rmtree(dst_path)
            except Exception as e:
                print(f"Error removing old directory {dst_path}: {e}", flush=True)
        try:
            shutil.copytree(src_path, dst_path)
            print(f"Synced Directory: {src_rel} -> {dst_rel}", flush=True)
        except Exception as e:
            print(f"Error copying directory {src_rel}: {e}", flush=True)
            
    # Handle files
    else:
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        try:
            shutil.copy2(src_path, dst_path)
            print(f"Synced File: {src_rel} -> {dst_rel}", flush=True)
        except Exception as e:
            print(f"Error copying file {src_rel}: {e}", flush=True)

print("\nSync completed successfully!", flush=True)
