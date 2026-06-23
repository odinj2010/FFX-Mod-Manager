import subprocess
import shutil
import os
import sys

cwd = os.path.dirname(os.path.abspath(__file__))

def compile_tool(spec_name, space_name):
    print(f"\n=== Compiling {spec_name} ===", flush=True)
    spec_path = os.path.join(cwd, f"{spec_name}.spec")
    cmd = [sys.executable, "-m", "PyInstaller", spec_path, "--noconfirm", "--clean"]
    
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Compilation FAILED for {spec_name}:", flush=True)
        print(res.stderr, flush=True)
        return False
    else:
        print(f"Successfully compiled {spec_name}", flush=True)
        
        # Ensure we copy to the spaced name if requested
        src = os.path.join(cwd, "dist", f"{spec_name}.exe")
        if os.path.exists(src) and space_name:
            dst = os.path.join(cwd, "dist", f"{space_name}.exe")
            try:
                shutil.copy2(src, dst)
                print(f"Copied {src} -> {dst}", flush=True)
            except Exception as e:
                print(f"Error copying to {dst}: {e}", flush=True)
        return True

def compile_trackers():
    print(f"\n=== Auto-Discovering and Compiling Plugin Trackers ===", flush=True)
    plugins_dir = os.path.join(cwd, "plugins")
    if not os.path.exists(plugins_dir):
        print("No plugins directory found.", flush=True)
        return True
        
    success = True
    for d in os.listdir(plugins_dir):
        dpath = os.path.join(plugins_dir, d)
        if os.path.isdir(dpath):
            tracker_py = os.path.join(dpath, "tracker.py")
            if os.path.exists(tracker_py):
                print(f"\nCompiling tracker for plugin '{d}'...", flush=True)
                cmd = [
                    sys.executable, "-m", "PyInstaller",
                    "--noconsole",
                    "--onefile",
                    "--clean",
                    tracker_py
                ]
                res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
                if res.returncode != 0:
                    print(f"Compilation FAILED for tracker in {d}:", flush=True)
                    print(res.stderr, flush=True)
                    success = False
                else:
                    print(f"Successfully compiled tracker for {d}", flush=True)
                    src = os.path.join(cwd, "dist", "tracker.exe")
                    dst = os.path.join(cwd, "dist", "plugins", d, "tracker.exe")
                    dev_dst = os.path.join(cwd, "plugins", d, "tracker.exe")
                    if os.path.exists(src):
                        try:
                            os.makedirs(os.path.dirname(dst), exist_ok=True)
                            shutil.copy2(src, dst)
                            print(f"Copied {src} -> {dst}", flush=True)
                            
                            # Also copy to dev directory
                            shutil.copy2(src, dev_dst)
                            print(f"Copied {src} -> {dev_dst}", flush=True)
                        except Exception as e:
                            print(f"Error copying tracker executable for {d}: {e}", flush=True)
                            success = False
    return success

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compile Mod Manager, Toolbox, or Trackers individually or all together.")
    parser.add_argument("--manager", action="store_true", help="Compile Spira Mod Manager (spiramm)")
    parser.add_argument("--toolbox", action="store_true", help="Compile FFX Modding Toolbox")
    parser.add_argument("--tracker", action="store_true", help="Compile Plugin Trackers")
    parser.add_argument("--all", action="store_true", help="Compile all targets (default if no arguments are passed)")
    
    args = parser.parse_args()
    
    # If no specific flags are passed, compile all
    if not (args.manager or args.toolbox or args.tracker or args.all):
        args.all = True
        
    compiled_any = False
    all_success = True
    
    if args.manager or args.all:
        compiled_any = True
        if not compile_tool("SpiraModManager", None):
            all_success = False
            
    if args.toolbox:
        compiled_any = True
        if not compile_tool("FFX_Modding_Toolbox", "FFX Modding Toolbox"):
            all_success = False
            
    if args.tracker or args.all:
        compiled_any = True
        if not compile_trackers():
            all_success = False
            
    if compiled_any:
        if all_success:
            print("\nCompilation completed successfully for all selected targets!", flush=True)
        else:
            print("\nOne or more selected compilations FAILED.", flush=True)
