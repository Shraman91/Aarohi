"""
tests/test_flow.py
Verifies challenge verification, crypto round-trip, ring frame caching,
and flag validation logic.
"""

import hashlib
import os
import pytest

from challenges.sanity import SanityChallenge
from challenges.binary import BinaryChallenge
from challenges.crypto import CryptoChallenge
from challenges.osint import OsintChallenge
from challenges.insanity import InsanityChallenge
from tools.build_crypto import decrypt, encrypt, PLAINTEXT, FLAG as CRYPTO_FLAG
import renderer

def test_sanity_challenge():
    # Correct canonical flag
    assert SanityChallenge.check_flag("CTF{ladybug}") is True
    # Tolerant normalization
    assert SanityChallenge.check_flag("ladybug") is True
    assert SanityChallenge.check_flag("LADYBUG") is True
    assert SanityChallenge.check_flag("Ladybug") is True
    assert SanityChallenge.check_flag("  ladybug  ") is True
    assert SanityChallenge.check_flag("CTF{ladybug}") is True
    # Incorrect
    assert SanityChallenge.check_flag("random_world") is False
    assert SanityChallenge.check_flag("") is False

def test_insanity_challenge():
    # Correct flag
    assert InsanityChallenge.check_flag("CTF{affine_insanity_conquered}") is True
    assert InsanityChallenge.check_flag("affine_insanity_conquered") is True
    assert InsanityChallenge.check_flag("ctf{affine_insanity_conquered}") is True
    # Incorrect
    assert InsanityChallenge.check_flag("CTF{wrong_flag}") is False
    assert InsanityChallenge.check_flag("") is False

    # HTML payload inspection
    payload = InsanityChallenge.get_html_payload()
    assert InsanityChallenge.HIDDEN_CIPHERTEXT in payload
    assert "user-select: text" in payload
    assert "opacity: 0" in payload

def test_pwn_challenge():
    assert BinaryChallenge.check_flag("CTF{buffer_overflow_unlocked}") is True
    assert BinaryChallenge.check_flag("wrong_flag") is False
    assert BinaryChallenge.check_flag("") is False
    assert BinaryChallenge.check_flag("  CTF{buffer_overflow_unlocked}  ") is True

    # Check source code is present and does NOT leak the flag
    src = BinaryChallenge.get_source_code()
    assert "void win()" in src
    assert "char password[32];" in src
    assert "gets(password);" in src
    assert "CTF{buffer_overflow_unlocked}" not in src

def test_crypto_round_trip():
    # Verify encrypt and decrypt are inverse functions
    ciphertext = encrypt(PLAINTEXT)
    decrypted = decrypt(ciphertext)
    assert decrypted == PLAINTEXT

    # Verify hardcoded challenge ciphertext decodes correctly
    recovered = decrypt(CryptoChallenge.CIPHERTEXT)
    assert recovered == PLAINTEXT
    assert CRYPTO_FLAG in recovered

    # Verify flag validation
    assert CryptoChallenge.check_flag(CRYPTO_FLAG) is True
    assert CryptoChallenge.check_flag("CTF{wrong_flag}") is False

def test_osint_challenge():
    # Correct canonical flag
    assert OsintChallenge.check_flag("CTF{taj_mahal}") is True

    # Tolerant normalization
    assert OsintChallenge.check_flag("taj mahal") is True
    assert OsintChallenge.check_flag("TAJ MAHAL") is True
    assert OsintChallenge.check_flag("Taj Mahal") is True
    assert OsintChallenge.check_flag("taj_mahal") is True
    assert OsintChallenge.check_flag("CTF{taj mahal}") is True

    # Incorrect answers
    assert OsintChallenge.check_flag("red fort") is False
    assert OsintChallenge.check_flag("qutub minar") is False
    assert OsintChallenge.check_flag("") is False

def test_ring_renderer_caching():
    # Generate 5 test frames
    frames = renderer.get_frames(W=60, H=22, duration=0.25, fps=20, mono=False)
    assert len(frames) == 5
    for f in frames:
        assert 'ascii-ring-wrapper' in f
        assert 'ascii-ring' in f
        assert '</pre></div>' in f

    # Generate mono frames
    mono_frames = renderer.get_frames(W=60, H=22, duration=0.25, fps=20, mono=True)
    assert len(mono_frames) == 5
    for f in mono_frames:
        assert 'ascii-ring mono' in f

def test_ring_video_exists_and_valid():
    # Verify the compiled MP4 ring animation is present and valid
    video_path = renderer.RING_VIDEO_PATH
    assert os.path.exists(video_path), f"Video file {video_path} does not exist"
    assert os.path.getsize(video_path) > 100_000, "Video file too small"

    # Verify metadata with imageio
    import imageio
    reader = imageio.get_reader(video_path)
    meta = reader.get_meta_data()
    reader.close()
    assert meta["codec"] == "h264"
    assert meta["fps"] == 30.0
    assert meta["duration"] >= 10.0

def test_no_plaintext_flags_in_modules():
    # Verify no plaintext flag string is stored in challenge modules
    import inspect
    for c_cls in [SanityChallenge, BinaryChallenge, CryptoChallenge, OsintChallenge, InsanityChallenge]:
        src = inspect.getsource(c_cls)
        assert "CTF{buffer_overflow_unlocked}" not in src
        assert "CTF{triple_layer_decoded}" not in src
        assert "CTF{ladybug}" not in src
        assert "CTF{affine_insanity_conquered}" not in src
        # Ensure only FLAG_HASH is stored
        assert hasattr(c_cls, "FLAG_HASH")

