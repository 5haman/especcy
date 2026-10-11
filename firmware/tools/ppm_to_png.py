#!/usr/bin/env python3
"""Convert a binary PPM frame from speccy-host to PNG, scaled by whole pixels."""
import argparse
from pathlib import Path
import re
import struct
import zlib


def read_ppm(data):
    header = re.match(rb"P6\s+(\d+)\s+(\d+)\s+(\d+)\s", data)
    if not header or int(header[3]) != 255:
        raise ValueError("Expected an 8-bit binary PPM (P6)")
    width, height = int(header[1]), int(header[2])
    pixels = data[header.end():]
    if width == 0 or height == 0 or len(pixels) != width * height * 3:
        raise ValueError("PPM pixel data does not match its header")
    return width, height, pixels


def png(width, height, rows):
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    raw = b"".join(b"\0" + row for row in rows)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ppm", type=Path)
    p.add_argument("png", type=Path)
    p.add_argument("--scale", type=int, choices=range(1, 9), default=1, metavar="1-8")
    args = p.parse_args()
    try:
        width, height, pixels = read_ppm(args.ppm.read_bytes())
        rows = []
        for y in range(height):
            row = pixels[y * width * 3:(y + 1) * width * 3]
            wide = b"".join(row[x:x + 3] * args.scale for x in range(0, len(row), 3))
            rows += [wide] * args.scale
        args.png.write_bytes(png(width * args.scale, height * args.scale, rows))
    except (OSError, ValueError) as error:
        p.error(str(error))


if __name__ == "__main__":
    main()
