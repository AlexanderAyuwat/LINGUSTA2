"""
Generates animated placeholder demo videos for each sign lesson.
Uses mjpg codec which is reliably available on Windows.
Run: python create_dummy_videos.py
"""
import cv2
import numpy as np
import math
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUT_DIR  = BASE_DIR / "assets" / "demo_videos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H   = 640, 480
FPS    = 24
SECS   = 3
FRAMES = FPS * SECS

# Per-sign config: word, instruction hint, accent colour (BGR)
SIGNS = [
    {
        "name":    "hungry",
        "word":    "HUNGRY",
        "hint":    "Rub your fist on your stomach",
        "colour":  (114, 111, 169),   # warm rose-purple
    },
    {
        "name":    "sleepy",
        "word":    "SLEEPY",
        "hint":    "Pull hand down over face",
        "colour":  (130, 100, 80),    # warm muted blue
    },
    {
        "name":    "drink",
        "word":    "DRINK",
        "hint":    "Mime holding a cup to your mouth",
        "colour":  (80, 130, 120),    # teal-green
    },
    {
        "name":    "yes",
        "word":    "YES",
        "hint":    "Nod your fist up and down",
        "colour":  (70, 130, 80),     # green
    },
]

# Palette
BG       = (28, 18, 23)
WHITE    = (255, 255, 255)
CREAM    = (200, 228, 245)
MUTED    = (160, 148, 155)

FONT      = cv2.FONT_HERSHEY_DUPLEX
FONT_BOLD = cv2.FONT_HERSHEY_SIMPLEX


def put_centered(img, text, y, font, scale, colour, thickness=2):
    sz  = cv2.getTextSize(text, font, scale, thickness)[0]
    x   = (W - sz[0]) // 2
    cv2.putText(img, text, (x, y), font, scale, colour, thickness, cv2.LINE_AA)


def draw_frame(sign, frame_idx):
    img = np.full((H, W, 3), BG, dtype=np.uint8)
    t   = frame_idx / FRAMES          # 0 → 1
    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 4)  # 0 → 1 oscillating

    # ── Animated circle ─────────────────────────────────────────────────────────
    cx, cy = W // 2, H // 2 - 60
    r_base = 70
    r      = int(r_base + 18 * pulse)
    # Outer glow ring
    cv2.circle(img, (cx, cy), r + 20, tuple(int(c * 0.35) for c in sign["colour"]), -1, cv2.LINE_AA)
    # Main circle
    cv2.circle(img, (cx, cy), r, sign["colour"], -1, cv2.LINE_AA)
    # Inner highlight
    cv2.circle(img, (cx - 18, cy - 18), r // 3, tuple(min(c + 60, 255) for c in sign["colour"]), -1, cv2.LINE_AA)

    # ── Dots in the circle (simple hand icon placeholder) ───────────────────────
    dot_colour = tuple(min(c + 80, 255) for c in sign["colour"])
    for i in range(5):
        angle  = math.radians(-60 + i * 30)
        dx     = int(math.cos(angle) * (r_base // 2 + int(8 * pulse)))
        dy     = int(math.sin(angle) * (r_base // 2 + int(8 * pulse)))
        cv2.circle(img, (cx + dx, cy - dy - 10), 7, dot_colour, -1, cv2.LINE_AA)

    # ── Text ─────────────────────────────────────────────────────────────────────
    # "DEMO" small label at top
    put_centered(img, "SIGN DEMO",  38, FONT_BOLD, 0.55, MUTED, 1)

    # Big word
    put_centered(img, sign["word"], cy + r + 55, FONT, 2.0, WHITE, 2)

    # Hint (fades in after first half)
    alpha = max(0.0, (t - 0.3) / 0.4)
    if alpha > 0:
        hint_col = tuple(int(c * alpha) for c in CREAM)
        put_centered(img, sign["hint"], cy + r + 110, FONT_BOLD, 0.65, hint_col, 1)

    # ── Bottom progress bar ───────────────────────────────────────────────────────
    bar_y   = H - 22
    bar_w   = int(W * t)
    cv2.rectangle(img, (0, bar_y - 6), (W, bar_y + 6), (50, 40, 44), -1)
    cv2.rectangle(img, (0, bar_y - 6), (bar_w, bar_y + 6), sign["colour"], -1)

    return img


for sign in SIGNS:
    out_path = OUT_DIR / f"{sign['name']}.mp4"

    # Use MJPG into .avi first, then rename — most reliable on Windows.
    # Actually let's just use mp4v and hope for the best; fallback to MJPG.
    for fourcc_str in ["mp4v", "MJPG", "XVID"]:
        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
        suffix = ".mp4" if fourcc_str == "mp4v" else ".avi"
        test_path = OUT_DIR / f"{sign['name']}{suffix}"
        writer = cv2.VideoWriter(str(test_path), fourcc, FPS, (W, H))
        if writer.isOpened():
            break
        writer.release()
        writer = None

    if not writer or not writer.isOpened():
        print(f"[ERROR] Could not open VideoWriter for {sign['name']}")
        continue

    for i in range(FRAMES):
        frame = draw_frame(sign, i)
        writer.write(frame)
    writer.release()
    print(f"Created: {test_path}")

print("\nAll done! Videos are in assets/demo_videos/")
