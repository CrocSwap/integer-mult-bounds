#!/usr/bin/env python3
"""Static inventory of locale-dependent text I/O in the verification surface.

Locale-dependent means the codec used for decoding/encoding text is chosen by
the platform (``Path.read_text()``/``write_text()``/``open()`` without an
explicit ``encoding=``).  On a UTF-8 (Linux) host this silently matches the
repository's UTF-8 files; on Windows/cp1252 or any non-UTF-8 locale the same
calls either raise ``UnicodeDecodeError`` or decode to mojibake, so a check
can fail (or, worse, verify the wrong text) depending on the host.

This tool is read-only evidence: it classifies sites but changes nothing.
"""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SURFACE = ('scripts', 'research', 'tests', 'formal')

READ_TEXT = re.compile(r'\.read_text\(\s*\)')
WRITE_TEXT = re.compile(r'\.write_text\(')
OPEN_CALL = re.compile(r'\bopen\(')


def scan():
    sites = {}
    for base in SURFACE:
        root = ROOT / base
        if not root.is_dir():
            continue
        for path in sorted(root.rglob('*.py')):
            if '__pycache__' in path.parts:
                continue
            try:
                lines = path.read_text(encoding='utf-8').splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            hits = []
            for number, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith('#'):
                    continue
                if 'encoding=' in line:
                    continue  # codec pinned explicitly
                if READ_TEXT.search(line):
                    hits.append(dict(line=number, kind='read_text()', source=stripped[:160]))
                elif WRITE_TEXT.search(line):
                    hits.append(dict(line=number, kind='write_text()', source=stripped[:160]))
                elif OPEN_CALL.search(line) and "'rb'" not in line and '"rb"' not in line \
                        and "'wb'" not in line and '"wb"' not in line and "'r+b'" not in line:
                    hits.append(dict(line=number, kind='open()', source=stripped[:160]))
            if hits:
                sites[path.relative_to(ROOT).as_posix()] = hits
    return sites


def non_ascii_files():
    """Files in the surface whose bytes are not 7-bit ASCII (need UTF-8)."""
    out = []
    for base in SURFACE:
        root = ROOT / base
        if not root.is_dir():
            continue
        for path in sorted(root.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if any(b > 0x7F for b in data):
                out.append(path.relative_to(ROOT).as_posix())
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    sites = scan()
    payload = dict(
        surface=list(SURFACE),
        file_count=len(sites),
        site_count=sum(len(v) for v in sites.values()),
        non_ascii_files=non_ascii_files(),
        sites=sites,
    )
    text = json.dumps(payload, indent=1, sort_keys=True) + '\n'
    if a.output:
        out = a.output if a.output.is_absolute() else ROOT / a.output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8', newline='\n')
    counts = {}
    for path, hits in sites.items():
        counts[path.split('/')[0]] = counts.get(path.split('/')[0], 0) + len(hits)
    print(f"locale-dependent text I/O: {payload['site_count']} sites in "
          f"{payload['file_count']} files {counts}")
    print(f"non-ASCII files in surface: {len(payload['non_ascii_files'])}")


if __name__ == '__main__':
    main()
