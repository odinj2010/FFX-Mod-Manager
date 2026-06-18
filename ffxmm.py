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



CONFIG_FILE = "ffxmm_config.json"
APP_VERSION = "2.3.0"

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
        self.mod_search_var = tk.StringVar()
        self.mod_category_var = tk.StringVar(value="All Categories")
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
        self.update_profile_dropdown()
        
        # Auto-import loose files check
        self.root.after(500, self.auto_import_loose_files)
        
        # Check for Updates asynchronously in the background
        self.root.after(1000, self.check_for_updates)

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
            
        self.is_fahrenheit_mode = False
        if self.game_dir:
            # Check for Fahrenheit FIRST to decide folder structure
            fh_launcher = os.path.join(self.game_dir, "fahrenheit", "bin", "fhstage0.exe")
            if os.path.exists(fh_launcher):
                self.is_fahrenheit_mode = True
                # In Fahrenheit, everything lives inside the fahrenheit/ folder
                self.mods_dir = os.path.join(self.game_dir, "fahrenheit", "mods")
                self.mods_disabled_dir = os.path.join(self.game_dir, "fahrenheit", "mods_disabled")
            else:
                self.mods_dir = os.path.join(self.game_dir, "data", "mods")
                self.mods_disabled_dir = os.path.join(self.game_dir, "data", "mods_disabled")
            
            # Create directories only for what is actually needed
            try:
                os.makedirs(self.mods_disabled_dir, exist_ok=True)
                os.makedirs(self.mods_dir, exist_ok=True)
            except Exception:
                pass
        else:
            self.mods_dir = ""
            self.mods_disabled_dir = ""

    def check_loader_status(self):
        if not self.game_dir:
            return "Unknown (Configure Game Folder)", self.error_color
            
        # Check for Fahrenheit
        fh_launcher = os.path.join(self.game_dir, "fahrenheit", "bin", "fhstage0.exe")
        if os.path.exists(fh_launcher):
            self.is_fahrenheit_mode = True
            return "🟢 Active Mod Loader Detected (Fahrenheit Framework)", self.success_color
            
        self.is_fahrenheit_mode = False
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
        
        # Update Banner Frame (Hidden by default)
        self.update_banner_frame = tk.Frame(self.content_container, bg=self.bg_color)
        self.update_banner_frame.pack(fill="x", side="top", expand=False)
        
        # Standard Pages Frames
        self.page_mods_frame = tk.Frame(self.content_container, bg=self.bg_color)
        self.page_settings_frame = tk.Frame(self.content_container, bg=self.bg_color)
        self.page_plugins_browser_frame = tk.Frame(self.content_container, bg=self.bg_color)
        
        # Register standard pages
        self.pages["mods"] = {
            "name": "Mods",
            "frame": self.page_mods_frame,
            "icon": "📁"
        }
        self.pages["plugins_browser"] = {
            "name": "Plugin Browser",
            "frame": self.page_plugins_browser_frame,
            "icon": "🔌"
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
        
        # Search Bar
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        
        lbl_search = tk.Label(search_frame, text="🔍", font=("Segoe UI", 10), bg=self.bg_color, fg=self.text_dim)
        lbl_search.pack(side="left", padx=(0, 5))
        
        self.ent_search = ttk.Entry(search_frame, textvariable=self.mod_search_var)
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.cmb_category = ttk.Combobox(search_frame, textvariable=self.mod_category_var, state="readonly", width=12)
        self.cmb_category["values"] = ["All Categories"]
        self.cmb_category.pack(side="left")
        self.cmb_category.bind("<<ComboboxSelected>>", lambda e: self.refresh_list())
        
        self.mod_search_var.trace_add("write", lambda *args: self.refresh_list())

        # Profile management row
        profile_row = ttk.Frame(left_frame)
        profile_row.pack(fill="x", pady=(0, 10))
        
        lbl_prof = ttk.Label(profile_row, text="Profile:")
        lbl_prof.pack(side="left", padx=(0, 5))
        
        self.profile_combobox = ttk.Combobox(profile_row, values=["Default"], state="readonly", width=15)
        self.profile_combobox.set("Default")
        self.profile_combobox.pack(side="left", padx=(0, 5))
        
        btn_apply_prof = tk.Button(profile_row, text="✔️ Apply", command=self.apply_profile, bg=self.card_color,
                                   fg=self.text_color, font=("Segoe UI", 8, "bold"), relief="flat", activebackground=self.border_color, bd=0, padx=6, pady=2)
        btn_apply_prof.pack(side="left", padx=(0, 2))
        self.bind_hover(btn_apply_prof)
        
        btn_save_prof = tk.Button(profile_row, text="💾 Save", command=self.save_profile, bg=self.card_color,
                                  fg=self.text_color, font=("Segoe UI", 8, "bold"), relief="flat", activebackground=self.border_color, bd=0, padx=6, pady=2)
        btn_save_prof.pack(side="left", padx=(0, 2))
        self.bind_hover(btn_save_prof)
        
        btn_del_prof = tk.Button(profile_row, text="🗑️", command=self.delete_profile, bg=self.card_color,
                                 fg=self.error_color, font=("Segoe UI", 8, "bold"), relief="flat", activebackground=self.border_color, bd=0, padx=6, pady=2)
        btn_del_prof.pack(side="left")
        self.bind_hover(btn_del_prof)
        
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
        btn_p_frame = ttk.Frame(left_frame, padding=(0, 8, 0, 0))
        btn_p_frame.pack(fill="x")
        
        btn_enable = tk.Button(btn_p_frame, text="⚡ Enable Mod (Install)", command=self.enable_mod, bg=self.success_color,
                               fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#059669", height=2)
        btn_enable._is_success = True
        btn_enable.pack(fill="x", pady=3)
        self.bind_hover(btn_enable)
        
        btn_disable = tk.Button(btn_p_frame, text="⏪ Disable Mod (Uninstall)", command=self.disable_mod, bg=self.card_color,
                                fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color, height=2)
        btn_disable.pack(fill="x", pady=3)
        self.bind_hover(btn_disable)
        
        btn_new = tk.Button(btn_p_frame, text="Create New Mod", command=self.create_mod, bg=self.accent_color,
                            fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover)
        btn_new._is_primary = True
        btn_new.pack(fill="x", pady=2)
        self.bind_hover(btn_new, is_primary=True)
        
        btn_import = tk.Button(btn_p_frame, text="📥 Import Mod Archive (.zip / .rar)", command=self.import_zip_mod, bg=self.accent_color,
                               fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover)
        btn_import._is_primary = True
        btn_import.pack(fill="x", pady=2)
        self.bind_hover(btn_import, is_primary=True)
        
        btn_del = tk.Button(btn_p_frame, text="Delete Mod From Disk", command=self.delete_mod, bg=self.error_color,
                            fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#dc2626")
        btn_del._is_danger = True
        btn_del.pack(fill="x", pady=2)
        self.bind_hover(btn_del)
        
        # Load Order control frame (only packed when in Fahrenheit mode)
        self.load_order_frame = ttk.Frame(btn_p_frame)
        
        btn_move_up = tk.Button(self.load_order_frame, text="🔼 Move Up", command=self.move_mod_up, bg=self.card_color,
                                fg=self.text_color, font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color)
        btn_move_up.pack(side="left", fill="x", expand=True, padx=(0, 2), pady=2)
        self.bind_hover(btn_move_up)
        
        btn_move_down = tk.Button(self.load_order_frame, text="🔽 Move Down", command=self.move_mod_down, bg=self.card_color,
                                  fg=self.text_color, font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color)
        btn_move_down.pack(side="right", fill="x", expand=True, padx=(2, 0), pady=2)
        self.bind_hover(btn_move_down)
        
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
        
        # Notebook for Mod Details
        self.mod_details_notebook = ttk.Notebook(right_frame)
        self.mod_details_notebook.pack(fill="both", expand=True)
        
        # Tab 1: Information
        self.tab_info = ttk.Frame(self.mod_details_notebook, padding=10)
        self.mod_details_notebook.add(self.tab_info, text=" Information ")
        
        # Metadata Card (now inside tab_info)
        meta_frame = ttk.LabelFrame(self.tab_info, text=" Mod Metadata ", padding=10)
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
        
        ttk.Label(meta_frame, text="Category:").grid(row=4, column=0, sticky="w", pady=2)
        self.cmb_mod_category = ttk.Combobox(meta_frame, values=["General", "Texture", "Script", "Audio", "UI", "Gameplay", "Retranslation"], width=28)
        self.cmb_mod_category.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(meta_frame, text="Nexus Mod ID:").grid(row=5, column=0, sticky="w", pady=2)
        self.ent_nexus_id = ttk.Entry(meta_frame, width=15)
        self.ent_nexus_id.grid(row=5, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(meta_frame, text="Mod Link:").grid(row=6, column=0, sticky="w", pady=2)
        link_row = ttk.Frame(meta_frame)
        link_row.grid(row=6, column=1, sticky="w", padx=5, pady=2)
        
        self.ent_mod_link = ttk.Entry(link_row, width=22)
        self.ent_mod_link.pack(side="left", padx=(0, 5))
        
        btn_visit = tk.Button(link_row, text="🌐 Visit", command=self.visit_mod_link, bg=self.bg_color,
                               fg=self.text_color, relief="flat", activebackground=self.border_color, padx=5)
        btn_visit.pack(side="left")
        self.bind_hover(btn_visit)
        
        btn_save_meta = tk.Button(meta_frame, text="Save Details", command=self.save_mod_metadata, bg=self.card_color,
                                  fg=self.text_color, relief="flat", activebackground=self.border_color)
        btn_save_meta.grid(row=7, column=1, sticky="w", padx=5, pady=5)
        self.bind_hover(btn_save_meta)
        
        # Tab 2: Files
        self.tab_files = ttk.Frame(self.mod_details_notebook, padding=10)
        self.mod_details_notebook.add(self.tab_files, text=" Files ")
        
        files_frame = ttk.Frame(self.tab_files)
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
        
        # File Operations (inside tab_files)
        file_ops = ttk.Frame(self.tab_files, padding=(0, 5, 0, 0))
        file_ops.pack(fill="x")
        
        btn_import_f = tk.Button(file_ops, text="Import File(s)...", command=self.import_files, bg=self.accent_color,
                               fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover)
        btn_import_f._is_primary = True
        btn_import_f.pack(side="left", padx=(0, 5))
        self.bind_hover(btn_import_f, is_primary=True)
        
        btn_import_d = tk.Button(file_ops, text="Import Folder...", command=self.import_folder, bg=self.accent_color,
                                   fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover)
        btn_import_d._is_primary = True
        btn_import_d.pack(side="left", padx=5)
        self.bind_hover(btn_import_d, is_primary=True)
        
        btn_open_f = tk.Button(file_ops, text="Open Folder Location", command=self.open_folder, bg=self.card_color,
                             fg=self.text_color, relief="flat", activebackground=self.border_color)
        btn_open_f.pack(side="left", padx=5)
        self.bind_hover(btn_open_f)
        
        # Tab 3: Conflicts
        self.tab_conflicts = ttk.Frame(self.mod_details_notebook, padding=10)
        self.mod_details_notebook.add(self.tab_conflicts, text=" Conflicts ")
        
        self.lbl_conflict_summary = tk.Label(self.tab_conflicts, text="No conflicts detected.", font=("Segoe UI", 10), fg=self.success_color, bg=self.bg_color, wraplength=400, justify="left")
        self.lbl_conflict_summary.pack(anchor="w", pady=(0, 10))
        
        self.tree_conflicts = ttk.Treeview(self.tab_conflicts, columns=("mod", "file"), show="headings")
        self.tree_conflicts.heading("mod", text="Conflicting Mod")
        self.tree_conflicts.heading("file", text="Conflicting File")
        self.tree_conflicts.column("mod", width=120)
        self.tree_conflicts.column("file", width=200)
        self.tree_conflicts.pack(fill="both", expand=True)
        
        scroll_c = ttk.Scrollbar(self.tab_conflicts, command=self.tree_conflicts.yview)
        scroll_c.pack(fill="y", side="right")
        self.tree_conflicts.config(yscrollcommand=scroll_c.set)
        
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
        
        # Safe Mode & Diagnostics Card (Card Style)
        safe_card = tk.Frame(self.page_settings_frame, bg=self.card_color, highlightthickness=1, highlightbackground=self.border_color, padx=15, pady=15)
        safe_card._is_card = True
        safe_card.pack(fill="x", pady=10)
        
        lbl_safe_title = tk.Label(safe_card, text="Safety & Diagnostics Controls", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_color)
        lbl_safe_title._is_title = True
        lbl_safe_title.pack(anchor="w", pady=(0, 10))
        
        safe_row = tk.Frame(safe_card, bg=self.card_color)
        safe_row.pack(fill="x")
        
        btn_safe_reset = tk.Button(safe_row, text="⚠️ Disable All Active Mods (Safe Reset)", command=self.safe_mode_reset, bg=self.error_color,
                                   fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#dc2626", padx=12, pady=4)
        btn_safe_reset._is_danger = True
        btn_safe_reset.pack(side="left", padx=(0, 15))
        self.bind_hover(btn_safe_reset)
        
        btn_verify_disk = tk.Button(safe_row, text="💾 Verify Disk & Permissions", command=self.verify_deployment_safety, bg=self.bg_color,
                                    fg=self.text_color, relief="flat", activebackground=self.border_color, padx=12, pady=4)
        btn_verify_disk.pack(side="left")
        self.bind_hover(btn_verify_disk)

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
        
        btn_create_theme = tk.Button(theme_row, text="🎨 Create Custom Theme", command=self.open_theme_creator, bg=self.bg_color,
                                     fg=self.text_color, relief="flat", activebackground=self.border_color, padx=12, pady=4)
        btn_create_theme.pack(side="left")
        self.bind_hover(btn_create_theme)
        
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
        
        # Build Plugins Browser page UI
        self.create_plugins_browser_page()

        # Add bottom-aligned navigation buttons
        self.add_sidebar_nav_button("plugins_browser", "Plugin Browser", "🔌", side="bottom")
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

    def open_theme_creator(self):
        ThemeCreatorDialog(self)



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
        self.update_loader_status_ui()
        if getattr(self, "is_fahrenheit_mode", False):
            self.load_order_frame.pack(fill="x", pady=2)
        else:
            self.load_order_frame.pack_forget()
            
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
            
        # Notify plugins of mod list refresh
        if hasattr(self, "plugins"):
            for plugin in self.plugins:
                if hasattr(plugin, "on_mods_refreshed"):
                    try:
                        plugin.on_mods_refreshed()
                    except Exception as e:
                        self.log(f"Error in plugin mods refreshed callback: {e}", "error")
                        
        self.log("Mod list refreshed.", "info")

    def scan_mods(self):
        for widget in self.mod_cards_container.winfo_children():
            widget.destroy()
            
        if not self.mods_disabled_dir:
            return
            
        mods = {}
        
        # Detect if we are in Fahrenheit mode
        self.is_fahrenheit_mode = False
        if self.game_dir:
            fh_launcher = os.path.join(self.game_dir, "fahrenheit", "bin", "fhstage0.exe")
            if os.path.exists(fh_launcher):
                self.is_fahrenheit_mode = True
                
        # 1. Scan enabled mods
        if self.is_fahrenheit_mode:
            loadorder_path = os.path.join(self.game_dir, "fahrenheit", "mods", "loadorder")
            active_ids = []
            if os.path.exists(loadorder_path):
                try:
                    with open(loadorder_path, "r", encoding="utf-8") as f:
                        active_ids = [line.strip() for line in f if line.strip()]
                except Exception:
                    pass
            
            for mod_id in active_ids:
                modinfo_path = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id, "modinfo.ffxmod")
                if os.path.exists(modinfo_path):
                    try:
                        with open(modinfo_path, "r") as f:
                            data = decode_metadata(f.read())
                            mods[mod_id] = {
                                "name": data.get("name", mod_id),
                                "creator": data.get("author", data.get("creator", "Unknown")),
                                "category": data.get("category", "General"),
                                "status": "Enabled",
                                "files": data.get("files", []),
                                "size": data.get("size", 0)
                            }
                    except Exception:
                        pass
                else:
                    # Fallback if manifest exists but modinfo.ffxmod doesn't
                    manifest_path = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id, f"{mod_id}.manifest.json")
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            mods[mod_id] = {
                                "name": data.get("Name", mod_id),
                                "creator": data.get("Authors", "Unknown"),
                                "category": data.get("Category", "General"),
                                "status": "Enabled",
                                "files": [],
                                "size": 0
                            }
                        except Exception:
                            pass
        else:
            if self.mods_dir:
                try:
                    for file in os.listdir(self.mods_dir):
                        if file.endswith((".ffxmod", ".json")) and not file.startswith("modinfo"):
                            mod_id, _ = os.path.splitext(file)
                            try:
                                with open(os.path.join(self.mods_dir, file), "r") as f:
                                    data = decode_metadata(f.read())
                                    mods[mod_id] = {
                                        "name": data.get("name", mod_id),
                                        "creator": data.get("author", data.get("creator", "Unknown")),
                                        "category": data.get("category", "General"),
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
                if os.path.isdir(dpath) and not d.startswith("_"):
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
                                    "creator": data.get("author", data.get("creator", "Unknown")),
                                    "category": data.get("category", "General"),
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
                                "creator": "Unknown",
                                "category": "General",
                                "status": "Disabled",
                                "files": [],
                                "size": 0
                            }
        except Exception:
            pass
            
        # Update self.mod_list with UNFILTERED mods
        self.mod_list = list(mods.keys())
            
        # 3. Dynamic Category Population
        all_categories = set()
        for info in mods.values():
            cat = info.get("category", "General").strip()
            if cat:
                all_categories.add(cat)
        
        # Standard categories to ensure we always have some defaults in the editor
        base_categories = {"General", "Texture", "Script", "Audio", "UI", "Gameplay", "Retranslation"}
        cat_list = ["All Categories"] + sorted(list(all_categories))
        
        if hasattr(self, "cmb_category"):
            self.cmb_category["values"] = cat_list
            
        if hasattr(self, "cmb_mod_category"):
            # The editor should have the base categories plus any custom ones found
            editor_cats = sorted(list(base_categories.union(all_categories)))
            self.cmb_mod_category["values"] = editor_cats
            
        # 4. Apply Filtering
        query = self.mod_search_var.get().strip().lower()
        cat_filter = self.mod_category_var.get().strip()
        
        if cat_filter and cat_filter != "All Categories":
            mods = {m_id: info for m_id, info in mods.items() if info.get("category", "General").strip() == cat_filter}
            
        if query:
            filtered_mods = {}
            for m_id, info in mods.items():
                if (query in m_id.lower() or 
                    query in info.get("name", "").lower() or 
                    query in info.get("creator", "").lower() or 
                    query in info.get("category", "").lower()):
                    filtered_mods[m_id] = info
            mods = filtered_mods
            
        # Render Mod Cards
        card_count = 0
        for mod_id, info in mods.items():
            self.create_mod_card(mod_id, info)
            card_count += 1
            
        # Trigger dynamic canvas resize config update
        self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all"))
        self.root.update_idletasks()

    def create_mod_card(self, mod_id, info):
        is_selected = (self.selected_mod_id == mod_id)
        card = tk.Frame(self.mod_cards_container, highlightthickness=1, bd=0)
        card._is_card = True
        card._is_active_card = is_selected
        card._mod_id = mod_id
        
        border = self.accent_color if is_selected else self.border_color
        card.configure(bg=self.card_color, highlightbackground=border, highlightcolor=border)
        card.pack(fill="x", pady=4, padx=5, ipady=6)
        
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
        status_text = "● Active" if status == "Enabled" else "○ Disabled"
        lbl_status = tk.Label(top_row, text=f" {status_text} ", font=("Segoe UI", 8, "bold"), fg=status_fg, bg=status_bg, padx=6, pady=2)
        lbl_status._is_status_pill = True
        lbl_status.grid(row=0, column=1, sticky="e")
        
        # Middle Row: Category badge & Info
        middle_row = tk.Frame(card, bg=self.card_color)
        middle_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=1)
        
        category = info.get("category", "General").upper()
        # Pill colors depending on category
        cat_colors = {
            "TEXTURE": ("#1e3a8a", "#3b82f6"),
            "AUDIO": ("#312e81", "#6366f1"),
            "SCRIPT": ("#065f46", "#10b981"),
            "UI": ("#5b21b6", "#8b5cf6"),
            "GAMEPLAY": ("#7c2d12", "#f97316")
        }
        bg_c, fg_c = cat_colors.get(category, ("#374151", self.text_dim))
        
        lbl_cat = tk.Label(middle_row, text=f" {category} ", font=("Segoe UI", 7, "bold"), fg=fg_c, bg=bg_c, padx=4, pady=1)
        lbl_cat._is_status_pill = True
        lbl_cat.pack(side="left", padx=(0, 5))
        
        info_text = f"Files: {len(info['files'])}  |  Size: {self.get_friendly_size(info['size'])}"
        lbl_info = tk.Label(middle_row, text=info_text, font=("Segoe UI", 8), fg=self.text_dim, bg=self.card_color, anchor="w")
        lbl_info._is_muted = True
        lbl_info.pack(side="left")
        
        # Click binding for card selection
        def select_click(event, m_id=mod_id):
            self.select_mod(m_id)
            
        card.bind("<Button-1>", select_click)
        top_row.bind("<Button-1>", select_click)
        middle_row.bind("<Button-1>", select_click)
        lbl_name.bind("<Button-1>", select_click)
        lbl_status.bind("<Button-1>", select_click)
        lbl_info.bind("<Button-1>", select_click)
        lbl_cat.bind("<Button-1>", select_click)
        
        # Hover bindings
        def on_enter(event, c=card):
            if self.selected_mod_id != mod_id:
                c.configure(highlightbackground=self.accent_color)
        def on_leave(event, c=card):
            if self.selected_mod_id != mod_id:
                c.configure(highlightbackground=self.border_color)
                
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Propagate hovers from inner elements to card container
        top_row.bind("<Enter>", on_enter)
        top_row.bind("<Leave>", on_leave)
        middle_row.bind("<Enter>", on_enter)
        middle_row.bind("<Leave>", on_leave)
        lbl_name.bind("<Enter>", on_enter)
        lbl_name.bind("<Leave>", on_leave)
        lbl_status.bind("<Enter>", on_enter)
        lbl_status.bind("<Leave>", on_leave)
        lbl_info.bind("<Enter>", on_enter)
        lbl_info.bind("<Leave>", on_leave)
        lbl_cat.bind("<Enter>", on_enter)
        lbl_cat.bind("<Leave>", on_leave)

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
        
        self.cmb_mod_category.set(info.get("category", "General"))
        
        self.ent_nexus_id.delete(0, tk.END)
        self.ent_nexus_id.insert(0, info.get("nexus_id", ""))
        
        self.ent_mod_link.delete(0, tk.END)
        self.ent_mod_link.insert(0, info.get("link", info.get("url", "")))
        
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
            
        # Update Conflict Tab
        self.update_conflict_ui(mod_id)

    def check_for_conflicts(self, mod_id):
        mod_repo_path = os.path.join(self.mods_disabled_dir, mod_id)
        info_path = os.path.join(mod_repo_path, "modinfo.ffxmod")
        fallback_path = os.path.join(mod_repo_path, "modinfo.json")
        read_path = info_path if os.path.exists(info_path) else fallback_path
        
        if not os.path.exists(read_path):
            return {}
            
        try:
            with open(read_path, "r") as f:
                info = decode_metadata(f.read())
        except Exception:
            return {}
            
        files = info.get("files", [])
        conflicts = {} # {other_mod_id: [file1, file2, ...]}
        
        for rel in files:
            other_owner = self.find_active_file_owner(rel, exclude_mod_id=mod_id)
            if other_owner:
                if other_owner not in conflicts:
                    conflicts[other_owner] = []
                conflicts[other_owner].append(rel)
        
        return conflicts

    def update_conflict_ui(self, mod_id):
        if not hasattr(self, "tree_conflicts"):
            return
            
        self.tree_conflicts.delete(*self.tree_conflicts.get_children())
        conflicts = self.check_for_conflicts(mod_id)
        
        if not conflicts:
            self.lbl_conflict_summary.config(text="No conflicts detected. This mod's files are unique among enabled mods.", fg=self.success_color)
            try:
                self.mod_details_notebook.tab(2, text=" Conflicts ")
            except Exception:
                pass
        else:
            total_files = sum(len(fs) for fs in conflicts.values())
            self.lbl_conflict_summary.config(text=f"⚠️ Warning: {total_files} file(s) conflict with {len(conflicts)} other enabled mod(s). Priority is determined by load order.", fg=self.error_color)
            try:
                self.mod_details_notebook.tab(2, text=f" Conflicts ({total_files}) ")
            except Exception:
                pass
            
            for other_id, files in conflicts.items():
                for f in files:
                    self.tree_conflicts.insert("", tk.END, values=(other_id, f))

    def auto_import_loose_files(self):
        if not self.mods_dir or getattr(self, "is_fahrenheit_mode", False):
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
        
        for folder in ["ffx_data", "ffx_ps2", "ffx2_data", "ffx2_ps2"]:
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
            if self.is_fahrenheit_mode:
                read_tracker = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id, "modinfo.ffxmod")
            else:
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
        creator_name = info.get("creator", info.get("author", ""))
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
        
        self.cmb_mod_category.set(info.get("category", "General"))
        
        self.ent_nexus_id.delete(0, tk.END)
        self.ent_nexus_id.insert(0, info.get("nexus_id", ""))
        
        self.ent_mod_link.delete(0, tk.END)
        self.ent_mod_link.insert(0, info.get("link", info.get("url", "")))
        
        # Populate files list
        self.tree_files.delete(*self.tree_files.get_children())
        files_list = info.get("files", [])
        
        mod_status = self.get_mod_status(mod_id)
        mod_repo_path = os.path.join(self.mods_disabled_dir, mod_id)
        
        for rel in files_list:
            # Check size from repo if disabled, or active mods folder if enabled
            fsize = 0
            if mod_status == "Disabled":
                src_path = os.path.join(mod_repo_path, rel)
            else:
                if self.is_fahrenheit_mode:
                    src_path = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id, "efl", "x", "FFX_Data", rel)
                else:
                    src_path = os.path.join(self.mods_dir, rel)
                    
            if os.path.exists(src_path):
                fsize = os.path.getsize(src_path)
            self.tree_files.insert("", tk.END, values=(rel, self.get_friendly_size(fsize)))
            
        # Update Conflict Tab
        self.update_conflict_ui(mod_id)
 
    def get_mod_status(self, mod_id):
        if getattr(self, "is_fahrenheit_mode", False):
            order = self.read_load_order()
            return "Enabled" if mod_id in order else "Disabled"
        else:
            tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
            old_tracker_path = os.path.join(self.mods_dir, f"{mod_id}.json")
            return "Enabled" if (os.path.exists(tracker_path) or os.path.exists(old_tracker_path)) else "Disabled"
 
    def clear_metadata_fields(self):
        self.ent_mod_creator.config(state="normal")
        self.ent_mod_name.delete(0, tk.END)
        self.ent_mod_creator.delete(0, tk.END)
        self.ent_mod_version.delete(0, tk.END)
        self.ent_mod_desc.delete(0, tk.END)

    def visit_mod_link(self):
        url = self.ent_mod_link.get().strip()
        if not url and self.ent_nexus_id.get().strip():
            url = f"https://www.nexusmods.com/finalfantasyxx2hdremaster/mods/{self.ent_nexus_id.get().strip()}"
            
        if url:
            import webbrowser
            webbrowser.open(url)
        else:
            messagebox.showinfo("Info", "No link or Nexus ID available for this mod.")

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
        creator_before = info.get("creator", info.get("author", ""))
        creator_input = self.ent_mod_creator.get().strip()
        
        # If creator was already set (not empty/User), do not allow modifying it
        if creator_before.strip().lower() not in ["", "user"] and creator_input != creator_before:
            creator_input = creator_before  # Keep original creator
            
        info["name"] = self.ent_mod_name.get().strip() or mod_id
        info["creator"] = creator_input
        info["author"] = creator_input
        info["version"] = self.ent_mod_version.get().strip() or "1.0"
        info["description"] = self.ent_mod_desc.get().strip()
        info["category"] = self.cmb_mod_category.get().strip() or "General"
        info["nexus_id"] = self.ent_nexus_id.get().strip()
        info["link"] = self.ent_mod_link.get().strip()
        
        try:
            with open(info_path, "w") as f:
                f.write(encode_metadata(info))
                
            # Clean up old .json file if we migrated it to .ffxmod
            if os.path.exists(fallback_path) and info_path != fallback_path:
                try:
                    os.remove(fallback_path)
                except Exception:
                    pass
                
            # If enabled, also sync name to tracking ffxmod / manifest
            if self.is_fahrenheit_mode:
                active_mod_dir = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id)
                tracker_path = os.path.join(active_mod_dir, "modinfo.ffxmod")
                manifest_path = os.path.join(active_mod_dir, f"{mod_id}.manifest.json")
                if os.path.exists(tracker_path):
                    try:
                        with open(tracker_path, "r") as f:
                            track = decode_metadata(f.read())
                        track["name"] = info["name"]
                        track["category"] = info["category"]
                        with open(tracker_path, "w") as f:
                            f.write(encode_metadata(track))
                    except Exception:
                        pass
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            man = json.load(f)
                        man["Name"] = info["name"]
                        man["Desc"] = info["description"]
                        man["Authors"] = info["creator"]
                        man["Version"] = info["version"]
                        man["Category"] = info["category"]
                        man["Link"] = info["link"]
                        with open(manifest_path, "w", encoding="utf-8") as f:
                            json.dump(man, f, indent=2)
                    except Exception:
                        pass
            else:
                tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
                old_tracker_path = os.path.join(self.mods_dir, f"{mod_id}.json")
                read_tracker = tracker_path if os.path.exists(tracker_path) else old_tracker_path if os.path.exists(old_tracker_path) else tracker_path
                
                if os.path.exists(read_tracker):
                    try:
                        with open(read_tracker, "r") as f:
                            track = decode_metadata(f.read())
                        track["name"] = info["name"]
                        track["category"] = info["category"]
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
                "category": "General",
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

    def find_active_file_owner(self, rel_path, exclude_mod_id=None):
        rel_norm = os.path.normpath(rel_path).lower()
        if getattr(self, "is_fahrenheit_mode", False):
            # In Fahrenheit, mods are prioritized according to the load order.
            # The mod listed LATEST in loadorder takes priority (overrides earlier ones).
            # So the active file owner is the enabled mod that comes LAST in loadorder containing this file.
            order = self.read_load_order()
            active_owner = None
            for other_mod_id in order:
                if exclude_mod_id and other_mod_id.lower() == exclude_mod_id.lower():
                    continue
                tracker_path = os.path.join(self.game_dir, "fahrenheit", "mods", other_mod_id, "modinfo.ffxmod")
                if os.path.exists(tracker_path):
                    try:
                        with open(tracker_path, "r", encoding="utf-8") as tf:
                            track = decode_metadata(tf.read())
                        track_files = [os.path.normpath(x).lower() for x in track.get("files", [])]
                        if rel_norm in track_files:
                            active_owner = other_mod_id
                    except Exception:
                        pass
            return active_owner
        else:
            if not self.mods_dir or not os.path.exists(self.mods_dir):
                return None
            for f in os.listdir(self.mods_dir):
                if f.endswith((".ffxmod", ".json")) and not f.startswith("modinfo"):
                    other_mod_id = f[:-7] if f.endswith(".ffxmod") else f[:-5]
                    if exclude_mod_id and other_mod_id.lower() == exclude_mod_id.lower():
                        continue
                    tracker_path = os.path.join(self.mods_dir, f)
                    try:
                        with open(tracker_path, "r", encoding="utf-8") as tf:
                            track = decode_metadata(tf.read())
                        track_files = [os.path.normpath(x).lower() for x in track.get("files", [])]
                        if rel_norm in track_files:
                            return other_mod_id
                    except Exception:
                        pass
            return None

    def enable_mod_logic(self, mod_id):
        mod_repo = os.path.join(self.mods_disabled_dir, mod_id)
        info_path = os.path.join(mod_repo, "modinfo.ffxmod")
        if not os.path.exists(info_path):
            info_path = os.path.join(mod_repo, "modinfo.json")
            
        if not os.path.exists(info_path):
            self.log(f"Error: Mod metadata file 'modinfo.ffxmod' is missing for mod '{mod_id}'.", "error")
            return False
            
        try:
            with open(info_path, "r", encoding="utf-8") as f:
                info = decode_metadata(f.read())
        except Exception as e:
            self.log(f"Error reading modinfo for mod '{mod_id}': {e}", "error")
            return False
            
        files = info.get("files", [])
        if not files:
            self.log(f"Warning: Mod '{mod_id}' is empty. No files to move.", "error")
            return False
            
        success_count = 0
        total_size = 0
        
        # Determine target active folder
        if self.is_fahrenheit_mode:
            active_mod_dir = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id)
            active_files_dir = os.path.join(active_mod_dir, "efl", "x", "FFX_Data")
        else:
            active_files_dir = self.mods_dir
            
        for rel in files:
            src = os.path.join(mod_repo, rel)
            dest = os.path.join(active_files_dir, rel)
            if os.path.exists(src):
                try:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    if os.path.lexists(dest):
                        # Find owner of the active file to avoid losing it
                        owner = self.find_active_file_owner(rel, exclude_mod_id=mod_id)
                        if owner:
                            owner_repo = os.path.join(self.mods_disabled_dir, owner)
                            owner_dest = os.path.join(owner_repo, rel)
                            try:
                                os.makedirs(os.path.dirname(owner_dest), exist_ok=True)
                                if os.path.lexists(owner_dest):
                                    if os.path.isdir(owner_dest) and not os.path.islink(owner_dest):
                                        shutil.rmtree(owner_dest)
                                    else:
                                        os.remove(owner_dest)
                                shutil.move(dest, owner_dest)
                                self.log(f"[Conflict] Moved active file '{rel}' back to '{owner}' repository before overwriting.", "info")
                            except Exception as ce:
                                self.log(f"[Conflict Error] Failed to backup conflicting file '{rel}' for '{owner}': {ce}", "error")
                        else:
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
                if os.path.exists(dest):
                    success_count += 1
                    total_size += os.path.getsize(dest)
                else:
                    self.log(f"Warning: File missing in repository: '{rel}'", "error")
                
        tracker = {
            "name": info.get("name", mod_id),
            "category": info.get("category", "General"),
            "files": files,
            "size": total_size
        }
        try:
            if self.is_fahrenheit_mode:
                # Write tracker file to fahrenheit/mods/{mod_id}/modinfo.ffxmod
                tracker_path = os.path.join(active_mod_dir, "modinfo.ffxmod")
                with open(tracker_path, "w", encoding="utf-8") as f:
                    f.write(encode_metadata(tracker))
                    
                # Write manifest file to fahrenheit/mods/{mod_id}/{mod_id}.manifest.json
                manifest_path = os.path.join(active_mod_dir, f"{mod_id}.manifest.json")
                manifest_data = {
                    "Id": mod_id,
                    "Name": info.get("name", mod_id),
                    "Desc": info.get("description", ""),
                    "Authors": info.get("author", info.get("creator", "Unknown")),
                    "Version": info.get("version", "1.0"),
                    "Category": info.get("category", "General"),
                    "Link": "",
                    "Dependencies": [],
                    "LoadAfter": [],
                    "Flags": "NONE"
                }
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest_data, f, indent=2)
                    
                # Append to loadorder file
                self.add_to_load_order(mod_id)
            else:
                tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
                with open(tracker_path, "w", encoding="utf-8") as f:
                    f.write(encode_metadata(tracker))
                old_tracker = os.path.join(self.mods_dir, f"{mod_id}.json")
                if os.path.exists(old_tracker):
                    try:
                        os.remove(old_tracker)
                    except Exception:
                        pass
            self.log(f"Successfully enabled mod '{mod_id}' ({success_count} of {len(files)} files activated).", "success")
            return True
        except Exception as e:
            self.log(f"Failed to write tracking file for mod '{mod_id}': {e}", "error")
            return False

    def enable_mod(self):
        mod_id = self.selected_mod_id
        if not mod_id:
            messagebox.showwarning("Warning", "Select a mod to enable.")
            return
            
        if self.get_mod_status(mod_id) == "Enabled":
            messagebox.showinfo("Status", "Mod is already enabled.")
            return
            
        self.log(f"Enabling mod '{mod_id}'...")
        if self.enable_mod_logic(mod_id):
            self.scan_mods()
            self.select_mod(mod_id)

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
        if self.is_fahrenheit_mode:
            active_mod_dir = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id)
            read_path = os.path.join(active_mod_dir, "modinfo.ffxmod")
            active_files_dir = os.path.join(active_mod_dir, "efl", "x", "FFX_Data")
        else:
            tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
            old_tracker_path = os.path.join(self.mods_dir, f"{mod_id}.json")
            read_path = tracker_path if os.path.exists(tracker_path) else old_tracker_path
            active_files_dir = self.mods_dir
            
        if not os.path.exists(read_path):
            self.log("Error: Active tracking file missing. Cannot uninstall cleanly.", "error")
            return
            
        try:
            with open(read_path, "r", encoding="utf-8") as f:
                track = decode_metadata(f.read())
        except Exception as e:
            self.log(f"Error reading tracking file: {e}", "error")
            return
            
        files = track.get("files", [])
        remove_count = 0
        mod_repo = os.path.join(self.mods_disabled_dir, mod_id)
        
        for rel in files:
            dest = os.path.join(active_files_dir, rel)
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
                    
                    # Auto-Restore logic: Check if another active mod lists this file path
                    other_owner = self.find_active_file_owner(rel, exclude_mod_id=mod_id)
                    if other_owner:
                        other_src = os.path.join(self.mods_disabled_dir, other_owner, rel)
                        if os.path.exists(other_src):
                            try:
                                os.makedirs(os.path.dirname(dest), exist_ok=True)
                                shutil.move(other_src, dest)
                                self.log(f"[Conflict] Restored overwritten file '{rel}' from '{other_owner}' repository.", "info")
                            except Exception as re:
                                self.log(f"[Conflict Error] Failed to restore file '{rel}' for '{other_owner}': {re}", "error")
                                
                    parent = os.path.dirname(dest)
                    while parent and parent != active_files_dir:
                        if not os.listdir(parent):
                            os.rmdir(parent)
                            parent = os.path.dirname(parent)
                        else:
                            break
                except Exception as e:
                    self.log(f"Failed to move back '{rel}': {e}", "error")
                    
        try:
            if self.is_fahrenheit_mode:
                # Remove from loadorder
                self.remove_from_load_order(mod_id)
                # Remove active mod directory
                if os.path.exists(active_mod_dir):
                    shutil.rmtree(active_mod_dir, ignore_errors=True)
            else:
                if os.path.exists(tracker_path):
                    os.remove(tracker_path)
                if os.path.exists(old_tracker_path):
                    os.remove(old_tracker_path)
            self.log(f"Successfully disabled mod '{mod_id}' (deactivated {remove_count} files).", "success")
        except Exception as e:
            self.log(f"Failed to delete tracking file: {e}", "error")

    def update_profile_dropdown(self):
        profiles = self.config.get("profiles", {})
        names = sorted(list(profiles.keys()))
        if not names:
            names = ["Default"]
        self.profile_combobox["values"] = names
        current = self.profile_combobox.get()
        if current not in names:
            self.profile_combobox.set(names[0])

    def save_profile(self):
        from tkinter import simpledialog
        name = simpledialog.askstring("Save Profile", "Enter a name for the new profile:")
        if not name:
            return
        name = name.strip()
        if not name:
            return
            
        # Get all currently enabled mod IDs
        enabled_mods = []
        for mod_id in self.mod_list:
            if self.get_mod_status(mod_id) == "Enabled":
                enabled_mods.append(mod_id)
                
        if "profiles" not in self.config:
            self.config["profiles"] = {}
            
        self.config["profiles"][name] = enabled_mods
        self.save_config()
        self.update_profile_dropdown()
        self.profile_combobox.set(name)
        self.log(f"Saved profile '{name}' with {len(enabled_mods)} active mods.", "success")

    def apply_profile(self):
        profile_name = self.profile_combobox.get()
        if not profile_name:
            return
            
        profiles = self.config.get("profiles", {})
        if profile_name not in profiles:
            if profile_name == "Default":
                enabled_mods = []
            else:
                self.log(f"Profile '{profile_name}' not found.", "error")
                return
        else:
            enabled_mods = profiles[profile_name]
            
        self.log(f"Applying profile '{profile_name}'...", "info")
        
        changed = False
        for mod_id in self.mod_list:
            is_enabled_now = (self.get_mod_status(mod_id) == "Enabled")
            should_be_enabled = (mod_id in enabled_mods)
            
            if should_be_enabled and not is_enabled_now:
                self.enable_mod_logic(mod_id)
                changed = True
            elif not should_be_enabled and is_enabled_now:
                self.disable_mod_logic(mod_id)
                changed = True
                
        if changed:
            self.scan_mods()
            if self.selected_mod_id:
                self.select_mod(self.selected_mod_id)
            else:
                self.clear_metadata_fields()
            self.log(f"Successfully applied profile '{profile_name}'.", "success")
        else:
            self.log(f"Profile '{profile_name}' is already active. No changes made.", "info")

    def delete_profile(self):
        profile_name = self.profile_combobox.get()
        if not profile_name or profile_name == "Default":
            messagebox.showwarning("Warning", "Cannot delete the Default profile.")
            return
            
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete profile '{profile_name}'?"):
            return
            
        profiles = self.config.get("profiles", {})
        if profile_name in profiles:
            del profiles[profile_name]
            self.save_config()
            self.update_profile_dropdown()
            self.log(f"Deleted profile '{profile_name}'.", "success")

    def import_zip_mod(self):
        from tkinter import filedialog
        import zipfile
        import shutil
        import re
        
        zip_path = filedialog.askopenfilename(filetypes=[("Mod Archives", "*.zip;*.rar"), ("Zip Archives", "*.zip"), ("RAR Archives", "*.rar")])
        if not zip_path:
            return
            
        self.log(f"Scanning archive: {os.path.basename(zip_path)}...")
        
        # Create a temporary import directory
        temp_dir = os.path.join(self.mods_disabled_dir, "_temp_import")
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
        os.makedirs(temp_dir, exist_ok=True)
        
        ext = os.path.splitext(zip_path)[1].lower()
        
        # Build UI Progress Modal
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Extracting Mod...")
        progress_win.geometry("450x150")
        progress_win.configure(bg=self.bg_color)
        progress_win.transient(self.root)
        progress_win.grab_set()
        
        lbl_msg = tk.Label(progress_win, text=f"Preparing extraction of {os.path.basename(zip_path)}...", font=("Segoe UI", 10), fg=self.text_color, bg=self.bg_color)
        lbl_msg.pack(pady=15, padx=20, anchor="w")
        
        progress = ttk.Progressbar(progress_win, orient="horizontal", mode="determinate", length=400)
        progress.pack(pady=5, padx=20, fill="x")
        
        lbl_percent = tk.Label(progress_win, text="0%", font=("Segoe UI", 9, "bold"), fg=self.accent_color, bg=self.bg_color)
        lbl_percent.pack(pady=5, padx=20, anchor="e")
        self.root.update()

        if ext == ".zip":
            try:
                with zipfile.ZipFile(zip_path, "r") as z:
                    list_files = z.infolist()
                    total = len(list_files)
                    for idx, z_file in enumerate(list_files):
                        z.extract(z_file, temp_dir)
                        if idx % max(1, total // 50) == 0 or idx == total - 1:
                            pct = int((idx + 1) / total * 100)
                            lbl_msg.config(text=f"Extracting: {z_file.filename}")
                            lbl_percent.config(text=f"{pct}%")
                            progress["value"] = pct
                            self.root.update()
            except Exception as e:
                progress_win.destroy()
                self.log(f"Failed to extract zip archive: {e}", "error")
                if os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                return
        elif ext == ".rar":
            progress_win.destroy() # Rar decompression relies on external subprocess, we destroy progress_win and run it.
            extracted = False
            # Method 1: Check for 7-Zip
            seven_zip_paths = [
                r"C:\Program Files\7-Zip\7z.exe",
                r"C:\Program Files (x86)\7-Zip\7z.exe"
            ]
            for sz_path in seven_zip_paths:
                if os.path.exists(sz_path):
                    try:
                        import subprocess
                        res = subprocess.run([sz_path, "x", zip_path, f"-o{temp_dir}", "-y"], capture_output=True)
                        if res.returncode == 0:
                            extracted = True
                            self.log("Successfully extracted RAR archive using 7-Zip.")
                            break
                    except Exception:
                        pass
                        
            # Method 2: Check for WinRAR
            if not extracted:
                winrar_paths = [
                    r"C:\Program Files\WinRAR\UnRAR.exe",
                    r"C:\Program Files\WinRAR\WinRAR.exe"
                ]
                for wr_path in winrar_paths:
                    if os.path.exists(wr_path):
                        try:
                            import subprocess
                            if "unrar" in wr_path.lower():
                                res = subprocess.run([wr_path, "x", zip_path, "-y", temp_dir], capture_output=True)
                            else:
                                res = subprocess.run([wr_path, "x", zip_path, "-y", temp_dir], capture_output=True)
                            if res.returncode == 0:
                                extracted = True
                                self.log("Successfully extracted RAR archive using WinRAR.")
                                break
                        except Exception:
                            pass
                            
            # Method 3: Fall back to native tar.exe (Windows 10/11)
            if not extracted:
                try:
                    import subprocess
                    res = subprocess.run(["tar", "-xf", zip_path, "-C", temp_dir], capture_output=True)
                    if res.returncode == 0:
                        extracted = True
                        self.log("Successfully extracted RAR archive using Windows tar.")
                except Exception:
                    pass
                    
            if not extracted:
                self.log("Error: Failed to extract RAR archive. Ensure 7-Zip, WinRAR, or Windows tar is installed.", "error")
                if os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                return
        else:
            progress_win.destroy()
            self.log(f"Error: Unsupported archive format '{ext}'. Only .zip and .rar are supported.", "error")
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
            return
            
        try:
            progress_win.destroy()
        except Exception:
            pass
            
        # Analyze the extracted contents
        # Strip single top-level folder wrapper if present
        root_dir = temp_dir
        subdirs = [x for x in os.listdir(temp_dir) if not x.startswith(".") and x != "__MACOSX"]
        if len(subdirs) == 1 and os.path.isdir(os.path.join(temp_dir, subdirs[0])):
            root_dir = os.path.join(temp_dir, subdirs[0])
            
        # Check for pre-existing metadata to enforce Credits Lock
        meta_data = None
        for inf in ["modinfo.ffxmod", "modinfo.json"]:
            mpath = os.path.join(root_dir, inf)
            if os.path.exists(mpath):
                try:
                    with open(mpath, "r", encoding="utf-8") as f:
                        meta_data = decode_metadata(f.read())
                    if meta_data and meta_data.get("name"):
                        break
                except Exception:
                    pass
                    
        mod_name = ""
        mod_creator = ""
        mod_version = "1.0"
        mod_desc = ""
        
        if meta_data and meta_data.get("name"):
            # Existing mod metadata found! Credits Lock active.
            mod_name = meta_data.get("name")
            mod_creator = meta_data.get("author", meta_data.get("creator", "Unknown"))
            mod_version = meta_data.get("version", "1.0")
            mod_desc = meta_data.get("description", "")
            self.log(f"Existing metadata detected. Mod: '{mod_name}' by '{mod_creator}' (Credits Locked).", "success")
        else:
            # No pre-existing metadata. Open popup dialog.
            from tkinter import simpledialog
            mod_name = simpledialog.askstring("Import Mod", "Enter Mod Name:")
            if not mod_name:
                shutil.rmtree(temp_dir)
                return
            mod_name = mod_name.strip()
            if not mod_name:
                shutil.rmtree(temp_dir)
                return
                
            mod_creator = simpledialog.askstring("Import Mod", "Enter Creator/Author:") or "Unknown"
            mod_creator = mod_creator.strip()
            
            mod_version = simpledialog.askstring("Import Mod", "Enter Version:", initialvalue="1.0") or "1.0"
            mod_desc = simpledialog.askstring("Import Mod", "Enter Description:") or ""
            
        # Gather file list relative to the root_dir
        mod_files = []
        for r, d, fs in os.walk(root_dir):
            for f in fs:
                if f in ["modinfo.ffxmod", "modinfo.json", "mod.json"]:
                    continue
                fpath = os.path.join(r, f)
                rel = os.path.relpath(fpath, root_dir)
                rel = rel.replace("\\", "/")
                mod_files.append(rel)
                
        if not mod_files:
            self.log("Error: Archive contains no mod files.", "error")
            shutil.rmtree(temp_dir)
            return
            
        info = {
            "name": mod_name,
            "author": mod_creator,
            "version": mod_version,
            "description": mod_desc,
            "category": "General",
            "files": mod_files
        }
        
        # Remove existing metadata files to write fresh ffxmod
        for inf in ["modinfo.ffxmod", "modinfo.json", "mod.json"]:
            mpath = os.path.join(root_dir, inf)
            if os.path.exists(mpath):
                try:
                    os.remove(mpath)
                except Exception:
                    pass
                    
        try:
            with open(os.path.join(root_dir, "modinfo.ffxmod"), "w", encoding="utf-8") as f:
                f.write(encode_metadata(info))
        except Exception as e:
            self.log(f"Failed to write metadata: {e}", "error")
            shutil.rmtree(temp_dir)
            return
            
        # Move to final mods_disabled folder
        sanitized_folder = re.sub(r'[^a-zA-Z0-9_-]', '_', mod_name).lower()
        final_dest = os.path.join(self.mods_disabled_dir, sanitized_folder)
        
        if os.path.exists(final_dest):
            if not messagebox.askyesno("Confirm Overwrite", f"Mod folder '{sanitized_folder}' already exists. Overwrite?"):
                counter = 1
                while os.path.exists(os.path.join(self.mods_disabled_dir, f"{sanitized_folder}_{counter}")):
                    counter += 1
                final_dest = os.path.join(self.mods_disabled_dir, f"{sanitized_folder}_{counter}")
            else:
                try:
                    shutil.rmtree(final_dest)
                except Exception:
                    pass
                    
        try:
            shutil.move(root_dir, final_dest)
            self.log(f"Successfully imported mod '{mod_name}' to repository folder '{os.path.basename(final_dest)}'.", "success")
        except Exception as e:
            self.log(f"Failed to move imported mod to repository: {e}", "error")
            
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
                
        self.scan_mods()

    def create_plugins_browser_page(self):
        frame = self.page_plugins_browser_frame
        frame.config(padx=15, pady=15)
        
        lbl_title = tk.Label(frame, text="🔌 Plugin Browser", font=("Segoe UI", 14, "bold"), fg=self.accent_color, bg=self.bg_color)
        lbl_title._is_title = True
        lbl_title.pack(anchor="w", pady=(0, 15))
        
        self.plugins_list_container = ttk.Frame(frame)
        self.plugins_list_container.pack(fill="both", expand=True)
        
        self.plugins_canvas = tk.Canvas(self.plugins_list_container, bg=self.bg_color, highlightthickness=0, borderwidth=0)
        self.plugins_scrollbar = ttk.Scrollbar(self.plugins_list_container, orient="vertical", command=self.plugins_canvas.yview)
        
        self.plugins_grid = ttk.Frame(self.plugins_canvas)
        self.plugins_canvas.configure(yscrollcommand=self.plugins_scrollbar.set)
        
        self.plugins_scrollbar.pack(side="right", fill="y")
        self.plugins_canvas.pack(side="left", fill="both", expand=True)
        
        self.plugins_canvas_window = self.plugins_canvas.create_window((0, 0), window=self.plugins_grid, anchor="nw")
        
        def on_plugins_configure(event):
            self.plugins_canvas.configure(scrollregion=self.plugins_canvas.bbox("all"))
        self.plugins_grid.bind("<Configure>", on_plugins_configure)
        
        def on_plugins_canvas_configure(event):
            self.plugins_canvas.itemconfig(self.plugins_canvas_window, width=event.width)
        self.plugins_canvas.bind("<Configure>", on_plugins_canvas_configure)
        
        def _on_plugins_mousewheel(event):
            self.plugins_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def bind_plugins_mouse(event):
            self.plugins_canvas.bind_all("<MouseWheel>", _on_plugins_mousewheel)
        def unbind_plugins_mouse(event):
            self.plugins_canvas.unbind_all("<MouseWheel>")
        self.plugins_canvas.bind("<Enter>", bind_plugins_mouse)
        self.plugins_canvas.bind("<Leave>", unbind_plugins_mouse)
        
        self.btn_refresh_plugins = tk.Button(frame, text="🔄 Refresh Plugins List", command=self.refresh_plugins_list, bg=self.card_color,
                                            fg=self.text_color, font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color, padx=12, pady=4)
        self.btn_refresh_plugins.pack(anchor="w", pady=(10, 0))
        self.bind_hover(self.btn_refresh_plugins)
        
        self.refresh_plugins_list()

    def refresh_plugins_list(self):
        for widget in self.plugins_grid.winfo_children():
            widget.destroy()
            
        lbl_loading = tk.Label(self.plugins_grid, text="Fetching plugin index...", font=("Segoe UI", 10, "italic"), fg=self.text_dim, bg=self.bg_color)
        lbl_loading.pack(anchor="w", pady=10)
        self.root.update()
        
        default_plugins = []
        plugins_list = default_plugins
        import urllib.request
        try:
            req = urllib.request.Request(
                "https://raw.githubusercontent.com/odinj2010/FFX-Mod-Manager/main/plugins.json",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=3.0) as response:
                content = response.read().decode('utf-8')
                fetched = json.loads(content)
                if isinstance(fetched, list) and len(fetched) > 0:
                    plugins_list = fetched
                    self.log("Successfully fetched remote plugin manifest.", "success")
        except Exception as e:
            self.log(f"Offline Mode: No plugin manifest available. ({e})", "info")
            
        lbl_loading.destroy()
        
        if not plugins_list:
            lbl_no_plugins = tk.Label(self.plugins_grid, text="No plugins available. Verify your internet connection or check back later.", font=("Segoe UI", 10, "italic"), fg=self.text_dim, bg=self.bg_color)
            lbl_no_plugins._is_muted = True
            lbl_no_plugins.pack(anchor="w", pady=10)
            self.update_widget_colors(self.plugins_grid)
            return
        
        for idx, plugin in enumerate(plugins_list):
            p_id = plugin["id"]
            name = plugin["name"]
            creator = plugin["creator"]
            version = plugin["version"]
            desc = plugin["description"]
            icon = plugin.get("icon", "🔌")
            url = plugin["download_url"]
            
            card = tk.Frame(self.plugins_grid, bd=1, relief="solid", highlightthickness=0, bg=self.card_color, padx=15, pady=15)
            card._is_card = True
            card.pack(fill="x", pady=6, padx=5)
            
            title_row = ttk.Frame(card)
            title_row.pack(fill="x", pady=(0, 5))
            
            lbl_p_name = tk.Label(title_row, text=f"{icon}  {name}  (v{version})", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_color)
            lbl_p_name._is_title = True
            lbl_p_name.pack(side="left")
            
            lbl_p_creator = tk.Label(title_row, text=f"by {creator}", font=("Segoe UI", 9, "italic"), fg=self.text_dim, bg=self.card_color)
            lbl_p_creator.pack(side="left", padx=15)
            
            lbl_p_desc = tk.Label(card, text=desc, font=("Segoe UI", 9), fg=self.text_color, bg=self.card_color, wraplength=500, justify="left", anchor="w")
            lbl_p_desc.pack(fill="x", pady=(0, 10))
            
            is_installed = False
            has_update = False
            local_version = ""
            
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            p_dir = os.path.join(base_dir, "plugins", p_id)
            local_json = os.path.join(p_dir, "plugin.json")
            
            if os.path.exists(local_json):
                is_installed = True
                try:
                    with open(local_json, "r", encoding="utf-8") as lf:
                        local_meta = json.load(lf)
                        local_version = local_meta.get("version", "")
                except Exception:
                    pass
                
                if local_version:
                    def parse_ver(v_str):
                        clean_str = v_str.upper().lstrip("V").lstrip(".")
                        parts = []
                        for x in clean_str.split("."):
                            try:
                                parts.append(int("".join(c for c in x if c.isdigit())))
                            except Exception:
                                parts.append(0)
                        return tuple(parts)
                    
                    try:
                        if parse_ver(version) > parse_ver(local_version):
                            has_update = True
                    except Exception:
                        pass

            if has_update:
                btn_text = f"🆕 Update to v{version}"
                btn_bg = self.accent_color
                is_primary_btn = True
            elif is_installed:
                btn_text = f"🔄 Reinstall (v{local_version})"
                btn_bg = self.border_color
                is_primary_btn = False
            else:
                btn_text = "📥 Install Plugin"
                btn_bg = self.accent_color
                is_primary_btn = True
                
            btn_state = "normal"
            
            btn_action = tk.Button(card, text=btn_text, state=btn_state, bg=btn_bg, fg="white",
                                   font=("Segoe UI", 9, "bold"), relief="flat", 
                                   activebackground=self.accent_hover if is_primary_btn else self.border_color, padx=12, pady=4)
            btn_action._is_primary = is_primary_btn
            btn_action.pack(anchor="e")
            if btn_state == "normal":
                btn_action.config(command=lambda pid=p_id, dl_url=url, btn=btn_action: self.install_plugin(pid, dl_url, btn))
                self.bind_hover(btn_action, is_primary=is_primary_btn)
                
        self.update_widget_colors(self.plugins_grid)

    def install_plugin(self, plugin_id, download_url, button):
        if not download_url:
            self.log(f"Error: Invalid download URL for plugin '{plugin_id}'.", "error")
            return
            
        button.config(text="Downloading...", state="disabled")
        self.root.update()
        
        import threading
        t = threading.Thread(target=self.download_plugin_async, args=(plugin_id, download_url, button))
        t.daemon = True
        t.start()

    def download_plugin_async(self, plugin_id, download_url, button):
        import urllib.request
        import zipfile
        import shutil
        
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        plugins_dir = os.path.join(base_dir, "plugins")
        os.makedirs(plugins_dir, exist_ok=True)
        
        zip_temp_path = os.path.join(plugins_dir, f"{plugin_id}_download.zip")
        dest_plugin_dir = os.path.join(plugins_dir, plugin_id)
        
        try:
            # Terminate active tracker process if it's currently running
            active_plugin = self.pages.get(f"plugin_{plugin_id}", {}).get("instance")
            if active_plugin:
                p = getattr(active_plugin, "_tracker_process", None)
                if p:
                    try:
                        self.log(f"Terminating running tracker process for plugin '{plugin_id}' before reinstall...", "info")
                        p.terminate()
                        p.wait(timeout=1)
                    except Exception:
                        try:
                            p.kill()
                        except Exception:
                            pass
                    active_plugin._tracker_process = None

            self.log(f"Downloading plugin zip from {download_url}...", "info")
            req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(zip_temp_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
                
            self.log(f"Extracting plugin '{plugin_id}'...", "info")
            if os.path.exists(dest_plugin_dir):
                try:
                    shutil.rmtree(dest_plugin_dir)
                except Exception:
                    pass
            os.makedirs(dest_plugin_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_temp_path, "r") as z:
                z.extractall(dest_plugin_dir)
                
            # Auto-unwrap if zip files were compressed inside a single wrapper folder
            try:
                extracted_items = os.listdir(dest_plugin_dir)
                if len(extracted_items) == 1:
                    sub_dir = os.path.join(dest_plugin_dir, extracted_items[0])
                    if os.path.isdir(sub_dir) and (os.path.exists(os.path.join(sub_dir, "plugin.json")) or os.path.exists(os.path.join(sub_dir, "plugin.JSON"))):
                        self.log(f"Unwrapping nested plugin folder '{extracted_items[0]}'...", "info")
                        for item in os.listdir(sub_dir):
                            shutil.move(os.path.join(sub_dir, item), os.path.join(dest_plugin_dir, item))
                        try:
                            os.rmdir(sub_dir)
                        except Exception:
                            pass
            except Exception as ue:
                self.log(f"Warning during plugin folder unwrapping: {ue}", "error")
                
            if os.path.exists(zip_temp_path):
                os.remove(zip_temp_path)
                
            self.log(f"Plugin '{plugin_id}' installed successfully! Reloading plugins...", "success")
            self.root.after(100, self.reload_plugins_ui, button)
            
        except Exception as e:
            self.log(f"Failed to download or install plugin '{plugin_id}': {e}", "error")
            if os.path.exists(zip_temp_path):
                try:
                    os.remove(zip_temp_path)
                except Exception:
                    pass
            self.root.after(100, lambda: button.config(text="❌ Failed. Retry", state="normal"))

    def reload_plugins_ui(self, button):
        plugin_keys = [k for k in self.pages.keys() if k.startswith("plugin_")]
        for pk in plugin_keys:
            # Notify the plugin instance that it is unloading
            instance = self.pages[pk].get("instance")
            if instance and hasattr(instance, "on_unload"):
                try:
                    instance.on_unload()
                except Exception as e:
                    self.log(f"Error unloading plugin '{pk}': {e}", "error")

            btn = self.sidebar_buttons.get(pk)
            if btn:
                try:
                    btn.destroy()
                except Exception:
                    pass
                del self.sidebar_buttons[pk]
            frame = self.pages[pk].get("frame")
            if frame:
                try:
                    frame.destroy()
                except Exception:
                    pass
            del self.pages[pk]
            
        # Purge any imported plugin modules from python's system cache
        for pk in list(sys.modules.keys()):
            if pk.startswith("plugin_"):
                sys.modules.pop(pk, None)
            
        self.load_plugins()
        self.apply_theme(self.current_theme_name)
        button.config(text="🔄 Reinstall", state="normal", bg=self.border_color)
        self.bind_hover(button, is_primary=False)

    def resolve_mod_relative_path(self, abs_path):
        abs_path = abs_path.replace("\\", "/")
        parts = abs_path.split("/")
        
        # 1. If absolute path contains the root folders explicitly
        if "ffx2_ps2/" in abs_path.lower():
            idx = abs_path.lower().find("ffx2_ps2/")
            return abs_path[idx:]
        if "ffx2_data/" in abs_path.lower():
            idx = abs_path.lower().find("ffx2_data/")
            return abs_path[idx:]
        if "ffx_ps2/" in abs_path.lower():
            idx = abs_path.lower().find("ffx_ps2/")
            return abs_path[idx:]
        if "ffx_data/" in abs_path.lower():
            idx = abs_path.lower().find("ffx_data/")
            return abs_path[idx:]
            
        # 2. If it contains subfolders ffx2/master, ffx/master or gamedata
        if "ffx2/master" in abs_path.lower():
            idx = abs_path.lower().find("ffx2/master")
            return "ffx2_ps2/" + abs_path[idx:]
        if "ffx/master" in abs_path.lower():
            idx = abs_path.lower().find("ffx/master")
            return "ffx_ps2/" + abs_path[idx:]
        if "gamedata" in abs_path.lower():
            idx = abs_path.lower().find("gamedata")
            if "ffx2" in abs_path.lower():
                return "ffx2_data/" + abs_path[idx:]
            else:
                return "ffx_data/" + abs_path[idx:]
            
        # 3. If it contains localized folders like jppc, new_uspc, uspc
        for loc in ["jppc", "new_uspc", "uspc"]:
            if loc in parts:
                idx = parts.index(loc)
                ext = os.path.splitext(abs_path)[1].lower()
                is_ffx2 = "ffx2" in abs_path.lower()
                
                if ext in [".bin", ".dat", ".evt"]:
                    prefix = "ffx2_ps2/ffx2/master/" if is_ffx2 else "ffx_ps2/ffx/master/"
                    return prefix + "/".join(parts[idx:])
                else:
                    prefix = "ffx2_data/gamedata/" if is_ffx2 else "ffx_data/gamedata/"
                    return prefix + "/".join(parts[idx:])
                    
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
                    if self.is_fahrenheit_mode:
                        active_files_dir = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id, "efl", "x", "FFX_Data")
                        tracker_path = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id, "modinfo.ffxmod")
                    else:
                        active_files_dir = self.mods_dir
                        tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
                        
                    for rel in files_list:
                        src = os.path.join(mod_repo, rel)
                        dest = os.path.join(active_files_dir, rel)
                        if os.path.exists(src):
                            try:
                                os.makedirs(os.path.dirname(dest), exist_ok=True)
                                shutil.copy2(src, dest)
                                total_size += os.path.getsize(dest)
                            except Exception:
                                pass
                                
                    with open(tracker_path, "w") as f:
                        f.write(encode_metadata({
                            "name": info.get("name", mod_id),
                            "files": files_list,
                            "size": total_size
                        }))
                        
                    if not self.is_fahrenheit_mode:
                        old_tracker = os.path.join(self.mods_dir, f"{mod_id}.json")
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
                    if self.is_fahrenheit_mode:
                        active_files_dir = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id, "efl", "x", "FFX_Data")
                        tracker_path = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id, "modinfo.ffxmod")
                    else:
                        active_files_dir = self.mods_dir
                        tracker_path = os.path.join(self.mods_dir, f"{mod_id}.ffxmod")
                        
                    for rel in files_list:
                        src = os.path.join(mod_repo, rel)
                        dest = os.path.join(active_files_dir, rel)
                        if os.path.exists(src):
                            try:
                                os.makedirs(os.path.dirname(dest), exist_ok=True)
                                shutil.copy2(src, dest)
                                total_size += os.path.getsize(dest)
                            except Exception:
                                pass
                                
                    with open(tracker_path, "w") as f:
                        f.write(encode_metadata({
                            "name": info.get("name", mod_id),
                            "files": files_list,
                            "size": total_size
                        }))
                        
                    if not self.is_fahrenheit_mode:
                        old_tracker = os.path.join(self.mods_dir, f"{mod_id}.json")
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

    def read_load_order(self):
        if not self.game_dir:
            return []
        loadorder_path = os.path.join(self.game_dir, "fahrenheit", "mods", "loadorder")
        if not os.path.exists(loadorder_path):
            return []
        try:
            with open(loadorder_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.log(f"Failed to read loadorder file: {e}", "error")
            return []

    def write_load_order(self, order_list):
        if not self.game_dir:
            return
        loadorder_path = os.path.join(self.game_dir, "fahrenheit", "mods", "loadorder")
        try:
            os.makedirs(os.path.dirname(loadorder_path), exist_ok=True)
            with open(loadorder_path, "w", encoding="utf-8") as f:
                for mod_id in order_list:
                    f.write(f"{mod_id}\n")
            
            # Keep manifests in sync with the physical load order
            self.sync_fahrenheit_manifests(order_list)
        except Exception as e:
            self.log(f"Failed to write loadorder file: {e}", "error")

    def sync_fahrenheit_manifests(self, order_list):
        if not getattr(self, "is_fahrenheit_mode", False):
            return
            
        for i, mod_id in enumerate(order_list):
            manifest_path = os.path.join(self.game_dir, "fahrenheit", "mods", mod_id, f"{mod_id}.manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                    
                    # Update LoadAfter to match current GUI position
                    manifest["LoadAfter"] = order_list[:i]
                    
                    with open(manifest_path, "w", encoding="utf-8") as f:
                        json.dump(manifest, f, indent=2)
                except Exception:
                    pass

    def add_to_load_order(self, mod_id):
        order = self.read_load_order()
        if mod_id not in order:
            order.append(mod_id)
            self.write_load_order(order)

    def remove_from_load_order(self, mod_id):
        order = self.read_load_order()
        if mod_id in order:
            order.remove(mod_id)
            self.write_load_order(order)

    def move_mod_up(self):
        mod_id = self.selected_mod_id
        if not mod_id:
            messagebox.showwarning("Warning", "Select an enabled mod to move.")
            return
        if self.get_mod_status(mod_id) != "Enabled":
            messagebox.showwarning("Warning", "Only enabled mods can be moved in the load order.")
            return
            
        order = self.read_load_order()
        if mod_id not in order:
            return
            
        idx = order.index(mod_id)
        if idx > 0:
            order[idx], order[idx - 1] = order[idx - 1], order[idx]
            self.write_load_order(order)
            self.log(f"Moved '{mod_id}' up in load order.", "success")
            self.refresh_list()
            self.select_mod(mod_id)

    def move_mod_down(self):
        mod_id = self.selected_mod_id
        if not mod_id:
            messagebox.showwarning("Warning", "Select an enabled mod to move.")
            return
        if self.get_mod_status(mod_id) != "Enabled":
            messagebox.showwarning("Warning", "Only enabled mods can be moved in the load order.")
            return
            
        order = self.read_load_order()
        if mod_id not in order:
            return
            
        idx = order.index(mod_id)
        if idx < len(order) - 1:
            order[idx], order[idx + 1] = order[idx + 1], order[idx]
            self.write_load_order(order)
            self.log(f"Moved '{mod_id}' down in load order.", "success")
            self.refresh_list()
            self.select_mod(mod_id)

    def safe_mode_reset(self):
        if not self.game_dir:
            messagebox.showwarning("Warning", "Configure FFX game directory first.")
            return
        if not messagebox.askyesno("Confirm Safe Reset", "Are you sure you want to disable ALL active mods?\n\nThis will return all files to their inactive repository backups and clean up the active mod folder."):
            return
            
        self.log("Starting Safe Mode reset: Deactivating all active mods...")
        disabled_count = 0
        
        # Read active mods list
        active_list = []
        if self.is_fahrenheit_mode:
            active_list = self.read_load_order()
        else:
            if self.mods_dir and os.path.exists(self.mods_dir):
                for f in os.listdir(self.mods_dir):
                    if f.endswith((".ffxmod", ".json")) and not f.startswith("modinfo"):
                        active_list.append(f[:-7] if f.endswith(".ffxmod") else f[:-5])
                        
        for mod_id in active_list:
            try:
                self.disable_mod_logic(mod_id)
                disabled_count += 1
            except Exception as e:
                self.log(f"Failed disabling '{mod_id}': {e}", "error")
                
        self.refresh_list()
        messagebox.showinfo("Safe Reset Complete", f"Successfully deactivated {disabled_count} active mod(s). Your directory has been restored to clean state.")
        self.log(f"Safe reset completed successfully (deactivated {disabled_count} mods).", "success")

    def verify_deployment_safety(self):
        if not self.game_dir or not os.path.exists(self.game_dir):
            messagebox.showwarning("Diagnostics", "No valid game folder configured.")
            return
            
        self.log("Running diagnostics on game directories...")
        
        # 1. Check permissions (attempt write a dummy file)
        dummy_path = os.path.join(self.game_dir, "_ffxmm_perm_test.tmp")
        write_ok = False
        try:
            with open(dummy_path, "w") as f:
                f.write("test")
            os.remove(dummy_path)
            write_ok = True
        except Exception:
            pass
            
        perm_status = "🟢 Permissions: Write Access OK" if write_ok else "❌ Permissions: Access Denied (Run as Administrator)"
        self.log(perm_status, "info" if write_ok else "error")
        
        # 2. Check Disk Space
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        total_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(self.game_dir),
            None,
            ctypes.byref(total_bytes),
            ctypes.byref(free_bytes)
        )
        free_gb = free_bytes.value / (1024**3)
        space_ok = free_gb > 1.0 # arbitrary 1GB warning threshold
        space_status = f"🟢 Free Space: {free_gb:.2f} GB" if space_ok else f"⚠️ Free Space low: {free_gb:.2f} GB"
        self.log(space_status, "info" if space_ok else "error")
        
        # 3. Check Steam Registry mapping status
        steam_path = self.get_steam_install_path()
        steam_status = f"🟢 Steam install matched: {steam_path}" if steam_path else "⚠️ Steam install path registry key mapping missing (using manual path)"
        self.log(steam_status, "info" if steam_path else "warning")
        
        messagebox.showinfo("Diagnostics Complete", f"Diagnostics status:\n\n- Write Permissions: {'OK' if write_ok else 'Denied'}\n- Disk Free Space: {free_gb:.2f} GB\n- Steam Path Auto-Mapping: {'Detected' if steam_path else 'Missing'}")

    def check_for_updates(self):
        import threading
        t = threading.Thread(target=self.run_update_check, daemon=True)
        t.start()

    def run_update_check(self):
        import urllib.request
        import json
        
        try:
            req = urllib.request.Request(
                "https://api.github.com/repos/odinj2010/FFX-Mod-Manager/releases/latest",
                headers={'User-Agent': 'FFXMM-Update-Checker'}
            )
            with urllib.request.urlopen(req, timeout=4.0) as response:
                data = json.loads(response.read().decode('utf-8'))
                raw_tag = data.get("tag_name", "").strip()
                tag_name = raw_tag.upper().lstrip("V").lstrip(".")
                html_url = data.get("html_url", "https://github.com/odinj2010/FFX-Mod-Manager/releases")
                
                if not tag_name:
                    return
                    
                # Parse versions
                def parse_ver(v_str):
                    # Remove any leading V/v or dots again just in case
                    clean_str = v_str.upper().lstrip("V").lstrip(".")
                    parts = []
                    for x in clean_str.split("."):
                        try:
                            parts.append(int("".join(c for c in x if c.isdigit())))
                        except Exception:
                            parts.append(0)
                    return tuple(parts)
                    
                local_ver = parse_ver(APP_VERSION)
                online_ver = parse_ver(tag_name)
                
                if online_ver > local_ver:
                    self.log(f"New update available: {raw_tag} (Current: v{APP_VERSION})", "info")
                    self.root.after(0, lambda: self.show_update_banner(raw_tag, html_url))
        except Exception as e:
            # Silent fail so it doesn't interrupt offline use
            pass

    def show_update_banner(self, new_ver, update_url):
        # Clear existing banner content if any
        for widget in self.update_banner_frame.winfo_children():
            widget.destroy()
            
        banner = tk.Frame(self.update_banner_frame, bg="#1e3a8a" if self.bg_color != "#f3f4f6" else "#bfdbfe", pady=8, padx=15)
        banner.pack(fill="x", expand=True, pady=(0, 10))
        
        # Ensure correct formatting of display names
        disp_new = new_ver if new_ver.upper().startswith("V") else f"v{new_ver}"
        disp_local = APP_VERSION if APP_VERSION.upper().startswith("V") else f"v{APP_VERSION}"
        
        lbl_msg = tk.Label(banner, text=f"🚀 A new version of FFX Mod Manager is available: {disp_new} (Current: {disp_local})", 
                           bg=banner.cget("bg"), fg="#ffffff" if self.bg_color != "#f3f4f6" else "#1e3a8a", font=("Segoe UI", 9, "bold"))
        lbl_msg.pack(side="left")
        
        def choose_download_source():
            dialog = tk.Toplevel(self.root)
            dialog.title("Select Download Source")
            dialog.geometry("400x180")
            dialog.configure(bg=self.bg_color)
            dialog.transient(self.root)
            
            # Center the dialog window over root window
            dialog.update_idletasks()
            parent_w = self.root.winfo_width()
            parent_h = self.root.winfo_height()
            parent_x = self.root.winfo_x()
            parent_y = self.root.winfo_y()
            
            w = 400
            h = 180
            x = parent_x + (parent_w - w) // 2
            y = parent_y + (parent_h - h) // 2
            dialog.geometry(f"{w}x{h}+{x}+{y}")
            
            dialog.grab_set()
            
            lbl_title = tk.Label(dialog, text="Where would you like to download from?", font=("Segoe UI", 10, "bold"), fg=self.text_color, bg=self.bg_color)
            lbl_title.pack(pady=(20, 15))
            
            def open_github():
                import webbrowser
                webbrowser.open(update_url)
                dialog.destroy()
                
            def open_nexus():
                import webbrowser
                # Static Nexus FFXMM mods page link
                webbrowser.open("https://www.nexusmods.com/finalfantasyxx2hdremaster/mods/327")
                dialog.destroy()
                
            btn_frame = tk.Frame(dialog, bg=self.bg_color)
            btn_frame.pack(fill="x", padx=40, pady=5)
            
            btn_nexus = tk.Button(btn_frame, text="📥 Download from Nexus Mods", command=open_nexus, bg=self.accent_color, fg="white",
                                  font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover, height=2)
            btn_nexus._is_primary = True
            btn_nexus.pack(fill="x", expand=True)
            self.bind_hover(btn_nexus, is_primary=True)
            
            # Small fallback text link on the bottom
            lbl_fallback = tk.Label(dialog, text="Nexus Mods quarantined or not working?", font=("Segoe UI", 8), fg=self.text_dim, bg=self.bg_color)
            lbl_fallback.pack(pady=(15, 0))
            
            lbl_github = tk.Label(dialog, text="Get temporary backup download from GitHub", font=("Segoe UI", 8, "underline"), fg=self.accent_color, bg=self.bg_color, cursor="hand2")
            lbl_github.pack(pady=(0, 10))
            
            def on_git_enter(event):
                lbl_github.configure(fg=self.accent_hover)
            def on_git_leave(event):
                lbl_github.configure(fg=self.accent_color)
                
            lbl_github.bind("<Button-1>", lambda e: open_github())
            lbl_github.bind("<Enter>", on_git_enter)
            lbl_github.bind("<Leave>", on_git_leave)
            
        btn_download = tk.Button(banner, text="📥 Get Update", command=choose_download_source, bg=self.accent_color, fg="white", 
                                 font=("Segoe UI", 8, "bold"), relief="flat", activebackground=self.accent_hover, bd=0, padx=8, pady=2)
        btn_download.pack(side="right", padx=(10, 0))
        self.bind_hover(btn_download)
        
        btn_close = tk.Button(banner, text="✕", command=banner.destroy, bg=banner.cget("bg"), fg="#ffffff" if self.bg_color != "#f3f4f6" else "#1e3a8a", 
                              font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color, bd=0, padx=6)
        btn_close.pack(side="right")

    def launch_game(self):
        if not self.game_dir:
            messagebox.showwarning("Warning", "Please configure your FFX Game Folder first.")
            return
            
        fh_launcher = os.path.join(self.game_dir, "fahrenheit", "bin", "fhstage0.exe")
        if os.path.exists(fh_launcher):
            self.is_fahrenheit_mode = True
            self.log("Launching Final Fantasy X via Fahrenheit Framework...", "info")
            try:
                game_exe = os.path.join(self.game_dir, "FFX.exe")
                fh_dir = os.path.join(self.game_dir, "fahrenheit", "bin")
                p = subprocess.Popen(
                    [fh_launcher, game_exe],
                    cwd=fh_dir
                )
                self.log(f"Fahrenheit launcher started (PID: {p.pid}). Monitoring game process...", "success")
                
                # Start background monitoring for game process & plugin trackers
                self.root.after(2000, self.start_game_monitoring)
            except Exception as e:
                self.log(f"Failed to launch Fahrenheit: {e}", "error")
        else:
            self.is_fahrenheit_mode = False
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
        self.log("Waiting for game process (FFX.exe or FFX-2.exe) to start...", "info")
        
        pid = None
        detected_exe = None
        # Loop checking for FFX.exe or FFX-2.exe up to 60 seconds
        for _ in range(60):
            for exe in ["FFX.exe", "FFX-2.exe"]:
                pid = self.find_process_id(exe)
                if pid:
                    detected_exe = exe
                    break
            if pid:
                break
            time.sleep(1)
            
        if not pid:
            self.log("Game launch monitoring timed out.", "warning")
            return
            
        self.log(f"Game process {detected_exe} detected running (PID: {pid})!", "success")
        
        # Fire plugin launch hooks
        self.on_game_launched(pid, detected_exe)
        
        # Monitor until it closes
        while True:
            if not self.is_process_running(pid):
                break
            time.sleep(2)
            
        self.log(f"Game process {detected_exe} closed.", "info")
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
            # Clean null-terminated byte string and compare
            exe_name = pe32.szExeFile.split(b'\0')[0].decode('utf-8', errors='ignore')
            if exe_name.lower() == process_name.lower():
                pid = pe32.th32ProcessID
                break
            if not kernel32.Process32Next(hProcessSnap, ctypes.byref(pe32)):
                break
                
        kernel32.CloseHandle(hProcessSnap)
        return pid

    def is_process_running(self, pid):
        if not kernel32 or not pid:
            return False
            
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        
        hProcess = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not hProcess:
            # Check if it failed because the process is already gone
            return False
            
        exit_code = ctypes.c_ulong()
        running = False
        if kernel32.GetExitCodeProcess(hProcess, ctypes.byref(exit_code)):
            running = (exit_code.value == STILL_ACTIVE)
            
        kernel32.CloseHandle(hProcess)
        return running

    def on_game_launched(self, pid, exe_name="FFX.exe"):
        for plugin in self.plugins:
            # Achievements and Walkthrough are FFX-specific. Avoid launching their trackers on FFX-2.
            is_ffx_only = plugin._metadata.get("name") in ["Achievements", "Walkthrough", "Custom Achievements"]
            if is_ffx_only and exe_name == "FFX-2.exe":
                self.log(f"Skipping background tracker execution for FFX-only plugin '{plugin._metadata['name']}' during FFX-2 gameplay.", "info")
                continue
                
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
                    # Query actual hotkey from config if exists
                    default_hk = plugin._metadata.get("default_hotkey", "F8")
                    hk_str = default_hk
                    cfg_path = os.path.join(plugin_dir, "overlay_config.json")
                    if os.path.exists(cfg_path):
                        try:
                            with open(cfg_path, "r", encoding="utf-8") as f:
                                hk_str = json.load(f).get("hotkey_str", default_hk)
                        except Exception:
                            pass
                    self.log(f"💡 Tip: Press {hk_str} in-game to toggle the {plugin._metadata['name']} overlay HUD!", "info")

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
                            sys.modules[f"plugin_{d}"] = module
                            sys.path.insert(0, dpath)
                            try:
                                spec.loader.exec_module(module)
                            finally:
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


class ThemeCreatorDialog:
    def __init__(self, manager):
        self.manager = manager
        self.dialog = tk.Toplevel(manager.root)
        self.dialog.title("Create Custom Theme")
        self.dialog.geometry("700x520")
        self.dialog.configure(bg=manager.bg_color)
        self.dialog.transient(manager.root)
        self.dialog.grab_set()
        
        # Color fields
        self.colors = {
            "bg_color": tk.StringVar(value=manager.bg_color),
            "card_color": tk.StringVar(value=manager.card_color),
            "accent_color": tk.StringVar(value=manager.accent_color),
            "accent_hover": tk.StringVar(value=manager.accent_hover),
            "text_color": tk.StringVar(value=manager.text_color),
            "text_dim": tk.StringVar(value=manager.text_dim),
            "border_color": tk.StringVar(value=manager.border_color),
            "success_color": tk.StringVar(value=manager.success_color),
            "error_color": tk.StringVar(value=manager.error_color)
        }
        
        self.theme_name_var = tk.StringVar(value="My Custom Theme")
        self.create_widgets()
        
    def create_widgets(self):
        main_pane = tk.Frame(self.dialog, bg=self.manager.bg_color, padx=15, pady=15)
        main_pane.pack(fill="both", expand=True)
        
        left_frame = tk.Frame(main_pane, bg=self.manager.bg_color)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        right_frame = tk.Frame(main_pane, bg=self.manager.bg_color, width=280)
        right_frame.pack(side="right", fill="both", expand=False)
        
        # Form: Theme Name
        tk.Label(left_frame, text="Theme Name:", font=("Segoe UI", 10, "bold"), bg=self.manager.bg_color, fg=self.manager.text_color).grid(row=0, column=0, sticky="w", pady=5)
        ent_name = ttk.Entry(left_frame, textvariable=self.theme_name_var, width=22)
        ent_name.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        row_idx = 1
        for key, var in self.colors.items():
            lbl_name = key.replace("_", " ").title() + ":"
            tk.Label(left_frame, text=lbl_name, bg=self.manager.bg_color, fg=self.manager.text_color).grid(row=row_idx, column=0, sticky="w", pady=4)
            
            color_input_frame = tk.Frame(left_frame, bg=self.manager.bg_color)
            color_input_frame.grid(row=row_idx, column=1, sticky="w", padx=5, pady=4)
            
            ent_val = ttk.Entry(color_input_frame, textvariable=var, width=10)
            ent_val.pack(side="left", padx=(0, 5))
            
            # Trace changes
            var.trace_add("write", lambda *args, k=key: self.update_preview())
            
            btn_pick = tk.Button(color_input_frame, width=3, height=1, relief="flat", bd=1)
            btn_pick.pack(side="left")
            btn_pick.config(command=lambda v=var, b=btn_pick: self.pick_color(v, b))
            btn_pick.config(bg=var.get())
            
            setattr(self, f"btn_{key}", btn_pick)
            row_idx += 1
            
        btn_frame = tk.Frame(left_frame, bg=self.manager.bg_color)
        btn_frame.grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=15)
        
        btn_save = tk.Button(btn_frame, text="Save & Apply", command=self.save_theme, bg=self.manager.success_color,
                             fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#059669", padx=12, pady=4)
        btn_save.pack(side="left", padx=(0, 10))
        self.manager.bind_hover(btn_save)
        
        btn_cancel = tk.Button(btn_frame, text="Cancel", command=self.dialog.destroy, bg=self.manager.card_color,
                               fg=self.manager.text_color, font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.manager.border_color, padx=12, pady=4)
        btn_cancel.pack(side="left")
        self.manager.bind_hover(btn_cancel)
        
        # Right Frame: Live Preview
        lbl_prev_title = tk.Label(right_frame, text="Live Preview", font=("Segoe UI", 10, "bold"), bg=self.manager.bg_color, fg=self.manager.text_color)
        lbl_prev_title.pack(anchor="w", pady=(0, 5))
        
        self.preview_area = tk.Frame(right_frame, bd=1, relief="solid", padx=10, pady=10)
        self.preview_area.pack(fill="both", expand=True)
        
        self.prev_card = tk.Frame(self.preview_area, bd=1, relief="solid", padx=10, pady=10)
        self.prev_card.pack(fill="x", pady=10)
        
        self.prev_lbl = tk.Label(self.prev_card, text="Sample Mod Title", font=("Segoe UI", 10, "bold"))
        self.prev_lbl.pack(anchor="w")
        
        self.prev_desc = tk.Label(self.prev_card, text="This is a description of the mod.", font=("Segoe UI", 8))
        self.prev_desc.pack(anchor="w", pady=(2, 5))
        
        self.prev_btn = tk.Button(self.prev_card, text="Sample Button", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=3)
        self.prev_btn.pack(fill="x")
        
        self.update_preview()
        
    def pick_color(self, var, btn):
        from tkinter import colorchooser
        color = colorchooser.askcolor(initialcolor=var.get(), parent=self.dialog)
        if color[1]:
            var.set(color[1])
            btn.config(bg=color[1])
            self.update_preview()
            
    def update_preview(self):
        try:
            bg = self.colors["bg_color"].get()
            card = self.colors["card_color"].get()
            accent = self.colors["accent_color"].get()
            text = self.colors["text_color"].get()
            dim = self.colors["text_dim"].get()
            border = self.colors["border_color"].get()
            
            # Update picking buttons bg
            for key, var in self.colors.items():
                btn = getattr(self, f"btn_{key}", None)
                if btn:
                    try:
                        btn.config(bg=var.get())
                    except Exception:
                        pass
                        
            # Update Preview area elements
            self.preview_area.config(bg=bg, highlightbackground=border, highlightcolor=border)
            self.prev_card.config(bg=card, highlightbackground=border, highlightcolor=border)
            self.prev_lbl.config(bg=card, fg=text)
            self.prev_desc.config(bg=card, fg=dim)
            self.prev_btn.config(bg=accent, fg="white", activebackground=accent)
        except Exception:
            pass
            
    def save_theme(self):
        import re
        name = self.theme_name_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a theme name.")
            return
            
        tdata = {"name": name}
        hex_pat = re.compile(r"^#[0-9a-fA-F]{6}$")
        for key, var in self.colors.items():
            val = var.get().strip()
            if not hex_pat.match(val):
                messagebox.showwarning("Warning", f"Invalid Hex color code for {key}: '{val}'")
                return
            tdata[key] = val
            
        slug = re.sub(r'[^a-zA-Z0-9_-]', '_', name).lower() + ".json"
        
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        themes_dir = os.path.join(base_dir, "themes")
        os.makedirs(themes_dir, exist_ok=True)
        
        path = os.path.join(themes_dir, slug)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(tdata, f, indent=2)
            self.manager.themes[name] = tdata
            self.manager.theme_selector["values"] = list(self.manager.themes.keys())
            self.manager.apply_theme(name)
            self.manager.theme_selector.set(name)
            self.manager.log(f"Successfully created and applied theme '{name}' (saved as {slug}).", "success")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save theme file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FFXModManagerGUI(root)
    root.mainloop()
