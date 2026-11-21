#!/usr/bin/env python3
"""Independently verify an ASCII RUP refutation on an exact CNF subset.

Usage: check_rup.py FULL.cnf CORE.cnf CORE.drat
First checks the core is a clause multiset subset of FULL. Then checks every
non-deletion proof line by fresh, ordinary unit propagation with the negated
lemma as assumptions. Deletion lines are ignored (retaining clauses makes RUP
only easier). Requires an explicit empty final lemma. This intentionally uses
a simple full scan rather than a SAT solver or drat-trim to check the proof.
"""
from collections import Counter
import sys

if len(sys.argv) != 4:
    raise SystemExit(__doc__)
full, core, proof = sys.argv[1:]

def cnf(path):
    n = m = None
    clauses = []
    with open(path) as fh:
        for line in fh:
            if line.startswith("c") or not line.strip(): continue
            if line.startswith("p"):
                p, kind, n, m = line.split()
                assert p == "p" and kind == "cnf"
                n, m = int(n), int(m)
            else:
                v = [int(x) for x in line.split()]
                assert v and v[-1] == 0 and 0 not in v[:-1]
                clauses.append(tuple(v[:-1]))
    assert n is not None and len(clauses) == m
    assert all(abs(x) <= n for cl in clauses for x in cl)
    return n, clauses

n, base = cnf(core)
needed = Counter(tuple(sorted(c)) for c in base)
with open(full) as fh:
    for line in fh:
        if line[0] in "cp" or not line.strip(): continue
        row = tuple(sorted(int(x) for x in line.split()[:-1]))
        if needed[row] > 0:
            needed[row] -= 1
assert all(v == 0 for v in needed.values()), "core is not a subset of full CNF"
print(f"PASS all {len(base)} core clauses occur in the full formula", flush=True)

def rup(clauses, lemma):
    assignment = bytearray(n + 1)  # 0 unknown, 1 true, 2 false
    for literal in lemma:
        var = abs(literal)
        value = 2 if literal > 0 else 1  # negate the lemma
        if assignment[var] and assignment[var] != value:
            return True  # the clause itself is tautological
        assignment[var] = value
    while True:
        progress = False
        for cl in clauses:
            last, unknown = 0, 0
            for lit in cl:
                val = assignment[abs(lit)]
                if not val:
                    last = lit
                    unknown += 1
                elif (val == 1) == (lit > 0):
                    break
            else:  # no literal was true
                if unknown == 0:
                    return True
                if unknown == 1:
                    var = abs(last)
                    value = 1 if last > 0 else 2
                    if assignment[var] and assignment[var] != value:
                        return True
                    if not assignment[var]:
                        assignment[var] = value
                        progress = True
        if not progress:
            return False

steps = 0
last = None
with open(proof) as fh:
    for line in fh:
        if not line.strip() or line.startswith("c"): continue
        if line.startswith("d "): continue
        row = [int(x) for x in line.split()]
        assert row and row[-1] == 0 and all(0 < abs(v) <= n for v in row[:-1])
        lemma = tuple(row[:-1])
        if not rup(base, lemma):
            raise AssertionError(f"RUP failure at addition {steps+1}")
        base.append(lemma)
        steps += 1
        last = lemma
assert last == (), "refutation does not end in an empty clause"
print(f"PASS {steps} RUP additions verified by independent unit propagation")
