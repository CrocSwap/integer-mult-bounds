"""Independent exact Gaussian-matrix operator and endpoint controls.

The matrix arithmetic does not use tableau update formulas.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from functools import lru_cache
from model import IDENTITY, FREE

N = 8


def rot(a, b, p):
    return ((a, b), (-b, a), (-a, -b), (b, -a))[p % 4]


def normalize(e, re, im, projective=False):
    while e and all(value % 2 == 0 for value in re+im):
        e -= 1
        re, im = [v//2 for v in re], [v//2 for v in im]
    variants = []
    for p in range(4 if projective else 1):
        entries = [rot(a, b, p) for a, b in zip(re, im)]
        variants.append((e, tuple(a for a, _ in entries), tuple(b for _, b in entries)))
    return min(variants)


def identity():
    return normalize(0, [int(i == j) for i in range(N) for j in range(N)], [0]*64)


@lru_cache(maxsize=40_000)
def multiply(a, b, projective=False):
    ea, ar, ai = a
    eb, br, bi = b
    re, im = [0]*64, [0]*64
    for i in range(N):
        for k in range(N):
            x, y = ar[8*i+k], ai[8*i+k]
            if x == y == 0:
                continue
            for j in range(N):
                u, v = br[8*k+j], bi[8*k+j]
                re[8*i+j] += x*u-y*v
                im[8*i+j] += x*v+y*u
    return normalize(ea+eb, re, im, projective)


def pauli(value):
    x, z, p = value & 7, (value >> 3) & 7, value >> 6
    re, im = [0]*64, [0]*64
    for col in range(8):
        re[8*(col ^ x)+col], im[8*(col ^ x)+col] = rot(1, 0, p+2*((z & col).bit_count() % 2))
    return normalize(0, re, im)


@lru_cache(None)
def operator(op):
    name, a, b = op
    re, im = [0]*64, [0]*64
    if name == "C":
        for col in range(8):
            re[8*col+col], im[8*col+col] = 1, 1
            re[8*(col ^ a)+col], im[8*(col ^ a)+col] = 1, -1
        return normalize(1, re, im)
    for col in range(8):
        row, p = col, 0
        if name == "S":
            p = (col >> a) & 1
        elif name == "X":
            row ^= 1 << a
        elif name == "Z":
            p = 2*((col >> a) & 1)
        elif name == "CX":
            row ^= ((col >> a) & 1) << b
        elif name == "CZ":
            p = 2*((col >> a) & 1)*((col >> b) & 1)
        else:
            raise ValueError(op)
        re[8*row+col], im[8*row+col] = rot(1, 0, p)
    return normalize(0, re, im)


@lru_cache(maxsize=10_000)
def signature(matrix):
    # Recover all six conjugated generators by GP = P'G, independently of
    # the optimized tableau update formulas used by the search.
    images = []
    for generator in IDENTITY:
        wanted = multiply(matrix, pauli(generator))
        matches = [value for value in range(256) if multiply(pauli(value), matrix) == wanted]
        assert len(matches) == 1
        images.append(matches[0])
    return tuple(images)


def independent_frame(g):
    basis = [value & 63 for value in g]
    result = 0
    for value in range(64):
        image = 0
        for i in range(6):
            if value & (1 << i):
                image ^= basis[i]
        if image & 7 == 0:
            result |= 1 << value
    return result


def execute(program):
    unit = normalize(*identity(), projective=True)
    rows = [{(r, unit): Q(1)} for r in range(3)]
    for gate in program:
        if gate[0] == 'mix3':
            changed = []
            for r in range(3):
                row = {}
                for c in range(3):
                    for key, value in rows[c].items():
                        row[key] = row.get(key, 0)+gate[1+3*r+c]*value
                changed.append({key: value for key, value in row.items() if value})
            rows = changed
        else:
            op = ('C', gate[2], 0) if gate[0] == 'paid' else FREE[gate[2]]
            changed = {}
            for (column, matrix), value in rows[gate[1]].items():
                key = column, multiply(operator(op), matrix, True)
                changed[key] = changed.get(key, 0)+value
            rows[gate[1]] = {key: value for key, value in changed.items() if value}
    return [{(col, signature(matrix)): value for (col, matrix), value in row.items()} for row in rows]
