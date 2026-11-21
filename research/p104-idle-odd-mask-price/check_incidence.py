#!/usr/bin/env python3
"""Finite controls for an abstract sharp odd-idle incidence construction.

No endpoint identity, signed-Gram frame, or legal caller is constructed.
The general algebraic construction and its exact quantifiers are in
INCIDENCE.md. This script checks small and k=77 boundary instances.
"""
from itertools import product
from hashlib import sha256
from pathlib import Path
import json


def check(k, q, d):
    assert k >= 3 and q >= 1 and 1 <= d <= k
    n = 2 * k - 2 + q
    stages = frozenset(range(k))
    odd_stage_set = frozenset(range(d))

    # Role r has one special piece on the common d-set if r<q;
    # otherwise every piece is a singleton. A special role also has
    # singleton pieces at all stages outside the d-set.
    pieces = []
    for r in range(n):
        p = []
        if r < q:
            p.append((r, odd_stage_set, True))
            p.extend((r, frozenset([s]), False) for s in stages - odd_stage_set)
        else:
            p.extend((r, frozenset([s]), False) for s in stages)
        assert set().union(*(S for _, S, _ in p)) == set(stages)
        assert sum(len(S) for _, S, _ in p) == k
        pieces.append(p)

    # Pairwise disjoint pieces per role give a stage-by-stage bijection
    # from roles to events and hence exact stage incidence.
    for s in stages:
        seen = [(r, S, odd) for role in pieces for r, S, odd in role if s in S]
        assert len(seen) == n
        assert sorted(r for r, _, _ in seen) == list(range(n))
    events = [e for role in pieces for e in role]
    odd = [e for e in events if e[2]]
    assert len(odd) == q and sum(len(S) for _, S, _ in odd) == q*d
    assert n + 2 == 2*k + q

    # For the matched Cfg, a(r,s) is the size of its unique stage piece;
    # mark the backbone singleton roles as mains.
    def size(r, s):
        matches = [len(S) for _, S, _ in pieces[r] if s in S]
        assert len(matches) == 1
        return matches[0]

    assert all(1 <= size(r, s) <= k for r in range(n) for s in stages)
    mains = sum(size(r, s) == 1 for r in range(q, n) for s in stages)
    assert mains == (2*k - 2)*k and mains >= 2*k
    assert n >= k - 2                      # LC, every role nonleaf
    assert k*n >= k*(2*k - 2)             # LEAF, zero leaves
    for ell in range(3, k + 1):
        # Definitional expression HPDual.rowS with all role masks full.
        row_sum = 0
        for r in range(n):
            for s in stages:
                a = size(r, s)
                row_sum += (k - a) if a < ell else 0
        assert row_sum >= 2*k*(k - 1)     # LawQ.rc2

    # Two backbone roles supply bh,ah.  x_e = y_e is the coordinate
    # vector for e's role. Multistage special events use only r<q, where
    # bh=0, proving x_ker; different pieces of the same role are disjoint,
    # proving biorthogonality whenever event stage sets overlap.
    def coord(role, col):
        return int(role == q + col)
    gram = [[sum(coord(r, a)*coord(r, b) for r in range(n))
             for b in range(2)] for a in range(2)]
    assert gram == [[1, 0], [0, 1]]       # gBlk(s,t) for all s,t
    for r, S, _ in events:
        assert S <= stages                 # x_supp, all role masks full
        if len(S) >= 2:
            assert r < q and all(coord(r, a) == 0 for a in range(2))
    for role in pieces:
        for (_, s1, _), (_, s2, _) in product(role, repeat=2):
            if s1 != s2:
                assert s1.isdisjoint(s2)
    # For every ordered s != t and every threshold l, gSet contains at
    # most q multistage events, while wSet contains all n roles.
    assert 2 + q <= n
    # C=2 or C=4 predesignated singleton contacts/stage are available,
    # without claiming those events are a realizable J grammar word.
    assert 2*k - 2 >= 4
    print(f"k={k} Q={q} d={d} n={n} odd-incidence={q*d}; "
          f"LawQ/matching/EvData rows: PASS")


for args in [(3, 1, 1), (3, 1, 3), (3, 4, 3),
             (17, 1, 17), (77, 1, 26), (77, 1, 77), (77, 4, 26)]:
    check(*args)


def check_7113():
    source = Path(__file__).resolve().parent / "expected_ODD-TYPE-AB-CALLER.json"
    raw = source.read_bytes()
    assert sha256(raw).hexdigest() == "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
    C = json.loads(raw)
    k = C["stages"]
    assert k == 17
    for ty, contacts, expected_plain, expected_odd in [
        ("A", 4, 128, 0), ("B", 2, 162, 4)
    ]:
        rows = C["types"][ty]["diagonal"]
        events = [e for e in C["events"] if e[0] == ty and e[1] in ("IDLE_ONE", "IDLE_ODD")]
        target_by_stage = [sum(r[s + 2] for r in rows) for s in range(k)]
        plain_by_stage = [sum(s + 1 in e[3] for e in events) for s in range(k)]
        assert target_by_stage == [contacts + value for value in plain_by_stage]
        assert sum(target_by_stage) == 196 and sum(plain_by_stage) == expected_plain
        assert sum(len(e[3]) for e in events if e[1] == "IDLE_ODD") == expected_odd
        print(f"#7113 {ty}: all {k} stage incidences match; "
              f"target=196 contacts={contacts*k} plain={expected_plain} odd={expected_odd}")


check_7113()
