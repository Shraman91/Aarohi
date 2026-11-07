"""
renderer.py
Thin wrapper around assets/ring/renderer.py
Handles full-sequence intro reveal and infinite live spinning ring animation.
"""

import html
import os
import sys
import time
import numpy as np
import streamlit as st

# ------------------------------------------------------------------ Configuration
RING_FPS = 30           # Smooth 30 FPS playback for seamless web streaming
RING_LOOP = 1          # Loops for finite animations
DEFAULT_WIDTH = 80      # Proportional width: centers ring & eliminates side blank space
DEFAULT_HEIGHT = 42     # Proportional height: displays full cathedral ring and sparkling facets
INTRO_DURATION = 5.2    # Full intro reveal duration (assembly + typing banners)
LOOP_DURATION = 2.4     # Continuous loop cycle duration for infinite spinning

# Path to pre-rendered MP4 video for native browser autoplay and infinite looping
RING_VIDEO_PATH = os.path.join(os.path.dirname(__file__), "assets", "ring", "ring.mp4")

# Load the existing ring renderer module directly from assets/ring/renderer.py
import importlib.util
ENGINE_PATH = os.path.join(os.path.dirname(__file__), "assets", "ring", "renderer.py")
spec = importlib.util.spec_from_file_location("ring_ascii_engine", ENGINE_PATH)
ring_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ring_engine)

def frame_to_html(chars: np.ndarray, rgb: np.ndarray) -> str:
    """Convert 2D characters and RGB arrays into colorized HTML with guaranteed line breaks."""
    H, W = chars.shape
    q = (np.clip(rgb, 0, 1) * 255).astype(np.int32) // 4 * 4
    
    html_lines = []
    for y in range(H):
        line_parts = []
        curr_color = None
        curr_text = []

        for x in range(W):
            ch = chars[y, x]
            # Escape HTML special characters
            escaped_ch = "&lt;" if ch == '<' else ("&gt;" if ch == '>' else ("&amp;" if ch == '&' else ch))
            color = (int(q[y, x, 0]), int(q[y, x, 1]), int(q[y, x, 2]))

            if color != curr_color:
                if curr_text:
                    c_r, c_g, c_b = curr_color
                    line_parts.append(f'<span style="color:rgb({c_r},{c_g},{c_b})">{"".join(curr_text)}</span>')
                    curr_text = []
                curr_color = color

            curr_text.append(escaped_ch)

        if curr_text:
            c_r, c_g, c_b = curr_color
            line_parts.append(f'<span style="color:rgb({c_r},{c_g},{c_b})">{"".join(curr_text)}</span>')

        row_content = "".join(line_parts)
        # Block-level div ensures each line cannot collapse horizontally
        html_lines.append(f'<div class="ascii-row">{row_content}</div>')

    inner_html = "".join(html_lines)
    return (
        '<div class="ascii-ring-wrapper">'
        '<pre class="ascii-ring">'
        f'{inner_html}'
        '</pre></div>'
    )

def frame_to_mono(chars: np.ndarray) -> str:
    """Convert 2D characters array into clean monospace plain text inside pre block."""
    H, W = chars.shape
    html_lines = []
    for y in range(H):
        escaped_line = "".join(
            "&lt;" if ch == '<' else ("&gt;" if ch == '>' else ("&amp;" if ch == '&' else ch))
            for ch in chars[y]
        )
        html_lines.append(f'<div class="ascii-row">{escaped_line}</div>')
    inner = "".join(html_lines)
    return (
        '<div class="ascii-ring-wrapper">'
        '<pre class="ascii-ring mono">'
        f'{inner}'
        '</pre></div>'
    )

def _display_frame(placeholder: st.delta_generator.DeltaGenerator, frame: str) -> None:
    if hasattr(placeholder, "html"):
        placeholder.html(frame)
    else:
        placeholder.markdown(frame, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_frames(
    W: int = DEFAULT_WIDTH,
    H: int = DEFAULT_HEIGHT,
    duration: float = INTRO_DURATION,
    fps: int = RING_FPS,
    mono: bool = False,
    t_start: float = 0.0
) -> list[str]:
    """Pre-computes and caches a sequence of animation frames as HTML strings."""
    total_frames = max(1, int(duration * fps))
    frames = []
    for i in range(total_frames):
        t = t_start + (i / fps)
        chars, rgb = ring_engine.render(t, W, H)
        if mono:
            frames.append(frame_to_mono(chars))
        else:
            frames.append(frame_to_html(chars, rgb))
    return frames

@st.cache_data(show_spinner=False)
def get_intro_frames(W: int = DEFAULT_WIDTH, H: int = DEFAULT_HEIGHT, fps: int = RING_FPS, mono: bool = False) -> list[str]:
    """Pre-computes the complete intro sequence: ring assembly + typing out 'will you be' and 'MINE?'."""
    return get_frames(W=W, H=H, duration=INTRO_DURATION, fps=fps, mono=mono, t_start=0.0)

@st.cache_data(show_spinner=False)
def get_loop_frames(W: int = DEFAULT_WIDTH, H: int = DEFAULT_HEIGHT, fps: int = RING_FPS, mono: bool = False) -> list[str]:
    """Pre-computes the continuous spinning loop of the completed diamond ring and banners."""
    return get_frames(W=W, H=H, duration=LOOP_DURATION, fps=fps, mono=mono, t_start=5.0)

def render_ring_video(placeholder: st.delta_generator.DeltaGenerator = None, video_path: str = None) -> bool:
    """
    Renders the ring animation as an autolooping HTML5 video via st.video().
    Provides full-resolution, 30 FPS playback with zero HTML line collapse
    and native browser-level infinite looping without blocking python execution.
    """
    if video_path is None:
        video_path = RING_VIDEO_PATH

    if not os.path.exists(video_path):
        return False

    target = placeholder if placeholder is not None else st
    target.video(video_path, autoplay=True, loop=True, muted=True)
    return True

def render_ring_animation_infinite(placeholder: st.delta_generator.DeltaGenerator, mono: bool = False) -> None:
    """
    Renders the complete 3D ASCII ring sequence:
    1. Plays full intro reveal from t=0.0 (assembly, typing banners, sparkle sweeps).
    2. Then seamlessly loops the rotating diamond ring infinitely without stopping.
    """
    intro_frames = get_intro_frames(W=DEFAULT_WIDTH, H=DEFAULT_HEIGHT, fps=RING_FPS, mono=mono)
    loop_frames = get_loop_frames(W=DEFAULT_WIDTH, H=DEFAULT_HEIGHT, fps=RING_FPS, mono=mono)

    delay = 1.0 / max(1, RING_FPS)

    # 1. Play the complete intro animation once per session
    if not st.session_state.get("ring_intro_played", False):
        for frame in intro_frames:
            _display_frame(placeholder, frame)
            time.sleep(delay)
        st.session_state["ring_intro_played"] = True

    # 2. Seamlessly loop the spinning diamond ring forever
    while True:
        for frame in loop_frames:
            _display_frame(placeholder, frame)
            time.sleep(delay)

def render_ring_animation(placeholder: st.delta_generator.DeltaGenerator, mono: bool = False, infinite: bool = True) -> None:
    """
    Renders or plays the ring animation.
    Prioritizes native MP4 video playback for maximum resolution, smooth 30 FPS,
    and seamless infinite browser looping. Falls back to frame-by-frame HTML streaming
    if the video file is not found.
    """
    if os.path.exists(RING_VIDEO_PATH):
        render_ring_video(placeholder, RING_VIDEO_PATH)
        return

    if infinite:
        render_ring_animation_infinite(placeholder, mono=mono)
    else:
        intro_frames = get_intro_frames(W=DEFAULT_WIDTH, H=DEFAULT_HEIGHT, fps=RING_FPS, mono=mono)
        if not intro_frames:
            return
        delay = 1.0 / max(1, RING_FPS)
        for frame in intro_frames:
            _display_frame(placeholder, frame)
            time.sleep(delay)
        _display_frame(placeholder, intro_frames[-1])
