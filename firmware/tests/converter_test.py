"""Synthetic snapshot conversion cases; no Spectrum ROM or game needed."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from z80_to_sna import convert, expand_page


def snapshot(version=54, compressed=True):
    header = bytearray(32 + version)
    header[:30] = bytes(range(30))
    header[6:8] = b"\0\0"
    header[27:30] = bytes([1, 1, 2])
    struct.pack_into("<H", header, 8, 0xc002)
    struct.pack_into("<H", header, 30, version)
    struct.pack_into("<H", header, 32, 0x9123)
    pages = bytearray()
    for page in (4, 5, 8):
        encoded = b"\xed\xed\xff" + bytes([page])
        encoded = encoded * 64 + b"\xed\xed\x40" + bytes([page]) if compressed else bytes([page]) * 16384
        pages.extend(struct.pack("<HB", len(encoded) if compressed else 0xffff, page) + encoded)
    return header + pages


class ConverterTests(unittest.TestCase):
    def test_registers_and_pages(self):
        for version in (23, 54, 55):
            for compressed in (True, False):
                source = snapshot(version, compressed)
                sna = convert(source)
                self.assertEqual(len(sna), 49179)
                self.assertEqual(sna[:23], bytes([10, 19, 20, 17, 18, 15, 16, 22, 21,
                                                 4, 5, 13, 14, 2, 3, 23, 24, 25, 26, 4, 11, 1, 0]))
                self.assertEqual(sna[23:27], b"\0\xc0\x02\x06")
                self.assertEqual(sna[27], 8)
                self.assertEqual(sna[27 + 16384], 4)
                self.assertEqual(sna[27 + 32768:27 + 32770], b"\x23\x91")
                self.assertEqual(sna[-1], 5)

    def test_invalid_headers_and_pages(self):
        original = snapshot()
        variants = [original[:34], original[:-1], original + b"\0", original[:86],
                    original + original[86:]]
        for at, value in ((6, 1), (30, 22), (34, 3), (36, 255), (37, 128), (27, 0), (29, 3), (88, 7)):
            bad = original.copy()
            bad[at] = value
            variants.append(bad)
        for bad in variants:
            with self.assertRaises(ValueError):
                convert(bad)
        for sp in (1, 0x4000, 0x4001):
            bad = original.copy()
            struct.pack_into("<H", bad, 8, sp)
            with self.assertRaises(ValueError):
                convert(bad)

    def test_encoding_limits(self):
        self.assertEqual(expand_page(b"\xed\x00" * 8192), b"\xed\x00" * 8192)
        for encoded in (b"\xed\xed", b"\xed\xed\0\x55", b"\x00" * 16383,
                        b"\x00" * 16385, b"\xed\xed\xff\x55" * 65):
            with self.assertRaises(ValueError):
                expand_page(encoded)


if __name__ == "__main__":
    unittest.main()
