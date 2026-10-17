"""Make the app icon files from the drawing in static/icon.svg. Mac only (uses the built-in sips tool).

Usage (from the project folder):
    python scripts/make_icons.py

Makes:
    static/apple-touch-icon.png  180 x 180, for the iPhone home screen
    static/favicon.ico           32 x 32, for the browser tab
"""

import struct
import subprocess
import tempfile
from pathlib import Path

STATIC = Path(__file__).resolve().parent.parent / "static"
SOURCE = STATIC / "icon.svg"


def make_png(size, out_path):
    """Draw the SVG as a square PNG of the given size, using the Mac's sips tool."""
    subprocess.run(
        ["sips", "-s", "format", "png", "-z", str(size), str(size), str(SOURCE), "--out", str(out_path)],
        check=True,  # stop with an error if sips fails, instead of carrying on with a missing file
        capture_output=True,
    )


def png_to_ico(png_bytes, size):
    """Wrap a PNG in the .ico format: a 6-byte header, one 16-byte entry describing the image, then the PNG."""
    header = struct.pack("<HHH", 0, 1, 1)  # reserved, type 1 = icon, 1 image
    entry = struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(png_bytes), 6 + 16)
    return header + entry + png_bytes


make_png(180, STATIC / "apple-touch-icon.png")

with tempfile.TemporaryDirectory() as folder:
    small_png = Path(folder) / "favicon.png"
    make_png(32, small_png)
    (STATIC / "favicon.ico").write_bytes(png_to_ico(small_png.read_bytes(), 32))

print("Made static/apple-touch-icon.png and static/favicon.ico")
