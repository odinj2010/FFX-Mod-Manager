import os
import tkinter as tk
from tkinter import ttk
from tooltip import ToolTip
from mix_data import INGREDIENTS, MIX_OUTCOMES, calculate_mix

class RikkuMixTab:
    def __init__(self, parent_frame, manager_gui):
        self.parent = parent_frame
        self.manager = manager_gui
        
        # Style variables from manager
        self.bg_color = self.manager.bg_color
        self.card_color = self.manager.card_color
        self.accent_color = self.manager.accent_color
        self.accent_hover = self.manager.accent_hover
        self.text_color = self.manager.text_color
        self.text_dim = self.manager.text_dim
        self.border_color = self.manager.border_color
        
        # Main layout container
        self.frame = tk.Frame(self.parent, bg=self.bg_color)
        self.frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 1. Main Header Title
        self.lbl_title = tk.Label(
            self.frame, 
            text="🧪 Rikku's Mix Calculator & Recipe Book", 
            font=("Segoe UI", 13, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        self.lbl_title._is_title = True
        self.lbl_title.pack(anchor="w", pady=(0, 15))
        
        # Side-by-side Two Column Panel
        self.split_pane = tk.Frame(self.frame, bg=self.bg_color)
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
        ToolTip(self.cmb_item1, "Choose the first ingredient for Rikku's Mix Overdrive.", get_theme_colors=lambda: self.manager.themes.get(self.manager.current_theme_name))
        
        # Ingredient 2 Dropdown
        lbl_item2 = tk.Label(calc_inner, text="Select Ingredient 2:", font=("Segoe UI", 9), fg=self.text_color, bg=self.card_color)
        lbl_item2.pack(anchor="w", pady=(0, 4))
        
        self.cmb_item2 = ttk.Combobox(calc_inner, values=INGREDIENTS, state="readonly", font=("Segoe UI", 9))
        self.cmb_item2.pack(fill="x", pady=(0, 20))
        self.cmb_item2.set("Dark Matter")
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
        
        self.lbl_mix_desc = tk.Label(self.result_container, text="", font=("Segoe UI", 9), fg=self.text_color, bg=self.card_color, justify="left", wraplength=350)
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
        
        self.lbl_dir_effect = tk.Label(self.dir_details, text="", font=("Segoe UI", 9, "italic"), fg=self.text_dim, bg=self.card_color, justify="left", wraplength=350)
        self.lbl_dir_effect.pack(anchor="w", pady=(0, 8))
        
        self.lbl_recipes_header = tk.Label(self.dir_details, text="KNOWN FORMULAS:", font=("Segoe UI", 8, "bold"), fg=self.text_dim, bg=self.card_color)
        self.lbl_recipes_header.pack(anchor="w")
        
        self.lbl_recipes_list = tk.Label(self.dir_details, text="Select a mix to view recipes...", font=("Segoe UI", 9), fg=self.text_color, bg=self.card_color, justify="left")
        self.lbl_recipes_list.pack(anchor="w", pady=(2, 0))
        
        # Initial loads
        self.filter_directory()
        self.perform_calculation()
        
        self.retheme()

    def perform_calculation(self):
        """Calculates Rikku's Mix outcome based on the two comboboxes."""
        item1 = self.cmb_item1.get()
        item2 = self.cmb_item2.get()
        if item1 and item2:
            mix_name, mix_desc = calculate_mix(item1, item2)
            self.lbl_mix_name.config(text=mix_name)
            self.lbl_mix_desc.config(text=mix_desc)

    def filter_directory(self):
        """Filters the Listbox outcomes based on search input."""
        query = self.search_var.get().lower().strip()
        self.lst_outcomes.delete(0, tk.END)
        for mix_name in sorted(MIX_OUTCOMES.keys()):
            if not query or query in mix_name.lower():
                self.lst_outcomes.insert(tk.END, mix_name)

    def on_directory_select(self, event):
        """Displays details and recipes for selected outcome."""
        selection = self.lst_outcomes.curselection()
        if selection:
            mix_name = self.lst_outcomes.get(selection[0])
            details = MIX_OUTCOMES[mix_name]
            self.lbl_dir_effect.config(text=details["description"])
            
            # Format recipes list
            recipe_strs = []
            for item1, item2 in details["recipes"]:
                recipe_strs.append(f"• {item1}  +  {item2}")
            self.lbl_recipes_list.config(text="\n".join(recipe_strs))

    def retheme(self):
        """Invoked by manager GUI when changing themes."""
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
        self.split_pane.configure(bg=self.bg_color)
        self.lbl_title.configure(bg=self.bg_color, fg=self.accent_color)
        
        # Calculator card colors
        self.calc_card.configure(bg=self.card_color, fg=self.text_dim, highlightbackground=self.border_color)
        for widget in self.calc_card.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.card_color)
                for sub in widget.winfo_children():
                    if isinstance(sub, tk.Label):
                        # Determine if title
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
                        # Inside ListBox frame
                        sub.configure(bg=self.card_color)
                        for sub_widget in sub.winfo_children():
                            if isinstance(sub_widget, tk.Listbox):
                                #Retheme Listbox
                                sub_widget.configure(bg=self.card_color, fg=self.text_color, highlightbackground=self.border_color, selectbackground=self.accent_color)
