"""SEPPAYS gen3.py (own code): random SEPARATION gadgets (pinned, GTD).  Per gadget, helper H (token + whatever it holds):
  carriers k_i: INIT at a sub-chart of H, copy H's snapshot (k_i += c_i H), climb (paid);
  H absorbs Y's at cold charts (Y climbs inside q^perp first), climbs free;
  root m: INIT at chart(H), reads H (lam) and the carriers (token cancels: sum c_i-weights = lam), so m = lam*(H now - snapshot);
  m writes back H -= m/lam (H returns to the snapshot), climbs (paid) to cover target labels, delivers into X_t's, CLEAR.
variant 'tree'  : one root, carriers read only by it              (inside class CT)
variant 'shared': two roots split the read of H and share a carrier  (outside CT: carrier read twice)
variant 'pub'   : the snapshot is carried by a second helper G (public, free climb) whose own token is cancelled by an
                  owned copy of G's token taken at G's start chart                   (outside CT: public carrier)"""
import random
from fractions import Fraction as Fr
from eng import *
from gen import rand_up

def gen3(n, P, F, rng, nh=2, ngad=3, variant='tree', lams=None):
    T = len(P); ALL = frozenset(range(1 << n))
    if lams is None: lams = [1] if F.p == 2 else [1, -1, Fr(1, 2), 2, Fr(-1, 2)]
    qperp = [perp([q], n) for q in P]
    meta = dict(nh=nh + (1 if variant == 'pub' else 0), Xch=[span([q]) for q in P], Ych=[frozenset([0])] * T,
                Hch=[frozenset([0])] * (nh + (1 if variant == 'pub' else 0)))
    R = Run(n, P, F, **meta); cnt = [0]
    def new(C):
        r = ('O', cnt[0]); cnt[0] += 1; R.INIT(r, C); return r
    def up(r, within=ALL, k=1):
        for _ in range(k):
            D = rand_up(R.reg[r][0], n, within, rng)
            if D != R.reg[r][0]: R.MOVE(r, D)
    def sub(C):
        S = subspaces_containing(frozenset([0]), n, C); return rng.choice(S)
    for g in range(ngad):
        H = ('H', rng.randrange(nh)); C0 = R.reg[H][0]
        if variant == 'pub':
            G = ('H', nh)
            if not R.reg[G][0] <= C0: continue
        # snapshot carriers
        lam = F.c(rng.choice(lams)); ks = []
        if variant in ('tree', 'shared'):
            parts = [lam] if rng.random() < 0.6 or F.p == 2 else [lam * Fr(1, 2), lam * Fr(1, 2)]
            for c in parts:
                k = new(sub(C0)); R.ADD(k, c, H); ks.append(k)
        else:   # public carrier G copies H's snapshot at C0 (G must sit <= C0); owned kt copies G's token now
            kt = new(R.reg[G][0]); R.ADD(kt, 1, G)            # kt = G's current content (token + old stuff)
            R.MOVE(G, C0) if R.reg[G][0] != C0 else None
            R.ADD(G, lam, H)                                   # G = g + lam*H(snapshot)
        # H absorbs Y's at cold charts, climbs
        for _ in range(rng.choice([1, 2, 3])):
            if rng.random() < 0.5: up(H)
            s = rng.randrange(T); Y = ('Y', s)
            if R.reg[H][0] <= qperp[s]:
                if not R.reg[H][0] <= R.reg[Y][0]:
                    D = span(list(R.reg[Y][0] | R.reg[H][0]))
                    if D <= qperp[s]: R.MOVE(Y, D)
                if R.reg[H][0] <= R.reg[Y][0]: R.ADD(H, rng.choice(lams), Y)
        up(H, k=rng.choice([0, 1, 2]))
        C = R.reg[H][0]
        roots = [new(C)] + ([new(C)] if variant == 'shared' else [])
        split = [F.c(1)] if len(roots) == 1 else ([F.c(1), F.c(0)] if F.p == 2 else [Fr(1, 2), Fr(1, 2)])
        if variant in ('tree', 'shared'):
            for k in ks:
                D = span(list(R.reg[k][0] | C))
                if D != R.reg[k][0]: R.MOVE(k, D)
            for m, f in zip(roots, split):
                if f == 0: continue
                R.ADD(m, f * lam, H)
                for k in ks: R.ADD(m, -f, k)
        else:
            if not C <= R.reg[G][0]: R.MOVE(G, span(list(R.reg[G][0] | C)))
            # G climbed free; kt carries G's pre-copy content up (paid)
            D = span(list(R.reg[kt][0] | R.reg[G][0])); R.MOVE(kt, D)
            for m, f in zip(roots, split):
                R.ADD(m, lam, H); R.ADD(m, -1, G); R.ADD(m, 1, kt)   # lam H(now) - (G_now - G_old) = lam (H now - snapshot)
                # restore G: G -= lam*H(snapshot) needs snapshot; use m: G += m - lam*H(now) ... do it via the owned path:
        # write back and deliver
        for m in roots:
            if R.reg[m][1]:
                inv = F.c(1) / lam if F.p == 0 else F.c(1)
                R.ADD(H, -inv, m)
        if variant == 'pub':
            # G must return to its old content: G_now = old + lam*snap.  lam*snap = lam*H(restored H = snapshot).
            if not R.reg[G][0] <= R.reg[H][0]: R.MOVE(H, span(list(R.reg[H][0] | R.reg[G][0])))
            R.ADD(G, -lam, H)
            R.CLEAR(kt)
        for m in roots:
            up(m, k=rng.choice([0, 1, 2]))
            ts = [t for t in range(T) if R.reg[('X', t)][0] <= R.reg[m][0]]
            for t in rng.sample(ts, min(len(ts), rng.choice([1, 2, 3]))):
                R.ADD(('X', t), rng.choice(lams), m)
            R.CLEAR(m)
        for k in ks: R.CLEAR(k)
    return R, meta
