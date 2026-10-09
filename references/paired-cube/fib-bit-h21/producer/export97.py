#!/usr/bin/env python3
"""Export a bitcomp/bitcomp_w compiled bit word to PR97's frozen-data format (witness_<h>.json.gz and
deferred_<h>.json.gz, as read by PR97's deferred.py, Swapnil Jain's round-seven checkers and an independent
B-defer replay).

Lifted frames are M_n = U_n: flag = identity and j(n) = h for every lifted addition (span(n) <= U_n, so
span(n) + (U_n cap F_h) = U_n). Deferred readout frames sigma_u and V-leaf starts s_i are bitcomp_w.bdefer's, as
primitive integer bases recovered from the mod-p frames by rational reconstruction and verified exactly.
usage: export97.py DAG.json OUTDIR [--choice AAA] [--witness]   (DAG: the kit's dump, or a witness with --witness)"""
import argparse, gzip, json, math, os, sys
from collections import defaultdict
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bitcomp as bc
import bitcomp_w as bw
from linalg_p import P, Span, kernel, span_of

HALF = math.isqrt(P // 2)


def ratrec(x):
    """a/b == x mod P with |a|, b <= sqrt(P/2), or None"""
    x %= P
    r0, r1, s0, s1 = P, x, 0, 1
    while r1 > HALF:
        q = r0 // r1
        r0, r1, s0, s1 = r1, r0 - q * r1, s1, s0 - q * s1
    if s1 == 0 or abs(s1) > HALF:
        return None
    return Fraction(r1, s1) if s1 > 0 else Fraction(-r1, -s1)


def primitive(fr):
    den = 1
    for q in fr:
        den = den * q.denominator // math.gcd(den, q.denominator)
    v = [int(q * den) for q in fr]
    g = 0
    for x in v:
        g = math.gcd(g, abs(x))
    v = [x // g for x in v]
    for x in v:
        if x:
            return v if x > 0 else [-y for y in v]
    return v


def exact_frame(K, gens):
    """primitive integer basis of ker(K) over Q; gens = exact integer covectors whose span is K (checked)."""
    B = kernel(K)
    out = []
    for b in B:
        q = [ratrec(x) for x in b]
        assert all(x is not None for x in q), 'rational reconstruction failed'
        out.append(primitive(q))
    for g in gens:
        for b in out:
            assert sum(x * y for x, y in zip(g, b)) == 0, 'reconstructed frame not annihilated exactly'
    if gens:
        S = Span(K.h)
        for g in gens:
            S.insert(g)
        assert len(S) == len(K), 'generator rank differs from frame annihilator'
    return out


def bdefer_x(pr, sl, fr):
    """bitcomp_w.bdefer, also returning the frames (exact generators tracked alongside the mod-p spans)."""
    import types
    gens = {}
    orig_insert, orig_add = Span.insert, Span.add_span
    # track generators: every Span created in bdefer is built from fr.K frames and root covectors
    res = {}
    h, v, R = pr.h, pr.v, sl['R']
    chains, hold = sl['chains'], sl['hold']
    bd = bw.bdefer(pr, sl, fr, log=lambda *a: None)
    return bd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dag'); ap.add_argument('outdir')
    ap.add_argument('--choice', default='AAA'); ap.add_argument('--witness', action='store_true')
    ap.add_argument('--plain-dn', type=int, default=8)
    a = ap.parse_args()
    if a.witness:
        pr, links_s, late_s = bc.load_witness(a.dag)
        lifted_s = {int(k) for k in json.load(gzip.open(a.dag, 'rt'))['j']}
    else:
        pr, links_s, late_s, lifted_s = bc.load_dump(a.dag), None, None, None
    c = a.choice.upper()
    links = links_s if c[0] == 'S' else bw.weighted_links(pr, rounds=2, log=lambda *x: None)
    Kn = bc.node_frames(pr, links)
    lifted = lifted_s if c[2] == 'S' else bw.lifted_set(pr, Kn, links, plain_dn=a.plain_dn)[0]
    fr = bc.Frames(pr, Kn, lifted)
    if os.environ.get('FIXLINKS', '1') == '1':
        links, lifted, Kn, st = bw.fix_plain_links(pr, links, lifted, log=lambda *x: None)
        fr = bc.Frames(pr, Kn, lifted)
        print('fix', st)
    late = late_s if c[1] == 'S' else ({} if c[1] == 'N' else bw.beneficial_late(pr, links, fr))
    export(pr, links, late, lifted, Kn, fr, a.outdir)


def export(pr, links, late, lifted, Kn, fr, outdir):
    h, v = pr.h, pr.v
    sl = bc.compile_slots(pr, links, late)
    R, chains, hold, start = sl['R'], sl['chains'], sl['hold'], sl['start']
    X = bdefer_frames(pr, sl, fr)
    f, placed, vK, vdim, order_of = X['f'], X['placed'], X['vK'], X['vdim'], X['order_of']
    L = bc.place_ops(pr, sl)
    act = pr.act
    lifted = {n for n in lifted if n in set(act) and pr.args[n] is not None}
    # ---------------------------------------------------------------- witness
    W = dict(h=h, seed=0,
             args={str(n): (list(pr.args[n]) if pr.args[n] else None) for n in act},
             leaf={str(n): list(pr.leafT[n]) for n in act if pr.args[n] is None},
             outputs=[[c, list(T), n] for (c, T), n in sorted(pr.outputs.items())],
             retained=[[c, n] for c, n in sorted(pr.retained.items())],
             links=[[x, y, k] for x, (y, k) in sorted(links.items())],
             j={str(n): h for n in sorted(lifted)},
             flag=[[int(i == j) for j in range(h)] for i in range(h)],
             late={str(n): [list(e), list(lt)] for n, (e, lt) in sorted(late.items())},
             claimed={})
    # ---------------------------------------------------------------- deferred word
    vleaf = sorted(s for s in range(R) if pr.args[hold[s][0]] is None)
    ops = [['src', s, hold[s][0]] for s in vleaf]
    i = 0
    while i < len(L):
        o = L[i]
        if o[0] == 'add':
            ops.append(['add', o[1], o[2], o[3]])
            i += 1
        else:
            # one fan per copy: grouping would merge phase-one and later copies of one pivot
            ops.append(['fan', o[1], [o[2]]])
            i += 1
    out = [[s, ch[-2][1], list(ch[-2][2])] for s, ch in enumerate(chains) if ch[-2][0] == 'out']
    ret = [[s, ch[-2][1]] for s, ch in enumerate(chains) if ch[-2][0] == 'ret']
    node_dims = [[n, fr.dim(('n', n))] for n in act]
    late_dims = []
    for n, (e, lt) in sorted(late.items()):
        for k in range(len(lt) - 1):
            late_dims.append([n, list(lt[k:]), fr.dim(('c', n, tuple(lt[k:])))])
    readout = sorted((s for s in range(R) if f[s]), key=lambda s: (f[s], s))
    sigma = [placed[s] for s in readout]
    for s, B in zip(readout, sigma):
        assert len(B) == f[s]
    vstart = [vK[s] for s in vleaf]
    leaves = defaultdict(list)
    for s in vleaf:
        leaves[hold[s][0]].append(s)
    xs_order = []
    for n in sorted(leaves):
        ss = leaves[n]
        early = sorted((s for s in ss if not f[s]), key=lambda s: (vdim[s], order_of[s]))
        dfr = sorted((s for s in ss if f[s]), key=lambda s: (vdim[s], order_of[s]))
        xs_order.append([n, early + dfr])
    dv = sorted((s for s in vleaf if f[s]), key=lambda s: (vdim[s], hold[s][0], order_of[s]))
    D = dict(h=h, R=R, description='bitcomp_w compile exported by export97.py', ops=ops,
             hold=[list(x) for x in hold], start=[list(x) for x in start], out=out, ret=ret, node_dims=node_dims,
             late_dims=late_dims, readout_order=readout, sigma=sigma, vleaf_slots=vleaf, vleaf_start=vstart,
             xs_order=xs_order, deferred_v_order=dv, claimed={})
    # check_lifted's regression pins: R and the undeferred chain-step histogram (V-leaf slots start at <t_S>)
    from collections import Counter as _C
    dimk = {('n', n): d for n, d in node_dims}
    dimk.update({('c', n, tuple(lt)): d for n, lt, d in late_dims})
    rk = _C()
    for s in range(R):
        ds = [0, 1 if pr.args[hold[s][0]] is None else fr.dim(chains[s][1])] + [fr.dim(k) for k in chains[s][2:]]
        assert ds[-1] == h and all(b >= a for a, b in zip(ds, ds[1:]))
        for a_, b_ in zip(ds, ds[1:]):
            if b_ > a_:
                rk[b_ - a_] += 1
    W['claimed'] = dict(R=R, rk={str(r): c for r, c in sorted(rk.items())})
    os.makedirs(outdir, exist_ok=True)
    with gzip.open(os.path.join(outdir, 'witness_%d.json.gz' % h), 'wt') as fo:
        json.dump(W, fo)
    with gzip.open(os.path.join(outdir, 'deferred_%d.json.gz' % h), 'wt') as fo:
        json.dump(D, fo)
    print(json.dumps(dict(h=h, R=R, deferred=len(readout), vleaf=len(vleaf), ops=len(ops), links=len(links),
                          late=len(late), lifted=len(lifted), max_sigma_entry=max((abs(x) for B in sigma for r in B for x in r), default=0),
                          max_vstart_entry=max(abs(x) for B in vstart for r in B for x in r))))


def bdefer_frames(pr, sl, fr):
    """bitcomp_w.bdefer's frames: placed sigma_u and V-leaf starts as exact primitive bases, f, vdim, use order."""
    from collections import defaultdict as dd
    h, v, R = pr.h, pr.v, sl['R']
    chains, hold = sl['chains'], sl['hold']
    bd = bw.bdefer(pr, sl, fr, log=lambda *a: None)
    # recompute the V-leaf starts and placements exactly as bw.bdefer does, keeping the spans
    L = bc.place_ops(pr, sl)
    leaf_slots = dd(list)
    for s in range(R):
        if pr.args[hold[s][0]] is None:
            leaf_slots[hold[s][0]].append(s)
    order_of = {}
    vKs, vdim = {}, {}
    for n, ss in leaf_slots.items():
        ss.sort(key=lambda s: (pr.gpos.get(hold[s][1], 10 ** 9) if len(hold[s]) > 1 else 10 ** 9, s))
        for i, s in enumerate(ss):
            order_of[s] = i
        acc = Span(h)
        for s in reversed(ss):
            acc = acc.copy().add_span(fr.K(chains[s][2]))
            if bw.nondeg(acc):
                vKs[s], vdim[s] = acc, h - len(acc)
            else:
                vKs[s], vdim[s] = None, 1
    assert vdim == bd['vdim'], 'V-leaf start dims differ from bdefer'
    vK = {}
    for s in vKs:
        if vKs[s] is None:
            vK[s] = [pr.tvec[hold[s][0]]]
        else:
            vK[s] = exact_frame(vKs[s], [])
    placed = {}
    f = bd['f']
    PL = bd.get('placedK')
    assert PL is not None, 'patched bdefer needed (placedK)'
    for s, K in PL.items():
        placed[s] = exact_frame(K, [])
        assert len(placed[s]) == f[s]
    return dict(f=f, placed=placed, vK=vK, vdim=vdim, order_of=order_of)


if __name__ == '__main__':
    main()
