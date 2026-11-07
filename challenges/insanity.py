"""
challenges/insanity.py
Challenge 04: Insanity Challenge - "Phantom Echoes"
Features hidden/invisible text appended at the end of the log,
revealed only when copied and pasted into external apps, encrypted with an Affine Cipher.
"""

import hashlib

class InsanityChallenge:
    id = "insanity"
    title = "Insanity Check"
    category = "STEGO"
    difficulty = "Hard"

    # SHA-256 hash of affine flag
    FLAG_HASH = "133ff3393f9ada9e767e31faffbbe90d209f2909bc0205906fce9771c7559f20"
    EASTER_EGG = "> Phantom signal resolved. You saw right through the invisible veil."

    scenario = """
    SIGNAL INTERCEPT // ANOMALOUS TRANSMISSION BUFFER
    ----------------------------------------------------------------------
    An automated memory dump from a decommissioned terminal node was intercepted.
    The console displays what looks like an ordinary, uncorrupted system log.
    
    However, deep memory forensics detected abnormal buffer length discrepancies.
    Something extra was appended to the tail of this transmission that evades visual rendering.

    Investigate the transmission block below, extract the hidden trailing payload,
    and break the encryption.
    """

    VISIBLE_TEXT = (
        "CLASSIFIED TELEMETRY DUMP: SUB-NODE // 0xDEADBEEF\n"
        "----------------------------------------------------------------------\n"
        "[SESSION START]\n"
        "Timestamp: 2026-11-06 23:45:00 UTC\n"
        "Diagnostic: All primary register checks executed successfully.\n"
        "Memory variance across sector 7 remains within nominal limits.\n"
        "Perimeter security daemons reporting zero intrusion alerts.\n"
        "No anomalous behavior detected in active display buffer.\n"
        "[SESSION CONCLUDED NORMALLY]"
    )

    # Affine Cipher: E(x) = (7x + 10) mod 26
    HIDDEN_CIPHERTEXT = "RMWEXF NHM GOJMXYM JOMG NHM NZUNH. TJKA: YNT{kttoxm_oxgkxonw_yexsumzmf}"

    hints = [
        "The web browser renders visual elements based on CSS stylesheets, but the clipboard captures raw text within the DOM selection. Copy the transmission block and paste it into an external text editor.",
        "The trailing hidden payload is encoded with an Affine Cipher: a modular linear substitution mapping E(x) = (a * x + b) mod 26, where a is coprime to 26.",
        "Perform known-plaintext analysis on the tail: the ciphertext fragment 'TJKA: YNT{' directly corresponds to the known format 'FLAG: CTF{'. Use these mappings to solve the simultaneous linear congruences for slope a and shift b."
    ]

    @classmethod
    def get_html_payload(cls) -> str:
        """Returns the formatted terminal log with appended hidden text."""
        visible_html = cls.VISIBLE_TEXT.replace("\n", "<br>")
        # The hidden ciphertext is rendered with opacity 0, transparent color, and tiny font
        # so it is invisible on screen but included when the user copies the block.
        hidden_span = (
            f'<span style="opacity: 0; font-size: 0.1px; color: transparent; line-height: 0; '
            f'user-select: text;" aria-hidden="true"> {cls.HIDDEN_CIPHERTEXT}</span>'
        )
        return (
            f'<div class="terminal-card" style="font-family: \'Fira Code\', monospace; '
            f'line-height: 1.6; user-select: text; word-break: break-word;">'
            f'<span>{visible_html}</span>'
            f'{hidden_span}'
            f'</div>'
        )

    @classmethod
    def normalize_input(cls, text: str) -> str:
        s = text.strip()
        if not s.lower().startswith("ctf{") and not s.lower().endswith("}"):
            s = f"CTF{{{s}}}"
        elif s.lower().startswith("ctf{") and s.endswith("}"):
            inner = s[4:-1].strip()
            s = f"CTF{{{inner}}}"
        return s.lower()

    @classmethod
    def check_flag(cls, flag_input: str) -> bool:
        if not flag_input:
            return False
        # Normalize to lowercase CTF{...}
        norm = cls.normalize_input(flag_input)
        # Check canonical lowercase or uppercase
        canonical = f"CTF{{{norm[4:-1]}}}"
        h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return h == cls.FLAG_HASH
