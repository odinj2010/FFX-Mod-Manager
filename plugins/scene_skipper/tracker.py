import os
import sys
import time
import json
import ctypes
import ctypes.wintypes
import struct
import tkinter as tk

# Windows API Constants
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_QUERY_INFORMATION = 0x0400

# Win32 structures
class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long)
    ]

# Setup Win32 handles
kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

try:
    psapi = ctypes.windll.psapi
except Exception:
    psapi = None

# Declare VirtualAllocEx, VirtualProtectEx, VirtualFreeEx
kernel32.VirtualAllocEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD]
kernel32.VirtualAllocEx.restype = ctypes.c_void_p

kernel32.VirtualProtectEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD)]
kernel32.VirtualProtectEx.restype = ctypes.wintypes.BOOL

kernel32.VirtualFreeEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, ctypes.wintypes.DWORD]
kernel32.VirtualFreeEx.restype = ctypes.wintypes.BOOL

kernel32.WriteProcessMemory.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
kernel32.WriteProcessMemory.restype = ctypes.wintypes.BOOL

kernel32.ReadProcessMemory.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
kernel32.ReadProcessMemory.restype = ctypes.wintypes.BOOL

user32.GetForegroundWindow.restype = ctypes.wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [ctypes.wintypes.HWND, ctypes.POINTER(ctypes.wintypes.DWORD)]

def find_game_hwnd(pid):
    hwnd_found = [None]
    def enum_callback(hwnd, extra):
        window_pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
        if window_pid.value == pid:
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value.upper()
                    if "FINAL FANTASY" in title or "FFX" in title:
                        hwnd_found[0] = hwnd
                        return False
                    if hwnd_found[0] is None:
                        hwnd_found[0] = hwnd
        return True
    
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    user32.EnumWindows(EnumWindowsProc(enum_callback), 0)
    return hwnd_found[0]

def get_game_client_rect_screen(hwnd):
    rect = RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        return None
    pt = POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    return pt.x, pt.y, w, h


class SceneSkipperOverlayHUD:
    def __init__(self, pid, game_dir):
        self.pid = pid
        self.game_dir = game_dir
        
        # Load overlay configuration
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.plugin_dir, "overlay_config.json")
        
        self.hotkey_vk = 0x76       # F7 default
        self.skip_key_vk = 0x08     # Backspace default
        self.skip_speed = "4x"      # Default speed up
        self.hud_position = "Right-Half"
        self.hud_opacity = 0.85
        self.hud_scale = 1.0
        
        self.last_config_check = 0.0
        self.config_mtime = 0.0
        self.load_config()
        
        # Setup process handle (with VM operations and VM writes)
        desired_access = PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION | PROCESS_QUERY_INFORMATION
        self.hProcess = kernel32.OpenProcess(desired_access, False, self.pid)
        if not self.hProcess:
            sys.exit(1)
            
        # Resolve base address of FFX.exe or FFX-2.exe
        self.base_address = self.get_module_base(self.pid, "FFX.exe")
        self.is_ffx2 = False
        if not self.base_address:
            self.base_address = self.get_module_base(self.pid, "FFX-2.exe")
            self.is_ffx2 = True
            
        # Event/cutscene memory offsets
        # FFX Steam version event indicator is at 0xD2CA90 (1 byte)
        # FFX-2 Steam version event indicator is at 0xABEB90 (1 byte)
        self.event_offset = 0xABEB90 if self.is_ffx2 else 0xD2CA90
        
        # Hook installation
        self.hook_allocated_address = None
        self.qpc_addr = None
        self.original_qpc_bytes = None
        self.install_speedhack_hook()
        
        # States
        self.is_skipping = False
        self.key_was_pressed = False
        self.overlay_visible = False
        self.f7_was_pressed = False
        self.is_cutscene_now = False
        
        self.overlay_window = None
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Loop schedules
        self.root.after(100, self.check_loop)
        
        # Start main loop
        try:
            self.root.mainloop()
        finally:
            self.uninstall_speedhack_hook()

    def read_mem(self, addr, size):
        buf = (ctypes.c_ubyte * size)()
        bytesRead = ctypes.c_size_t()
        if kernel32.ReadProcessMemory(self.hProcess, ctypes.c_void_p(addr), ctypes.byref(buf), size, ctypes.byref(bytesRead)):
            return bytes(buf[:bytesRead.value])
        return None

    def get_proc_address_32(self, dll_name, func_name):
        dll_base = self.get_module_base(self.pid, dll_name)
        if not dll_base:
            return None
            
        e_lfanew_data = self.read_mem(dll_base + 0x3C, 4)
        if not e_lfanew_data:
            return None
        e_lfanew = struct.unpack("<I", e_lfanew_data)[0]
        
        pe_header = dll_base + e_lfanew
        opt_header = pe_header + 24
        
        magic_data = self.read_mem(opt_header, 2)
        if not magic_data:
            return None
        magic = struct.unpack("<H", magic_data)[0]
        
        if magic == 0x10B: # PE32 (32-bit)
            export_dir_rva_addr = opt_header + 96
        elif magic == 0x20B: # PE32+ (64-bit)
            export_dir_rva_addr = opt_header + 112
        else:
            return None
            
        export_dir_data = self.read_mem(export_dir_rva_addr, 8)
        if not export_dir_data:
            return None
        export_rva, export_size = struct.unpack("<II", export_dir_data)
        if export_rva == 0 or export_size == 0:
            return None
            
        export_table_addr = dll_base + export_rva
        export_table = self.read_mem(export_table_addr, 40)
        if not export_table:
            return None
            
        num_names = struct.unpack("<I", export_table[24:28])[0]
        addr_funcs = struct.unpack("<I", export_table[28:32])[0]
        addr_names = struct.unpack("<I", export_table[32:36])[0]
        addr_ords = struct.unpack("<I", export_table[36:40])[0]
        
        names_data = self.read_mem(dll_base + addr_names, num_names * 4)
        ords_data = self.read_mem(dll_base + addr_ords, num_names * 2)
        funcs_data = self.read_mem(dll_base + addr_funcs, num_names * 4)
        
        if not names_data or not ords_data or not funcs_data:
            return None
            
        for i in range(num_names):
            name_rva = struct.unpack("<I", names_data[i*4 : i*4 + 4])[0]
            name_bytes = self.read_mem(dll_base + name_rva, 64)
            if not name_bytes:
                continue
            name_str = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
            if name_str == func_name:
                ordinal = struct.unpack("<H", ords_data[i*2 : i*2 + 2])[0]
                func_rva_data = self.read_mem(dll_base + addr_funcs + ordinal * 4, 4)
                if not func_rva_data:
                    return None
                func_rva = struct.unpack("<I", func_rva_data)[0]
                return dll_base + func_rva
                
        return None

    def log_debug(self, msg):
        log_path = os.path.join(self.plugin_dir, "debug_hook.log")
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        except Exception:
            pass

    def hook_api(self, dll_name, func_name, tramp_addr, detour_bytes_builder, detour_addr):
        self.log_debug(f"Attempting to hook {dll_name}!{func_name}...")
        target_addr = self.get_proc_address_32(dll_name, func_name)
        if not target_addr:
            self.log_debug(f"Failed to resolve address for {dll_name}!{func_name}")
            return False
            
        self.log_debug(f"Resolved {dll_name}!{func_name} at {hex(target_addr)}")
            
        # Avoid duplicate hooks on same address
        for hook_info in self.active_hooks:
            if hook_info["target_addr"] == target_addr:
                self.log_debug(f"Already hooked address {hex(target_addr)}")
                return True
                
        # Read original 5 bytes
        original_bytes = (ctypes.c_ubyte * 5)()
        bytesRead = ctypes.c_size_t()
        if not kernel32.ReadProcessMemory(self.hProcess, ctypes.c_void_p(target_addr), ctypes.byref(original_bytes), 5, ctypes.byref(bytesRead)) or bytesRead.value != 5:
            self.log_debug(f"Failed to read memory at {hex(target_addr)}")
            return False

        orig_hex = " ".join(f"{b:02X}" for b in original_bytes)
        self.log_debug(f"Original bytes at {hex(target_addr)}: {orig_hex}")

        # Safety Check: If the function starts with a jump (0xE9), it is already hooked or forwarded.
        # Overwriting it and copying the jump to trampoline would cause a crash.
        if original_bytes[0] == 0xE9:
            self.log_debug(f"Skipping hook for {dll_name}!{func_name} at {hex(target_addr)}: already hooked/forwarded (starts with E9 JMP).")
            return False

        # Compile trampoline
        trampoline = bytearray(original_bytes)
        jmp_back_offset = (target_addr + 5) - (tramp_addr + 5 + 5)
        trampoline.append(0xE9)
        trampoline.extend(struct.pack("<i", jmp_back_offset))
        
        # Compile detour bytes
        detour_bytes = detour_bytes_builder(tramp_addr, detour_addr)
        
        # Write trampoline and detour to target memory
        bytesWritten = ctypes.c_size_t()
        if not kernel32.WriteProcessMemory(self.hProcess, ctypes.c_void_p(tramp_addr), bytes(trampoline), len(trampoline), ctypes.byref(bytesWritten)):
            self.log_debug(f"Failed to write trampoline at {hex(tramp_addr)}")
            return False
        if not kernel32.WriteProcessMemory(self.hProcess, ctypes.c_void_p(detour_addr), bytes(detour_bytes), len(detour_bytes), ctypes.byref(bytesWritten)):
            self.log_debug(f"Failed to write detour at {hex(detour_addr)}")
            return False
        
        # Apply detour jump
        hook_jmp_offset = detour_addr - (target_addr + 5)
        hook_instruction = bytearray([0xE9])
        hook_instruction.extend(struct.pack("<i", hook_jmp_offset))
        
        old_protect = ctypes.wintypes.DWORD()
        if kernel32.VirtualProtectEx(self.hProcess, ctypes.c_void_p(target_addr), 5, 0x40, ctypes.byref(old_protect)):
            success = kernel32.WriteProcessMemory(self.hProcess, ctypes.c_void_p(target_addr), bytes(hook_instruction), 5, ctypes.byref(bytesWritten))
            kernel32.VirtualProtectEx(self.hProcess, ctypes.c_void_p(target_addr), 5, old_protect, ctypes.byref(old_protect))
            if not success:
                self.log_debug(f"Failed to write detour jump to target address {hex(target_addr)}")
                return False
        else:
            self.log_debug(f"Failed to VirtualProtectEx at {hex(target_addr)}")
            return False
            
        self.active_hooks.append({
            "target_addr": target_addr,
            "original_bytes": bytes(original_bytes)
        })
        self.log_debug(f"Successfully hooked {dll_name}!{func_name}")
        return True

    def build_qpc_detour(self, tramp_addr, detour_addr):
        H = self.hook_allocated_address
        detour_bytes = bytearray()
        detour_bytes.extend(b"\x55\x8B\xEC\x53\x51\x52\x56\x57")
        
        # mov eax, [H + 0]
        detour_bytes.append(0xA1)
        detour_bytes.extend(struct.pack("<I", H + 0))
        
        # test eax, eax
        detour_bytes.extend(b"\x85\xC0")
        
        # jz run_original
        jz_run_original_idx = len(detour_bytes)
        detour_bytes.extend(b"\x74\x00")
        
        # push parameter
        detour_bytes.extend(b"\xFF\x75\x08")
        
        # call trampoline (relative call E8)
        call_trampoline_idx = len(detour_bytes)
        detour_bytes.append(0xE8)
        detour_bytes.extend(b"\x00\x00\x00\x00")
        
        # test eax, eax
        detour_bytes.extend(b"\x85\xC0")
        
        # jz done
        jz_done_idx = len(detour_bytes)
        detour_bytes.extend(b"\x74\x00")
        
        # mov ecx, [ebp + 8]
        detour_bytes.extend(b"\x8B\x4D\x08")
        
        # fild qword ptr [ecx]
        detour_bytes.extend(b"\xDF\x29")
        
        # fild qword ptr [H + 16]
        detour_bytes.extend(b"\xDF\x2D")
        detour_bytes.extend(struct.pack("<I", H + 16))
        
        # fsubp st(1), st(0)
        detour_bytes.extend(b"\xDE\xE9")
        
        # fld qword ptr [H + 8]
        detour_bytes.extend(b"\xDD\x05")
        detour_bytes.extend(struct.pack("<I", H + 8))
        
        # fmulp st(1), st(0)
        detour_bytes.extend(b"\xDE\xC9")
        
        # fild qword ptr [H + 24]
        detour_bytes.extend(b"\xDF\x2D")
        detour_bytes.extend(struct.pack("<I", H + 24))
        
        # faddp st(1), st(0)
        detour_bytes.extend(b"\xDE\xC1")
        
        # fistp qword ptr [ecx]
        detour_bytes.extend(b"\xDF\x39")
        
        # mov eax, 1
        detour_bytes.extend(b"\xB8\x01\x00\x00\x00")
        
        # jmp done
        jmp_done_idx = len(detour_bytes)
        detour_bytes.extend(b"\xEB\x00")
        
        # run_original:
        run_original_offset = len(detour_bytes)
        detour_bytes.extend(b"\xFF\x75\x08")
        call_trampoline_2_idx = len(detour_bytes)
        detour_bytes.append(0xE8)
        detour_bytes.extend(b"\x00\x00\x00\x00")
        
        # done:
        done_offset = len(detour_bytes)
        detour_bytes.extend(b"\x5F\x5E\x5A\x59\x5B\x5D")
        detour_bytes.extend(b"\xC2\x04\x00")
        
        # Resolve short jumps
        detour_bytes[jz_run_original_idx + 1] = run_original_offset - (jz_run_original_idx + 2)
        detour_bytes[jz_done_idx + 1] = done_offset - (jz_done_idx + 2)
        detour_bytes[jmp_done_idx + 1] = done_offset - (jmp_done_idx + 2)
        
        # Resolve trampoline calls
        offset_1 = tramp_addr - (detour_addr + call_trampoline_idx + 5)
        detour_bytes[call_trampoline_idx + 1 : call_trampoline_idx + 5] = struct.pack("<i", offset_1)
        
        offset_2 = tramp_addr - (detour_addr + call_trampoline_2_idx + 5)
        detour_bytes[call_trampoline_2_idx + 1 : call_trampoline_2_idx + 5] = struct.pack("<i", offset_2)
        
        return detour_bytes

    def build_tick_detour(self, tramp_addr, detour_addr):
        H = self.hook_allocated_address
        detour_tick = bytearray()
        detour_tick.extend(b"\x55\x8B\xEC\x53\x51\x52\x56\x57")
        
        # mov eax, [H + 0]
        detour_tick.append(0xA1)
        detour_tick.extend(struct.pack("<I", H + 0))
        
        # test eax, eax
        detour_tick.extend(b"\x85\xC0")
        
        # jz run_original_tick
        jz_run_original_idx = len(detour_tick)
        detour_tick.extend(b"\x74\x00")
        
        # call trampoline
        call_tramp_idx = len(detour_tick)
        detour_tick.append(0xE8)
        detour_tick.extend(b"\x00\x00\x00\x00")
        
        # push eax
        detour_tick.append(0x50)
        
        # fild dword ptr [esp]
        detour_tick.extend(b"\xDB\x04\x24")
        
        # add esp, 4
        detour_tick.extend(b"\x83\xC4\x04")
        
        # fild qword ptr [H + 16]
        detour_tick.extend(b"\xDF\x2D")
        detour_tick.extend(struct.pack("<I", H + 16))
        
        # fsubp st(1), st(0)
        detour_tick.extend(b"\xDE\xE9")
        
        # fld qword ptr [H + 8]
        detour_tick.extend(b"\xDD\x05")
        detour_tick.extend(struct.pack("<I", H + 8))
        
        # fmulp st(1), st(0)
        detour_tick.extend(b"\xDE\xC9")
        
        # fild qword ptr [H + 24]
        detour_tick.extend(b"\xDF\x2D")
        detour_tick.extend(struct.pack("<I", H + 24))
        
        # faddp st(1), st(0)
        detour_tick.extend(b"\xDE\xC1")
        
        # sub esp, 8
        detour_tick.extend(b"\x83\xEC\x08")
        
        # fistp qword ptr [esp]
        detour_tick.extend(b"\xDF\x1C\x24")
        
        # pop eax
        detour_tick.append(0x58)
        
        # add esp, 4
        detour_tick.extend(b"\x83\xC4\x04")
        
        # jmp done_tick
        jmp_done_idx = len(detour_tick)
        detour_tick.extend(b"\xEB\x00")
        
        # run_original_tick:
        run_original_offset = len(detour_tick)
        call_tramp_2_idx = len(detour_tick)
        detour_tick.append(0xE8)
        detour_tick.extend(b"\x00\x00\x00\x00")
        
        # done_tick:
        done_offset = len(detour_tick)
        detour_tick.extend(b"\x5F\x5E\x5A\x59\x5B\x5D")
        detour_tick.append(0xC3)
        
        # Resolve short jumps
        detour_tick[jz_run_original_idx + 1] = run_original_offset - (jz_run_original_idx + 2)
        detour_tick[jmp_done_idx + 1] = done_offset - (jmp_done_idx + 2)
        
        # Resolve trampoline calls
        offset_1 = tramp_addr - (detour_addr + call_tramp_idx + 5)
        detour_tick[call_tramp_idx + 1 : call_tramp_idx + 5] = struct.pack("<i", offset_1)
        
        offset_2 = tramp_addr - (detour_addr + call_tramp_2_idx + 5)
        detour_tick[call_tramp_2_idx + 1 : call_tramp_2_idx + 5] = struct.pack("<i", offset_2)
        
        return detour_tick

    def install_speedhack_hook(self):
        self.active_hooks = []
        self.log_debug("install_speedhack_hook starting...")
        
        # Allocate memory in target process (1024 bytes)
        # H structure:
        # H + 0: enabled (4 bytes)
        # H + 4: padding (4 bytes)
        # H + 8: multiplier (8 bytes, double)
        # H + 16: real_base (8 bytes, int64)
        # H + 24: fake_base (8 bytes, int64)
        # H + 32 onwards: trampolines and detours
        self.hook_allocated_address = kernel32.VirtualAllocEx(self.hProcess, None, 1024, 0x3000, 0x40) # MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE
        if not self.hook_allocated_address:
            self.log_debug("VirtualAllocEx failed to allocate memory in target process.")
            return False

        H = self.hook_allocated_address
        self.log_debug(f"Allocated memory in target process at {hex(H)}")
        
        # Write default state (enabled=0, multiplier=1.0)
        state = struct.pack("<Iidqq", 0, 0, 1.0, 0, 0)
        bytesWritten = ctypes.c_size_t()
        kernel32.WriteProcessMemory(self.hProcess, ctypes.c_void_p(H), state, len(state), ctypes.byref(bytesWritten))

        # Hook 1: QPC (kernelbase.dll)
        self.hook_api("kernelbase.dll", "QueryPerformanceCounter", H + 32, self.build_qpc_detour, H + 48)
        
        # Hook 2: GetTickCount (kernelbase.dll)
        # self.hook_api("kernelbase.dll", "GetTickCount", H + 224, self.build_tick_detour, H + 240)
        
        # Hook 3: timeGetTime (winmm.dll)
        # self.hook_api("winmm.dll", "timeGetTime", H + 416, self.build_tick_detour, H + 432)
        
        self.log_debug(f"install_speedhack_hook finished. Active hooks count: {len(self.active_hooks)}")
        return len(self.active_hooks) > 0

    def set_speed(self, speed_mult):
        if not self.hook_allocated_address:
            return
            
        real_time = ctypes.c_int64()
        kernel32.QueryPerformanceCounter(ctypes.byref(real_time))
        
        # Read current bases to calculate current fake time continuously
        buffer = (ctypes.c_ubyte * 32)()
        bytesRead = ctypes.c_size_t()
        kernel32.ReadProcessMemory(self.hProcess, ctypes.c_void_p(self.hook_allocated_address), ctypes.byref(buffer), 32, ctypes.byref(bytesRead))
        
        buf_bytes = bytes(buffer)
        enabled = struct.unpack("<I", buf_bytes[0:4])[0]
        curr_mult = struct.unpack("<d", buf_bytes[8:16])[0]
        real_base = struct.unpack("<q", buf_bytes[16:24])[0]
        fake_base = struct.unpack("<q", buf_bytes[24:32])[0]
        
        if enabled == 0:
            curr_fake = real_time.value
        else:
            curr_fake = int(fake_base + (real_time.value - real_base) * curr_mult)
            
        new_enabled = 1 if speed_mult != 1.0 else 0
        packed_state = struct.pack("<Iidqq", new_enabled, 0, speed_mult, real_time.value, curr_fake)
        
        bytesWritten = ctypes.c_size_t()
        kernel32.WriteProcessMemory(self.hProcess, ctypes.c_void_p(self.hook_allocated_address), packed_state, len(packed_state), ctypes.byref(bytesWritten))

    def uninstall_speedhack_hook(self):
        if hasattr(self, "active_hooks") and self.active_hooks:
            # Disable speedhack first
            self.set_speed(1.0)
            time.sleep(0.05)
            
            # Restore all original bytes
            for hook in self.active_hooks:
                target_addr = hook["target_addr"]
                orig_bytes = hook["original_bytes"]
                
                old_protect = ctypes.wintypes.DWORD()
                kernel32.VirtualProtectEx(self.hProcess, ctypes.c_void_p(target_addr), 5, 0x40, ctypes.byref(old_protect))
                bytesWritten = ctypes.c_size_t()
                kernel32.WriteProcessMemory(self.hProcess, ctypes.c_void_p(target_addr), orig_bytes, 5, ctypes.byref(bytesWritten))
                kernel32.VirtualProtectEx(self.hProcess, ctypes.c_void_p(target_addr), 5, old_protect, ctypes.byref(old_protect))
            
            self.active_hooks = []
            
        if hasattr(self, "hook_allocated_address") and self.hook_allocated_address:
            kernel32.VirtualFreeEx(self.hProcess, ctypes.c_void_p(self.hook_allocated_address), 0, 0x8000) # MEM_RELEASE
            self.hook_allocated_address = None

    def get_module_base(self, pid, module_name):
        try:
            hModules = (ctypes.wintypes.HMODULE * 1024)()
            cbNeeded = ctypes.wintypes.DWORD()
            if psapi and psapi.EnumProcessModules(self.hProcess, ctypes.byref(hModules), ctypes.sizeof(hModules), ctypes.byref(cbNeeded)):
                count = cbNeeded.value // ctypes.sizeof(ctypes.wintypes.HMODULE)
                for i in range(count):
                    hMod = hModules[i]
                    buf = ctypes.create_unicode_buffer(260)
                    if psapi.GetModuleBaseNameW(self.hProcess, hMod, buf, ctypes.sizeof(buf) // 2):
                        if buf.value.lower() == module_name.lower():
                            return hMod
        except Exception:
            pass
            
        TH32CS_SNAPMODULE = 0x00000008
        TH32CS_SNAPMODULE32 = 0x00000010
        class MODULEENTRY32(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.c_ulong),
                ("th32ModuleID", ctypes.c_ulong),
                ("th32ProcessID", ctypes.c_ulong),
                ("GlblcntUsage", ctypes.c_ulong),
                ("ProccntUsage", ctypes.c_ulong),
                ("modBaseAddr", ctypes.c_void_p),
                ("modBaseSize", ctypes.c_ulong),
                ("hModule", ctypes.c_void_p),
                ("szModule", ctypes.c_char * 256),
                ("szExePath", ctypes.c_char * 260)
            ]
        hSnapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
        if hSnapshot != -1:
            try:
                me = MODULEENTRY32()
                me.dwSize = ctypes.sizeof(MODULEENTRY32)
                if kernel32.Module32First(hSnapshot, ctypes.byref(me)):
                    while True:
                        if me.szModule.decode('utf-8', errors='ignore').lower() == module_name.lower():
                            return me.modBaseAddr
                        if not kernel32.Module32Next(hSnapshot, ctypes.byref(me)):
                            break
            finally:
                kernel32.CloseHandle(hSnapshot)
        return None

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                mtime = os.path.getmtime(self.config_path)
                if mtime != self.config_mtime:
                    self.config_mtime = mtime
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    self.hotkey_vk = cfg.get("hotkey_vk", 0x76)
                    self.skip_key_vk = cfg.get("skip_key_vk", 0x08)
                    self.skip_speed = cfg.get("speed", "4x")
                    self.hud_position = cfg.get("position", "Right-Half")
                    self.hud_opacity = float(cfg.get("opacity", 0.85))
                    self.hud_scale = float(cfg.get("scale", 1.0))
            except Exception:
                pass

    def is_game_foreground(self):
        foreground_hwnd = user32.GetForegroundWindow()
        if not foreground_hwnd:
            return False
        window_pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(foreground_hwnd, ctypes.byref(window_pid))
        return window_pid.value == self.pid

    def is_cutscene_active(self):
        if not getattr(self, "base_address", None):
            return False
        target_addr = self.base_address + self.event_offset
        buffer = ctypes.c_ubyte()
        bytesRead = ctypes.c_size_t()
        ret = kernel32.ReadProcessMemory(self.hProcess, ctypes.c_void_p(target_addr), ctypes.byref(buffer), 1, ctypes.byref(bytesRead))
        if ret and bytesRead.value == 1:
            return buffer.value > 0
        return False

    def simulate_key_press(self, vk_code):
        # Resolve hardware scan code for DirectX/DirectInput compatibility
        scan_code = user32.MapVirtualKeyW(vk_code, 0)
        user32.keybd_event(vk_code, scan_code, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(vk_code, scan_code, 2, 0)
        time.sleep(0.05)

    def toggle_overlay(self, game_hwnd):
        if self.overlay_visible:
            self.overlay_visible = False
            if self.overlay_window:
                self.overlay_window.withdraw()
        else:
            self.overlay_visible = True
            if not self.overlay_window:
                self.create_overlay_window()
            self.sync_position(game_hwnd)
            self.overlay_window.deiconify()
            self.overlay_window.lift()

    def create_overlay_window(self):
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.overrideredirect(True)
        self.overlay_window.wm_attributes("-topmost", True)
        self.overlay_window.wm_attributes("-disabled", True)
        self.overlay_window.wm_attributes("-alpha", self.hud_opacity)
        self.overlay_window.configure(bg="#0b0f19")
        
        # UI Elements
        frame = tk.Frame(self.overlay_window, bg="#0b0f19", bd=1, relief="solid")
        frame.config(highlightbackground="#1e3a8a", highlightcolor="#1e3a8a")
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.lbl_header = tk.Label(frame, text="⏩ Scene Skipper Overlay", font=("Segoe UI", int(11 * self.hud_scale), "bold"), fg="#60a5fa", bg="#0b0f19")
        self.lbl_header.pack(fill="x", padx=10, pady=(8, 2))
        
        self.lbl_status = tk.Label(frame, text="Checking game...", font=("Segoe UI", int(10 * self.hud_scale)), fg="#d1d5db", bg="#0b0f19", anchor="w")
        self.lbl_status.pack(fill="x", padx=15, pady=2)
        
        self.lbl_action = tk.Label(frame, text="Pause game + press Skip Key", font=("Segoe UI", int(9 * self.hud_scale), "italic"), fg="#9ca3af", bg="#0b0f19", anchor="w")
        self.lbl_action.pack(fill="x", padx=15, pady=(2, 8))

    def sync_position(self, game_hwnd):
        if game_hwnd and self.overlay_window:
            rect = get_game_client_rect_screen(game_hwnd)
            if rect:
                x, y, w, h = rect
                overlay_w = int(260 * self.hud_scale)
                overlay_h = int(90 * self.hud_scale)
                
                # Position near top right of game window
                overlay_x = x + w - overlay_w - 20
                overlay_y = y + 20
                self.overlay_window.geometry(f"{overlay_w}x{overlay_h}+{overlay_x}+{overlay_y}")

    def update_hud(self):
        if not self.overlay_window or not self.overlay_visible:
            return
            
        game_detected = "FFX-2" if self.is_ffx2 else "FFX"
        status_text = f"Game: {game_detected} | Cutscene: {'Yes' if self.is_cutscene_now else 'No'}"
        
        # Map VK to label
        skip_key_name = "Backspace"
        if self.skip_key_vk == 0x20: skip_key_name = "Spacebar"
        elif self.skip_key_vk == 0x0D: skip_key_name = "Enter"
        elif self.skip_key_vk == 0x09: skip_key_name = "Tab"
        elif self.skip_key_vk == 0x1B: skip_key_name = "Escape"
        
        if self.is_skipping:
            self.lbl_status.config(text="⏩ FAST-FORWARD ACTIVE", fg="#10b981")
            self.lbl_action.config(text=f"Skipping at {self.skip_speed} speed...", fg="#10b981")
        else:
            self.lbl_status.config(text=status_text, fg="#d1d5db" if not self.is_cutscene_now else "#60a5fa")
            action_text = f"Pause game + press [{skip_key_name}] to skip" if self.is_cutscene_now else "Waiting for cutscene..."
            self.lbl_action.config(text=action_text, fg="#9ca3af" if not self.is_cutscene_now else "#f59e0b")

    def check_loop(self):
        # 1. Verify game is running
        exit_code = ctypes.wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(self.hProcess, ctypes.byref(exit_code)) or exit_code.value != 259:
            self.root.destroy()
            sys.exit(0)
            
        # 2. Check configuration file updates
        now = time.time()
        if now - self.last_config_check > 2.0:
            self.load_config()
            self.last_config_check = now
            
        game_hwnd = find_game_hwnd(self.pid)
        is_foreground = self.is_game_foreground()
        
        # 3. Handle Overlay hotkey toggle (F7)
        if is_foreground:
            f7_state = user32.GetAsyncKeyState(self.hotkey_vk) & 0x8000
            if f7_state:
                if not self.f7_was_pressed:
                    self.f7_was_pressed = True
                    self.toggle_overlay(game_hwnd)
            else:
                self.f7_was_pressed = False
                
        # 4. Sync position of overlay if active
        if self.overlay_visible and game_hwnd:
            self.sync_position(game_hwnd)
            
        # 5. Cutscene event state tracking
        self.is_cutscene_now = self.is_cutscene_active()
        
        # 6. Listen for skip trigger key
        if is_foreground:
            skip_pressed = user32.GetAsyncKeyState(self.skip_key_vk) & 0x8000
            if skip_pressed:
                if not self.key_was_pressed:
                    self.key_was_pressed = True
                    
                    if not self.is_skipping:
                        self.is_skipping = True
                        print("Fast-forward skip triggered!", flush=True)
                        
                        # Unpause the game by sending Escape, Backspace, X, and B (covers all default cancel/unpause controls)
                        self.simulate_key_press(0x1B) # Escape key
                        self.simulate_key_press(0x08) # Backspace key
                        self.simulate_key_press(0x58) # X key
                        self.simulate_key_press(0x42) # B key
                        time.sleep(0.2) # Allow menu to transition closed
                        
                        # Parse target speed multiplier
                        mult = 4.0
                        try:
                            mult = float(self.skip_speed.lower().replace("x", ""))
                        except ValueError:
                            pass
                        
                        # Apply speedhack
                        self.set_speed(mult)
                    else:
                        # Manual toggle off if key pressed again while skipping
                        self.is_skipping = False
                        print("Manual skip toggle off. Restoring 1x speed...", flush=True)
                        self.set_speed(1.0)
            else:
                self.key_was_pressed = False
                
        # 7. Automated return to 1x speed when cutscene finishes
        if self.is_skipping and not self.is_cutscene_now:
            self.is_skipping = False
            print("Cutscene ended automatically. Restoring 1x speed...", flush=True)
            self.set_speed(1.0)
                    
        # 8. Refresh HUD display values
        self.update_hud()
        
        # Schedule next check
        self.root.after(100, self.check_loop)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    pid = int(sys.argv[1])
    game_dir = sys.argv[2]
    
    hud = SceneSkipperOverlayHUD(pid, game_dir)

