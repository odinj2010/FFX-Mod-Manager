import os
import json
import tkinter as tk
from tkinter import ttk

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


class AchievementsTab:
    def __init__(self, parent_frame, manager_gui):
        self.parent = parent_frame
        self.manager = manager_gui
        self.save_file = os.path.join(self.manager.game_dir, "data", "custom_achievements.json") if self.manager.game_dir else ""
        
        # Borrow styling variables
        self.bg_color = self.manager.bg_color
        self.card_color = self.manager.card_color
        self.accent_color = self.manager.accent_color
        self.accent_hover = self.manager.accent_hover
        self.text_color = self.manager.text_color
        self.text_dim = self.manager.text_dim
        self.border_color = self.manager.border_color
        self.success_color = self.manager.success_color
        
        # State variables
        self.selected_category = "All"
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_view())
        
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load defaults from plugin.json
        manifest_file = os.path.join(self.plugin_dir, "plugin.json")
        default_hk = "F8"
        if os.path.exists(manifest_file):
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    default_hk = json.load(f).get("default_hotkey", "F8")
            except Exception:
                pass

        # HUD vars
        self.hud_position = tk.StringVar(value="Right-Half")
        self.hud_hotkey = tk.StringVar(value=default_hk)
        self.hud_opacity = tk.DoubleVar(value=0.85)
        self.hud_scale = tk.DoubleVar(value=1.0)
        self.load_overlay_config()
        
        # Load progress
        self.progress_data = self.load_progress()
        
        # Build layout
        self.create_widgets()
        self.refresh_view()

    def load_progress(self):
        if self.save_file and os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def load_overlay_config(self):
        if "plugin_settings" not in self.manager.config:
            self.manager.config["plugin_settings"] = {}
        if "achievements" not in self.manager.config["plugin_settings"]:
            self.manager.config["plugin_settings"]["achievements"] = {}
        p_cfg = self.manager.config["plugin_settings"]["achievements"]
        self.hud_position.set(p_cfg.get("position", "Right-Half"))
        self.hud_hotkey.set(p_cfg.get("hotkey", "F8"))
        self.hud_opacity.set(float(p_cfg.get("opacity", 0.85)))
        self.hud_scale.set(float(p_cfg.get("scale", 1.0)))

    def save_overlay_config(self):
        if "plugin_settings" not in self.manager.config:
            self.manager.config["plugin_settings"] = {}
        if "achievements" not in self.manager.config["plugin_settings"]:
            self.manager.config["plugin_settings"]["achievements"] = {}
        p_cfg = self.manager.config["plugin_settings"]["achievements"]
        p_cfg["position"] = self.hud_position.get()
        p_cfg["hotkey"] = self.hud_hotkey.get()
        p_cfg["opacity"] = str(round(self.hud_opacity.get(), 2))
        p_cfg["scale"] = str(round(self.hud_scale.get(), 2))
        self.manager.save_config()
        self.manager.broadcast_event("on_config_changed", "plugin_settings.achievements.position", p_cfg["position"])
        self.manager.broadcast_event("on_config_changed", "plugin_settings.achievements.hotkey", p_cfg["hotkey"])
        self.manager.broadcast_event("on_config_changed", "plugin_settings.achievements.opacity", p_cfg["opacity"])
        self.manager.broadcast_event("on_config_changed", "plugin_settings.achievements.scale", p_cfg["scale"])
        self.manager.log("Achievements HUD settings updated centrally.", "success")

    def get_vk_code(self, hotkey_str):
        mapping = {f"F{i}": 0x6F + i for i in range(1, 13)}
        return mapping.get(hotkey_str, 0x77)  # F8 default

    def create_widgets(self):
        # Create Notebook tab switcher inside self.parent
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Achievements Tab
        self.tab_achievements = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_achievements, text="🏆 Achievements")
        
        # Settings Tab
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙️ Settings")
        
        # Build Achievements Tab widgets
        self.create_achievements_tab_widgets()
        
        # Build Settings Tab widgets
        self.create_settings_tab_widgets()

    def create_achievements_tab_widgets(self):
        # Main container frame
        main_container = ttk.Frame(self.tab_achievements, padding=15)
        main_container.pack(fill="both", expand=True)
        
        # Top Panel: Header and Global Progress
        top_panel = ttk.Frame(main_container)
        top_panel.pack(fill="x", pady=(0, 15))
        
        lbl_title = tk.Label(top_panel, text="🏆 Custom Achievements", font=("Segoe UI", 14, "bold"), fg=self.accent_color, bg=self.bg_color)
        lbl_title._is_title = True
        lbl_title.pack(side="left", anchor="w")
        
        # Progress indicator
        self.lbl_progress = tk.Label(top_panel, text="0 / 0 Unlocked (0%)", font=("Segoe UI", 10, "bold"), fg=self.success_color, bg=self.bg_color)
        self.lbl_progress._is_diagnostic = True
        self.lbl_progress.pack(side="right", anchor="e", padx=(10, 0))
        
        self.progress_bar = ttk.Progressbar(main_container, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", pady=(0, 15))
        
        # Search & Filter Row
        control_row = ttk.Frame(main_container)
        control_row.pack(fill="x", pady=(0, 10))
        
        # Category Buttons
        categories = ["All", "Combat", "Minigames", "Collection"]
        self.cat_buttons = {}
        for cat in categories:
            btn = tk.Button(
                control_row, text=cat, 
                command=lambda c=cat: self.filter_category(c),
                bg=self.accent_color if cat == "All" else self.card_color,
                fg="white" if cat == "All" else self.text_color,
                font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=4
            )
            btn.pack(side="left", padx=(0, 5))
            self.cat_buttons[cat] = btn
            if cat != "All":
                self.manager.bind_hover(btn)
                
        # Search input
        lbl_search = tk.Label(control_row, text="Search:", fg=self.text_color, bg=self.bg_color)
        lbl_search.pack(side="left", padx=(20, 5))
        
        self.ent_search = ttk.Entry(control_row, textvariable=self.search_var, width=25)
        self.ent_search.pack(side="left", fill="x", expand=False)
        
        # Reload Button
        btn_reload = tk.Button(
            control_row, text="🔄 Reload", 
            command=self.reload_data,
            bg=self.card_color, fg=self.text_color,
            font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=4
        )
        btn_reload.pack(side="right", padx=(5, 0))
        self.manager.bind_hover(btn_reload)
        
        # Content Scrollable List
        list_container = ttk.Frame(main_container)
        list_container.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(list_container, bg=self.bg_color, highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        
        self.cards_frame = ttk.Frame(self.canvas)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        
        # Scroll binds
        def on_cards_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.cards_frame.bind("<Configure>", on_cards_configure)
        
        def on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind("<Configure>", on_canvas_configure)
        
        # Mousewheel
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
        def bind_mouse(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def unbind_mouse(event):
            self.canvas.unbind_all("<MouseWheel>")
            
        self.canvas.bind("<Enter>", bind_mouse)
        self.canvas.bind("<Leave>", unbind_mouse)

    def filter_category(self, cat):
        self.selected_category = cat
        for name, btn in self.cat_buttons.items():
            if name == cat:
                btn.config(bg=self.accent_color, fg="white")
                # Remove leave bind temporarily to keep accent background
                btn.unbind("<Leave>")
                btn.unbind("<Enter>")
            else:
                btn.config(bg=self.card_color, fg=self.text_color)
                # Rebind hover colors
                self.manager.bind_hover(btn)
        self.refresh_view()

    def reload_data(self):
        self.progress_data = self.load_progress()
        self.refresh_view()

    def refresh_view(self):
        # Clear cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
            
        search_query = self.search_var.get().lower().strip()
        unlocked_count = 0
        total_count = len(ACHIEVEMENTS)
        
        # Pre-filter achievements
        filtered_list = []
        for ach in ACHIEVEMENTS:
            is_unlocked = self.progress_data.get(ach["id"], {}).get("unlocked", False)
            if is_unlocked:
                unlocked_count += 1
                
            # Filter checks
            if self.selected_category != "All" and ach["category"] != self.selected_category:
                continue
            if self.selected_category == "Unlocked" and not is_unlocked:
                continue
            if self.selected_category == "Locked" and is_unlocked:
                continue
            if search_query and search_query not in ach["name"].lower() and search_query not in ach["description"].lower():
                continue
                
            filtered_list.append((ach, is_unlocked))
            
        # Update progress widgets
        pct = int((unlocked_count / total_count) * 100) if total_count > 0 else 0
        self.lbl_progress.config(text=f"🏆 {unlocked_count} / {total_count} Unlocked ({pct}%)")
        self.progress_bar.config(value=pct)
        
        # Render cards
        if not filtered_list:
            lbl_empty = tk.Label(self.cards_frame, text="No achievements found match criteria.", font=("Segoe UI", 10, "italic"), fg=self.text_dim, bg=self.bg_color)
            lbl_empty._is_muted = True
            lbl_empty.pack(pady=20)
            return
            
        for ach, is_unlocked in filtered_list:
            card = tk.Frame(self.cards_frame, bg=self.card_color, bd=1, relief="solid", highlightthickness=0)
            # Use border color for card outline
            card.config(highlightbackground=self.border_color, highlightcolor=self.border_color)
            card.pack(fill="x", pady=4, padx=2, ipady=5)
            
            # Unlocked card highlight
            card_accent = self.success_color if is_unlocked else self.border_color
            
            # Left icon area (emoji)
            parts = ach["name"].split(" ", 1)
            icon_char = parts[0] if len(parts) > 1 else "🏆"
            title_text = parts[1] if len(parts) > 1 else ach["name"]
            
            lbl_icon = tk.Label(card, text=icon_char, bg=self.card_color, fg=self.text_color, font=("Segoe UI", 18))
            lbl_icon.pack(side="left", padx=15)
            
            # Center text area
            txt_frame = tk.Frame(card, bg=self.card_color)
            txt_frame.pack(side="left", fill="both", expand=True, padx=5)
            
            lbl_card_title = tk.Label(
                txt_frame, text=title_text, bg=self.card_color, 
                fg=self.text_color if is_unlocked else self.text_dim, 
                font=("Segoe UI", 11, "bold"), anchor="w"
            )
            lbl_card_title.pack(anchor="w", pady=(2, 0))
            
            lbl_card_desc = tk.Label(
                txt_frame, text=ach["description"], bg=self.card_color, 
                fg=self.text_dim, font=("Segoe UI", 9), anchor="w", wrap=450, justify="left"
            )
            lbl_card_desc.pack(anchor="w", pady=(0, 2))
            
            # Right status area
            status_frame = tk.Frame(card, bg=self.card_color)
            status_frame.pack(side="right", padx=15, fill="y")
            
            if is_unlocked:
                unlocked_at = self.progress_data[ach["id"]].get("unlocked_at", "")
                date_str = unlocked_at.split("T")[0] if unlocked_at else "Unlocked"
                
                lbl_status = tk.Label(status_frame, text=f"🟢 {date_str}", bg=self.card_color, fg=self.success_color, font=("Segoe UI", 9, "bold"))
                lbl_status.pack(side="top", pady=5)
            else:
                lbl_status = tk.Label(status_frame, text="🔒 Locked", bg=self.card_color, fg=self.text_dim, font=("Segoe UI", 9))
                lbl_status.pack(side="top", pady=5)
                
            # Add category tag
            lbl_tag = tk.Label(status_frame, text=ach["category"], bg=self.bg_color, fg=self.text_dim, font=("Segoe UI", 7, "bold"), padx=6, pady=2)
            lbl_tag.pack(side="bottom", anchor="e")

    def on_game_launch(self, pid):
        # Triggered when game launches. We reload data to make sure it's up to date.
        self.reload_data()

    def on_game_close(self):
        # Triggered when game exits. Reload final results.
        self.reload_data()

    def create_settings_tab_widgets(self):
        settings_container = ttk.Frame(self.tab_settings, padding=15)
        settings_container.pack(fill="both", expand=True)
        
        lbl_settings_title = tk.Label(settings_container, text="⚙️ Achievements Overlay Settings", font=("Segoe UI", 12, "bold"), fg=self.accent_color, bg=self.bg_color)
        lbl_settings_title._is_title = True
        lbl_settings_title.pack(anchor="w", pady=(0, 15))
        
        # Config Card Frame
        hud_card = tk.LabelFrame(settings_container, text=" Transparent HUD Settings ", labelanchor="nw", bg=self.bg_color, fg=self.accent_color, font=("Segoe UI", 9, "bold"))
        hud_card.pack(fill="x", pady=(5, 0))
        self.overlay_card = hud_card
        
        self.grid_frame = tk.Frame(hud_card, bg=self.bg_color, padx=15, pady=15)
        self.grid_frame.pack(fill="x")
        
        # Position Row
        tk.Label(self.grid_frame, text="Position:", bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6, padx=(0, 10))
        pos_cb = ttk.Combobox(self.grid_frame, textvariable=self.hud_position, values=["Left-Half", "Right-Half", "Top-Half", "Bottom-Half"], state="readonly", width=15)
        pos_cb.grid(row=0, column=1, sticky="w", pady=6, padx=(0, 20))
        
        # Toggle Hotkey Row
        tk.Label(self.grid_frame, text="Toggle Hotkey:", bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=0, column=2, sticky="w", pady=6, padx=(0, 10))
        hk_cb = ttk.Combobox(self.grid_frame, textvariable=self.hud_hotkey, values=[f"F{i}" for i in range(1, 13)], state="readonly", width=12)
        hk_cb.grid(row=0, column=3, sticky="w", pady=6, padx=(0, 20))
        
        # Opacity Row
        tk.Label(self.grid_frame, text="Opacity:", bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6, padx=(0, 10))
        op_scale = tk.Scale(self.grid_frame, variable=self.hud_opacity, from_=0.1, to=1.0, resolution=0.05, orient="horizontal", showvalue=True, bg=self.bg_color, fg=self.text_color, highlightthickness=0, bd=0, length=120)
        op_scale.grid(row=1, column=1, sticky="w", pady=6, padx=(0, 20))
        
        # Scale Row
        tk.Label(self.grid_frame, text="HUD Scale:", bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=1, column=2, sticky="w", pady=6, padx=(0, 10))
        sc_scale = tk.Scale(self.grid_frame, variable=self.hud_scale, from_=0.5, to=1.5, resolution=0.05, orient="horizontal", showvalue=True, bg=self.bg_color, fg=self.text_color, highlightthickness=0, bd=0, length=120)
        sc_scale.grid(row=1, column=3, sticky="w", pady=6, padx=(0, 20))
        
        # Save Button
        self.btn_save_hud = tk.Button(self.grid_frame, text="💾 Save HUD Settings", command=self.save_overlay_config, bg=self.accent_color, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover, padx=15, pady=6)
        self.btn_save_hud.grid(row=0, column=4, rowspan=2, padx=(25, 0), sticky="ns")
        self.manager.bind_hover(self.btn_save_hud, is_primary=True)

    def retheme(self):
        # Update styling variables from manager
        self.bg_color = self.manager.bg_color
        self.card_color = self.manager.card_color
        self.accent_color = self.manager.accent_color
        self.accent_hover = self.manager.accent_hover
        self.text_color = self.manager.text_color
        self.text_dim = self.manager.text_dim
        self.border_color = self.manager.border_color
        self.success_color = self.manager.success_color
        
        # Configure the Canvas background explicitly
        if hasattr(self, "canvas") and self.canvas:
            self.canvas.configure(bg=self.bg_color)
            
        if hasattr(self, "lbl_progress") and self.lbl_progress:
            self.lbl_progress.configure(bg=self.bg_color, fg=self.success_color)
            
        if hasattr(self, "overlay_card") and self.overlay_card:
            self.overlay_card.configure(bg=self.bg_color, fg=self.accent_color)
            self.grid_frame.configure(bg=self.bg_color)
            for widget in self.grid_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg=self.bg_color, fg=self.text_color)
                elif isinstance(widget, tk.Scale):
                    widget.configure(bg=self.bg_color, fg=self.text_color, activebackground=self.accent_hover)
            self.btn_save_hud.configure(bg=self.accent_color, fg="white", activebackground=self.accent_hover)

        # Re-apply category button colors for the new theme and refresh view
        self.filter_category(self.selected_category)

