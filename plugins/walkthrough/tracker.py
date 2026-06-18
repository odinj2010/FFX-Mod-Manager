import os
import sys
import time
import json
import ctypes
import ctypes.wintypes
import threading
import tkinter as tk

# Windows API Constants
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

# Setup Win32 handles
kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

user32.GetForegroundWindow.restype = ctypes.wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [ctypes.wintypes.HWND, ctypes.POINTER(ctypes.wintypes.DWORD)]

class WalkthroughOverlayHUD:
    def __init__(self, pid, game_dir, config_path, guide_path):
        self.pid = pid
        self.game_dir = game_dir
        self.config_path = config_path
        self.guide_path = guide_path
        
        # Load Guide
        self.guide_data = self.load_guide_data()
        
        # Default Configs
        self.hud_position = "Right-Half"
        self.hud_opacity = 0.85
        self.hud_scale = 1.0
        self.hotkey_vk = 0x78 # F9 default
        self.last_config_check = 0.0
        self.config_mtime = 0.0
        
        self.is_visible = False
        self.current_zone_id = ""
        
        self.load_config()
        
        # Setup process handle
        self.hProcess = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, self.pid)
        if not self.hProcess:
            # Show user-friendly popup warning about elevation/permissions
            user32.MessageBoxW(
                0,
                "Failed to open FFX game process handle.\n\nIf Final Fantasy X is running as Administrator (e.g. via Steam with high privileges), you must run FFX Mod Manager as Administrator as well for overlays to work.",
                "FFX Mod Manager - Walkthrough Plugin Error",
                0x10 # MB_ICONERROR
            )
            sys.exit(1)
            
        # Spawn GUI on main thread
        self.run_hud_window()

    def load_guide_data(self):
        if os.path.exists(self.guide_path):
            try:
                with open(self.guide_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                self.config_mtime = os.path.getmtime(self.config_path)
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.hud_position = cfg.get("position", "Right-Half")
                self.hud_opacity = float(cfg.get("opacity", 0.85))
                self.hud_scale = float(cfg.get("scale", 1.0))
                self.hotkey_vk = int(cfg.get("hotkey_vk", 0x78))
            except Exception:
                pass

    def check_and_reload_config(self):
        self.last_config_check = time.time()
        if os.path.exists(self.config_path):
            try:
                current_mtime = os.path.getmtime(self.config_path)
                if current_mtime != self.config_mtime:
                    self.load_config()
                    if hasattr(self, "root") and self.root:
                        self.root.wm_attributes("-alpha", self.hud_opacity)
                        self.update_geometry()
            except Exception:
                pass

    def is_game_running(self):
        exit_code = ctypes.c_ulong()
        if kernel32.GetExitCodeProcess(self.hProcess, ctypes.byref(exit_code)):
            return exit_code.value == 259 # STILL_ACTIVE
        return False

    def run_hud_window(self):
        self.root = tk.Tk()
        self.root.title("FFX Walkthrough Overlay HUD")
        
        # Make transparent, borderless click-through overlay
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-disabled", True)
        self.root.attributes("-alpha", self.hud_opacity)
        self.root.configure(bg="#0b0f19")
        
        # Calculate Dimensions based on screen size and settings
        self.update_geometry()
        
        # HUD Widget styling
        self.frame = tk.Frame(self.root, bg="#0b0f19", bd=1, relief="solid", highlightthickness=0)
        self.frame.config(highlightbackground="#1e3a8a", highlightcolor="#1e3a8a")
        self.frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.lbl_header = tk.Label(self.frame, text="📖 Walkthrough Overlay", font=("Segoe UI", int(11 * self.hud_scale), "bold"), fg="#60a5fa", bg="#0b0f19", anchor="w")
        self.lbl_header.pack(fill="x", padx=15, pady=(10, 5))
        
        self.lbl_zone = tk.Label(self.frame, text="Current Zone: Tracking...", font=("Segoe UI", int(10 * self.hud_scale), "bold"), fg="#10b981", bg="#0b0f19", anchor="w")
        self.lbl_zone.pack(fill="x", padx=15, pady=2)
        
        self.txt_content = tk.Text(self.frame, wrap="word", bg="#060913", fg="#d1d5db", font=("Consolas", int(9 * self.hud_scale)), bd=0, highlightthickness=0)
        self.txt_content.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Start periodic tasks
        self.key_was_pressed = False
        
        if not self.is_visible:
            self.root.withdraw()
            
        self.check_loop()
        self.track_zone_loop()
        
        self.root.mainloop()

    def update_geometry(self):
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        
        # Overlay Layout coordinates positioning
        if self.hud_position == "Left-Half":
            w = int(screen_w * 0.35)
            h = screen_h
            x = 0
            y = 0
        elif self.hud_position == "Right-Half":
            w = int(screen_w * 0.35)
            h = screen_h
            x = screen_w - w
            y = 0
        elif self.hud_position == "Top-Half":
            w = screen_w
            h = int(screen_h * 0.3)
            x = 0
            y = 0
        else: # Bottom-Half
            w = screen_w
            h = int(screen_h * 0.3)
            x = 0
            y = screen_h - h
            
        def apply():
            if hasattr(self, "root") and self.root:
                self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.after(0, apply)

    def check_loop(self):
        if not self.is_game_running():
            self.root.quit()
            return
            
        # Check config updates periodically
        if time.time() - self.last_config_check > 2.0:
            self.check_and_reload_config()
            
        # Check hotkey press
        hotkey_state = user32.GetAsyncKeyState(self.hotkey_vk) & 0x8000
        if hotkey_state:
            if not self.key_was_pressed:
                self.key_was_pressed = True
                self.is_visible = not self.is_visible
                if self.is_visible:
                    self.root.deiconify()
                else:
                    self.root.withdraw()
        else:
            self.key_was_pressed = False
            
        self.root.after(100, self.check_loop)

    def track_zone_loop(self):
        if not self.is_game_running():
            return
            
        base_address = 0xD3A124
        buffer = ctypes.c_int()
        bytesRead = ctypes.c_size_t()
        
        ret = kernel32.ReadProcessMemory(self.hProcess, ctypes.c_void_p(base_address), ctypes.byref(buffer), ctypes.sizeof(buffer), ctypes.byref(bytesRead))
        if ret:
            self.update_hud_for_room(buffer.value)
            
        self.root.after(3000, self.track_zone_loop)

    def update_hud_for_room(self, room_id):
        # Match room_id against guide_data.json
        matched_zone = None
        for zone in self.guide_data:
            if room_id in zone.get("room_ids", []):
                matched_zone = zone
                break
                
        if not matched_zone or matched_zone["id"] == self.current_zone_id:
            return
            
        self.current_zone_id = matched_zone["id"]
        
        # Build guide display text
        display_text = ""
        display_text += "--- 100% CHECKLIST ---\n"
        for item in matched_zone.get("checklist", []):
            display_text += f"[ ] {item}\n"
        display_text += "\n--- STEPS ---\n"
        for step in matched_zone.get("steps", []):
            display_text += f"{step}\n\n"
            
        if hasattr(self, "txt_content") and self.txt_content:
            self.lbl_zone.config(text=f"Current Zone: {matched_zone['name']}")
            self.txt_content.config(state="normal")
            self.txt_content.delete("1.0", tk.END)
            self.txt_content.insert(tk.END, display_text)
            self.txt_content.config(state="disabled")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        pid = int(sys.argv[1])
        game_dir = sys.argv[2]
        
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(plugin_dir, "overlay_config.json")
        guide_path = os.path.join(plugin_dir, "guide_data.json")
        
        hud = WalkthroughOverlayHUD(pid, game_dir, config_path, guide_path)
