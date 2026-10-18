"""Exact phase-interface models; ywz65 with OpenAI Codex, Apache-2.0."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    root = HERE.parents[1]
    records = [(root / r['path'], r) for r in
               json.loads((HERE / 'SOURCES.json').read_text())['files'] if r['usage'] == 'input']
    records += [(HERE / r['path'], r) for r in
                json.loads((HERE / 'VENDOR.json').read_text())['files']]
    for path, record in records:
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == record['sha256'], 'source SHA: ' + str(path))
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        need(hashlib.sha1(blob).hexdigest() == record['git_blob'], 'source blob: ' + str(path))


def load_source():
    # Authenticate BEFORE loading either executable predecessor.
    authenticate()
    modules = []
    for name in ('intervals', 'phase_kernel'):
        spec = importlib.util.spec_from_file_location('r032_pinned_' + name,
                                                      HERE / 'predecessor' / (name + '.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        modules.append(module)
    return modules


def norm2(x):
    return sum(a * a for a in x)


def disk(p):
    s = 1 << p
    return [(a, b) for a in range(-s, s + 1) for b in range(-s, s + 1)
            if a * a + b * b <= s * s]


def error25(x, y, sign=1):
    """25 times squared error in p-grid units for (3+4i sign)/5."""
    a, b = x
    c, d = y
    return (5*c - 3*a + 4*sign*b)**2 + (5*d - 4*sign*a - 3*b)**2


def phase_box(intervals, p, sign=1):
    box = intervals.point(F(3, 5), F(4*sign, 5), p + 8)
    need(box[0].contains(F(3, 5)) and box[1].contains(F(4*sign, 5)),
         'intended rational phase enclosure')
    return box


def refined_product(x, w):
    a, b = x
    u, v = w
    return u*a - v*b, v*a + u*b


def refined_inverse(y, w):
    c, d = y
    u, v = w
    determinant = u*u + v*v
    need(determinant > 0, 'nonzero refined multiplier')
    a, b = u*c + v*d, u*d - v*c
    need(a % determinant == b % determinant == 0, 'refined image membership')
    return a // determinant, b // determinant


def nearest(n, d):
    """Round n/d to nearest, ties toward positive infinity."""
    need(d > 0, 'positive denominator')
    return (2*n + d) // (2*d)


def lift(x, inverse=False):
    """Three rounded shears: bijection of Z^2, NOT of each closed disk."""
    a, b = x
    if inverse:
        a += nearest(b, 2)
        b -= nearest(4*a, 5)
        a += nearest(b, 2)
    else:
        a -= nearest(b, 2)
        b += nearest(4*a, 5)
        a -= nearest(b, 2)
    return a, b


def strict_json_equal(a, b):
    need(type(a) is type(b), 'receipt type mismatch')
    if isinstance(a, dict):
        need(a.keys() == b.keys(), 'receipt keys mismatch')
        for key in a:
            strict_json_equal(a[key], b[key])
    elif isinstance(a, list):
        need(len(a) == len(b), 'receipt length mismatch')
        for x, y in zip(a, b):
            strict_json_equal(x, y)
    else:
        need(a == b, 'receipt value mismatch')
