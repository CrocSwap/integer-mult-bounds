#!/usr/bin/env python3
"""Terminal-sink substitution (PR #166) on the paired-cube complex word with its frozen physical layer.

The substitution is the terminal-sink lemma of PR #166 by jamesyc (closed by its author), independently audited
here: this gate's own frame scans, replay and controls carry the soundness argument and do not use #166's checker.
Gate, audit and integration by eumemic with Anthropic Claude assistance.  Apache-2.0.

Sink.  An auxiliary role z that starts at frame 0 with no gauge (no source injection, not a donor or recipient),
is written only as a destination (z <- z + b*a, never a control), never in phase one, at frames
0 <= F_1 <= ... <= F_k <= U (the frame of its single side root, read y_t += c*z for t in T), and has a pivot p in T
with no deferred old-value read of p between the phase cut and z's last write.  Then z is deleted and:
  1. at the phase cut, after the copied-centre scatter:  y_t -= y_p  for t in T - p, at frame 0;
  2. at each original write time:                       y_p += c*b*a, at frame F_i;
  3. right after the last write:                        y_t += y_p  for t in T - p, at frame U.
Ledger per sink: one physical register fewer and, per core, one child r = rank U and one child h - r fewer; the
deficit is unchanged.

Checks (sinks_record), from the regenerated word, the frozen layer (references/paired-cube/physical) and sinks.json:
  - every sink satisfies the conditions above, recomputed from the word, the layer and the read schedule
    (#161's: a recipient is read at its frozen read op, an unpaired gauge at the phase cut), and target groups of
    different sinks are disjoint;
  - the literal substituted stage word (X ports, Y ports, physical slots; time-0 and deferred reads, injections,
    ops, the centre scatter, side-root reads, K on the sources, full-frame inverses) has every frame step nested,
    forward and literally reflected;
  - the unsubstituted word's literal per-stage histogram equals #161's record over three stages, and the
    substituted word's is that minus [r] and [h - r] per sink; the change is booked per register class
    (auxiliary slots and centre copies: local; X: source data; Y: target data) onto #161's record;
  - a dirty-scratch replay mod 2^61-1 gives (X, Y + X, Z) forward and (X - Y, Y, Z) reflected;
  - controls that must be rejected: a sandwich raised before the centre scatter, an omitted post-shear, an
    uncomplemented reflected pivot write, and a post-shear moved after its pivot's first correction.
The record has the shape of paired_cube_physical.physical() with the sinks applied (plus a 'sinks' entry), so
paired_cube_network.py prices it as the complex profile.

Why all-eight roots only: on this word the face0 sinks that meet the conditions fail the frame scan, because the
post-shear at their rank-19 U raises target registers above later rank-18 reads.

usage: sinks_gate.py [--write]                         (frozen check against certificates/paired-cube-sinks-input.json)
       sinks_gate.py --tree=T --work=W --layer=L --sinks=S.json [--out=X.json]   (dumped word; pipeline use)
"""
import json
import random
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SINKS = HERE / 'sinks.json'
OUTPUT = ROOT / 'certificates/paired-cube-sinks-input.json'
P = (1 << 61) - 1


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sinks_record(g, witness, word, record, frames_in, pairs_in, sinks_in, base):
    """Apply and check the substitution; base = paired_cube_physical.physical(...) of the same layer."""
    h, v, R = g['h'], g['v'], record['R']

    @lru_cache(maxsize=None)
    def basis(rows):
        b, mask = {}, 0
        for x in rows:
            mm = x & mask
            while mm:
                p = mm.bit_length() - 1
                x ^= b[p]
                mm ^= 1 << p
            if x:
                p = x.bit_length() - 1
                for k in list(b):
                    if b[k] >> p & 1:
                        b[k] ^= x
                b[p] = x
                mask |= 1 << p
        return tuple(b[p] for p in sorted(b, reverse=True))

    @lru_cache(maxsize=None)
    def perp(U):
        U = basis(U)
        piv = {r.bit_length() - 1: r for r in U}
        out = []
        for j in range(h):
            if j not in piv:
                x = 1 << j
                for p, r in piv.items():
                    if r >> j & 1:
                        x |= 1 << p
                out.append(x)
        return basis(tuple(out))

    @lru_cache(maxsize=None)
    def contained(Aa, Bb):
        rb = basis(Bb)
        return len(basis(rb + tuple(Aa))) == len(rb)

    ZERO, FULL = (), basis(tuple(1 << i for i in range(h)))
    inputs, labels = g['inputs'], g['labels']
    roots = [dict(r, node=r['node'] + 1) for r in g['roots']]
    args = [None] + [None if a is None else (a[0] + 1, a[1] + 1) for a in g['args']]
    ann = witness['annihilators']
    ops = [tuple(o) for o in word['ops']]
    coef = [tuple(c) for c in word['opcoeff']]
    require(all(ca == 1 for ca, cb in coef), 'Every operation is a shear dest += cb*control')
    frames = [perp(tuple(ann[x])) for _, _, x in ops]
    for i, F in frames_in:
        frames[i] = basis(tuple(F))
    pairs = [(int(a), int(b)) for a, b, _ in pairs_in]
    deadline = {int(b): (None if t is None else int(t)) for _, b, t in pairs_in}
    phase1 = sorted(word['phase1'])
    pset = set(phase1)
    rest = [i for i in range(len(ops)) if i not in pset]
    position = {i: k for k, i in enumerate(phase1 + rest)}
    sources = {int(x): s for x, s in word['sources'].items()}
    rootroles = word['rootroles']
    selected = [z['role'] for z in word['selected']]
    gauge_targets = {z['role']: z['targets'] for z in word['selected']}
    merge = {b: a for a, b in pairs}
    live = sorted(set(range(R)) - set(merge))
    slot = {s: i for i, s in enumerate(live)}
    X = lambda t: t
    Y = lambda t: v + t
    A = lambda s: 2 * v + slot[merge.get(s, s)]
    NREG = 2 * v + len(live)

    # exact responses of the unsubstituted word (every retained read keeps its original column)
    inv = lambda x: pow(x % P, P - 2, P)
    HALF, THIRD, SIXTH = inv(2), inv(3), inv(6)
    cseed, dseed, rootframe, rootorder, span = {}, {}, {}, [], {}
    for x in range(1, len(args)):
        span[x] = basis((inputs[x - 1],)) if args[x] is None else basis(span[args[x][0]] + span[args[x][1]])
    for r, s in zip(roots, rootroles):
        if r['kind'] == 'center':
            c = [0] * h
            c[r['coordinate']] = 1
            cseed[s] = c
            rootframe[s] = span[r['node']]
        else:
            dseed[s] = {t: (HALF if q == '1/2' else P - HALF) for t, q in zip(r['targets'], r['coefficients'])}
            rootframe[s] = perp(basis(tuple(inputs[t] for t in r['targets'])))
            rootorder.append((s, r['targets']))
    cvec, dpart = [None] * R, [dict() for _ in range(R)]
    for s, c in cseed.items():
        cvec[s] = list(c)
    for s, d in dseed.items():
        dpart[s] = dict(d)
    for (a, b, x), (ca, cb) in zip(reversed(ops), reversed(coef)):
        if cvec[a] is not None:
            cvec[b] = [(cb * u) % P for u in cvec[a]] if cvec[b] is None else [(w + cb * u) % P for w, u in zip(cvec[b], cvec[a])]
        if dpart[a]:
            db = dpart[b]
            for t, u in dpart[a].items():
                db[t] = (db.get(t, 0) + cb * u) % P
    scatter = [[THIRD if c in labels[t] else (P - SIXTH) for t in range(v)] for c in range(h)]
    deferred = set(selected)

    def reach(s, mode):
        if mode == 'seed':
            return sorted(dseed.get(s, {}))
        return list(range(v)) if cvec[s] is not None else sorted(t for t, u in dpart[s].items() if u)

    read_op = {s: (deadline[s] if deadline.get(s) is not None else rest[0]) for s in selected}
    require(all(op not in pset for op in read_op.values()), 'Deferred read inside phase one')
    reads_at = {}
    for s in reversed(selected):
        reads_at.setdefault(read_op[s], []).append(s)
    gauge = {z['role']: perp(basis(tuple(z['annihilator']))) for z in word['selected']}
    leaf_of = {s: x for x, s in sources.items()}
    first_read = {}
    for s in selected:
        for t in gauge_targets[s]:
            first_read[t] = min(first_read.get(t, 1 << 60), position[read_op[s]])

    # sinks: recompute and check every condition
    sink = {}
    for s, p in sinks_in:
        js = [j for j, r in enumerate(rootroles) if r == s]
        require(len(js) == 1 and roots[js[0]]['kind'] == 'side', 'Sink %d: exactly one side root' % s)
        j = js[0]
        T = list(roots[j]['targets'])
        require(len(set(roots[j]['coefficients'])) == 1, 'Sink %d: one root coefficient' % s)
        require(s not in merge and s not in set(merge.values()) and s not in deferred, 'Sink %d: no pair, no gauge' % s)
        require(s not in sources.values() and s not in cseed, 'Sink %d: no source injection, not a centre' % s)
        W_ = [i for i, (a, b, x) in enumerate(ops) if a == s]
        require(W_ and not any(b == s for a, b, x in ops), 'Sink %d: destination-only writes' % s)
        require(all(i not in pset for i in W_), 'Sink %d: no write in phase one' % s)
        U = rootframe[s]
        path = [ZERO] + [frames[i] for i in W_] + [U]
        require(all(contained(p0, p1) for p0, p1 in zip(path, path[1:])), 'Sink %d: write frames nested into U' % s)
        require(cvec[s] is None and dpart[s] == dseed[s], 'Sink %d: response equals its root seed' % s)
        last = max(position[i] for i in W_)
        require(p in T and first_read.get(p, 1 << 60) > last, 'Sink %d: pivot corrected before the last write' % s)
        sink[s] = dict(T=T, c=p, writes=W_, U=U, coeff=roots[j]['coefficients'][0])
    targets = [t for z in sink.values() for t in z['T']]
    require(len(targets) == len(set(targets)), 'Target groups of different sinks are disjoint')

    def build(active, control=None, ctl_sink=None, ctl_op=None):
        sink_of_write = {i: s for s, z in active.items() for i in z['writes']}
        last_write = {z['writes'][-1]: s for s, z in active.items()}
        W, fwd_ops = [], []

        def op_event(i):
            a, b, x = ops[i]
            fwd_ops.append(i)
            return ('op', A(a), A(b), coef[i][1], frames[i])
        for s in range(R):
            if s not in deferred and s not in active:
                W.append(('read', A(s), s, -1, 'resp', ZERO, 'Y', reach(s, 'resp')))
        for s, xnode in sorted(leaf_of.items()):
            W.append(('inj', A(s), X(xnode - 1), 1, basis((inputs[xnode - 1],))))
        if control == 'early_raise':
            z = active[ctl_sink]
            W += [('ysh', Y(t), Y(z['c']), -1, frames[z['writes'][0]]) for t in z['T'] if t != z['c']]
        for i in phase1:
            W.append(op_event(i))
        for s in cseed:
            W.append(('centre', A(s), s, 1, rootframe[s], ZERO, 'Y'))
        for s, z in active.items():                   # 1. pre-shears at the phase cut, frame 0
            if not (control == 'early_raise' and s == ctl_sink):
                W += [('ysh', Y(t), Y(z['c']), -1, ZERO) for t in z['T'] if t != z['c']]
        for i in rest:
            for s in reads_at.get(i, ()):
                W.append(('read', A(s), s, -1, 'resp', gauge[s], 'Y', gauge_targets[s]))
            if i in sink_of_write:                    # 2. pivot writes at the original write frames
                s = sink_of_write[i]
                k = coef[i][1] * (HALF if active[s]['coeff'] == '1/2' else P - HALF) % P
                W.append(('yw', Y(active[s]['c']), A(ops[i][1]), k, frames[i]))
            else:
                W.append(op_event(i))
            posts = [last_write[i]] if i in last_write and not (control == 'late_post' and last_write[i] == ctl_sink) else []
            if control == 'late_post' and i == ctl_op:
                posts.append(ctl_sink)
            for s in posts:                           # 3. post-shears after the last write, frame U
                if not (control == 'omit_post' and s == ctl_sink):
                    z = active[s]
                    W += [('ysh', Y(t), Y(z['c']), +1, z['U']) for t in z['T'] if t != z['c']]
        for s, tg in rootorder:
            if s not in active:
                W.append(('read', A(s), s, 1, 'seed', rootframe[s], 'Y', tg))
        for b0 in range(0, v, 8):
            qs = [inputs[b0 + k] for k in range(8)]
            K2 = [[1 if (qs[i] ^ qs[j]).bit_count() == 6 else -1 if (qs[i] ^ qs[j]).bit_count() == 2 else 0
                   for j in range(8)] for i in range(8)]
            for parity in (0, 1):
                S = [k for k in range(8) if k.bit_count() % 2 == parity]
                Tg = [k ^ 7 for k in S]
                Tm = [[K2[j][i] * HALF % P for i in S] for j in Tg]
                regs = [X(b0 + k) for k in S]
                W.append(('ktr', regs, Tm, basis(tuple(qs[k] for k in S)), 'X'))
                W += [('kd', Y(b0 + Tg[k]), X(b0 + S[k]), 1, perp(basis((qs[Tg[k]],)))) for k in range(4)]
                W.append(('ktr', regs, [[Tm[l][k] for l in range(4)] for k in range(4)], FULL, 'X'))
        W += [('op', A(ops[i][0]), A(ops[i][1]), -coef[i][1], FULL) for i in reversed(fwd_ops)]
        W += [('inj', A(s), X(x - 1), -1, FULL) for s, x in sorted(leaf_of.items(), reverse=True)]
        return W

    swapXY = lambda r: r + v if r < v else (r - v if r < 2 * v else r)

    def reflect(e):
        k = e[0]
        if k == 'read':
            _, a, s, sg, mode, F, bank, tg = e
            return ('read', a, s, -sg, mode, perp(F), 'X' if bank == 'Y' else 'Y', tg)
        if k == 'centre':
            _, a, s, sg, F, G, bank = e
            return ('centre', a, s, -sg, perp(F), perp(G), 'X' if bank == 'Y' else 'Y')
        if k == 'inj':
            return ('inj', e[1], swapXY(e[2]), -e[3], perp(e[4]))
        if k == 'op':
            return ('op', e[1], e[2], -e[3], perp(e[4]))
        if k == 'ysh':
            return ('ysh', swapXY(e[1]), swapXY(e[2]), -e[3], perp(e[4]))
        if k == 'yw':
            return ('yw', swapXY(e[1]), e[2], (P - e[3]) % P, perp(e[4]))
        if k == 'ktr':
            M = e[2]
            return ('ktr', [swapXY(r) for r in e[1]], [[M[l][kk] for l in range(4)] for kk in range(4)], perp(e[3]),
                    'Y' if e[4] == 'X' else 'X')
        if k == 'kd':
            return ('kd', swapXY(e[1]), swapXY(e[2]), -e[3], perp(e[4]))
        raise ValueError(k)

    def ends(active):
        removed = {A(s) for s in active}
        st, fi = [None] * NREG, [None] * NREG
        for t in range(v):
            st[X(t)], st[Y(t)] = basis((inputs[t],)), ZERO
            fi[X(t)], fi[Y(t)] = FULL, perp(basis((inputs[t],)))
        for s in live:
            st[A(s)], fi[A(s)] = gauge.get(s, ZERO), FULL
        for r in removed:
            st[r] = fi[r] = ZERO
        rs, rf = [None] * NREG, [None] * NREG
        for r in range(NREG):
            rs[swapXY(r)], rf[swapXY(r)] = perp(fi[r]), perp(st[r])
        for r in removed:
            rs[r] = rf[r] = ZERO
        return removed, (st, fi), (rs, rf)

    def framescan(events, st, fin, removed):
        """Per-stage children split by register class: local (slots and centre copies), source (X), target (Y)."""
        cur = list(st)
        H = {'local': Counter(), 'source': Counter(), 'target': Counter()}
        cls = lambda r: 'source' if r < v else ('target' if r < 2 * v else 'local')

        def promote(r, F):
            require(r not in removed, 'Deleted sink touched')
            old = cur[r]
            if old is F:
                return
            require(contained(old, F), 'Frame step not nested (register %d, %d -> %d)' % (r, len(old), len(F)))
            if len(F) > len(old):
                H[cls(r)][len(F) - len(old)] += 1
            cur[r] = F
        for e in events:
            k = e[0]
            if k == 'read':
                _, a, s, sg, mode, F, bank, tg = e
                promote(a, F)
                for t in tg:
                    promote((0 if bank == 'X' else v) + t, F)
            elif k == 'centre':
                _, a, s, sg, F, G, bank = e
                require(contained(G, F) or contained(F, G), 'Centre frames comparable')
                promote(a, F)
                H['local'][abs(len(F) - len(G))] += 1
                for t in range(v):
                    promote((0 if bank == 'X' else v) + t, G)
            elif k in ('inj', 'op', 'ysh', 'yw', 'kd'):
                require(e[1] != e[2], 'Distinct registers')
                promote(e[1], e[4])
                promote(e[2], e[4])
            elif k == 'ktr':
                for r in e[1]:
                    promote(r, e[3])
        for r in range(NREG):
            if r not in removed:
                promote(r, fin[r])
        return H

    def run_scalar(events, xin, yin, zin):
        bank, a = {'X': list(xin), 'Y': list(yin)}, list(zin)
        pend = {'X': [0] * h, 'Y': [0] * h}

        def flush(bnk):
            B = bank[bnk]
            for kk in range(h):
                f = pend[bnk][kk]
                if f:
                    row = scatter[kk]
                    for t in range(v):
                        B[t] = (B[t] + f * row[t]) % P
                    pend[bnk][kk] = 0

        def get(r):
            if r < 2 * v:
                bnk = 'X' if r < v else 'Y'
                flush(bnk)
                return bank[bnk][r % v]
            return a[r - 2 * v]

        def add(r, val):
            if r < 2 * v:
                B = bank['X' if r < v else 'Y']
                B[r % v] = (B[r % v] + val) % P
            else:
                a[r - 2 * v] = (a[r - 2 * v] + val) % P
        for e in events:
            k = e[0]
            if k == 'read':
                _, ar, s, sg, mode, F, bnk, tg = e
                val = a[ar - 2 * v]
                c = cseed.get(s) if mode == 'seed' else cvec[s]
                d = dseed.get(s, {}) if mode == 'seed' else dpart[s]
                if c is not None:
                    for kk, u in enumerate(c):
                        if u:
                            pend[bnk][kk] = (pend[bnk][kk] + sg * u * val) % P
                B = bank[bnk]
                for t, u in d.items():
                    B[t] = (B[t] + sg * u * val) % P
            elif k == 'centre':
                _, ar, s, sg, F, G, bnk = e
                val = a[ar - 2 * v]
                for kk, u in enumerate(cseed[s]):
                    if u:
                        pend[bnk][kk] = (pend[bnk][kk] + sg * u * val) % P
            elif k in ('inj', 'op', 'ysh', 'yw', 'kd'):
                add(e[1], e[3] * get(e[2]))
            elif k == 'ktr':
                regs, M = e[1], e[2]
                vals = [get(r) for r in regs]
                for kk, r in enumerate(regs):
                    add(r, sum(M[kk][l] * vals[l] for l in range(4)) % P - vals[kk])
        flush('X')
        flush('Y')
        return bank['X'], bank['Y'], a

    def replay(Wf, removed, seed):
        rng = random.Random(seed)
        x0 = [rng.randrange(P) for _ in range(v)]
        y0 = [rng.randrange(P) for _ in range(v)]
        z0 = [rng.randrange(P) for _ in live]
        keep = [i for i, s in enumerate(live) if A(s) not in removed]
        xf, yf, zf = run_scalar(Wf, x0, y0, z0)
        fwd = xf == x0 and all((yf[t] - y0[t] - x0[t]) % P == 0 for t in range(v)) and all(zf[i] == z0[i] for i in keep)
        xr, yr, zr = run_scalar([reflect(e) for e in reversed(Wf)], x0, y0, z0)
        ref = all((xr[t] - x0[t] + y0[t]) % P == 0 for t in range(v)) and yr == y0 and all(zr[i] == z0[i] for i in keep)
        return fwd, ref

    # the unsubstituted word: its literal per-stage histogram is #161's record over three stages
    removed0, (st0, fi0), _ = ends({})
    H0 = framescan(build({}), st0, fi0, removed0)
    cover = Counter({int(r): n for r, n in base['child_histogram'].items()})
    cover.subtract(Counter(3 * len(gauge[s]) for s in live if s in gauge))
    cover[2] -= 2 * v
    require(all(n >= 0 and n % 3 == 0 for n in cover.values()), 'Cover children are a three-stage multiple')
    require(sum(H0.values(), Counter()) == Counter({r: n // 3 for r, n in cover.items() if n}),
            'Literal per-stage histogram of the unsubstituted word = #161 record / 3')
    # the substituted word
    removed, (st, fi), (rst, rfi) = ends(sink)
    W = build(sink)
    Hf = framescan(W, st, fi, removed)
    Hr = framescan([reflect(e) for e in reversed(W)], rst, rfi, removed)
    require(sum(Hf.values(), Counter()) == sum(Hr.values(), Counter()), 'Reflected per-stage histogram')
    delta = sum(H0.values(), Counter())
    delta.subtract(sum(Hf.values(), Counter()))
    expect = Counter()
    for z in sink.values():
        expect[len(z['U'])] += 1
        expect[h - len(z['U'])] += 1
    require(+delta == expect and not -delta, 'Per-stage histogram drops [r] and [h - r] per sink')
    fwd, ref = replay(W, removed, 166)
    require(fwd and ref, 'Dirty-scratch replay forward (X, Y+X, Z) and reflected (X-Y, Y, Z)')
    controls = {}

    def rejected(Wc):
        try:
            framescan(Wc, st, fi, removed)
            framescan([reflect(e) for e in reversed(Wc)], rst, rfi, removed)
        except AssertionError:
            return True
        return not all(replay(Wc, removed, 168))
    s0 = next(iter(sink))
    controls['early_raise'] = rejected(build(sink, 'early_raise', s0))
    controls['omit_post_shear'] = rejected(build(sink, 'omit_post', s0))
    bad = [reflect(e) for e in reversed(W)]
    j = next(j for j, e in enumerate(bad) if e[0] == 'yw' and 3 <= len(e[4]) <= h - 3)
    bad[j] = bad[j][:4] + (perp(bad[j][4]),)
    try:
        framescan(bad, rst, rfi, removed)
        controls['uncomplemented_reflected_pivot_write'] = False
    except AssertionError:
        controls['uncomplemented_reflected_pivot_write'] = True
    pc, sl, tl = min((first_read[t], s, t) for s, z in sink.items() for t in z['T'] if t in first_read)
    moved = dict(sink)
    moved[sl] = dict(sink[sl], c=tl)
    controls['post_shear_after_pivot_correction'] = rejected(build(moved, 'late_post', sl, (phase1 + rest)[pc]))
    require(all(controls.values()), 'Every control is rejected')
    # the substituted record, in physical()'s format
    rec = json.loads(json.dumps(base))
    for name, cls in (('local_histogram', 'local'), ('source_data_histogram', 'source'), ('target_data_histogram', 'target')):
        Hc = Counter({int(r): n for r, n in base[name].items()})
        Hc.update(Hf[cls])
        Hc.subtract(H0[cls])
        require(all(n >= 0 for n in Hc.values()), 'Nonnegative %s children' % cls)
        rec[name] = {str(r): n for r, n in sorted(Hc.items()) if n}
    m = 3 * h
    C = Counter({int(r): n for r, n in base['child_histogram'].items()})
    for r, n in expect.items():
        C[r] -= 3 * n
    C = Counter({r: n for r, n in C.items() if n})
    require(min(C.values()) > 0, 'Positive children')
    rec['child_histogram'] = {str(r): C[r] for r in sorted(C)}
    rec['physical_R'] = base['physical_R'] - len(sink)
    rec['W_per_vertex'] = base['W_per_vertex'] - len(sink)
    rec['rank_per_vertex'] = sum(r * n for r, n in C.items())
    rec['deficit_per_vertex'] = rec['W_per_vertex'] * m - rec['rank_per_vertex']
    require(rec['deficit_per_vertex'] == base['deficit_per_vertex'], 'Deficit unchanged')
    rec['sinks'] = len(sink)
    rec['sink_substitution'] = dict(
        lemma='terminal-sink lemma of PR #166 by jamesyc (closed by its author), independently audited here', sinks=[[s, z['c']] for s, z in sink.items()],
        root_ranks={str(r): n for r, n in sorted(Counter(len(z['U']) for z in sink.values()).items())},
        per_stage_removed={str(r): n for r, n in sorted(expect.items())}, events=len(W),
        forward_and_reflected_nested=True, replay_seed=166, replay_forward=fwd, replay_reflected=ref,
        controls_rejected=controls)
    return rec


def checked_sinks_record():
    """Regenerate the word, check the frozen layer with #161's checker, apply sinks.json, compare the frozen record."""
    sys.path.insert(0, str(ROOT / 'scripts'))
    import paired_cube_physical as PCP
    g, witness, word, record = PCP.regenerated_word()
    frames_in = json.loads((PCP.REF / 'frames.json').read_text())['frames']
    pairs_in = json.loads((PCP.REF / 'pairs.json').read_text())['pairs']
    base = PCP.physical(g, witness, word, record, frames_in, pairs_in)
    require(json.loads(PCP.OUTPUT.read_text()) == json.loads(json.dumps(base)), 'Frozen physical input differs')
    result = sinks_record(g, witness, word, record, frames_in, pairs_in, json.loads(SINKS.read_text())['sinks'], base)
    require(json.loads(OUTPUT.read_text()) == json.loads(json.dumps(result)), 'Frozen sinks input differs')
    return result


def main():
    flags = dict(a.split('=', 1) if '=' in a else (a, True) for a in sys.argv[1:])
    if '--work' in flags:
        tree = Path(flags['--tree']).resolve()
        sys.path.insert(0, str(tree / 'scripts'))
        import paired_cube_physical as PCP
        g, witness, word, record = (json.loads((Path(flags['--work']) / n).read_text()) for n in
                                    ('graph.json', 'frames.json', 'selection.json', 'record.json'))
        frames_in = json.loads((Path(flags['--layer']) / 'frames.json').read_text())['frames']
        pairs_in = json.loads((Path(flags['--layer']) / 'pairs.json').read_text())['pairs']
        base = PCP.physical(g, witness, word, record, frames_in, pairs_in)
        result = sinks_record(g, witness, word, record, frames_in, pairs_in,
                              json.loads(Path(flags['--sinks']).read_text())['sinks'], base)
        if '--out' in flags:
            Path(flags['--out']).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        sys.path.insert(0, str(ROOT / 'scripts'))
        import paired_cube_physical as PCP
        g, witness, word, record = PCP.regenerated_word()
        frames_in = json.loads((PCP.REF / 'frames.json').read_text())['frames']
        pairs_in = json.loads((PCP.REF / 'pairs.json').read_text())['pairs']
        base = PCP.physical(g, witness, word, record, frames_in, pairs_in)
        result = sinks_record(g, witness, word, record, frames_in, pairs_in, json.loads(SINKS.read_text())['sinks'], base)
        text = json.dumps(result, indent=2, sort_keys=True) + '\n'
        if '--write' in flags:
            OUTPUT.write_text(text)
        else:
            require(OUTPUT.read_text() == text, 'Frozen sinks input differs')
    print('PASS terminal sinks: %d sinks (root ranks %s), W %d -> %d, deficit %d; nested forward and reflected, '
          'replay and %d controls rejected' % (result['sinks'], result['sink_substitution']['root_ranks'],
                                               base['W_per_vertex'], result['W_per_vertex'],
                                               result['deficit_per_vertex'], len(result['sink_substitution']['controls_rejected'])))


if __name__ == '__main__':
    main()
