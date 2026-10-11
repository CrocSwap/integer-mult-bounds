"""Our own check of the bridged layout B_K (Sussman's B_2, Work/Bridge/Net.lean; DaysSky's B_K generalisation, PR #363),
reimplemented from the schedule stated in PR #363's README and Sussman's coordinate-frame stage geometry:
K bank pairs, 2K+1 stages on H + 2K.H (m = (2K+1)h). Pair 1: forward, backward, forward; pair p >= 2: backward, forward,
borrowing its first forward from pair p-1 through twin gates (+-1 additions at equal frames).
Checks: frames are coordinate sets; every climb nested; twin gates at equal frames; each invocation entered at its
stage frame; final frames; m-1 moves per data role; exchange identity X_p = -y_p, Y_p = x_p (exact integer
linear algebra on symbolic coefficient vectors). Returns the idle climbs per role pair (optionally split at s).
Chafik Boukhalfa (chafreaky) with Anthropic Claude assistance; Apache-2.0."""
def layout(K, h, split=None):
    s = 2 * K + 1; m = s * h; l = 0
    blk = lambda name, skip=None: {(name, j) for j in range(h) if j != skip}
    B0 = blk('b0'); F = ['F%d' % i for i in range(s - 1)]
    ALL = set(B0).union(*[blk(f) for f in F]); assert len(ALL) == m
    def enter(t, X):
        if t == 0: return {('b0', l)} if X else set()
        base = set(B0) if X else B0 - {('b0', l)}
        for f in F[:t - 1]: base |= blk(f, l)
        return base
    def leave(t, X):
        return (set(B0) if X else B0 - {('b0', l)}) if t == 0 else enter(t, X) | blk(F[t - 1], l)
    sched = [(0, 'F', 1), (1, 'B', 1), (2, 'F', 1)]
    for p in range(2, K + 1): sched += [(2 * p - 1, 'B', p), (2 * p, 'F', p)]
    fr = {(X, p): enter(0, X) for p in range(1, K + 1) for X in (True, False)}
    inv = {k: 0 for k in fr}; idle = {k: [] for k in fr}
    # symbolic values: vector over symbols x1..xK, y1..yK
    sym = lambda nm, p: tuple(int(q == (nm, p)) for q in [(a, b) for a in 'xy' for b in range(1, K + 1)])
    val = {(True, p): sym('x', p) for p in range(1, K + 1)} | {(False, p): sym('y', p) for p in range(1, K + 1)}
    add = lambda u, w, c: tuple(a + c * b for a, b in zip(u, w))
    def go(k, new, is_idle):
        assert fr[k] <= new, 'climb not nested'
        if new != fr[k]:
            (idle[k].append(len(new) - len(fr[k])) if is_idle else None)
            if not is_idle: inv[k] += len(new) - len(fr[k])
        fr[k] = set(new)
    def gate(d, s_, c):
        assert fr[d] == fr[s_], 'twin gate at unequal frames'
        val[d] = add(val[d], val[s_], c)
    for t, kind, p in sched:
        for X in (True, False):
            go((X, p), enter(t, X), True); go((X, p), leave(t, X), False)
        if kind == 'F': val[(False, p)] = add(val[(False, p)], val[(True, p)], 1)
        else: val[(True, p)] = add(val[(True, p)], val[(False, p)], -1)
        for q in range(2, K + 1):
            if t in (2 * q - 3, 2 * q - 2):
                for X in (True, False): go((X, q), fr[(X, q - 1)], True)
                if t == 2 * q - 3: gate((True, q - 1), (True, q), 1); gate((False, q), (False, q - 1), -1)
                else: gate((False, q), (False, q - 1), 1); gate((True, q - 1), (True, q), -1)
    for k in fr: go(k, ALL if k[0] else ALL - {('b0', l)}, True)
    for q in range(K, 1, -1): gate((False, q - 1), (False, q), -1); gate((True, q), (True, q - 1), 1)
    for k in fr: assert inv[k] + sum(idle[k]) == m - 1
    for p in range(1, K + 1):
        assert val[(True, p)] == tuple(-a for a in sym('y', p)) and val[(False, p)] == sym('x', p), ('exchange', p)
        assert idle[(True, p)] == idle[(False, p)]
    blocks = [r for p in range(1, K + 1) for r in idle[(True, p)]]
    if split:
        out = []
        for r in blocks:
            while r > split: out.append(split); r -= split
            if r: out.append(r)
        blocks = out
    return dict(m=m, per_pair={p: idle[(True, p)] for p in range(1, K + 1)}, blocks=blocks)
if __name__ == '__main__':
    print(layout(2, 9)); print(layout(3, 9)); print(layout(3, 9, split=31))
