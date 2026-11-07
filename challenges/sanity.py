"""
challenges/sanity.py
Challenge 00: Sanity Check - "our minecraft world"
"""

import hashlib
import os

class SanityChallenge:
    id = "sanity"
    title = "Sanity Check"
    category = "SANITY"
    difficulty = "Moderate"

    # SHA-256 hash of handshake key
    FLAG_HASH = "472fe7fb6822ef48d532aee77b16868b5a1589f3364907aa9e9777cc1f86235e"
    EASTER_EGG = "> Handshake verified. Some worlds are built to last forever."

    scenario = """
    SYSTEM ACCESS HANDSHAKE // IDENTITY VERIFICATION
    --------------------------------------------------
    Before executing deeper decryption protocols, the terminal requires a sanity check.
    Only the designated co-pilot knows the key to this terminal.

    Enter the secret keyphrase to clear the handshake.
    (Accepts the name directly or standard CTF{...} format).
    """

    hints = [
        "our minecraft world",
        "Think back to the world where our shared builds and late-night adventures began.",
        "The sanctuary we crafted block by block together."
    ]

    @classmethod
    def normalize_input(cls, text: str) -> str:
        s = text.strip().lower()
        if s.startswith("ctf{") and s.endswith("}"):
            s = s[4:-1].strip()
        # Replace spaces or hyphens with underscores
        s = s.replace(" ", "_").replace("-", "_")
        return f"CTF{{{s}}}"

    @classmethod
    def check_flag(cls, flag_input: str) -> bool:
        if not flag_input:
            return False

        # Support custom world name override via environment variable if set
        custom_world = os.environ.get("MINECRAFT_WORLD_NAME", "").strip()
        if custom_world:
            if cls.normalize_input(flag_input) == cls.normalize_input(custom_world):
                return True

        normalized = cls.normalize_input(flag_input)
        h = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        return h == cls.FLAG_HASH
