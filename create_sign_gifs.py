"""
create_sign_gifs.py
Generates animated GIF demo clips for each TSL sign lesson.
Uses only Pillow (pip install Pillow) — no codec issues.

Signs:
  hungry  – C-hand at throat, moves down to stomach
  sleepy  – hand slides down over face (eye level → chin)
  drink   – C-shape cup mime, wrist rises to mouth
  yes     – fist nods up and down twice
"""

from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

# ── Output dir ─────────────────────────────────────────────────────────────────
OUT = Path(__file__).parent / "assets" / "demo_videos"
OUT.mkdir(parents=True, exist_ok=True)

# ── Canvas constants ───────────────────────────────────────────────────────────
W, H    = 400, 500
FPS     = 24           # frames per second
LOOP_S  = 3.0          # seconds per loop
N       = int(FPS * LOOP_S)

# ── Palette ────────────────────────────────────────────────────────────────────
BG          = (254, 250, 247)       # warm off-white
SKIN        = (240, 195, 160)
SKIN_DARK   = (210, 160, 120)
SHIRT       = (158, 94, 106)        # brand warm red
SHIRT_SHAD  = (122, 69, 80)
HAIR        = (60,  40,  30)
EYE         = (40,  30,  25)
ARROW       = (158, 94, 106, 180)   # semi-transparent brand red
TRAIL       = (200, 140, 150, 80)


# ══════════════════════════════════════════════════════════════════════════════
# Easing helpers
# ══════════════════════════════════════════════════════════════════════════════
def ease_in_out(t):
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

def lerpxy(p0, p1, t):
    return (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t))

def ease_lerp(p0, p1, t):
    return lerpxy(p0, p1, ease_in_out(t))


# ══════════════════════════════════════════════════════════════════════════════
# Avatar drawing
# ══════════════════════════════════════════════════════════════════════════════
CX = W // 2   # center X
HEAD_Y   = 110
HEAD_R   = 48
NECK_TOP = HEAD_Y + HEAD_R
NECK_BOT = NECK_TOP + 18
SHLDR_Y  = NECK_BOT + 10

# Torso bounding box
TORSO = (CX - 62, SHLDR_Y, CX + 62, SHLDR_Y + 160)

# Shoulder socket positions
L_SHLDR = (TORSO[0] + 8,  SHLDR_Y + 8)
R_SHLDR = (TORSO[2] - 8,  SHLDR_Y + 8)


def draw_rounded_rect(draw, box, radius, fill, outline=None, width=2):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)


def draw_avatar_base(draw):
    """Draws the static parts: torso, head, hair, face. Returns without arms."""
    # ── Torso ──────────────────────────────────────────────────────────────────
    draw_rounded_rect(draw, TORSO, 20, SHIRT_SHAD)
    draw_rounded_rect(draw,
        (TORSO[0] + 4, TORSO[1], TORSO[2] - 4, TORSO[3] - 6),
        16, SHIRT)

    # ── Neck ───────────────────────────────────────────────────────────────────
    draw.rectangle([(CX - 14, NECK_TOP), (CX + 14, NECK_BOT)], fill=SKIN)

    # ── Head ───────────────────────────────────────────────────────────────────
    # Hair cap (slightly taller ellipse)
    draw.ellipse([
        (CX - HEAD_R, HEAD_Y - HEAD_R - 12),
        (CX + HEAD_R, HEAD_Y + HEAD_R * 0.3)
    ], fill=HAIR)
    # Face
    draw.ellipse([
        (CX - HEAD_R, HEAD_Y - HEAD_R),
        (CX + HEAD_R, HEAD_Y + HEAD_R)
    ], fill=SKIN, outline=SKIN_DARK, width=2)

    # ── Eyes ───────────────────────────────────────────────────────────────────
    for ex in (CX - 14, CX + 14):
        draw.ellipse([(ex - 5, HEAD_Y - 8), (ex + 5, HEAD_Y + 2)], fill=EYE)
        # Highlight
        draw.ellipse([(ex + 1, HEAD_Y - 6), (ex + 3, HEAD_Y - 4)], fill=(255,255,255))

    # ── Nose ────────────────────────────────────────────────────────────────────
    draw.ellipse([(CX - 3, HEAD_Y + 8), (CX + 3, HEAD_Y + 14)], fill=SKIN_DARK)

    # ── Mouth (neutral slight smile) ────────────────────────────────────────────
    draw.arc([(CX - 10, HEAD_Y + 16), (CX + 10, HEAD_Y + 26)], 10, 170, fill=SKIN_DARK, width=2)


ARM_W   = 13   # half-width of arm
HAND_R  = 18   # hand circle radius


def draw_arm(draw, shoulder, elbow, hand_pos, hand_type="c"):
    """
    Draws: upper arm (shoulder→elbow), lower arm (elbow→hand), hand shape.
    hand_type: 'c' = C-shape cup, 'fist' = closed fist, 'open' = flat
    """
    sx, sy = shoulder
    ex, ey = elbow
    hx, hy = hand_pos

    # Upper arm (thick line)
    draw.line([(sx, sy), (ex, ey)], fill=SKIN_DARK, width=ARM_W + 2)
    draw.line([(sx, sy), (ex, ey)], fill=SKIN,      width=ARM_W)

    # Lower arm
    draw.line([(ex, ey), (hx, hy)], fill=SKIN_DARK, width=ARM_W + 2)
    draw.line([(ex, ey), (hx, hy)], fill=SKIN,      width=ARM_W)

    # Hand
    if hand_type == "c":
        # C-shape: open oval
        draw.ellipse([(hx - HAND_R, hy - HAND_R), (hx + HAND_R, hy + HAND_R)],
                     fill=SKIN, outline=SKIN_DARK, width=3)
        # Thumb stub
        draw.ellipse([(hx - HAND_R - 8, hy - 8), (hx - HAND_R + 4, hy + 8)],
                     fill=SKIN, outline=SKIN_DARK, width=2)
    elif hand_type == "fist":
        draw.ellipse([(hx - HAND_R, hy - HAND_R + 4), (hx + HAND_R, hy + HAND_R)],
                     fill=SKIN, outline=SKIN_DARK, width=3)
        # Knuckle lines
        for i in range(3):
            lx = hx - 8 + i * 8
            draw.line([(lx, hy - HAND_R + 4), (lx, hy - HAND_R + 12)], fill=SKIN_DARK, width=2)
    else:  # open / flat
        draw.ellipse([(hx - HAND_R, hy - HAND_R), (hx + HAND_R, hy + HAND_R)],
                     fill=SKIN, outline=SKIN_DARK, width=3)


def draw_motion_arrow(draw, frm, to, color=ARROW):
    """Draws a directional arrow from frm→to."""
    fx, fy = frm
    tx, ty  = to
    # Shaft
    draw.line([(fx, fy), (tx, ty)], fill=color[:3], width=3)
    # Arrowhead
    angle  = math.atan2(ty - fy, tx - fx)
    size   = 12
    for da in (math.pi * 0.75, -math.pi * 0.75):
        ax = int(tx + size * math.cos(angle + da))
        ay = int(ty + size * math.sin(angle + da))
        draw.line([(tx, ty), (ax, ay)], fill=color[:3], width=3)


def static_left_arm(draw):
    """Draws the resting left arm (always the same)."""
    ls = L_SHLDR
    le = (ls[0] - 12, ls[1] + 65)
    lh = (ls[0] - 6,  ls[1] + 125)
    draw_arm(draw, ls, le, lh, "open")


# ══════════════════════════════════════════════════════════════════════════════
# GIF builder
# ══════════════════════════════════════════════════════════════════════════════
def make_gif(name, frame_fn, label, hint, n_frames=N):
    frames = []
    for i in range(n_frames):
        t = i / n_frames   # 0..1
        img  = Image.new("RGBA", (W, H), BG + (255,))
        draw = ImageDraw.Draw(img, "RGBA")

        # Light background circle (focus zone)
        draw.ellipse([(CX - 130, 80), (CX + 130, H - 80)],
                     fill=(240, 228, 232, 120))

        frame_fn(draw, t)

        # ── Label ────────────────────────────────────────────────────────────
        try:
            font_big  = ImageFont.truetype("arial.ttf", 26)
            font_hint = ImageFont.truetype("arial.ttf", 15)
        except:
            font_big  = ImageFont.load_default()
            font_hint = font_big

        # Word label
        bb = draw.textbbox((0, 0), label, font=font_big)
        tw = bb[2] - bb[0]
        draw.text(((W - tw) // 2, H - 72), label, fill=SHIRT, font=font_big)

        # Hint
        bb2 = draw.textbbox((0, 0), hint, font=font_hint)
        tw2 = bb2[2] - bb2[0]
        draw.text(((W - tw2) // 2, H - 40), hint, fill=(150, 120, 130), font=font_hint)

        frames.append(img.convert("RGB"))

    dur_ms = int(1000 / FPS)
    out_path = OUT / f"{name}.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=dur_ms,
        optimize=False,
    )
    print(f"Saved {out_path}  ({n_frames} frames @ {FPS}fps)")


# ══════════════════════════════════════════════════════════════════════════════
# Sign animations
# ══════════════════════════════════════════════════════════════════════════════

def anim_hungry(draw, t):
    """
    Hungry (หิว): C-handshape at throat, slides straight down to stomach.
    Slight pause at the bottom, return up.
    """
    # t in [0,1]: 0→0.4 = down, 0.4→0.6 = pause, 0.6→1.0 = up
    if t < 0.4:
        phase = ease_in_out(t / 0.4)
        start   = (CX + 30, NECK_TOP + 10)   # throat
        end_pos = (CX + 28, TORSO[3] - 30)   # stomach
        hp = ease_lerp(start, end_pos, phase)
        arrow_to = (CX + 28, TORSO[3] - 30)
        draw_motion_arrow(draw, (CX + 28, TORSO[1] + 10), arrow_to, ARROW)
    elif t < 0.6:
        hp = (CX + 28, TORSO[3] - 30)
    else:
        phase = ease_in_out((t - 0.6) / 0.4)
        start   = (CX + 28, TORSO[3] - 30)
        end_pos = (CX + 30, NECK_TOP + 10)
        hp = ease_lerp(start, end_pos, phase)

    # Elbow interpolates naturally
    rs = R_SHLDR
    elbow = (rs[0] + 30, rs[1] + 50)

    draw_avatar_base(draw)
    static_left_arm(draw)
    draw_arm(draw, rs, elbow, hp, "c")


def anim_sleepy(draw, t):
    """
    Sleepy (ง่วง): Open hand at eye level, slides down over face.
    """
    EYE_POS  = (CX - 10, HEAD_Y - 5)
    CHIN_POS = (CX - 10, NECK_TOP + 5)
    REST_POS = (CX - 10, TORSO[1] + 20)

    if t < 0.15:
        # Start at rest, move up to eye
        phase = ease_in_out(t / 0.15)
        hp = ease_lerp(REST_POS, EYE_POS, phase)
    elif t < 0.5:
        # Slide down from eye to chin
        phase = ease_in_out((t - 0.15) / 0.35)
        hp = ease_lerp(EYE_POS, CHIN_POS, phase)
        draw_motion_arrow(draw, EYE_POS, CHIN_POS, ARROW)
    elif t < 0.65:
        hp = CHIN_POS
    else:
        # Return to rest
        phase = ease_in_out((t - 0.65) / 0.35)
        hp = ease_lerp(CHIN_POS, REST_POS, phase)

    rs    = R_SHLDR
    elbow = (rs[0] - 10, rs[1] + 60)

    draw_avatar_base(draw)
    static_left_arm(draw)
    draw_arm(draw, rs, elbow, hp, "open")


def anim_drink(draw, t):
    """
    Drink (ดื่ม): C-shape cup at chest, arcs up to mouth.
    """
    MOUTH_POS = (CX + 20, HEAD_Y + 22)
    CHEST_POS = (CX + 30, TORSO[1] + 50)

    if t < 0.1:
        # Brief hold at chest
        hp = CHEST_POS
    elif t < 0.45:
        phase = ease_in_out((t - 0.1) / 0.35)
        hp = ease_lerp(CHEST_POS, MOUTH_POS, phase)
        # Arrow curving up
        draw_motion_arrow(draw, CHEST_POS, MOUTH_POS, ARROW)
    elif t < 0.65:
        # Pause at mouth
        hp = MOUTH_POS
    else:
        phase = ease_in_out((t - 0.65) / 0.35)
        hp = ease_lerp(MOUTH_POS, CHEST_POS, phase)

    rs    = R_SHLDR
    elbow = (rs[0] + 15, rs[1] + 70)

    draw_avatar_base(draw)
    static_left_arm(draw)
    draw_arm(draw, rs, elbow, hp, "c")


def anim_yes(draw, t):
    """
    Yes (ใช่): Fist nods up-down twice.
    """
    UP_POS   = (CX + 20, TORSO[1] + 10)
    DOWN_POS = (CX + 20, TORSO[1] + 45)

    # Two nods in the loop
    phase_in_nod = (t * 2) % 1.0   # two full cycles
    if phase_in_nod < 0.5:
        hp = ease_lerp(UP_POS, DOWN_POS, ease_in_out(phase_in_nod * 2))
    else:
        hp = ease_lerp(DOWN_POS, UP_POS, ease_in_out((phase_in_nod - 0.5) * 2))

    rs    = R_SHLDR
    elbow = (rs[0] + 10, rs[1] + 55)

    # Small vertical arrow hint
    draw_motion_arrow(draw, (CX + 30, TORSO[1] - 10), (CX + 30, TORSO[1] + 55), ARROW)

    draw_avatar_base(draw)
    static_left_arm(draw)
    draw_arm(draw, rs, elbow, hp, "fist")


# ══════════════════════════════════════════════════════════════════════════════
# Run
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    make_gif("hungry", anim_hungry, "HUNGRY",
             "C-hand at throat \u2192 slides to stomach")
    make_gif("sleepy",  anim_sleepy,  "SLEEPY",
             "Hand slides down over face")
    make_gif("drink",   anim_drink,   "DRINK",
             "Cup hand rises to mouth")
    make_gif("yes",     anim_yes,     "YES",
             "Fist nods up and down")
    print("\nAll done! GIFs saved in assets/demo_videos/")
