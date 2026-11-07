"""
tools/build_crypto.py
Generates the triple-layer ciphertext for Challenge 02 (CRYPTO).
Encryption Order: Plaintext -> Caesar (+3) -> Base64 -> Base62.
Decryption Order: Ciphertext -> Base62 Decode -> Base64 Decode -> Caesar (-3).
"""

import base64
import hashlib
import sys

BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE62_DICT = {c: i for i, c in enumerate(BASE62_ALPHABET)}

PLAINTEXT = "THE NEXT ANSWER IS A MONUMENT BUILT FOR A LOVE THAT OUTLIVED TIME. FLAG: CTF{triple_layer_decoded}"
FLAG = "CTF{triple_layer_decoded}"

def caesar_encrypt(text: str, shift: int = 3) -> str:
    res = []
    for ch in text:
        if 'A' <= ch <= 'Z':
            res.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        elif 'a' <= ch <= 'z':
            res.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        else:
            res.append(ch)
    return "".join(res)

def caesar_decrypt(text: str, shift: int = 3) -> str:
    return caesar_encrypt(text, -shift)

def bytes_to_base62(b: bytes) -> str:
    """Encode bytes to Base62 using big-integer representation, preserving leading zeros."""
    leading_zeros = 0
    for byte in b:
        if byte == 0:
            leading_zeros += 1
        else:
            break

    num = int.from_bytes(b, byteorder='big')
    if num == 0:
        return BASE62_ALPHABET[0] * len(b)

    digits = []
    base = len(BASE62_ALPHABET)
    while num > 0:
        digits.append(BASE62_ALPHABET[num % base])
        num //= base

    digits.reverse()
    return (BASE62_ALPHABET[0] * leading_zeros) + "".join(digits)

def base62_to_bytes(s: str) -> bytes:
    """Decode Base62 string back to bytes, preserving leading zeros."""
    leading_zeros = 0
    zero_char = BASE62_ALPHABET[0]
    for ch in s:
        if ch == zero_char:
            leading_zeros += 1
        else:
            break

    num = 0
    base = len(BASE62_ALPHABET)
    for ch in s[leading_zeros:]:
        if ch not in BASE62_DICT:
            raise ValueError(f"Invalid Base62 character: {ch}")
        num = num * base + BASE62_DICT[ch]

    if num == 0:
        return b'\x00' * leading_zeros

    # Calculate byte length needed
    byte_len = (num.bit_length() + 7) // 8
    raw_bytes = num.to_bytes(byte_len, byteorder='big')
    return (b'\x00' * leading_zeros) + raw_bytes

def encrypt(plaintext: str) -> str:
    # 1. Caesar +3
    c1 = caesar_encrypt(plaintext, shift=3)
    # 2. Base64
    b64_bytes = base64.b64encode(c1.encode('utf-8'))
    # 3. Base62
    c3 = bytes_to_base62(b64_bytes)
    return c3

def decrypt(ciphertext: str) -> str:
    # 1. Base62 decode
    b64_bytes = base62_to_bytes(ciphertext)
    # 2. Base64 decode
    c1_bytes = base64.b64decode(b64_bytes)
    c1 = c1_bytes.decode('utf-8')
    # 3. Caesar -3
    plaintext = caesar_decrypt(c1, shift=3)
    return plaintext

def main():
    ciphertext = encrypt(PLAINTEXT)
    decrypted = decrypt(ciphertext)

    flag_hash = hashlib.sha256(FLAG.encode('utf-8')).hexdigest()

    print("=== STACK OVERFLOW CIPHER GENERATOR ===")
    print(f"Plaintext:  {PLAINTEXT}")
    print(f"Flag:       {FLAG}")
    print(f"Flag Hash:  {flag_hash}")
    print(f"Ciphertext:\n{ciphertext}\n")
    print(f"Verification Round-Trip: {'PASSED' if decrypted == PLAINTEXT else 'FAILED'}")

    if decrypted != PLAINTEXT:
        sys.exit(1)

if __name__ == "__main__":
    main()

