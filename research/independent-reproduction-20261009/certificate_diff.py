"""Read-only diagnostic for #202 (head 8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d).

`research/source-assisted-v4/verify.py` asserts that its rebuilt certificate equals
the committed one ("Canonical certificate does not reproduce"). This script calls
the package's own `build()`, then prints every leaf of the rebuilt certificate that
differs from the committed `certificate.json`. It writes nothing in the repository.

Usage, from the repository root at the #202 head:
    python -B research/independent-reproduction-20261009/certificate_diff.py
"""
import sys
from pathlib import Path

PKG = Path('research/source-assisted-v4').resolve()
sys.path.insert(0, str(PKG))
import verify  # noqa: E402  (the package's own module)

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
built = verify.build()
committed = verify.read(PKG / 'certificate.json')


def short(x):
    s = repr(x)
    return s if len(s) <= 160 else s[:150] + '...(' + str(len(s)) + ')'


def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((path + '/' + k, 'only-built' if k in a else 'only-committed', short(a.get(k, b.get(k)))))
            else:
                walk(a[k], b[k], path + '/' + k, out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + '[' + str(i) + ']', out)
    elif a != b:
        out.append((path, short(a), short(b)))


diffs = []
walk(built, committed, '', diffs)
print('python', sys.version.split()[0])
print('differing leaves:', len(diffs))
for p, x, y in diffs[:40]:
    print(p, '\n   built    :', x, '\n   committed:', y)
