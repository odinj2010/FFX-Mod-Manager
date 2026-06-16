import os
import struct

COLOR_MAP = {
    0x41: "WHITE",
    0x43: "YELLOW",
    0x52: "GREY",
    0x88: "BLUE",
    0x94: "RED",
    0x97: "PINK",
    0xA1: "OL_PURPLE",
    0xB1: "OL_CYAN"
}
COLOR_REV = {v: k for k, v in COLOR_MAP.items()}

class FFXCodec:
    def __init__(self, ffx_master_path=None):
        self.ffx_master_path = ffx_master_path
        self.byte_to_char_maps = {}
        self.char_to_byte_maps = {}
        self.loaded_charsets = set()
        
    def find_charset_file(self, charset):
        # List of potential paths to look for ffxsjistbl_*.bin
        search_paths = []
        if self.ffx_master_path:
            search_paths.append(os.path.join(self.ffx_master_path, "jppc", "ffx_encoding"))
            search_paths.append(os.path.join(self.ffx_master_path, "ffx_encoding"))
            
        # Relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        search_paths.append(os.path.join(script_dir, "..", "VBF Browser", "extracted", "ffx_ps2", "ffx", "master", "jppc", "ffx_encoding"))
        search_paths.append(os.path.join(script_dir, "jppc", "ffx_encoding"))
        search_paths.append(os.path.join(script_dir, "ffx_encoding"))
        search_paths.append(script_dir)
        
        for p in search_paths:
            full_path = os.path.join(p, f"ffxsjistbl_{charset}.bin")
            if os.path.exists(full_path):
                return full_path
        return None

    def load_charset(self, charset):
        if charset in self.loaded_charsets:
            return True
            
        filepath = self.find_charset_file(charset)
        if not filepath:
            # Fallback to loading an empty mapping or raise error
            return False
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                charset_chars = f.read()
                
            byte_to_char = {i + 0x30: c for i, c in enumerate(charset_chars)}
            char_to_byte = {c: i + 0x30 for i, c in enumerate(charset_chars)}
            
            self.byte_to_char_maps[charset] = byte_to_char
            self.char_to_byte_maps[charset] = char_to_byte
            self.loaded_charsets.add(charset)
            return True
        except Exception:
            return False

    def decode_ffx_bytes(self, table, offset, charset="us"):
        self.load_charset(charset)
        byte_to_char = self.byte_to_char_maps.get(charset, {})
        
        if offset < 0 or offset >= len(table):
            return ""
            
        # Get string bounds (stop at 0x00 terminator, handling multi-byte arguments)
        end = offset
        last_takes_args = False
        last_was_04 = False
        while end < len(table) and (table[end] != 0x00 or last_takes_args or last_was_04):
            last_was_04 = (table[end] == 0x04)
            last_takes_args = (not last_takes_args) and (0x2B <= table[end] <= 0x2F)
            end += 1
            
        bytes_subset = table[offset:end]
        out = []
        i = 0
        extra_five_sections = False
        
        while i < len(bytes_subset):
            idx = bytes_subset[i]
            extra_offset = 0x410 if extra_five_sections else 0
            extra_five_sections = False
            
            if idx >= 0x30:
                char_idx = idx + extra_offset
                c = byte_to_char.get(char_idx)
                if c:
                    out.append(c)
                else:
                    out.append(f"{{UNKDBLCHR:04:{idx:02X}}}" if extra_offset else f"{{UNKCHR:{idx:02X}}}")
            elif idx >= 0x2B:
                section = idx - 0x2B
                i += 1
                if i >= len(bytes_subset):
                    break
                low_byte = bytes_subset[i]
                actual_idx = section * 0xD0 + low_byte
                char_idx = actual_idx + extra_offset
                c = byte_to_char.get(char_idx)
                if c:
                    out.append(c)
                else:
                    out.append(f"{{UNKTPLCHR:04:{idx:02X}:{low_byte:02X}}}" if extra_offset else f"{{UNKDBLCHR:{idx:02X}:{low_byte:02X}}}")
            else:
                if extra_offset != 0:
                    char_idx = idx + extra_offset
                    c = byte_to_char.get(char_idx)
                    if c:
                        out.append(c)
                    else:
                        out.append(f"{{UNKDBLCHR:04:{idx:02X}}}")
                elif idx == 0x01:
                    out.append("{PAUSE}")
                elif idx == 0x03:
                    out.append("\n")
                elif idx == 0x04:
                    extra_five_sections = True
                elif idx == 0x07:
                    i += 1
                    if i >= len(bytes_subset): break
                    pixels = bytes_subset[i] - 0x30
                    out.append(f"{{SPACE:{pixels:02X}}}")
                elif idx == 0x09:
                    i += 1
                    if i >= len(bytes_subset): break
                    var_idx = bytes_subset[i] - 0x30
                    out.append(f"{{TIME:{var_idx:02X}}}")
                elif idx == 0x0A:
                    i += 1
                    if i >= len(bytes_subset): break
                    clr = bytes_subset[i]
                    clr_name = COLOR_MAP.get(clr, f"{clr:02X}")
                    out.append(f"{{CLR:{clr_name}}}")
                elif idx == 0x0B:
                    i += 1
                    if i >= len(bytes_subset): break
                    ctrl_idx = bytes_subset[i]
                    out.append(f"{{CTRL:{ctrl_idx:02X}}}")
                elif idx == 0x10:
                    i += 1
                    if i >= len(bytes_subset): break
                    rawValue = bytes_subset[i]
                    if rawValue == 0xFF:
                        out.append("{CHOICE-END}")
                    else:
                        choice_idx = rawValue - 0x30
                        out.append(f"{{CHOICE:{choice_idx:02X}}}")
                elif idx == 0x12:
                    i += 1
                    if i >= len(bytes_subset): break
                    var_idx = bytes_subset[i] - 0x30
                    out.append(f"{{VAR:{var_idx:02X}}}")
                elif idx == 0x13:
                    if i + 1 < len(bytes_subset) and bytes_subset[i+1] <= 0x43:
                        i += 1
                        pc_idx = bytes_subset[i] - 0x30
                        out.append(f"{{PC:{pc_idx:02X}}}")
                    else:
                        section = idx - 0x13
                        i += 1
                        if i >= len(bytes_subset): break
                        line = bytes_subset[i] - 0x30
                        out.append(f"{{MCR:s{section:02X}l{line:02X}}}")
                elif 0x13 <= idx <= 0x22:
                    section = idx - 0x13
                    i += 1
                    if i >= len(bytes_subset): break
                    line = bytes_subset[i] - 0x30
                    out.append(f"{{MCR:s{section:02X}l{line:02X}}}")
                elif idx == 0x23:
                    i += 1
                    if i >= len(bytes_subset): break
                    var_idx = bytes_subset[i]
                    out.append(f"{{KEY:{var_idx:02X}}}")
                elif idx == 0x27:
                    i += 1
                    if i >= len(bytes_subset): break
                    arg = bytes_subset[i]
                    out.append(f"{{UNK27:{arg:02X}}}")
                elif idx == 0x28:
                    i += 1
                    if i >= len(bytes_subset): break
                    var_idx = bytes_subset[i] - 0x30
                    out.append(f"{{CMD:28:{var_idx:02X}}}")
                elif idx == 0x2A:
                    i += 1
                    if i >= len(bytes_subset): break
                    var_idx = bytes_subset[i] - 0x30
                    out.append(f"{{CMD:2A:{var_idx:02X}}}")
                else:
                    i += 1
                    if i >= len(bytes_subset): break
                    var_idx = bytes_subset[i] - 0x30
                    out.append(f"{{CMD:{idx:02X}:{var_idx:02X}}}")
            i += 1
            
        return "".join(out)

    def char_to_bytes(self, char, charset="us"):
        self.load_charset(charset)
        char_to_byte = self.char_to_byte_maps.get(charset, {})
        
        if char == "\n":
            return [0x03]
        index_value = char_to_byte.get(char)
        if index_value is None:
            return None
            
        bytes_out = []
        if index_value >= 0x100:
            section = 0x2B
            while True:
                section += 1
                index_value -= 0xD0
                if index_value < 0x100:
                    break
            if section >= 0x30:
                bytes_out.append(0x04)
                if section >= 0x31:
                    bytes_out.append(section - 0x05)
            else:
                bytes_out.append(section)
        bytes_out.append(index_value)
        return bytes_out

    def parse_command(self, cmd):
        if cmd == "PAUSE":
            return [0x01]
        elif cmd == "\\n":
            return [0x03]
        elif cmd == "CHOICE-END":
            return [0x10, 0xFF]
        elif cmd.startswith("SPACE:"):
            pixels = int(cmd[6:], 16)
            return [0x07, pixels + 0x30]
        elif cmd.startswith("TIME:"):
            var_idx = int(cmd[5:], 16)
            return [0x09, var_idx + 0x30]
        elif cmd.startswith("CLR:") or cmd.startswith("COLOR:"):
            color_name = cmd.split(":")[1]
            color_byte = COLOR_REV.get(color_name)
            if color_byte is None:
                color_byte = int(color_name, 16)
            return [0x0A, color_byte]
        elif cmd.startswith("CTRL:"):
            ctrl_idx = int(cmd[5:], 16)
            return [0x0B, ctrl_idx]
        elif cmd.startswith("CHOICE:"):
            choice_idx = int(cmd[7:], 16)
            return [0x10, choice_idx + 0x30]
        elif cmd.startswith("VAR:"):
            var_idx = int(cmd[4:], 16)
            return [0x12, var_idx + 0x30]
        elif cmd.startswith("PC:"):
            pc = int(cmd[3:], 16)
            return [0x13, pc + 0x30]
        elif cmd.startswith("MCR:") or cmd.startswith("MACRO:"):
            section = int(cmd[5:7], 16) + 0x13
            line = int(cmd[8:10], 16) + 0x30
            return [section, line]
        elif cmd.startswith("KEY:"):
            key_item_idx = int(cmd[4:], 16)
            return [0x23, key_item_idx]
        elif cmd.startswith("KEY04:"):
            key_item_idx = int(cmd[6:], 16)
            return [0x04, 0x23, key_item_idx]
        elif cmd.startswith("UNK27:"):
            arg = int(cmd[6:], 16)
            return [0x27, arg]
        elif cmd.startswith("UNK0427:"):
            arg = int(cmd[8:], 16)
            return [0x04, 0x27, arg]
        elif cmd.startswith("CMD:"):
            parts = cmd.split(":")
            if len(parts) == 3:
                cmd_idx = int(parts[1], 16)
                var_idx = int(parts[2], 16)
                return [cmd_idx, var_idx + 0x30]
        elif cmd.startswith("UNKCHR:"):
            parts = cmd.split(":")
            return [int(parts[1], 16)]
        elif cmd.startswith("UNKDBLCHR:"):
            parts = cmd.split(":")
            if len(parts) == 3:
                return [int(parts[1], 16), int(parts[2], 16)]
            elif len(parts) == 2:
                return [int(parts[1], 16)]
        elif cmd.startswith("UNKTPLCHR:"):
            parts = cmd.split(":")
            if len(parts) == 4:
                return [int(parts[1], 16), int(parts[2], 16), int(parts[3], 16)]
        return None

    def encode_ffx_string(self, string, charset="us"):
        byte_list = []
        i = 0
        while i < len(string):
            chr_char = string[i]
            if chr_char == "{":
                end_idx = string[i:].find("}")
                if end_idx != -1:
                    cmd_content = string[i+1 : i+end_idx]
                    cmd_bytes = self.parse_command(cmd_content)
                    if cmd_bytes is not None:
                        byte_list.extend(cmd_bytes)
                        i += end_idx + 1
                        continue
            
            char_bytes = self.char_to_bytes(chr_char, charset)
            if char_bytes is not None:
                byte_list.extend(char_bytes)
            i += 1
        return byte_list

    def read_ffx_text_bin(self, filepath, record_length, charset="us"):
        """
        Reads an FFX text bin file.
        Returns a tuple: (records_list, min_idx, max_idx, magic_part)
        Each record in records_list is a dict:
        {
          'id': index,
          'name': str,
          'sname': str,
          'desc': str,
          'sdesc': str,
          'extra_bytes': bytes (binary part from 0x10 to record_length)
        }
        """
        with open(filepath, "rb") as f:
            file_bytes = f.read()
            
        if len(file_bytes) < 20:
            raise ValueError("File is too small to be a valid FFX .bin file.")
            
        header = file_bytes[:20]
        magic_part = header[:8]
        min_idx, max_idx, rec_len, tot_len = struct.unpack("<HHHH", header[8:16])
        
        # Override record_length if it is read from file header
        if rec_len != record_length:
            # Game's actual record length takes priority
            record_length = rec_len
            
        data_bytes = file_bytes[20 : 20+tot_len]
        string_bytes = list(file_bytes[20+tot_len :])
        
        record_count = max_idx - min_idx + 1
        records = []
        
        for idx in range(record_count):
            rec_offset = idx * record_length
            rec_data = data_bytes[rec_offset : rec_offset+record_length]
            if len(rec_data) < 16:
                # Pad to 16 if needed
                rec_data = rec_data + b"\x00" * (16 - len(rec_data))
                
            name_off, name_key = struct.unpack("<HH", rec_data[0:4])
            sname_off, sname_key = struct.unpack("<HH", rec_data[4:8])
            desc_off, desc_key = struct.unpack("<HH", rec_data[8:12])
            sdesc_off, sdesc_key = struct.unpack("<HH", rec_data[12:16])
            
            name = self.decode_ffx_bytes(string_bytes, name_off, charset)
            sname = self.decode_ffx_bytes(string_bytes, sname_off, charset)
            desc = self.decode_ffx_bytes(string_bytes, desc_off, charset)
            sdesc = self.decode_ffx_bytes(string_bytes, sdesc_off, charset)
            
            extra_bytes = rec_data[16:]
            
            records.append({
                "id": idx + min_idx,
                "name": name,
                "name_key": name_key,
                "sname": sname,
                "sname_key": sname_key,
                "desc": desc,
                "desc_key": desc_key,
                "sdesc": sdesc,
                "sdesc_key": sdesc_key,
                "extra_bytes": extra_bytes
            })
            
        return records, min_idx, max_idx, magic_part

    def write_ffx_text_bin(self, filepath, records, min_idx, max_idx, magic_part, charset="us"):
        """
        Repacks and saves records back to a .bin file.
        """
        # Encode all strings and prepare unique mappings
        refs = []
        for r in records:
            refs.append(('name', r['name'], r))
            refs.append(('sname', r['sname'], r))
            refs.append(('desc', r['desc'], r))
            refs.append(('sdesc', r['sdesc'], r))
            
        encoded_cache = {}
        for ref_type, s, r in refs:
            if s not in encoded_cache:
                encoded_cache[s] = self.encode_ffx_string(s, charset) + [0x00]
                
        # Sort by encoded length ascending to build deterministic buffer
        refs_sorted = sorted(refs, key=lambda x: len(encoded_cache[x[1]]))
        
        unique_map = {}
        byte_list = []
        
        for ref_type, s, r in refs_sorted:
            if s in unique_map:
                offset = unique_map[s]
            else:
                offset = len(byte_list)
                unique_map[s] = offset
                byte_list.extend(encoded_cache[s])
                
            r[ref_type + '_offset'] = offset
            # Retain original keys to prevent crashes in the game's localized text engine
            r[ref_type + '_key'] = r.get(ref_type + '_key', 0)
            
        # Rebuild structured record bytes
        data_blocks = []
        record_length = 16
        if records:
            record_length = 16 + len(records[0]['extra_bytes'])
            
        for r in records:
            header_bytes = struct.pack("<HHHHHHHH",
                r['name_offset'], r['name_key'],
                r['sname_offset'], r['sname_key'],
                r['desc_offset'], r['desc_key'],
                r['sdesc_offset'], r['sdesc_key']
            )
            record_block = header_bytes + r['extra_bytes']
            data_blocks.append(record_block)
            
        data_bytes = b"".join(data_blocks)
        string_buffer = bytes(byte_list)
        
        # Build 20-byte file header
        tot_len = len(data_bytes)
        file_header = magic_part + struct.pack("<HHHH", min_idx, max_idx, record_length, tot_len) + struct.pack("<I", 20)
        
        # Write file
        with open(filepath, "wb") as f:
            f.write(file_header + data_bytes + string_buffer)
            
        return len(file_header + data_bytes + string_buffer)
