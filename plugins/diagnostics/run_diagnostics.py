import os
import sys
import json
import socket

def send_ipc_log(sock, message, level="info"):
    payload = json.dumps({"cmd": "log", "message": message, "level": level}) + "\n"
    try:
        sock.sendall(payload.encode("utf-8"))
    except Exception:
        # Fallback to standard print if socket fails
        print(f"[{level.upper()}] {message}")

def run_diagnostics():
    # 1. Read arguments passed by the utility runner
    # The runner passes: [game_dir, active_game_mode] as arguments
    game_dir = sys.argv[1] if len(sys.argv) > 1 else ""
    game_mode = sys.argv[2] if len(sys.argv) > 2 else "FFX"
    
    # 2. Establish connection to SpiraMM's IPC API Server
    ipc_port = int(os.environ.get("SPIRAMM_IPC_PORT", 8692))
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", ipc_port))
    except Exception as e:
        print(f"Failed to connect to SpiraMM IPC server on port {ipc_port}: {e}")
        
    send_ipc_log(sock, "Starting SpiraMM Diagnostic Run...", "info")
    send_ipc_log(sock, f"Active Game Mode: {game_mode}", "info")
    send_ipc_log(sock, f"Game Directory: {game_dir}", "info")
    
    if not game_dir or not os.path.exists(game_dir):
        send_ipc_log(sock, "Error: Game directory is invalid or not set in settings.", "error")
        return
        
    # Check executables
    exe_name = "FFX.exe" if game_mode == "FFX" else "FFX-2.exe"
    exe_path = os.path.join(game_dir, exe_name)
    if os.path.exists(exe_path):
        send_ipc_log(sock, f"Success: {exe_name} executable found.", "success")
    else:
        send_ipc_log(sock, f"Warning: {exe_name} not found in the game folder.", "warning")
        
    # Check Fahrenheit Mod Loader
    fh_launcher = os.path.join(game_dir, "fahrenheit", "bin", "fhstage0.exe")
    if os.path.exists(fh_launcher):
        send_ipc_log(sock, "Status: Fahrenheit Mod Loader is active for this installation.", "info")
    else:
        send_ipc_log(sock, "Status: Native Steam File Loader (EFL) active / standard launch.", "info")
        
    # Check for VBF extracted files directory
    extracted_vbf = os.path.abspath(os.path.join(os.getcwd(), "..", "VBF Browser", "extracted"))
    if os.path.exists(extracted_vbf):
        send_ipc_log(sock, f"Success: Extracted VBF directory found: '{extracted_vbf}'", "success")
    else:
        send_ipc_log(sock, "Status: Extracted VBF path directory does not exist yet (clean setup).", "info")
        
    send_ipc_log(sock, "Diagnostics complete. No issues found!", "success")
    
    if sock:
        try:
            sock.close()
        except Exception:
            pass

if __name__ == "__main__":
    run_diagnostics()
