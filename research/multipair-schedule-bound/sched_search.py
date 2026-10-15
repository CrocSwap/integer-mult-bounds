#!/usr/bin/env python3
"""Exhaustive F2 check of the multi-pair stage/call frontier (Theorem S of README.md).

Pair-level model (research/cross-shear-stage-bound tensored with I_v): data (X, Y) in F^K x F^K,
K bank pairs. One STAGE runs any set of local words in parallel on disjoint pairs, forward
(Y_p += X_p) or backward (X_q += Y_q), with arbitrary invertible block-diagonal bridges between
stages. After bridges a stage is [[I, H], [E, I]] with HE = 0 and EH = 0 (forward and backward
pairs are disjoint), and it costs N_stage = rank E + rank H local-word invocations (pair-calls).
Bridges are absorbed: the state is M modulo left block-diagonal action, i.e. the pair
(P, Q) = (row space of the top block row, row space of the bottom block row). A stage maps
top -> top + H bottom and bottom -> bottom + E top (old rows; HE = EH = 0 makes it well defined).
Start (X, Y), goal (Y, X) = block antidiagonal. `--alternating` restricts every stage to E = 0
or H = 0 alternately (one orientation per stage, the B_K template's form).

Prints, for each stage count s <= S, the minimum number of pair-calls N reaching the goal
in exactly s stages (None if > N_max), and compares with
    Theorem S lower bound      N >= 2K + ceil(2K / (s - 1))          (s >= 2)
    parallel B_k chains        N  = 2K + ceil(K / k), k = floor((s - 1) / 2)   (s >= 3).
Standard library only; exact F2 arithmetic on bitmasks.
usage: python -B sched_search.py K N_max S [--alternating] [--maxrank r] [--wastefree-after-1]
  --maxrank r          every stage has rank E <= r and rank H <= r (a restriction: found N are upper
                       bounds on the true frontier, the Theorem S assertion still applies)
  --wastefree-after-1  prune every stage t >= 2 that does not lower Phi by its full cost
"""
import json
import sys
from itertools import product


def rref(rows, n):
    """Canonical reduced row echelon basis (tuple of ints) of span(rows) in F2^n."""
    piv = {}                                     # leading bit -> row; rows reduced at all pivots
    for r in rows:
        for lead in sorted(piv, reverse=True):
            if (r >> lead) & 1:
                r ^= piv[lead]
        if r:
            lead = r.bit_length() - 1
            for l2 in piv:
                if (piv[l2] >> lead) & 1:
                    piv[l2] ^= r
            piv[lead] = r
    return tuple(sorted(piv.values(), reverse=True))


def rank(rows):
    basis = []
    for r in rows:
        for b in basis:
            r = min(r, r ^ b)
        if r:
            basis.append(r)
    return len(basis)


def main():
    K, N_max, S = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    alternating = '--alternating' in sys.argv
    maxrank = int(sys.argv[sys.argv.index('--maxrank') + 1]) if '--maxrank' in sys.argv else None
    wastefree = '--wastefree-after-1' in sys.argv
    n = 2 * K
    xmask = (1 << K) - 1                       # low K bits = X coordinates, high K bits = Y
    X = tuple(1 << i for i in range(K))
    Y = tuple(1 << (K + i) for i in range(K))
    start, goal = (rref(X, n), rref(Y, n)), (rref(Y, n), rref(X, n))

    mats = list(product(range(1 << K), repeat=K))   # matrix = tuple of K row masks (bit j = column j)

    def mul(A, B):                                   # (AB)_i = XOR of rows B_j with A_ij = 1
        out = []
        for a in A:
            r = 0
            for j in range(K):
                if (a >> j) & 1:
                    r ^= B[j]
            out.append(r)
        return tuple(out)

    rk = {M: rank(M) for M in mats}
    zero = tuple([0] * K)
    pairs = []                                       # (E, H, cost) with HE = EH = 0
    for E in mats:
        for H in mats:
            if E == zero and H == zero:
                continue
            if alternating and E != zero and H != zero:
                continue
            if maxrank is not None and (rk[E] > maxrank or rk[H] > maxrank):
                continue
            if mul(H, E) == zero and mul(E, H) == zero:
                pairs.append((E, H, rk[E] + rk[H]))

    def combos(rows):
        c = [0] * (1 << K)
        for m in range(1, 1 << K):
            low = (m & -m).bit_length() - 1
            c[m] = c[m & (m - 1)] ^ rows[low]
        return c

    def phi(P, Q):
        return rank([p & xmask for p in P]) + rank([q >> K for q in Q])

    layer = {start: 0}
    result = {}
    for s in range(1, S + 1):
        nxt = {}
        for (P, Q), used in layer.items():
            pc, qc = combos(P), combos(Q)
            topc, botc = {}, {}
            for E, H, cost in pairs:
                if alternating and ((s % 2 == 1) != (E != zero)):
                    continue                          # odd stages forward (E), even backward (H)
                if used + cost > N_max:
                    continue
                if H not in topc:
                    topc[H] = rref([P[i] ^ qc[H[i]] for i in range(K)], n)
                if E not in botc:
                    botc[E] = rref([Q[i] ^ pc[E[i]] for i in range(K)], n)
                st = (topc[H], botc[E])
                u = used + cost
                ph = phi(*st)
                if u + ph > N_max:
                    continue
                if wastefree and s >= 2 and ph != phi(P, Q) - cost:
                    continue
                if nxt.get(st, 1 << 30) > u:
                    nxt[st] = u
        layer = nxt
        result[s] = layer.get(goal)
        print(json.dumps({'K': K, 'stage': s, 'states': len(layer), 'min_N': result[s]}), flush=True)

    rows = []
    best = None                                   # min N over schedules with AT MOST s stages
    for s in range(2, S + 1):
        bound = 2 * K + -(-2 * K // (s - 1))
        k = (s - 1) // 2
        chains = 2 * K + -(-K // k) if k >= 1 else None
        if result[s] is not None:
            best = result[s] if best is None else min(best, result[s])
        rows.append({'s': s, 'min_N_exactly_s': result[s], 'min_N_at_most_s': best,
                     'theorem_S_bound': bound, 'parallel_chains': chains})
        assert result[s] is None or result[s] >= bound, ('THEOREM S VIOLATED', s, result[s], bound)
    print(json.dumps({'K': K, 'N_max': N_max, 'alternating': alternating, 'maxrank': maxrank,
                      'wastefree_after_1': wastefree, 'pairs': len(pairs), 'frontier': rows}))


if __name__ == '__main__':
    main()
