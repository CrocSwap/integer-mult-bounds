#!/usr/bin/env python3
"""Exact, standalone E8 root-line triple-gather census (Python 3.9+, stdlib).

Root coordinates are doubled: (±2,±2,0^6) and (±1^8) with even
minus-sign parity. Physical roots have norm 2; doubled roots norm 8.
Root *lines* identify r with -r.

This is a combinatorial source-INCIDENCE check, not a physically scheduled
copy mechanism or a new integer-multiplication exponent certificate.
"""
from __future__ import annotations

import collections
import hashlib
import itertools
import json
import sys
from pathlib import Path

EXPECTED = {
    "root_count": 240,
    "line_count": 120,
    "degree": 56,
    "edge_count": 3360,
    "pair_counts": {"adjacent:open28:closed30": 3360,
                    "nonadjacent:open24:closed24": 3780},
    "triples": {
        "0edges:rank3:open8:closed8:union107": 37800,
        "1edges:rank3:open12:closed12:union105": 120960,
        "2edges:rank3:open12:closed13:union100": 90720,
        "3edges:rank2:open0:closed3:union84": 1120,
        "3edges:rank3:open16:closed19:union100": 30240,
    },
    "min_closed_union": 84,
    "minimizer_count": 1120,
    "total_triples": 280840,
    "checks_negative": 7,
}


def scalar(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    return sum(x*y for x, y in zip(a, b))


def canonical(r: tuple[int, ...]) -> tuple[int, ...]:
    return r if next(x for x in r if x) > 0 else tuple(-x for x in r)


def roots() -> list[tuple[int, ...]]:
    result = []
    for i, j in itertools.combinations(range(8), 2):
        for p, q in itertools.product((-2, 2), repeat=2):
            row = [0]*8
            row[i] = p
            row[j] = q
            result.append(tuple(row))
    for signs in itertools.product((-1, 1), repeat=8):
        if sum(s < 0 for s in signs) % 2 == 0:
            result.append(signs)
    return result


def validate_root_set(rs: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    assert len(rs) == 240, "expected exactly 240 roots"
    assert len(set(rs)) == 240, "duplicate roots"
    assert all(len(r) == 8 and scalar(r, r) == 8 for r in rs)
    s = set(rs)
    assert all(tuple(-a for a in r) in s for r in rs), "antipodal closure"
    ls = sorted({canonical(r) for r in rs})
    assert len(ls) == 120
    assert all(r in s for r in ls)
    return ls


def graph(ls: list[tuple[int, ...]], threshold: int=4) -> list[int]:
    return [sum((1 << j) for j, w in enumerate(ls)
                if i != j and abs(scalar(v, w)) == threshold)
            for i, v in enumerate(ls)]


def validate_graph(ls: list[tuple[int, ...]], adj: list[int]) -> None:
    assert len(ls) == 120 and len(adj) == 120
    assert all((a >> i & 1) == 0 for i, a in enumerate(adj)), "self loops"
    assert all(a.bit_count() == 56 for a in adj), "not 56-regular"
    for i, a in enumerate(adj):
        for j in range(i+1, 120):
            assert ((a >> j) & 1) == ((adj[j] >> i) & 1), "asymmetric edge"
    assert sum(a.bit_count() for a in adj) // 2 == 3360


def census(ls: list[tuple[int, ...]], adj: list[int]) -> dict:
    pair = collections.Counter()
    for a, b in itertools.combinations(range(120), 2):
        connected = bool((adj[a] >> b) & 1)
        common = (adj[a] & adj[b]).bit_count()
        closed_common = ((adj[a] | (1 << a)) & (adj[b] | (1 << b))).bit_count()
        key = ("adjacent" if connected else "nonadjacent") + f":open{common}:closed{closed_common}"
        pair[key] += 1
    closed = [a | (1 << i) for i, a in enumerate(adj)]
    out = collections.Counter()
    minimum = 120
    minimizers = 0
    for a, b, c in itertools.combinations(range(120), 3):
        edges = ((adj[a] >> b) & 1) + ((adj[a] >> c) & 1) + ((adj[b] >> c) & 1)
        open3 = (adj[a] & adj[b] & adj[c]).bit_count()
        closed3 = (closed[a] & closed[b] & closed[c]).bit_count()
        union = (closed[a] | closed[b] | closed[c]).bit_count()
        ab, ac, bc = scalar(ls[a], ls[b]), scalar(ls[a], ls[c]), scalar(ls[b], ls[c])
        # The Gram determinant of three doubled E8 roots (diagonal 8).
        gram_det = 512 + 2*ab*ac*bc - 8*(ab*ab+ac*ac+bc*bc)
        assert gram_det >= 0
        rank = 2 if gram_det == 0 else 3
        if rank == 2:
            assert edges == 3, "unexpected linear dependency"
            # Exactly one of ±a ±b ±c = 0 for A2 root-line triangles.
            assert any(all(u*x + v*y + w*z == 0 for x,y,z in zip(ls[a],ls[b],ls[c]))
                       for u,v,w in itertools.product((-1,1),repeat=3))
        # Independent union-size formula, using the previously counted pair intersections.
        intersection_ab = (closed[a] & closed[b]).bit_count()
        intersection_ac = (closed[a] & closed[c]).bit_count()
        intersection_bc = (closed[b] & closed[c]).bit_count()
        assert union == 3*57 - (intersection_ab + intersection_ac + intersection_bc) + closed3
        key = f"{edges}edges:rank{rank}:open{open3}:closed{closed3}:union{union}"
        out[key] += 1
        if union < minimum:
            minimum, minimizers = union, 1
        elif union == minimum:
            minimizers += 1
    return {
        "root_count": 240, "line_count": len(ls), "degree": 56,
        "edge_count": sum(a.bit_count() for a in adj)//2,
        "pair_counts": dict(sorted(pair.items())),
        "triples": dict(sorted(out.items())),
        "min_closed_union": minimum, "minimizer_count": minimizers,
        "total_triples": sum(out.values()),
        "checks_negative": 7,
    }


def negative_controls(rs: list[tuple[int, ...]], ls: list[tuple[int, ...]], adj: list[int]) -> None:
    def rejects(fn):
        try:
            fn()
        except AssertionError:
            return
        raise AssertionError("negative control unexpectedly passed")
    rejects(lambda: validate_root_set(rs[:-1]))
    rejects(lambda: validate_root_set(rs[:-1] + [rs[0]]))
    mutated = rs.copy()
    mutated[0] = tuple(1 if i == 0 else 0 for i in range(8))
    rejects(lambda: validate_root_set(mutated))
    bad = adj.copy()
    bad[0] |= 1
    rejects(lambda: validate_graph(ls, bad))
    bad = adj.copy()
    target = (adj[0] & -adj[0]).bit_length()-1
    bad[0] &= ~(1 << target)
    rejects(lambda: validate_graph(ls, bad))
    bad = adj.copy()
    bad[0] &= ~(1 << target)
    bad[target] &= ~(1 << 0)
    rejects(lambda: validate_graph(ls, bad))
    rejects(lambda: validate_graph(ls, graph(ls, threshold=2)))


def run() -> dict:
    rs = roots()
    ls = validate_root_set(rs)
    adj = graph(ls)
    validate_graph(ls, adj)
    negative_controls(rs, ls, adj)
    result = census(ls, adj)
    assert result == EXPECTED, f"unexpected census: {result}"
    return result


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Optimized Python disables proof assertions; do not run with -O")
    result = run()
    canonical_bytes = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    target = Path(__file__).with_name('RESULT.json')
    assert target.read_bytes() == canonical_bytes, 'receipt mismatch'
    print('PASS_E8_A2_TRIPLE_GATHERS: roots=240 lines=120 triples=280840 '
          'A2=1120 min_union=84 negative_controls=7')
    print('RESULT.json sha256:', hashlib.sha256(canonical_bytes).hexdigest())
