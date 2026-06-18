# FFX Mod Manager Plugin Development Guide

Welcome! The FFX Mod Manager features an open, generic plugin loading system. Anyone can build custom modules—such as save editors, database lookups, speedrun splits, notes viewers, or live in-game HUD trackers—by dropping a folder into the `plugins/` directory.

This guide is structured to help **both non-coders** and **advanced programmers** build plugins.

---

## 1. Quick Start: "No-Code" Custom Notes/Guides Tab
If you have **no coding experience**, you can still create a custom tab in the Mod Manager to store your speedrun notes, monster arena checklists, or leveling guides!

Follow these 4 simple steps:

### Step A: Create the Folders
1. Navigate to the FFX Mod Manager folder.
2. Open the `plugins` folder.
3. Create a new folder inside it named `my_notes_tab`.

### Step B: Create the Manifest (`plugin.json`)
1. Inside your `my_notes_tab` folder, create a new text file and rename it to `plugin.json` (make sure to change the extension from `.txt` to `.json`).
2. Open it in Notepad, paste the following text, and save:
```json
{
  "name": "My Notes & Guides",
  "icon": "📝",
  "version": "1.0",
  "entry_point": "gui.NotesTab",
  "description": "A custom tab to display my FFX notes and guides."
}
```
*Note: You can change the `"name"` and choose any `"icon"` emoji you want!*

### Step C: Create the Interface (`gui.py`)
1. Create another text file in the same folder and rename it to `gui.py`.
2. Open it in Notepad, paste this complete template, and save:
```python
import tkinter as tk
from tkinter import ttk

class NotesTab:
    def __init__(self, parent_frame, manager_gui):
        self.parent = parent_frame
        self.manager = manager_gui  # Reference to Mod Manager
        
        # Load theme colors
        self.bg_color = self.manager.bg_color
        self.text_color = self.manager.text_color
        
        # Create a container frame
        self.frame = tk.Frame(self.parent, bg=self.bg_color)
        self.frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 1. Main Header Title
        self.lbl_title = tk.Label(
            self.frame, 
            text="📝 My Personal FFX Modding Guides", 
            font=("Segoe UI", 14, "bold"),
            fg=self.manager.accent_color,
            bg=self.bg_color
        )
        self.lbl_title._is_title = True  # Marks it to automatically change color with themes
        self.lbl_title.pack(anchor="w", pady=(0, 15))
        
        # 2. Text Box containing your notes
        self.txt_notes = tk.Text(
            self.frame, 
            font=("Segoe UI", 10), 
            wrap="word", 
            bd=0, 
            padx=10, 
            pady=10
        )
        self.txt_notes.pack(fill="both", expand=True)
        
        # --- WRITE YOUR CUSTOM NOTES/GUIDES IN THE BLOCK BELOW ---
        notes_text = """FFX QUICK REFERENCE GUIDES:

1. Thund Plains Lightning Dodge Cheat-Sheet:
   - Walk to the crater near the agency tower.
   - Loop: walk towards the lightning trigger spot, dodge, run back.
   - Dodge 50 consecutive lightning bolts for Elixir.
   - Dodge 200 consecutive lightning bolts for Venus Sigil (Lulu Celestial).

2. Monster Arena Checklist:
   - Besaid: Dingo, Condor, Water Flan (Need 10 of each).
   - Kilika: Dinonix, Killer Bee, Yellow Element, Ragora (Need 10 of each).
   - Calm Lands: Chimera Brain, Coeurl, Malboro, Defender X (Essential).

3. Rikku's Key Mix Recipes:
   - Trio of 9999: Dark Matter + Potion (All attacks deal 9999).
   - Hyper Mighty G: Healing Spring + Underdog's Secret (Haste/Protect/Shell/Regen/Auto-Life).
   - Ultra NulAll: Healing Spring + Healing Spring (Nullifies all elemental damage).
"""
        # ---------------------------------------------------------
        
        self.txt_notes.insert("1.0", notes_text)
        self.txt_notes.config(state="disabled") # Make it read-only
        
        # Configure initial text colors
        self.retheme()

    def retheme(self):
        """This function runs automatically whenever you switch theme styles in settings!"""
        self.bg_color = self.manager.bg_color
        
        # Determine background and text colors depending on whether theme is Dark or Light
        is_dark = (self.bg_color != "#f3f4f6")
        text_bg = "#0d0d0d" if is_dark else "#ffffff"
        text_fg = "#d1d5db" if is_dark else "#111827"
        
        # Update text area and container background colors
        self.frame.configure(bg=self.bg_color)
        self.txt_notes.configure(bg=text_bg, fg=text_fg, insertbackground=text_fg)
```

### Step D: Try it Out!
Launch **`FFX Mod Manager.exe`** (or restart it if it is already open). You will see your new custom tab **📝 My Notes & Guides** show up in the left-sidebar! Try switching appearance themes in Settings—the notes page and text will update colors dynamically!

---

## 2. Manifest File Structure (`plugin.json`)

If you are a developer writing custom functionality, here is the full directory layout and manifest description:

```text
plugins/
└── my_plugin/
    ├── plugin.json       # Manifest metadata (Required)
    ├── gui.py            # Main GUI class entry point (Required)
    ├── tracker.py        # Background script launched on game startup (Optional)
    └── tracker.exe       # Pre-compiled tracker binary (Optional)
```

### Manifest Fields:
- **`name`** (String): The text displayed on the tab header inside the Mod Manager sidebar.
- **`icon`** (String): A single emoji used next to the plugin name in the sidebar (e.g. `"🏆"`, `"⚙️"`, `"📝"`).
- **`version`** (String): Version metadata.
- **`entry_point`** (String): Points to the GUI loader class in the format `[filename].[ClassName]` (e.g., `gui.NotesTab`).
- **`tracker_script`** (String, Optional): Python filename for a background RAM tracker.
- **`description`** (String): Brief summary.

---

## 3. Developing Python GUI Tabs (`gui.py`)

Every GUI plugin must expose the class defined in `entry_point`. The class is instantiated with two parameters:

1. **`parent_frame`** (`ttk.Frame`): A container managed by the sidebar. Add your widgets directly here as children of `parent_frame`.
2. **`manager_gui`** (`FFXModManagerGUI`): Reference to the parent Mod Manager app, exposing directories, logging functions, configs, and styles.

### Styling with the Mod Manager Theme
To keep your plugin looking modern and matched with the application theme, read styles from `self.manager`:

| Variable | Description | Example (Dark Theme) |
|---|---|---|
| `self.manager.bg_color` | Main screen background color | `#121212` |
| `self.manager.card_color` | Frame/Card container color | `#1e1e1e` |
| `self.manager.accent_color` | Highlight/Active element color | `#3b82f6` |
| `self.manager.accent_hover` | Element color during mouse hovers | `#2563eb` |
| `self.manager.text_color` | Main text foreground | `#e5e7eb` |
| `self.manager.text_dim` | Muted/Disabled text | `#9ca3af` |
| `self.manager.border_color` | Frame dividers and card borders | `#374151` |
| `self.manager.success_color` | Successful status/Completed pills | `#10b981` |
| `self.manager.error_color` | Warn/Delete/Error operations | `#ef4444` |

### Adding Auto-Theme Support
Implement the `retheme(self)` method in your class. When the user changes themes in the Settings pane, the Mod Manager updates its own styling and then propagates the update by calling `.retheme()` on every loaded plugin tab.

```python
    def retheme(self):
        # Update colors from manager
        self.bg_color = self.manager.bg_color
        self.card_color = self.manager.card_color
        self.text_color = self.manager.text_color
        
        # Repaint your elements
        self.container.configure(bg=self.bg_color)
        self.lbl_title.configure(fg=self.manager.accent_color, bg=self.bg_color)
```

### Tagging Standard Widgets
Standard widgets (like standard labels or primary buttons) can be styled automatically by the Mod Manager's recursive propagator `update_widget_colors(self, widget)`:
- Set `widget._is_title = True` on standard Labels to have them automatically color-configured with `self.manager.accent_color`.
- Set `widget._is_muted = True` on Labels to style them automatically with `self.manager.text_dim`.
- Set `widget._is_primary = True` on standard Buttons to color them with `accent_color` and bind hover states.
- Set `widget._is_diagnostic = True` or `_is_status_pill = True` to prevent the Mod Manager from overriding your custom colors.

---

## 4. Background Trackers (`tracker.py` / `tracker.exe`)

Background trackers are useful for scanning game RAM, tracking speedruns, or showing in-game HUDs on top of `FFX.exe`.

### Execution Cycle:
1. When the user clicks **Launch FFX**, the Mod Manager monitors system processes until it detects that `FFX.exe` is running.
2. The Mod Manager scans the plugin folder for a tracker. It checks for a compiled **`tracker.exe`** first (this allows you to ship your plugin with a self-contained executable so users don't need a Python interpreter installed). If missing, it falls back to launching **`tracker.py`** via the system Python.
3. The tracker is spawned in the background with two arguments:
   `tracker.exe <PID> <GAME_DIRECTORY>`
   - `<PID>`: Process ID of the running `FFX.exe` game instance.
   - `<GAME_DIRECTORY>`: Folder directory of FFX.
4. When `FFX.exe` closes, the Mod Manager automatically clean-terminates the tracker process.

### Live memory scanning example:
```python
import sys
import ctypes
import time

PROCESS_VM_READ = 0x0010
kernel32 = ctypes.windll.kernel32

def main():
    pid = int(sys.argv[1])
    game_dir = sys.argv[2]
    
    # Open process handle to FFX
    hProcess = kernel32.OpenProcess(PROCESS_VM_READ, False, pid)
    if not hProcess:
        sys.exit(1)
        
    buffer = ctypes.create_string_buffer(4)
    bytes_read = ctypes.c_size_t()
    
    # Base Gil RAM offset relative to active gameplay block signature
    gil_address = 0x1E4F90FC # Dummy address (use dynamic signature scan to resolve)
    
    try:
        while True:
            # Read 4 bytes from game RAM
            if kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(gil_address), buffer, 4, ctypes.byref(bytes_read)):
                gil_count = int.from_bytes(buffer.raw, byteorder='little')
                print(f"Current Gil: {gil_count}")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        kernel32.CloseHandle(hProcess)

if __name__ == "__main__":
    main()
```

---

## 5. In-Game HUD Overlays

If you want to render information on top of the game screen (similar to the Custom Achievements overlay):

- **Click-Through Transparency**: Use Tkinter attributes `wm_attributes("-disabled", True)` to make your HUD overlay click-through, and `wm_attributes("-alpha", 0.9)` for opacity. This prevents the window from stealing keyboard/controller inputs.
- **Screen Borders Sync**: Query the game window coordinates via Win32 API functions (`GetClientRect` and `ClientToScreen`) to align your overlay exactly on the corner of the active game window.
- **Global Key Polling**: Run `ctypes.windll.user32.GetAsyncKeyState(VK_CODE)` inside your main thread to capture keystrokes globally (e.g. using `F8` to toggle the HUD display) even when the game has active focus.

---

## 6. Developer Guidelines and Best Practices

To ensure your plugin works correctly when distributed to the public and alongside other plugins, follow these guidelines:

### A. Avoid Module Namespace Collisions
The Mod Manager dynamically loads all plugins into a single Python process. If multiple plugins have a file with the same name (like `utils.py` or `config.py`), they can overwrite each other's imports.
*   **Rule**: Always use relative imports (e.g., `from . import helper` or `from .utils import my_func`) for sub-files within your plugin directory. Do not use top-level absolute imports (like `import utils`).

### B. Standard Library Constraints for `gui.py`
The compiled `FFX Mod Manager.exe` runs in a frozen PyInstaller environment that only bundles the Python Standard Library and Tkinter.
*   **Constraint**: Your `gui.py` script **cannot** import external libraries (like `requests`, `psutil`, or `pymem`). Keep `gui.py` lightweight, focusing only on the user interface using Python's standard library.

### C. Build a Standalone `tracker.exe`
If your background tracker requires third-party packages (e.g. for memory reading, overlay rendering, or external network calls):
*   **Requirement**: You must compile `tracker.py` into a standalone `tracker.exe` using PyInstaller before zipping your plugin:
    ```bash
    pyinstaller --noconsole --onefile --clean tracker.py
    ```
  The Mod Manager will automatically run the compiled `tracker.exe` if present. This ensures the tracker runs on the user's PC even if they do not have Python installed.

### D. Implement Resource Cleanup (`on_unload`)
If your GUI plugin starts background threads, opens persistent socket connections, or binds custom keyboard hotkeys:
*   **Requirement**: Define an `on_unload(self)` method in your main GUI class. The Mod Manager calls this when the plugin is reinstalled or reloaded. Use it to cleanly stop threads, close files/sockets, and release resources.
    ```python
    def on_unload(self):
        # Stop background threads or clean up connections
        self.my_thread.stop()
    ```

### E. Listen to Mod List Changes (`on_mods_refreshed`)
If your plugin needs to display mod statistics, analyze conflicts, or dynamically adjust settings based on active mods:
*   **Optional Hook**: Implement the `on_mods_refreshed(self)` hook. The Mod Manager calls this whenever mods are enabled, disabled, reordered, or scanned.
    ```python
    def on_mods_refreshed(self):
        # Re-scan manager mods list or update display
        active_mods = self.manager.mods
    ```
