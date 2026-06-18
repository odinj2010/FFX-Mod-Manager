import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

class WalkthroughTab:
    def __init__(self, parent_frame, manager_gui):
        self.parent = parent_frame
        self.manager = manager_gui
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.plugin_dir, "overlay_config.json")
        self.guide_file = os.path.join(self.plugin_dir, "guide_data.json")
        
        # Borrow styling variables
        self.bg_color = self.manager.bg_color
        self.card_color = self.manager.card_color
        self.accent_color = self.manager.accent_color
        self.accent_hover = self.manager.accent_hover
        self.text_color = self.manager.text_color
        self.text_dim = self.manager.text_dim
        self.border_color = self.manager.border_color
        self.success_color = self.manager.success_color
        self.error_color = self.manager.error_color
        
        # State variables
        self.selected_zone_id = ""
        self.guide_data = self.load_guide_data()
        self.checklist_state = self.load_checklist_state()
        
        # HUD vars
        self.hud_position = tk.StringVar(value="Right-Half")
        self.hud_hotkey = tk.StringVar(value="F9")
        self.hud_opacity = tk.DoubleVar(value=0.85)
        self.hud_scale = tk.DoubleVar(value=1.0)
        self.load_overlay_config()
        
        self.create_widgets()
        self.populate_zones()
        if self.guide_data:
            self.select_zone(self.guide_data[0]["id"])
            
    def load_guide_data(self):
        if os.path.exists(self.guide_file):
            try:
                with open(self.guide_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.manager.log(f"Error loading walkthrough guide database: {e}", "error")
        return []

    def load_checklist_state(self):
        state_path = os.path.join(self.plugin_dir, "checklist_progress.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_checklist_state(self):
        state_path = os.path.join(self.plugin_dir, "checklist_progress.json")
        try:
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(self.checklist_state, f, indent=2)
        except Exception:
            pass

    def load_overlay_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.hud_position.set(cfg.get("position", "Right-Half"))
                self.hud_hotkey.set(cfg.get("hotkey_str", "F9"))
                self.hud_opacity.set(float(cfg.get("opacity", 0.85)))
                self.hud_scale.set(float(cfg.get("scale", 1.0)))
            except Exception:
                pass

    def save_overlay_config(self):
        cfg = {
            "position": self.hud_position.get(),
            "hotkey_str": self.hud_hotkey.get(),
            "opacity": round(self.hud_opacity.get(), 2),
            "scale": round(self.hud_scale.get(), 2),
            "hotkey_vk": self.get_vk_code(self.hud_hotkey.get())
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            self.manager.log("Walkthrough HUD settings saved successfully.", "success")
        except Exception as e:
            self.manager.log(f"Failed to save HUD config: {e}", "error")

    def get_vk_code(self, hotkey_str):
        mapping = {f"F{i}": 0x6F + i for i in range(1, 13)}
        return mapping.get(hotkey_str, 0x78)  # F9 default

    def create_widgets(self):
        main_layout = ttk.Panedwindow(self.parent, orient="horizontal")
        main_layout.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left Side - Zone selector & Config
        left_pane = ttk.Frame(main_layout, padding=5)
        main_layout.add(left_pane, weight=1)
        
        lbl_list = tk.Label(left_pane, text="📖 Walkthrough Sections", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.bg_color)
        lbl_list._is_title = True
        lbl_list.pack(anchor="w", pady=(0, 5))
        
        # Zone Listbox
        list_frame = ttk.Frame(left_pane)
        list_frame.pack(fill="both", expand=True)
        
        self.tree_zones = ttk.Treeview(list_frame, columns=("name",), show="headings", selectmode="browse")
        self.tree_zones.heading("name", text="Chapters / Locations")
        self.tree_zones.column("name", anchor="w")
        self.tree_zones.pack(side="left", fill="both", expand=True)
        
        scroll_z = ttk.Scrollbar(list_frame, command=self.tree_zones.yview)
        scroll_z.pack(side="right", fill="y")
        self.tree_zones.config(yscrollcommand=scroll_z.set)
        self.tree_zones.bind("<<TreeviewSelect>>", self.on_zone_selected)
        
        # HUD Settings Frame inside Left Pane
        hud_card = tk.LabelFrame(left_pane, text=" Transparent HUD Settings ", labelanchor="nw", bg=self.bg_color, fg=self.accent_color, font=("Segoe UI", 9, "bold"))
        hud_card.pack(fill="x", pady=(15, 0))
        self.overlay_card = hud_card
        
        self.grid_frame = tk.Frame(hud_card, bg=self.bg_color, padx=10, pady=10)
        self.grid_frame.pack(fill="x")
        
        tk.Label(self.grid_frame, text="Position:", bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, sticky="w", pady=4, padx=(0, 5))
        pos_cb = ttk.Combobox(self.grid_frame, textvariable=self.hud_position, values=["Left-Half", "Right-Half", "Top-Half", "Bottom-Half"], state="readonly", width=12)
        pos_cb.grid(row=0, column=1, sticky="w", pady=4, padx=(0, 15))
        
        tk.Label(self.grid_frame, text="Toggle Hotkey:", bg=self.bg_color, fg=self.text_color).grid(row=0, column=2, sticky="w", pady=4, padx=(0, 5))
        hk_cb = ttk.Combobox(self.grid_frame, textvariable=self.hud_hotkey, values=[f"F{i}" for i in range(1, 13)], state="readonly", width=8)
        hk_cb.grid(row=0, column=3, sticky="w", pady=4, padx=(0, 15))
        
        tk.Label(self.grid_frame, text="Opacity:", bg=self.bg_color, fg=self.text_color).grid(row=1, column=0, sticky="w", pady=4, padx=(0, 5))
        op_scale = tk.Scale(self.grid_frame, variable=self.hud_opacity, from_=0.1, to=1.0, resolution=0.05, orient="horizontal", showvalue=True, bg=self.bg_color, fg=self.text_color, highlightthickness=0, bd=0, length=100)
        op_scale.grid(row=1, column=1, sticky="w", pady=4, padx=(0, 15))
        
        tk.Label(self.grid_frame, text="HUD Scale:", bg=self.bg_color, fg=self.text_color).grid(row=1, column=2, sticky="w", pady=4, padx=(0, 5))
        sc_scale = tk.Scale(self.grid_frame, variable=self.hud_scale, from_=0.5, to=1.5, resolution=0.05, orient="horizontal", showvalue=True, bg=self.bg_color, fg=self.text_color, highlightthickness=0, bd=0, length=100)
        sc_scale.grid(row=1, column=3, sticky="w", pady=4, padx=(0, 15))
        
        self.btn_save_hud = tk.Button(self.grid_frame, text="💾 Save HUD", command=self.save_overlay_config, bg=self.accent_color, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover, padx=12, pady=4)
        self.btn_save_hud.grid(row=0, column=4, rowspan=2, padx=(15, 0), sticky="ns")
        self.manager.bind_hover(self.btn_save_hud, is_primary=True)
        
        # Right Side - Step instructions and checklist items
        right_pane = ttk.Frame(main_layout, padding=(10, 5, 0, 5))
        main_layout.add(right_pane, weight=2)
        
        self.lbl_zone_title = tk.Label(right_pane, text="Select a Chapter", font=("Segoe UI", 12, "bold"), fg=self.accent_color, bg=self.bg_color)
        self.lbl_zone_title._is_title = True
        self.lbl_zone_title.pack(anchor="w", pady=(0, 5))
        
        # Text instructions Box
        self.txt_guide = tk.Text(right_pane, wrap="word", bg="#0d0d0d", fg="#d1d5db", font=("Consolas", 10), bd=0, relief="flat", height=12)
        self.txt_guide.pack(fill="both", expand=True, pady=(0, 10))
        
        scroll_t = ttk.Scrollbar(right_pane, command=self.txt_guide.yview)
        scroll_t.pack(side="right", fill="y")
        self.txt_guide.config(yscrollcommand=scroll_t.set)
        
        # 100% Checklist items Frame
        chk_label = tk.Label(right_pane, text="100% Checklist Achievements", font=("Segoe UI", 10, "bold"), fg=self.accent_color, bg=self.bg_color)
        chk_label._is_title = True
        chk_label.pack(anchor="w", pady=2)
        
        self.chk_container = ttk.Frame(right_pane)
        self.chk_container.pack(fill="x", pady=(0, 5))
        
    def populate_zones(self):
        self.tree_zones.delete(*self.tree_zones.get_children())
        for zone in self.guide_data:
            self.tree_zones.insert("", tk.END, iid=zone["id"], values=(zone["name"],))

    def on_zone_selected(self, event=None):
        sel = self.tree_zones.selection()
        if sel:
            self.select_zone(sel[0])
            
    def select_zone(self, zone_id):
        self.selected_zone_id = zone_id
        
        # Find zone guide dict
        zone = next((z for z in self.guide_data if z["id"] == zone_id), None)
        if not zone:
            return
            
        self.lbl_zone_title.config(text=zone["name"])
        
        # Write steps
        self.txt_guide.config(state="normal")
        self.txt_guide.delete("1.0", tk.END)
        for step in zone["steps"]:
            self.txt_guide.insert(tk.END, step + "\n\n")
        self.txt_guide.config(state="disabled")
        
        # Re-render checklist checkboxes
        for widget in self.chk_container.winfo_children():
            widget.destroy()
            
        for idx, item in enumerate(zone["checklist"]):
            # Checklist item state tracking
            item_key = f"{zone_id}_{idx}"
            is_checked = self.checklist_state.get(item_key, False)
            
            chk_var = tk.BooleanVar(value=is_checked)
            
            def on_chk_toggle(var=chk_var, k=item_key):
                self.checklist_state[k] = var.get()
                self.save_checklist_state()
                
            cb = tk.Checkbutton(self.chk_container, text=item, variable=chk_var, command=on_chk_toggle,
                                bg=self.bg_color, fg=self.text_color, activebackground=self.bg_color, activeforeground=self.text_color, selectcolor=self.card_color)
            cb.pack(anchor="w", pady=2)

    def on_game_launch(self, pid):
        pass

    def on_game_close(self):
        pass

    def retheme(self):
        self.bg_color = self.manager.bg_color
        self.card_color = self.manager.card_color
        self.accent_color = self.manager.accent_color
        self.accent_hover = self.manager.accent_hover
        self.text_color = self.manager.text_color
        self.text_dim = self.manager.text_dim
        self.border_color = self.manager.border_color
        self.success_color = self.manager.success_color
        self.error_color = self.manager.error_color
        
        if hasattr(self, "overlay_card") and self.overlay_card:
            self.overlay_card.configure(bg=self.bg_color, fg=self.accent_color)
            self.grid_frame.configure(bg=self.bg_color)
            for widget in self.grid_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg=self.bg_color, fg=self.text_color)
                elif isinstance(widget, tk.Scale):
                    widget.configure(bg=self.bg_color, fg=self.text_color, activebackground=self.accent_hover)
            self.btn_save_hud.configure(bg=self.accent_color, fg="white", activebackground=self.accent_hover)
            
        if hasattr(self, "txt_guide") and self.txt_guide:
            self.txt_guide.configure(
                bg="#0d0d0d" if self.bg_color != "#f3f4f6" else "#ffffff", 
                fg="#d1d5db" if self.bg_color != "#f3f4f6" else "#111827"
            )
            
        if self.selected_zone_id:
            self.select_zone(self.selected_zone_id)
