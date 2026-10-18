"""Exhaustive check: every sub-configuration of the pool with at most 4 lines is Corollary-J certifiable
(no harmonic line is immovable). Immovability is upward closed and the order-48 signed-permutation group acts on
the pool, so it suffices to test all 4-subsets that contain one representative of each orbit of harmonic lines.
Uses implementation A's pool and row encoding (lib/jet.py).
Written for this package (thakrarsagar, with AI assistance from Claude Opus 5.5). Apache-2.0."""
from itertools import combinations
from jet import Jet, pool, signed_perms, act, normalise


def harmonic_orbit_reps(P, harm):
    idx = {l: i for i, l in enumerate(P)}
    perms = []
    for g in signed_perms():
        perms.append([idx[(normalise(act(g, p)), normalise(act(g, q)))] for p, q in P])
    reps, seen = [], set()
    for h in harm:
        if h in seen:
            continue
        reps.append(h)
        seen |= {pm[h] for pm in perms}
    return reps, perms


def check_small(size=4, minimal_only=False):
    """Return (orbit representatives of harmonic lines, number of subsets tested, immovable subsets found).
    With minimal_only=True, immovable subsets that contain an immovable (size-1)-subset are not reported
    (they are not inclusion-minimal)."""
    P = pool()
    J = Jet(P)
    row = {(t, s): J.row(t, s, D) for (t, s, D) in J.inc}
    delta = {t: J.delta(t) for t in J.harm}
    harm = set(J.harm)
    reps, perms = harmonic_orbit_reps(P, J.harm)
    assert all(sorted(pm) == list(range(len(P))) for pm in perms)
    tested = 0
    bad = []
    for r in reps:
        others = [u for u in range(len(P)) if u != r]
        for rest in combinations(others, size - 1):
            S = (r,) + rest
            tested += 1
            basis = {}
            for x in S:
                for y in S:
                    m = row.get((x, y))
                    if m is None:
                        continue
                    while m:
                        h = m.bit_length() - 1
                        if h in basis:
                            m ^= basis[h]
                        else:
                            basis[h] = m
                            break
            for t in S:
                if t in harm:
                    m = delta[t]
                    while m:
                        h = m.bit_length() - 1
                        if h not in basis:
                            break
                        m ^= basis[h]
                    if not m:
                        if not minimal_only or not any(_immovable(row, delta, harm, S[:i] + S[i + 1:])
                                                       for i in range(len(S))):
                            bad.append(S)
                        break
    return reps, tested, bad


def _immovable(row, delta, harm, S):
    basis = {}
    for x in S:
        for y in S:
            m = row.get((x, y))
            if m is None:
                continue
            while m:
                h = m.bit_length() - 1
                if h in basis:
                    m ^= basis[h]
                else:
                    basis[h] = m
                    break
    for t in S:
        if t in harm:
            m = delta[t]
            while m:
                h = m.bit_length() - 1
                if h not in basis:
                    break
                m ^= basis[h]
            if not m:
                return True
    return False
