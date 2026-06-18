# FFX Mod Manager v2.1.0 - The Fahrenheit Update

This release brings deep integration for the **Fahrenheit Framework**, a modernized tabbed interface, and powerful new tools for managing mod conflicts and discovery.

## 🚀 Key Features

### 🛠️ Deep Fahrenheit Framework Integration
*   **Automatic Manifest Generation:** The manager now dynamically generates `.manifest.json` files required by Fahrenheit, including correct path mapping for `efl/x/FFX_Data`.
*   **Load Order Sync:** Physical load order in the GUI now automatically synchronizes with Fahrenheit's `loadorder` file and internal manifest `LoadAfter` priorities.
*   **Zero-Footprint Mode:** When Fahrenheit is detected, all mod data (Active & Disabled) is neatly contained within the `/fahrenheit` directory, keeping the game's `/data` folder clean.
*   **Native Launcher Support:** Integrated support for `fhstage0.exe` to ensure the framework initializes correctly when launching from the manager.

### 🔍 Search & Discovery
*   **Real-time Search Bar:** Quickly find mods by name, ID, author, or category.
*   **Dynamic Category Filtering:** Organize your mod library with a new Category system (Texture, Script, Audio, UI, etc.) and filter the list instantly via a new dropdown.
*   **Metadata Expansion:** Support for "Nexus Mod ID" and "Mod Link" with a one-click **🌐 Visit** button to jump directly to a mod's online page.

### 🛡️ Conflict Radar & UI Overhaul
*   **Tabbed Mod Details:** A new layout that separates Mod Information, File Lists, and Conflicts into organized tabs.
*   **Conflict Radar:** A dedicated "Conflicts" tab that scans your enabled mods and alerts you to overlapping files, showing exactly which mods are competing for the same game assets.
*   **Reorganized Sidebar:** Improved navigation with the Plugin Browser and Settings moved to a persistent bottom section, prioritizing your active mods and plugin tools.

## 🔧 Improvements & Fixes
*   **Windows Process Detection:** Fixed a bug where game monitoring would "time out" on some Windows systems due to null-terminated string handling in the PID monitor.
*   **Metadata Security:** Hardened the `ffxmod` metadata encoding/decoding process.
*   **Cross-Platform Foundations:** Prepared the codebase for better compatibility across different environments.
*   **Improved Logging:** More detailed console output for conflict resolution and launcher status.

## 📝 Roadmap Highlights
*   **Integrated String Editor:** Utilizing the `ffx_codec.py` to allow live editing of game text.
*   **VBF Ghosting:** In-app browser for internal game files.
*   **Nexus Update Checker:** Automatic notifications when a mod you use is updated online.

---
*Thank you for being part of the FFX modding community! Report any issues on our GitHub page.*
