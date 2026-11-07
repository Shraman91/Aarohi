from .sanity import SanityChallenge
from .binary import BinaryChallenge
from .crypto import CryptoChallenge
from .osint import OsintChallenge
from .insanity import InsanityChallenge

CHALLENGES = {
    "sanity": SanityChallenge,
    "binary": BinaryChallenge,
    "crypto": CryptoChallenge,
    "osint": OsintChallenge,
    "insanity": InsanityChallenge,
}


