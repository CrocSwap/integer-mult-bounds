"""Exact checks for irreducible price-null cycle exchanges in the PR6345 register-tax model.

Produced by Nick Petalas. Apache-2.0. Standard library only.

Model (PR6345, research/p104-frontier-symmetric-ladders): a register's timeline is a chain of
integer dimensions; its tax is the multiset of step sizes, minus one copy of its span if it is a
helper. A change of several registers is price-null when the summed tax change is zero.
"""
from collections import Counter
from itertools import combinations
import sys

STATUS = 'PASS_PRICE_NULL_CYCLE_EXCHANGES'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def tax(chain, helper=False):
    t = Counter(abs(y - x) for x, y in zip(chain, chain[1:]))
    if helper:
        t[chain[-1] - chain[0]] -= 1
    return t


def delta(old, new, helper=False):
    d = Counter(tax(new, helper))
    d.subtract(tax(old, helper))
    return {k: v for k, v in d.items() if v}


def total(deltas):
    s = Counter()
    for d in deltas:
        s.update(d)
    return {k: v for k, v in s.items() if v}


def irreducible(deltas):
    """True when the whole family is null and no nonempty proper subfamily is."""
    k = len(deltas)
    if total(deltas):
        return False
    return all(total([deltas[i] for i in S]) for r in range(1, k) for S in combinations(range(k), r))


def cycle(u, c):
    """Theorem 2 family: register i has window [0, u_i+u_{i+1}+c]; its stop moves from u_i to u_i+c."""
    k = len(u)
    regs = []
    for i in range(k):
        L = u[i] + u[(i + 1) % k] + c
        regs.append(((0, u[i], L), (0, u[i] + c, L)))
    return regs


def check_theorem1(N):
    """Two one-stop monotone chains with different windows never cancel unless both are unchanged."""
    count = 0
    for LA in range(2, N + 1):
        for LB in range(2, N + 1):
            if LA == LB:
                continue
            for s in range(1, LA):
                for s2 in range(1, LA):
                    dA = delta((0, s, LA), (0, s2, LA))
                    for t in range(1, LB):
                        for t2 in range(1, LB):
                            dB = delta((0, t, LB), (0, t2, LB))
                            if not total([dA, dB]):
                                need(not dA and not dB, 'Theorem 1 counterexample %r' % ((LA, s, s2, LB, t, t2),))
                            count += 1
    # helpers with fixed endpoints: the span term cancels inside each delta
    for s in range(1, 7):
        for s2 in range(1, 7):
            need(delta((0, s, 7), (0, s2, 7), True) == delta((0, s, 7), (0, s2, 7)), 'Helper span cancels')
    return count


def check_theorem2(kmax):
    for k in range(3, kmax + 1):
        u = [2 ** j for j in range(k)]
        c = 2 ** k
        regs = cycle(u, c)
        windows = [r[0][2] for r in regs]
        need(len(set(windows)) == k, 'Distinct windows k=%d' % k)
        need(all(0 < new[1] < new[2] for _, new in regs), 'Interior stops k=%d' % k)
        deltas = [delta(o, n) for o, n in regs]
        need(all(deltas), 'Every register changes k=%d' % k)
        need(irreducible(deltas), 'Irreducible k=%d' % k)
    return kmax - 2


def minimal_three_cycle(N):
    """Exhaustive: least max window of an irreducible price-null change of three one-stop chains
    with pairwise distinct windows, every register changed. Stops are unordered (s ~ L-s)."""
    moves = {}
    for L in range(2, N + 1):
        out = []
        for s in range(1, L // 2 + 1):
            for s2 in range(1, L // 2 + 1):
                if s != s2:
                    out.append(((0, s, L), (0, s2, L), delta((0, s, L), (0, s2, L))))
        moves[L] = out
    best = None
    for L3 in range(4, N + 1):
        for L2 in range(3, L3):
            for L1 in range(2, L2):
                for a in moves[L1]:
                    for b in moves[L2]:
                        ab = total([a[2], b[2]])
                        for c in moves[L3]:
                            if not total([ab, c[2]]):
                                need(irreducible([a[2], b[2], c[2]]), 'A three-register null change is irreducible')
                                if best is None:
                                    best = (L3, [(a[0], a[1]), (b[0], b[1]), (c[0], c[1])])
        if best:
            return best
    return best


def controls():
    # a cycle with one register's shift removed is no longer null
    regs = cycle([1, 2, 4], 8)
    deltas = [delta(o, n) for o, n in regs]
    need(total(deltas[:2]), 'Control: dropping a register breaks nullity')
    # equal windows do admit a pairwise exchange (freedom 3 is real there)
    dA, dB = delta((0, 1, 6), (0, 2, 6)), delta((0, 2, 6), (0, 1, 6))
    need(dA and not total([dA, dB]), 'Control: equal windows exchange')
    # a non-generic shift (c collides with a value) can split into smaller null families
    regs = cycle([1, 2, 1, 2], 3)
    deltas = [delta(o, n) for o, n in regs]
    need(not total(deltas), 'Control: degenerate cycle is still null')
    need(not irreducible(deltas), 'Control: genericity is needed for irreducibility')


def main():
    n1 = check_theorem1(12)
    print('PASS Theorem 1: %d one-stop pairs with distinct windows <= 12 checked; no nontrivial cancellation' % n1)
    n2 = check_theorem2(8)
    print('PASS Theorem 2: irreducible cycles with distinct windows for k = 3..8 (%d sizes)' % n2)
    L, witness = minimal_three_cycle(12)
    need(L == 6, 'Minimal largest window is 6, got %d' % L)
    need(witness == [((0, 1, 4), (0, 2, 4)), ((0, 2, 5), (0, 1, 5)), ((0, 2, 6), (0, 3, 6))], 'Pinned witness')
    print('PASS minimal three-register cycle: largest window %d, first witness %r' % (L, witness))
    controls()
    print('PASS controls')
    print(STATUS)


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()
