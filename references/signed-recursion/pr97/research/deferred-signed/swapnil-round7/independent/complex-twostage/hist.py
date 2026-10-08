"""Residual-rank histogram of the two-stage complex network (m = h^2) on the NStar3 producer with retained totals,
optionally with copied retained centres; every nonzero residual is one whole-residual child (full batching).

Network. Each stage runs v = C(h,3) invocations of the producer's role network on a bank of R auxiliary roles.
Forward invocation (y <- y + x), single-factor frame dims (low 0, high h, label = dim of the node label):
  mix(low) sret(low) inject(low) mix(low,rev) copy(line=1) mix(label) sret(low) inject(t^perp=h-1) mix(high,rev) copy(F=h)
  mix = every addition gate on its role slots; inject = pieces into y[t]; copy = x[t] into its source slot;
  sret = the retained-total scatter into y[S] (reads the h retained roles).
Stage 1: forward per fixed a2, frames L (x) t_a2, dim = d. Stage 2: the inverse (op list and gates reversed, labels
complemented in F) per fixed a1, frames D0 + t_a1 (x) L^perp, dim = m - d; source = Y, target = X.
Endpoints: every auxiliary role 0 -> ... -> m per invocation (arbitrary scratch restored); X: U (dim 1) -> m,
Y: 0 -> m-1; plus one rank-one endpoint-correction child per data pair. Frames are nested along every role
(frames.py, and the explicit simulation), so each edge's rank is the dimension difference.
Copied centres (PR #36 lemma): in the second sret (forward op 6, stage-two op 3) each retained role is read from a
transformed copy; the original moves directly from its previous frame p to its next frame q. The copy is charged
|p - lo| in stage 1 (copy made before the original moves) and |q - lo| in stage 2 (original moves first).
Total rank s = W m - N + 2L, or W m - N + L with copies, W = 2N + 2vR, L = 2v((h-1)^2 + h), N = v^2.
Usage: python3 hist.py 24 copy   (prints the histogram and the sum check)"""
import sys
from collections import Counter
from producer import NStar3, compile_roles

DESIG = 6                    # index of the copied scatter op in the forward op list


def label_dims(c):
    """dim of the frame label of every active node, from supports: 1 for an input; the number of triples when
    they share a common pair; else the number of covered points (see frames.Checker.label)."""
    out = {}
    for n in c.active:
        sp = c.sup[n]; k = bin(sp).count('1')
        if k == 1: out[n] = 1; continue
        common = (1 << c.h) - 1; i = 0
        while sp:
            if sp & 1: common &= sum(1 << p for p in c.triples[i])
            sp >>= 1; i += 1
        out[n] = k if bin(common).count('1') >= 2 else bin(c.cover(n)).count('1')
    return out


def forward_ops(c, kk, dl):
    """list of ops; op = list of (roles, single-factor dim). Roles: ('s', slot), ('x', t), ('y', t)."""
    h = c.h; T = c.triples
    pieces = {t: [] for t in T}
    for i, sl in kk['pout'].items(): pieces[c.pieces[i][0]].append(sl)
    rout = kk['rout']
    def mix(mode, rev=False):
        g = list(reversed(kk['gates'])) if rev else kk['gates']
        return [(tuple(('s', q) for q in set(ins + outs)), {'low': 0, 'high': h}.get(mode, dl.get(n))) for n, ins, outs in g]
    def sret():
        out = []
        for S in T:          # the retained totals that the scatter identity uses for y[S]
            names = [('*',)] + ([('E', i) for i in S] if h - 1 not in S else [('E', i) for i in range(h - 1) if i not in S])
            out.append((tuple([('y', S)] + [('s', rout[nm]) for nm in names]), 0))
        return out
    inject = lambda d: [(tuple([('y', t)] + [('s', q) for q in pieces[t]]), d) for t in T if pieces[t]]
    copy = lambda d: [((('x', t), ('s', sl)), d) for t, sl in kk['src'].items()]
    return [mix('low'), sret(), inject(0), mix('low', True), copy(1), mix('label'), sret(), inject(h - 1),
            mix('high', True), copy(h)]


def build(h, copied):
    c = NStar3(h); kk = compile_roles(c); dl = label_dims(c)
    T = c.triples; v = len(T); m = h * h; N = v * v; R = kk['size']
    f = forward_ops(c, kk, dl)
    r = [[(roles, h - d) for roles, d in reversed(op)] for op in reversed(f)]
    ret = {('s', q) for q in kk['rout'].values()}
    H = Counter(); data = {}
    for stage, ops, lift, desig in ((1, f, lambda d: d, DESIG), (2, r, lambda d: m - h + d, len(f) - 1 - DESIG)):
        cur = {}; dd = {}; pend = set(); done = set(); Hs = Counter()
        for oi, op in enumerate(ops):
            for roles, d in op:
                D = lift(d)
                for ro in roles:
                    if ro[0] in ('x', 'y'): dd.setdefault(ro, []).append(D); continue
                    p = cur.get(ro, 0)
                    if copied and ro in ret and oi == desig:
                        # one copy per retained role serves all of this op's scatter reads
                        if ro not in done:
                            done.add(ro)
                            if stage == 1: Hs[abs(p - D)] += p != D        # copy made at p, original stays at p
                            else: pend.add(ro); lo2 = D                    # copy charged once q is known
                        continue
                    if ro in pend:                                         # stage 2: q = this frame
                        pend.discard(ro); Hs[abs(lo2 - D)] += lo2 != D
                    if p != D: Hs[abs(p - D)] += 1
                    cur[ro] = D
        assert len(cur) == R and not pend
        for ro, p in cur.items(): Hs[m - p] += p != m                      # auxiliary endpoint: full frame
        for k_, n_ in Hs.items(): H[k_] += v * n_                          # dims do not depend on the fixed index
        data[stage] = dd
    # data pairs (a1, a2): X = stage-1 'x' of a1 then stage-2 target ('y') of a2; Y = stage-1 'y' then stage-2 'x'
    p1 = Counter((tuple(data[1].get(('x', t), [])), tuple(data[1].get(('y', t), []))) for t in T)
    p2 = Counter((tuple(data[2].get(('y', t), [])), tuple(data[2].get(('x', t), []))) for t in T)
    for (x1, y1), n1 in p1.items():
        for (x2, y2), n2 in p2.items():
            for sq in ([1, *x1, *x2, m], [0, *y1, *y2, m - 1]):
                for a, b in zip(sq, sq[1:]):
                    if a != b: H[abs(b - a)] += n1 * n2
    H[1] += N                                                              # endpoint correction children
    W = 2 * N + 2 * v * R; L = 2 * v * ((h - 1) ** 2 + h); s = W * m - N + (L if copied else 2 * L)
    tot = sum(k_ * n_ for k_, n_ in H.items())
    return dict(h=h, v=v, m=m, N=N, R=R, W=W, L=L, s=s, hist={k_: n_ for k_, n_ in sorted(H.items()) if n_}, sum=tot, sum_ok=tot == s,
                maxrank=max(H), c=c)


if __name__ == '__main__':
    h = int(sys.argv[1]); copied = len(sys.argv) > 2 and sys.argv[2] == 'copy'
    d = build(h, copied); d.pop('c'); print(d)
