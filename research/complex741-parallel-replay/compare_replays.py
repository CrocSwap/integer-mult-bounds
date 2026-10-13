#!/usr/bin/env python3
"""Compare two #741 complex replay directories file by file.

Every file in either tree is compared as bytes, then (for .gz) as decompressed bytes,
then (for JSON) structurally, with differences reported by JSON key path. A JSON
difference is accepted only when
  - its key path contains a timing key (TIMING), or
  - both values are SHA-256 digests of the same relative file in the respective trees,
    and that file is itself identical or accepted (checked to a fixed point).
Logs (human-readable progress) must have the same number of lines; each differing line
pair must agree in text and integers, may differ in decimal floats (elapsed times), and
may differ in 64-hex tokens only as digests of the same accepted file. Exit status 0
means every difference was accepted; rejected ones are listed under "other".
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

TIMING = ('seconds', 'elapsed_seconds')  # elapsed wall-clock time
FLOAT = re.compile(r'\d+\.\d+(?:[eE][-+]?\d+)?')
HEX = re.compile(r'[0-9a-f]{64}')
TOKEN = re.compile(r'(\b[0-9a-f]{64}\b|\d+\.\d+(?:[eE][-+]?\d+)?)')


def load(path):
    raw = path.read_bytes()
    return gzip.decompress(raw) if path.suffix == '.gz' else raw


def diff(x, y, at=''):
    """[(path, x_value, y_value)] for every differing leaf."""
    if isinstance(x, dict) and isinstance(y, dict):
        out = [(at + '/' + k, x.get(k), y.get(k)) for k in sorted(set(x) ^ set(y))]
        for k in sorted(set(x) & set(y)):
            out += diff(x[k], y[k], at + '/' + k)
        return out
    if isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        return [d for i, (a, b) in enumerate(zip(x, y)) for d in diff(a, b, f'{at}/{i}')]
    return [] if x == y else [(at or '/', x, y)]


def index(root, files):
    out = {}
    for rel in files:
        p = root / rel
        if p.is_file():
            for blob in {p.read_bytes(), load(p)}:
                out.setdefault(hashlib.sha256(blob).hexdigest(), set()).add(rel)
    return out


def compare(a, b):
    a, b = Path(a), Path(b)
    files = sorted({p.relative_to(a).as_posix() for p in a.rglob('*') if p.is_file()}
                   | {p.relative_to(b).as_posix() for p in b.rglob('*') if p.is_file()})
    explained, pending = set(), {}
    report = {'files': len(files), 'identical_bytes': 0, 'identical_payload': 0,
              'accepted': {}, 'logs': {}, 'other': {}}
    for rel in files:
        pa, pb = a / rel, b / rel
        if not (pa.is_file() and pb.is_file()):
            report['other'][rel] = 'missing in ' + ('first' if not pa.is_file() else 'second')
        elif pa.read_bytes() == pb.read_bytes():
            report['identical_bytes'] += 1
            explained.add(rel)
        elif load(pa) == load(pb):
            report['identical_payload'] += 1
            explained.add(rel)
        elif rel.endswith('.log'):
            la, lb = pa.read_text(encoding='utf-8').splitlines(), pb.read_text(encoding='utf-8').splitlines()
            pending[rel] = [('log', x, y) for x, y in zip(la, lb) if x != y] if len(la) == len(lb) else None
        else:
            try:
                pending[rel] = diff(json.loads(load(pa)), json.loads(load(pb)))
            except ValueError:
                report['other'][rel] = 'non-JSON content differs'
    ia, ib = index(a, files), index(b, files)

    def same_file_digest(x, y):
        return bool(ia.get(x, set()) & ib.get(y, set()) & explained)

    def line_ok(x, y):
        # Text and integers must match; decimal floats (elapsed times in progress lines)
        # may differ; a 64-hex token may differ only as the digest of an explained file.
        sx, sy = TOKEN.split(x), TOKEN.split(y)
        if len(sx) != len(sy) or sx[0::2] != sy[0::2]:
            return False
        return all(u == v or (FLOAT.fullmatch(u) and FLOAT.fullmatch(v))
                   or (HEX.fullmatch(u) and HEX.fullmatch(v) and same_file_digest(u, v))
                   for u, v in zip(sx[1::2], sy[1::2]))

    def ok(d):
        path, x, y = d
        if path == 'log':
            return line_ok(x, y)
        if set(path.split('/')) & set(TIMING):
            return True
        return isinstance(x, str) and isinstance(y, str) and same_file_digest(x, y)

    changed = True
    while changed:
        changed = False
        for rel in list(pending):
            if pending[rel] is not None and all(map(ok, pending[rel])):
                ds = pending.pop(rel)
                if rel.endswith('.log'):
                    report['logs'][rel] = len(ds)
                else:
                    report['accepted'][rel] = [d[0] for d in ds]
                explained.add(rel)
                changed = True
    for rel, ds in pending.items():
        report['other'][rel] = ('line counts differ' if ds is None else
                                [d[1] + ' | ' + d[2] if d[0] == 'log' else d[0] for d in ds if not ok(d)])
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('first', type=Path)
    ap.add_argument('second', type=Path)
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    report = compare(a.first, a.second)
    text = json.dumps(report, indent=1, sort_keys=True) + '\n'
    if a.out:
        a.out.write_text(text, encoding='utf-8')
    else:
        sys.stdout.write(text)
    print(f"{report['files']} files: {report['identical_bytes']} identical bytes, "
          f"{report['identical_payload']} identical decompressed, {len(report['accepted'])} JSON files differ "
          f"only in timing or digests of such files, {len(report['logs'])} logs differ only in elapsed "
          f"times or such digests, {len(report['other'])} other differences", file=sys.stderr)
    sys.exit(1 if report['other'] else 0)


if __name__ == '__main__':
    main()
