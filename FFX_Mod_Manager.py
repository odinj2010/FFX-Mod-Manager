import os
import sys
import json
import shutil
import subprocess
import tkinter as tk
import base64
from tkinter import ttk, filedialog, messagebox, simpledialog


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
        
        # Dark Theme Palette
        self.bg_color = "#121212"
        self.card_color = "#1e1e1e"
        self.accent_color = "#3b82f6"
        self.accent_hover = "#2563eb"
        self.text_color = "#e5e7eb"
        self.text_dim = "#9ca3af"
        self.border_color = "#374151"
        self.success_color = "#10b981"
        self.error_color = "#ef4444"
        
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
        
        # Load configs
        self.config = self.load_config()
        self.init_paths()
        
        # Build UI
        self.create_widgets()
        
        # Auto-import loose files check
        self.root.after(500, self.auto_import_loose_files)

    def load_config(self):
        config = {
            "game_dir": "",
            "mods_dir": "",
            "mods_disabled_dir": ""
        }
        
        # 1. Try Mod Manager config
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config.update(json.load(f))
                    return config
            except Exception:
                pass
                
        # 2. Try Modding Toolbox config
        if os.path.exists(TOOLBOX_CONFIG):
            try:
                with open(TOOLBOX_CONFIG, "r") as f:
                    toolbox = json.load(f)
                    path = toolbox.get("loose_folder_path", "")
                    if path:
                        # If loose_folder_path points to data/mods
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
            with open(CONFIG_FILE, "w") as f:
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
        # Create a scrollable canvas wrapper to support smaller window sizes
        canvas = tk.Canvas(self.parent, bg=self.bg_color, highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        
        main_frame = ttk.Frame(canvas, padding=15)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        main_frame.bind("<Configure>", on_frame_configure)
        
        def on_canvas_configure(event):
            # Stretch the main frame to fill the canvas width
            canvas.itemconfig(canvas_window, width=event.width)
            # If the canvas area is taller than the frame's requested height, stretch the frame's height
            # so that internal widgets (like treeviews and listboxes) expand to fill the window.
            # Otherwise, let the frame use its requested height so the scrollbar functions.
            req_height = main_frame.winfo_reqheight()
            if event.height > req_height:
                canvas.itemconfig(canvas_window, height=event.height)
            else:
                canvas.itemconfig(canvas_window, height="")
                
        canvas.bind("<Configure>", on_canvas_configure)
        
        def _on_mousewheel(event):
            # Do not scroll the main canvas if the mouse is currently scrolling inside
            # another scrollable widget like a Treeview or Text log.
            try:
                widget_type = event.widget.winfo_class()
                if widget_type in ("Text", "Treeview", "Listbox"):
                    return
            except Exception:
                pass
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            
        canvas.bind("<Enter>", bind_mousewheel)
        canvas.bind("<Leave>", unbind_mousewheel)
        
        # 1. Config top bar
        cfg_frame = ttk.LabelFrame(main_frame, text=" Game Directory Settings ", padding=10)
        cfg_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(cfg_frame, text="FFX Game Folder:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.ent_game_path = ttk.Entry(cfg_frame, width=50)
        self.ent_game_path.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        cfg_frame.columnconfigure(1, weight=1)
        
        if self.game_dir:
            self.ent_game_path.insert(0, self.game_dir)
            
        self.ent_game_path.bind("<FocusOut>", self.on_game_path_changed)
        self.ent_game_path.bind("<Return>", self.on_game_path_changed)
        
        btn_browse = tk.Button(cfg_frame, text="Browse...", command=self.browse_game_folder, bg=self.card_color, 
                               fg=self.text_color, relief="flat", activebackground=self.border_color)
        btn_browse.grid(row=0, column=2, padx=(0, 10))
        self.bind_hover(btn_browse)
        
        # Mod Loader Status Bar
        self.lbl_loader_status = ttk.Label(cfg_frame, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_loader_status.grid(row=1, column=0, columnspan=3, sticky="w", pady=(5, 0))
        self.update_loader_status_ui()
        
        # 2. Main Paned Window
        paned = ttk.Panedwindow(main_frame, orient="horizontal")
        paned.pack(fill="both", expand=True, pady=5)
        
        # Left Panel - Mod List
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        lbl_mod = ttk.Label(left_frame, text="Available Mods", font=("Segoe UI", 11, "bold"), foreground=self.accent_color)
        lbl_mod.pack(anchor="w", pady=(0, 5))
        
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill="both", expand=True)
        
        self.tree_mods = ttk.Treeview(tree_frame, columns=("name", "status", "files", "size"), show="headings", selectmode="browse")
        self.tree_mods.heading("name", text="Mod Name")
        self.tree_mods.heading("status", text="Status")
        self.tree_mods.heading("files", text="Files")
        self.tree_mods.heading("size", text="Size")
        self.tree_mods.column("name", width=150, anchor="w")
        self.tree_mods.column("status", width=80, anchor="center")
        self.tree_mods.column("files", width=60, anchor="center")
        self.tree_mods.column("size", width=80, anchor="e")
        self.tree_mods.pack(fill="both", expand=True, side="left")
        
        scroll = ttk.Scrollbar(tree_frame, command=self.tree_mods.yview)
        scroll.pack(fill="y", side="right")
        self.tree_mods.config(yscrollcommand=scroll.set)
        
        # Actions Frame under list
        btn_p_frame = ttk.Frame(left_frame, padding=(0, 5, 0, 0))
        btn_p_frame.pack(fill="x")
        
        btn_enable = tk.Button(btn_p_frame, text="⚡ Enable Mod (Install)", command=self.enable_mod, bg=self.success_color,
                               fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#059669")
        btn_enable.pack(fill="x", pady=2)
        self.bind_hover_color(btn_enable, "#059669", self.success_color)
        
        btn_disable = tk.Button(btn_p_frame, text="⏪ Disable Mod (Uninstall)", command=self.disable_mod, bg=self.card_color,
                                fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color)
        btn_disable.pack(fill="x", pady=2)
        self.bind_hover(btn_disable)
        
        btn_new = tk.Button(btn_p_frame, text="Create New Mod", command=self.create_mod, bg=self.accent_color,
                            fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover)
        btn_new.pack(fill="x", pady=2)
        self.bind_hover(btn_new, is_primary=True)
        
        btn_del = tk.Button(btn_p_frame, text="Delete Mod From Disk", command=self.delete_mod, bg=self.error_color,
                            fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#dc2626")
        btn_del.pack(fill="x", pady=2)
        self.bind_hover_color(btn_del, "#dc2626", self.error_color)
        
        btn_refresh = tk.Button(btn_p_frame, text="🔄 Refresh Mod List", command=self.refresh_list, bg=self.card_color,
                                fg=self.text_color, font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.border_color)
        btn_refresh.pack(fill="x", pady=2)
        self.bind_hover(btn_refresh)
        
        # Right Panel - Mod Details
        right_frame = ttk.Frame(paned, padding=(10, 0, 0, 0))
        paned.add(right_frame, weight=1)
        
        self.lbl_mod_title = ttk.Label(right_frame, text="Selected Mod: <None>", font=("Segoe UI", 11, "bold"), foreground=self.accent_color)
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
        ttk.Label(right_frame, text="Files Installed by Mod", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(5, 2))
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
        btn_import.pack(side="left", padx=(0, 5))
        self.bind_hover(btn_import, is_primary=True)
        
        btn_import_dir = tk.Button(file_ops, text="Import Folder...", command=self.import_folder, bg=self.accent_color,
                                   fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover)
        btn_import_dir.pack(side="left", padx=5)
        self.bind_hover(btn_import_dir, is_primary=True)
        
        btn_open = tk.Button(file_ops, text="Open Folder Location", command=self.open_folder, bg=self.card_color,
                             fg=self.text_color, relief="flat", activebackground=self.border_color)
        btn_open.pack(side="left", padx=5)
        self.bind_hover(btn_open)
        
        # 3. Log / Console Panel
        log_label = ttk.Label(main_frame, text="Console Log", font=("Segoe UI", 10, "bold"), foreground=self.accent_color)
        log_label.pack(anchor="w", pady=(10, 2))
        
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill="x", side="bottom", expand=False)
        
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
        
        # Binds
        self.tree_mods.bind("<<TreeviewSelect>>", self.on_mod_selected)
        
        # Scan mods
        self.scan_mods()

    def update_loader_status_ui(self):
        status, color = self.check_loader_status()
        self.lbl_loader_status.config(text=status, foreground=color)

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
        sel = self.tree_mods.selection()
        selected_id = sel[0] if sel else None
        
        self.scan_mods()
        
        if selected_id and self.tree_mods.exists(selected_id):
            self.tree_mods.selection_set(selected_id)
            self.tree_mods.see(selected_id)
        else:
            self.clear_metadata_fields()
            self.tree_files.delete(*self.tree_files.get_children())
            self.lbl_mod_title.config(text="Selected Mod: <None>")
            
        self.log("Mod list refreshed.", "info")

    def scan_mods(self):
        self.tree_mods.delete(*self.tree_mods.get_children())
        if not self.mods_dir or not self.mods_disabled_dir:
            return
            
        mods = {}
        
        # 1. Scan enabled mods in mods folder (looking for tracking ffxmod / json files)
        try:
            for file in os.listdir(self.mods_dir):
                if file.endswith((".ffxmod", ".json")) and not file.startswith("modinfo"):
                    mod_id, _ = os.path.splitext(file)
                    # Load tracking metadata
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
                                # If it's already registered as enabled, skip it
                                if d in mods:
                                    continue
                                    
                                # Count files and calculate size
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
                        # Unregistered folder inside mods_disabled
                        if d not in mods:
                            mods[d] = {
                                "name": d,
                                "status": "Disabled",
                                "files": [],
                                "size": 0
                            }
        except Exception:
            pass
            
        # Populate Treeview
        for mod_id, info in mods.items():
            self.tree_mods.insert("", tk.END, iid=mod_id, values=(
                info["name"],
                info["status"],
                len(info["files"]),
                self.get_friendly_size(info["size"])
            ))

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
        sel = self.tree_mods.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a mod first.")
            return
            
        mod_id = sel[0]
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
            self.tree_mods.selection_set(mod_id)
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
            self.tree_mods.selection_set(mod_id)
        except Exception as e:
            self.log(f"Failed to create mod: {e}", "error")

    def delete_mod(self):
        sel = self.tree_mods.selection()
        if not sel:
            messagebox.showwarning("Warning", "No mod selected.")
            return
            
        mod_id = sel[0]
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete mod '{mod_id}' completely from your disk?\n\nThis will remove it from the repository and delete all its source files. This cannot be undone."):
            return
            
        # Disable first if enabled
        if self.get_mod_status(mod_id) == "Enabled":
            self.disable_mod_logic(mod_id)
            
        # Remove from mods_disabled repo
        mod_repo_path = os.path.join(self.mods_disabled_dir, mod_id)
        try:
            shutil.rmtree(mod_repo_path, ignore_errors=True)
            self.log(f"Deleted mod '{mod_id}' successfully.", "success")
            self.scan_mods()
        except Exception as e:
            self.log(f"Failed to delete mod folder: {e}", "error")

    def enable_mod(self):
        sel = self.tree_mods.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a mod to enable.")
            return
            
        mod_id = sel[0]
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
            self.tree_mods.selection_set(mod_id)
        except Exception as e:
            self.log(f"Failed to write tracking file: {e}", "error")

    def disable_mod(self):
        sel = self.tree_mods.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a mod to disable.")
            return
            
        mod_id = sel[0]
        if self.get_mod_status(mod_id) == "Disabled":
            messagebox.showinfo("Status", "Mod is already disabled.")
            return
            
        self.disable_mod_logic(mod_id)
        self.scan_mods()
        self.tree_mods.selection_set(mod_id)

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
        sel = self.tree_mods.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a mod project first.")
            return
            
        mod_id = sel[0]
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
            abs_path = os.path.abspath(fpath)
            rel_path = self.resolve_mod_relative_path(abs_path)
            
            if not rel_path:
                rel_path = filedialog.askstring(
                    "Relative Path Required",
                    f"Could not automatically resolve relative path for:\n{os.path.basename(abs_path)}\n\nPlease enter relative path under data folder (e.g. ffx/master/jppc/battle/kernel/item.bin):",
                    initialvalue=os.path.basename(abs_path),
                    parent=self.root
                )
                if not rel_path:
                    continue
                    
            rel_path = rel_path.replace("\\", "/")
            is_enabled = (self.get_mod_status(mod_id) == "Enabled")
            dest = os.path.join(self.mods_dir if is_enabled else mod_repo, rel_path)
            
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(abs_path, dest)
                if rel_path not in files_list:
                    files_list.append(rel_path)
                import_count += 1
                self.log(f"Imported '{rel_path}' into mod '{mod_id}'.", "success")
            except Exception as e:
                self.log(f"Failed to import {os.path.basename(abs_path)}: {e}", "error")
                messagebox.showerror("Error", f"Failed to import file:\n{e}")
                
        if import_count > 0:
            info["files"] = files_list
            try:
                with open(info_path, "w") as f:
                    f.write(encode_metadata(info))
                    
                # Clean up legacy JSON file
                if info_path != fallback_path and os.path.exists(fallback_path):
                    try:
                        os.remove(fallback_path)
                    except Exception:
                        pass
                    
                # If enabled, also sync size & files to active mods tracker
                if self.get_mod_status(mod_id) == "Enabled":
                    total_size = 0
                    for rel in files_list:
                        fpath = os.path.join(mod_repo, rel)
                        if os.path.exists(fpath):
                            total_size += os.path.getsize(fpath)
                            
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
            self.tree_mods.selection_set(mod_id)

    def import_folder(self):
        sel = self.tree_mods.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a mod project first.")
            return
            
        mod_id = sel[0]
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
        
        for fpath in all_files:
            abs_path = os.path.abspath(fpath)
            # 1. Try to resolve via game path logic
            rel_path = self.resolve_mod_relative_path(abs_path)
            
            # 2. Fallback: use relative path from the selected import folder itself
            if not rel_path:
                rel_path = os.path.relpath(abs_path, selected_dir)
                
            rel_path = rel_path.replace("\\", "/")
            is_enabled = (self.get_mod_status(mod_id) == "Enabled")
            dest = os.path.join(self.mods_dir if is_enabled else mod_repo, rel_path)
            
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(abs_path, dest)
                if rel_path not in files_list:
                    files_list.append(rel_path)
                import_count += 1
            except Exception as e:
                self.log(f"Failed to import {os.path.basename(abs_path)}: {e}", "error")
                
        if import_count > 0:
            info["files"] = files_list
            try:
                with open(info_path, "w") as f:
                    f.write(encode_metadata(info))
                    
                # Clean up legacy JSON file
                if info_path != fallback_path and os.path.exists(fallback_path):
                    try:
                        os.remove(fallback_path)
                    except Exception:
                        pass
                    
                # If enabled, also sync size & files to active mods tracker
                if self.get_mod_status(mod_id) == "Enabled":
                    total_size = 0
                    for rel in files_list:
                        fpath = os.path.join(mod_repo, rel)
                        if os.path.exists(fpath):
                            total_size += os.path.getsize(fpath)
                            
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
            self.tree_mods.selection_set(mod_id)

    def open_folder(self):
        sel = self.tree_mods.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a mod folder to open.")
            return
            
        mod_id = sel[0]
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

    def bind_hover(self, btn, is_primary=False):
        normal_bg = self.accent_color if is_primary else self.card_color
        hover_bg = self.accent_hover if is_primary else self.border_color
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))

    def bind_hover_color(self, btn, hover, normal):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal))

if __name__ == "__main__":
    root = tk.Tk()
    app = FFXModManagerGUI(root)
    root.mainloop()
