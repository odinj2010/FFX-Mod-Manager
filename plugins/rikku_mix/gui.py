import os
import sys
import json
import tkinter as tk
from tkinter import ttk
from mix_data import INGREDIENTS, MIX_OUTCOMES, calculate_mix

# Retrieve ToolTip class from parent manager's modules to prevent import failures in compiled exe mode
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

class RikkuMixTab:
    def __init__(self, parent_frame, manager_gui):
        self.parent = parent_frame
        self.manager = manager_gui
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.plugin_dir, "overlay_config.json")
        
        # Borrow styling variables
        self.bg_color = self.manager.bg_color
        self.card_color = self.manager.card_color
        self.accent_color = self.manager.accent_color
        self.accent_hover = self.manager.accent_hover
        self.text_color = self.manager.text_color
        self.text_dim = self.manager.text_dim
        self.border_color = self.manager.border_color
        
        # HUD Variables
        self.hud_position = tk.StringVar(value="Right-Half")
        self.hud_hotkey = tk.StringVar(value="F6")
        self.hud_opacity = tk.DoubleVar(value=0.85)
        self.hud_scale = tk.DoubleVar(value=1.0)
        self.load_overlay_config()
        
        # Main layout container
        self.frame = tk.Frame(self.parent, bg=self.bg_color)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create Notebook tab switcher inside self.frame
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Calculator
        self.tab_calc = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.tab_calc, text="🧪 Calculator")
        
        # Tab 2: Settings
        self.tab_settings = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.tab_settings, text="⚙️ Overlay Settings")
        
        # Build widgets for each tab
        self.create_calculator_widgets()
        self.create_settings_widgets()
        
        self.retheme()

    def load_overlay_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.hud_position.set(cfg.get("position", "Right-Half"))
                self.hud_hotkey.set(cfg.get("hotkey_str", "F6"))
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
            self.manager.log("Rikku's Mix HUD settings saved successfully.", "success")
        except Exception as e:
            self.manager.log(f"Failed to save HUD config: {e}", "error")

    def get_vk_code(self, hotkey_str):
        mapping = {f"F{i}": 0x6F + i for i in range(1, 13)}
        return mapping.get(hotkey_str, 0x75)  # F6 default

    def create_calculator_widgets(self):
        # Container frame inside Tab 1
        calc_container = tk.Frame(self.tab_calc, bg=self.bg_color)
        calc_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.lbl_title = tk.Label(
            calc_container, 
            text="🧪 Rikku's Mix Calculator & Recipe Book", 
            font=("Segoe UI", 13, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        self.lbl_title._is_title = True
        self.lbl_title.pack(anchor="w", pady=(0, 15))
        
        # Side-by-side Two Column Panel
        self.split_pane = tk.Frame(calc_container, bg=self.bg_color)
        self.split_pane.pack(fill="both", expand=True)
        
        # LEFT COLUMN: Calculator Panel (Card Style)
        self.calc_card = tk.LabelFrame(
            self.split_pane, text=" Ingredient Calculator ", font=("Segoe UI", 9, "bold"),
            fg=self.text_dim, bg=self.card_color, highlightthickness=1, highlightbackground=self.border_color, bd=0
        )
        self.calc_card._is_card = True
        self.calc_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        calc_inner = tk.Frame(self.calc_card, bg=self.card_color, padx=15, pady=15)
        calc_inner.pack(fill="both", expand=True)
        
        # Ingredient 1 Dropdown
        lbl_item1 = tk.Label(calc_inner, text="Select Ingredient 1:", font=("Segoe UI", 9), fg=self.text_color, bg=self.card_color)
        lbl_item1.pack(anchor="w", pady=(0, 4))
        
        self.cmb_item1 = ttk.Combobox(calc_inner, values=INGREDIENTS, state="readonly", font=("Segoe UI", 9))
        self.cmb_item1.pack(fill="x", pady=(0, 15))
        self.cmb_item1.set("Potion")
        self.cmb_item1.bind("<<ComboboxSelected>>", lambda e: self.perform_calculation())
        ToolTip(self.cmb_item1, "Choose the first ingredient for Rikku's Mix Overdrive.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))
        
        # Ingredient 2 Dropdown
        lbl_item2 = tk.Label(calc_inner, text="Select Ingredient 2:", font=("Segoe UI", 9), fg=self.text_color, bg=self.card_color)
        lbl_item2.pack(anchor="w", pady=(0, 4))
        
        self.cmb_item2 = ttk.Combobox(calc_inner, values=INGREDIENTS, state="readonly", font=("Segoe UI", 9))
        self.cmb_item2.pack(fill="x", pady=(0, 20))
        self.cmb_item2.set("Dark Matter")
        self.cmb_item2.bind("<<ComboboxSelected>>", lambda e: self.perform_calculation())
        ToolTip(self.cmb_item2, "Choose the second ingredient for Rikku's Mix Overdrive.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))
        
        # Calculate Action Button
        self.btn_calc = tk.Button(
            calc_inner, text="🧪 Combine Ingredients", command=self.perform_calculation,
            font=("Segoe UI", 9, "bold"), fg="white", bg=self.accent_color, relief="flat", activebackground=self.accent_hover, pady=6
        )
        self.btn_calc._is_primary = True
        self.btn_calc.pack(fill="x", pady=(0, 20))
        self.manager.bind_hover(self.btn_calc, is_primary=True)
        ToolTip(self.btn_calc, "Mix the two selected ingredients to calculate the resulting Overdrive effect.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))
        
        # Result Display Area
        self.result_container = tk.Frame(calc_inner, bg=self.card_color)
        self.result_container.pack(fill="both", expand=True)
        
        self.lbl_result_header = tk.Label(self.result_container, text="RESULT MIX:", font=("Segoe UI", 8, "bold"), fg=self.text_dim, bg=self.card_color)
        self.lbl_result_header.pack(anchor="w")
        
        self.lbl_mix_name = tk.Label(self.result_container, text="Select ingredients...", font=("Segoe UI", 12, "bold"), fg=self.accent_color, bg=self.card_color)
        self.lbl_mix_name.pack(anchor="w", pady=(2, 6))
        
        self.lbl_mix_desc = tk.Label(self.result_container, text="", font=("Segoe UI", 9), fg=self.text_color, bg=self.card_color, justify="left", wraplength=300)
        self.lbl_mix_desc.pack(anchor="w")
        
        # RIGHT COLUMN: Recipe Directory (Card Style)
        self.dir_card = tk.LabelFrame(
            self.split_pane, text=" Recipe Directory ", font=("Segoe UI", 9, "bold"),
            fg=self.text_dim, bg=self.card_color, highlightthickness=1, highlightbackground=self.border_color, bd=0
        )
        self.dir_card._is_card = True
        self.dir_card.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        dir_inner = tk.Frame(self.dir_card, bg=self.card_color, padx=15, pady=15)
        dir_inner.pack(fill="both", expand=True)
        
        # Search Box
        lbl_search = tk.Label(dir_inner, text="Search Mix Outcomes:", font=("Segoe UI", 9), fg=self.text_color, bg=self.card_color)
        lbl_search.pack(anchor="w", pady=(0, 4))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_directory())
        self.ent_search = ttk.Entry(dir_inner, textvariable=self.search_var, font=("Segoe UI", 9))
        self.ent_search.pack(fill="x", pady=(0, 10))
        ToolTip(self.ent_search, "Type mix name here to filter the recipe catalog.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))
        
        # Outcomes List Box with Scrollbar
        list_frame = tk.Frame(dir_inner, bg=self.card_color)
        list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.lst_outcomes = tk.Listbox(
            list_frame, font=("Segoe UI", 9), bd=1, relief="flat", highlightthickness=1, highlightbackground=self.border_color,
            bg=self.card_color, fg=self.text_color, selectbackground=self.accent_color, selectforeground="white",
            yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.lst_outcomes.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.lst_outcomes.pack(side="left", fill="both", expand=True)
        self.lst_outcomes.bind("<<ListboxSelect>>", self.on_directory_select)
        ToolTip(self.lst_outcomes, "Select any Mix outcome from the list to see its recipes.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))
        
        # Directory Details Display Card
        self.dir_details = tk.Frame(dir_inner, bg=self.card_color)
        self.dir_details.pack(fill="x")
        
        self.lbl_dir_effect = tk.Label(self.dir_details, text="", font=("Segoe UI", 9, "italic"), fg=self.text_dim, bg=self.card_color, justify="left", wraplength=300)
        self.lbl_dir_effect.pack(anchor="w", pady=(0, 8))
        
        self.lbl_recipes_header = tk.Label(self.dir_details, text="KNOWN FORMULAS:", font=("Segoe UI", 8, "bold"), fg=self.text_dim, bg=self.card_color)
        self.lbl_recipes_header.pack(anchor="w")
        
        self.lbl_recipes_list = tk.Label(self.dir_details, text="Select a mix to view recipes...", font=("Segoe UI", 9), fg=self.text_color, bg=self.card_color, justify="left")
        self.lbl_recipes_list.pack(anchor="w", pady=(2, 0))
        
        # Initial loads
        self.filter_directory()
        self.perform_calculation()

    def create_settings_widgets(self):
        self.settings_container = tk.Frame(self.tab_settings, bg=self.bg_color, padx=15, pady=15)
        self.settings_container.pack(fill="both", expand=True)
        
        self.lbl_settings_title = tk.Label(self.settings_container, text="⚙️ Rikku's Mix Overlay Settings", font=("Segoe UI", 12, "bold"), fg=self.accent_color, bg=self.bg_color)
        self.lbl_settings_title._is_title = True
        self.lbl_settings_title.pack(anchor="w", pady=(0, 15))
        
        # Config Card Frame
        hud_card = tk.LabelFrame(self.settings_container, text=" Transparent HUD Settings ", labelanchor="nw", bg=self.bg_color, fg=self.accent_color, font=("Segoe UI", 9, "bold"))
        hud_card.pack(fill="x", pady=(5, 0))
        self.overlay_card = hud_card
        
        self.grid_frame = tk.Frame(hud_card, bg=self.bg_color, padx=15, pady=15)
        self.grid_frame.pack(fill="x")
        
        # Position Row
        tk.Label(self.grid_frame, text="Position:", bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6, padx=(0, 10))
        pos_cb = ttk.Combobox(self.grid_frame, textvariable=self.hud_position, values=["Left-Half", "Right-Half", "Top-Half", "Bottom-Half"], state="readonly", width=15)
        pos_cb.grid(row=0, column=1, sticky="w", pady=6, padx=(0, 20))
        ToolTip(pos_cb, "Select where the overlay is positioned on the game screen.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))
        
        # Toggle Hotkey Row
        tk.Label(self.grid_frame, text="Toggle Hotkey:", bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=0, column=2, sticky="w", pady=6, padx=(0, 10))
        hk_cb = ttk.Combobox(self.grid_frame, textvariable=self.hud_hotkey, values=[f"F{i}" for i in range(1, 13)], state="readonly", width=12)
        hk_cb.grid(row=0, column=3, sticky="w", pady=6, padx=(0, 20))
        ToolTip(hk_cb, "Choose the keyboard hotkey to toggle the in-game overlay cheat-sheet.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))
        
        # Opacity Row
        tk.Label(self.grid_frame, text="Opacity:", bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6, padx=(0, 10))
        op_scale = tk.Scale(self.grid_frame, variable=self.hud_opacity, from_=0.1, to=1.0, resolution=0.05, orient="horizontal", showvalue=True, bg=self.bg_color, fg=self.text_color, highlightthickness=0, bd=0, length=120)
        op_scale.grid(row=1, column=1, sticky="w", pady=6, padx=(0, 20))
        ToolTip(op_scale, "Adjust transparency level of the overlay.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))
        
        # Scale Row
        tk.Label(self.grid_frame, text="HUD Scale:", bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=1, column=2, sticky="w", pady=6, padx=(0, 10))
        sc_scale = tk.Scale(self.grid_frame, variable=self.hud_scale, from_=0.5, to=1.5, resolution=0.05, orient="horizontal", showvalue=True, bg=self.bg_color, fg=self.text_color, highlightthickness=0, bd=0, length=120)
        sc_scale.grid(row=1, column=3, sticky="w", pady=6, padx=(0, 20))
        ToolTip(sc_scale, "Scale font size and layout elements of the overlay.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))
        
        # Save Button
        self.btn_save_hud = tk.Button(self.grid_frame, text="💾 Save HUD Settings", command=self.save_overlay_config, bg=self.accent_color, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", activebackground=self.accent_hover, padx=15, pady=6)
        self.btn_save_hud.grid(row=0, column=4, rowspan=2, padx=(25, 0), sticky="ns")
        self.manager.bind_hover(self.btn_save_hud, is_primary=True)
        ToolTip(self.btn_save_hud, "Save these settings and instantly apply them to the overlay.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))

    def perform_calculation(self):
        item1 = self.cmb_item1.get()
        item2 = self.cmb_item2.get()
        if item1 and item2:
            mix_name, mix_desc = calculate_mix(item1, item2)
            self.lbl_mix_name.config(text=mix_name)
            self.lbl_mix_desc.config(text=mix_desc)

    def filter_directory(self):
        query = self.search_var.get().lower().strip()
        self.lst_outcomes.delete(0, tk.END)
        for mix_name in sorted(MIX_OUTCOMES.keys()):
            if not query or query in mix_name.lower():
                self.lst_outcomes.insert(tk.END, mix_name)

    def on_directory_select(self, event):
        selection = self.lst_outcomes.curselection()
        if selection:
            mix_name = self.lst_outcomes.get(selection[0])
            details = MIX_OUTCOMES[mix_name]
            self.lbl_dir_effect.config(text=details["description"])
            
            recipe_strs = []
            for item1, item2 in details["recipes"]:
                recipe_strs.append(f"• {item1}  +  {item2}")
            self.lbl_recipes_list.config(text="\n".join(recipe_strs))

    def retheme(self):
        # Update colors from manager
        self.bg_color = self.manager.bg_color
        self.card_color = self.manager.card_color
        self.accent_color = self.manager.accent_color
        self.accent_hover = self.manager.accent_hover
        self.text_color = self.manager.text_color
        self.text_dim = self.manager.text_dim
        self.border_color = self.manager.border_color
        
        # Configure frames background
        self.frame.configure(bg=self.bg_color)
        self.lbl_title.configure(bg=self.bg_color, fg=self.accent_color)
        self.tab_calc.configure(bg=self.bg_color)
        self.tab_settings.configure(bg=self.bg_color)
        self.split_pane.configure(bg=self.bg_color)
        
        # Settings retheme
        if hasattr(self, "settings_container") and self.settings_container:
            self.settings_container.configure(bg=self.bg_color)
        if hasattr(self, "lbl_settings_title"):
            self.lbl_settings_title.configure(bg=self.bg_color, fg=self.accent_color)
        if hasattr(self, "overlay_card"):
            self.overlay_card.configure(bg=self.bg_color, fg=self.accent_color)
            self.grid_frame.configure(bg=self.bg_color)
            for widget in self.grid_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg=self.bg_color, fg=self.text_color)
                elif isinstance(widget, tk.Scale):
                    widget.configure(bg=self.bg_color, fg=self.text_color, activebackground=self.accent_hover)
            self.btn_save_hud.configure(bg=self.accent_color, fg="white", activebackground=self.accent_hover)
            
        # Calculator card colors
        self.calc_card.configure(bg=self.card_color, fg=self.text_dim, highlightbackground=self.border_color)
        for widget in self.calc_card.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.card_color)
                for sub in widget.winfo_children():
                    if isinstance(sub, tk.Label):
                        if sub == self.lbl_mix_name:
                            sub.configure(bg=self.card_color, fg=self.accent_color)
                        else:
                            sub.configure(bg=self.card_color, fg=self.text_color if sub != self.lbl_result_header else self.text_dim)
        
        # Buttons colors
        self.btn_calc.configure(bg=self.accent_color, fg="white", activebackground=self.accent_hover)
        
        # Directory card colors
        self.dir_card.configure(bg=self.card_color, fg=self.text_dim, highlightbackground=self.border_color)
        for widget in self.dir_card.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.card_color)
                for sub in widget.winfo_children():
                    if isinstance(sub, tk.Label):
                        sub.configure(bg=self.card_color, fg=self.text_color if sub != self.lbl_recipes_header else self.text_dim)
                    elif isinstance(sub, tk.Frame):
                        sub.configure(bg=self.card_color)
                        for sub_widget in sub.winfo_children():
                            if isinstance(sub_widget, tk.Listbox):
                                sub_widget.configure(bg=self.card_color, fg=self.text_color, highlightbackground=self.border_color, selectbackground=self.accent_color)
