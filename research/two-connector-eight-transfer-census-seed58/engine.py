"""Exact census of the PR1438/PR1498 two-connector family (standard library).

Model (PR1498): n read-only sources with increments b_j, two dirty connectors
z0 = e0 + ..., z1 = e1 + ..., operations B_j(p): z_p += b_j, C: z0 += z1, and
readouts A_m(p) of z_p. Every B_j occurs twice and both occurrences use the
source's port (forced by restoration, PR1498 step 1). A mask m is covered when
two cuts on the same connector have equal dirt and source parts differing by m.
"""
from collections import Counter

# XOR-translation of a set of values {0..31} stored as a 32-bit mask is a bit
# permutation: flipping value bit k swaps the blocks selected by MASKS[k].
MASKS = (0x55555555, 0x33333333, 0x0F0F0F0F, 0x00FF00FF, 0x0000FFFF)


def translate(s, v):
    for k in range(5):
        if v >> k & 1:
            h = 1 << k
            s = ((s & MASKS[k]) << h) | ((s >> h) & MASKS[k])
    return s


def words(n):
    """All pairings of 2n positions, labels by first occurrence: (2n-1)!! words."""
    out = []
    def fill(w, label):
        if label == n:
            out.append(tuple(w))
            return
        i = w.index(None)
        w[i] = label
        for k in range(i + 1, 2 * n):
            if w[k] is None:
                w[k] = label
                fill(w, label + 1)
                w[k] = None
        w[i] = None
    fill([None] * (2 * n), 0)
    return out


def census_word(word, n, T, ports_list, reduced=True, want_full=False):
    """Count restored schedules of one B word with exactly T transfers.

    reduced=True allows 0, 1 or 2 transfers per gap; reduced=False allows any.
    Returns (leaves, Counter{(r, coverage size)}, list of full schedules).
    """
    full_mask = (1 << (1 << n)) - 1
    gaps = 2 * n + 1
    hist, full, leaves = Counter(), [], [0]
    for ports in ports_list:
        r = bin(ports).count('1')
        cvec = [0] * gaps

        def visit(S, D, v):
            if S >> v & 1:
                return S, D
            S |= 1 << v
            return S, D | translate(S, v)

        def go(g, budget, z0, q1, par, opened, S1, D1, Se, De, So, Do):
            last = g == 2 * n
            choices = (budget,) if last else range(0, min(budget, 2 if reduced else budget) + 1)
            for c in choices:
                if reduced and c > 2:
                    continue
                cz0, cpar, cSe, cDe, cSo, cDo = z0, par, Se, De, So, Do
                for _ in range(c):
                    cz0 ^= q1
                    cpar ^= 1
                    if cpar:
                        cSo, cDo = visit(cSo, cDo, cz0)
                    else:
                        cSe, cDe = visit(cSe, cDe, cz0)
                cvec[g] = c
                if last:
                    leaves[0] += 1
                    if cpar == 0 and cz0 == 0 and q1 == 0:
                        cov = D1 | cDe | cDo
                        hist[(r, bin(cov).count('1'))] += 1
                        if cov == full_mask and want_full:
                            full.append((word, ports, tuple(cvec)))
                    continue
                j = word[g]
                bit = 1 << j
                nz0, nq1, nopened, nS1, nD1 = cz0, q1, opened, S1, D1
                nSe, nDe, nSo, nDo = cSe, cDe, cSo, cDo
                if ports >> j & 1:
                    if q1 & bit:
                        if (opened >> j & 1) != cpar:   # odd transfers while b_j sat in z1
                            continue
                    else:
                        nopened = (opened & ~bit) | (cpar << j)
                    nq1 = q1 ^ bit
                    nS1, nD1 = visit(S1, D1, nq1)
                else:
                    nz0 = cz0 ^ bit
                    if cpar:
                        nSo, nDo = visit(cSo, cDo, nz0)
                    else:
                        nSe, nDe = visit(cSe, cDe, nz0)
                go(g + 1, budget - c, nz0, nq1, cpar, nopened, nS1, nD1, nSe, nDe, nSo, nDo)

        go(0, T, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0)
    return leaves[0], hist, full
