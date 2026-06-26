import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import urllib.request
import zipfile
import re
import ctypes

# Retrieve ToolTip class from parent manager's modules to prevent import failures
ToolTip = None
if 'tooltip' in sys.modules:
    ToolTip = getattr(sys.modules['tooltip'], 'ToolTip', None)
if not ToolTip:
    try:
        from tooltip import ToolTip
    except ImportError:
        class ToolTip:
            def __init__(self, *args, **kwargs):
                pass

class ToolkitTab:
    def __init__(self, parent_frame, manager_gui):
        self.parent = parent_frame
        self.manager = manager_gui
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.plugin_dir, "toolkit_config.json")
        
        # Get SpiraMM directory path dynamically
        self.manager_dir = os.path.dirname(os.path.dirname(self.plugin_dir))
        
        # Setup tools list
        self.community_tools = {
            "vbf_browser": {"name": "VBF Browser", "desc": "Native tool to unpack, inspect, and patch main game VBF archives."},
            "ffxed": {"name": "FFXED Save Editor", "desc": "Comprehensive save file modifier for Final Fantasy X."},
            "checksum": {"name": "MemorySumChecker", "desc": "Verifies and corrects save game checksums to prevent corruption errors."},
            "farplane": {"name": "Farplane", "desc": "Live memory editor, trainer, and visual data viewer for FFX/FFX-2."}
        }
        
        self.custom_tools = {
            "text": {
                "name": "FFX Text Tool",
                "folder": "FFX-Text-Tool",
                "script": "FFX_Text_Tool.py",
                "exe": "FFX_Text_Tool.exe",
                "desc": "Browse, search, edit, and re-import text strings from the game script.",
                "download_url": "https://github.com/odinj2010/FFX-Text-Tool/releases/latest/download/FFX_Text_Tool.zip"
            },
            "sphere": {
                "name": "FFX Sphere Grid Tool",
                "folder": "FFX-Sphere-Grid-Tool",
                "script": "FFX_Sphere_Grid_Tool.py",
                "exe": "FFX_Sphere_Grid_Tool.exe",
                "desc": "Edit sphere grid node properties, item paths, and character starting positions.",
                "download_url": "https://github.com/odinj2010/FFX-Sphere-Grid-Tool/releases/latest/download/FFX-Sphere-Grid-Tool.zip"
            },
            "shop": {
                "name": "FFX Shop Tool",
                "folder": "FFX-Shop-Tool",
                "script": "FFX_Shop_Tool.py",
                "exe": "FFX_Shop_Tool.exe",
                "desc": "Modify shop inventories, prices, items, and unlock triggers.",
                "download_url": "https://github.com/odinj2010/FFX-Shop-Tool/releases/latest/download/FFX-Shop-Tool.zip"
            },
            "phyre": {
                "name": "FFX Phyre Tool",
                "folder": "FFX-Phyre-Tool",
                "script": "FFX_Phyre_Tool.py",
                "exe": "FFX_Phyre_Tool.exe",
                "desc": "Extract and re-pack 3D models and Phyre engine textures.",
                "download_url": "https://github.com/odinj2010/FFX-Phyre-Tool/releases/latest/download/FFX_Phyre_Tool.zip"
            },
            "audio": {
                "name": "FFX Audio Tool",
                "folder": "FFX-Audio-Tool",
                "script": "FFX_Audio_Tool.py",
                "exe": "FFX_Audio_Tool.exe",
                "desc": "Convert, replace, and edit game voice lines, sound effects, and music.",
                "download_url": "https://github.com/odinj2010/FFX-Audio-Tool/releases/latest/download/FFX-Audio-Tool.zip"
            },
            "ai": {
                "name": "FFX AI Tool",
                "folder": "FFX_AI_Tool",
                "script": "FFX_AI_Tool.py",
                "exe": "FFX_AI_Tool.exe",
                "desc": "Edit enemy AI scripts, combat routines, and behaviors.",
                "download_url": "https://github.com/odinj2010/FFX_AI_Tool/releases/latest/download/FFX_AI_Tool.zip"
            }
        }
        
        # Paths dict configured by user or auto-detected
        self.tool_paths = {}
        self.tool_versions = {}
        self.tool_updates_available = {}
        self.load_config()
        self.auto_detect_custom_tools()
        
        # UI Tracking Collections for retargeting themes
        self.canvases = []
        self.headers = []
        self.header_labels = []
        self.cards = []
        self.card_headers = []
        self.lbl_names = []
        self.lbl_descs = []
        self.lbl_paths = []
        self.launch_buttons = {}
        self.browse_buttons = {}
        self.update_buttons = {}
        self.download_buttons = {}
        self.tool_status_labels = {}
        self.tool_path_labels = {}
        
        # Set default colors
        self.bg_color = "#121212"
        self.card_color = "#1e1e1e"
        self.accent_color = "#00ffcc"
        self.accent_hover = "#33ffdd"
        self.text_color = "#ffffff"
        self.text_dim = "#aaaaaa"
        self.border_color = "#333333"
        self.success_color = "#10b981"
        self.error_color = "#ef4444"
        
        # Build UI layout
        self.frame = tk.Frame(self.parent, bg=self.bg_color)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.left_col = tk.Frame(self.frame, bg=self.bg_color)
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.right_col = tk.Frame(self.frame, bg=self.bg_color)
        self.right_col.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        self.build_section(self.left_col, "Community Utilities", self.community_tools, is_custom=False)
        self.build_section(self.right_col, "My Custom Tools", self.custom_tools, is_custom=True)
        
        self.retheme()
        
        # Check for tool updates asynchronously
        threading.Thread(target=self.check_for_tool_updates, daemon=True).start()
        
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    if "paths" in config:
                        self.tool_paths = config["paths"]
                        self.tool_versions = config.get("versions", {})
                    else:
                        # Legacy format support
                        self.tool_paths = config
                        self.tool_versions = {}
            except Exception:
                self.tool_paths = {}
                self.tool_versions = {}
                
    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump({
                    "paths": self.tool_paths,
                    "versions": self.tool_versions
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving toolkit config: {e}")

    def find_executable(self, folder_path, exe_name):
        for root, dirs, files in os.walk(folder_path):
            if exe_name in files:
                return os.path.join(root, exe_name)
        return None

    def get_exe_version(self, path):
        try:
            size = ctypes.windll.version.GetFileVersionInfoSizeW(path, None)
            if size == 0:
                return None
            buffer = ctypes.create_string_buffer(size * 2)
            if not ctypes.windll.version.GetFileVersionInfoW(path, None, size, buffer):
                return None
            
            # Try reading StringFileInfo version first (it holds actual project version strings like 2.2.0.0)
            fixed_info_ptr = ctypes.c_void_p()
            fixed_info_size = ctypes.c_uint()
            
            if ctypes.windll.version.VerQueryValueW(
                buffer,
                "\\VarFileInfo\\Translation",
                ctypes.byref(fixed_info_ptr),
                ctypes.byref(fixed_info_size)
            ) and fixed_info_size.value >= 4:
                trans = ctypes.cast(fixed_info_ptr.value, ctypes.POINTER(ctypes.c_uint16))
                lang = trans[0]
                codepage = trans[1]
                
                # Check ProductVersion first, then FileVersion string
                for key in ["ProductVersion", "FileVersion"]:
                    sub_block = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\{key}"
                    str_ptr = ctypes.c_void_p()
                    str_size = ctypes.c_uint()
                    if ctypes.windll.version.VerQueryValueW(
                        buffer,
                        sub_block,
                        ctypes.byref(str_ptr),
                        ctypes.byref(str_size)
                    ) and str_ptr.value:
                        val = ctypes.wstring_at(str_ptr.value).strip()
                        if val:
                            return val

            # Fallback to FixedFileInfo dwFileVersionMS/LS
            fixed_info_ptr = ctypes.c_void_p()
            fixed_info_size = ctypes.c_uint()
            if not ctypes.windll.version.VerQueryValueW(
                buffer,
                "\\",
                ctypes.byref(fixed_info_ptr),
                ctypes.byref(fixed_info_size)
            ):
                return None
            if fixed_info_size.value < 20:
                return None
            ms = ctypes.cast(fixed_info_ptr.value + 8, ctypes.POINTER(ctypes.c_uint32)).contents.value
            ls = ctypes.cast(fixed_info_ptr.value + 12, ctypes.POINTER(ctypes.c_uint32)).contents.value
            return f"{ms >> 16}.{ms & 0xffff}.{ls >> 16}.{ls & 0xffff}"
        except Exception as e:
            print(f"Error reading exe version: {e}")
            return None

    def get_py_version(self, path):
        folder = os.path.dirname(path)
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith("_version.txt"):
                    version_file = os.path.join(folder, f)
                    try:
                        with open(version_file, "r", encoding="utf-8") as file:
                            content = file.read()
                            m = re.search(r"ProductVersion',\s*u?'([^']+)'", content)
                            if not m:
                                m = re.search(r'ProductVersion",\s*u?"([^"]+)"', content)
                            if m:
                                return m.group(1)
                            m = re.search(r"FileVersion',\s*u?'([^']+)'", content)
                            if not m:
                                m = re.search(r'FileVersion",\s*u?"([^"]+)"', content)
                            if m:
                                return m.group(1)
                    except Exception:
                        pass
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    m = re.search(r"^(?:__version__|VERSION)\s*=\s*['\"]([^'\"]+)['\"]", line)
                    if m:
                        return m.group(1)
        except Exception:
            pass
        return None

    def extract_tool_version(self, path):
        if not path or not os.path.exists(path):
            return None
        if path.endswith(".exe"):
            return self.get_exe_version(path)
        elif path.endswith(".py"):
            return self.get_py_version(path)
        return None

    def auto_detect_custom_tools(self):
        # 1. First, verify configured paths are still valid
        for tid in list(self.tool_paths.keys()):
            if not os.path.exists(self.tool_paths[tid]):
                del self.tool_paths[tid]
                if tid in self.tool_versions:
                    del self.tool_versions[tid]

        # 2. Check local plugin bin folder (Self-contained zip installation path)
        for tid, tool in self.custom_tools.items():
            if tid in self.tool_paths:
                continue
            bin_dir = os.path.join(self.plugin_dir, "bin", tid)
            if os.path.exists(bin_dir):
                exe_path = self.find_executable(bin_dir, tool["exe"])
                if exe_path:
                    self.tool_paths[tid] = os.path.abspath(exe_path)
                    continue

        # 3. Fallback: Check parent dev folder structure
        parent_dir = os.path.dirname(self.manager_dir)
        for tid, tool in self.custom_tools.items():
            if tid in self.tool_paths:
                continue
            tool_folder = os.path.join(parent_dir, tool["folder"])
            # Fallback for folder naming conventions (e.g. FFX_AI_Tool vs FFX-AI-Tool)
            if not os.path.exists(tool_folder):
                alt_folder = tool["folder"].replace("_", "-") if "_" in tool["folder"] else tool["folder"].replace("-", "_")
                tool_folder = os.path.join(parent_dir, alt_folder)
                
            if os.path.exists(tool_folder):
                exe_path = os.path.join(tool_folder, "dist", tool["exe"])
                if os.path.exists(exe_path):
                    self.tool_paths[tid] = os.path.abspath(exe_path)
                    continue
                py_path = os.path.join(tool_folder, tool["script"])
                if os.path.exists(py_path):
                    self.tool_paths[tid] = os.path.abspath(py_path)
                    continue

        # 4. Resolve versions for all discovered tools
        for tid in self.tool_paths:
            version = self.extract_tool_version(self.tool_paths[tid])
            if version:
                self.tool_versions[tid] = version

        # Always save configuration to migrate structure on startup
        self.save_config()

    def check_for_tool_updates(self):
        for tid, tool in self.custom_tools.items():
            path = self.tool_paths.get(tid, "")
            if not path or not os.path.exists(path):
                continue
                
            bin_dir = os.path.join(self.plugin_dir, "bin", tid)
            # Only check updates for self-contained installations
            if not path.startswith(os.path.abspath(bin_dir)):
                continue
                
            try:
                url = f"https://api.github.com/repos/odinj2010/{tool['folder']}/releases/latest"
                req = urllib.request.Request(url, headers={"User-Agent": "SpiraMM-Toolkit-Plugin"})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    latest_tag = data.get("tag_name", "")
                    
                installed_version = self.tool_versions.get(tid, "v0.0.0")
                if latest_tag and latest_tag != installed_version:
                    self.tool_updates_available[tid] = latest_tag
                    # Refresh UI for this tool on main thread
                    self.frame.after(0, self.update_tool_ui, tid, True)
            except Exception as e:
                print(f"Error checking update for {tid}: {e}")

    def build_section(self, parent, title, tools_dict, is_custom=False):
        header_frame = tk.Frame(parent, bg=self.card_color, highlightbackground=self.border_color, highlightthickness=1)
        header_frame.pack(fill="x", pady=(0, 10))
        self.headers.append(header_frame)
        
        lbl_title = tk.Label(header_frame, text=title, font=("Helvetica", 14, "bold"), bg=self.card_color, fg=self.accent_color)
        lbl_title.pack(anchor="w", padx=15, pady=10)
        self.header_labels.append(lbl_title)
        
        container_outer = tk.Frame(parent, bg=self.bg_color)
        container_outer.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(container_outer, bg=self.bg_color, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container_outer, orient="vertical", command=canvas.yview)
        self.canvases.append(canvas)
        
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _configure_canvas_width(event, c=canvas, wid=window_id):
            c.itemconfig(wid, width=event.width)
        canvas.bind("<Configure>", _configure_canvas_width)
        
        def _on_mousewheel(event, c=canvas):
            c.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def bind_mouse(event, c=canvas):
            c.bind_all("<MouseWheel>", lambda e, cv=c: _on_mousewheel(e, cv))
        def unbind_mouse(event, c=canvas):
            c.unbind_all("<MouseWheel>")
            
        canvas.bind("<Enter>", bind_mouse)
        canvas.bind("<Leave>", unbind_mouse)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for tid, tool in tools_dict.items():
            card = tk.Frame(scrollable_frame, bg=self.card_color, highlightbackground=self.border_color, highlightthickness=1)
            card.pack(fill="x", pady=5, padx=2)
            self.cards.append(card)
            
            row_header = tk.Frame(card, bg=self.card_color)
            row_header.pack(fill="x", padx=12, pady=(8, 2))
            self.card_headers.append(row_header)
            
            lbl_name = tk.Label(row_header, text=tool["name"], font=("Helvetica", 11, "bold"), bg=self.card_color, fg=self.text_color)
            lbl_name.pack(side="left")
            self.lbl_names.append(lbl_name)
            
            status_var = tk.StringVar()
            lbl_status = tk.Label(row_header, textvariable=status_var, font=("Helvetica", 9, "italic"), bg=self.card_color)
            lbl_status.pack(side="right")
            self.tool_status_labels[tid] = (lbl_status, status_var)
            
            lbl_desc = tk.Label(card, text=tool["desc"], font=("Helvetica", 9), bg=self.card_color, fg=self.text_dim, justify="left", anchor="w", wraplength=280)
            lbl_desc.pack(fill="x", padx=12, pady=2)
            self.lbl_descs.append(lbl_desc)
            
            path_var = tk.StringVar()
            lbl_path = tk.Label(card, textvariable=path_var, font=("Courier", 8), bg=self.card_color, fg=self.text_dim, justify="left", anchor="w", wraplength=280)
            lbl_path.pack(fill="x", padx=12, pady=2)
            self.tool_path_labels[tid] = path_var
            self.lbl_paths.append(lbl_path)
            
            row_actions = tk.Frame(card, bg=self.card_color)
            row_actions.pack(fill="x", padx=12, pady=(2, 8))
            
            btn_launch = tk.Button(row_actions, text="Launch", font=("Helvetica", 9, "bold"), bg=self.accent_color, fg="#000000", activebackground=self.accent_hover, activeforeground="#000000", bd=0, padx=12, pady=4, cursor="hand2")
            btn_launch.pack(side="left")
            self.launch_buttons[tid] = btn_launch
            
            if is_custom:
                btn_update = tk.Button(row_actions, text="Update", font=("Helvetica", 9, "bold"), bg="#ffaa00", fg="#000000", activebackground="#ffbb11", activeforeground="#000000", bd=0, padx=12, pady=4, cursor="hand2")
                self.update_buttons[tid] = btn_update
                btn_update.configure(command=lambda t=tid, b=btn_update: self.start_update(t, b))
            
            btn_browse = tk.Button(row_actions, text="Browse", font=("Helvetica", 9), bg=self.bg_color, fg=self.text_color, activebackground=self.border_color, activeforeground=self.text_color, bd=1, highlightbackground=self.border_color, padx=10, pady=3, cursor="hand2")
            btn_browse.pack(side="right", padx=(5, 0))
            self.browse_buttons[tid] = btn_browse
            
            btn_launch.configure(command=lambda t=tid, ic=is_custom, bl=btn_launch: self.launch_tool(t, ic, bl))
            btn_browse.configure(command=lambda t=tid, ic=is_custom: self.browse_path(t, ic))
            
            if is_custom:
                self.download_buttons[tid] = btn_launch

    def retheme(self):
        self.bg_color = getattr(self.manager, "bg_color", "#121212")
        self.card_color = getattr(self.manager, "card_color", "#1e1e1e")
        self.accent_color = getattr(self.manager, "accent_color", "#00ffcc")
        self.accent_hover = getattr(self.manager, "accent_hover", "#33ffdd")
        self.text_color = getattr(self.manager, "text_color", "#ffffff")
        self.text_dim = getattr(self.manager, "text_dim", "#aaaaaa")
        self.border_color = getattr(self.manager, "border_color", "#333333")
        self.success_color = getattr(self.manager, "success_color", "#10b981")
        self.error_color = getattr(self.manager, "error_color", "#ef4444")
        
        if hasattr(self, "frame") and self.frame:
            self.frame.configure(bg=self.bg_color)
            self.left_col.configure(bg=self.bg_color)
            self.right_col.configure(bg=self.bg_color)
            
        for c in self.canvases:
            c.configure(bg=self.bg_color)
            
        for h in self.headers:
            h.configure(bg=self.card_color, highlightbackground=self.border_color)
            
        for hl in self.header_labels:
            hl.configure(bg=self.card_color, fg=self.accent_color)
            
        for cd in self.cards:
            cd.configure(bg=self.card_color, highlightbackground=self.border_color)
            
        for ch in self.card_headers:
            ch.configure(bg=self.card_color)
            
        for n in self.lbl_names:
            n.configure(bg=self.card_color, fg=self.text_color)
            
        for d in self.lbl_descs:
            d.configure(bg=self.card_color, fg=self.text_dim)
            
        for p in self.lbl_paths:
            p.configure(bg=self.card_color, fg=self.text_dim)
            
        for tid, btn in self.launch_buttons.items():
            path = self.tool_paths.get(tid, "")
            is_custom = tid in self.custom_tools
            if is_custom and (not path or not os.path.exists(path)):
                btn.configure(bg="#ffaa00", fg="#000000", activebackground="#ffbb11", activeforeground="#000000")
            else:
                btn.configure(bg=self.accent_color, fg="#000000", activebackground=self.accent_hover, activeforeground="#000000")
                
        for btn in self.browse_buttons.values():
            btn.configure(bg=self.bg_color, fg=self.text_color, activebackground=self.border_color, activeforeground=self.text_color, highlightbackground=self.border_color)
            
        for tid in self.community_tools:
            self.update_tool_ui(tid, is_custom=False)
        for tid in self.custom_tools:
            self.update_tool_ui(tid, is_custom=True)

    def update_tool_ui(self, tid, is_custom):
        lbl_status, status_var = self.tool_status_labels[tid]
        path_var = self.tool_path_labels[tid]
        
        # Hide update button by default
        if tid in self.update_buttons:
            self.update_buttons[tid].pack_forget()
            
        path = self.tool_paths.get(tid, "")
        if path and os.path.exists(path):
            installed_ver = self.tool_versions.get(tid, "")
            
            if is_custom and tid in self.tool_updates_available:
                latest_ver = self.tool_updates_available[tid]
                status_var.set(f"Update Available ({installed_ver} -> {latest_ver})")
                lbl_status.configure(fg="#ffaa00", bg=self.card_color)
                if tid in self.update_buttons:
                    self.update_buttons[tid].pack(side="left", padx=(8, 0))
            else:
                if is_custom and installed_ver:
                    status_var.set(f"Ready ({installed_ver})")
                else:
                    status_var.set("Ready")
                lbl_status.configure(fg=self.success_color, bg=self.card_color)
                
            display_path = path if len(path) < 40 else "..." + path[-37:]
            path_var.set(display_path)
            
            if is_custom and tid in self.download_buttons:
                self.download_buttons[tid].configure(text="Launch", state="normal", bg=self.accent_color)
        else:
            path_var.set("Not Configured")
            if is_custom:
                status_var.set("Not Downloaded")
                lbl_status.configure(fg=self.error_color, bg=self.card_color)
                if tid in self.download_buttons:
                    self.download_buttons[tid].configure(text="Download", state="normal", bg="#ffaa00")
            else:
                status_var.set("Not Configured")
                lbl_status.configure(fg=self.error_color, bg=self.card_color)

    def browse_path(self, tid, is_custom):
        initial_dir = os.path.dirname(self.manager_dir) if is_custom else "/"
        file_types = [("Executables & Scripts", "*.exe;*.py"), ("All Files", "*.*")]
        
        path = filedialog.askopenfilename(
            title=f"Select path for {self.community_tools[tid]['name'] if not is_custom else self.custom_tools[tid]['name']}",
            initialdir=initial_dir,
            filetypes=file_types
        )
        if path:
            self.tool_paths[tid] = os.path.abspath(path)
            # Resolve and save version dynamically from manual selection
            version = self.extract_tool_version(path)
            if version:
                self.tool_versions[tid] = version
            elif tid in self.tool_versions:
                del self.tool_versions[tid]
            self.save_config()
            self.update_tool_ui(tid, is_custom)

    def launch_tool(self, tid, is_custom, btn_obj):
        path = self.tool_paths.get(tid, "")
        
        if is_custom and (not path or not os.path.exists(path)):
            self.start_download(tid, btn_obj)
            return
            
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Tool path is not configured or the target file does not exist. Please browse to the file first.")
            return
            
        try:
            working_dir = os.path.dirname(path)
            if path.endswith(".py"):
                subprocess.Popen([sys.executable, path], cwd=working_dir, creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
            else:
                subprocess.Popen([path], cwd=working_dir, creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
        except Exception as e:
            messagebox.showerror("Launch Failed", f"Failed to launch tool:\n{e}")

    def start_download(self, tid, btn_obj):
        btn_obj.configure(text="Downloading...", state="disabled", bg=self.border_color)
        lbl_status, status_var = self.tool_status_labels[tid]
        status_var.set("Downloading zip...")
        lbl_status.configure(fg="#ffaa00")
        
        threading.Thread(target=self.run_download_and_extract, args=(tid, False), daemon=True).start()

    def start_update(self, tid, btn_obj):
        btn_obj.configure(text="Updating...", state="disabled", bg=self.border_color)
        lbl_status, status_var = self.tool_status_labels[tid]
        status_var.set("Updating tool...")
        lbl_status.configure(fg="#ffaa00")
        
        threading.Thread(target=self.run_download_and_extract, args=(tid, True), daemon=True).start()

    def run_download_and_extract(self, tid, is_update=False):
        tool = self.custom_tools[tid]
        url = tool["download_url"]
        
        latest_tag = "v1.0.0"
        try:
            api_url = f"https://api.github.com/repos/odinj2010/{tool['folder']}/releases/latest"
            req = urllib.request.Request(api_url, headers={"User-Agent": "SpiraMM-Toolkit-Plugin"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_tag = data.get("tag_name", "v1.0.0")
        except Exception:
            if tid in self.tool_updates_available:
                latest_tag = self.tool_updates_available[tid]
        
        bin_dir = os.path.join(self.plugin_dir, "bin", tid)
        os.makedirs(bin_dir, exist_ok=True)
        zip_path = os.path.join(bin_dir, "download.zip")
        
        success = False
        try:
            urllib.request.urlretrieve(url, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(bin_dir)
                
            if os.path.exists(zip_path):
                os.remove(zip_path)
                
            exe_path = self.find_executable(bin_dir, tool["exe"])
            if exe_path:
                self.tool_paths[tid] = os.path.abspath(exe_path)
                self.tool_versions[tid] = latest_tag
                if tid in self.tool_updates_available:
                    del self.tool_updates_available[tid]
                self.save_config()
                success = True
        except Exception as e:
            print(f"Error downloading/extracting tool {tid}: {e}")
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except Exception:
                    pass
            success = False
            
        self.frame.after(0, self.on_download_complete, tid, success, is_update)

    def on_download_complete(self, tid, success, is_update=False):
        self.update_tool_ui(tid, is_custom=True)
        tool = self.custom_tools[tid]
        action = "updated" if is_update else "downloaded"
        if success:
            messagebox.showinfo("Success", f"Successfully {action} and extracted {tool['name']}!")
        else:
            messagebox.showerror("Error", f"Failed to {action} or extract {tool['name']}.\nEnsure you have an internet connection.")
