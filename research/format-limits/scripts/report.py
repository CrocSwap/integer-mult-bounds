"""Shared paths and PASS/FAIL reporting for the checks of research/format-limits.

Every check prints one line per claim: 'PASS <claim-id> <detail>' or 'FAIL <claim-id> <detail>', and finish() exits
with status 1 if any claim failed.  Paths: PKG is this package, DATA its data/ directory, REPO the repository root
(the package lives at REPO/research/format-limits; files of main are read from REPO and pinned in DEPENDS.json).
"""
import gzip
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE.parent
DATA = PKG / 'data'
VENDOR = DATA / 'vendor'
REPO = pathlib.Path(os.environ.get('FORMAT_LIMITS_REPO', PKG.parent.parent)).resolve()

_failed = []


def check(cid, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + cid + ('  ' + str(detail) if detail != '' else ''), flush=True)
    if not ok:
        _failed.append(cid)
    return ok


def near(x, expected, places):
    """x agrees with a value printed to `places` decimals: |x - expected| <= 0.6 * 10^-places (half a unit of the last
    printed digit plus slack, so a float computed with a different library build cannot flip a rounding boundary)."""
    return abs(float(x) - float(expected)) <= 0.6 * 10.0 ** (-places)


def near_all(xs, expected, places):
    xs, expected = list(xs), list(expected)
    return len(xs) == len(expected) and all(
        (x == e) if isinstance(e, int) and not isinstance(e, bool) and p is None else near(x, e, p)
        for x, e, p in zip(xs, expected, places))


def finish():
    if _failed:
        print('FAILED CLAIMS: ' + ' '.join(_failed), flush=True)
        sys.exit(1)


def load_json(path):
    path = pathlib.Path(path)
    if path.suffix == '.gz':
        return json.loads(gzip.decompress(path.read_bytes()))
    return json.loads(path.read_text())


def main_file(rel):
    """a file of the repository's main branch (pinned by sha256 in DEPENDS.json)."""
    p = REPO / rel
    if not p.exists():
        sys.exit('missing file of main: %s (run from a checkout of the whole repository)' % rel)
    return p
