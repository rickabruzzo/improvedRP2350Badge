#!/usr/bin/env python3
"""
qr_gen.py — Honeycomb London Dinner Badge
Generates a QR code from the linkedin_url in config.json and writes
the matrix back into config.json as qr_size + qr_rows.

Run this once per guest after editing config.json with their LinkedIn URL.
The badge reads qr_rows at boot — no QR library needed on the device.

Usage:
    python qr_gen.py                  (reads/writes config.json in current dir)
    python qr_gen.py path/to/config.json

Requirements:
    pip install qrcode
"""

import sys
import json
import os

try:
    import qrcode
except ImportError:
    print("ERROR: qrcode not installed. Run: pip install qrcode")
    sys.exit(1)


def matrix_to_row_ints(matrix):
    """Encode each row of the QR matrix as an integer bitmask."""
    size = len(matrix)
    rows = []
    for row in matrix:
        v = 0
        for cell in row:
            v = (v << 1) | (1 if cell else 0)
        rows.append(v)
    return size, rows


def generate_qr(url):
    """Generate QR matrix for a URL. Returns (size, row_ints)."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=1
    )
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    return matrix_to_row_ints(matrix)


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"

    if not os.path.exists(config_path):
        print(f"ERROR: config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        cfg = json.load(f)

    url = cfg.get("linkedin_url", "").strip()
    if not url:
        print("ERROR: no 'linkedin_url' found in config.json")
        print('Add: "linkedin_url": "https://linkedin.com/in/username"')
        sys.exit(1)

    print(f"  Generating QR for: {url}")
    size, rows = generate_qr(url)
    print(f"  Matrix: {size}×{size} ({len(rows)} rows, {len(json.dumps(rows))} bytes)")

    cfg["qr_size"] = size
    cfg["qr_rows"] = rows

    with open(config_path, "w") as f:
        json.dump(cfg, f, indent=2)

    print(f"  ✓ Written to {config_path}")


if __name__ == "__main__":
    main()
