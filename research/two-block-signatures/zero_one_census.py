#!/usr/bin/env python3
"""Exact six-port census of zero-one coefficient matrices inverted over Q."""
from collections import Counter
from itertools import combinations
from math import factorial, gcd
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0,str(PACKAGE))
from algebra import inverse, masks
from construction_check import need
from signatures import TYPES, Profile, multiplicity


def primitive(values):
    divisor = gcd(*values)
    if not divisor:
        return None
    if next(x for x in values if x) < 0:
        divisor = -divisor
    return tuple(v//divisor for v in values)


def minor(rows, columns):
    if len(rows) == 2:
        a,b = rows
        i,j = columns
        return a[i]*b[j] - a[j]*b[i]
    a,b,c = rows
    i,j,k = columns
    return (a[i]*(b[j]*c[k]-b[k]*c[j]) - a[j]*(b[i]*c[k]-b[k]*c[i])
            + a[k]*(b[i]*c[j]-b[j]*c[i]))


def row_spaces(d, subsets):
    n = 2*d
    vectors = [tuple((v>>j)&1 for j in range(n)) for v in range(1,1<<n)]
    bases = Counter()
    first = {}
    for rows in combinations(vectors,d):
        key = primitive([minor(rows,I) for I in subsets])
        if key is not None:
            bases[key] += factorial(d)
            first.setdefault(key,rows)
    incidence = {}
    for key in bases:
        active = [set(I) for I,x in zip(subsets,key,strict=True) if x]
        source = sum(1<<j for j in set.union(*active))
        axes = sum(1<<j for j in set.intersection(*active))
        incidence[key] = source, axes
    return bases, first, incidence


def parity(xs):
    return (-1)**sum(x>y for k,x in enumerate(xs) for y in xs[k+1:])


def coordinate_orbits(bases, subsets, n):
    index = {s:i for i,s in enumerate(subsets)}
    moves = []
    for j in range(n-1):
        swap = list(range(n))
        swap[j],swap[j+1] = swap[j+1],swap[j]
        images = [[swap[i] for i in subset] for subset in subsets]
        moves.append([(index[tuple(sorted(img))],parity(img)) for img in images])
    seen = set()
    for start in bases:
        if start in seen:
            continue
        group = [start]
        seen.add(start)
        for key in group:
            for action in moves:
                other = primitive([sign*key[i] for i,sign in action])
                need(bases[other] == bases[start], "zero-one orbit weight")
                if other not in seen:
                    seen.add(other)
                    group.append(other)
        yield start,len(group)


def row_masks(sa, ea, sb, eb, n):
    return tuple(4*(((sa>>j)&1)+2*((sb>>j)&1)) + (1-((eb>>j)&1))+2*(1-((ea>>j)&1))
                 for j in range(n))


def canonical_matrix(rows, symbols, d):
    order = sorted(range(2*d),key=lambda j:TYPES.index(symbols[j]))
    mat = tuple(tuple(row[j] for j in order) for row in rows)
    inv = inverse(mat,"Q")
    need(inv is not None and masks(mat,inv,d) == tuple(symbols[j] for j in order), "zero-one witness masks")
    return ["".join(str(x) for x in row) for row in mat]


def compute(d):
    if d not in (2,3):
        raise ValueError("zero-one oracle bounded to four or six ports")
    n = 2*d
    subsets = list(combinations(range(n),d))
    index = {s:i for i,s in enumerate(subsets)}
    bases, first, incidence = row_spaces(d,subsets)
    adj = []
    for I in subsets:
        J = tuple(k for k in range(n) if k not in I)
        adj.append((index[J],parity(I+J)))
    hist, witnesses = Counter(), {}
    pairs = orbits = covered = 0
    for upper, weight in coordinate_orbits(bases,subsets,n):
        orbits += 1
        covered += weight
        dual = [(j,sign*x) for x,(j,sign) in zip(upper,adj,strict=True) if x]
        for lower, number in bases.items():
            if not sum(c*lower[j] for j,c in dual):
                continue
            pairs += weight
            syms = row_masks(*incidence[upper],*incidence[lower],n)
            key = tuple(syms.count(s) for s in TYPES)
            hist[key] += weight*bases[upper]*number
            if key not in witnesses:
                witnesses[key] = canonical_matrix(first[upper]+first[lower],syms,d)
    need(covered == len(bases), "incomplete zero-one space partition")
    summary = dict(spaces=len(bases),first_space_orbits=orbits,ordered_space_pairs=pairs,
                   invertible_matrices=sum(hist.values()),profiles=len(hist),
                   signatures=sum(multiplicity(Profile(*k).symbols()) for k in hist))
    return summary,hist,witnesses


def raw_four_port():
    """All 2^16 matrices. Read inverse supports from integer 3x3 cofactors."""
    vectors = [tuple((v>>i)&1 for i in range(4)) for v in range(16)]
    triples = list(combinations(range(4),3))[::-1]  # item j omits coordinate j
    # Table of all minors for an ordered triple of four-bit rows and deleted column.
    lookup = {(a,b,c,j):minor((vectors[a],vectors[b],vectors[c]),I)
              for a in range(16) for b in range(16) for c in range(16) for j,I in enumerate(triples)}
    hist = Counter()
    for bits in range(1<<16):
        rows = tuple((bits>>(4*i))&15 for i in range(4))
        remaining = [tuple(rows[k] for k in keep) for keep in triples]
        adj = [[lookup[keep+(j,)] for j in range(4)] for keep in remaining]
        det = sum((-1)**j*vectors[rows[0]][j]*adj[0][j] for j in range(4))
        if det:
            symbols = []
            for j in range(4):
                s = int(bool((rows[0]|rows[1]) & (1<<j))) + 2*int(bool((rows[2]|rows[3]) & (1<<j)))
                r = int(bool(adj[0][j] or adj[1][j])) + 2*int(bool(adj[2][j] or adj[3][j]))
                symbols.append(4*s+r)
            hist[tuple(symbols.count(s) for s in TYPES)] += 1
    return hist


def build():
    small, hist4, _ = compute(2)
    need(small["signatures"] == 391 and hist4 == raw_four_port(), "zero-one literal four-port census")
    six, hist, mats = compute(3)
    need(six["invertible_matrices"] == 28836612000, "known zero-one invertible total")
    stored = json.loads((PACKAGE/"SIX-PORTS.json").read_bytes())
    binary = {tuple(r["counts"]) for r in stored if r["binary"] is not None}
    ordinary = {tuple(r["counts"]) for r in stored}
    need(binary < set(hist) < ordinary, "zero-one coefficient domain nesting")
    rows = []
    for key,total in sorted(hist.items()):
        per,rem = divmod(total,multiplicity(Profile(*key).symbols()))
        need(per>0 and rem == 0, "zero-one labeling multiplicity")
        rows.append(dict(counts=list(key),matrices_per_label=per,matrix=mats[key]))
    return dict(four_port=small,six_port=six,profiles=rows)


if __name__ == "__main__":
    result = build()
    need(result == json.loads((PACKAGE/"ZERO-ONE.json").read_bytes()), "stored zero-one census differs")
    print(json.dumps({"status":"PASS_TWO_BLOCK_ZERO_ONE_Q","result":result["six_port"]},sort_keys=True))
