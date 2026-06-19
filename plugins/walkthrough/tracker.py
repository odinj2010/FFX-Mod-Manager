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
try:
    psapi = ctypes.windll.psapi
except Exception:
    psapi = None

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
        
        # Load defaults from plugin.json
        plugin_dir = os.path.dirname(self.config_path)
        manifest_path = os.path.join(plugin_dir, "plugin.json")
        default_hk = "F9"
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    default_hk = json.load(f).get("default_hotkey", "F9")
            except Exception:
                pass
        self.hotkey_vk = self.get_vk_code(default_hk)
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
            
        # Resolve base address of FFX.exe
        self.base_address = self.get_module_base(self.pid, "FFX.exe")
        if not self.base_address:
            # Fallback check for FFX-2 just in case
            self.base_address = self.get_module_base(self.pid, "FFX-2.exe")
            
        # Spawn GUI on main thread
        self.run_hud_window()

    def get_module_base(self, pid, module_name):
        # Method 1: EnumProcessModules (extremely robust, especially on 64-bit Python calling 32-bit processes)
        if psapi:
            try:
                hProcess = kernel32.OpenProcess(0x0400 | 0x0010, False, pid)  # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
                if hProcess:
                    try:
                        hModules = (ctypes.wintypes.HMODULE * 1024)()
                        cbNeeded = ctypes.wintypes.DWORD()
                        if psapi.EnumProcessModules(hProcess, ctypes.byref(hModules), ctypes.sizeof(hModules), ctypes.byref(cbNeeded)):
                            count = cbNeeded.value // ctypes.sizeof(ctypes.wintypes.HMODULE)
                            for i in range(count):
                                hMod = hModules[i]
                                buf = ctypes.create_unicode_buffer(260)
                                if psapi.GetModuleBaseNameW(hProcess, hMod, buf, ctypes.sizeof(buf) // 2):
                                    if buf.value.lower() == module_name.lower():
                                        return hMod
                    finally:
                        kernel32.CloseHandle(hProcess)
            except Exception:
                pass

        # Method 2: Fallback to CreateToolhelp32Snapshot
        TH32CS_SNAPMODULE = 0x00000008
        TH32CS_SNAPMODULE32 = 0x00000010
        
        class MODULEENTRY32(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.c_ulong),
                ("th32ModuleID", ctypes.c_ulong),
                ("th32ProcessID", ctypes.c_ulong),
                ("GlblcntUsage", ctypes.c_ulong),
                ("ProccntUsage", ctypes.c_ulong),
                ("modBaseAddr", ctypes.c_void_p),
                ("modBaseSize", ctypes.c_ulong),
                ("hModule", ctypes.c_void_p),
                ("szModule", ctypes.c_char * 256),
                ("szExePath", ctypes.c_char * 260)
            ]
            
        hSnapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
        if hSnapshot == -1:
            return None
            
        me32 = MODULEENTRY32()
        me32.dwSize = ctypes.sizeof(MODULEENTRY32)
        
        if not kernel32.Module32First(hSnapshot, ctypes.byref(me32)):
            kernel32.CloseHandle(hSnapshot)
            return None
            
        base_address = None
        while True:
            try:
                name = me32.szModule.decode('utf-8', errors='ignore')
            except Exception:
                name = ""
            if name.lower() == module_name.lower():
                base_address = me32.modBaseAddr
                break
            if not kernel32.Module32Next(hSnapshot, ctypes.byref(me32)):
                break
                
        kernel32.CloseHandle(hSnapshot)
        return base_address

    def load_guide_data(self):
        if os.path.exists(self.guide_path):
            try:
                with open(self.guide_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def get_vk_code(self, hotkey_str):
        mapping = {f"F{i}": 0x6F + i for i in range(1, 13)}
        return mapping.get(hotkey_str, 0x78)  # F9 default

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
            
        self.root.after(100, self.check_loop)

    def track_zone_loop(self):
        if not self.is_game_running():
            return
            
        offset = 0xD307E8
        base = self.base_address if getattr(self, "base_address", None) else 0
        target_addr = base + offset
        
        buffer = ctypes.c_uint16()
        bytesRead = ctypes.c_size_t()
        
        ret = kernel32.ReadProcessMemory(self.hProcess, ctypes.c_void_p(target_addr), ctypes.byref(buffer), ctypes.sizeof(buffer), ctypes.byref(bytesRead))
        if ret:
            self.update_hud_for_room(buffer.value)
        else:
            # Display diagnostic warning if reading process memory fails
            status_text = f"Current Zone: Tracking... (Read Error, Base: {hex(base) if base else 'None'})"
            if hasattr(self, "lbl_zone") and self.lbl_zone:
                self.lbl_zone.config(text=status_text, fg="#ef4444")
            
        self.root.after(3000, self.track_zone_loop)

    def update_hud_for_room(self, zone_id):
        # Map Zone ID to guide chapter ID
        zone_map = {
            0: "zanarkand",
            1: "submerged_ruins",  # Baaj Temple
            2: "submerged_ruins",  # Submerged Ruins
            3: "submerged_ruins",  # Salvage Ship
            4: "besaid",
            5: "besaid",
            6: "ss_liki",
            7: "kilika",
            8: "ss_liki",  # S.S. Winno
            9: "luca",
            10: "luca",
            11: "luca",
            12: "luca",
            13: "mi_ihen",
            14: "mi_ihen",
            15: "mi_ihen",
            16: "mi_ihen",
            17: "mushroom_rock",
            18: "mushroom_rock",
            19: "mushroom_rock",
            20: "djose",
            21: "djose",
            22: "moonflow",
            23: "moonflow",
            24: "thunder_plains",
            25: "macalania",  # Macalania Woods
            26: "macalania",  # Lake Macalania
            27: "macalania",  # Macalania Temple
            28: "bikanel",
            29: "al_bhed_home",
            30: "bevelle",
            31: "bevelle",
            32: "calm_lands",
            33: "remie_temple",
            34: "cavern_stolen_fayth",
            35: "mt_gagazet",
            36: "mt_gagazet",
            37: "zanarkand_dome",
        }
        
        target_zone_id = zone_map.get(zone_id)
        if not target_zone_id:
            # Display diagnostic warning for unknown zone IDs
            status_text = f"Current Zone: Unknown Zone (ID: {zone_id})"
            if hasattr(self, "lbl_zone") and self.lbl_zone:
                self.lbl_zone.config(text=status_text, fg="#f59e0b")
            
            # Clear text area and show paused placeholder
            if hasattr(self, "txt_content") and self.txt_content:
                self.txt_content.config(state="normal")
                self.txt_content.delete("1.0", tk.END)
                self.txt_content.insert(tk.END, "Walkthrough paused: Unknown map ID.\n\nMap-specific guides will resume once you load into a known game area.")
                self.txt_content.config(state="disabled")
            
            self.current_zone_id = ""
            return
            
        if target_zone_id == self.current_zone_id:
            return
            
        # Find zone guide dict
        matched_zone = None
        for zone in self.guide_data:
            if zone["id"] == target_zone_id:
                matched_zone = zone
                break
                
        if not matched_zone:
            return
            
        self.current_zone_id = target_zone_id
        
        # Build guide display text
        display_text = ""
        display_text += "--- 100% CHECKLIST ---\n"
        for item in matched_zone.get("checklist", []):
            display_text += f"[ ] {item}\n"
        display_text += "\n--- STEPS ---\n"
        for step in matched_zone.get("steps", []):
            display_text += f"{step}\n\n"
            
        if hasattr(self, "txt_content") and self.txt_content:
            self.lbl_zone.config(text=f"Current Zone: {matched_zone['name']}", fg="#10b981")
            self.txt_content.config(state="normal")
            self.txt_content.delete("1.0", tk.END)
            self.txt_content.insert(tk.END, display_text)
            self.txt_content.config(state="disabled")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        pid = int(sys.argv[1])
        game_dir = sys.argv[2]
        
        if getattr(sys, 'frozen', False):
            plugin_dir = os.path.dirname(sys.executable)
        else:
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            
        config_path = os.path.join(plugin_dir, "overlay_config.json")
        guide_path = os.path.join(plugin_dir, "guide_data.json")
        
        hud = WalkthroughOverlayHUD(pid, game_dir, config_path, guide_path)
