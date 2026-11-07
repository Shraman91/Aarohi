"""
tools/build_ring_video.py
Renders the complete 3D procedural ASCII diamond ring animation into an MP4 video.
Includes:
- Full assembly sequence from t=0.0s (particles coalescing into cathedral band and gem)
- Dynamic banner typewriter reveal ("will you be" -> "MINE?")
- Rotating diamond ring with star glints, light sweeps, and pulsing crimson text
"""

import os
import sys
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

# Add assets/ring to path to import the procedural renderer
RING_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "ring"))
if RING_DIR not in sys.path:
    sys.path.insert(0, RING_DIR)

import renderer as ring_engine

def build_video(
    output_path: str = None,
    fps: int = 30,
    duration: float = 14.0,
    W: int = 80,
    H: int = 42,
    font_size: int = 26
):
    if output_path is None:
        output_path = os.path.join(RING_DIR, "ring.mp4")

    print(f"[VIDEO BUILDER] Output target: {output_path}")
    print(f"[VIDEO BUILDER] Configuration: {W}x{H} grid @ {fps} FPS, duration: {duration}s")

    # Font setup
    font_candidates = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
        r"C:\Windows\Fonts\cour.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    font = None
    for fc in font_candidates:
        if os.path.exists(fc):
            try:
                font = ImageFont.truetype(fc, font_size)
                print(f"[VIDEO BUILDER] Using font: {fc} (size {font_size})")
                break
            except Exception:
                continue

    if font is None:
        font = ImageFont.load_default()
        print("[VIDEO BUILDER] Warning: Using default bitmap font")

    # Layout calculation
    char_w = int(font.getlength("M"))
    ascent, descent = font.getmetrics()
    char_h = ascent + descent + 2

    text_w = char_w * W
    text_h = char_h * H

    min_pad = 20
    # Must be divisible by 16 for standard H.264 macroblock encoding
    video_w = ((text_w + 2 * min_pad + 15) // 16) * 16
    video_h = ((text_h + 2 * min_pad + 15) // 16) * 16
    offset_x = (video_w - text_w) // 2
    offset_y = (video_h - text_h) // 2

    print(f"[VIDEO BUILDER] Resolution: {video_w}x{video_h} (macroblock 16 aligned)")
    print(f"[VIDEO BUILDER] Content text box: {text_w}x{text_h}, padding offsets: ({offset_x}, {offset_y})")

    total_frames = int(duration * fps)
    print(f"[VIDEO BUILDER] Total frames to generate: {total_frames}")

    # Ensure target directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    writer = imageio.get_writer(
        output_path,
        fps=fps,
        codec="libx264",
        pixelformat="yuv420p",
        bitrate="2500k",
        quality=9
    )

    t_start = time.time()
    bg_color = (4, 6, 5)  # Terminal dark theme #040605

    for frame_idx in range(total_frames):
        t = frame_idx / fps
        chars, rgb = ring_engine.render(t, W, H)

        img = Image.new("RGB", (video_w, video_h), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Quantize colors slightly to match renderer behavior and optimize drawing
        q = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)

        for y in range(H):
            row_chars = chars[y]
            row_q = q[y]
            curr_col = None
            curr_txt = []
            curr_x = 0

            for x in range(W):
                ch = row_chars[x]
                if ch == ' ':
                    if curr_txt:
                        draw.text(
                            (offset_x + curr_x * char_w, offset_y + y * char_h),
                            "".join(curr_txt),
                            font=font,
                            fill=curr_col
                        )
                        curr_txt = []
                    curr_col = None
                else:
                    c = (int(row_q[x, 0]), int(row_q[x, 1]), int(row_q[x, 2]))
                    if c != curr_col:
                        if curr_txt:
                            draw.text(
                                (offset_x + curr_x * char_w, offset_y + y * char_h),
                                "".join(curr_txt),
                                font=font,
                                fill=curr_col
                            )
                            curr_txt = []
                        curr_col = c
                        curr_x = x
                    curr_txt.append(ch)

            if curr_txt:
                draw.text(
                    (offset_x + curr_x * char_w, offset_y + y * char_h),
                    "".join(curr_txt),
                    font=font,
                    fill=curr_col
                )

        writer.append_data(np.array(img))

        if (frame_idx + 1) % 60 == 0 or (frame_idx + 1) == total_frames:
            elapsed = time.time() - t_start
            fps_actual = (frame_idx + 1) / max(0.001, elapsed)
            rem = (total_frames - (frame_idx + 1)) / max(0.001, fps_actual)
            print(
                f"[VIDEO BUILDER] Rendered {frame_idx + 1}/{total_frames} frames "
                f"({(frame_idx + 1)/total_frames*100:.1f}%) "
                f"- Speed: {fps_actual:.1f} fps - ETA: {rem:.1f}s"
            )

    writer.close()
    elapsed = time.time() - t_start
    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"[VIDEO BUILDER] Done! File saved: {output_path} ({file_size_kb:.1f} KB in {elapsed:.1f}s)")

if __name__ == "__main__":
    build_video()

