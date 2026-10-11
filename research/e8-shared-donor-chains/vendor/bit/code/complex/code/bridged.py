"""The bridged word B_k: k bank pairs per class, s = 2k + 1 stages of invocations, on the label space
H + (s - 1) x H (m = s h).  Generalises Jacob Sussman's B_2 (Work/Bridge/Net.lean, Work/BridgeGeom/Net.lean; k = 2,
five stages) to any k.

Schedule (pair 1 as in B_2; every further pair borrows its first forward invocation from the pair before it):
    stage 0  forward  pair 1   window block 0
    stage 1  backward pair 1   window block F0
    stage 2  forward  pair 1   window block F1
    stage 2p-1 backward pair p   window block F(2p-2)      (p = 2..k)
    stage 2p   forward  pair p   window block F(2p-1)
Free twin gates (scalar +-1 additions between equal-frame roles of pairs p-1 and p):
    after stage 2p-3:  X(p-1) += X(p),  Y(p) -= Y(p-1)
    after stage 2p-2:  Y(p) += Y(p-1),  X(p-1) -= X(p)
    at the end, for p = k down to 2:  Y(p-1) -= Y(p),  X(p) += X(p-1)

Frames are coordinate sets in the one orthonormal basis of the class (Sussman's BBB, Work/BridgeGeom/Stage.lean:
every bank frame of the class is a coordinate frame JB s q):
    X enters stage t >= 1 at  block0 + qS(F0..F(t-2)),  leaves at  + qS(F(t-1));  stage 0: {l} -> block0
    Y enters stage t >= 1 at  block0 - l + qS(F0..F(t-2)), leaves at + qS(F(t-1)); stage 0: {} -> block0 - l
    X ends at every coordinate, Y at every coordinate but (block0, l).
check(k, h) verifies: every climb nested; every gate between roles at equal frames; every invocation entered at its
stage frame; final frames; each data role makes m - 1 moves; the exchange identity X_i = -y_i, Y_i = x_i (sympy).
It returns the idle climbs (moves of data roles outside invocations) per class, as blocks."""
import itertools

def qS(blocks, h, l=0):
    return frozenset((c, j) for c in blocks for j in range(h) if j != l)

def check(k, h, l=0, split=None):
    s = 2 * k + 1; m = s * h
    B0 = frozenset(('b0', j) for j in range(h))
    F = ['F%d' % i for i in range(s - 1)]
    allc = B0 | frozenset((c, j) for c in F for j in range(h))
    assert len(allc) == m
    def stage_in(t, role):
        if t == 0: return frozenset([('b0', l)]) if role == 'X' else frozenset()
        base = B0 if role == 'X' else B0 - {('b0', l)}
        return base | qS(F[:t - 1], h, l)
    def stage_out(t, role):
        if t == 0: return B0 if role == 'X' else B0 - {('b0', l)}
        return stage_in(t, role) | qS([F[t - 1]], h, l)
    final = {'X': allc, 'Y': allc - {('b0', l)}}
    stages = [(0, 'F', 1), (1, 'B', 1), (2, 'F', 1)] + [x for p in range(2, k + 1) for x in ((2 * p - 1, 'B', p), (2 * p, 'F', p))]
    cur = {(r, p): stage_in(0, r) for p in range(1, k + 1) for r in 'XY'}
    inv_moves = {key: 0 for key in cur}; idle = {key: [] for key in cur}; log = []
    def climb(key, new, idle_flag):
        old = cur[key]
        assert old <= new, ('not nested', key, len(old), len(new))
        if new != old:
            if idle_flag: idle[key].append(len(new) - len(old))
            else: inv_moves[key] += len(new) - len(old)
        cur[key] = new
    def gate(dst, src, sign):
        assert cur[dst] == cur[src], ('gate at unequal frames', dst, src)
        log.append(('G', dst, src, sign))
    for t, kind, p in stages:
        for r in 'XY':
            climb((r, p), stage_in(t, r), True)          # pair p reaches its stage frame (idle climb if needed)
            climb((r, p), stage_out(t, r), False)        # the invocation
        log.append((kind, p))
        # twin gates of pairs (q-1, q) after stages 2q-3 and 2q-2
        for q in range(2, k + 1):
            if t == 2 * q - 3:
                for r in 'XY': climb((r, q), cur[(r, q - 1)], True)
                gate(('X', q - 1), ('X', q), 1); gate(('Y', q), ('Y', q - 1), -1)
            if t == 2 * q - 2:
                for r in 'XY': climb((r, q), cur[(r, q - 1)], True)
                gate(('Y', q), ('Y', q - 1), 1); gate(('X', q - 1), ('X', q), -1)
    for key in cur: climb(key, final[key[0]], True)
    for q in range(k, 1, -1):
        gate(('Y', q - 1), ('Y', q), -1); gate(('X', q), ('X', q - 1), 1)
    for key in cur:
        assert inv_moves[key] + sum(idle[key]) == m - 1, (key, inv_moves[key], idle[key])
    # exchange identity (Sussman's abstraction: forward Y += X, backward X -= Y, gates are +-1 additions)
    import sympy as sp
    S = {}
    for p in range(1, k + 1):
        S[('X', p)] = sp.Symbol('x%d' % p); S[('Y', p)] = sp.Symbol('y%d' % p)
    for op in log:
        if op[0] == 'F': S[('Y', op[1])] = sp.expand(S[('Y', op[1])] + S[('X', op[1])])
        elif op[0] == 'B': S[('X', op[1])] = sp.expand(S[('X', op[1])] - S[('Y', op[1])])
        else: S[op[1]] = sp.expand(S[op[1]] + op[3] * S[op[2]])
    for p in range(1, k + 1):
        assert S[('X', p)] == -sp.Symbol('y%d' % p) and S[('Y', p)] == sp.Symbol('x%d' % p), (p, S[('X', p)], S[('Y', p)])
    # idle blocks per class: X and Y of every pair have equal idle ranks
    for p in range(1, k + 1): assert idle[('X', p)] == idle[('Y', p)], (p, idle[('X', p)], idle[('Y', p)])
    blocks = [r for p in range(1, k + 1) for r in idle[('X', p)]]
    if split:
        out = []
        for r in blocks:
            while r > split: out.append(split); r -= split
            if r: out.append(r)
        blocks = out
    return dict(stages=s, m=m, blocks_per_role_pair=blocks, gates=sum(1 for x in log if x[0] == 'G'),
                invocations=sum(1 for x in log if x[0] in 'FB'), per_pair_idle={p: idle[('X', p)] for p in range(1, k + 1)})

if __name__ == '__main__':
    import sys
    h = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    for k in (1, 2, 3, 4):
        if k == 1:
            continue
        r = check(k, h)
        print('k=%d stages=%d m=%d invocations=%d twin gates=%d idle per pair %s  (sum %d per role pair)' % (
            k, r['stages'], r['m'], r['invocations'], r['gates'], r['per_pair_idle'], sum(r['blocks_per_role_pair'])))
