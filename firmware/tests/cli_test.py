"""End-to-end CLI and content-boundary checks, without commercial content."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

exe, content, generator = sys.argv[1:]
content = Path(content)
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    base = [exe, "--rom", str(content / "spectrum48.rom"), "--snapshot", str(content / "game48.sna"),
            "--output", str(td / "frame.ppm")]
    for mask, expected in [(0,0), (1,1), (2,2), (4,4), (8,8), (16,16), (9,9), (3,0), (12,0), (31,16)]:
        run = subprocess.run(base + ["--frames", "4", "--buttons", str(mask)], capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
        metrics = json.loads(run.stdout)
        assert metrics["frames"] == 4 and metrics["kempston"] == expected
        assert 4 * 69888 <= metrics["emulated_cycles"] < 4 * 69888 + 128
        image = (td / "frame.ppm").read_bytes()
        assert image.startswith(b"P6\n128 128\n255\n") and len(image) == 15 + 128 * 128 * 3
    for args in (["--frames", "-1"], ["--frames", "1x"], ["--buttons", "32"], ["--frames", "1000001"],
                 ["--unknown", "x"], ["--frames"], ["--save-snapshot"]):
        bad = subprocess.run(base + args, capture_output=True, text=True)
        assert bad.returncode != 0 and bad.stderr, args
    saved = td / "saved.sna"
    capture = subprocess.run(base + ["--start-dizzy", "--frames", "30", "--save-snapshot", str(saved)],
                             capture_output=True, text=True)
    assert capture.returncode == 0 and saved.stat().st_size == 49179, capture.stderr
    reload = subprocess.run(base + ["--snapshot", str(saved), "--frames", "4", "--buttons", "16"],
                            capture_output=True, text=True)
    assert reload.returncode == 0 and json.loads(reload.stdout)["kempston"] == 16, reload.stderr
    sna = bytearray((content / "game48.sna").read_bytes())
    sna[25] = 3
    (td / "bad.sna").write_bytes(sna)
    bad = subprocess.run(base + ["--snapshot", str(td / "bad.sna")], capture_output=True, text=True)
    assert bad.returncode != 0 and "Invalid SNA" in bad.stderr
    pack = [sys.executable, generator, "--output-dir", str(td / "pack")]
    assert subprocess.run(pack, capture_output=True).returncode == 0
    metadata = json.loads((td / "pack/content.json").read_text())
    assert metadata["mode"] == "diagnostic"
    assert metadata["rom_sha256"] == hashlib.sha256((td / "pack/spectrum48.rom").read_bytes()).hexdigest()
    assert subprocess.run(pack + ["--mode", "dizzy"], capture_output=True).returncode != 0
    assert subprocess.run(pack + ["--mode", "dizzy", "--rom", str(content / "spectrum48.rom"),
        "--snapshot", str(td / "bad.sna")], capture_output=True).returncode != 0
    assert subprocess.run(pack + ["--mode", "dizzy", "--rom", str(content / "spectrum48.rom"),
        "--snapshot", str(content / "game48.sna")], capture_output=True).returncode == 0
    assert json.loads((td / "pack/content.json").read_text())["mode"] == "dizzy"
print("PASS: CLI images/metrics, all five inputs, opposing directions, invalid arguments/content, asset packaging")
