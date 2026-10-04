# /// script
# requires-python = ">=3.12"
# dependencies = ["reportlab==4.4.5", "pymupdf==1.26.4", "pillow==11.3.0"]
# ///
"""Build and check the native, navigable Speccy micro PDF.

Run from any directory: uv run docs/prospectus/build.py
The generated previews are PDF renders, not separate layout implementations.
"""
from pathlib import Path
import argparse
import hashlib
import json

import fitz
from PIL import Image, ImageDraw
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W, H = 960, 600
INK = "#10181C"
PAPER = "#F2F0E9"
WHITE = "#F6F4EE"
MUTED = "#A3B1B6"
GREY = "#506069"
LINE = "#2B383E"
PALE_LINE = "#D4D7CE"
CORAL, YELLOW, MINT, BLUE = "#F0806B", "#EBD06C", "#79C4B5", "#71B7DB"
CHAPTERS = ["The idea", "The scale", "The controls", "The picture", "The layers",
            "The system", "The evidence", "The next step"]
TEXT_BOXES = []


def fonts(directory):
    fallback = Path(__import__("reportlab").__file__).parent / "fonts"
    for name, filename, substitute in [
        ("Body", "Arial.ttf", "Vera.ttf"),
        ("Bold", "Arial Bold.ttf", "VeraBd.ttf"),
        ("Label", "DIN Alternate Bold.ttf", "VeraBd.ttf"),
    ]:
        path = directory / filename
        pdfmetrics.registerFont(TTFont(name, str(path if path.exists() else fallback / substitute)))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="Bold", italic="Body", boldItalic="Bold")


class Prospectus:
    def __init__(self, path):
        self.c = canvas.Canvas(str(path), pagesize=(W, H), pageCompression=1, invariant=1)
        self.c.setTitle("Speccy micro — Product prospectus")
        self.c.setAuthor("Especcy")
        self.c.setSubject("An eight-page visual prospectus for the compact ZX Spectrum handheld concept")
        self.c.setCreator("Especcy / ReportLab / CAD-based concept visualization")
        self.c.setKeywords("Speccy micro, Especcy, ZX Spectrum, ESP32, product concept, prospectus")
        self.c.setViewerPreference("DisplayDocTitle", "true")
        self.c.setViewerPreference("FitWindow", "true")
        self.c.setPageSize((W, H))
        self.page = 0
        self.renders = json.loads((HERE / "assets/renders.json").read_text())
        photos = json.loads((HERE / "photoreal-prompts.json").read_text())["assets"]
        self.photo_assets = {}
        for name, asset in self.renders["views"].items():
            asset["anchors"].update(photos[name].get("anchor_overrides", {}))
            path = HERE / photos[name]["file"]
            with Image.open(HERE / asset["file"]) as original, Image.open(path) as photo:
                assert photo.mode == "RGBA", f"Missing transparency: {path.name}"
                assert photo.getchannel("A").getextrema() == (0, 255), f"Invalid alpha: {path.name}"
                # Fit the visible product to the CAD frame; generated canvases have different margins.
                # The threshold ignores nearly invisible alpha noise. It does not alter either bitmap.
                ob = original.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
                pb = photo.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
                assert ob and pb, f"Empty product image: {name}"
                scale = min((ob[2] - ob[0]) / (pb[2] - pb[0]), (ob[3] - ob[1]) / (pb[3] - pb[1]))
                left = (ob[0] + ob[2] - (pb[0] + pb[2]) * scale) / 2
                top = (ob[1] + ob[3] - (pb[1] + pb[3]) * scale) / 2
                self.photo_assets[name] = (path, left, top, photo.width * scale, photo.height * scale)

    def rect(self, x, t, width, height, color, radius=0, stroke=None):
        self.c.setFillColor(HexColor(color))
        self.c.setStrokeColor(HexColor(stroke or color))
        if radius:
            self.c.roundRect(x, H - t - height, width, height, radius, fill=1, stroke=bool(stroke))
        else:
            self.c.rect(x, H - t - height, width, height, fill=1, stroke=bool(stroke))

    def line(self, x1, t1, x2, t2, color=LINE, width=0.7):
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(width)
        self.c.line(x1, H - t1, x2, H - t2)

    def text(self, value, x, t, size=14, color=INK, font="Body", tracking=0, align="left"):
        glyphs = pdfmetrics.getFont(font).face.charToGlyph
        assert all(glyphs.get(ord(char), 0) for char in value), f"Unsupported glyph in {font}: {value}"
        width = pdfmetrics.stringWidth(value, font, size) + max(0, len(value) - 1) * tracking
        if align == "right":
            x -= width
        elif align == "center":
            x -= width / 2
        TEXT_BOXES.append((self.page, x, t, x + width, t + size * 1.04, value))
        self.c.saveState()
        self.c.setFillColor(HexColor(color))
        obj = self.c.beginText(x, H - t - size * 0.8)
        obj.setFont(font, size)
        obj.setCharSpace(tracking)
        obj.textOut(value)
        self.c.drawText(obj)
        self.c.restoreState()
        return width

    def para(self, value, x, t, width, size=14, color=GREY, leading=None):
        style = ParagraphStyle("Body", fontName="Body", fontSize=size,
                               leading=leading or size * 1.5, textColor=HexColor(color))
        p = Paragraph(value, style)
        _, height = p.wrap(width, H)
        TEXT_BOXES.append((self.page, x, t, x + width, t + height, value))
        p.drawOn(self.c, x, H - t - height)
        return height

    def heading(self, lines, x=44, t=110, size=60, color=INK):
        for index, value in enumerate(lines):
            self.text(value, x, t + index * size * 1.07, size, color, "Bold", -1.8)

    def label(self, value, x, t, color=GREY, size=10):
        arrow = value.endswith("→")
        width = self.text(value.removesuffix("→").rstrip().upper(), x, t, size, color, "Label", 1.1)
        if arrow:
            ax, ay = x + width + 13, t + size * 0.45
            self.line(ax, ay, ax + 13, ay, color, 0.8)
            self.line(ax + 9, ay - 3, ax + 13, ay, color, 0.8)
            self.line(ax + 9, ay + 3, ax + 13, ay, color, 0.8)

    def spectrum(self, x, t, width=96, height=4):
        for index, color in enumerate((CORAL, YELLOW, MINT, BLUE)):
            self.rect(x + width * index / 4, t, width / 4, height, color)

    def glow(self, x, t, radius, color):
        rgb = HexColor(color)
        self.c.saveState()
        for r in range(int(radius), 0, -3):
            self.c.setFillColor(Color(rgb.red, rgb.green, rgb.blue, alpha=0.008))
            self.c.circle(x, H - t, r, fill=1, stroke=0)
        self.c.restoreState()

    def image(self, name, x, t, width, height):
        asset = self.renders["views"][name]
        ratio = min(width / asset["width"], height / asset["height"])
        iw, ih = asset["width"] * ratio, asset["height"] * ratio
        ix, it = x + (width - iw) / 2, t + (height - ih) / 2
        path, left, top, pw, ph = self.photo_assets[name]
        self.c.drawImage(str(path), ix + left * ratio, H - it - (top + ph) * ratio,
                         pw * ratio, ph * ratio, mask="auto")
        return ix, it, iw, ih

    def anchor(self, name, key, bounds):
        px, py = self.renders["views"][name]["anchors"][key]
        x, t, width, height = bounds
        return x + px * width, t + py * height

    def link(self, destination, x, t, width, height):
        self.c.linkRect("", f"page-{destination}", (x, H - t - height, x + width, H - t), thickness=0)

    def start(self, dark=False):
        self.page += 1
        self.dark = dark
        self.bg, self.fg, self.sub = (INK, WHITE, MUTED) if dark else (PAPER, INK, GREY)
        self.rect(0, 0, W, H, self.bg)
        self.c.bookmarkPage(f"page-{self.page}", fit="XYZ", left=0, top=H, zoom=0)
        self.c.addOutlineEntry(f"{self.page:02d} · {CHAPTERS[self.page - 1]}", f"page-{self.page}", level=0)
        self.label("SPECCY / MICRO", 44, 33, self.fg, 12)
        self.spectrum(169, 39, 46, 3)
        self.label(f"{self.page:02d} / {CHAPTERS[self.page - 1]}", 723, 35, self.sub, 9)
        self.line(44, 65, 916, 65, LINE if dark else PALE_LINE)

    def finish(self):
        self.line(44, 550, 916, 550, LINE if self.dark else PALE_LINE)
        self.label("ESPECCY  /  PRODUCT CONCEPT  /  OCT 2026", 44, 570, self.sub, 8)
        for index in range(1, 9):
            x = 600 + (index - 1) * 33
            self.text(f"{index:02d}", x, 568, 10,
                      self.fg if index == self.page else self.sub, "Bold" if index == self.page else "Body")
            if index == self.page:
                self.rect(x, 585, 13, 2, MINT if self.dark else INK)
            self.link(index, x - 6, 562, 27, 28)
        self.text(f"{self.page} / 8", 916, 569, 10, self.sub, align="right")
        self.c.showPage()

    def cover(self):
        self.start(True)
        self.glow(691, 318, 260, MINT)
        self.glow(892, 124, 190, CORAL)
        self.label("A ZX SPECTRUM HANDHELD CONCEPT", 46, 104, MINT)
        self.heading(["A whole era.", "A tiny form."], 44, 149, 64, WHITE)
        self.para("Meet Speccy micro. A compact, USB-powered<br/>design for a very familiar kind of play.",
                  47, 307, 368, 16, MUTED, 24)
        self.image("hero", 404, 72, 550, 471)
        self.label("24 × 38 × 12 MM", 47, 401, WHITE, 13)
        self.text("Modeled envelope, including button caps.", 47, 426, 11, MUTED)
        self.rect(46, 479, 237, 37, "#233A3C", 3)
        self.label("EXPLORE THE CONCEPT  →", 60, 492, MINT, 10)
        self.link(2, 46, 479, 237, 37)
        self.text("Concept visualization · illustrative screen", 916, 529, 9, MUTED, align="right")
        self.finish()

    def scale(self):
        self.start()
        self.label("THE DIMENSIONS ARE THE DESIGN", 44, 96)
        self.heading(["Small is", "the point."], 44, 126, 61)
        self.para("A complete modeled enclosure in a footprint<br/>of 24 × 38 mm. The 12 mm depth includes<br/>the six button caps; the USB cable is separate.",
                  46, 272, 355, 15)
        self.line(46, 367, 350, 367, PALE_LINE)
        self.text("24", 44, 387, 48, INK, "Bold", -1)
        self.text("38", 149, 387, 48, INK, "Bold", -1)
        self.text("12", 254, 387, 48, INK, "Bold", -1)
        self.label("WIDTH / MM", 47, 448, size=8)
        self.label("LENGTH / MM", 152, 448, size=8)
        self.label("DEPTH / MM", 257, 448, size=8)
        self.text("Dimensions are a packaging target; physical fit is open.", 46, 505, 10, GREY)
        self.rect(417, 89, 499, 439, "#E2E5DD", 6)
        self.image("front", 459, 104, 291, 404)
        self.line(452, 145, 452, 459, GREY)
        self.line(447, 145, 457, 145, GREY)
        self.line(447, 459, 457, 459, GREY)
        self.label("38 MM", 430, 111, size=9)
        self.label("ENLARGED CONCEPT VIEW", 508, 508, size=8)
        # A print-scale footprint, kept independent of the enlarged render.
        mm = 72 / 25.4
        fw, fh = 24 * mm, 38 * mm
        self.rect(793, 293, fw, fh, PAPER, 3 * mm, INK)
        self.spectrum(805, 308, 35, 2)
        self.label("1:1", 806, 333, INK, 16)
        self.label("FOOTPRINT", 798, 367, GREY, 6)
        self.para("Print at 100%<br/>for actual scale.", 787, 421, 104, 10, GREY, 15)
        self.label("THE SIZE OF THE IDEA", 767, 122, GREY, 8)
        self.finish()

    def controls(self):
        self.start(True)
        self.glow(275, 305, 205, BLUE)
        self.label("DESIGNED EXPERIENCE", 528, 101, MINT)
        self.heading(["A familiar", "way to play."], 526, 132, 51, WHITE)
        self.para("The selected workload is original Dizzy on<br/>Spectrum 48K, using Kempston inputs.", 529, 256, 359, 14, MUTED)
        bounds = self.image("front", 100, 96, 364, 441)
        x, t = self.anchor("front", "Screen", bounds)
        self.line(x - 70, t, 91, 185, MINT)
        self.label("0.85-INCH LCD", 44, 151, MINT, 9)
        x, t = self.anchor("front", "Left", bounds)
        self.line(x, t, 88, 383, WHITE)
        self.label("DIRECTION", 44, 398, WHITE, 8)
        for index, (title, body, color) in enumerate([
            ("Four directions", "Up, Down, Left and Right.", WHITE),
            ("Fire", "The game’s action button.", CORAL),
            ("Menu", "Pause, Resume and Restart.", MINT),
        ]):
            row = 332 + index * 63
            self.rect(529, row + 4, 3, 29, color)
            self.text(title, 549, row, 17, WHITE, "Bold")
            self.text(body, 549, row + 25, 12, MUTED)
        self.text("Concept visualization · physical controls remain untested.", 44, 529, 9, MUTED)
        self.finish()

    def picture(self):
        self.start()
        self.label("THE PICTURE, RECONSIDERED", 44, 97)
        self.heading(["128 pixels.", "Still Spectrum."], 44, 127, 57)
        self.para("The 256 × 192 game picture is reduced by<br/>averaging each 2 × 2 pixel block. The result is<br/>128 × 96, centered on a 128 × 128 LCD.",
                  46, 274, 391, 14.5)
        self.rect(45, 370, 111, 44, INK, 3)
        self.text("2:1", 60, 378, 28, PAPER, "Bold")
        self.label("REDUCTION", 179, 388, GREY, 11)
        self.para("Compactness has a visible tradeoff: fine detail<br/>and text lose clarity. Readability on the actual<br/>display remains a prototype test.",
                  46, 443, 385, 12.5)
        self.rect(481, 108, 435, 422, "#E2E5DD", 6)
        self.label("128 × 128 / DISPLAY GRID", 519, 129, INK, 10)
        # Keep the original CAD illustration sharp at an integer 2× enlargement.
        screen = Image.open(ROOT / "hardware/cad/renders/screen_128.png").resize((256, 256), Image.Resampling.NEAREST)
        sx, sy = 532, 183
        self.c.drawImage(ImageReader(screen), sx, H - sy - 256, 256, 256)
        self.line(804, sy, 804, sy + 32, GREY)
        self.line(799, sy, 809, sy, GREY)
        self.line(799, sy + 32, 809, sy + 32, GREY)
        self.label("16 ROWS", 817, sy + 11, GREY, 8)
        self.line(804, sy + 32, 804, sy + 224, INK)
        self.label("96 ROWS", 817, sy + 123, INK, 8)
        self.line(804, sy + 224, 804, sy + 256, GREY)
        self.line(799, sy + 256, 809, sy + 256, GREY)
        self.label("16 ROWS", 817, sy + 235, GREY, 8)
        self.text("128 columns", 660, 454, 11, INK, align="center")
        self.line(532, 448, 788, 448, GREY)
        self.text("CAD artwork shown; firmware uses border-colored rows.", 502, 489, 10, GREY)
        self.text("Illustration, not a game or runtime capture.", 502, 508, 9, GREY)
        self.finish()

    def layers(self):
        self.start()
        self.label("THE MECHANICAL STACK", 44, 97)
        self.heading(["Every layer", "has a reason."], 44, 127, 52)
        self.para("Six layers in the presentation.<br/>One compact assembled envelope.", 46, 252, 290, 14)
        bounds = self.image("exploded", 303, 88, 320, 445)
        rows = [
            ("Front shell", "Front shell", "Screen window and control openings."),
            ("Button plungers", "Six button plungers", "Four directions, Fire and Menu."),
            ("LCD", "0.85-inch LCD", "Connector replaced by eight wires."),
            ("Carrier", "Custom carrier", "Switches, power and external UART."),
            ("ESP32", "ESP32-WROOM-32E-N4", "The selected module below the carrier."),
            ("Rear shell", "Rear shell", "USB opening and programming access."),
        ]
        for index, (key, title, body) in enumerate(rows):
            row = 109 + index * 65
            x, t = self.anchor("exploded", key, bounds)
            self.line(x, t, 636, row + 12, GREY)
            self.c.setFillColor(HexColor(MINT))
            self.c.circle(x, H - t, 2.4, fill=1, stroke=0)
            self.label(f"{6 - index:02d}", 646, row + 3, GREY, 9)
            self.text(title, 677, row, 15, INK, "Bold")
            self.text(body, 677, row + 24, 10.4, GREY)
        self.rect(45, 376, 257, 124, "#E2E5DD", 4)
        self.label("THE STACK STILL NEEDS SAMPLES", 60, 395, GREY, 8)
        self.para("LCD depth, switch travel, wires<br/>and socket clearance need measured<br/>parts and assembly trials.", 60, 417, 222, 12, GREY, 18)
        self.text("Exploded concept visualization · layer spacing is illustrative.", 44, 529, 9, GREY)
        self.finish()

    def system(self):
        self.start(True)
        self.label("THE SELECTED HARDWARE", 44, 97, MINT)
        self.heading(["Small outside.", "Specific inside."], 44, 127, 54, WHITE)
        rows = [
            ("PROCESSOR", "ESP32-WROOM-32E-N4"),
            ("DISPLAY", "Waveshare 0.85″ / GC9107 / SPI"),
            ("POWER", "Micro-B 5 V / 3.3 V LDO"),
            ("CONTROLS", "Four directions / Fire / Menu"),
            ("CONTENT", "48K ROM + selected SNA in flash"),
            ("PROGRAMMING", "External UART / six underside pads"),
        ]
        for index, (label, value) in enumerate(rows):
            row = 273 + index * 36
            self.label(label, 47, row + 3, MUTED, 8)
            self.text(value, 174, row, 12.4, WHITE)
            self.line(47, row + 26, 499, row + 26, LINE)
        self.rect(47, 502, 452, 29, "#233A3C", 3)
        self.text("USB-powered · battery-free · radios disabled", 61, 510, 11, MINT)
        self.glow(724, 260, 176, MINT)
        self.image("back", 558, 107, 340, 318)
        self.label("UNDERSIDE / SERVICE INTERFACE", 573, 435, MINT, 9)
        self.para("The fixture uses manual BOOT / RESET and<br/>gated UART. Its 3V3 pogo pad senses the rail;<br/>it does not supply the device.", 573, 459, 331, 11.5, MUTED, 17)
        self.text("Concept view · fixture operation awaits bench tests", 573, 522, 9, MUTED)
        self.finish()

    def evidence(self):
        self.start()
        self.label("RECORDED REPOSITORY BASELINE", 44, 97)
        self.heading(["A concept with", "real evidence."], 44, 127, 53)
        self.para("The digital and software work is tangible.<br/>A working physical device is still the next proof.", 46, 256, 421, 14)
        for index, (title, body) in enumerate([
            ("Digital geometry", "47 native shapes checked; eight closed STL meshes.<br/>The modeled envelope has been verified."),
            ("Firmware", "Three native test suites pass; two ESP32 modes build.<br/>Original Dizzy starts, walks and jumps on the host."),
            ("Electrical study", "Carrier and fixture pass electrical rule checks.<br/>The placement board is unrouted; DRC remains open."),
        ]):
            row = 335 + index * 65
            self.rect(46, row + 3, 4, 40, INK)
            self.text(title, 64, row, 16, INK, "Bold")
            self.para(body, 64, row + 23, 414, 10.5, GREY, 15)
        self.rect(525, 98, 391, 433, INK, 6)
        self.label("OPEN / PHYSICAL VALIDATION", 549, 122, MINT, 9)
        self.heading(["Next proof:", "the real device."], 548, 161, 36, WHITE)
        for index, (title, body) in enumerate([
            ("Fit & assembly", "Switch travel, USB clearance, LCD and wires."),
            ("Power & heat", "Current, source limits and enclosure temperature."),
            ("Play & readability", "Display, controls and real-time performance."),
            ("Programming & recovery", "Probe access, boot, flash and interrupted power."),
        ]):
            row = 279 + index * 56
            self.c.setStrokeColor(HexColor(MINT))
            self.c.setLineWidth(0.8)
            self.c.circle(556, H - row - 7, 4, stroke=1, fill=0)
            self.text(title, 573, row, 13.5, WHITE, "Bold")
            self.text(body, 573, row + 22, 9.6, MUTED)
        self.text("Recorded evidence, not new hardware test results.", 44, 529, 9, GREY)
        self.finish()

    def closing(self):
        self.start(True)
        self.glow(745, 294, 242, BLUE)
        self.label("A SMALL DESIGN. A CLEAR NEXT STEP.", 44, 101, MINT)
        self.heading(["Make the next", "millimetre count."], 43, 138, 54, WHITE)
        self.para("Explore the source. Measure the selected parts.<br/>Turn the digital study into evidence on the bench.", 47, 275, 481, 15, MUTED)
        self.image("hero", 607, 112, 302, 339)
        self.spectrum(47, 346, 151, 5)
        self.rect(46, 380, 187, 38, "#233A3C", 3)
        self.label("REVIEW THE EVIDENCE  →", 59, 394, MINT, 9)
        self.link(7, 46, 380, 187, 38)
        self.rect(247, 380, 187, 38, "#1B282E", 3)
        self.label("EXPLORE THE SYSTEM  →", 260, 394, WHITE, 9)
        self.link(6, 247, 380, 187, 38)
        self.line(47, 446, 916, 446, LINE)
        self.label("SOURCE NOTES / IN THE REPOSITORY", 47, 464, MUTED, 8)
        self.text("Product & verification", 47, 486, 11, WHITE, "Bold")
        self.text("docs/product-brief.md · docs/verification.md", 47, 505, 9.8, MUTED)
        self.text("CAD, firmware & electronics", 483, 486, 11, WHITE, "Bold")
        self.text("hardware/cad/ · firmware/ · hardware/electronics/", 483, 505, 9.8, MUTED)
        self.text("Concept prospectus · physical acceptance, price, release date and distribution rights remain open.",
                  47, 529, 9, MUTED)
        self.finish()

    def build(self):
        for make_page in (self.cover, self.scale, self.controls, self.picture,
                          self.layers, self.system, self.evidence, self.closing):
            make_page()
        self.c.save()


def verify_and_preview(path):
    """Check the document itself; leave a small, runnable regression check."""
    doc = fitz.open(path)
    assert len(doc) == 8, f"Expected 8 pages, got {len(doc)}"
    assert len(doc.get_toc()) == 8, "Missing chapter bookmarks"
    assert [item[2] for item in doc.get_toc()] == list(range(1, 9)), "Bad bookmark destinations"
    texts, links, fonts_found = [], 0, set()
    photo_pages = {0: "hero", 1: "front", 2: "front", 4: "exploded", 5: "back", 7: "hero"}
    for index, page in enumerate(doc):
        assert tuple(page.rect) == (0, 0, W, H), f"Wrong page size: {index + 1}"
        text = page.get_text()
        assert len(text.strip()) > 220, f"Missing selectable content on page {index + 1}"
        assert "\ufffd" not in text, f"Broken glyph on page {index + 1}"
        texts.append(text)
        if index in photo_pages:
            images = page.get_image_info()
            assert len(images) == 1, f"Missing product photo on page {index + 1}"
            with Image.open(HERE / "assets" / f"{photo_pages[index]}-photo.png") as photo:
                assert (images[0]["width"], images[0]["height"]) == photo.size, f"Wrong image on page {index + 1}"
        page_links = page.get_links()
        assert len(page_links) >= 8, f"Missing navigation on page {index + 1}"
        for link in page_links:
            assert link["kind"] == fitz.LINK_GOTO, f"Unexpected link type on page {index + 1}"
            assert 0 <= link["page"] < len(doc), f"Bad link destination on page {index + 1}"
        links += len(page_links)
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    assert page.rect.contains(fitz.Rect(span["bbox"])), f"Clipped PDF text: {span['text']}"
        for font in page.get_fonts():
            if font[1] != "n/a":
                assert doc.extract_font(font[0])[3], f"Font not embedded: {font[3]}"
                fonts_found.add(font[3])
    required = {
        1: ["24 × 38 × 12", "Concept visualization"],
        2: ["physical fit is open", "1:1"],
        3: ["Dizzy", "Kempston", "Resume and Restart"],
        4: ["256 × 192", "128 × 96", "border-colored"],
        5: ["eight wires", "measured"],
        6: ["ESP32-WROOM-32E-N4", "senses the rail"],
        7: ["unrouted", "DRC remains open", "real-time performance"],
        8: ["distribution rights remain open"],
    }
    for number, phrases in required.items():
        for phrase in phrases:
            assert phrase in texts[number - 1], f"Missing required claim on page {number}: {phrase}"
    for page, x1, t1, x2, t2, text in TEXT_BOXES:
        assert 0 <= x1 < x2 <= W and 0 <= t1 < t2 <= H, f"Text outside page {page}: {text}"
    overlaps = []
    for i, a in enumerate(TEXT_BOXES):
        for b in TEXT_BOXES[i + 1:]:
            if a[0] != b[0]:
                continue
            width = min(a[3], b[3]) - max(a[1], b[1])
            height = min(a[4], b[4]) - max(a[2], b[2])
            if width > 1 and height > 1:
                overlaps.append([a[0], a[5], b[5]])
    assert not overlaps, f"Overlapping text boxes: {overlaps}"
    previews = HERE / "previews"
    previews.mkdir(exist_ok=True)
    sheet = Image.new("RGB", (1560, 2048), "#D8DDD8")
    draw = ImageDraw.Draw(sheet)
    for index, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img.save(previews / f"{index + 1:02d}.png", optimize=True)
        thumb = img.resize((744, 465), Image.Resampling.LANCZOS)
        x, y = 24 + (index % 2) * 768, 32 + (index // 2) * 504
        sheet.paste(thumb, (x, y))
        draw.text((x, y + 474), f"{index + 1:02d}  {CHAPTERS[index]}", fill=INK)
    sheet.save(HERE / "preview.jpg", quality=92)
    report = {
        "file": path.name, "pages": len(doc), "page_size_pt": [W, H],
        "chapter_bookmarks": len(doc.get_toc()), "internal_links": links,
        "embedded_fonts": sorted(fonts_found), "selectable_text": True,
        "text_within_page": True, "text_box_overlaps": overlaps,
        "required_claims_present": True, "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "source_model_sha256": hashlib.sha256((ROOT / "hardware/cad/models/speccy_micro.blend").read_bytes()).hexdigest(),
        "photoreal_assets": {name: hashlib.sha256((HERE / "assets" / f"{name}-photo.png").read_bytes()).hexdigest()
                            for name in ("hero", "front", "exploded", "back")},
        "visualization_mode": "AI-enhanced CAD-based concept",
        "photoreal_images_verified_in_pdf": True,
    }
    (HERE / "checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, default=Path("/System/Library/Fonts/Supplemental"))
    args = parser.parse_args()
    fonts(args.font_dir)
    params = json.loads((ROOT / "hardware/cad/parameters.json").read_text())
    assert [params["case"][key] for key in ("width", "length", "overall_height")] == [24, 38, 12], "Refresh prospectus dimensions"
    assert params["esp32"]["part"] == "ESP32-WROOM-32E-N4", "Refresh processor specification"
    assert params["lcd"]["pixels"] == [128, 128] and len(params["buttons"]) == 6, "Refresh display/controls"
    output = HERE / "speccy-micro-prospectus.pdf"
    Prospectus(output).build()
    verify_and_preview(output)


if __name__ == "__main__":
    main()
