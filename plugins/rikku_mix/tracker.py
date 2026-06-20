import os
import sys
import time
import json
import ctypes
import ctypes.wintypes
import tkinter as tk
from mix_data import MIX_OUTCOMES

# Windows API Constants
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

# Setup Win32 handles
kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

user32.GetForegroundWindow.restype = ctypes.wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [ctypes.wintypes.HWND, ctypes.POINTER(ctypes.wintypes.DWORD)]

class RikkuMixOverlayHUD:
    def __init__(self, pid, game_dir, config_path):
        self.pid = pid
        self.game_dir = game_dir
        self.config_path = config_path
        
        # Default Configs
        self.hud_position = "Right-Half"
        self.hud_opacity = 0.85
        self.hud_scale = 1.0
        
        # Load defaults from plugin.json
        plugin_dir = os.path.dirname(self.config_path)
        manifest_path = os.path.join(plugin_dir, "plugin.json")
        default_hk = "F6"
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    default_hk = json.load(f).get("default_hotkey", "F6")
            except Exception:
                pass
        self.hotkey_vk = self.get_vk_code(default_hk)
        self.last_config_check = 0.0
        self.config_mtime = 0.0
        
        self.is_visible = False
        self.key_was_pressed = False
        
        self.load_config()
        
        # Setup process handle
        self.hProcess = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, self.pid)
        if not self.hProcess:
            # Show user-friendly popup warning about elevation/permissions
            user32.MessageBoxW(
                0,
                "Failed to open FFX game process handle.\n\nIf Final Fantasy X is running as Administrator, you must run FFX Mod Manager as Administrator as well for overlays to work.",
                "FFX Mod Manager - Rikku's Mix Plugin Error",
                0x10 # MB_ICONERROR
            )
            sys.exit(1)
            
        # Spawn GUI on main thread
        self.run_hud_window()

    def is_game_running(self):
        exit_code = ctypes.c_ulong()
        if kernel32.GetExitCodeProcess(self.hProcess, ctypes.byref(exit_code)):
            return exit_code.value == 259 # STILL_ACTIVE
        return False

    def get_vk_code(self, hotkey_str):
        mapping = {f"F{i}": 0x6F + i for i in range(1, 13)}
        return mapping.get(hotkey_str, 0x75)  # F6 default

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                self.config_mtime = os.path.getmtime(self.config_path)
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.hud_position = cfg.get("position", "Right-Half")
                self.hud_opacity = float(cfg.get("opacity", 0.85))
                self.hud_scale = float(cfg.get("scale", 1.0))
                self.hotkey_vk = int(cfg.get("hotkey_vk", self.hotkey_vk))
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

    def run_hud_window(self):
        self.root = tk.Tk()
        self.root.title("FFX Rikku's Mix Overlay HUD")
        
        # Make transparent, borderless click-through overlay
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-disabled", True)
        self.root.attributes("-alpha", self.hud_opacity)
        self.root.configure(bg="#0b0f19")
        
        self.update_geometry()
        
        # HUD Widget styling
        self.frame = tk.Frame(self.root, bg="#0b0f19", bd=1, relief="solid", highlightthickness=0)
        self.frame.config(highlightbackground="#0d9488", highlightcolor="#0d9488")
        self.frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.lbl_header = tk.Label(self.frame, text="🧪 Rikku's Mix Cheat-Sheet", font=("Segoe UI", int(11 * self.hud_scale), "bold"), fg="#2dd4bf", bg="#0b0f19", anchor="w")
        self.lbl_header.pack(fill="x", padx=15, pady=(10, 5))
        
        self.lbl_scroll_hint = tk.Label(self.frame, text="Use PageUp / PageDown to scroll", font=("Segoe UI", int(8 * self.hud_scale)), fg="#9ca3af", bg="#0b0f19", anchor="w")
        self.lbl_scroll_hint.pack(fill="x", padx=15, pady=(0, 5))
        
        self.txt_content = tk.Text(self.frame, wrap="word", bg="#060913", fg="#e2e8f0", font=("Consolas", int(9 * self.hud_scale)), bd=0, highlightthickness=0)
        self.txt_content.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Populate reference content
        self.populate_cheat_sheet()
        
        if not self.is_visible:
            self.root.withdraw()
            
        self.check_loop()
        
        self.root.mainloop()

    def populate_cheat_sheet(self):
        display_text = ""
        for mix_name, details in sorted(MIX_OUTCOMES.items()):
            display_text += f"🌟 {mix_name.upper()}\n"
            display_text += f"   Effect: {details['description']}\n"
            display_text += "   Formulas:\n"
            for item1, item2 in details["recipes"]:
                display_text += f"    • {item1}  +  {item2}\n"
            display_text += "\n" + ("=" * 40) + "\n\n"
            
        self.txt_content.config(state="normal")
        self.txt_content.delete("1.0", tk.END)
        self.txt_content.insert(tk.END, display_text)
        self.txt_content.config(state="disabled")

    def update_geometry(self):
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        
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
            try:
                self.root.destroy()
            except Exception:
                pass
            sys.exit(0)
            
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
            
        # PageUp / PageDown scrolling
        if self.is_visible:
            if user32.GetAsyncKeyState(0x21) & 0x8000: # PageUp
                self.txt_content.config(state="normal")
                self.txt_content.yview_scroll(-1, "pages")
                self.txt_content.config(state="disabled")
                time.sleep(0.1) # Small debounce
            elif user32.GetAsyncKeyState(0x22) & 0x8000: # PageDown
                self.txt_content.config(state="normal")
                self.txt_content.yview_scroll(1, "pages")
                self.txt_content.config(state="disabled")
                time.sleep(0.1) # Small debounce
                
        self.root.after(100, self.check_loop)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        pid = int(sys.argv[1])
        game_dir = sys.argv[2]
        
        if getattr(sys, 'frozen', False):
            plugin_dir = os.path.dirname(sys.executable)
        else:
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            
        config_path = os.path.join(plugin_dir, "overlay_config.json")
        
        hud = RikkuMixOverlayHUD(pid, game_dir, config_path)
