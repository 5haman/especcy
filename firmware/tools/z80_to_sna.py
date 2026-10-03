#!/usr/bin/env python3
"""Convert an extended 48K Z80 snapshot to SNA offline; never runs on the device."""
import argparse
from pathlib import Path
import struct

from content import ROM_SIZE, validate


def expand_page(data):
    out = bytearray()
    at = 0
    while at < len(data):
        if data[at:at + 2] == b"\xed\xed":
            if at + 4 > len(data) or data[at + 2] == 0:
                raise ValueError("Invalid Z80 run-length encoding")
            out.extend(bytes([data[at + 3]]) * data[at + 2])
            at += 4
        else:
            out.append(data[at])
            at += 1
        if len(out) > 16384:
            raise ValueError("Z80 page expands beyond 16 KiB")
    if len(out) != 16384:
        raise ValueError("Z80 page must expand to 16 KiB")
    return out


def convert(data):
    if len(data) < 35 or len(data) > 65536 or data[6:8] != b"\0\0":
        raise ValueError("Only extended 48K Z80 v2/v3 snapshots are supported")
    header_size = struct.unpack_from("<H", data, 30)[0]
    if header_size not in (23, 54, 55) or len(data) < 32 + header_size:
        raise ValueError("Invalid extended Z80 header")
    if data[34] not in (0, 1) or data[37] & 0x80 or data[36]:
        raise ValueError("Snapshot requires hardware other than a plain 48K Spectrum")
    if bool(data[27]) != bool(data[28]) or data[29] & 3 > 2:
        raise ValueError("SNA cannot represent this Z80 interrupt state")
    pages = {}
    at = 32 + header_size
    while at < len(data):
        if at + 3 > len(data):
            raise ValueError("Truncated Z80 page header")
        length, page = struct.unpack_from("<HB", data, at)
        at += 3
        if page not in (8, 4, 5) or page in pages:
            raise ValueError("Unexpected or duplicate Z80 RAM page")
        size = 16384 if length == 0xffff else length
        if at + size > len(data):
            raise ValueError("Truncated Z80 RAM page")
        encoded = data[at:at + size]
        pages[page] = encoded if length == 0xffff else expand_page(encoded)
        at += size
    if set(pages) != {8, 4, 5}:
        raise ValueError("Z80 snapshot must contain all three 48K RAM pages")
    ram = bytearray(pages[8] + pages[4] + pages[5])
    header = bytearray(27)
    header[0] = data[10]
    for target, source in ((1, 19), (3, 17), (5, 15), (9, 4), (11, 13),
                           (13, 2), (15, 23), (17, 25)):
        header[target:target + 2] = data[source:source + 2]
    header[7:9] = bytes([data[22], data[21]])
    header[19] = 4 if data[28] else 0
    flags = 1 if data[12] == 255 else data[12]  # Z80 format's legacy flags convention
    header[20] = (data[11] & 127) | (flags & 1) << 7
    header[21:23] = bytes([data[1], data[0]])
    sp = (struct.unpack_from("<H", data, 8)[0] - 2) & 0xffff
    if sp < 0x4000 or sp == 0xffff:
        raise ValueError("SNA return address must fit in RAM")
    struct.pack_into("<H", header, 23, sp)
    header[25], header[26] = data[29] & 3, (flags >> 1) & 7
    ram[sp - 0x4000:sp - 0x4000 + 2] = data[32:34]
    sna = bytes(header + ram)
    validate(bytes(ROM_SIZE), sna)
    return sna


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 65536:
            raise ValueError("Z80 input exceeds the 48K converter limit")
        args.output.write_bytes(convert(args.input.read_bytes()))
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
