#!/usr/bin/env python3
"""Check relative links and heading anchors in the repository's tracked Markdown files.

External URLs are not fetched. Run from any directory inside the Git checkout.
"""
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SRC = re.compile(r"""<(?:img|a)\s[^>]*(?:src|href)=["']([^"']+)["']""")
FENCE = re.compile(r"^(```|~~~)")


def anchors(path):
    """GitHub-style heading anchors, including -1/-2 suffixes for duplicates."""
    seen, result, fenced = {}, set(), False
    for line in path.read_text().splitlines():
        if FENCE.match(line):
            fenced = not fenced
        heading = None if fenced else re.match(r"#{1,6}\s+(.*?)\s*#*\s*$", line)
        if heading:
            text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading[1])
            slug = re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            result.add(slug if count == 0 else f"{slug}-{count}")
    return result


def main():
    files = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z", "*.md"], check=True,
                           capture_output=True, text=True).stdout.split("\0")
    errors, checked = [], 0
    for name in filter(None, files):
        path = REPO / name
        fenced = False
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if FENCE.match(line):
                fenced = not fenced
            if fenced:
                continue
            for target in LINK.findall(line) + SRC.findall(line):
                if re.match(r"[a-z][a-z0-9+.-]*:", target, re.I):
                    continue
                checked += 1
                file_part, _, fragment = target.partition("#")
                resolved = (path.parent / unquote(file_part)).resolve() if file_part else path
                if not resolved.exists():
                    errors.append(f"{name}:{number}: missing target {target}")
                elif fragment and resolved.suffix == ".md" and fragment not in anchors(resolved):
                    errors.append(f"{name}:{number}: missing anchor {target}")
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print(f"DOC_LINKS_OK: {checked} relative links in {len(list(filter(None, files)))} Markdown files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
