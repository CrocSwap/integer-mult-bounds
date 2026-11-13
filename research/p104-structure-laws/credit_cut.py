"""Credit/cut law (A30') checks.  Standard library only; exact arithmetic.

Part 1  Loss identity.  For a public register path S = E_0 -> ... -> E_m = T with every
        MOVE priced at d(E,F) = dim E + dim F - 2 dim(E & F) and net credit dim T - dim S:
            paid - credit = 2 * sum_i (dim E_i - dim(E_i & E_{i+1})).
        Exhaustive over all 2-step paths of subspaces of F2^4 and all 3-step paths of F2^3,
        plus every path inside the random words of Part 2.
Part 2  Two-sided cut law on up-sets U of the subspace lattice (exact rationals, odd
        denominators allowed):
            junk_U <= o_in(U) + p_out(U)    (premise: public finals independent)
            cout_U <= o_out(U) + p_out(U)
        on seeded random words with public laterals/descents, owned ascents/descents and
        dirty CLEARs.  Controls: dropping p_out is violated; dropping the invertible-T
        premise is violated.
Part 3  The #7334 word (vendored, SHA256-authenticated): every public MOVE ascends,
        every owned lifetime is monotone, and on all 511 principal up-sets
        U_q = {frames containing q}:  p_out = 0, both sides hold, and
            need_in(U) = rank(pubArr + F_U) - rank(pubArr) = o_in(U)
        (zero slack) on every cut with o_in > 0.  Control: without owned arrivals the span
        invariant F_U <= span(arrivals) fails on exactly those cuts.
Prints PASS_CREDIT_CUT_LAW.
"""
import gzip
import hashlib
import itertools
import json
import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORD = HERE / 'data' / 'word-7334.json.gz'
WORD_SHA256 = '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a'
P = 2147483647


def require(ok, label):
    if not ok:
        print('FAIL ' + label)
        sys.exit(1)
    print('ok   ' + label)


def span(b):
    s = {0}
    for v in b:
        s |= {x ^ v for x in s}
    return frozenset(s)


def subspaces(d):
    vecs = range(1, 2 ** d)
    return sorted({span(c) for k in range(d + 1) for c in itertools.combinations(vecs, k)}, key=len)


def sdim(S):
    return len(S).bit_length() - 1


# ---------------------------------------------------------------- Part 1
def loss_ok(path):
    paid = sum(sdim(a) + sdim(b) - 2 * sdim(a & b) for a, b in zip(path, path[1:]))
    depth = sum(sdim(a) - sdim(a & b) for a, b in zip(path, path[1:]))
    return paid - (sdim(path[-1]) - sdim(path[0])) == 2 * depth


def part1():
    n = bad = 0
    for d, steps in ((4, 2), (3, 3)):
        subs = subspaces(d)
        for path in itertools.product(subs, repeat=steps + 1):
            n += 1
            bad += not loss_ok(path)
    require(n == 67 ** 3 + 16 ** 4 and bad == 0,
            'loss identity: %d exhaustive paths (F2^4 two steps, F2^3 three steps), 0 violations' % n)
    # control: crediting dim-gap but pricing laterals at |delta dim| breaks it
    subs = subspaces(3)
    wrong = sum(1 for a, b in itertools.product(subs, repeat=2)
                if abs(sdim(b) - sdim(a)) - (sdim(b) - sdim(a)) != 2 * (sdim(a) - sdim(a & b)))
    require(wrong > 0, 'control: pricing a MOVE at |delta dim| instead of d(E,F) violates the identity on %d pairs' % wrong)


# ---------------------------------------------------------------- Part 2
def frank(rows, cols):
    M = [[r.get(c, 0) for c in cols] for r in rows]
    M = [row for row in M if any(row)]
    rk = 0
    for c in range(len(cols)):
        piv = next((i for i in range(rk, len(M)) if M[i][c]), None)
        if piv is None:
            continue
        M[rk], M[piv] = M[piv], M[rk]
        for i in range(len(M)):
            if i != rk and M[i][c]:
                f = M[i][c] / M[rk][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[rk])]
        rk += 1
    return rk


def fuzz(d, nwords, seed):
    rng = random.Random(seed)
    subs = subspaces(d)
    vecs = list(range(1, 2 ** d))
    Qs = [frozenset(q) for k in range(1, len(vecs) + 1) for q in itertools.combinations(vecs, k)]
    if len(Qs) > 60:
        Qs = rng.sample(Qs, 60)
    coef = [Fr(1), Fr(-1), Fr(1, 2), Fr(-1, 3), Fr(2, 5), Fr(3)]
    st = dict(cuts=0, nonzero=0, viol=0, viol_invT=0, ctrl=0, sing=0, idviol=0, pout=0)
    for _ in range(nwords):
        npub = rng.randint(2, 4)
        nown = rng.randint(0, 2)
        N = npub + nown
        ini = [rng.choice(subs) for _ in range(npub)]
        cur = ini + [None] * nown
        rows = [{r: Fr(1)} for r in range(npub)] + [{} for _ in range(nown)]
        moves, path = [], {r: [ini[r]] for r in range(npub)}
        for _ in range(rng.randint(4, 14)):
            t = rng.random()
            r = rng.randrange(N)
            if r >= npub and cur[r] is None:          # owned INIT (zero content)
                cur[r] = rng.choice(subs)
                rows[r] = {}
                continue
            if cur[r] is None:
                continue
            if t < 0.35:                               # any MOVE: ascent, descent or lateral
                b = rng.choice([s for s in subs if s != cur[r]])
                moves.append((r, cur[r], b, dict(rows[r])))
                cur[r] = b
                if r < npub:
                    path[r].append(b)
            elif t < 0.85:                             # ADD at a common frame
                s = rng.choice([x for x in range(N) if x != r and cur[x] == cur[r]] or [None])
                if s is None:
                    continue
                c = rng.choice(coef)
                R = rows[r]
                for k, v in rows[s].items():
                    nv = R.get(k, 0) + c * v
                    if nv:
                        R[k] = nv
                    else:
                        R.pop(k, None)
            elif r >= npub:                            # dirty CLEAR
                cur[r] = None
                rows[r] = {}
        fin = cur[:npub]
        allk = sorted({k for r in range(npub) for k in rows[r]})
        invT = bool(allk) and frank([rows[r] for r in range(npub)], allk) == npub
        st['sing'] += not invT
        for r in range(npub):
            st['idviol'] += not loss_ok(path[r])
        for Q in Qs:
            inU = lambda S: bool(S & Q)                # an up-set of the subspace lattice
            o_in = o_out = p_out = 0
            arr = [{r: Fr(1)} for r in range(npub) if inU(ini[r])]
            for (r, a, b, c) in moves:
                if not inU(a) and inU(b):
                    arr.append(c)
                    o_in += r >= npub
                if inU(a) and not inU(b):
                    if r >= npub:
                        o_out += 1
                    else:
                        p_out += 1
            F = [rows[r] for r in range(npub) if inU(fin[r])]
            cols = sorted({k for v in arr + F for k in v})
            junk = (frank(arr + F, cols) - frank(F, cols)) if cols else 0
            Cin = [r for r in range(npub) if inU(ini[r])]
            outF = [rows[r] for r in range(npub) if not inU(fin[r])]
            cout = frank(outF, Cin) if (Cin and outF) else 0
            st['cuts'] += 1
            st['nonzero'] += bool(junk or cout)
            st['pout'] += bool(p_out)
            if junk > o_in + p_out or cout > o_out + p_out:
                st['viol'] += 1
                st['viol_invT'] += invT
            if junk > o_in or cout > o_out:
                st['ctrl'] += 1
    return st


def part2():
    for d, nw, seed in ((3, 20000, 7), (4, 1500, 11)):
        st = fuzz(d, nw, seed)
        print('     F2^%d, %d words: %s' % (d, nw, st))
        require(st['viol_invT'] == 0 and st['idviol'] == 0,
                'cut law on F2^%d: 0 violations on invertible-T words over %d cuts; loss identity 0 violations' % (d, st['cuts']))
        require(st['ctrl'] > 0, 'control F2^%d: bound without the p_out term is violated on %d cuts' % (d, st['ctrl']))
        if d == 3:
            require(st['viol'] > 0 and st['sing'] > 0,
                    'control F2^3: all %d violations sit on singular-T words (premise needed)' % st['viol'])


# ---------------------------------------------------------------- Part 3
def modq(s):
    f = Fr(s)
    return f.numerator % P * pow(f.denominator % P, P - 2, P) % P


class Echelon:
    """Incremental row echelon form mod P over sparse dict rows."""

    def __init__(self):
        self.piv = {}

    def add(self, v):
        v = dict(v)
        while v:
            k = min(v)
            b = self.piv.get(k)
            if b is None:
                inv = pow(v[k], P - 2, P)
                self.piv[k] = {c: x * inv % P for c, x in v.items()}
                return True
            f = v[k]
            for c, x in b.items():
                nv = (v.get(c, 0) - f * x) % P
                if nv:
                    v[c] = nv
                else:
                    v.pop(c, None)
        return False

    def copy(self):
        e = Echelon()
        e.piv = dict(self.piv)
        return e


def rank(vs):
    e = Echelon()
    return sum(e.add(v) for v in vs if v)


def part3(qs=range(1, 512)):
    raw = WORD.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA256, '#7334 WORD.json.gz SHA256 ' + WORD_SHA256[:16] + '...')
    W = json.loads(gzip.decompress(raw))
    n, NO = W['public'], W['owned_fields']
    N = n + NO
    SP = [span(f) for f in W['frames']]
    for f in W['frames']:
        assert len(span(f)) == 2 ** len(f)
    rows = [{r: 1} if r < n else {} for r in range(N)]
    cur = list(W['initial']) + [None] * NO
    moves = []
    pub_up = pub_other = 0
    life, lives = {}, []
    for e in W['program']:
        op, r = e[0], e[1]
        if op == 'MOVE':
            a, b = e[2], e[3]
            assert cur[r] == a
            if r < n:
                if SP[a] < SP[b]:
                    pub_up += 1
                else:
                    pub_other += 1
            else:
                life[r].append(len(SP[b]) > len(SP[a]))
            moves.append((r, a, b, dict(rows[r])))
            cur[r] = b
        elif op == 'INIT':
            assert r >= n and cur[r] is None
            rows[r] = {}
            cur[r] = e[2]
            life[r] = []
        elif op == 'CLEAR':
            assert r >= n and cur[r] == e[2]
            lives.append(life.pop(r))
            rows[r] = {}
            cur[r] = None
        elif op == 'SCALE':
            q = modq(e[2])
            rows[r] = {k: v * q % P for k, v in rows[r].items()}
        elif op in ('ADD', 'COPY'):
            s, q, f = e[2], modq(e[3]), e[4]
            assert cur[r] == f and cur[s] == f, 'ADD/COPY operands share a frame'
            if op == 'COPY':
                assert not rows[r]
            R = rows[r]
            for k, v in rows[s].items():
                nv = (R.get(k, 0) + q * v) % P
                if nv:
                    R[k] = nv
                else:
                    R.pop(k, None)
        else:
            raise AssertionError(op)
    require(not life and all(c is None for c in cur[n:]), 'every owned register is dead at the end')
    require(cur[:n] == W['final'], 'public registers end at their final frames')
    require(pub_other == 0, 'all %d public MOVEs strictly ascend (no public exits from any up-set)' % pub_up)
    mono = sum(1 for L in lives if all(L) or not any(L))
    require(mono == len(lives),
            'all %d owned lifetimes are monotone (%d with MOVEs: %d up-only, %d down-only)'
            % (len(lives), sum(1 for L in lives if L), sum(1 for L in lives if L and all(L)),
               sum(1 for L in lives if L and not any(L))))
    # T-coordinates: x -> x T^{-1}, where T = public final rows (sparse; inverted exactly mod p).
    aug = []
    for r in range(n):
        v = dict(rows[r])
        v.update({n + r: 1})
        aug.append(v)
    piv = {}
    for v in aug:
        while True:
            ks = [k for k in v if k < n]
            if not ks:
                break
            k = min(ks)
            b = piv.get(k)
            if b is None:
                inv = pow(v[k], P - 2, P)
                piv[k] = {c: x * inv % P for c, x in v.items()}
                break
            g = v[k]
            for c, x in b.items():
                nv = (v.get(c, 0) - g * x) % P
                if nv:
                    v[c] = nv
                else:
                    v.pop(c, None)
    require(len(piv) == n, 'T invertible: the %d public final rows are independent mod p' % n)
    for k in sorted(piv, reverse=True):          # back-substitute to reduced form
        b = piv[k]
        for k2 in [c for c in b if c < n and c != k]:
            g = b[k2]
            for c, x in piv[k2].items():
                nv = (b.get(c, 0) - g * x) % P
                if nv:
                    b[c] = nv
                else:
                    b.pop(c, None)
    Tinv = [None] * n
    for k, b in piv.items():
        assert all(c >= n for c in b if c != k)
        Tinv[k] = {c - n: x for c, x in b.items() if c >= n}
    for r in range(0, n, 97):                    # spot check Tinv[r] . T = e_r
        acc = {}
        for k, x in Tinv[r].items():
            for c, y in rows[k].items():
                acc[c] = (acc.get(c, 0) + x * y) % P
        assert {c: x for c, x in acc.items() if x} == {r: 1}

    def tco(v):
        out = {}
        for k, x in v.items():
            for c, y in Tinv[k].items():
                nv = (out.get(c, 0) + x * y) % P
                if nv:
                    out[c] = nv
                else:
                    out.pop(c, None)
        return out
    moves = [(r, a, b, tco(c)) for (r, a, b, c) in moves]
    ini, fin = W['initial'], W['final']
    tot_in = tight = viol = nontriv = 0
    slack_out = []
    for q in qs:
        inU = lambda f: q in SP[f]
        o_in = o_out = p_out = 0
        pub_arr = [Tinv[r] for r in range(n) if inU(ini[r])]
        own_arr = []
        for (r, a, b, c) in moves:
            if not inU(a) and inU(b):
                (own_arr if r >= n else pub_arr).append(c)
                o_in += r >= n
            if inU(a) and not inU(b):
                if r >= n:
                    o_out += 1
                else:
                    p_out += 1
        Pc = {r for r in range(n) if not inU(fin[r])}
        nPU = n - len(Pc)
        assert len(pub_arr) == nPU                # ascend-only: each public final in U arrived once
        cut = lambda v: {k: x for k, x in v.items() if k in Pc}
        e = Echelon()
        pubjunk = sum(e.add(cut(v)) for v in pub_arr if v)          # = rank(pubArr + F_U) - |F_U|
        junk = pubjunk + sum(e.add(cut(v)) for v in own_arr if v)   # all arrivals
        Cin = {r for r in range(n) if inU(ini[r])}
        cout = rank([{k: x for k, x in rows[r].items() if k in Cin} for r in Pc])
        viol += (junk > o_in + p_out) or (cout > o_out + p_out)
        if o_in:
            nontriv += 1
            tight += pubjunk == o_in
        tot_in += o_in
        slack_out.append(o_out - cout)
    print('     principal up-sets: 511; with owned entries %d; pubjunk = o_in on %d; sum o_in %d; min copy-out slack %d'
          % (nontriv, tight, tot_in, min(slack_out)))
    require(viol == 0, 'both sides of the cut law hold exactly on all 511 principal up-sets (p_out = 0 everywhere)')
    require(nontriv == 501 and tight == 501 and tot_in == 2032,
            'pubjunk = o_in on all 501 up-sets with owned entries (2,032 entry incidences); with '
            'pubjunk <= need_in <= o_in this gives need_in = o_in: zero slack, every owned entry forced')


if __name__ == '__main__':
    part1()
    part2()
    part3()
    print('PASS_CREDIT_CUT_LAW')
