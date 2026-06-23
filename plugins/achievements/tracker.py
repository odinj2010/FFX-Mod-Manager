import os
import sys
import time
import json
import ctypes
import ctypes.wintypes
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import socket
import base64
import queue

# Windows API Constants
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_ulong),
        ("PartitionId", ctypes.c_ushort),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong)
    ]

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long)
    ]

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

try:
    from gui import ACHIEVEMENTS
except Exception:
    ACHIEVEMENTS = [
        {
            "id": "lightning_master",
            "name": "⚡ Lightning Master",
            "description": "Dodge 500 consecutive lightning bolts in the Thunder Plains without leaving or saving.",
            "category": "Minigames"
        },
        {
            "id": "no_summons_yunalesca",
            "name": "💀 Death Defied",
            "description": "Defeat Yunalesca without summoning a single Aeon.",
            "category": "Combat"
        },
        {
            "id": "nsg_sin",
            "name": "🚫 Zero Upgrades",
            "description": "Defeat Sin's Core without ever activating any nodes on the Sphere Grid.",
            "category": "Combat"
        },
        {
            "id": "lucky_sevens",
            "name": "🎰 Lucky Sevens",
            "description": "Deal exactly 7,777 damage in a single attack with any character.",
            "category": "Combat"
        },
        {
            "id": "overkill_penance",
            "name": "⚔️ Penance Annihilated",
            "description": "Defeat Penance with an Overkill.",
            "category": "Combat"
        },
        {
            "id": "blitzball_dynasty",
            "name": "⚽ Blitzball Dynasty",
            "description": "Win 5 consecutive Blitzball matches without conceding a single goal.",
            "category": "Minigames"
        },
        {
            "id": "al_bhed_scholar",
            "name": "📜 Al Bhed Scholar",
            "description": "Collect all Al Bhed Primers 1 to 26 in a single playthrough.",
            "category": "Collection"
        },
        {
            "id": "gil_millionaire",
            "name": "🪙 Spiran Millionaire",
            "description": "Amass 1,000,000 Gil at once.",
            "category": "Collection"
        },
        {
            "id": "potion_collector",
            "name": "🧪 Potion Collector",
            "description": "Have 5 or more Potions in your inventory.",
            "category": "Collection"
        }
    ]

def get_save_dir():
    home = os.path.expanduser("~")
    possible_paths = [
        os.path.join(home, "Documents", "SQUARE ENIX", "FINAL FANTASY X&X-2 HD Remaster", "FINAL FANTASY X"),
        os.path.join(home, "Documents", "SQUARE ENIX", "FINAL FANTASY X&X2 HD Remaster", "FINAL FANTASY X")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def get_latest_save_file(save_dir):
    if not save_dir:
        return None
    try:
        files = [os.path.join(save_dir, f) for f in os.listdir(save_dir) if f.startswith("ffx_") and not f.endswith(".tmp")]
        if not files:
            return None
        return max(files, key=os.path.getmtime)
    except Exception:
        return None

def read_save_signature(file_path):
    if not file_path or not os.path.exists(file_path):
        return None, None
    try:
        with open(file_path, "rb") as f:
            f.seek(0x59a4)
            sig = f.read(16)
            f.seek(0x40)
            full_data = f.read(0x3000)
            return sig, full_data
    except Exception:
        return None, None

def scan_process_memory(hProcess, signature):
    mbi = MEMORY_BASIC_INFORMATION()
    address = 0
    max_address = 0x7FFFFFFFFFFF if sys.maxsize > 2**32 else 0x7FFFFFFF
    while address < max_address:
        if not kernel32.VirtualQueryEx(hProcess, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        is_readable = (mbi.State == MEM_COMMIT and 
                       not (mbi.Protect & PAGE_NOACCESS) and 
                       not (mbi.Protect & PAGE_GUARD))
        if is_readable and mbi.RegionSize > 0:
            buffer = ctypes.create_string_buffer(mbi.RegionSize)
            bytes_read = ctypes.c_size_t()
            if kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(address), buffer, mbi.RegionSize, ctypes.byref(bytes_read)):
                data = buffer.raw[:bytes_read.value]
                idx = data.find(signature)
                if idx != -1:
                    save_block_address = address + idx
                    return save_block_address
        address += mbi.RegionSize
    return None

def show_toast(title, message):
    ps_code = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $xml = [Windows.Data.Xml.Dom.XmlDocument]::new()
    $xml.LoadXml($template.GetXml())
    $toastXml = [xml]$template.GetXml()
    $toastXml.toast.visual.binding.text[0].InnerText = "{title}"
    $toastXml.toast.visual.binding.text[1].InnerText = "{message}"
    $xml.LoadXml($toastXml.OuterXml)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Spira Mod Manager").Show($toast)
    """
    try:
        subprocess.Popen(
            ["powershell", "-Command", ps_code],
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
    except Exception:
        pass

def load_achievements_status(json_path):
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_achievements_status(json_path, data):
    try:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def find_game_hwnd(pid):
    hwnd_found = [None]
    def enum_callback(hwnd, extra):
        window_pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
        if window_pid.value == pid:
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value.upper()
                    if "FINAL FANTASY" in title or "FFX" in title:
                        hwnd_found[0] = hwnd
                        return False
                    if hwnd_found[0] is None:
                        hwnd_found[0] = hwnd
        return True
    
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    user32.EnumWindows(EnumWindowsProc(enum_callback), 0)
    return hwnd_found[0]

def get_game_client_rect_screen(hwnd):
    rect = RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        return None
    pt = POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    return pt.x, pt.y, w, h

def discover_ipc_port(plugin_dir):
    for i in range(len(sys.argv) - 1):
        if sys.argv[i] == "--ipc-port":
            try:
                return int(sys.argv[i+1])
            except ValueError:
                pass
    env_port = os.environ.get("SPIRAMM_IPC_PORT")
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            pass
    curr = os.path.abspath(plugin_dir)
    for _ in range(5):
        config_path = os.path.join(curr, "spiramm_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if "ipc_port" in cfg:
                        return int(cfg["ipc_port"])
            except Exception:
                pass
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return 8692

class IPCClient:
    def __init__(self, port, event_handler_cb=None):
        self.port = port
        self.event_handler_cb = event_handler_cb
        self.sock = None
        self.running = False
        self.pending_responses = {}
        self.msg_counter = 0
        self.lock = threading.Lock()
        
    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(("127.0.0.1", self.port))
            self.running = True
            self.listener_thread = threading.Thread(target=self._recv_loop, daemon=True)
            self.listener_thread.start()
            return True
        except Exception as e:
            print(f"IPC Client failed to connect to port {self.port}: {e}", flush=True)
            return False

    def close(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

    def _recv_loop(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                buffer += data.decode('utf-8', errors='ignore')
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        if "event" in msg:
                            if self.event_handler_cb:
                                self.event_handler_cb(msg)
                        else:
                            with self.lock:
                                for q in self.pending_responses.values():
                                    q.put(msg)
                    except Exception as e:
                        print(f"Error parsing message in IPC client loop: {e}", flush=True)
            except Exception:
                break
        self.running = False

    def send_cmd(self, cmd_dict, timeout=2.0):
        if not self.running or not self.sock:
            return None
        with self.lock:
            self.msg_counter += 1
            msg_id = self.msg_counter
            q = queue.Queue(maxsize=1)
            self.pending_responses[msg_id] = q
        try:
            raw_msg = (json.dumps(cmd_dict) + "\n").encode('utf-8')
            self.sock.sendall(raw_msg)
            resp = q.get(timeout=timeout)
            return resp
        except queue.Empty:
            print(f"IPC command timed out: {cmd_dict}", flush=True)
            return None
        except Exception as e:
            print(f"IPC command failed: {e}", flush=True)
            return None
        finally:
            with self.lock:
                self.pending_responses.pop(msg_id, None)

    def read_remote_memory(self, address, type_str="int", size=4):
        resp = self.send_cmd({"cmd": "read_memory", "address": address, "type": type_str, "size": size})
        if resp and resp.get("success"):
            val = resp.get("value")
            if type_str == "bytes" and isinstance(val, str):
                return base64.b64decode(val.encode('utf-8'))
            return val
        return None

class AchievementsOverlayApp:
    def __init__(self, pid, game_dir, json_path):
        self.pid = pid
        self.game_dir = game_dir
        self.json_path = json_path
        self.game_active = True
        
        if getattr(sys, 'frozen', False):
            self.plugin_dir = os.path.dirname(sys.executable)
        else:
            self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
            
        # Discover IPC Port & connect
        self.ipc_port = discover_ipc_port(self.plugin_dir)
        self.ipc_client = IPCClient(self.ipc_port, self.on_ipc_event)
        
        # Default configuration
        self.hud_position = "Right-Half"
        self.hud_opacity = 0.85
        self.hud_scale = 1.0
        self.hotkey_vk = self.get_vk_code("F8")
        
        self.load_config()
        
        # Connect to manager IPC server
        if not self.ipc_client.connect():
            print("Failed to connect to SpiraMM local IPC Server. Exiting.", flush=True)
            sys.exit(1)
            
        # Startup Signature scan - open process handle temporarily
        hProcess = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
        if not hProcess:
            print("Failed to open process handle for startup signature scan.", flush=True)
            sys.exit(1)
            
        save_dir = get_save_dir()
        latest_file = get_latest_save_file(save_dir)
        signature, original_data = read_save_signature(latest_file)
        if not signature:
            signature = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            
        self.save_block_address = None
        print("Scanning RAM for active save data block...", flush=True)
        for attempt in range(20):
            self.save_block_address = scan_process_memory(hProcess, signature)
            if self.save_block_address:
                break
            time.sleep(2)
            
        kernel32.CloseHandle(hProcess)
        
        if not self.save_block_address:
            print("Failed to locate save data block in RAM. Background thread exiting.", flush=True)
            sys.exit(1)
            
        print(f"Save data block located in RAM at: {hex(self.save_block_address)}", flush=True)
        
        self.overlay_window = None
        self.overlay_visible = False
        self.f8_was_pressed = False
        self.needs_refresh = False
        self.achievements_data = {}
        
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.root.after(100, self.check_hotkey_and_game)
        
        self.scanner_thread = threading.Thread(target=self.ram_scanner_loop, daemon=True)
        self.scanner_thread.start()
        
    def get_vk_code(self, hotkey_str):
        mapping = {f"F{i}": 0x6F + i for i in range(1, 13)}
        return mapping.get(hotkey_str, 0x77)

    def load_config(self):
        curr = os.path.abspath(self.plugin_dir)
        config_path = None
        for _ in range(5):
            p = os.path.join(curr, "spiramm_config.json")
            if os.path.exists(p):
                config_path = p
                break
            parent = os.path.dirname(curr)
            if parent == curr:
                break
            curr = parent
            
        if config_path:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                p_cfg = cfg.get("plugin_settings", {}).get("achievements", {})
                self.hud_position = p_cfg.get("position", "Right-Half")
                self.hud_opacity = float(p_cfg.get("opacity", 0.85))
                self.hud_scale = float(p_cfg.get("scale", 1.0))
                self.hotkey_vk = self.get_vk_code(p_cfg.get("hotkey", "F8"))
            except Exception as e:
                print(f"Error loading central config in tracker: {e}", flush=True)

    def on_ipc_event(self, msg):
        event = msg.get("event")
        args = msg.get("args", [])
        if event == "on_config_changed":
            path = args[0] if len(args) > 0 else ""
            val = args[1] if len(args) > 1 else None
            if path.startswith("plugin_settings.achievements."):
                key = path.replace("plugin_settings.achievements.", "")
                if key == "position":
                    self.hud_position = val
                    self.root.after(0, lambda: self.sync_position(None))
                elif key == "hotkey":
                    self.hotkey_vk = self.get_vk_code(val)
                elif key == "opacity":
                    try:
                        self.hud_opacity = float(val)
                        if self.overlay_window:
                            self.root.after(0, lambda: self.overlay_window.wm_attributes("-alpha", self.hud_opacity))
                    except ValueError:
                        pass
                elif key == "scale":
                    try:
                        self.hud_scale = float(val)
                        self.root.after(0, lambda: self.reload_and_draw_achievements())
                        self.root.after(0, lambda: self.sync_position(None))
                    except ValueError:
                        pass
        elif event in ["on_theme_change", "on_theme_changed"]:
            self.root.after(0, lambda: self.reload_and_draw_achievements())
        elif event == "on_game_close":
            self.game_active = False

    def is_game_running(self):
        return self.game_active and self.ipc_client.running

    def check_hotkey_and_game(self):
        if not self.is_game_running():
            print("Game exited or IPC disconnected. Closing tracker overlay.", flush=True)
            try:
                self.root.destroy()
            except Exception:
                pass
            sys.exit(0)
            
        game_hwnd = find_game_hwnd(self.pid)
        foreground_hwnd = user32.GetForegroundWindow()
        is_game_focused = (game_hwnd is not None) and (foreground_hwnd == game_hwnd)
        
        f8_state = user32.GetAsyncKeyState(self.hotkey_vk) & 0x8000
        if f8_state:
            if not self.f8_was_pressed:
                self.f8_was_pressed = True
                if self.overlay_visible or is_game_focused:
                    self.toggle_overlay(game_hwnd)
        else:
            self.f8_was_pressed = False
            
        if self.needs_refresh:
            self.needs_refresh = False
            self.reload_and_draw_achievements()
            
        self.root.after(100, self.check_hotkey_and_game)

    def toggle_overlay(self, game_hwnd):
        if self.overlay_visible:
            self.overlay_visible = False
            if self.overlay_window:
                self.overlay_window.withdraw()
        else:
            self.overlay_visible = True
            if not self.overlay_window:
                self.create_overlay_window()
            self.sync_position(game_hwnd)
            self.reload_and_draw_achievements()
            self.overlay_window.deiconify()
            self.overlay_window.lift()
            self.sync_position_loop()

    def create_overlay_window(self):
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.overrideredirect(True)
        self.overlay_window.wm_attributes("-topmost", True)
        self.overlay_window.wm_attributes("-disabled", True)
        self.overlay_window.wm_attributes("-alpha", self.hud_opacity)
        self.overlay_window.configure(bg="#121212")
        
        self.content_frame = tk.Frame(self.overlay_window, bg="#121212", padx=15, pady=15)
        self.content_frame.pack(fill="both", expand=True)

    def sync_position(self, game_hwnd):
        if not game_hwnd:
            game_hwnd = find_game_hwnd(self.pid)
        if game_hwnd and self.overlay_window:
            rect = get_game_client_rect_screen(game_hwnd)
            if rect:
                x, y, w, h = rect
                overlay_w = int(340 * self.hud_scale)
                overlay_h = h - 20
                
                if self.hud_position == "Left-Half":
                    overlay_x = x + 10
                    overlay_y = y + 10
                elif self.hud_position == "Right-Half":
                    overlay_x = x + w - overlay_w - 10
                    overlay_y = y + 10
                elif self.hud_position == "Top-Half":
                    overlay_w = w - 20
                    overlay_h = int(h * 0.3)
                    overlay_x = x + 10
                    overlay_y = y + 10
                else:
                    overlay_w = w - 20
                    overlay_h = int(h * 0.3)
                    overlay_x = x + 10
                    overlay_y = y + h - overlay_h - 10
                
                if overlay_h < 200:
                    overlay_h = 200
                self.overlay_window.geometry(f"{overlay_w}x{overlay_h}+{overlay_x}+{overlay_y}")

    def sync_position_loop(self):
        if self.overlay_visible and self.overlay_window:
            game_hwnd = find_game_hwnd(self.pid)
            self.sync_position(game_hwnd)
            self.root.after(200, self.sync_position_loop)

    def reload_and_draw_achievements(self):
        if not self.overlay_window:
            return
            
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        self.achievements_data = load_achievements_status(self.json_path)
        
        lbl_title = tk.Label(
            self.content_frame, text="🏆 CUSTOM ACHIEVEMENTS", 
            bg="#121212", fg="#3b82f6", font=("Segoe UI", int(12 * self.hud_scale), "bold")
        )
        lbl_title.pack(anchor="w", pady=(0, 5))
        
        unlocked_count = 0
        total_count = len(ACHIEVEMENTS)
        for ach in ACHIEVEMENTS:
            if self.achievements_data.get(ach["id"], {}).get("unlocked", False):
                unlocked_count += 1
        pct = int((unlocked_count / total_count) * 100) if total_count > 0 else 0
        
        lbl_prog = tk.Label(
            self.content_frame, text=f"{unlocked_count} / {total_count} Unlocked ({pct}%)",
            bg="#121212", fg="#10b981", font=("Segoe UI", int(9 * self.hud_scale), "bold")
        )
        lbl_prog.pack(anchor="w", pady=(0, 2))
        
        canvas_bar = tk.Canvas(self.content_frame, height=int(6 * self.hud_scale), bg="#374151", highlightthickness=0)
        canvas_bar.pack(fill="x", pady=(0, 15))
        
        def draw_progress(event=None):
            canvas_bar.delete("all")
            w = canvas_bar.winfo_width()
            fill_w = int(w * (pct / 100))
            canvas_bar.create_rectangle(0, 0, fill_w, int(6 * self.hud_scale), fill="#10b981", width=0)
        canvas_bar.bind("<Configure>", draw_progress)
        
        for ach in ACHIEVEMENTS:
            is_unlocked = self.achievements_data.get(ach["id"], {}).get("unlocked", False)
            card_bg = "#1e1e1e" if is_unlocked else "#161616"
            border_color = "#10b981" if is_unlocked else "#2d2d2d"
            text_color = "#e5e7eb" if is_unlocked else "#9ca3af"
            
            card = tk.Frame(self.content_frame, bg=card_bg, highlightthickness=1, highlightbackground=border_color)
            card.pack(fill="x", pady=3, ipady=4)
            
            parts = ach["name"].split(" ", 1)
            icon_char = parts[0] if len(parts) > 1 else "🏆"
            title_text = parts[1] if len(parts) > 1 else ach["name"]
            
            if not is_unlocked:
                icon_char = "🔒"
                
            lbl_icon = tk.Label(card, text=icon_char, bg=card_bg, fg=text_color, font=("Segoe UI", int(13 * self.hud_scale)))
            lbl_icon.pack(side="left", padx=(10, 8))
            
            txt_frame = tk.Frame(card, bg=card_bg)
            txt_frame.pack(side="left", fill="both", expand=True)
            
            lbl_c_title = tk.Label(
                txt_frame, text=title_text, bg=card_bg, fg=text_color, 
                font=("Segoe UI", int(9 * self.hud_scale), "bold"), anchor="w"
            )
            lbl_c_title.pack(anchor="w", pady=(1, 0))
            
            status_text = "Locked"
            status_color = "#9ca3af"
            if is_unlocked:
                unlocked_at = self.achievements_data[ach["id"]].get("unlocked_at", "")
                date_str = unlocked_at.split("T")[0] if unlocked_at else "Unlocked"
                status_text = f"Unlocked {date_str}"
                status_color = "#10b981"
                
            lbl_c_status = tk.Label(
                txt_frame, text=status_text, bg=card_bg, fg=status_color, 
                font=("Segoe UI", int(7 * self.hud_scale), "bold"), anchor="w"
            )
            lbl_c_status.pack(anchor="w", pady=(0, 1))

    def ram_scanner_loop(self):
        def unlock(ach_id, name, desc):
            if not self.achievements_data.get(ach_id, {}).get("unlocked", False):
                self.achievements_data[ach_id] = {
                    "unlocked": True,
                    "unlocked_at": datetime.utcnow().isoformat() + "Z",
                    "name": name,
                    "description": desc
                }
                save_achievements_status(self.json_path, self.achievements_data)
                show_toast("🏆 Achievement Unlocked!", f"{name}\n{desc}")
                print(f"UNLOCKED: {name} - {desc}", flush=True)
                self.needs_refresh = True

        while self.is_game_running():
            self.achievements_data = load_achievements_status(self.json_path)
            save_block_base = self.save_block_address - 0x5964
            
            # Read RAM data remotely using socket query
            ram_data = self.ipc_client.read_remote_memory(save_block_base, type_str="bytes", size=0x6800)
            if ram_data and len(ram_data) >= 0x4100:
                gil = int.from_bytes(ram_data[0x4FC:0x4FC+4], byteorder='little')
                if gil >= 1000000:
                    unlock("gil_millionaire", "🪙 Spiran Millionaire", "Amass 1,000,000 Gil at once.")
                    
                al_bhed_mask = int.from_bytes(ram_data[0x50C:0x50C+4], byteorder='little')
                if (al_bhed_mask & 0x03FFFFFF) == 0x03FFFFFF:
                    unlock("al_bhed_scholar", "📜 Al Bhed Scholar", "Collect all Al Bhed Primers 1 to 26 in a single playthrough.")
                    
                lightning_max = int.from_bytes(ram_data[0x5BA:0x5BA+2], byteorder='little')
                if lightning_max >= 500:
                    unlock("lightning_master", "⚡ Lightning Master", "Dodge 500 consecutive lightning bolts in the Thunder Plains.")
                    
                story_prog = ram_data[0x4E0]
                if story_prog >= 240:
                    s_levels_total = 0
                    for offset in [0x1D8 + 0x5964, 0x270 + 0x5964, 0x308 + 0x5964, 0x3A0 + 0x5964, 0x438 + 0x5964, 0x4D0 + 0x5964]:
                        if offset < len(ram_data):
                            s_levels_total += ram_data[offset]
                    if s_levels_total == 0:
                        unlock("nsg_sin", "🚫 Zero Upgrades", "Defeat Sin's Core without ever activating any nodes on the Sphere Grid.")

                if story_prog >= 220:
                    unlock("no_summons_yunalesca", "💀 Death Defied", "Defeat Yunalesca without summoning a single Aeon.")
                    
                for offset in [0x1B8 + 0x5964, 0x250 + 0x5964, 0x2E8 + 0x5964, 0x380 + 0x5964, 0x418 + 0x5964, 0x4B0 + 0x5964]:
                    if offset + 4 <= len(ram_data):
                        hp = int.from_bytes(ram_data[offset:offset+4], byteorder='little')
                        if hp == 7777:
                            unlock("lucky_sevens", "🎰 Lucky Sevens", "Deal exactly 7,777 damage in a single attack with any character.")
                            break
                            
                potion_count = 0
                items_start_offset = 0x4020
                for i in range(112):
                    slot_offset = items_start_offset + i * 2
                    if slot_offset + 1 < len(ram_data):
                        qty = ram_data[slot_offset]
                        item_id = ram_data[slot_offset + 1]
                        if item_id in [0x00, 0x01, 0x02, 0x03] and qty > 0:
                            potion_count += qty
                if potion_count >= 5:
                    unlock("potion_collector", "🧪 Potion Collector", "Have 5 or more Potions in your inventory.")
            else:
                pass
                
            time.sleep(1.0)
        self.ipc_client.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: tracker.py <PID> <GAME_DIR>")
        sys.exit(1)
        
    pid = int(sys.argv[1])
    game_dir = sys.argv[2]
    json_path = os.path.join(game_dir, "data", "custom_achievements.json")
    
    print(f"Achievements Tracker Overlay started. PID: {pid}, Game Dir: {game_dir}", flush=True)
    
    app = AchievementsOverlayApp(pid, game_dir, json_path)
    app.root.mainloop()

if __name__ == "__main__":
    main()
