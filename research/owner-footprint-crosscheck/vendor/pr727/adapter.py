#!/usr/bin/env python3
"""Opt-in exact footprint masks for the pinned PR626 independent owner checker.

Agastya Sondhi (@TMM2009), with substantial OpenAI Codex assistance.
Apache-2.0. Original checker: Chafik Boukhalfa/chafreaky; see NOTICE.md.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = Path('research/complex-k492-owner-repair')
CHECKER = PACKAGE / 'extras/check_owner_map.py'
INTERVALS = PACKAGE / 'extras/exact_intervals.py'

# Exact, counted edits to the source-pinned checker. Its remaining code executes
# unchanged, including every need(), actual native width and moment calculation.
REPLACEMENTS = (
    ('used=defaultdict(set);', 'used=defaultdict(int);'),
    ("cells=set(range(r['offset'],r['offset']+w));",
     "cells=interval_mask(r['offset'],w);"),
    ('cells==set(range(len(cells)))', 'is_prefix(cells)'),
    ('len(cells)<cap:idle[cap-len(cells)]',
     'cells.bit_count()<cap:idle[cap-cells.bit_count()]'),
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def interval_mask(offset, width):
    """Encode range(offset, offset + width); caller has checked nonnegativity."""
    return ((1 << width) - 1) << offset


def is_prefix(mask):
    """For a nonnegative integer, test whether its one-bits form [0, k)."""
    return mask & (mask + 1) == 0


def origins():
    return json.loads((HERE / 'ORIGINS.json').read_text())


def check_pins(root=ROOT, sources_only=False):
    for name, record in origins()['files'].items():
        if sources_only and name not in (str(CHECKER), str(INTERVALS)):
            continue
        require(hashlib.sha256((root / name).read_bytes()).hexdigest()
                == record['sha256'], 'source/input pin mismatch: ' + name)


def transformed(source):
    for old, new in REPLACEMENTS:
        require(source.count(old) == 1, 'adapter anchor changed: ' + old)
        source = source.replace(old, new)
    return source


def run(root, engine, checker_args):
    # Data may be changed and repinned for new experiments. The inherited
    # checker performs its own plan/owner/native bindings. Benchmark inputs are
    # separately pinned in ORIGINS.json before and after the complete run.
    check_pins(root, sources_only=True)
    path = root / CHECKER
    source = path.read_text()
    if engine == 'masks':
        source = transformed(source)
    elif engine != 'sets':
        raise ValueError('unknown engine')
    old_argv = sys.argv
    sys.argv = [str(path), *checker_args]
    try:
        exec(compile(source, str(path), 'exec'), {
            '__name__': '__main__', '__file__': str(path),
            'interval_mask': interval_mask, 'is_prefix': is_prefix,
        })
    finally:
        sys.argv = old_argv


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--engine', choices=['sets', 'masks'], default='masks')
    args, rest = ap.parse_known_args()
    run(args.root.resolve(), args.engine, rest)


if __name__ == '__main__':
    main()
