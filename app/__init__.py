import sys
import os
import math
import json


def _write_top_level_error(label, exc):
    try:
        with open("/error.log", "w") as _f:
            _f.write(f"=== {label} ===\n")
            sys.print_exception(exc, _f)
    except Exception:
        pass


try:
    sys.path.insert(0, "/system/apps/badge")
    os.chdir("/system/apps/badge")

    badge.mode(HIRES | VSYNC)

    CX = screen.width / 2   # 160
    CY = screen.height / 2  # 120

    screen.antialias = image.X4

    # ---------------------------------------------------------------------------
    # Load config.json
    # ---------------------------------------------------------------------------
    _cfg = {}
    try:
        with open("config.json", "r") as _f:
            _cfg = json.load(_f)
    except Exception:
        pass

    id_name         = _cfg.get("name", "Guest")
    id_role         = _cfg.get("title", "")
    id_company      = _cfg.get("company", "")
    id_bg_hex       = _cfg.get("background_color", "#0298EC")
    id_avatar_file  = _cfg.get("avatar", "avatar.png")
    id_logo_file    = _cfg.get("logo", "logo.png")
    id_linkedin_url = _cfg.get("linkedin_url", "")
    _qr_size        = _cfg.get("qr_size", 0)
    _qr_rows        = _cfg.get("qr_rows", [])

    # ---------------------------------------------------------------------------
    # Parse background hex to rgb
    # ---------------------------------------------------------------------------
    def _hex_to_rgb(h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    _bg_r, _bg_g, _bg_b = _hex_to_rgb(id_bg_hex)

    # ---------------------------------------------------------------------------
    # Load images
    # ---------------------------------------------------------------------------
    id_photo = image.load(id_avatar_file)

    id_logo = None
    try:
        id_logo = image.load(id_logo_file)
    except Exception:
        pass

    # ---------------------------------------------------------------------------
    # Pre-compute QR rect list at boot — no per-frame work
    # Each entry is (px, py) screen coordinates for a dark module
    # ---------------------------------------------------------------------------
    QR_MODULE_PX   = 4
    QR_RENDER_SIZE = _qr_size * QR_MODULE_PX if _qr_size else 0
    QR_X0          = int(CX - QR_RENDER_SIZE / 2)
    QR_Y0          = int(CY - QR_RENDER_SIZE / 2) - 10

    _qr_rects = []

    if _qr_size and _qr_rows:
        for row_idx, row_val in enumerate(_qr_rows):
            for col_idx in range(_qr_size):
                bit_pos = _qr_size - 1 - col_idx
                if (row_val >> bit_pos) & 1:
                    _qr_rects.append((
                        QR_X0 + col_idx * QR_MODULE_PX,
                        QR_Y0 + row_idx * QR_MODULE_PX
                    ))

    # ---------------------------------------------------------------------------
    # Card geometry — full screen identity layout
    # Card: 280x200px, top-left at (20, 20), corner radius 10
    # Vertical stack (y relative to card top-left):
    #   Logo:   y=20, max 120x30px, centered
    #   Photo:  y=58, 80x80px, centered
    #   Name:   y=148, large font
    #   Title:  y=164, small font
    # ---------------------------------------------------------------------------
    CARD_X      = 20
    CARD_Y      = 20
    CARD_W      = 280
    CARD_H      = 200

    # Logo: centered, screen y=28, max 220x44px
    LOGO_Y      = 28
    LOGO_MAX_W  = 220
    LOGO_MAX_H  = 44

    # Two-column row: screen y=82, height=110px
    ROW_Y       = 82

    # Left column — photo
    PHOTO_X     = 36
    PHOTO_W     = 90
    PHOTO_H     = 110

    # Right column — name and title
    TEXT_X      = 140
    NAME_Y      = 112
    TITLE_Y     = 130

    # Press B hint at bottom of card
    HINT_Y      = 204

    id_body    = shape.rounded_rectangle(0, 0, CARD_W, CARD_H, 10)
    id_outline = shape.rounded_rectangle(0, 0, CARD_W, CARD_H, 10).stroke(2)

    hue        = 255
    chroma     = 0
    background = color.rgb(_bg_r, _bg_g, _bg_b)

    show_qr = False

    small_font = pixel_font.load("/system/assets/fonts/winds.ppf")
    large_font = pixel_font.load("/system/assets/fonts/nope.ppf")

except Exception as e:
    _write_top_level_error("BOOT-TIME EXCEPTION", e)
    raise


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def draw_background():
    # Ripple centered on card center (160, 120)
    cx = CARD_X + CARD_W / 2
    cy = CARD_Y + CARD_H / 2
    y = 0
    for _row in range(24):
        x = 0
        for _col in range(32):
            dist = math.sqrt((x + 5 - cx) ** 2 + (y + 5 - cy) ** 2)
            pulse = (math.sin(-badge.ticks / 400 + (dist / 6)) / 2) + 0.5
            pulse = 0.8 + (pulse / 2)
            screen.pen = color.rgb(0, 0, 0, int(100 * pulse))
            screen.rectangle(x, y, 10, 10)
            x += 10
        y += 10


def shadow_text(text, x, y, r=0, g=0, b=0):
    screen.pen = color.rgb(0, 20, 50, 120)
    screen.text(text, vec2(x + 1, y + 1))
    screen.pen = color.rgb(r, g, b)
    screen.text(text, vec2(x, y))


def center_text(text, y, r=0, g=0, b=0):
    w, _ = screen.measure_text(text)
    shadow_text(text, int(CX - w / 2), y, r, g, b)


def change_background(h=None, c=None):
    global background, hue, chroma
    if h:
        hue = (hue + h) % 255
        background = color.oklch(255, chroma, hue)
    if c:
        chroma = max(0, min(255, chroma + c))
        background = color.oklch(255, chroma, hue)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------
def draw_identity():
    screen.pen = background
    screen.clear()
    draw_background()

    # Card shadow
    id_body.transform = mat3().translate(CARD_X + 4, CARD_Y + 4)
    screen.pen = color.rgb(50, 50, 50, 100)
    screen.shape(id_body)

    # Card body
    id_body.transform = mat3().translate(CARD_X, CARD_Y)
    screen.pen = color.rgb(1, 72, 123)
    screen.shape(id_body)

    # Card outline
    id_outline.transform = mat3().translate(CARD_X, CARD_Y)
    screen.pen = color.rgb(2, 152, 236, 180)
    screen.shape(id_outline)

    # --- Logo: centered at top, max 200x28px ---
    if id_logo is not None:
        lx = int(CX - id_logo.width / 2)
        screen.blit(id_logo, vec2(lx, LOGO_Y))
    else:
        screen.font = small_font
        center_text(id_company, LOGO_Y + 10)

    # --- Left column: photo ---
    screen.blit(id_photo, vec2(PHOTO_X, ROW_Y))

    # --- Right column: name and title (white on Denim) ---
    screen.font = large_font
    shadow_text(id_name, TEXT_X, NAME_Y, 255, 255, 255)
    screen.font = small_font
    shadow_text(id_role, TEXT_X, TITLE_Y, 255, 255, 255)

    # --- Press B hint at card bottom ---
    screen.font = small_font
    center_text("press B for LinkedIn", HINT_Y, 180, 210, 255)


def draw_qr():
    screen.pen = color.rgb(_bg_r, _bg_g, _bg_b)
    screen.clear()

    if not _qr_rects:
        screen.font = small_font
        screen.pen = color.rgb(255, 255, 255)
        center_text("no linkedin url set", int(CY))
        return

    # Draw QR from pre-computed rect list
    screen.pen = color.rgb(255, 255, 255)
    for (px, py) in _qr_rects:
        screen.rectangle(px, py, QR_MODULE_PX, QR_MODULE_PX)

    # Handle label
    screen.font = small_font
    label_y = QR_Y0 + QR_RENDER_SIZE + 8
    if id_linkedin_url:
        handle = id_linkedin_url.rstrip("/").split("/")[-1]
        center_text("linkedin.com/in/" + handle, label_y, 255, 255, 255)

    # Hint
    center_text("press B to go back", label_y + 14, 255, 255, 255)


# ---------------------------------------------------------------------------
# BadgeOS entry points
# ---------------------------------------------------------------------------
def init():
    pass


def update():
    global show_qr, background

    # Button B — toggle QR on press-and-release
    if badge.released(BUTTON_B):
        show_qr = not show_qr

    # Background color controls (identity screen only)
    if not show_qr:
        if badge.held(BUTTON_UP):
            change_background(h=5)
        if badge.held(BUTTON_DOWN):
            change_background(h=-5)
        if badge.held(BUTTON_C):
            change_background(c=5)
        if badge.held(BUTTON_A):
            change_background(c=-5)

    if show_qr:
        draw_qr()
    else:
        draw_identity()


def on_exit():
    pass


try:
    init()
    run(update)
except Exception as e:
    _write_top_level_error("RUN-TIME EXCEPTION", e)
    raise
