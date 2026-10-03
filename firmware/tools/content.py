#!/usr/bin/env python3
"""Validate local content or generate an original, distributable 48K diagnostic."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROM_SIZE, RAM_SIZE, SNA_SIZE = 16384, 49152, 49179


def validate(rom, sna):
    if len(rom) != ROM_SIZE:
        raise ValueError("ROM must contain exactly 16384 bytes")
    if len(sna) != SNA_SIZE:
        raise ValueError("Only 49179-byte 48K SNA snapshots are supported")
    if sna[25] > 2 or sna[26] > 7 or sna[19] & ~4:
        raise ValueError("Invalid SNA interrupt mode, border or IFF2")
    sp = struct.unpack_from("<H", sna, 23)[0]
    if sp < 0x4000 or sp == 0xffff:
        raise ValueError("SNA return address must fit in RAM")


def diagnostic():
    rom = bytearray(ROM_SIZE)
    rom[0x38:0x3b] = bytes([0xfb, 0xed, 0x4d])  # EI; RETI
    sna = bytearray(SNA_SIZE)
    sna[19], sna[25], sna[26] = 4, 1, 1
    struct.pack_into("<H", sna, 23, 0xc000)
    struct.pack_into("<H", sna, 27 + 0x8000, 0x8000)  # saved PC on stack
    # EI; HALT; read Kempston; store mask; set one attribute and border; loop.
    program = bytes([0xfb, 0x76, 0xdb, 0x1f, 0x32, 0x00, 0x5b,
                     0xe6, 7, 0xf6, 0x40, 0x32, 0x00, 0x58,
                     0xd3, 0xfe, 0xc3, 0x01, 0x80])
    sna[27 + 0x4000:27 + 0x4000 + len(program)] = program
    for y in range(192):
        addr = ((y & 0xc0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
        for col in range(32):
            sna[27 + addr + col] = 0xaa if y & 1 else 0x55
    for row in range(24):
        for col in range(32):
            sna[27 + 0x1800 + row * 32 + col] = ((row // 3) & 1) << 6 | ((col // 4) & 7) | ((row // 3) & 7) << 3
    return bytes(rom), bytes(sna)


def read_exact(path, size):
    p = Path(path)
    if p.stat().st_size != size:
        raise ValueError(f"{p.name} must contain exactly {size} bytes")
    return p.read_bytes()


def write_changed(path, data):
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("diagnostic", "dizzy"), default="diagnostic")
    p.add_argument("--rom")
    p.add_argument("--snapshot")
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    try:
        if args.mode == "diagnostic":
            if args.rom or args.snapshot:
                raise ValueError("Local content requires --mode dizzy")
            rom, sna = diagnostic()
        else:
            if not args.rom or not args.snapshot:
                raise ValueError("Dizzy mode requires --rom and --snapshot; no game assets are bundled")
            rom = read_exact(args.rom, ROM_SIZE)
            sna = read_exact(args.snapshot, SNA_SIZE)
        validate(rom, sna)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_changed(args.output_dir / "spectrum48.rom", rom)
        write_changed(args.output_dir / "game48.sna", sna)
        manifest = {"mode": args.mode, "snapshot_format": "48K SNA", "rom_bytes": len(rom),
                    "snapshot_bytes": len(sna), "rom_sha256": hashlib.sha256(rom).hexdigest(),
                    "snapshot_sha256": hashlib.sha256(sna).hexdigest(),
                    "provenance": "Project-authored diagnostic" if args.mode == "diagnostic" else "User-supplied local ROM and Dizzy snapshot; distribution permission not inferred"}
        write_changed(args.output_dir / "content.json", (json.dumps(manifest, indent=2) + "\n").encode())
    except (OSError, ValueError) as error:
        p.error(str(error))


if __name__ == "__main__":
    main()
