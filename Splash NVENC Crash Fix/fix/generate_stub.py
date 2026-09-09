"""
Splash Player NVENC Crash Fix - DLL Generator

Generates a stub nvEncodeAPI.dll that prevents the NVENC initialization crash
in Splash Player 2.7.0 on systems with newer NVIDIA drivers (2024+).

The stub exports NvEncodeAPICreateInstance returning NULL (0), which causes
Splash to gracefully skip NVENC hardware encoding and fall back to software rendering.

Usage:
    python generate_stub.py [output_path]

If no output path is given, writes to the current directory.
"""

import struct
import os
import sys
import ctypes


def generate_nvenc_stub(output_path: str) -> bool:
    """Generate a minimal 32-bit DLL that stubs out NvEncodeAPICreateInstance."""

    FILE_ALIGN = 0x200
    SECT_ALIGN = 0x1000

    export_func_name = b'NvEncodeAPICreateInstance\x00'
    dll_name = b'nvEncodeAPI.dll\x00'

    # DllMain (entry point): returns TRUE so LoadLibrary succeeds
    # NvEncodeAPICreateInstance: returns 0 (NVENC not available)
    dllmain = b'\xB8\x01\x00\x00\x00\xC2\x0C\x00'
    nvenc_stub = b'\x31\xC0\xC2\x04\x00'
    code = dllmain + nvenc_stub

    code_rva = SECT_ALIGN
    nvenc_rva = code_rva + len(dllmain)
    sect2_rva = 2 * SECT_ALIGN

    func_tbl_rva = sect2_rva + 40
    name_tbl_rva = sect2_rva + 44
    ord_tbl_rva = sect2_rva + 48
    strings_rva = sect2_rva + 50
    dll_name_rva = strings_rva + len(export_func_name)

    exp_dir = struct.pack('<IIHHIIIIIII',
        0, 0, 0, 0,
        dll_name_rva, 1, 1, 1,
        func_tbl_rva, name_tbl_rva, ord_tbl_rva)

    func_tbl = struct.pack('<I', nvenc_rva)
    name_tbl = struct.pack('<I', strings_rva)
    ord_tbl = struct.pack('<H', 0)

    sect2_data = exp_dir + func_tbl + name_tbl + ord_tbl + export_func_name + dll_name
    sect2_vsize = len(sect2_data)
    sect2_raw_size = FILE_ALIGN
    sect2_raw_ptr = 2 * FILE_ALIGN

    text_raw = code.ljust(FILE_ALIGN, b'\x00')
    soi = 3 * SECT_ALIGN

    dos = bytearray(64)
    dos[0:2] = b'MZ'
    struct.pack_into('<I', dos, 60, 64)

    pe_coff = b'PE\x00\x00'
    pe_coff += struct.pack('<HHIIIHH', 0x014C, 2, 0, 0, 0, 224, 0x2102)

    oh = bytearray(224)
    struct.pack_into('<H',  oh,  0, 0x10B)
    struct.pack_into('<I',  oh,  4, SECT_ALIGN)
    struct.pack_into('<I',  oh,  8, SECT_ALIGN)
    struct.pack_into('<I',  oh, 16, code_rva)
    struct.pack_into('<I',  oh, 20, code_rva)
    struct.pack_into('<I',  oh, 24, 0x10000)
    struct.pack_into('<I',  oh, 28, 0x10000000)
    struct.pack_into('<I',  oh, 32, SECT_ALIGN)
    struct.pack_into('<I',  oh, 36, FILE_ALIGN)
    struct.pack_into('<H',  oh, 40, 4)
    struct.pack_into('<H',  oh, 48, 4)
    struct.pack_into('<I',  oh, 56, soi)
    struct.pack_into('<I',  oh, 60, FILE_ALIGN)
    struct.pack_into('<H',  oh, 68, 2)
    struct.pack_into('<I',  oh, 72, 0x100000)
    struct.pack_into('<I',  oh, 76, 0x1000)
    struct.pack_into('<I',  oh, 80, 0x100000)
    struct.pack_into('<I',  oh, 84, 0x1000)
    struct.pack_into('<I',  oh, 92, 16)

    s1 = bytearray(40)
    s1[0:5] = b'.text'
    struct.pack_into('<I', s1,  8, SECT_ALIGN)
    struct.pack_into('<I', s1, 12, code_rva)
    struct.pack_into('<I', s1, 16, FILE_ALIGN)
    struct.pack_into('<I', s1, 20, FILE_ALIGN)
    struct.pack_into('<I', s1, 36, 0x60000020)

    s2 = bytearray(40)
    s2[0:6] = b'.edata'
    struct.pack_into('<I', s2,  8, sect2_vsize)
    struct.pack_into('<I', s2, 12, sect2_rva)
    struct.pack_into('<I', s2, 16, sect2_raw_size)
    struct.pack_into('<I', s2, 20, sect2_raw_ptr)
    struct.pack_into('<I', s2, 36, 0x40000040)

    pe = dos + pe_coff + bytes(oh) + bytes(s1) + bytes(s2)
    pe += b'\x00' * (FILE_ALIGN - len(pe))
    pe += text_raw
    pe += sect2_data.ljust(sect2_raw_size, b'\x00')

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(pe)

    return True


def main():
    if len(sys.argv) > 1:
        out = sys.argv[1]
    else:
        out = os.path.join(os.getcwd(), 'nvEncodeAPI.dll')

    print(f'Generating stub DLL: {out}')
    try:
        generate_nvenc_stub(out)
    except PermissionError as e:
        print(f'[ERROR] Cannot write to "{out}".', file=sys.stderr)
        print('        Run this script as Administrator (the game folder is protected).', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'[ERROR] Failed to generate the DLL: {e}', file=sys.stderr)
        sys.exit(1)

    try:
        size = os.path.getsize(out)
    except OSError:
        size = -1
    print(f'Done! File size: {size} bytes')
    print('Integrity: generated purely with Python structs, no external binaries used.')


if __name__ == '__main__':
    main()
