#!/usr/bin/env python3
"""Exact replay of multi-pair schedules built from parallel borrowing chains (README section 3).

A schedule here is a set of independent Sussman borrowing chains (research/cross-shear-stage-bound,
recipe tensored with I_v) run side by side in one replica: chain c owns k_c bank pairs, starts at
stage 0, runs 2 k_c + 1 counted calls on consecutive stages, and is FORWARD-first (Y_0 += X_0) or
BACKWARD-first (X_0 += Y_0, the X <-> Y mirror). A stage therefore runs several local words at
once (rank > v at the pair level), possibly with both orientations (a mixed stage).

For each schedule the script checks, in exact rational arithmetic on random data and on all unit
vectors (pair level, v = 1):
  * the endpoint is the signed exchange (X_p = -y_p, Y_p = x_p forward-first; mirror otherwise);
  * every stage is [[I, H], [E, I]] with HE = EH = 0 (forward and backward pairs disjoint);
  * N (pair-calls) = sum (2 k_c + 1), s = max(2 k_c + 1), and Theorem S: N >= 2K + ceil(2K/(s-1)),
    with equality iff all chains have length s and (s-1)/2 divides K;
  * per-port idle windows in units of a = 8 (a register is frame-locked whenever it is active in a
    call or is read or written by a bridge; bridges sit between stages, as in format-limits (Sch)),
    the largest idle child, and the outer halving guard m^2 > 2 R^2 with m = 1 + 8 s.
B_4 alone reproduces format-limits-corrected (Sch): idle windows {8: 6, 16: 4, 32: 4, 48: 4} per port.

usage: python -B chains_replay.py            (runs the built-in cases, prints one JSON line each)
"""
import json
import random
from fractions import Fraction as Fr

A_STAGE = 8


def chain_ops(k, base, forward):
    """Ops of one borrowing chain on pairs base..base+k-1, in time order.

    ('call', stage, dst, src, sign, pair) means bank dst += sign * bank src on that pair
    ('X','Y' banks); ('bridge', after_stage, dst_bank, dst_pair, src_bank, src_pair, sign).
    Forward-first is the cross-shear-stage-bound recipe; backward-first swaps the roles of X and Y.
    """
    X, Y = ('X', 'Y') if forward else ('Y', 'X')
    ops = [('call', 0, Y, X, +1, base)]
    st = 0
    for j in range(k):
        p = base + j
        st += 1
        ops.append(('call', st, X, Y, -1, p))
        if j + 1 < k:
            ops.append(('bridge', st, X, p, X, p + 1, +1))
            ops.append(('bridge', st, Y, p + 1, Y, p, -1))
        st += 1
        ops.append(('call', st, Y, X, +1, p))
        if j + 1 < k:
            ops.append(('bridge', st, X, p, X, p + 1, -1))
            ops.append(('bridge', st, Y, p + 1, Y, p, +1))
    for j in range(k - 2, -1, -1):
        ops.append(('bridge', 'end', X, base + j + 1, X, base + j, +1))
        ops.append(('bridge', 'end', Y, base + j, Y, base + j + 1, -1))
    return ops, 2 * k + 1


def build(chains):
    """chains: list of (k, forward). Returns ops sorted into stages, K, s, N."""
    ops, base, s, N = [], 0, 0, 0
    for k, fwd in chains:
        o, length = chain_ops(k, base, fwd)
        ops.append(o)
        base += k
        s = max(s, length)
        N += length
    return ops, base, s, N


def replay(chain_ops_list, K, s, data):
    """Apply all chains' ops stage by stage; returns final registers."""
    reg = {('X', p): data[('x', p)] for p in range(K)}
    reg.update({('Y', p): data[('y', p)] for p in range(K)})
    order = []
    for o in chain_ops_list:
        for op in o:
            t = op[1]
            if op[0] == 'call':
                key = (t, 0)
            else:
                key = (s + 1, 0) if t == 'end' else (t, 1)
            order.append((key, op))
    # within a stage all calls read the pre-stage values (parallel, disjoint pairs)
    by_key = {}
    for key, op in order:
        by_key.setdefault(key, []).append(op)
    for key in sorted(by_key):
        ops = by_key[key]
        if key[1] == 0 and key[0] <= s:
            snap = dict(reg)
            for op in ops:
                _, _, dst, src, sign, p = op
                reg[(dst, p)] = snap[(dst, p)] + sign * snap[(src, p)]
        else:
            for op in ops:     # bridges of different chains touch disjoint pairs; apply in recipe order
                _, _, db, dp, sb, sp, sign = op
                reg[(db, dp)] = reg[(db, dp)] + sign * reg[(sb, sp)]
    return reg


def stage_matrices(chain_ops_list, K, s):
    """Per stage: forward pairs (E) and backward pairs (H); check disjointness (HE = EH = 0)."""
    stages = {}
    for o in chain_ops_list:
        for op in o:
            if op[0] == 'call':
                _, t, dst, src, sign, p = op
                stages.setdefault(t, {'E': set(), 'H': set()})['E' if dst == 'Y' else 'H'].add(p)
    for t, d in stages.items():
        assert not (d['E'] & d['H']), ('a pair runs both orientations in one stage', t)
    return stages


def idle_windows(chain_ops_list, K, s):
    """Idle stretches (in stages) per register, split by calls and by bridge reads/writes."""
    locks = {(b, p): [] for b in 'XY' for p in range(K)}   # events: ('active', t) or ('boundary', t)
    for o in chain_ops_list:
        for op in o:
            if op[0] == 'call':
                _, t, dst, src, sign, p = op
                locks[(dst, p)].append(('active', t))
                locks[(src, p)].append(('active', t))
            elif op[1] != 'end':
                _, t, db, dp, sb, sp, sign = op
                locks[(db, dp)].append(('boundary', t))
                locks[(sb, sp)].append(('boundary', t))
    hist = {}
    for r, ev in locks.items():
        active = {t for kind, t in ev if kind == 'active'}
        cuts = {t for kind, t in ev if kind == 'boundary'}     # lock between stage t and t+1
        run = 0
        for t in range(s):
            if t in active:
                if run:
                    hist[run * A_STAGE] = hist.get(run * A_STAGE, 0) + 1
                run = 0
                continue
            run += 1
            if t in cuts:
                hist[run * A_STAGE] = hist.get(run * A_STAGE, 0) + 1
                run = 0
        if run:
            hist[run * A_STAGE] = hist.get(run * A_STAGE, 0) + 1
    return dict(sorted(hist.items()))


def r_max(m):
    R = 0
    while 2 * (R + 1) ** 2 < m * m:
        R += 1
    return R


def check(chains, seed=1):
    ops, K, s, N = build(chains)
    rng = random.Random(seed)
    trials = [{(c, p): Fr(rng.randint(-99, 99), rng.randint(1, 9)) for c in 'xy' for p in range(K)}]
    for c in 'xy':                     # all unit vectors: the full linear map
        for p in range(K):
            trials.append({(cc, pp): Fr(int(cc == c and pp == p)) for cc in 'xy' for pp in range(K)})
    owner, base = {}, 0
    for k, fwd in chains:
        for p in range(base, base + k):
            owner[p] = fwd
        base += k
    for data in trials:
        reg = replay(ops, K, s, data)
        for p in range(K):
            if owner[p]:
                assert reg[('X', p)] == -data[('y', p)] and reg[('Y', p)] == data[('x', p)], ('endpoint', p)
            else:
                assert reg[('Y', p)] == -data[('x', p)] and reg[('X', p)] == data[('y', p)], ('endpoint', p)
    st = stage_matrices(ops, K, s)
    assert len(st) == s
    calls = sum(len(d['E']) + len(d['H']) for d in st.values())
    assert calls == N
    bound = 2 * K + -(-2 * K // (s - 1))
    assert N >= bound, 'THEOREM S VIOLATED'
    win = idle_windows(ops, K, s)
    m = 1 + A_STAGE * s
    largest = max(win) if win else 0
    mixed = sum(1 for d in st.values() if d['E'] and d['H'])
    return dict(chains=[[k, 'forward' if f else 'backward'] for k, f in chains], K=K, s=s, N=N, m=m,
                W_per_replica_ports=2 * K * 112, D_per_replica=2 * K * 112 - 64 * N,
                theorem_S_bound=bound, attains_bound=(N == bound), mixed_orientation_stages=mixed,
                pair_calls_per_stage=[len(st[t]['E']) + len(st[t]['H']) for t in sorted(st)],
                idle_windows_per_port=win, largest_idle_child=largest, R_max_halving_guard=r_max(m),
                largest_child_needs_split=largest > r_max(m), endpoint='signed exchange, exact')


CASES = [
    [(4, True)],                                  # B_4 = the T74 template
    [(2, True), (2, False)],                      # s = 5, two opposite chains: every stage mixed
    [(2, True), (2, True)],                       # s = 5, rank-2v calls, one orientation per stage
    [(4, True), (4, False)],                      # s = 9, K = 8: rank-2v mixed stages
    [(4, True), (3, True)],                       # unequal chains in one window (dominated)
    [(3, True), (3, False), (1, True)],           # s = 7, K = 7, N = 17 (padded by one idle stage: the s = 8 chain value)
    [(1, True), (1, False), (1, True)],           # s = 3, full-rank 3-shear per pair
]

if __name__ == '__main__':
    out = [check(c) for c in CASES]
    b4 = out[0]
    assert b4['idle_windows_per_port'] == {8: 6, 16: 4, 32: 4, 48: 4}, b4['idle_windows_per_port']
    for o in out:
        print(json.dumps(o))
    print('PASS_F1_CHAINS_REPLAY cases=%d' % len(out))
