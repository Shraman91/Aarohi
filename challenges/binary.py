import hashlib
import os

class BinaryChallenge:
    id = "binary"
    title = "Holy C"
    category = "PWN"
    difficulty = "Intermediate"
    
    FLAG_HASH = "ed164d2fe25f3b71bfb209707932e5400874ec85573f7b92f4996b8ac499be2b"
    EASTER_EGG = "> Vulnerability discovered: Weakness for one particular human."

    scenario = """
    A classified authentication daemon is guarding this node.
    Security analysts reported that the developer used deprecated routines inside the login procedure.
    
    Your mission: Overflow the buffer, hijack the execution flow, and divert control to the hidden `win()` routine to extract the secret key.
    
    *Note: The target is a 64-bit Linux ELF binary. Run locally on Linux, WSL, or via the provided Docker container.*
    """

    hints = [
        "Memory boundaries are only as strict as the programmer enforces them. Trace the stack frame of the routine handling authentication to determine where user input collides with frame metadata.",
        "Consider the layout of an x86-64 stack frame: local variables, saved base pointer (RBP), followed by the return instruction pointer (RIP). Determine the exact byte distance needed to redirect control flow.",
        "System V AMD64 ABI requires the stack to be 16-byte aligned before any call instruction that reaches vector-accelerated glibc functions like printf. If your payload triggers a fault on a movaps instruction, adjust the return target accordingly."
    ]

    @classmethod
    def check_flag(cls, flag_input: str) -> bool:
        if not flag_input:
            return False
        clean = flag_input.strip()
        h = hashlib.sha256(clean.encode('utf-8')).hexdigest()
        return h == cls.FLAG_HASH

    @classmethod
    def get_source_code(cls) -> str:
        src_path = os.path.join(os.path.dirname(__file__), "..", "assets", "binary", "vuln.c")
        if os.path.exists(src_path):
            with open(src_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    @classmethod
    def get_binary_bytes(cls) -> bytes | None:
        bin_path = os.path.join(os.path.dirname(__file__), "..", "assets", "binary", "vuln")
        if os.path.exists(bin_path):
            with open(bin_path, "rb") as f:
                return f.read()
        return None

