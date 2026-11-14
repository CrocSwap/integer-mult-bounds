"""halfwall.py -- exact rank-certificate checks for the decoder "half wall" (HALFWALL lane).

Run:  python -I -B halfwall.py      (python 3.12, standard library only, one core)

Scope (honest): these are RANK CERTIFICATES in the row model.  Labels are the odd-weight
vectors of F2^h, Q[x,y] = x.y mod 2 as a 0/1 integer matrix; the DEC(L) row price is the
F2 pairing rank.  A flag F < B (subspaces of F2^h) gives a row type
    D = odd labels in B,  S = odd labels orthogonal to F,  climb = dim B - dim F
(identical (D,S) deduplicated keeping the minimum climb; empty D or S skipped).
A functional split for a subspace A is Z_A = Q o [a.q_t = a.q_s for all a in A]; then
    rank Z_A[D,S] = sum over A-signature blocks P of rank_Q Q[D&P, S&P]
(A = 0 gives Z = Q;  A = F2^h gives Z = I, rank |D&S|).  A mixture pi certifies lambda if
E_pi rank Z[D,S] <= lambda * climb on every flag; then (certificate lemma, lane PROOF.md) C >= n/lambda.
This file re-checks only the finite linear algebra; the certificate lemma itself is not re-proved here.

Checks (each prints an `ok ...` line; any failure exits via SystemExit('FAIL ...')):
  1. Theorem A : h=3 and h=4, Z = Q, over ALL flags: max rank_Q Q[D,S]/climb = 4/3 and 3/2 exactly.
  2. Theorem B': h=5, exact rational S_5-symmetric mixture of functional splits (each orbit enumerated
     explicitly), max over ALL flags of E rank / climb = lambda5 exactly; lambda5 <= 1.86 so C >= n/1.86.
  3. Theorem C : h=6, exact rational S_6-symmetric mixture; E rank <= lambda6 * climb on every flag.
     Flags are enumerated with the top space B restricted to S_6-orbit representatives of subspaces: every
     flag is a coordinate-permutation image of one of those, and the mixture is S_6-invariant (full orbits
     averaged), so this covers all flags.  The number of distinct closures over ALL flags is also
     recomputed and compared with the lane figure 82,537.  Then the integrality corollary for distinct
     labels n <= 32: lambda6 < 2n/(n-1) (odd n) and < 2n/(n-2) (even n >= 4), so C >= ceil(n/2).
  4. Full-flag obstruction at h=7: over all 29,212 subspaces A of F2^7, sum over blocks of
     rank Q[block,block] on the full flag (D = S = all 64 odd labels, climb 7) is >= 15.  The sum is invariant
     under coordinate permutations, so S_7-orbit representatives are evaluated and orbit sizes are checked to
     total 29,212.  Ranks mod a prime are lower bounds of rational ranks, which is the direction needed.
     Hence every functional-split mixture has lambda7 >= 15/7 > 2.0317, and (restriction monotonicity,
     lane PROOF Prop D, quoted not re-proved) lambda9 >= 15/7 > 2*255/254.  15 is attained (exact control).
Each theorem also has a biting control (a slightly smaller lambda, or a perturbed mixture, is refuted).

Exactness of rational ranks: for 0/1 matrices with <= 32 rows and columns, Hadamard gives |minor| <= 32^16 = 2^80
< p = 2^89 - 1.  rank mod p <= rank_Q, and all (r+1)-minors vanish mod p (r = rank mod p) and are smaller than
p in absolute value, so they vanish: rank_Q = rank mod p.  Larger matrices (the h=7 exactness control) use
p = 2^521 - 1 > 64^32 (Hadamard bound for 64x64).
"""
import itertools
import time
from fractions import Fraction as Fr

T0 = time.time()
P89 = (1 << 89) - 1
P521 = (1 << 521) - 1
P61 = (1 << 61) - 1


def fail(msg):
    raise SystemExit('FAIL ' + msg)


def log(*a):
    print('   [%5.1fs]' % (time.time() - T0), *a, flush=True)


def rank_mod(rows, p):
    rows = [r[:] for r in rows]
    m = len(rows)
    if m == 0:
        return 0
    ncols = len(rows[0])
    r = 0
    for c in range(ncols):
        piv = -1
        for i in range(r, m):
            if rows[i][c]:
                piv = i
                break
        if piv < 0:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        pr = rows[r]
        a = pr[c]
        for i in range(r + 1, m):
            f = rows[i][c]
            if f:
                rows[i] = [(x * a - f * y) % p for x, y in zip(rows[i], pr)]
        r += 1
        if r == m:
            break
    return r


class Ctx:
    """Tables for F2^h: subspaces as RREF bases, masks over x in [0,2^h), odd labels, block-rank cache."""

    def __init__(self, h):
        self.h = h
        self.N = 1 << h
        self.par = [bin(x).count('1') & 1 for x in range(self.N)]
        self.odd = [x for x in range(self.N) if self.par[x]]
        self.ODD = sum(1 << x for x in self.odd)
        self.cache = {}
        self.gens = [self._permtab([1, 0] + list(range(2, h))),
                     self._permtab(list(range(1, h)) + [0])]   # generators of S_h on coordinates
        self._subs = None

    def _permtab(self, p):
        return [sum(((x >> i) & 1) << p[i] for i in range(self.h)) for x in range(self.N)]

    @staticmethod
    def rref(vs):
        basis = []
        for v in vs:
            for b in basis:
                v = min(v, v ^ b)
            if v:
                basis.append(v)
        for i in range(len(basis)):
            for j in range(len(basis)):
                if i != j:
                    basis[j] = min(basis[j], basis[j] ^ basis[i])
        basis.sort(reverse=True)
        return tuple(basis)

    def all_subspaces(self):
        """Every subspace of F2^h exactly once, as RREF basis tuples (pivot = highest bit)."""
        if self._subs is not None:
            return self._subs
        h = self.h
        out = []
        for k in range(h + 1):
            for piv in itertools.combinations(range(h), k):
                pset = set(piv)
                slots = [(i, c) for i in range(k) for c in range(piv[i]) if c not in pset]
                for bits in range(1 << len(slots)):
                    rows = [1 << piv[i] for i in range(k)]
                    for t, (i, c) in enumerate(slots):
                        if (bits >> t) & 1:
                            rows[i] |= 1 << c
                    out.append(tuple(sorted(rows, reverse=True)))
        self._subs = out
        return out

    @staticmethod
    def span_elems(basis):
        el = [0]
        for b in basis:
            el = el + [x ^ b for x in el]
        return el

    def perp_mask(self, basis):
        m = 0
        for x in range(self.N):
            if all(not self.par[x & b] for b in basis):
                m |= 1 << x
        return m

    def orbit(self, basis):
        """S_h-orbit (set of RREF tuples) of the subspace spanned by `basis`."""
        start = self.rref(basis)
        seen = {start}
        stack = [start]
        while stack:
            s = stack.pop()
            for g in self.gens:
                t = self.rref([g[b] for b in s])
                if t not in seen:
                    seen.add(t)
                    stack.append(t)
        return seen

    def orbit_reps(self, bases):
        seen = set()
        reps = []
        sizes = 0
        for b in bases:
            if b in seen:
                continue
            o = self.orbit(b)
            reps.append(b)
            seen |= o
            sizes += len(o)
        return reps, sizes

    @staticmethod
    def labels_of(mask):
        out = []
        while mask:
            low = mask & -mask
            out.append(low.bit_length() - 1)
            mask ^= low
        return out

    def qrank(self, Dm, Sm):
        """Exact rank over Q of Q[Dm,Sm] (<= 32x32, certificate in module docstring)."""
        key = (Dm, Sm) if Dm <= Sm else (Sm, Dm)   # Q symmetric
        v = self.cache.get(key)
        if v is None:
            dl, sl = self.labels_of(key[0]), self.labels_of(key[1])
            if len(dl) > 32 or len(sl) > 32:
                fail('internal: block too large for the P89 exactness argument')
            par = self.par
            v = rank_mod([[par[d & s] for s in sl] for d in dl], P89)
            self.cache[key] = v
        return v

    def sig_blocks(self, basis):
        """Masks of the A-signature blocks (x ~ y iff a.x = a.y for all a in A) of the odd labels."""
        d = {}
        for x in self.odd:
            s = 0
            for j, a in enumerate(basis):
                s |= self.par[x & a] << j
            d[s] = d.get(s, 0) | (1 << x)
        return list(d.values())

    def split_rank(self, blocks, Dm, Sm):
        t = 0
        for P in blocks:
            dm = Dm & P
            if dm:
                sm = Sm & P
                if sm:
                    t += self.qrank(dm, sm)
        return t

    def flags(self, Bbases=None):
        """dict (D,S) -> min climb over all flags F < B with B in Bbases (default: all subspaces)."""
        info = []
        for b in self.all_subspaces():
            m = 0
            for x in self.span_elems(b):
                m |= 1 << x
            info.append((b, len(b), m))
        pm = {}
        want = None if Bbases is None else set(Bbases)
        res = {}
        for (bb, kb, bm) in info:
            if want is not None and bb not in want:
                continue
            D = bm & self.ODD
            if not D:
                continue
            for (fb, kf, fm) in info:
                if kf >= kb or (fm & ~bm):
                    continue
                S = pm.get(fb)
                if S is None:
                    S = pm[fb] = self.perp_mask(fb) & self.ODD
                if not S:
                    continue
                c = kb - kf
                k = (D, S)
                if k not in res or res[k] > c:
                    res[k] = c
        return res


def columns(ctx, cert):
    """cert = [(weight, basis | 'I')]; returns list of per-column orbit signature-block lists."""
    cols = []
    for w, basis in cert:
        if basis == 'I':
            cols.append(None)
        else:
            cols.append([ctx.sig_blocks(a) for a in sorted(ctx.orbit(basis))])
    return cols


def column_values(ctx, cols, flags):
    """For every flag, the exact orbit-averaged expected rank of each column (a Fraction)."""
    table = []
    for (D, S), c in flags.items():
        vals = []
        for col in cols:
            if col is None:
                vals.append(Fr(bin(D & S).count('1')))
            else:
                vals.append(Fr(sum(ctx.split_rank(b, D, S) for b in col), len(col)))
        table.append((vals, c, D, S))
    return table


def worst_ratio(table, weights):
    worst, arg = Fr(0), None
    for vals, c, D, S in table:
        r = sum(w * v for w, v in zip(weights, vals)) / c
        if r > worst:
            worst, arg = r, (D, S, c)
    return worst, arg


# --- exact rational mixtures (weights spread uniformly over the S_h-orbit of the representative A) -------------
# (weight, basis of representative A as bitmask integers; [] = A = 0, i.e. Z = Q; 'I' = Z = I).
# Weights: lane LP optimum (HALFWALL t_symlp2.py), rationalised with limit_denominator(1e6), renormalised to 1.
CERT5 = [
    (Fr(40, 569), []),            # Z = Q
    (Fr(158, 569), [29]),         # hyperplane split, a of weight 4 (orbit of 5)
    (Fr(316, 569), [18]),         # hyperplane split, a of weight 2 (orbit of 10)
    (Fr(55, 569), [9, 16]),       # dim-2 split (orbit of 30)
]
LAM5 = Fr(5291, 2845)             # = 1.859753954...
CERT6 = [
    (Fr(42, 697), []),            # Z = Q
    (Fr(30, 41), [46]),           # dim-1 split, a of weight 4 (orbit of 15)
    (Fr(145, 697), [23, 43]),     # dim-2 split (orbit of 15)
]
LAM6 = Fr(1395, 697)              # = 2.001434720...


def check_mixture(h, cert, lam, theorem, reps_only):
    ctx = Ctx(h)
    if sum(w for w, _ in cert) != 1:
        fail('%s weights do not sum to 1' % theorem)
    subs = ctx.all_subspaces()
    if reps_only:
        reps, tot = ctx.orbit_reps(subs)
        if tot != len(subs):
            fail('orbit sizes do not total the number of subspaces')
        flags = ctx.flags(reps)
        log('%s: %d subspaces, %d S_%d-orbit reps for B, %d distinct flag closures from them'
            % (theorem, len(subs), len(reps), h, len(flags)))
    else:
        flags = ctx.flags()
        log('%s: %d subspaces, %d distinct flag closures (all flags)' % (theorem, len(subs), len(flags)))
    cols = columns(ctx, cert)
    log('%s: column orbit sizes' % theorem, [1 if c is None else len(c) for c in cols])
    table = column_values(ctx, cols, flags)
    ws = [w for w, _ in cert]
    worst, arg = worst_ratio(table, ws)
    log('%s: max E rank/climb = %s = %.12f' % (theorem, worst, float(worst)))
    if worst != lam:
        fail('%s max ratio %s != stated %s' % (theorem, worst, lam))
    # biting controls
    claim = lam - Fr(1, 1000)
    if not worst > claim:
        fail('%s control: lambda-1/1000 not refuted' % theorem)
    # drop the heaviest column and renormalise: some flag must exceed lam
    j = max(range(len(ws)), key=lambda i: ws[i])
    w2 = [0 if i == j else w for i, w in enumerate(ws)]
    t = sum(w2)
    w2 = [w / t for w in w2]
    worse, _ = worst_ratio(table, w2)
    if not worse > lam:
        fail('%s control: perturbed mixture (heaviest column dropped) still meets lambda' % theorem)
    log('%s: controls: lambda-1/1000 refuted by a flag; dropping the heaviest column gives %.6f > lambda'
        % (theorem, float(worse)))
    return ctx, flags


def main():
    # ------------------------------------------------------------------ 1. Theorem A
    for h, want in ((3, Fr(4, 3)), (4, Fr(3, 2))):
        ctx = Ctx(h)
        flags = ctx.flags()
        table = column_values(ctx, [[ctx.sig_blocks(())]], flags)   # A = 0: one block = all odd labels, Z = Q
        worst, arg = worst_ratio(table, [Fr(1)])
        if worst != want:
            fail('Theorem A h=%d: max ratio %s != %s' % (h, worst, want))
        if not worst > want - Fr(1, 1000):
            fail('Theorem A h=%d control' % h)
        if h == 4 and len(flags) != 353:
            fail('Theorem A h=4: closure count %d != 353' % len(flags))
        print('ok Theorem A h=%d: %d flag closures, max rank_Q Q[D,S]/climb = %s exactly (claim %s refuted by a '
              'flag with D,S sizes %d,%d climb %d); C >= n/(%s)'
              % (h, len(flags), worst, want - Fr(1, 1000),
                 bin(arg[0]).count('1'), bin(arg[1]).count('1'), arg[2], want))
        log('Theorem A h=%d done' % h)

    # ------------------------------------------------------------------ 2. Theorem B' (h = 5)
    ctx5, flags5 = check_mixture(5, CERT5, LAM5, "Theorem B'", reps_only=False)
    if len(flags5) != 4503:
        fail("Theorem B': closure count %d != 4503" % len(flags5))
    if not LAM5 <= Fr(186, 100):
        fail("Theorem B': lambda5 > 1.86")
    print("ok Theorem B' h=5: S_5-symmetric mixture over all %d flag closures, lambda5 = %s = %.9f <= 1.86; "
          "C >= n/lambda5 = %.6f n > 0.537 n" % (len(flags5), LAM5, float(LAM5), float(1 / LAM5)))

    # ------------------------------------------------------------------ 3. Theorem C (h = 6)
    ctx6, flags6 = check_mixture(6, CERT6, LAM6, 'Theorem C', reps_only=True)
    full6 = ctx6.flags()
    if len(full6) != 82537:
        fail('Theorem C: total closure count %d != 82537' % len(full6))
    print('ok Theorem C h=6: E rank <= lambda6 * climb on every flag (%d orbit-rep flags covering all %d closures), '
          'lambda6 = %s = %.12f' % (len(flags6), len(full6), LAM6, float(LAM6)))
    for n in range(3, 33):
        if n % 2:
            thr = Fr(2 * n, n - 1)
        else:
            if n < 4:
                continue
            thr = Fr(2 * n, n - 2)
        if not LAM6 < thr:
            fail('integrality: lambda6 >= %s at n=%d' % (thr, n))
    # n <= 2 is trivial (C >= 1 = ceil(n/2) for n = 1, 2 since any decoder needs a row)
    print('ok Theorem C integrality: for every n in 3..32 (odd n: lambda6 < 2n/(n-1); even n >= 4: lambda6 < 2n/(n-2); '
          'min threshold %.6f) C >= ceil(n/2); distinct labels at h=6 give n <= 32'
          % float(min(Fr(2 * n, n - 1) if n % 2 else Fr(2 * n, n - 2) for n in range(3, 33) if n % 2 or n >= 4)))
    log('Theorem C done')

    # ------------------------------------------------------------------ 4. full-flag obstruction at h = 7
    ctx7 = Ctx(7)
    subs = ctx7.all_subspaces()
    if len(subs) != 29212:
        fail('h=7 subspace count %d != 29212' % len(subs))
    reps, tot = ctx7.orbit_reps(subs)
    if tot != 29212:
        fail('h=7 orbit sizes total %d != 29212' % tot)
    log('h=7: 29212 subspaces, %d S_7-orbit reps' % len(reps))
    odd = ctx7.odd
    par = ctx7.par

    def fullflag_sum(basis, p):
        t = 0
        for P in ctx7.sig_blocks(basis):
            ls = ctx7.labels_of(P)
            t += rank_mod([[par[a & b] for b in ls] for a in ls], p)
        return t

    best = {}
    for b in reps:
        v = fullflag_sum(b, P61)
        k = len(b)
        if k not in best or v < best[k][0]:
            best[k] = (v, b)
    mn = min(v for v, _ in best.values())
    if mn < 15:
        fail('h=7 full flag: min rank sum %d < 15' % mn)
    # exact control: an A attaining the minimum, exact rank over Q via p = 2^521-1 (>= Hadamard bound for 64x64)
    v, b = min(best.values(), key=lambda t: t[0])
    vex = fullflag_sum(b, P521)
    if vex != 15 or v != 15:
        fail('h=7 control: expected exactly 15, got mod-p %d exact %d' % (v, vex))
    # biting control: the claim "min >= 16" is refuted by that A
    if not vex < 16:
        fail('h=7 control')
    print('ok full flag h=7: min over all 29212 subspaces A of sum_blocks rank Q = %d (by dim A: %s); attained exactly '
          'by A = span%s with exact rational rank sum %d (so the bound 15 cannot be improved); '
          'lambda7 >= 15/7 = %.4f > 2.0317 and lambda9 >= 15/7 > 2*255/254 = %.4f for functional-split mixtures'
          % (mn, {k: best[k][0] for k in sorted(best)}, list(b), vex, 15 / 7, 2 * 255 / 254))
    if not Fr(15, 7) > Fr(2 * 255, 254) or not Fr(15, 7) > Fr(2032, 1000):
        fail('15/7 threshold comparison')

    print('checks done: 1 (Theorem A h=3,4), 2 (Theorem B h=5), 3 (Theorem C h=6 + integrality), 4 (h=7 full flag)')
    print('PASS_DECODER_HALFWALL')


if __name__ == '__main__':
    main()
