import tkinter as tk

class ToolTip:
    def __init__(self, widget, text, delay=500, get_theme_colors=None):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.get_theme_colors = get_theme_colors
        self.tip_window = None
        self.id = None
        
        self.widget.bind("<Enter>", self.on_enter, add="+")
        self.widget.bind("<Leave>", self.on_leave, add="+")
        self.widget.bind("<ButtonPress>", self.on_leave, add="+")

    def on_enter(self, event=None):
        self.schedule()

    def on_leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self):
        if self.id:
            try:
                self.widget.after_cancel(self.id)
            except Exception:
                pass
            self.id = None

    def show(self):
        if not self.text:
            return
            
        # Determine colors dynamically
        bg = "#1e1e1e"
        fg = "#e5e7eb"
        border = "#374151"
        
        if self.get_theme_colors:
            try:
                colors = self.get_theme_colors()
                if colors:
                    bg = colors.get("card_color", bg)
                    fg = colors.get("text_color", fg)
                    border = colors.get("border_color", border)
            except Exception:
                pass

        # Position tip window offset from cursor position
        try:
            x = self.widget.winfo_pointerx() + 15
            y = self.widget.winfo_pointery() + 15
        except Exception:
            # Fallback based on widget placement
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        frame = tk.Frame(tw, background=border, padx=1, pady=1)
        frame.pack()
        
        label = tk.Label(frame, text=self.text, justify="left",
                         background=bg, foreground=fg,
                         font=("Segoe UI", 9), padx=6, pady=4)
        label.pack()

    def hide(self):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None
