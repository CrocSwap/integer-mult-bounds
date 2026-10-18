# Apache-2.0; cxnmai with substantial OpenAI assistance.
"""Exact scalar model; no predecessor implementation imports."""
import copy
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
INDEX = 3  # assignment seed modulo nine


def load():
    with gzip.open(SOURCE, 'rt') as f:
        return json.load(f)


def bits(n):
    while n:
        b = n & -n
        yield b.bit_length() - 1
        n ^= b


def apply(values, gates):
    for _, dst, srcs in gates:
        for src in srcs:
            values[dst] ^= values[src]
    return values


def raw(w):
    v = w['v']
    values = apply([1 << r for r in range(2*v+w['R'])], w['A'])
    for t, row in enumerate(w['scatter']):
        for k in row:
            values[v+t] ^= values[w['ret'][k]]
    return apply(values, w['B'])


def rebuild(original, operands):
    w = copy.deepcopy(original)
    w['A'][-9+INDEX][2] = sorted(operands)
    v = w['v']
    values = raw(w)
    w['D'] = [[0, v+t, list(bits(values[v+t] >> (2*v)))] for t in range(v)]
    for g in w['D']:
        g[2] = [s+2*v for s in g[2]]
    w['C'] = [[1, d, list(ss)] for _, d, ss in reversed(w['A']+w['B'])
              if not v <= d < 2*v]
    return w


def counts(w):
    out = {p: sum(len(g[2]) for g in w[p]) for p in ('D', 'A', 'B', 'C')}
    out['scatter'] = sum(map(len, w['scatter']))
    out['total'] = sum(out.values())
    return out


def prefix(w):
    values = [1 << r for r in range(2*w['v']+w['R'])]
    return apply(values, w['A'][:-9+INDEX])


def kernel(values, order):
    pivots = {}
    out = []
    for r in order:
        val, combo = values[r] & ((1 << 120)-1), 1 << r
        while val:
            p = val.bit_length()-1
            if p not in pivots:
                pivots[p] = (val, combo)
                break
            a, b = pivots[p]
            val ^= a
            combo ^= b
        if not val:
            out.append(combo)
    return out
