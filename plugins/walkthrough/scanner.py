import os
import sys
import time
import ctypes
import ctypes.wintypes

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_ulong),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong)
    ]

def get_pid_by_name(process_name):
    import subprocess
    try:
        out = subprocess.check_output(["tasklist", "/FI", f"IMAGENAME eq {process_name}", "/FO", "CSV"], text=True)
        lines = out.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split(",")
            if len(parts) > 1:
                return int(parts[1].strip('"'))
    except Exception:
        pass
    return None

def scan_all_process_memory(hProcess, target_val):
    mbi = MEMORY_BASIC_INFORMATION()
    address = 0
    max_address = 0x7FFFFFFF  # FFX is 32-bit, max user address is 2GB
    candidates = []
    
    print("Scanning process RAM (this may take a few seconds)...", flush=True)
    while address < max_address:
        if not kernel32.VirtualQueryEx(hProcess, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        
        is_readable = (mbi.State == MEM_COMMIT and 
                       not (mbi.Protect & PAGE_NOACCESS) and 
                       not (mbi.Protect & PAGE_GUARD))
        
        if is_readable and mbi.RegionSize > 0:
            buffer = ctypes.create_string_buffer(mbi.RegionSize)
            bytes_read = ctypes.c_size_t()
            if kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(address), buffer, mbi.RegionSize, ctypes.byref(bytes_read)):
                data = buffer.raw[:bytes_read.value]
                # Scan for 2-byte (ushort) integers
                for offset in range(0, len(data) - 2, 2):
                    val = int.from_bytes(data[offset:offset+2], byteorder='little')
                    if val == target_val:
                        candidates.append(address + offset)
        address += mbi.RegionSize
    return candidates

def get_module_base(pid, module_name):
    try:
        psapi = ctypes.windll.psapi
        hProcess = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if hProcess:
            try:
                hModules = (ctypes.wintypes.HMODULE * 1024)()
                cbNeeded = ctypes.wintypes.DWORD()
                if psapi.EnumProcessModules(hProcess, ctypes.byref(hModules), ctypes.sizeof(hModules), ctypes.byref(cbNeeded)):
                    count = cbNeeded.value // ctypes.sizeof(ctypes.wintypes.HMODULE)
                    for i in range(count):
                        hMod = hModules[i]
                        buf = ctypes.create_unicode_buffer(260)
                        if psapi.GetModuleBaseNameW(hProcess, hMod, buf, ctypes.sizeof(buf) // 2):
                            if buf.value.lower() == module_name.lower():
                                return hMod
            finally:
                kernel32.CloseHandle(hProcess)
    except Exception:
        pass
    return None

def main():
    print("FFX Room ID Whole-Process Memory Scanner")
    pid = get_pid_by_name("FFX.exe")
    if not pid:
        print("FFX.exe is not running.")
        return
        
    print(f"Found FFX.exe running with PID: {pid}")
    hProcess = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not hProcess:
        print("Failed to open process handle. Try running as Administrator.")
        return
        
    base_address = get_module_base(pid, "FFX.exe")
    if base_address:
        print(f"FFX.exe Base Address: {hex(base_address)}")
    else:
        print("Could not resolve FFX.exe base address. Defaulting to 0x400000.")
        base_address = 0x400000

    print("\n--- PHASE 1: Locate candidates ---")
    print("Please make sure you are currently in Besaid Beach (Room ID: 62) or on Rikku's Boat (Room ID: 63).")
    target_str = input("Enter your current Room ID (e.g. 62): ")
    try:
        target_val = int(target_str)
    except ValueError:
        print("Invalid number.")
        return
        
    candidates = scan_all_process_memory(hProcess, target_val)
    print(f"Found {len(candidates)} potential addresses in RAM containing value {target_val}.")
    
    if not candidates:
        print("No matches. Exiting.")
        return
        
    print("\n--- PHASE 2: Filter by changing maps ---")
    print("Now, walk into a DIFFERENT room/map in the game.")
    new_target_str = input("Once you have moved to the new map, enter the NEW Room ID (or press Enter if you don't know it): ")
    try:
        new_target_val = int(new_target_str) if new_target_str.strip() else None
    except ValueError:
        new_target_val = None
        
    # Rescan candidates
    print("Filtering candidates...")
    final_candidates = []
    for addr in candidates:
        val_new = ctypes.c_uint16()
        bytes_read = ctypes.c_size_t()
        ret = kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(addr), ctypes.byref(val_new), 2, ctypes.byref(bytes_read))
        if ret and bytes_read.value == 2:
            if new_target_val is not None:
                if val_new.value == new_target_val:
                    offset_from_base = addr - base_address
                    final_candidates.append((addr, offset_from_base, val_new.value))
            else:
                if val_new.value != target_val:
                    offset_from_base = addr - base_address
                    final_candidates.append((addr, offset_from_base, val_new.value))
                
    print(f"\nPinpointed {len(final_candidates)} candidates:")
    for addr, offset, val in final_candidates[:100]:
        print(f"Address: {hex(addr)} | FFX.exe + {hex(offset)} | New Value: {val}")
    if len(final_candidates) > 100:
        print("... and more.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")
