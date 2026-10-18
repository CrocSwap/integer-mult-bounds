"""Exact I/O, source binding and Gaussian-integer fixture arithmetic.

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
The P112 model and accounting convention are credited in README.md.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
GEOMETRY = "research/p112-single-lift/reference-geometry.json"
PAIR = (4, 6)
NORMALS = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2)]
NAMES = ["axis4", "axis6", "plus", "minus", "generic"]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(raw):
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, "duplicate JSON key")
            out[k] = v
        return out

    def invalid(value):
        raise ValueError("invalid JSON constant: "+value)

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def source_bytes(manifest=None):
    pins = load((HERE/"SOURCES.json").read_bytes()) if manifest is None else manifest
    need(pins["base_commit"] == BASE, "source base changed")
    live = {r["path"] for r in pins["files"] if r["usage"] == "input"}
    need(live == {GEOMETRY, "research/p112-single-lift/SOURCES.json"}, "live input inventory")
    output = {}
    for row in pins["files"]:
        path = row["path"]
        need(not Path(path).is_absolute() and ".." not in Path(path).parts, "invalid source path")
        raw = subprocess.check_output(["git", "show", BASE+":"+path], cwd=ROOT)
        blob = subprocess.check_output(["git", "rev-parse", BASE+":"+path], cwd=ROOT, text=True).strip()
        need(row["git_blob"] == blob, "source blob: "+path)
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: "+path)
        if row["usage"] == "input":
            need((ROOT/path).read_bytes() == raw, "working input drift: "+path)
        else:
            need(row["usage"] == "provenance", "invalid usage")
        output[path] = raw
    return output


def gadd(a, b):
    return a[0]+b[0], a[1]+b[1]


def gscale(a, coefficient):
    return a[0]*coefficient, a[1]*coefficient


def gmul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def inverse_transpose(matrix):
    need(len(matrix) == 3 and all(len(row) == 3 for row in matrix), "GL3 shape")
    rows = [[Fraction(v) for v in row]+[Fraction(r == c) for c in range(3)]
            for r, row in enumerate(matrix)]
    for c in range(3):
        pivot = next((r for r in range(c, 3) if rows[r][c]), None)
        need(pivot is not None, "singular factor change")
        rows[c], rows[pivot] = rows[pivot], rows[c]
        scalar = rows[c][c]
        rows[c] = [x/scalar for x in rows[c]]
        for r in range(3):
            if r != c:
                scalar = rows[r][c]
                rows[r] = [a-scalar*b for a, b in zip(rows[r], rows[c])]
    need(all(v.denominator == 1 for row in rows for v in row), "fixture inverse not integral")
    return [[int(rows[c][r+3]) for c in range(3)] for r in range(3)]


def factors(x, u, v, matrix, phases=((1, 0), (1, 0), (1, 0)), conjugate_error=False):
    inv = inverse_transpose(matrix)
    left, right = [], []
    for row, uu, vv in zip(x, u, v):
        a, b = row[PAIR[0]], row[PAIR[1]]
        ll, rr = [], []
        for c in range(3):
            need(sum(t*t for t in phases[c]) == 1, "nonunit fixture phase")
            ll.append(gmul((a*matrix[0][c]+b*matrix[1][c]+matrix[2][c]*uu[0],
                            matrix[2][c]*uu[1]), phases[c]))
            phase = phases[c] if conjugate_error else (phases[c][0], -phases[c][1])
            rr.append(gmul((a*inv[0][c]+b*inv[1][c]+inv[2][c]*vv[0],
                            inv[2][c]*vv[1]), phase))
        left.append(ll)
        right.append(rr)
    return left, right, inv


def identity_check(x, u, v, left, right):
    for i in range(112):
        for j in range(112):
            got = (0, 0)
            for c in range(3):
                got = gadd(got, gmul(left[i][c], right[j][c]))
            target = gadd((x[i][PAIR[0]]*x[j][PAIR[0]]+x[i][PAIR[1]]*x[j][PAIR[1]], 0),
                          gmul(u[i], v[j]))
            need(got == target, "ordinary-transpose factor identity")
    return 112*112


def power_screen(q):
    need(isinstance(q, Fraction) and 0 < q <= 1, "power exponent outside (0,1]")
    p, d = q.numerator, q.denominator
    ratio_power = Fraction(3, 2)**d * Fraction(3, 4)**p
    need(ratio_power >= Fraction(9, 8)**d, "COPY ratio bound")
    return {"q": str(q), "ratio_to_power_denominator": str(ratio_power),
            "floor_to_power_denominator": str(Fraction(9, 8)**d)}
