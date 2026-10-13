"""Greatest-solution frame lifting for a native complex provider word.

The native audit (hpe_audit_and_transport.py) prices a provider word only through its frame chains: every gate
of A, B and the early-cleanup tail moves both of its registers to the gate frame, which must contain their
current frames; climbs are paid by their size. The scalar program never depends on the frames.

Given a word, this tool treats every A/B/tail gate frame as a variable X_g (a subspace of F_2^9) subject to
  X_g <= X_next(r)   for each register r of g and its next event (a later gate, the cut anchor, or its final frame),
and the fixed anchors (centre frames / target levels at the cut, terminal frames, hpe cone caps at end of B).
All constraints are of the form X <= Y or X <= const, so the componentwise intersection of two solutions is a
solution; a single reverse pass computes the greatest one, which contains the input word's frames.  Lower
anchors (start frames, cut equalities) are therefore preserved automatically.

Usage: frame_lift.py IN-FULL-WORD.json.gz OUT-FULL-WORD.json.gz [--mode greatest|search]
"""
import argparse, gzip, json, math, random, sys
from collections import Counter

H = 9
FULLMASK = (1 << (1 << H)) - 1


def span_mask(vecs):
    s = {0}
    for b in vecs:
        if b not in s:
            s |= {x ^ b for x in s}
    m = 0
    for x in s:
        m |= 1 << x
    return m


def dim(mask):
    return int(mask).bit_count().bit_length() - 1


def basis_of(mask):
    """reduced echelon basis (descending pivots), same canonical form as the audits' basis()."""
    els = [x for x in range(1, 1 << H) if mask >> x & 1]
    rows = []
    for x in els:
        for r in rows:
            if x ^ r < x:
                x ^= r
        if x:
            rows.append(x)
    # full reduction
    rows.sort(reverse=True)
    out = []
    for x in rows:
        for i, r in enumerate(out):
            if x ^ r < x:
                x ^= r
        if x:
            out = [r ^ x if (r ^ x) < r else r for r in out] + [x]
    return out


def perp_mask(p):
    return span_mask([z for z in range(1, 1 << H) if not (p & z).bit_count() % 2])


def regs(e):
    return [e[1]] + ([e[2]] if e[0] == 'add' else [])


def cost(prof, m=73, idle=48):
    """linearised recurrence weight of a profile, relative to idle filler (lower is better)."""
    return sum(n * r * (math.log(m / r) - math.log(m / idle)) for r, n in prof.items())


def events(word):
    """gate list [(part, index, gate)] in audit order and per-register event sequences."""
    gates = [('A', i, e) for i, e in enumerate(word['A'])] + [('B', i, e) for i, e in enumerate(word['B'])]
    tail = [(int(i), f) for i, f in word.get('early_cleanup', [])]
    for k, (i, f) in enumerate(tail):
        gates.append(('T', k, word['cleanup'][i][:-1] + [f]))
    return gates


def profile(word, frames=None):
    """paid profile exactly as the native audit's climb() (target levels / centre descents included)."""
    v = word['report']['v']; R = word['report']['R']; n = 2 * v + R
    gates = events(word)
    if frames is None:
        frames = [span_mask(g[2][-1]) for g in gates]
    cur = [1] * n   # mask 1 = the zero subspace {0}
    for t in range(v):
        cur[t] = span_mask([word['ports'][t]])
    for r, f in word.get('start_extra', {}).items():
        cur[int(r)] = span_mask(f)
    paid = Counter()

    def climb(r, f):
        o = cur[r]
        assert o & ~f == 0, ('nonmonotone', r)
        if o != f:
            paid[dim(f) - dim(o)] += 1; cur[r] = f
    lev = {int(t): span_mask(f) for t, f in word.get('target_levels', {}).items()}
    cut_done = False
    for (part, _, e), f in zip(gates, frames):
        if part != 'A' and not cut_done:
            cut_done = True
            for r, cf in zip(word['centers'], word['center_frames']):
                assert cur[r] == span_mask(cf), 'centre frame'
                served = sorted({lev.get(g[1] - v, 1) for g in word['cut'] if g[2] == r}, key=lambda m: -dim(m))
                o = span_mask(cf)
                for L in served:
                    assert L & ~o == 0
                    if L != o:
                        paid[dim(o) - dim(L)] += 1; o = L
            for t in range(v):
                assert cur[v + t] == lev.get(t, 1), ('target level', t)
        for r in regs(e):
            climb(r, f)
    for r, f in enumerate(final_frames(word)):
        climb(r, f)
    return paid


def final_frames(word):
    v = word['report']['v']; R = word['report']['R']
    fin = [FULLMASK] * v + [perp_mask(p) for p in word['ports']] + [FULLMASK] * R
    for r, f in word.get('helper_final', {}).items():
        fin[int(r)] = span_mask(f)
    return fin


def greatest(word, endB_cap=None, pinned=()):
    """greatest frame assignment; endB_cap: {register: mask} upper bounds at the end of B; pinned: gate ids kept."""
    v = word['report']['v']; R = word['report']['R']; n = 2 * v + R
    gates = events(word)
    orig = [span_mask(g[2][-1]) for g in gates]
    lev = {int(t): span_mask(f) for t, f in word.get('target_levels', {}).items()}
    cut_anchor = {}
    for r, cf in zip(word['centers'], word['center_frames']):
        cut_anchor[r] = span_mask(cf)
    for t in range(v):
        cut_anchor[v + t] = lev.get(t, 1)
    nA = len(word['A']); nAB = nA + len(word['B'])
    nxt = final_frames(word)
    X = [FULLMASK] * len(gates)
    pinned = set(pinned)
    if nAB == len(gates) and endB_cap:
        for r, m in endB_cap.items():
            nxt[r] &= m
    for gi in range(len(gates) - 1, -1, -1):
        part, _, e = gates[gi]
        f = FULLMASK
        for r in regs(e):
            f &= nxt[r]
        if gi in pinned:
            assert orig[gi] & ~f == 0
            f = orig[gi]
        X[gi] = f
        for r in regs(e):
            nxt[r] = f
        # crossing boundaries going backwards: before gate nAB (first tail gate) apply end-of-B caps,
        # before gate nA (first B gate) apply the cut anchors.
        if gi == nAB and endB_cap:
            for r, m in endB_cap.items():
                nxt[r] &= m
        if gi == nA:
            for r, m in cut_anchor.items():
                nxt[r] &= m
    # boundaries never crossed inside the loop (empty B or no tail)
    return X, orig


# Selected complex root a* (ASSEMBLY.json complex_lower). Each word's rank mass is fixed by its widths, so the
# moment at a* changes by sum over climbs of d*(m/d)^a*/(m*W): a profile change raises the complex root iff it
# lowers sum_climbs d*(73/d)^a*. FRAME_WEIGHT=exact uses that criterion (rescaled by 1/a*, minus the constant
# idle term); the default is its a->0 linearisation d*ln(48/d).
A_STAR = float(__import__('fractions').Fraction(__import__('os').environ.get('FRAME_ASTAR', '65528268492323474503/40000000000000000000000')))
EXACT = __import__('os').environ.get('FRAME_WEIGHT') == 'exact'


def W(d, m=73, idle=48):
    if not d:
        return 0.0
    if EXACT:
        return d * ((m / d) ** A_STAR - (m / idle) ** A_STAR) / A_STAR
    return d * (math.log(m / d) - math.log(m / idle))


def cone_caps(word):
    """end-of-B upper bounds implied by the audit's hpe cone pre-check: for every hyperplane-ended helper h with
    terminal U, each g in supp(row h of P^-1) and each g != h with P[g][h] != 0 must end B inside U."""
    from fractions import Fraction as Q
    import copy
    v = word['report']['v']; R = word['report']['R']; n = 2 * v + R
    hf = {int(r): span_mask(f) for r, f in word.get('helper_final', {}).items()}
    if not hf:
        return {}

    def apply(e, rows):
        if e[0] == 'scale':
            q = Q(e[2], e[3]); rows[e[1]] = {j: q * x for j, x in rows[e[1]].items()}
        else:
            t, s, q = e[1], e[2], Q(e[3], e[4])
            for j, x in list(rows[s].items()):
                z = rows[t].get(j, Q(0)) + q * x
                if z: rows[t][j] = z
                else: rows[t].pop(j, None)

    def inverse(e):
        e = copy.deepcopy(e)
        if e[0] == 'add': e[3] *= -1
        else: e[2], e[3] = e[3], e[2]
        return e
    main = word['A'] + word['cut'] + word['B']
    M = [{r: Q(1)} for r in range(n)]
    for e in main: apply(e, M)
    dirty = [{} for _ in range(n)]
    for r in range(v, 2 * v): dirty[r] = {j: x for j, x in M[r].items() if j >= 2 * v}
    for e in word['precondition']: apply(e, dirty)
    comp = [['add', r, j, -q.numerator, q.denominator, []] for r in range(v, 2 * v) for j, q in sorted(dirty[r].items())]
    prefix = word['precondition'] + comp + main
    P = [{r: Q(1)} for r in range(n)]
    for e in prefix: apply(e, P)
    Pinv = [{r: Q(1)} for r in range(n)]
    for e in reversed(prefix): apply(inverse(e), Pinv)
    caps = {}
    for h, U in hf.items():
        gs = {g for g, x in Pinv[h].items() if x} | {g for g in range(n) if g != h and P[g].get(h)}
        for g in gs:
            caps[g] = caps.get(g, FULLMASK) & U
    return caps


def chains(word, endB_cap=None):
    """per-register event chains: entries are ('g', gate id) or ('f', fixed mask)."""
    v = word['report']['v']; R = word['report']['R']; n = 2 * v + R
    gates = events(word)
    start = [1] * n
    for t in range(v):
        start[t] = span_mask([word['ports'][t]])
    for r, f in word.get('start_extra', {}).items():
        start[int(r)] = span_mask(f)
    lev = {int(t): span_mask(f) for t, f in word.get('target_levels', {}).items()}
    cut_anchor = {r: span_mask(cf) for r, cf in zip(word['centers'], word['center_frames'])}
    for t in range(v):
        cut_anchor[v + t] = lev.get(t, 1)
    ch = [[('f', start[r])] for r in range(n)]
    nA = len(word['A']); nAB = nA + len(word['B'])
    for gi, (part, _, e) in enumerate(gates):
        if gi == nA:
            for r, m in cut_anchor.items():
                ch[r].append(('a', m))   # cut anchor: the value just before it must EQUAL it (no climb at the cut)
        if gi == nAB and endB_cap:
            for r, m in endB_cap.items():
                ch[r].append(('cap', m))
        for r in regs(e):
            ch[r].append(('g', gi))
    if nAB == len(gates) and endB_cap:
        for r, m in endB_cap.items():
            ch[r].append(('cap', m))
    for r, f in enumerate(final_frames(word)):
        ch[r].append(('f', f))
    return ch


def search(word, X0, iters=6, seed=0, temp=0.0, endB_cap=None, log=print):
    """coordinate descent / annealing over gate frames inside the feasible interval of each gate."""
    rng = random.Random(seed)
    ch = chains(word, endB_cap)
    X = list(X0)
    # positions of each gate in its registers' chains
    pos = [[] for _ in X]
    for r, c in enumerate(ch):
        for k, (kind, val) in enumerate(c):
            if kind == 'g':
                pos[val].append((r, k))

    def val(r, k):
        kind, x = ch[r][k]
        return X[x] if kind == 'g' else x


    def prevv(r, k):
        k -= 1
        while ch[r][k][0] == 'cap':
            k -= 1
        return val(r, k)

    def nextv(r, k):
        """(upper bound, next real value)"""
        k += 1; ub = FULLMASK
        while ch[r][k][0] == 'cap':
            ub &= ch[r][k][1]; k += 1
        nv = val(r, k)
        return ub & nv, nv

    def local(g, x):
        c = 0.0
        for r, k in pos[g]:
            p = prevv(r, k); _, q = nextv(r, k)
            if p != x: c += W(dim(x) - dim(p))
            if x != q: c += W(dim(q) - dim(x))
        return c

    def total():
        c = 0.0
        for r in range(len(ch)):
            vals = [val(r, k) for k in range(len(ch[r])) if ch[r][k][0] != 'cap']
            for a, b in zip(vals, vals[1:]):
                if a != b: c += W(dim(b) - dim(a))
        return c
    order = list(range(len(X)))
    for it in range(iters):
        improved = 0
        rng.shuffle(order)
        for g in order:
            lo = 1; hi = FULLMASK; cands = set()
            for r, k in pos[g]:
                p = prevv(r, k); ub, q = nextv(r, k)
                lo |= p; hi &= ub; cands.add(p); cands.add(q & ub)
            # lo as a subspace: sum of subspaces = span of union
            lo = span_mask([x for x in range(1 << H) if lo >> x & 1])
            assert lo & ~hi == 0, ('infeasible interval', g)
            cands = {c for c in cands if lo & ~c == 0 and c & ~hi == 0} | {lo, hi, X[g]}
            if any(ch[r][k + 1][0] == 'a' for r, k in pos[g]):
                cands = {X[g]}   # the gate right before a cut anchor must equal it
            cur = local(g, X[g])
            best = min(cands, key=lambda c: (local(g, c), -dim(c)))
            bc = local(g, best)
            if bc < cur - 1e-12 or (temp and best != X[g] and rng.random() < math.exp(-(bc - cur) / temp)):
                if bc < cur - 1e-12: improved += 1
                X[g] = best
        log('iter', it, 'improved', improved, 'total %.3f' % total())
        if not improved and not temp:
            break
    return X


def push_search(word, X0, steps=200000, seed=0, temp0=0.3, endB_cap=None, log=print):
    """annealing with closure moves: raise gate g to X_g+F (propagating sums forward along every chain) or lower
    it to X_g & F (propagating intersections backward). Every accepted state is feasible by construction."""
    rng = random.Random(seed)
    ch = chains(word, endB_cap)
    X = list(X0)
    pos = [[] for _ in X]
    for r, c in enumerate(ch):
        for k, (kind, v_) in enumerate(c):
            if kind == 'g':
                pos[v_].append((r, k))
    sumcache = {}

    def ssum(a, b):
        if a & ~b == 0: return b
        if b & ~a == 0: return a
        key = (a, b)
        s = sumcache.get(key)
        if s is None:
            s = span_mask([x for x in range(1 << H) if (a | b) >> x & 1])
            sumcache[key] = s
        return s

    def rcost(r, Xs):
        c = 0.0; prev = None
        for kind, x in ch[r]:
            if kind == 'cap': continue
            v_ = Xs.get(x, X[x]) if kind == 'g' else x
            if prev is not None and prev != v_: c += W(dim(v_) - dim(prev))
            prev = v_
        return c

    def up(g, F):
        new = {g: ssum(X[g], F)}
        stack = [g]
        while stack:
            h = stack.pop(); val_ = new[h]
            for r, k in pos[h]:
                k2 = k + 1; ub = FULLMASK
                while ch[r][k2][0] == 'cap': ub &= ch[r][k2][1]; k2 += 1
                if val_ & ~ub: return None
                kind, x = ch[r][k2]
                if kind in ('f', 'a'):
                    if val_ & ~x or (kind == 'a' and val_ != x): return None
                    continue
                cur = new.get(x, X[x])
                if val_ & ~cur:
                    new[x] = ssum(cur, val_); stack.append(x)
        return new

    def down(g, F):
        new = {g: X[g] & F}
        stack = [g]
        while stack:
            h = stack.pop(); val_ = new[h]
            for r, k in pos[h]:
                k2 = k - 1
                while ch[r][k2][0] == 'cap': k2 -= 1
                kind, x = ch[r][k2]
                if kind in ('f', 'a'):
                    if x & ~val_: return None
                    continue
            for r, k in pos[h]:
                if ch[r][k + 1][0] == 'a' and ch[r][k + 1][1] != val_: return None
                cur = new.get(x, X[x])
                if cur & ~val_:
                    new[x] = cur & val_; stack.append(x)
        return new

    def total():
        return sum(rcost(r, {}) for r in range(len(ch)))
    best_total = cur_total = total(); best = list(X)
    log('start total %.3f' % cur_total)
    G = len(X); stats = Counter(); deltas = []
    for step in range(steps):
        temp = temp0 * (1 - step / steps)
        g = rng.randrange(G)
        # candidate frame: a neighbouring value in one of g's chains
        r, k = rng.choice(pos[g])
        k2 = k + rng.choice((-1, 1))
        while ch[r][k2][0] == 'cap': k2 += 1 if k2 > k else -1
        kind, x = ch[r][k2]
        F = X[x] if kind == 'g' else x
        new = up(g, F) if k2 > k else down(g, F)
        if not new:
            stats["infeasible"] += 1; continue
        if all(new[h] == X[h] for h in new):
            stats["noop"] += 1; continue
        stats["tried"] += 1
        affected = {r_ for h in new for r_, _ in pos[h]}
        delta = sum(rcost(r_, new) - rcost(r_, {}) for r_ in affected); deltas.append(delta)
        if delta < -1e-12 or (temp > 0 and rng.random() < math.exp(-delta / temp)):
            for h, v_ in new.items(): X[h] = v_
            cur_total += delta
            if cur_total < best_total - 1e-9:
                best_total = cur_total; best = list(X)
        if step % 50000 == 0:
            log('step', step, 'cur %.3f best %.3f' % (cur_total, best_total))
    deltas.sort(); log("stats", dict(stats), "best deltas", [round(d, 3) for d in deltas[:8]])
    return best


def apply_frames(word, X):
    import copy
    w = copy.deepcopy(word)
    gates = events(w)
    early = list(w.get('early_cleanup', []))
    for (part, i, e), f in zip(gates, X):
        b = basis_of(f)
        if part == 'A':
            w['A'][i][-1] = b
        elif part == 'B':
            w['B'][i][-1] = b
        else:
            early[i] = [early[i][0], b]
    if 'early_cleanup' in w:
        w['early_cleanup'] = early
    return w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out', nargs='?')
    ap.add_argument('--steps', type=int, default=200000); ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--temp', type=float, default=0.3)
    a = ap.parse_args()
    word = json.load(gzip.open(a.src))
    p0 = profile(word)
    X, orig = greatest(word)
    assert all(o & ~x == 0 for o, x in zip(orig, X))
    p1 = profile(word, X)
    print('input   ', dict(sorted(p0.items())), 'mass', sum(r * c for r, c in p0.items()), 'cost %.3f' % cost(p0))
    print('greatest', dict(sorted(p1.items())), 'mass', sum(r * c for r, c in p1.items()), 'cost %.3f' % cost(p1))
    print('changed gates', sum(o != x for o, x in zip(orig, X)))
    Y = search(word, orig, iters=30)
    Y = push_search(word, Y, steps=a.steps, seed=a.seed, temp0=a.temp)
    Y = search(word, Y, iters=30)
    p2 = profile(word, Y)
    print('search  ', dict(sorted(p2.items())), 'mass', sum(r * c for r, c in p2.items()), 'cost %.3f' % cost(p2))
    print('changed gates', sum(o != x for o, x in zip(orig, Y)))
    if a.out:
        w = apply_frames(word, Y)
        assert profile(w) == p2
        w['report']['local_profile'] = {str(k): z for k, z in sorted(p2.items())}
        open(a.out, 'wb').write(gzip.compress(json.dumps(w, sort_keys=True, separators=(',', ':')).encode(), mtime=0))


if __name__ == '__main__':
    main()
