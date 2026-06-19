import os
import json
import tkinter as tk
from tkinter import ttk

class SceneSkipperTab:
    def __init__(self, parent_frame, manager_gui):
        self.parent = parent_frame
        self.manager = manager_gui
        
        # Borrow styling variables
        self.bg_color = self.manager.bg_color
        self.card_color = self.manager.card_color
        self.accent_color = self.manager.accent_color
        self.accent_hover = self.manager.accent_hover
        self.text_color = self.manager.text_color
        self.text_dim = self.manager.text_dim
        self.border_color = self.manager.border_color
        self.success_color = self.manager.success_color
        
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.plugin_dir, "overlay_config.json")
        
        # Load defaults from plugin.json
        manifest_file = os.path.join(self.plugin_dir, "plugin.json")
        default_hk = "F7"
        if os.path.exists(manifest_file):
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    default_hk = json.load(f).get("default_hotkey", "F7")
            except Exception:
                pass

        # Configuration variables
        self.hud_hotkey = tk.StringVar(value=default_hk)
        self.skip_key = tk.StringVar(value="Backspace")
        self.fast_forward_speed = tk.StringVar(value="8x")
        self.load_overlay_config()
        
        self.create_widgets()

    def load_overlay_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.hud_hotkey.set(cfg.get("hotkey_str", "F7"))
                self.skip_key.set(cfg.get("skip_key", "Backspace"))
                self.fast_forward_speed.set(cfg.get("speed", "8x"))
            except Exception:
                pass

    def save_overlay_config(self):
        cfg = {
            "hotkey_str": self.hud_hotkey.get(),
            "skip_key": self.skip_key.get(),
            "speed": self.fast_forward_speed.get(),
            "hotkey_vk": self.get_vk_code(self.hud_hotkey.get()),
            "skip_key_vk": self.get_skip_vk_code(self.skip_key.get())
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            self.manager.log("Scene Skipper settings saved successfully.", "success")
        except Exception as e:
            self.manager.log(f"Failed to save Scene Skipper config: {e}", "error")

    def get_vk_code(self, hotkey_str):
        mapping = {f"F{i}": 0x6F + i for i in range(1, 13)}
        return mapping.get(hotkey_str, 0x76)  # F7 default

    def get_skip_vk_code(self, key_str):
        mapping = {
            "Backspace": 0x08,
            "Spacebar": 0x20,
            "Enter": 0x0D,
            "Tab": 0x09,
            "Escape": 0x1B,
            "F6": 0x75,
            "F7": 0x76,
            "F8": 0x77,
            "F9": 0x78
        }
        return mapping.get(key_str, 0x08)  # Backspace default

    def retheme(self):
        # Dynamically reload styling variables from main manager
        self.bg_color = self.manager.bg_color
        self.card_color = self.manager.card_color
        self.accent_color = self.manager.accent_color
        self.accent_hover = self.manager.accent_hover
        self.text_color = self.manager.text_color
        self.text_dim = self.manager.text_dim
        self.border_color = self.manager.border_color
        self.success_color = self.manager.success_color
        
        # Redraw or update configuration container elements
        if hasattr(self, "settings_panel"):
            self.settings_panel.configure(bg=self.card_color, highlightbackground=self.border_color)
        if hasattr(self, "lbl_title"):
            self.lbl_title.configure(fg=self.accent_color, bg=self.bg_color)
        if hasattr(self, "lbl_desc"):
            self.lbl_desc.configure(fg=self.text_color, bg=self.bg_color)
        
        # Re-apply color themes recursively to settings labels
        self.manager.update_widget_colors(self.parent)

    def create_widgets(self):
        # Title & Info
        self.lbl_title = tk.Label(self.parent, text="⏩ Scene Skipper Settings", font=("Segoe UI", 14, "bold"), fg=self.accent_color, bg=self.bg_color)
        self.lbl_title._is_title = True
        self.lbl_title.pack(anchor="w", pady=(10, 5))
        
        self.lbl_desc = tk.Label(self.parent, text="Configure how the Scene Skipper operates. Pause the game during a cutscene, then press the configured Skip Key to fly through the scene at high speed.", font=("Segoe UI", 10, "italic"), fg=self.text_color, bg=self.bg_color, justify="left", wraplength=700)
        self.lbl_desc.pack(anchor="w", pady=(0, 20))
        
        # Settings Card Frame
        self.settings_panel = tk.Frame(self.parent, bd=1, relief="solid", highlightthickness=0, bg=self.card_color, padx=20, pady=20)
        self.settings_panel._is_card = True
        self.settings_panel.pack(fill="x", pady=5)
        
        # 1. Hotkey setting
        row1 = ttk.Frame(self.settings_panel)
        row1.pack(fill="x", pady=8)
        lbl_hk = tk.Label(row1, text="Toggle Skipper Overlay/Status Key:", font=("Segoe UI", 10), fg=self.text_color, bg=self.card_color)
        lbl_hk.pack(side="left", padx=(0, 15))
        
        hk_combo = ttk.Combobox(row1, textvariable=self.hud_hotkey, values=[f"F{i}" for i in range(1, 13)], state="readonly", width=10)
        hk_combo.pack(side="left")
        
        # 2. Skip key setting
        row2 = ttk.Frame(self.settings_panel)
        row2.pack(fill="x", pady=8)
        lbl_skip = tk.Label(row2, text="Cutscene Skip Trigger Key (while paused):", font=("Segoe UI", 10), fg=self.text_color, bg=self.card_color)
        lbl_skip.pack(side="left", padx=(0, 15))
        
        skip_combo = ttk.Combobox(row2, textvariable=self.skip_key, values=["Backspace", "Spacebar", "Enter", "Tab", "Escape"], state="readonly", width=15)
        skip_combo.pack(side="left")
        
        # 3. Speed multiplier setting
        row3 = ttk.Frame(self.settings_panel)
        row3.pack(fill="x", pady=8)
        lbl_speed = tk.Label(row3, text="Skip Fast-Forward Speed:", font=("Segoe UI", 10), fg=self.text_color, bg=self.card_color)
        lbl_speed.pack(side="left", padx=(0, 15))
        
        speed_combo = ttk.Combobox(row3, textvariable=self.fast_forward_speed, values=["2x", "4x", "8x", "16x"], state="readonly", width=10)
        speed_combo.pack(side="left")
        
        # Save Button
        btn_save = tk.Button(self.settings_panel, text="💾 Save Configuration", bg=self.accent_color, fg="white",
                             font=("Segoe UI", 10, "bold"), relief="flat", activebackground=self.accent_hover, padx=15, pady=6,
                             command=self.save_overlay_config)
        btn_save._is_primary = True
        btn_save.pack(anchor="w", pady=(20, 0))
        
        self.manager.bind_hover(btn_save, is_primary=True)
        self.manager.update_widget_colors(self.parent)
