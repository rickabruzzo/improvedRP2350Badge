# Personalized Executive Badge for Tufty RP2350

A personalized ID badge app for the Pimoroni Tufty RP2350 running BadgeOS v4.03 (MicroPython/badgeware). Displays a guest's photo, name, title, and company logo on a polished animated card, with a QR code on the flip side linking to any URL — LinkedIn, a personal site, whatever you like.

Designed for event gifting or conference use. Each badge runs identical code; only the config file and assets change per person.

---

## Files

| File | Lives on | Purpose |
|---|---|---|
| `__init__.py` | Badge | Main app — identical across all badges |
| `config.json` | Badge | Per-guest data — the only file you change per person |
| `avatar.png` | Badge | Headshot, cropped to 90×110px |
| `logo.png` | Badge | Company or event logo, prepped via `logo_prep.py` |
| `icon.png` | Badge | Launcher icon — must stay in app root |
| `logo_prep.py` | Mac/PC only | Resizes logos to badge spec |
| `qr_gen.py` | Mac/PC only | Generates QR matrix from a URL into config.json |

---

## One-Time Setup

```bash
pip install qrcode pillow
```

---

## Per-Guest Workflow

### 1. Edit config.json

```json
{
  "name": "Jane Smith",
  "title": "Chief Technology Officer",
  "company": "Acme Corp",
  "background_color": "#25303E",
  "avatar": "avatar.png",
  "logo": "logo.png",
  "linkedin_url": "https://www.linkedin.com/in/janesmith/"
}
```

`background_color` is optional — omit it to use the default set in `__init__.py`.

### 2. Generate the QR code

Reads `linkedin_url` from config.json and writes the QR matrix back in as `qr_size` and `qr_rows`. No QR library needed on the badge itself.

```bash
python3 qr_gen.py
```

To point at a different config file:

```bash
python3 qr_gen.py path/to/config.json
```

### 3. Prep the company logo

Resizes to fit within 220×44px, maintains aspect ratio, preserves transparency. Output is always a PNG.

```bash
python3 logo_prep.py their_logo.png --out logo.png
```

Batch mode — outputs to `./prepped/`:

```bash
python3 logo_prep.py logo1.png logo2.png logo3.png
```

### 4. Prep the headshot

Manually crop the photo to **90×110px**, face centered. Save as `avatar.png`.

### 5. Deploy to badge

Copy these five files to the app folder on the badge:

```
__init__.py
config.json
avatar.png
logo.png
icon.png
```

`logo_prep.py` and `qr_gen.py` stay on your computer — they are not needed on the badge.

---

## Customizing Colors

### Background color

Set `background_color` in `config.json`. This is the animated ripple field behind the card:

```json
"background_color": "#1a1a2e"
```

> **Note:** `config.json` always wins. If you change the default in `__init__.py` but see no change on the badge, make sure `config.json` is updated too.

### Card body color

Edit this line in `__init__.py`:

```python
screen.pen = color.rgb(1, 72, 123)
```

Replace the RGB values with whatever color you want for the inset card panel.

### Text color

Name and title render white by default. To change them, find these lines in `draw_identity()`:

```python
shadow_text(id_name, TEXT_X, NAME_Y, 255, 255, 255)
shadow_text(id_role, TEXT_X, TITLE_Y, 255, 255, 255)
```

The last three arguments are R, G, B.

---

## Badge Controls

| Button | Action |
|---|---|
| B | Toggle between identity card and QR code screen |
| Up / Down | Cycle background hue |
| A | Decrease background chroma (toward grey) |
| C | Increase background chroma (more saturated) |

---

## Hardware

- **Device:** Pimoroni Tufty RP2350
- **OS:** BadgeOS v4.03
- **Screen:** 320×240px landscape
- **App path on badge:** `/system/apps/badge/`
