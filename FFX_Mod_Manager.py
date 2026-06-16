import os
import sys
import json
import shutil
import subprocess
import tkinter as tk
import base64
import ctypes
import ctypes.wintypes
from tkinter import ttk, filedialog, messagebox, simpledialog

# Load kernel32 for process memory reading & process scanning
try:
    kernel32 = ctypes.windll.kernel32
except Exception:
    kernel32 = None



CONFIG_FILE = "ffx_mod_manager_config.json"
TOOLBOX_CONFIG = "ffx_modding_toolbox_config.json"

def encode_metadata(data_dict):
    try:
        json_str = json.dumps(data_dict, indent=2)
        key = b"AuronTidusYunaRikkuLuluWakkaKimahri"
        data_bytes = json_str.encode('utf-8')
        obfuscated = bytes([b ^ key[i % len(key)] for i, b in enumerate(data_bytes)])
        return base64.b64encode(obfuscated).decode('utf-8')
    except Exception:
        return ""

def decode_metadata(raw_content):
    if not raw_content:
        return {}
    raw_content = raw_content.strip()
    if raw_content.startswith("{") and raw_content.endswith("}"):
        try:
            return json.loads(raw_content)
        except Exception:
            pass
    try:
        key = b"AuronTidusYunaRikkuLuluWakkaKimahri"
        obfuscated = base64.b64decode(raw_content.encode('utf-8'))
        data_bytes = bytes([b ^ key[i % len(key)] for i, b in enumerate(obfuscated)])
        return json.loads(data_bytes.decode('utf-8'))
    except Exception:
        return {}


class FFXModManagerGUI:
    def __init__(self, parent, is_embedded=False):
        self.parent = parent
        self.is_embedded = is_embedded
        self.root = parent.winfo_toplevel() if is_embedded else parent
        
        # Define Themes dictionary
        self.themes = {
            "Midnight Dark": {
                "name": "Midnight Dark",
                "bg_color": "#121212",
                "card_color": "#1e1e1e",
                "accent_color": "#3b82f6",
                "accent_hover": "#2563eb",
                "text_color": "#e5e7eb",
                "text_dim": "#9ca3af",
                "border_color": "#374151",
                "success_color": "#10b981",
                "error_color": "#ef4444"
            },
            "Spira Cobalt": {
                "name": "Spira Cobalt",
                "bg_color": "#0a1128",
                "card_color": "#001f54",
                "accent_color": "#00b4d8",
                "accent_hover": "#90e0ef",
                "text_color": "#f8f9fa",
                "text_dim": "#93b7be",
                "border_color": "#0077b6",
                "success_color": "#06d6a0",
                "error_color": "#ff5a5f"
            },
            "Auron Crimson": {
                "name": "Auron Crimson",
                "bg_color": "#160f0f",
                "card_color": "#2d1717",
                "accent_color": "#ef4444",
                "accent_hover": "#f87171",
                "text_color": "#f3f4f6",
                "text_dim": "#9ca3af",
                "border_color": "#4a2222",
                "success_color": "#10b981",
                "error_color": "#ef4444"
            },
            "Yuna White": {
                "name": "Yuna White",
                "bg_color": "#f3f4f6",
                "card_color": "#ffffff",
                "accent_color": "#4f46e5",
                "accent_hover": "#4338ca",
                "text_color": "#111827",
                "text_dim": "#6b7280",
                "border_color": "#e5e7eb",
                "success_color": "#059669",
                "error_color": "#dc2626"
            }
        }
        self.load_custom_themes()
        
        # Load configs
        self.config = self.load_config()
        
        # Load current theme
        selected_theme = self.config.get("selected_theme", "Midnight Dark")
        if selected_theme not in self.themes:
            selected_theme = "Midnight Dark"
        self.current_theme_name = selected_theme
        theme = self.themes[selected_theme]
        
        self.bg_color = theme["bg_color"]
        self.card_color = theme["card_color"]
        self.accent_color = theme["accent_color"]
        self.accent_hover = theme["accent_hover"]
        self.text_color = theme["text_color"]
        self.text_dim = theme["text_dim"]
        self.border_color = theme["border_color"]
        self.success_color = theme["success_color"]
        self.error_color = theme["error_color"]

        if not is_embedded:
            self.root.title("FFX Mod Manager")
            self.root.geometry("960x600")
            self.root.minsize(800, 500)
            self.root.configure(bg=self.bg_color)
            
            # Apply TTK styles
            self.style = ttk.Style()
            self.style.theme_use("clam")
            
            self.style.configure(".", background=self.bg_color, foreground=self.text_color)
            self.style.configure("TFrame", background=self.bg_color)
            self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 10))
            self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=self.accent_color)
            self.style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "italic"), foreground=self.text_dim)
            self.style.configure("TEntry", fieldbackground=self.card_color, foreground=self.text_color, 
                                 bordercolor=self.border_color, lightcolor=self.border_color, darkcolor=self.border_color)
            self.style.map("TEntry",
                           fieldbackground=[("readonly", self.bg_color)],
                           foreground=[("readonly", self.text_dim)])
            self.style.configure("TCombobox", fieldbackground=self.card_color, background=self.card_color, 
                                 foreground=self.text_color, arrowcolor=self.accent_color, bordercolor=self.border_color)
            self.style.map("TCombobox",
                           fieldbackground=[("readonly", self.card_color), ("disabled", self.card_color)],
                           foreground=[("readonly", self.text_color), ("disabled", self.text_dim)],
                           background=[("readonly", self.card_color), ("disabled", self.card_color), ("active", self.border_color)],
                           arrowcolor=[("disabled", self.text_dim), ("!disabled", self.accent_color)],
                           bordercolor=[("focus", self.accent_color), ("!focus", self.border_color)])
            
            # Notebook tabs
            self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
            self.style.configure("TNotebook.Tab", background=self.card_color, foreground=self.text_dim, 
                                 padding=[15, 6], font=("Segoe UI", 9, "bold"), borderwidth=1, bordercolor=self.border_color)
            self.style.map("TNotebook.Tab", 
                           background=[("selected", self.accent_color), ("active", self.border_color), ("", self.card_color)],
                           foreground=[("selected", "#ffffff"), ("active", self.text_color), ("", self.text_dim)])
            
            # Scrollbar Styling
            self.style.configure("Vertical.TScrollbar", background=self.card_color, troughcolor=self.bg_color, 
                                 bordercolor=self.border_color, arrowcolor=self.accent_color,
                                 lightcolor=self.border_color, darkcolor=self.border_color)
            self.style.map("Vertical.TScrollbar",
                           background=[("active", self.accent_color), ("pressed", self.accent_color), ("", self.card_color)],
                           arrowcolor=[("active", "#ffffff"), ("", self.accent_color)])
            self.style.configure("Horizontal.TScrollbar", background=self.card_color, troughcolor=self.bg_color, 
                                 bordercolor=self.border_color, arrowcolor=self.accent_color,
                                 lightcolor=self.border_color, darkcolor=self.border_color)
            self.style.map("Horizontal.TScrollbar",
                           background=[("active", self.accent_color), ("pressed", self.accent_color), ("", self.card_color)],
                           arrowcolor=[("active", "#ffffff"), ("", self.accent_color)])

            # Treeview Styling
            self.style.configure("Treeview", background=self.card_color, fieldbackground=self.card_color, 
                                 foreground=self.text_color, borderwidth=1, bordercolor=self.border_color,
                                 font=("Segoe UI", 9), rowheight=24)
            self.style.configure("Treeview.Heading", background=self.bg_color, foreground=self.accent_color,
                                 font=("Segoe UI", 9, "bold"), borderwidth=1, bordercolor=self.border_color)
            self.style.map("Treeview", 
                           background=[("selected", self.accent_color), ("!selected", self.card_color)],
                           foreground=[("selected", "#ffffff"), ("!selected", self.text_color)])

        # Option Database for Listboxes
        self.root.option_add("*TCombobox*Listbox.background", "#ffffff")
        self.root.option_add("*TCombobox*Listbox.foreground", "#000000")
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.accent_color)
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))

        # TCombobox post click bind
        def on_combobox_click(event):
            def configure_listbox(retries=0):
                try:
                    popdown = str(event.widget) + ".popdown"
                    listbox = popdown + ".f.l"
                    if event.widget.tk.call("winfo", "exists", listbox):
                        event.widget.tk.call(
                            listbox, "configure",
                            "-background", "#ffffff",
                            "-foreground", "#000000",
                            "-selectbackground", self.accent_color,
                            "-selectforeground", "#ffffff",
                            "-font", "{Segoe UI} 10"
                        )
                    elif retries < 10:
                        event.widget.after(20, lambda: configure_listbox(retries + 1))
                except Exception:
                    if retries < 10:
                        event.widget.after(20, lambda: configure_listbox(retries + 1))
            event.widget.after(5, configure_listbox)

        self.root.bind_class("TCombobox", "<ButtonPress-1>", on_combobox_click, add="+")
        self.root.bind_class("TCombobox", "<Down>", on_combobox_click, add="+")
        
        # Paths state
        self.game_dir = ""
        self.mods_dir = ""
        self.mods_disabled_dir = ""
        
        # State tracking for pages & themes
        self.selected_mod_id = ""
        self.pages = {}
        self.sidebar_buttons = {}
        self.current_page = ""
        
        self.init_paths()
        
        # Build UI
        self.create_widgets()
        
        # Load custom plugins dynamically
        self.load_plugins()
        
        # Apply the startup theme fully and load mod list
        self.apply_theme(self.current_theme_name)
        
        # Auto-import loose files check
        self.root.after(500, self.auto_import_loose_files)

    def load_custom_themes(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        themes_dir = os.path.join(base_dir, "themes")
        if os.path.exists(themes_dir):
            try:
                for file in os.listdir(themes_dir):
                    if file.endswith(".json"):
                        path = os.path.join(themes_dir, file)
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                tdata = json.load(f)
                            required = ["name", "bg_color", "card_color", "accent_color", "accent_hover", "text_color", "text_dim", "border_color", "success_color", "error_color"]
                            if all(k in tdata for k in required):
                                self.themes[tdata["name"]] = tdata
                        except Exception:
                            pass
            except Exception:
                pass

    def apply_theme(self, theme_name):
        if theme_name not in self.themes:
            return
        self.current_theme_name = theme_name
        self.config["selected_theme"] = theme_name
        self.save_config()
        
        theme = self.themes[theme_name]
        self.bg_color = theme["bg_color"]
        self.card_color = theme["card_color"]
        self.accent_color = theme["accent_color"]
        self.accent_hover = theme["accent_hover"]
        self.text_color = theme["text_color"]
        self.text_dim = theme["text_dim"]
        self.border_color = theme["border_color"]
        self.success_color = theme["success_color"]
        self.error_color = theme["error_color"]
        
        # Configure TTK Styles
        self.style.configure(".", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("Header.TLabel", foreground=self.accent_color, background=self.bg_color)
        self.style.configure("SubHeader.TLabel", foreground=self.text_dim, background=self.bg_color)
        self.style.configure("TLabelframe", background=self.bg_color, bordercolor=self.border_color)
        self.style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.accent_color)
        self.style.configure("TPanedwindow", background=self.bg_color)
        self.style.configure("TEntry", fieldbackground=self.card_color, foreground=self.text_color, 
                             bordercolor=self.border_color, lightcolor=self.border_color, darkcolor=self.border_color)
        self.style.map("TEntry",
                       fieldbackground=[("readonly", self.bg_color)],
                       foreground=[("readonly", self.text_dim)])
        self.style.configure("TCombobox", fieldbackground=self.card_color, background=self.card_color, 
                             foreground=self.text_color, arrowcolor=self.accent_color, bordercolor=self.border_color)
        self.style.map("TCombobox",
                       fieldbackground=[("readonly", self.card_color), ("disabled", self.card_color)],
                       foreground=[("readonly", self.text_color), ("disabled", self.text_dim)],
                       background=[("readonly", self.card_color), ("disabled", self.card_color), ("active", self.border_color)],
                       arrowcolor=[("disabled", self.text_dim), ("!disabled", self.accent_color)],
                       bordercolor=[("focus", self.accent_color), ("!focus", self.border_color)])
        
        self.style.configure("Treeview", background=self.card_color, fieldbackground=self.card_color, 
                             foreground=self.text_color, borderwidth=1, bordercolor=self.border_color)
        self.style.configure("Treeview.Heading", background=self.bg_color, foreground=self.accent_color,
                             borderwidth=1, bordercolor=self.border_color)
        self.style.map("Treeview", 
                       background=[("selected", self.accent_color), ("!selected", self.card_color)],
                       foreground=[("selected", "#ffffff"), ("!selected", self.text_color)])
                       
        self.style.configure("Vertical.TScrollbar", background=self.card_color, troughcolor=self.bg_color, 
                             bordercolor=self.border_color, arrowcolor=self.accent_color)
        self.style.map("Vertical.TScrollbar",
                       background=[("active", self.accent_color), ("pressed", self.accent_color), ("", self.card_color)])
                       
        # Update widgets recursively
        self.update_widget_colors(self.parent)
        
        # Trigger redraw of mod cards to apply new border/background colors and preserve selection
        self.refresh_list()
        
        # RETHEME PLUGINS
        if hasattr(self, "plugins"):
            for plugin in self.plugins:
                if hasattr(plugin, "retheme"):
                    try:
                        plugin.retheme()
                    except Exception as e:
                        self.log(f"Error re-theming plugin: {e}", "error")

    def update_widget_colors(self, widget):
        try:
            w_class = widget.winfo_class()
        except Exception:
            # If winfo_class fails, still try to recurse children
            try:
                for child in widget.winfo_children():
                    self.update_widget_colors(child)
            except Exception:
                pass
            return
            
        try:
            if w_class == "Button":
                is_primary = getattr(widget, "_is_primary", False)
                is_success = getattr(widget, "_is_success", False)
                is_danger = getattr(widget, "_is_danger", False)
                is_sidebar = getattr(widget, "_is_sidebar", False)
                
                if is_sidebar:
                    page_id = getattr(widget, "_page_id", "")
                    if self.current_page == page_id:
                        widget.configure(bg=self.accent_color, fg="#ffffff", activebackground=self.accent_color, activeforeground="#ffffff")
                    else:
                        widget.configure(bg=self.card_color, fg=self.text_color, activebackground=self.border_color, activeforeground=self.text_color)
                elif is_primary:
                    widget.configure(bg=self.accent_color, fg="#ffffff", activebackground=self.accent_hover, activeforeground="#ffffff")
                elif is_success:
                    widget.configure(bg=self.success_color, fg="#ffffff", activebackground="#059669", activeforeground="#ffffff")
                elif is_danger:
                    widget.configure(bg=self.error_color, fg="#ffffff", activebackground="#dc2626", activeforeground="#ffffff")
                else:
                    widget.configure(bg=self.card_color, fg=self.text_color, activebackground=self.border_color, activeforeground=self.text_color)
                    
            elif w_class == "Canvas":
                widget.configure(bg=self.bg_color)
                if hasattr(widget, "_redraw_func"):
                    try:
                        widget._redraw_func()
                    except Exception:
                        pass
                        
            elif w_class == "Text":
                widget.configure(bg="#0d0d0d" if self.bg_color != "#f3f4f6" else "#ffffff", 
                                 fg="#d1d5db" if self.bg_color != "#f3f4f6" else "#111827", 
                                 insertbackground="white" if self.bg_color != "#f3f4f6" else "black")
                                 
            elif w_class == "Frame":
                is_card = getattr(widget, "_is_card", False)
                is_active_card = getattr(widget, "_is_active_card", False)
                is_sidebar_panel = getattr(widget, "_is_sidebar_panel", False)
                
                if is_active_card:
                    widget.configure(bg=self.card_color, highlightbackground=self.accent_color)
                elif is_card:
                    widget.configure(bg=self.card_color, highlightbackground=self.border_color)
                elif is_sidebar_panel:
                    widget.configure(bg=self.card_color)
                else:
                    widget.configure(bg=self.bg_color)
                    
            elif w_class == "Label":
                if getattr(widget, "_is_status_pill", False) or getattr(widget, "_is_diagnostic", False):
                    # Do not overwrite custom color-coded status pills or diagnostic banners!
                    pass
                else:
                    is_title = getattr(widget, "_is_title", False)
                    is_muted = getattr(widget, "_is_muted", False)
                    
                    parent_bg = self.bg_color
                    curr = widget.master
                    while curr:
                        try:
                            c_class = curr.winfo_class()
                            if c_class == "Frame":
                                is_card = getattr(curr, "_is_card", False)
                                is_active_card = getattr(curr, "_is_active_card", False)
                                is_sidebar_panel = getattr(curr, "_is_sidebar_panel", False)
                                if is_active_card or is_card or is_sidebar_panel:
                                    parent_bg = self.card_color
                                    break
                            bg = curr.cget("bg")
                            if bg:
                                parent_bg = bg
                                break
                        except Exception:
                            pass
                        curr = curr.master
                        
                    if is_title:
                        widget.configure(bg=parent_bg, fg=self.accent_color)
                    elif is_muted:
                        widget.configure(bg=parent_bg, fg=self.text_dim)
                    else:
                        widget.configure(bg=parent_bg, fg=self.text_color)
        except Exception:
            pass
            
        # Recurse children is guaranteed to execute
        try:
            for child in widget.winfo_children():
                self.update_widget_colors(child)
        except Exception:
            pass

    def load_config(self):
        config = {
            "game_dir": "",
            "mods_dir": "",
            "mods_disabled_dir": "",
            "selected_theme": "Midnight Dark"
        }
        
        # 1. Try Mod Manager config
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config.update(json.load(f))
                    return config
            except Exception:
                pass
                
        # 2. Try Modding Toolbox config
        if os.path.exists(TOOLBOX_CONFIG):
            try:
                with open(TOOLBOX_CONFIG, "r", encoding="utf-8") as f:
                    toolbox = json.load(f)
                    path = toolbox.get("loose_folder_path", "")
                    if path:
                        if path.lower().endswith(r"\data\mods") or path.lower().endswith("/data/mods"):
                            config["game_dir"] = os.path.dirname(os.path.dirname(path))
                            config["mods_dir"] = path
                            config["mods_disabled_dir"] = os.path.join(os.path.dirname(path), "mods_disabled")
                        elif path.lower().endswith(r"\data") or path.lower().endswith("/data"):
                            config["game_dir"] = os.path.dirname(path)
                            config["mods_dir"] = os.path.join(path, "mods")
                            config["mods_disabled_dir"] = os.path.join(path, "mods_disabled")
            except Exception:
                pass
                
        return config

    def save_config(self):
        try:
            self.config["game_dir"] = self.game_dir
            self.config["mods_dir"] = self.mods_dir
            self.config["mods_disabled_dir"] = self.mods_disabled_dir
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def get_steam_install_path(self):
        try:
            import winreg
            for key_path in [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 359870",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 359870"
            ]:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    val, _ = winreg.QueryValueEx(key, "InstallLocation")
                    if val and os.path.exists(val):
                        return val
                except Exception:
                    pass
        except Exception:
            pass
        
        fallback = r"C:\Program Files (x86)\Steam\steamapps\common\FINAL FANTASY FFX&FFX-2 HD Remaster"
        if os.path.exists(fallback):
            return fallback
        return ""

    def init_paths(self):
        # Default Game Dir auto-detect
        if not self.config.get("game_dir"):
            self.game_dir = self.get_steam_install_path()
        else:
            self.game_dir = self.config["game_dir"]
            
        if self.game_dir:
            self.mods_dir = os.path.join(self.game_dir, "data", "mods")
            self.mods_disabled_dir = os.path.join(self.game_dir, "data", "mods_disabled")
            
            # Create directories if they don't exist
            try:
                os.makedirs(self.mods_dir, exist_ok=True)
                os.makedirs(self.mods_disabled_dir, exist_ok=True)
            except Exception:
                pass
        else:
            self.mods_dir = ""
            self.mods_disabled_dir = ""

    def check_loader_status(self):
        if not self.game_dir:
            return "Unknown (Configure Game Folder)", self.error_color
            
        # Check for UnX / External Loader DLLs
        loaders = ["d3d11.dll", "dinput8.dll", "dxgi.dll"]
        found = []
        for loader in loaders:
            if os.path.exists(os.path.join(self.game_dir, loader)):
                found.append(loader)
                
        if found:
            return f"🟢 Active Mod Loader Detected ({', '.join(found)})", self.success_color
        else:
            return "⚠️ Mod Loader DLL NOT Detected! (Mods will not load. Please install External File Loader)", self.error_color

    def log(self, text, tag=None):
        msg = str(text)
        if not msg.endswith("\n"):
            msg += "\n"
        if tag is None:
            tag = "error" if "error" in msg.lower() or "failed" in msg.lower() else "success" if "success" in msg.lower() else "info"
        
        def update():
            if hasattr(self, "txt_log") and self.txt_log:
                self.txt_log.insert(tk.END, msg, tag)
                self.txt_log.see(tk.END)
        self.root.after(0, update)

    def clear_log(self):
        if hasattr(self, "txt_log") and self.txt_log:
            self.txt_log.delete("1.0", tk.END)

    def create_widgets(self):
        # Main Layout Container
        main_layout = tk.Frame(self.parent, bg=self.bg_color)
        main_layout.pack(fill="both", expand=True)
        
        # 1. Left Sidebar Panel
        self.sidebar = tk.Frame(main_layout, bg=self.card_color, highlightthickness=0)
        self.sidebar._is_sidebar_panel = True
        self.sidebar.pack(side="left", fill="y")
        
        # Logo/Header inside Sidebar
        lbl_logo = tk.Label(self.sidebar, text="🎮 FFX MODS", font=("Segoe UI", 12, "bold"), fg=self.accent_color, bg=self.card_color, pady=15)
        lbl_logo._is_title = True
        lbl_logo.pack(fill="x")
        
        # Global Launch Button
        self.btn_sidebar_launch = tk.Button(self.sidebar, text="🎮 PLAY GAME", font=("Segoe UI", 10, "bold"),
                                             fg="#ffffff", bg=self.accent_color, relief="flat", activebackground=self.accent_hover,
                                             command=self.launch_game, pady=10, bd=0)
        self.btn_sidebar_launch._is_primary = True
        self.btn_sidebar_launch.pack(fill="x", padx=15, pady=(5, 15))
        self.bind_hover(self.btn_sidebar_launch, is_primary=True)
        
        # Navigation Buttons Container (Bottom)
        self.sidebar_bottom_frame = tk.Frame(self.sidebar, bg=self.card_color)
        self.sidebar_bottom_frame.pack(side="bottom", fill="x", pady=15)
        
        # Navigation Buttons Container (Top)
        self.sidebar_buttons_frame = tk.Frame(self.sidebar, bg=self.card_color)
        self.sidebar_buttons_frame.pack(fill="x", pady=10)
        
        # 2. Right Content & Workspace Panel
        self.content_container = tk.Frame(main_layout, bg=self.bg_color)
        self.content_container.pack(side="left", fill="both", expand=True)
        
        # Standard Pages Frames
        self.page_mods_frame = tk.Frame(self.content_container, bg=self.bg_color)
        self.page_settings_frame = tk.Frame(self.content_container, bg=self.bg_color)
        
        # Register standard pages
        self.pages["mods"] = {
            "name": "Mods",
            "frame": self.page_mods_frame,
            "icon": "📁"
        }
        self.pages["settings"] = {
            "name": "Settings",
            "frame": self.page_settings_frame,
            "icon": "⚙️"
        }
        
        # Add sidebar navigation options for standard pages
        self.add_sidebar_nav_button("mods", "Mods", "📁")
        
        # ----------------------------------------------------
        # PAGE 1: MODS PANEL LAYOUT
        # ----------------------------------------------------
        paned = ttk.Panedwindow(self.page_mods_frame, orient="horizontal")
        paned.pack(fill="both", expand=True)
        
        # Left Panel - Mod list container
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        lbl_mod = tk.Label(left_frame, text="Available Mods", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.bg_color)
        lbl_mod._is_title = True
        lbl_mod.pack(anchor="w", pady=(0, 5))
        
        # Scrollable Mod Cards Frame
        cards_pane = ttk.Frame(left_frame)
        cards_pane.pack(fill="both", expand=True)
        
        self.cards_canvas = tk.Canvas(cards_pane, bg=self.bg_color, highlightthickness=0, borderwidth=0)
        self.cards_scrollbar = ttk.Scrollbar(cards_pane, orient="vertical", command=self.cards_canvas.yview)
        
        self.mod_cards_container = ttk.Frame(self.cards_canvas)
        self.cards_canvas.configure(yscrollcommand=self.cards_scrollbar.set)
        
        self.cards_scrollbar.pack(side="right", fill="y")
        self.cards_canvas.pack(side="left", fill="both", expand=True)
        
        self.cards_window = self.cards_canvas.create_window((0, 0), window=self.mod_cards_container, anchor="nw")
        
        def on_cards_configure(event):
            self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all"))
        self.mod_cards_container.bind("<Configure>", on_cards_configure)
        
        def on_canvas_configure(event):
            self.cards_canvas.itemconfig(self.cards_window, width=event.width)
        self.cards_canvas.bind("<Configure>", on_canvas_configure)
        
        def _on_cards_mousewheel(event):
            self.cards_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def bind_cards_mouse(event):
            self.cards_canvas.bind_all("<MouseWheel>", _on_cards_mousewheel)
        def unbind_cards_mouse(event):
            self.cards_canvas.unbind_all("<MouseWheel>")
        self.cards_canvas.bind("<Enter>", bind_cards_mouse)
        self.cards_canvas.bind("<Leave>", unbind_cards_mouse)
        
        # Action buttons underneath card list
        btn_p_frame = ttk.Frame(left_frame, padding=(0, 5, 0, 0))
        btn_p_frame.pack(fill="x")
        
        btn_enable = tk.Button(btn_p_frame, text="⚡ Enable Mod (Install)", command=self.enable_mod, bg=self.success_color,
                               fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#059669")
        btn_enable._is_success = True
        btn_enable.pack(fill="x", pady=2)
        self.bind_hover(btn_enable)
        
        btn_disable = tk.Button(btn_p_frame, text="⏪ Disable Mod (Uninstall)", command=self.disable_mod, bg=self.card_color,
                                fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color)
        btn_disable.pack(fill="x", pady=2)
        self.bind_hover(btn_disable)
        
        btn_new = tk.Button(btn_p_frame, text="Create New Mod", command=self.create_mod, bg=self.accent_color,
                            fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover)
        btn_new._is_primary = True
        btn_new.pack(fill="x", pady=2)
        self.bind_hover(btn_new, is_primary=True)
        
        btn_del = tk.Button(btn_p_frame, text="Delete Mod From Disk", command=self.delete_mod, bg=self.error_color,
                            fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#dc2626")
        btn_del._is_danger = True
        btn_del.pack(fill="x", pady=2)
        self.bind_hover(btn_del)
        
        btn_refresh = tk.Button(btn_p_frame, text="🔄 Refresh Mod List", command=self.refresh_list, bg=self.card_color,
                                fg=self.text_color, font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color)
        btn_refresh.pack(fill="x", pady=2)
        self.bind_hover(btn_refresh)
        
        # Right Panel - Mod Details
        right_frame = ttk.Frame(paned, padding=(15, 0, 0, 0))
        paned.add(right_frame, weight=1)
        
        self.lbl_mod_title = tk.Label(right_frame, text="Selected Mod: <None>", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.bg_color)
        self.lbl_mod_title._is_title = True
        self.lbl_mod_title.pack(anchor="w", pady=(0, 5))
        
        # Metadata Card
        meta_frame = ttk.LabelFrame(right_frame, text=" Mod Information ", padding=10)
        meta_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(meta_frame, text="Mod Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_mod_name = ttk.Entry(meta_frame, width=30)
        self.ent_mod_name.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(meta_frame, text="Creator:").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_mod_creator = ttk.Entry(meta_frame, width=30)
        self.ent_mod_creator.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(meta_frame, text="Version:").grid(row=2, column=0, sticky="w", pady=2)
        self.ent_mod_version = ttk.Entry(meta_frame, width=15)
        self.ent_mod_version.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(meta_frame, text="Description:").grid(row=3, column=0, sticky="nw", pady=2)
        self.ent_mod_desc = ttk.Entry(meta_frame, width=30)
        self.ent_mod_desc.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        btn_save_meta = tk.Button(meta_frame, text="Save Details", command=self.save_mod_metadata, bg=self.card_color,
                                  fg=self.text_color, relief="flat", activebackground=self.border_color)
        btn_save_meta.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.bind_hover(btn_save_meta)
        
        # Files Treeview
        lbl_files = tk.Label(right_frame, text="Files Installed by Mod", font=("Segoe UI", 9, "bold"), fg=self.text_color, bg=self.bg_color)
        lbl_files.pack(anchor="w", pady=(5, 2))
        files_frame = ttk.Frame(right_frame)
        files_frame.pack(fill="both", expand=True)
        
        self.tree_files = ttk.Treeview(files_frame, columns=("relpath", "size"), show="headings")
        self.tree_files.heading("relpath", text="Relative Game Path")
        self.tree_files.heading("size", text="Size")
        self.tree_files.column("relpath", width=250, anchor="w")
        self.tree_files.column("size", width=80, anchor="e")
        self.tree_files.pack(fill="both", expand=True, side="left")
        
        scroll_f = ttk.Scrollbar(files_frame, command=self.tree_files.yview)
        scroll_f.pack(fill="y", side="right")
        self.tree_files.config(yscrollcommand=scroll_f.set)
        
        # File Operations
        file_ops = ttk.Frame(right_frame, padding=(0, 5, 0, 0))
        file_ops.pack(fill="x")
        
        btn_import = tk.Button(file_ops, text="Import File(s)...", command=self.import_files, bg=self.accent_color,
                               fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover)
        btn_import._is_primary = True
        btn_import.pack(side="left", padx=(0, 5))
        self.bind_hover(btn_import, is_primary=True)
        
        btn_import_dir = tk.Button(file_ops, text="Import Folder...", command=self.import_folder, bg=self.accent_color,
                                   fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover)
        btn_import_dir._is_primary = True
        btn_import_dir.pack(side="left", padx=5)
        self.bind_hover(btn_import_dir, is_primary=True)
        
        btn_open = tk.Button(file_ops, text="Open Folder Location", command=self.open_folder, bg=self.card_color,
                             fg=self.text_color, relief="flat", activebackground=self.border_color)
        btn_open.pack(side="left", padx=5)
        self.bind_hover(btn_open)
        
        # ----------------------------------------------------
        # PAGE 2: SETTINGS PANEL LAYOUT
        # ----------------------------------------------------
        # Folder directory settings (Card Style)
        dir_card = tk.Frame(self.page_settings_frame, bg=self.card_color, highlightthickness=1, highlightbackground=self.border_color, padx=15, pady=15)
        dir_card._is_card = True
        dir_card.pack(fill="x", pady=(0, 10))
        
        lbl_dir_title = tk.Label(dir_card, text="Game Directory Settings", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_color)
        lbl_dir_title._is_title = True
        lbl_dir_title.pack(anchor="w", pady=(0, 10))
        
        path_row = tk.Frame(dir_card, bg=self.card_color)
        path_row.pack(fill="x")
        path_row.columnconfigure(1, weight=1)
        
        lbl_path = tk.Label(path_row, text="FFX Game Folder:", bg=self.card_color, fg=self.text_color)
        lbl_path.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.ent_game_path = ttk.Entry(path_row, width=40)
        self.ent_game_path.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        if self.game_dir:
            self.ent_game_path.insert(0, self.game_dir)
        self.ent_game_path.bind("<FocusOut>", self.on_game_path_changed)
        self.ent_game_path.bind("<Return>", self.on_game_path_changed)
        
        btn_browse = tk.Button(path_row, text="Browse...", command=self.browse_game_folder, bg=self.bg_color, 
                               fg=self.text_color, relief="flat", activebackground=self.border_color, padx=10)
        btn_browse.grid(row=0, column=2, padx=(0, 10))
        self.bind_hover(btn_browse)
        
        btn_launch = tk.Button(path_row, text="🎮 Launch FFX", command=self.launch_game, bg=self.accent_color,
                               fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover, padx=10)
        btn_launch._is_primary = True
        btn_launch.grid(row=0, column=3)
        self.bind_hover(btn_launch, is_primary=True)
        
        # Mod Loader Diagnostic Banner
        self.lbl_loader_status = tk.Label(self.page_settings_frame, text="", font=("Segoe UI", 9, "bold"), anchor="w")
        self.lbl_loader_status._is_diagnostic = True
        self.lbl_loader_status.pack(fill="x", pady=5)
        self.update_loader_status_ui()
        
        # Theme Settings (Card Style)
        theme_card = tk.Frame(self.page_settings_frame, bg=self.card_color, highlightthickness=1, highlightbackground=self.border_color, padx=15, pady=15)
        theme_card._is_card = True
        theme_card.pack(fill="x", pady=10)
        
        lbl_theme_title = tk.Label(theme_card, text="Appearance Theme Settings", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_color)
        lbl_theme_title._is_title = True
        lbl_theme_title.pack(anchor="w", pady=(0, 10))
        
        theme_row = tk.Frame(theme_card, bg=self.card_color)
        theme_row.pack(fill="x")
        
        lbl_select = tk.Label(theme_row, text="Active Theme:", bg=self.card_color, fg=self.text_color)
        lbl_select.pack(side="left", padx=(0, 10))
        
        self.theme_selector = ttk.Combobox(theme_row, values=list(self.themes.keys()), state="readonly", width=20)
        self.theme_selector.set(self.current_theme_name)
        self.theme_selector.pack(side="left", padx=(0, 15))
        self.theme_selector.bind("<<ComboboxSelected>>", lambda e: self.apply_theme(self.theme_selector.get()))
        
        btn_open_themes = tk.Button(theme_card, text="📂 Open Custom Themes Folder", command=self.open_themes_folder, bg=self.bg_color,
                                    fg=self.text_color, relief="flat", activebackground=self.border_color, padx=12, pady=4)
        btn_open_themes.pack(anchor="w", pady=(15, 0))
        self.bind_hover(btn_open_themes)
        
        # ----------------------------------------------------
        # 3. GLOBAL CONSOLE LOG PANEL (Always at bottom of Content Panel)
        # ----------------------------------------------------
        log_label = tk.Label(self.content_container, text="Console Log", font=("Segoe UI", 10, "bold"), fg=self.accent_color, bg=self.bg_color, anchor="w")
        log_label._is_title = True
        log_label.pack(fill="x", pady=(15, 2), padx=15)
        
        log_frame = tk.Frame(self.content_container, bg=self.bg_color)
        log_frame.pack(fill="x", side="bottom", expand=False, padx=15, pady=(0, 15))
        
        self.txt_log = tk.Text(log_frame, height=5, bg="#0d0d0d", fg="#d1d5db", insertbackground="white",
                               relief="flat", font=("Consolas", 9), borderwidth=0)
        self.txt_log.pack(fill="both", side="left", expand=True)
        
        self.txt_log.tag_configure("info", foreground="#60a5fa")
        self.txt_log.tag_configure("success", foreground="#34d399")
        self.txt_log.tag_configure("error", foreground="#f87171")
        self.txt_log.tag_configure("default", foreground="#d1d5db")
        
        log_scroll = ttk.Scrollbar(log_frame, command=self.txt_log.yview)
        log_scroll.pack(fill="y", side="right")
        self.txt_log.config(yscrollcommand=log_scroll.set)
        
        # Add Settings button to navigation drawer
        self.add_sidebar_nav_button("settings", "Settings", "⚙️", side="bottom")
        
        # Set default active page
        self.switch_to_page("mods")

    def add_sidebar_nav_button(self, page_id, text, icon="", side="top"):
        parent_frame = self.sidebar_bottom_frame if side == "bottom" else self.sidebar_buttons_frame
        btn = tk.Button(parent_frame, text=f"  {icon}   {text}", font=("Segoe UI", 10, "bold"),
                        anchor="w", relief="flat", padx=20, pady=10, bg=self.card_color, fg=self.text_color,
                        activebackground=self.border_color, activeforeground=self.text_color, bd=0)
        btn._is_sidebar = True
        btn._page_id = page_id
        btn.pack(fill="x", pady=2)
        btn.config(command=lambda: self.switch_to_page(page_id))
        self.sidebar_buttons[page_id] = btn
        self.bind_hover(btn)

    def switch_to_page(self, page_id):
        self.current_page = page_id
        
        # Hide all frames
        for pid, pinfo in self.pages.items():
            pinfo["frame"].pack_forget()
            btn = self.sidebar_buttons.get(pid)
            if btn:
                btn.configure(bg=self.card_color, fg=self.text_color)
                
        # Show active frame
        active_p = self.pages[page_id]
        active_p["frame"].pack(fill="both", expand=True, padx=15, pady=15)
        
        btn = self.sidebar_buttons.get(page_id)
        if btn:
            btn.configure(bg=self.accent_color, fg="#ffffff")
            
        # Update colors recursively to ensure active sidebar styling updates correctly
        if hasattr(self, "sidebar") and self.sidebar:
            self.update_widget_colors(self.sidebar)

    def open_themes_folder(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        themes_dir = os.path.join(base_dir, "themes")
        os.makedirs(themes_dir, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(themes_dir)
        else:
            subprocess.Popen(["xdg-open", themes_dir])


    def update_loader_status_ui(self):
        status, color = self.check_loader_status()
        if hasattr(self, "lbl_loader_status") and self.lbl_loader_status:
            self.lbl_loader_status.config(text=status)
            if "active" in status.lower() or "🟢" in status:
                self.lbl_loader_status.config(bg="#064e3b", fg="#10b981", padx=15, pady=8, bd=1, relief="solid", highlightthickness=0)
            else:
                self.lbl_loader_status.config(bg="#7f1d1d", fg="#ef4444", padx=15, pady=8, bd=1, relief="solid", highlightthickness=0)

    def on_game_path_changed(self, event=None):
        path = self.ent_game_path.get().strip()
        if path != self.game_dir:
            self.game_dir = path
            self.init_paths()
            self.save_config()
            self.update_loader_status_ui()
            self.scan_mods()

    def browse_game_folder(self):
        folder = filedialog.askdirectory(title="Select Game Installation Directory")
        if folder:
            abspath = os.path.abspath(folder)
            self.ent_game_path.delete(0, tk.END)
            self.ent_game_path.insert(0, abspath)
            self.game_dir = abspath
            self.init_paths()
            self.save_config()
            self.update_loader_status_ui()
            self.scan_mods()

    def refresh_list(self):
        selected_id = self.selected_mod_id
        self.scan_mods()
        
        # Check if selected mod still exists
        exists = False
        for child in self.mod_cards_container.winfo_children():
            if getattr(child, "_is_card", False) and getattr(child, "_mod_id", None) == selected_id:
                exists = True
                break
                
        if selected_id and exists:
            self.select_mod(selected_id)
        else:
            self.selected_mod_id = ""
            self.clear_metadata_fields()
            self.tree_files.delete(*self.tree_files.get_children())
            self.lbl_mod_title.config(text="Selected Mod: <None>")
            
        self.log("Mod list refreshed.", "info")

    def scan_mods(self):
        for widget in self.mod_cards_container.winfo_children():
            widget.destroy()
            
        if not self.mods_dir or not self.mods_disabled_dir:
            return
            
        mods = {}
        
        # 1. Scan enabled mods in mods folder (looking for tracking ffxmod / json files)
        try:
            for file in os.listdir(self.mods_dir):
                if file.endswith((".ffxmod", ".json")) and not file.startswith("modinfo"):
                    mod_id, _ = os.path.splitext(file)
                    try:
                        with open(os.path.join(self.mods_dir, file), "r") as f:
                            data = decode_metadata(f.read())
                            mods[mod_id] = {
                                "name": data.get("name", mod_id),
                                "status": "Enabled",
                                "files": data.get("files", []),
                                "size": data.get("size", 0)
                            }
                    except Exception:
                        pass
        except Exception:
            pass
            
        # 2. Scan disabled mods in mods_disabled folder
        try:
            for d in os.listdir(self.mods_disabled_dir):
                dpath = os.path.join(self.mods_disabled_dir, d)
                if os.path.isdir(dpath):
                    info_path = os.path.join(dpath, "modinfo.ffxmod")
                    if not os.path.exists(info_path):
                        info_path = os.path.join(dpath, "modinfo.json")
                        
                    if os.path.exists(info_path):
                        try:
                            with open(info_path, "r") as f:
                                data = decode_metadata(f.read())
                                if d in mods:
                                    continue
                                    
                                files_list = data.get("files", [])
                                total_size = 0
                                for rel in files_list:
                                    fpath = os.path.join(dpath, rel)
                                    if os.path.exists(fpath):
                                        total_size += os.path.getsize(fpath)
                                        
                                mods[d] = {
                                    "name": data.get("name", d),
                                    "status": "Disabled",
                                    "files": files_list,
                                    "size": total_size
                                }
                        except Exception:
                            pass
                    else:
                        if d not in mods:
                            mods[d] = {
                                "name": d,
                                "status": "Disabled",
                                "files": [],
                                "size": 0
                            }
        except Exception:
            pass
            
        # Render Mod Cards
        for mod_id, info in mods.items():
            self.create_mod_card(mod_id, info)
            
        # Trigger dynamic canvas resize config update
        self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all"))

    def create_mod_card(self, mod_id, info):
        is_selected = (self.selected_mod_id == mod_id)
        card = tk.Frame(self.mod_cards_container, highlightthickness=1, bd=0)
        card._is_card = True
        card._is_active_card = is_selected
        card._mod_id = mod_id
        
        border = self.accent_color if is_selected else self.border_color
        card.configure(bg=self.card_color, highlightbackground=border, highlightcolor=border)
        card.pack(fill="x", pady=4, padx=5, ipady=5)
        
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=0)
        
        # Top Row: Mod Name & Status Pill
        top_row = tk.Frame(card, bg=self.card_color)
        top_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=2)
        top_row.columnconfigure(0, weight=1)
        
        lbl_name = tk.Label(top_row, text=info["name"], font=("Segoe UI", 10, "bold"), fg=self.text_color, bg=self.card_color, anchor="w")
        lbl_name.grid(row=0, column=0, sticky="w")
        
        status = info["status"]
        status_bg = "#064e3b" if status == "Enabled" else "#374151"
        status_fg = "#10b981" if status == "Enabled" else self.text_dim
        lbl_status = tk.Label(top_row, text=f" {status} ", font=("Segoe UI", 8, "bold"), fg=status_fg, bg=status_bg, padx=6, pady=2)
        lbl_status._is_status_pill = True
        lbl_status.grid(row=0, column=1, sticky="e")
        
        # Bottom Row: Files count & Size
        bottom_row = tk.Frame(card, bg=self.card_color)
        bottom_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=2)
        bottom_row.columnconfigure(0, weight=1)
        
        info_text = f"Files: {len(info['files'])}  |  Size: {self.get_friendly_size(info['size'])}"
        lbl_info = tk.Label(bottom_row, text=info_text, font=("Segoe UI", 8), fg=self.text_dim, bg=self.card_color, anchor="w")
        lbl_info._is_muted = True
        lbl_info.grid(row=0, column=0, sticky="w")
        
        # Click binding for card selection
        def select_click(event, m_id=mod_id):
            self.select_mod(m_id)
            
        card.bind("<Button-1>", select_click)
        top_row.bind("<Button-1>", select_click)
        bottom_row.bind("<Button-1>", select_click)
        lbl_name.bind("<Button-1>", select_click)
        lbl_status.bind("<Button-1>", select_click)
        lbl_info.bind("<Button-1>", select_click)
        
        # Hover bindings
        def on_enter(event, c=card):
            if self.selected_mod_id != mod_id:
                c.configure(highlightbackground=self.accent_color)
        def on_leave(event, c=card):
            if self.selected_mod_id != mod_id:
                c.configure(highlightbackground=self.border_color)
                
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    def select_mod(self, mod_id):
        self.selected_mod_id = mod_id
        
        # Update cards border styling dynamically
        for child in self.mod_cards_container.winfo_children():
            if getattr(child, "_is_card", False):
                m_id = getattr(child, "_mod_id", None)
                if m_id == mod_id:
                    child._is_active_card = True
                    child.configure(highlightbackground=self.accent_color, highlightcolor=self.accent_color)
                else:
                    child._is_active_card = False
                    child.configure(highlightbackground=self.border_color, highlightcolor=self.border_color)
                    
        self.lbl_mod_title.config(text=f"Selected Mod: {mod_id}")
        
        # Load mod details from repo modinfo
        info_path = os.path.join(self.mods_disabled_dir, mod_id, "modinfo.ffxmod")
        fallback_path = os.path.join(self.mods_disabled_dir, mod_id, "modinfo.json")
        read_path = info_path if os.path.exists(info_path) else fallback_path if os.path.exists(fallback_path) else info_path
        
        info = {}
        if os.path.exists(read_path):
            try:
                with open(read_path, "r") as f:
                    info = decode_metadata(f.read())
            except Exception:
                pass
                
        # If not in repo, try active tracker
        if not info:
            tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
            old_tracker_path = os.path.join(self.mods_dir, f"{mod_id}.json")
            read_tracker = tracker_path if os.path.exists(tracker_path) else old_tracker_path if os.path.exists(old_tracker_path) else tracker_path
            if os.path.exists(read_tracker):
                try:
                    with open(read_tracker, "r") as f:
                        info = decode_metadata(f.read())
                except Exception:
                    pass
                    
        self.ent_mod_name.delete(0, tk.END)
        self.ent_mod_name.insert(0, info.get("name", mod_id))
        
        self.ent_mod_creator.config(state="normal")
        self.ent_mod_creator.delete(0, tk.END)
        creator_name = info.get("creator", "")
        self.ent_mod_creator.insert(0, creator_name)
        
        # Lock Creator field in GUI if it is set to anything other than the default ('User' or empty)
        if creator_name.strip().lower() in ["", "user"]:
            self.ent_mod_creator.config(state="normal")
        else:
            self.ent_mod_creator.config(state="readonly")
            
        self.ent_mod_version.delete(0, tk.END)
        self.ent_mod_version.insert(0, info.get("version", "1.0"))
        
        self.ent_mod_desc.delete(0, tk.END)
        self.ent_mod_desc.insert(0, info.get("description", ""))
        
        # Populate files list
        self.tree_files.delete(*self.tree_files.get_children())
        files_list = info.get("files", [])
        
        mod_status = self.get_mod_status(mod_id)
        mod_repo_path = os.path.join(self.mods_disabled_dir, mod_id)
        
        for rel in files_list:
            # Check size from repo if disabled, or active mods folder if enabled
            fsize = 0
            src_path = os.path.join(mod_repo_path if mod_status == "Disabled" else self.mods_dir, rel)
            if os.path.exists(src_path):
                fsize = os.path.getsize(src_path)
            self.tree_files.insert("", tk.END, values=(rel, self.get_friendly_size(fsize)))

    def auto_import_loose_files(self):
        if not self.mods_dir:
            return
            
        # 1. Gather all files that belong to currently enabled mods
        managed_files = set()
        try:
            for file in os.listdir(self.mods_dir):
                if file.endswith((".ffxmod", ".json")) and not file.startswith("modinfo"):
                    try:
                        with open(os.path.join(self.mods_dir, file), "r") as f:
                            data = decode_metadata(f.read())
                            for rel in data.get("files", []):
                                managed_files.add(rel.replace("\\", "/").lower())
                    except Exception:
                        pass
        except Exception:
            pass
            
        # 2. Find truly unmanaged loose files inside ffx_data and ffx_ps2
        unmanaged_files = []
        total_size = 0
        
        for folder in ["ffx_data", "ffx_ps2"]:
            src_folder = os.path.join(self.mods_dir, folder)
            if os.path.isdir(src_folder):
                for root, dirs, files in os.walk(src_folder):
                    for file in files:
                        full_src = os.path.join(root, file)
                        rel = os.path.relpath(full_src, self.mods_dir)
                        rel_unix = rel.replace("\\", "/")
                        
                        if rel_unix.lower() not in managed_files:
                            unmanaged_files.append(rel_unix)
                            total_size += os.path.getsize(full_src)
                            
        if not unmanaged_files:
            return
            
        # Check if we already have an Imported Backup mod info (check both .ffxmod and legacy .json)
        backup_info_path = os.path.join(self.mods_dir, "Imported_Backup.ffxmod")
        if os.path.exists(backup_info_path) or os.path.exists(os.path.join(self.mods_dir, "Imported_Backup.json")):
            return
            
        ans = messagebox.askyesno(
            "Unmanaged Files Detected",
            f"The manager detected {len(unmanaged_files)} unmanaged loose files directly inside your mods folder (outside of active mod packages).\n\n"
            "Would you like to import them into a managed project ('Imported Backup')?\n"
            "This will let you enable/disable them safely without losing your current modifications."
        )
        if not ans:
            return
            
        self.log(f"Starting import of {len(unmanaged_files)} unmanaged loose files...")
        
        backup_repo = os.path.join(self.mods_disabled_dir, "Imported_Backup")
        os.makedirs(backup_repo, exist_ok=True)
        
        # Write modinfo.ffxmod to repository
        modinfo = {
            "name": "Imported Backup",
            "creator": "Auto-Imported",
            "version": "1.0",
            "description": "Loose files backed up and managed automatically.",
            "files": unmanaged_files
        }
        with open(os.path.join(backup_repo, "modinfo.ffxmod"), "w") as f:
            f.write(encode_metadata(modinfo))
            
        # Write tracking file to mods folder
        tracking = {
            "name": "Imported Backup",
            "files": unmanaged_files,
            "size": total_size
        }
        with open(backup_info_path, "w") as f:
            f.write(encode_metadata(tracking))
            
        self.log(f"Successfully imported and backed up {len(unmanaged_files)} loose files!", "success")
        self.scan_mods()
 
    def on_mod_selected(self, event=None):
        sel = self.tree_mods.selection()
        if not sel:
            self.lbl_mod_title.config(text="Selected Mod: <None>")
            self.clear_metadata_fields()
            self.tree_files.delete(*self.tree_mods.get_children())
            return
            
        mod_id = sel[0]
        self.lbl_mod_title.config(text=f"Selected Mod: {mod_id}")
        
        # Load mod details from repo modinfo
        info_path = os.path.join(self.mods_disabled_dir, mod_id, "modinfo.ffxmod")
        fallback_path = os.path.join(self.mods_disabled_dir, mod_id, "modinfo.json")
        read_path = info_path if os.path.exists(info_path) else fallback_path if os.path.exists(fallback_path) else info_path
        
        info = {}
        if os.path.exists(read_path):
            try:
                with open(read_path, "r") as f:
                    info = decode_metadata(f.read())
            except Exception:
                pass
                
        # If not in repo, try active tracker
        if not info:
            tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
            old_tracker_path = os.path.join(self.mods_dir, f"{mod_id}.json")
            read_tracker = tracker_path if os.path.exists(tracker_path) else old_tracker_path if os.path.exists(old_tracker_path) else tracker_path
            if os.path.exists(read_tracker):
                try:
                    with open(read_tracker, "r") as f:
                        info = decode_metadata(f.read())
                except Exception:
                    pass
                    
        self.ent_mod_name.delete(0, tk.END)
        self.ent_mod_name.insert(0, info.get("name", mod_id))
        
        self.ent_mod_creator.config(state="normal")
        self.ent_mod_creator.delete(0, tk.END)
        creator_name = info.get("creator", "")
        self.ent_mod_creator.insert(0, creator_name)
        
        # Lock Creator field in GUI if it is set to anything other than the default ('User' or empty)
        if creator_name.strip().lower() in ["", "user"]:
            self.ent_mod_creator.config(state="normal")
        else:
            self.ent_mod_creator.config(state="readonly")
        
        self.ent_mod_version.delete(0, tk.END)
        self.ent_mod_version.insert(0, info.get("version", "1.0"))
        
        self.ent_mod_desc.delete(0, tk.END)
        self.ent_mod_desc.insert(0, info.get("description", ""))
        
        # Populate files list
        self.tree_files.delete(*self.tree_files.get_children())
        files_list = info.get("files", [])
        
        mod_status = self.get_mod_status(mod_id)
        mod_repo_path = os.path.join(self.mods_disabled_dir, mod_id)
        
        for rel in files_list:
            # Check size from repo if disabled, or active mods folder if enabled
            fsize = 0
            src_path = os.path.join(mod_repo_path if mod_status == "Disabled" else self.mods_dir, rel)
            if os.path.exists(src_path):
                fsize = os.path.getsize(src_path)
            self.tree_files.insert("", tk.END, values=(rel, self.get_friendly_size(fsize)))
 
    def get_mod_status(self, mod_id):
        tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
        old_tracker_path = os.path.join(self.mods_dir, f"{mod_id}.json")
        return "Enabled" if (os.path.exists(tracker_path) or os.path.exists(old_tracker_path)) else "Disabled"
 
    def clear_metadata_fields(self):
        self.ent_mod_creator.config(state="normal")
        self.ent_mod_name.delete(0, tk.END)
        self.ent_mod_creator.delete(0, tk.END)
        self.ent_mod_version.delete(0, tk.END)
        self.ent_mod_desc.delete(0, tk.END)

    def save_mod_metadata(self):
        mod_id = self.selected_mod_id
        if not mod_id:
            messagebox.showwarning("Warning", "Please select a mod first.")
            return
            
        mod_repo_path = os.path.join(self.mods_disabled_dir, mod_id)
        os.makedirs(mod_repo_path, exist_ok=True)
        
        info_path = os.path.join(mod_repo_path, "modinfo.ffxmod")
        fallback_path = os.path.join(mod_repo_path, "modinfo.json")
        read_path = info_path if os.path.exists(info_path) else fallback_path if os.path.exists(fallback_path) else info_path
        
        info = {}
        if os.path.exists(read_path):
            try:
                with open(read_path, "r") as f:
                    info = decode_metadata(f.read())
            except Exception:
                pass
                
        # Double check if Creator field is locked in GUI but they tried to bypass it
        creator_before = info.get("creator", "")
        creator_input = self.ent_mod_creator.get().strip()
        
        # If creator was already set (not empty/User), do not allow modifying it
        if creator_before.strip().lower() not in ["", "user"] and creator_input != creator_before:
            creator_input = creator_before  # Keep original creator
            
        info["name"] = self.ent_mod_name.get().strip() or mod_id
        info["creator"] = creator_input
        info["version"] = self.ent_mod_version.get().strip() or "1.0"
        info["description"] = self.ent_mod_desc.get().strip()
        
        try:
            with open(info_path, "w") as f:
                f.write(encode_metadata(info))
                
            # Clean up old .json file if we migrated it to .ffxmod
            if os.path.exists(fallback_path) and info_path != fallback_path:
                try:
                    os.remove(fallback_path)
                except Exception:
                    pass
                
            # If enabled, also sync name to tracking ffxmod
            tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
            old_tracker_path = os.path.join(self.mods_dir, f"{mod_id}.json")
            read_tracker = tracker_path if os.path.exists(tracker_path) else old_tracker_path if os.path.exists(old_tracker_path) else tracker_path
            
            if os.path.exists(read_tracker):
                try:
                    with open(read_tracker, "r") as f:
                        track = decode_metadata(f.read())
                    track["name"] = info["name"]
                    with open(tracker_path, "w") as f:
                        f.write(encode_metadata(track))
                    # Clean up old tracker file if migrated
                    if tracker_path != old_tracker_path and os.path.exists(old_tracker_path):
                        os.remove(old_tracker_path)
                except Exception:
                    pass
                    
            self.log(f"Saved metadata for mod '{mod_id}' successfully.", "success")
            self.scan_mods()
            self.select_mod(mod_id)
        except Exception as e:
            self.log(f"Failed to save metadata: {e}", "error")

    def create_mod(self):
        name = simpledialog.askstring("Create Mod", "Enter Mod name:", parent=self.root)
        if not name:
            return
            
        clean_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip()
        if not clean_name:
            messagebox.showerror("Error", "Invalid name.")
            return
            
        mod_id = clean_name.replace(" ", "_")
        mod_repo_path = os.path.join(self.mods_disabled_dir, mod_id)
        if os.path.exists(mod_repo_path):
            messagebox.showerror("Error", f"Mod with ID '{mod_id}' already exists.")
            return
            
        try:
            os.makedirs(mod_repo_path, exist_ok=True)
            info = {
                "name": clean_name,
                "creator": "User",
                "version": "1.0",
                "description": "",
                "files": []
            }
            with open(os.path.join(mod_repo_path, "modinfo.ffxmod"), "w") as f:
                f.write(encode_metadata(info))
                
            self.log(f"Created new mod project '{clean_name}'.", "success")
            self.scan_mods()
            self.select_mod(mod_id)
        except Exception as e:
            self.log(f"Failed to create mod: {e}", "error")

    def delete_mod(self):
        mod_id = self.selected_mod_id
        if not mod_id:
            messagebox.showwarning("Warning", "No mod selected.")
            return
            
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete mod '{mod_id}' completely from your disk?\n\nThis will remove it from the repository and delete all its source files. This cannot be undone."):
            return
            
        # Disable first if enabled
        if self.get_mod_status(mod_id) == "Enabled":
            self.disable_mod_logic(mod_id)
            
        # Remove from mods_disabled repo
        mod_repo_path = os.path.join(self.mods_disabled_dir, mod_id)
        try:
            shutil.rmtree(mod_repo_path, ignore_errors=True)
            self.selected_mod_id = "" # Clear selection since mod is deleted
            self.log(f"Deleted mod '{mod_id}' successfully.", "success")
            self.scan_mods()
        except Exception as e:
            self.log(f"Failed to delete mod folder: {e}", "error")

    def enable_mod(self):
        mod_id = self.selected_mod_id
        if not mod_id:
            messagebox.showwarning("Warning", "Select a mod to enable.")
            return
            
        if self.get_mod_status(mod_id) == "Enabled":
            messagebox.showinfo("Status", "Mod is already enabled.")
            return
            
        self.log(f"Enabling mod '{mod_id}'...")
        mod_repo = os.path.join(self.mods_disabled_dir, mod_id)
        info_path = os.path.join(mod_repo, "modinfo.ffxmod")
        if not os.path.exists(info_path):
            info_path = os.path.join(mod_repo, "modinfo.json")
            
        if not os.path.exists(info_path):
            self.log("Error: Mod metadata file 'modinfo.ffxmod' is missing.", "error")
            return
            
        try:
            with open(info_path, "r") as f:
                info = decode_metadata(f.read())
        except Exception as e:
            self.log(f"Error reading modinfo: {e}", "error")
            return
            
        files = info.get("files", [])
        if not files:
            messagebox.showwarning("Warning", "Mod is empty. No files to move.")
            return
            
        success_count = 0
        total_size = 0
        
        for rel in files:
            src = os.path.join(mod_repo, rel)
            dest = os.path.join(self.mods_dir, rel)
            if os.path.exists(src):
                try:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    if os.path.lexists(dest):
                        try:
                            if os.path.isdir(dest) and not os.path.islink(dest):
                                shutil.rmtree(dest)
                            else:
                                os.remove(dest)
                        except Exception:
                            pass
                    shutil.move(src, dest)
                    success_count += 1
                    total_size += os.path.getsize(dest)
                except Exception as e:
                    self.log(f"Failed to move '{rel}' to active mods folder: {e}", "error")
            else:
                # If the file is already in dest (e.g. from an import), count it
                if os.path.exists(dest):
                    success_count += 1
                    total_size += os.path.getsize(dest)
                else:
                    self.log(f"Warning: File missing in repository: '{rel}'", "error")
                
        # Create active mods tracker file
        tracker = {
            "name": info.get("name", mod_id),
            "files": files,
            "size": total_size
        }
        try:
            tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
            with open(tracker_path, "w") as f:
                f.write(encode_metadata(tracker))
            # Clean up old .json tracker if it exists
            old_tracker = os.path.join(self.mods_dir, f"{mod_id}.json")
            if os.path.exists(old_tracker):
                try:
                    os.remove(old_tracker)
                except Exception:
                    pass
            self.log(f"Successfully enabled mod '{mod_id}' ({success_count} of {len(files)} files activated).", "success")
            self.scan_mods()
            self.select_mod(mod_id)
        except Exception as e:
            self.log(f"Failed to write tracking file: {e}", "error")

    def disable_mod(self):
        mod_id = self.selected_mod_id
        if not mod_id:
            messagebox.showwarning("Warning", "Select a mod to disable.")
            return
            
        if self.get_mod_status(mod_id) == "Disabled":
            messagebox.showinfo("Status", "Mod is already disabled.")
            return
            
        self.disable_mod_logic(mod_id)
        self.scan_mods()
        self.select_mod(mod_id)

    def disable_mod_logic(self, mod_id):
        self.log(f"Disabling mod '{mod_id}'...")
        tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
        old_tracker_path = os.path.join(self.mods_dir, f"{mod_id}.json")
        
        read_path = tracker_path if os.path.exists(tracker_path) else old_tracker_path
        if not os.path.exists(read_path):
            self.log("Error: Active tracking file missing. Cannot uninstall cleanly.", "error")
            return
            
        try:
            with open(read_path, "r") as f:
                track = decode_metadata(f.read())
        except Exception as e:
            self.log(f"Error reading tracking file: {e}", "error")
            return
            
        files = track.get("files", [])
        remove_count = 0
        mod_repo = os.path.join(self.mods_disabled_dir, mod_id)
        
        for rel in files:
            dest = os.path.join(self.mods_dir, rel)
            src_back = os.path.join(mod_repo, rel)
            if os.path.exists(dest):
                try:
                    os.makedirs(os.path.dirname(src_back), exist_ok=True)
                    if os.path.lexists(src_back):
                        try:
                            if os.path.isdir(src_back) and not os.path.islink(src_back):
                                shutil.rmtree(src_back)
                            else:
                                os.remove(src_back)
                        except Exception:
                            pass
                    shutil.move(dest, src_back)
                    remove_count += 1
                    # Clean up empty parent directories in mods folder
                    parent = os.path.dirname(dest)
                    while parent and parent != self.mods_dir:
                        if not os.listdir(parent):
                            os.rmdir(parent)
                            parent = os.path.dirname(parent)
                        else:
                            break
                except Exception as e:
                    self.log(f"Failed to move back '{rel}': {e}", "error")
                    
        # Remove tracking files
        try:
            if os.path.exists(tracker_path):
                os.remove(tracker_path)
            if os.path.exists(old_tracker_path):
                os.remove(old_tracker_path)
            self.log(f"Successfully disabled mod '{mod_id}' (deactivated {remove_count} files).", "success")
        except Exception as e:
            self.log(f"Failed to delete tracking file: {e}", "error")

    def resolve_mod_relative_path(self, abs_path):
        abs_path = abs_path.replace("\\", "/")
        parts = abs_path.split("/")
        
        # 1. If absolute path contains the root folders ffx_ps2 or ffx_data explicitly
        if "ffx_ps2/" in abs_path.lower():
            idx = abs_path.lower().find("ffx_ps2/")
            return abs_path[idx:]
        if "ffx_data/" in abs_path.lower():
            idx = abs_path.lower().find("ffx_data/")
            return abs_path[idx:]
            
        # 2. If it contains subfolders ffx/master or gamedata
        if "ffx/master" in abs_path.lower():
            idx = abs_path.lower().find("ffx/master")
            return "ffx_ps2/" + abs_path[idx:]
        if "gamedata" in abs_path.lower():
            idx = abs_path.lower().find("gamedata")
            return "ffx_data/" + abs_path[idx:]
            
        # 3. If it contains localized folders like jppc, new_uspc, uspc
        for loc in ["jppc", "new_uspc", "uspc"]:
            if loc in parts:
                idx = parts.index(loc)
                ext = os.path.splitext(abs_path)[1].lower()
                if ext in [".bin", ".dat", ".evt"]:
                    return "ffx_ps2/ffx/master/" + "/".join(parts[idx:])
                else:
                    return "ffx_data/gamedata/" + "/".join(parts[idx:])
                    
        return ""

    def import_files(self):
        mod_id = self.selected_mod_id
        if not mod_id:
            messagebox.showwarning("Warning", "Select a mod project first.")
            return
            
        mod_repo = os.path.join(self.mods_disabled_dir, mod_id)
        info_path = os.path.join(mod_repo, "modinfo.ffxmod")
        fallback_path = os.path.join(mod_repo, "modinfo.json")
        read_path = info_path if os.path.exists(info_path) else fallback_path if os.path.exists(fallback_path) else info_path
        
        if not os.path.exists(read_path):
            messagebox.showerror("Error", "Mod metadata file missing.")
            return
            
        files = filedialog.askopenfilenames(title="Select File(s) to Import")
        if not files:
            return
            
        try:
            with open(read_path, "r") as f:
                info = decode_metadata(f.read())
        except Exception:
            info = {}
            
        files_list = info.get("files", [])
        import_count = 0
        
        # Try to resolve master path for help
        master_path = ""
        # Look for FFX Tools extracted master path fallback
        potential_master = os.path.abspath(os.path.join(os.getcwd(), "..", "VBF Browser", "extracted", "ffx_ps2", "ffx", "master"))
        if os.path.exists(potential_master):
            master_path = potential_master
            
        for fpath in files:
            # Resolve relative destination path
            rel = self.resolve_mod_relative_path(fpath)
            if not rel and master_path:
                # Attempt resolution by checking if path contains master
                rel = self.resolve_mod_relative_path(os.path.join(master_path, os.path.basename(fpath)))
            
            if not rel:
                # Ask user for manual relative path
                rel = simpledialog.askstring(
                    "Relative Game Path",
                    f"Could not automatically resolve game path for:\n{os.path.basename(fpath)}\n\nEnter relative path (e.g. ffx_data/gamedata/abc.bin):",
                    parent=self.root
                )
                if not rel:
                    continue
            
            rel = rel.replace("\\", "/").strip().lstrip("/")
            
            # Destination path inside mod repo
            dest = os.path.join(mod_repo, rel)
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(fpath, dest)
                if rel not in files_list:
                    files_list.append(rel)
                import_count += 1
            except Exception as e:
                self.log(f"Failed to copy '{os.path.basename(fpath)}': {e}", "error")
                
        if import_count > 0:
            info["files"] = files_list
            try:
                with open(read_path, "w") as f:
                    f.write(encode_metadata(info))
                    
                # If currently enabled, also sync files to mods folder and tracker
                if self.get_mod_status(mod_id) == "Enabled":
                    total_size = 0
                    for rel in files_list:
                        src = os.path.join(mod_repo, rel)
                        dest = os.path.join(self.mods_dir, rel)
                        if os.path.exists(src):
                            try:
                                os.makedirs(os.path.dirname(dest), exist_ok=True)
                                shutil.copy2(src, dest)
                                total_size += os.path.getsize(dest)
                            except Exception:
                                pass
                                
                    tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
                    old_tracker = os.path.join(self.mods_dir, f"{mod_id}.json")
                    with open(tracker_path, "w") as f:
                        f.write(encode_metadata({
                            "name": info.get("name", mod_id),
                            "files": files_list,
                            "size": total_size
                        }))
                    if os.path.exists(old_tracker):
                        try:
                            os.remove(old_tracker)
                        except Exception:
                            pass
            except Exception:
                pass
                
            self.scan_mods()
            self.select_mod(mod_id)

    def import_folder(self):
        mod_id = self.selected_mod_id
        if not mod_id:
            messagebox.showwarning("Warning", "Select a mod project first.")
            return
            
        mod_repo = os.path.join(self.mods_disabled_dir, mod_id)
        info_path = os.path.join(mod_repo, "modinfo.ffxmod")
        fallback_path = os.path.join(mod_repo, "modinfo.json")
        read_path = info_path if os.path.exists(info_path) else fallback_path if os.path.exists(fallback_path) else info_path
        
        if not os.path.exists(read_path):
            messagebox.showerror("Error", "Mod metadata file missing.")
            return
            
        selected_dir = filedialog.askdirectory(title="Select Folder to Import")
        if not selected_dir:
            return
            
        try:
            with open(read_path, "r") as f:
                info = decode_metadata(f.read())
        except Exception:
            info = {}
            
        files_list = info.get("files", [])
        import_count = 0
        
        # Recursively find all files in the folder
        all_files = []
        for root, dirs, filenames in os.walk(selected_dir):
            for filename in filenames:
                all_files.append(os.path.join(root, filename))
                
        if not all_files:
            messagebox.showwarning("Warning", "The selected folder is empty.")
            return
            
        ans = messagebox.askyesno(
            "Confirm Folder Import",
            f"Found {len(all_files)} files in the selected folder.\n\n"
            "Do you want to import all of them?"
        )
        if not ans:
            return
            
        self.log(f"Importing folder contents for mod '{mod_id}'...")
        
        # Try to resolve master path for help
        master_path = ""
        potential_master = os.path.abspath(os.path.join(os.getcwd(), "..", "VBF Browser", "extracted", "ffx_ps2", "ffx", "master"))
        if os.path.exists(potential_master):
            master_path = potential_master
            
        for fpath in all_files:
            # Resolve relative destination path
            rel = self.resolve_mod_relative_path(fpath)
            if not rel and master_path:
                rel = self.resolve_mod_relative_path(os.path.join(master_path, os.path.basename(fpath)))
                
            if not rel:
                # Ask user for manual relative path
                rel = simpledialog.askstring(
                    "Relative Game Path",
                    f"Could not automatically resolve game path for:\n{os.path.basename(fpath)}\n\nEnter relative path (e.g. ffx_data/gamedata/abc.bin):",
                    parent=self.root
                )
                if not rel:
                    continue
                    
            rel = rel.replace("\\", "/").strip().lstrip("/")
            
            # Destination path inside mod repo
            dest = os.path.join(mod_repo, rel)
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(fpath, dest)
                if rel not in files_list:
                    files_list.append(rel)
                import_count += 1
            except Exception as e:
                self.log(f"Failed to copy '{os.path.basename(fpath)}': {e}", "error")
                
        if import_count > 0:
            info["files"] = files_list
            try:
                with open(read_path, "w") as f:
                    f.write(encode_metadata(info))
                    
                # If currently enabled, also sync files to mods folder and tracker
                if self.get_mod_status(mod_id) == "Enabled":
                    total_size = 0
                    for rel in files_list:
                        src = os.path.join(mod_repo, rel)
                        dest = os.path.join(self.mods_dir, rel)
                        if os.path.exists(src):
                            try:
                                os.makedirs(os.path.dirname(dest), exist_ok=True)
                                shutil.copy2(src, dest)
                                total_size += os.path.getsize(dest)
                            except Exception:
                                pass
                                
                    tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
                    old_tracker = os.path.join(self.mods_dir, f"{mod_id}.json")
                    with open(tracker_path, "w") as f:
                        f.write(encode_metadata({
                            "name": info.get("name", mod_id),
                            "files": files_list,
                            "size": total_size
                        }))
                    if os.path.exists(old_tracker):
                        try:
                            os.remove(old_tracker)
                        except Exception:
                            pass
            except Exception:
                pass
                
            self.log(f"Successfully imported {import_count} files from folder!", "success")
            self.scan_mods()
            self.select_mod(mod_id)

    def open_folder(self):
        mod_id = self.selected_mod_id
        if not mod_id:
            messagebox.showwarning("Warning", "Select a mod folder to open.")
            return
            
        status = self.get_mod_status(mod_id)
        if status == "Enabled":
            folder_path = os.path.join(self.mods_disabled_dir, mod_id)
        else:
            folder_path = os.path.join(self.mods_disabled_dir, mod_id)
            
        if os.path.exists(folder_path):
            try:
                if sys.platform == "win32":
                    os.startfile(folder_path)
                else:
                    subprocess.Popen(["xdg-open", folder_path])
            except Exception as e:
                self.log(f"Could not open folder: {e}", "error")
        else:
            messagebox.showerror("Error", "Mod folder does not exist on disk.")

    def get_friendly_size(self, size_in_bytes):
        if size_in_bytes < 1024:
            return f"{size_in_bytes} B"
        elif size_in_bytes < 1024 * 1024:
            return f"{size_in_bytes / 1024:.2f} KB"
        else:
            return f"{size_in_bytes / (1024 * 1024):.2f} MB"

    def get_button_colors(self, btn):
        is_primary = getattr(btn, "_is_primary", False)
        is_success = getattr(btn, "_is_success", False)
        is_danger = getattr(btn, "_is_danger", False)
        is_sidebar = getattr(btn, "_is_sidebar", False)
        
        if is_sidebar:
            page_id = getattr(btn, "_page_id", "")
            if self.current_page == page_id:
                normal_bg = self.accent_color
                hover_bg = self.accent_color
            else:
                normal_bg = self.card_color
                hover_bg = self.border_color
        elif is_primary:
            normal_bg = self.accent_color
            hover_bg = self.accent_hover
        elif is_success:
            normal_bg = self.success_color
            hover_bg = "#059669"
        elif is_danger:
            normal_bg = self.error_color
            hover_bg = "#dc2626"
        else:
            normal_bg = self.card_color
            hover_bg = self.border_color
            
        return normal_bg, hover_bg

    def bind_hover(self, btn, is_primary=False):
        if is_primary:
            btn._is_primary = True
        btn.bind("<Enter>", lambda e: btn.config(bg=self.get_button_colors(btn)[1]))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.get_button_colors(btn)[0]))

    def bind_hover_color(self, btn, hover, normal):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal))

    def launch_game(self):
        if not self.game_dir:
            messagebox.showwarning("Warning", "Please configure your FFX Game Folder first.")
            return
            
        self.log("Launching Final Fantasy X via Steam...", "info")
        try:
            import webbrowser
            webbrowser.open("steam://run/359870")
            
            # Start background monitoring for game process & plugin trackers
            self.root.after(2000, self.start_game_monitoring)
        except Exception as e:
            self.log(f"Failed to launch game: {e}", "error")

    def start_game_monitoring(self):
        import threading
        t = threading.Thread(target=self.monitor_game_process, daemon=True)
        t.start()

    def monitor_game_process(self):
        import time
        self.log("Waiting for game process (FFX.exe) to start...", "info")
        
        pid = None
        # Loop checking for FFX.exe up to 60 seconds
        for _ in range(60):
            pid = self.find_process_id("FFX.exe")
            if pid:
                break
            time.sleep(1)
            
        if not pid:
            self.log("Game launch monitoring timed out.", "warning")
            return
            
        self.log(f"Game process FFX.exe detected running (PID: {pid})!", "success")
        
        # Fire plugin launch hooks
        self.on_game_launched(pid)
        
        # Monitor until it closes
        while True:
            if not self.is_process_running(pid):
                break
            time.sleep(2)
            
        self.log("Game process closed.", "info")
        self.on_game_closed()

    def find_process_id(self, process_name):
        if not kernel32:
            return None
            
        import ctypes
        import ctypes.wintypes
        
        TH32CS_SNAPPROCESS = 0x00000002
        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.c_ulong),
                ("cntUsage", ctypes.c_ulong),
                ("th32ProcessID", ctypes.c_ulong),
                ("th32DefaultHeapID", ctypes.c_void_p),
                ("th32ModuleID", ctypes.c_ulong),
                ("cntThreads", ctypes.c_ulong),
                ("th32ParentProcessID", ctypes.c_ulong),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", ctypes.c_ulong),
                ("szExeFile", ctypes.c_char * 260)
            ]
            
        hProcessSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if hProcessSnap == -1:
            return None
            
        pe32 = PROCESSENTRY32()
        pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
        
        if not kernel32.Process32First(hProcessSnap, ctypes.byref(pe32)):
            kernel32.CloseHandle(hProcessSnap)
            return None
            
        pid = None
        while True:
            exe_name = pe32.szExeFile.decode('utf-8', errors='ignore')
            if exe_name.lower() == process_name.lower():
                pid = pe32.th32ProcessID
                break
            if not kernel32.Process32Next(hProcessSnap, ctypes.byref(pe32)):
                break
                
        kernel32.CloseHandle(hProcessSnap)
        return pid

    def is_process_running(self, pid):
        if not kernel32:
            return False
            
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        
        hProcess = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not hProcess:
            return False
            
        exit_code = ctypes.c_ulong()
        running = False
        if kernel32.GetExitCodeProcess(hProcess, ctypes.byref(exit_code)):
            running = (exit_code.value == STILL_ACTIVE)
            
        kernel32.CloseHandle(hProcess)
        return running

    def on_game_launched(self, pid):
        for plugin in self.plugins:
            if hasattr(plugin, "on_game_launch"):
                try:
                    plugin.on_game_launch(pid)
                except Exception as e:
                    self.log(f"Error in plugin launch callback: {e}", "error")
            
            tracker_script = plugin._metadata.get("tracker_script")
            if tracker_script:
                plugin_dir = plugin._metadata.get("_dir")
                base_name, _ = os.path.splitext(tracker_script)
                exe_name = base_name + ".exe"
                exe_path = os.path.join(plugin_dir, exe_name)
                script_path = os.path.join(plugin_dir, tracker_script)
                
                if os.path.exists(exe_path):
                    self.log(f"Starting background tracker executable for {plugin._metadata['name']}...", "info")
                    try:
                        p = subprocess.Popen(
                            [exe_path, str(pid), self.game_dir],
                            cwd=plugin_dir,
                            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                        )
                        plugin._tracker_process = p
                    except Exception as e:
                        self.log(f"Failed to start tracker executable: {e}", "error")
                elif os.path.exists(script_path):
                    self.log(f"Starting background tracker script for {plugin._metadata['name']}...", "info")
                    try:
                        python_exe = sys.executable if not getattr(sys, 'frozen', False) else "pythonw"
                        p = subprocess.Popen(
                            [python_exe, script_path, str(pid), self.game_dir],
                            cwd=plugin_dir,
                            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                        )
                        plugin._tracker_process = p
                    except Exception as e:
                        try:
                            p = subprocess.Popen(
                                ["python", script_path, str(pid), self.game_dir],
                                cwd=plugin_dir,
                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                            )
                            plugin._tracker_process = p
                        except Exception as e2:
                            self.log(f"Failed to start tracker script with system Python: {e2}", "error")
                
                if getattr(plugin, "_tracker_process", None):
                    self.log(f"💡 Tip: Press F8 in-game to toggle the {plugin._metadata['name']} overlay HUD!", "info")

    def on_game_closed(self):
        for plugin in self.plugins:
            if hasattr(plugin, "on_game_close"):
                try:
                    plugin.on_game_close()
                except Exception as e:
                    self.log(f"Error in plugin close callback: {e}", "error")
            
            p = getattr(plugin, "_tracker_process", None)
            if p:
                try:
                    p.terminate()
                    p.wait(timeout=2)
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass
                plugin._tracker_process = None

    def load_plugins(self):
        self.plugins = []
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        plugins_dir = os.path.join(base_dir, "plugins")
        if not os.path.exists(plugins_dir):
            try:
                os.makedirs(plugins_dir, exist_ok=True)
            except Exception:
                pass
            return
            
        import importlib.util
        
        try:
            for d in os.listdir(plugins_dir):
                dpath = os.path.join(plugins_dir, d)
                if os.path.isdir(dpath):
                    manifest_path = os.path.join(dpath, "plugin.json")
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                meta = json.load(f)
                            
                            name = meta.get("name")
                            entry_point = meta.get("entry_point")
                            if not name or not entry_point:
                                continue
                                
                            parts = entry_point.split(".")
                            if len(parts) != 2:
                                self.log(f"Invalid entry point in {d}: {entry_point}", "error")
                                continue
                                
                            module_file = parts[0] + ".py"
                            class_name = parts[1]
                            
                            module_path = os.path.join(dpath, module_file)
                            if not os.path.exists(module_path):
                                self.log(f"Module file missing: {module_path}", "error")
                                continue
                                
                            # Dynamically import the module
                            spec = importlib.util.spec_from_file_location(f"plugin_{d}", module_path)
                            module = importlib.util.module_from_spec(spec)
                            sys.path.insert(0, dpath)
                            spec.loader.exec_module(module)
                            sys.path.pop(0)
                            
                            plugin_class = getattr(module, class_name, None)
                            if not plugin_class:
                                self.log(f"Class '{class_name}' not found in module '{module_file}'", "error")
                                continue
                                
                            tab_frame = ttk.Frame(self.content_container)
                            plugin_inst = plugin_class(tab_frame, self)
                            meta["_dir"] = dpath
                            plugin_inst._metadata = meta
                            plugin_inst._tracker_process = None
                            
                            page_id = f"plugin_{d}"
                            self.pages[page_id] = {
                                "name": name,
                                "frame": tab_frame,
                                "instance": plugin_inst,
                                "icon": meta.get("icon", "🔌")
                            }
                            
                            self.add_sidebar_nav_button(page_id, name, meta.get("icon", "🔌"))
                            self.plugins.append(plugin_inst)
                            self.log(f"Successfully loaded plugin: {name} (v{meta.get('version', '1.0')})", "success")
                            
                        except Exception as e:
                            self.log(f"Failed to load plugin from '{d}': {e}", "error")
        except Exception as e:
            self.log(f"Error scanning plugins: {e}", "error")

if __name__ == "__main__":
    root = tk.Tk()
    app = FFXModManagerGUI(root)
    root.mainloop()
