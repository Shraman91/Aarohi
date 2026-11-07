import hashlib

class OsintChallenge:
    id = "osint"
    title = "The Lost Monument"
    category = "OSINT"
    difficulty = "Moderate"

    FLAG_HASH = "fcfc014d8f24f789f6bf11711d1cdb9b8259b505f532ba1bf1676ea189bd7934"
    EASTER_EGG = "> Interesting. Someone built an entire monument for love.\n\n> Anyway, moving on..."

    scenario = """
    FIELD INTELLIGENCE DOSSIER // DECLASSIFIED MEMO
    --------------------------------------------------
    Surveillance reports and archival cross-referencing indicate a singular target of interest:

    1. Geospatial positioning places the compound along the crescent bend of a sacred northern river.
    2. Commissioned during the golden age of a dynasty whose lineage traced back to Central Asia.
    3. Built not as a seat of empire or conquest, but as an eternal sanctum mourning an irreplaceable loss.
    4. Its bilateral symmetry combines high-domed bulbous cupolas, red sandstone perimeter gates, and luminous Makrana marble inlaid with floral semiprecious stones.
    5. Globally recognized by cultural preservation treaties as one of humanity's universally celebrated masterpieces.

    Identify this monument. Format your submission as either `CTF{monument_name}` or simply the monument's name.
    """

    hints = [
        "The white marble was quarried hundreds of miles away in Rajasthan and transported across the empire by a logistics train of over a thousand elephants.",
        "The four perimeter minarets were engineered with a deliberate outward tilt to protect the central dome in the event of seismic collapse.",
        "Directly across the riverbank lies an aligned moonlit viewing pavilion (Mehtab Bagh) designed specifically to reflect the white facade."
    ]

    @classmethod
    def normalize_input(cls, text: str) -> str:
        s = text.strip().lower()
        if s.startswith("ctf{") and s.endswith("}"):
            s = s[4:-1].strip()
        # Replace spaces or dashes with underscores
        s = s.replace(" ", "_").replace("-", "_")
        return f"CTF{{{s}}}"

    @classmethod
    def check_flag(cls, flag_input: str) -> bool:
        if not flag_input:
            return False
        normalized = cls.normalize_input(flag_input)
        h = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        return h == cls.FLAG_HASH

