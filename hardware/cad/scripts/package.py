"""Build the downloadable CAD package from the tracked hardware/cad files.

Run with Python 3 inside a Git checkout. The archive is reproducible: entries
are sorted, permissions are fixed, and every timestamp is SOURCE_DATE_EPOCH or
the time of the last commit that changed a packaged file.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import zipfile

REPO = Path(__file__).resolve().parents[3]
CAD = 'hardware/cad'
LICENSES = ['LICENSE', 'LICENSE-HARDWARE', 'LICENSE-DOCS']
PREFIX = 'speccy_micro/'


def git(*args):
    return subprocess.run(['git', '-C', str(REPO), *args], check=True,
                          capture_output=True, text=True).stdout


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=REPO / 'dist' / 'speccy_micro_package.zip')
    p.add_argument('--allow-dirty', action='store_true', help='package uncommitted changes')
    args = p.parse_args()
    if not args.allow_dirty and git('status', '--porcelain', '--', CAD, *LICENSES).strip():
        p.error(f'{CAD} or a license file has uncommitted changes; commit them or pass --allow-dirty')
    sources = {PREFIX + path[len(CAD) + 1:]: REPO / path
               for path in git('ls-files', '-z', '--', CAD).split('\0') if path}
    sources.update({PREFIX + name: REPO / name for name in LICENSES})
    epoch = int(os.environ.get('SOURCE_DATE_EPOCH') or git('log', '-1', '--format=%ct', '--', CAD, *LICENSES))
    stamp = time.gmtime(max(epoch, 315532800))[:6]  # ZIP dates start in 1980.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, 'w') as archive:
        for name in sorted(sources):
            info = zipfile.ZipInfo(name, stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, sources[name].read_bytes(), compresslevel=9)
    with zipfile.ZipFile(args.output) as archive:
        if archive.testzip() is not None or sorted(archive.namelist()) != sorted(sources):
            raise SystemExit('Archive verification failed')
        for name, path in sources.items():
            if archive.read(name) != path.read_bytes():
                raise SystemExit(f'Archive entry differs from its source: {name}')
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print('CAD_PACKAGE_OK', json.dumps({'entries': len(sources), 'sha256': digest, 'path': str(args.output)}))


if __name__ == '__main__':
    main()
