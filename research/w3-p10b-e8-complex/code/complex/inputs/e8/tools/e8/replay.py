#!/usr/bin/python3 -I
"""usage: python3 -I -B replay.py <certificate.json[.gz]> [e8] [json] [seed=<n>] [noparts] [norandom]

replay.py: a STAND-ALONE replay of a certificate of format gcert/1.
Python 3.9 standard library only.  It imports nothing of the published tools and nothing of the E8 harness, and it
reads only the certificate file.  Every rule below cites the line of the published code it was read from
(REL = this repository at its third revision; gx = REL/tools/gx/gx.py, core = REL/tools/gx/gxcore.py, unit = REL/tools/gx/gxunit.py,
rate = REL/tools/gx/gxrate.py, fold = REL/tools/gen/foldlib.py, logs = REL/tools/gen/gen_rates.py,
gsm = REL/tools/gx/gsmirror.py, Lean = REL/Work/GCert).

  e8        also require h = 9, v = 120 and ports = exactly the 120 bit vectors of length 9 of weight 3 or 7
  json      print one last line `JSON {...}` with the key numbers
  seed=<n>  seed of the two random-value runs (default: fresh values from the system)
  noparts   skip section 9 (the replay with separate positive and negative parts, the slowest part)
  norandom  skip the two random-value runs

Exit code: 0 accepted on every count; 1 REFUSED by a rule of the two published checkers (or the file is malformed,
or the program could not decide); 3 accepted by those rules but a Lean-facing extra test failed; 2 usage.
What is NOT checked: see README.md of this folder.

Control: figure 7474547 on tools/certificate/gcert1-p11-pr193.json.gz (about 40 s, 550 MB).
"""
import sys
import json
import gzip
import hashlib
import os
import random
import time
from collections import Counter
from fractions import Fraction as Q
from math import gcd


class Refuse(Exception):
    def __init__(self, rule, msg):
        Exception.__init__(self, "%s: %s" % (rule, msg))
        self.rule = rule


def need(cond, rule, msg):
    if not cond:
        raise Refuse(rule, msg)


def isint(x):
    return type(x) is int


def islist(x):
    return type(x) is list


def wt(x):
    return bin(x).count("1")


# =====================================================================================================================
# 0. the file
# =====================================================================================================================
def load(path):
    raw = open(path, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)

    def nodup(pairs):
        d = {}
        for k, val in pairs:
            need(k not in d, "F0", "the key %r occurs twice in one JSON object" % (k,))
            d[k] = val
        return d

    def noconst(s):
        raise Refuse("F0", "a number that is not finite (%s)" % s)
    try:
        c = json.loads(raw.decode("utf-8"), object_pairs_hook=nodup, parse_constant=noconst)
    except ValueError as e:
        raise Refuse("F0", "not JSON: %s" % e)
    return c, sha


# =====================================================================================================================
# 1. subspaces of F_2^h (own code: elimination by leading bit; for h <= 12 also the full list of elements)
# =====================================================================================================================
def canon(vectors):
    """the subspace spanned by the bit vectors, as its unique reduced basis, leading bits descending"""
    piv = {}
    for u in vectors:
        while u:
            p = u.bit_length() - 1
            if p in piv:
                u ^= piv[p]
            else:
                piv[p] = u
                break
    order = sorted(piv, reverse=True)
    for p in sorted(piv):                      # clear every leading bit from the vectors above it
        for q in order:
            if q > p and piv[q] >> p & 1:
                piv[q] ^= piv[p]
    return tuple(piv[p] for p in order)


def in_span(u, piv):
    while u:
        p = u.bit_length() - 1
        if p not in piv:
            return False
        u ^= piv[p]
    return True


def elements(basis):
    """bit set (one Python integer, bit e set if e is in the span)"""
    els = [0]
    for b in basis:
        els += [e ^ b for e in els]
    m = 0
    for e in els:
        m |= 1 << e
    return m


# =====================================================================================================================
# 2. outward-rounded fixed-point arithmetic for the figure (own code; an integer n stands for n / 2^P)
# =====================================================================================================================
def cdiv(a, b):
    return -((-a) // b)


class Undecided(Exception):
    pass


class Fix:
    def __init__(self, P):
        self.P, self.S = P, 1 << P
        lo, hi = self.atanh(1, 3)
        self.ln2 = (2 * lo, 2 * hi)            # ln 2 = 2 atanh(1/3)
        self.cache = {}

    def atanh(self, a, b):
        """bounds of atanh(a/b) = sum_k (a/b)^(2k+1) / (2k+1) for integers 0 <= a, 0 < b, 3a <= b"""
        assert 0 <= a and 0 < b and 3 * a <= b
        if a == 0:
            return 0, 0
        lo = hi = 0
        pl, ph = (a * self.S) // b, cdiv(a * self.S, b)
        a2, b2 = a * a, b * b
        K = self.P // 3 + 4                     # (1/9)^K < 2^-P
        for k in range(K):
            lo += pl // (2 * k + 1)
            hi += cdiv(ph, 2 * k + 1)
            pl, ph = (pl * a2) // b2, cdiv(ph * a2, b2)
        hi += cdiv(ph * 9, 8)                   # the tail: at most y^(2K+1) / (1 - y^2), and 1 / (1 - y^2) <= 9/8
        return lo, hi

    def ln(self, n):
        """bounds of ln n for an integer n >= 1: n = 2^k q, 1 <= q < 2, ln q = 2 atanh((q-1)/(q+1))"""
        if n not in self.cache:
            k = n.bit_length() - 1
            lo, hi = self.atanh(n - (1 << k), n + (1 << k))
            self.cache[n] = (k * self.ln2[0] + 2 * lo, k * self.ln2[1] + 2 * hi)
        return self.cache[n]

    def ln_ratio(self, m, r):
        (a, b), (c, d) = self.ln(m), self.ln(r)
        return a - d, b - c

    def exp_lo(self, x):
        """a lower bound of e^x for x >= 0 (x a lower bound of the argument)"""
        assert x >= 0
        tot, term, k = 0, self.S, 0
        while term > 0:
            tot += term
            k += 1
            term = (term * x) // (self.S * k)
        return tot

    def exp_up(self, x):
        """an upper bound of e^x for x >= 0 (x an upper bound of the argument)"""
        assert x >= 0
        tot, term, k = 0, self.S, 0
        while True:
            tot += term
            k += 1
            term = cdiv(term * x, self.S * k)   # an upper bound of x^k / k!
            if term <= 1 and (k + 1) * self.S >= 2 * x:
                break
        return tot + 2 * term + 1               # the tail from k on is at most twice its first term


def block_holds(F, U, A, B, sbits):
    """the whole-block inequality of fold:8,  (t-1) M(z) + W ((m-1)/m)^z + W (1/m)^z < t W,  z = 1 - A/10^B, t = 2^sbits,
    M(z) = sum over the block list of count * (rank/m)^z.   True = proved, False = proved false, None = undecided."""
    t, m, W, den = 1 << sbits, U["m"], U["W"], 10 ** B

    def term(r, n):                             # bounds of n (r/m)^z = n (r/m) exp((A/10^B) ln(m/r))
        l, u = F.ln_ratio(m, r)
        return (n * r * F.exp_lo((A * l) // den)) // m, cdiv(n * r * F.exp_up(cdiv(A * u, den)), m)
    lo = hi = 0
    for r, n in U["H"].items():
        a, b = term(r, n)
        lo, hi = lo + a, hi + b
    (a1, b1), (a2, b2) = term(m - 1, 1), term(1, 1)
    L, Hh, rhs = (t - 1) * lo + W * (a1 + a2), (t - 1) * hi + W * (b1 + b2), t * W * F.S
    return True if Hh < rhs else False if L >= rhs else None


def rank_holds(F, U, A, B, sbits):
    """the per-rank inequality of fold:10,  t W (m - m^z) < (t-1) D"""
    t, m, W, D, den = 1 << sbits, U["m"], U["W"], U["D"], 10 ** B
    l, u = F.ln_ratio(m, 1)
    e_lo, e_up = F.exp_lo((A * l) // den), F.exp_up(cdiv(A * u, den))
    one_minus_lo, one_minus_up = F.S - cdiv(F.S * F.S, e_lo), F.S - (F.S * F.S) // e_up      # 1 - e^-x
    L, Hh, rhs = t * W * m * one_minus_lo, t * W * m * one_minus_up, (t - 1) * D * F.S
    return True if Hh < rhs else False if L >= rhs else None


def last_true(f, top):
    """the largest A in [0, top) with f(A), for a monotone f (bisection as in fold:59-67)"""
    r0 = f(0)
    if r0 is None:
        raise Undecided()
    if not r0:
        return None
    lo, hi = 0, top
    while hi - lo > 1:
        mid = (lo + hi) // 2
        r = f(mid)
        if r is None:
            raise Undecided()
        if r:
            lo = mid
        else:
            hi = mid
    return lo


def log_upper(F, m, r, Dd=12):
    """the rational bound of the tools (logs:13-15): (ceiling of ln(m/r) 10^Dd, plus one) / 10^Dd"""
    l, u = F.ln_ratio(m, r)
    a, b = cdiv(l * 10 ** Dd, F.S), cdiv(u * 10 ** Dd, F.S)
    if a != b:
        raise Undecided()
    return Q(a + 1, 10 ** Dd)


def block_cert(U, Ls, A, B, sbits):
    """the exact rational certificate of the tools (fold:86-111): every (r/m)^z is bounded by
    (r/m)(1 + x + x^2/2 + (2/9) x^3), x = (A/10^B) L_r <= 1.  Returns the margin (a fraction; > 0 = certificate) or
    None when some x > 1 (the tool stops there)."""
    eps, t, m, W, H = Q(A, 10 ** B), 1 << sbits, U["m"], U["W"], U["H"]
    vals = []
    for r, n in [(r, H[r]) for r in sorted(H)] + [(m - 1, 1), (1, 1)]:
        x = eps * Ls[r]
        if x > 1:
            return None
        vals.append(n * Q(r, m) * (1 + x + x * x / 2 + x ** 3 * Q(2, 9)))
    nH = len(H)
    margin = t * W - ((t - 1) * sum(vals[:nH]) + W * (vals[nH] + vals[nH + 1]))
    if margin > 0:                              # the rounding step of fold:104-110, repeated as a test
        G = 0
        while Q((t - 1) * nH + 2 * W, 10 ** G) > margin / 50:
            G += 1
        up = [Q(cdiv((x * 10 ** G).numerator, (x * 10 ** G).denominator), 10 ** G) for x in vals]
        if not (t - 1) * sum(up[:nH]) + W * (up[nH] + up[nH + 1]) < t * W:
            return Q(0)
    return margin


def rank_cert(U, L1, A, B, sbits):
    """fold:136-146: t W m (x - x^2/2 + x^3/4) < (t-1) D with x = (A/10^B) L, L >= ln m, x <= 1"""
    t, m, W, D = 1 << sbits, U["m"], U["W"], U["D"]
    x = Q(A, 10 ** B) * L1
    return x <= 1 and t * W * m * (x - x * x / 2 + x ** 3 / 4) < (t - 1) * D


def figures(U, B, sbits):
    """(largest A with the tools' rational certificate, largest A for which the inequality is true), whole-block
    and per-rank.  unit:39-47 and rate:26-32: start at the largest true A and step down until the certificate exists."""
    P = 256
    while True:
        try:
            F = Fix(P)
            top = 10 ** B
            At = last_true(lambda a: block_holds(F, U, a, B, sbits), top)
            Rt = last_true(lambda a: rank_holds(F, U, a, B, sbits), top)
            if At is None or Rt is None:
                return None
            if At + 1 < top and block_holds(F, U, At + 1, B, sbits) is not False:
                raise Undecided()
            if Rt + 1 < top and rank_holds(F, U, Rt + 1, B, sbits) is not False:
                raise Undecided()
            Ls = {r: log_upper(F, U["m"], r) for r in list(U["H"]) + [U["m"] - 1, 1]}
            break
        except Undecided:
            P *= 2
            if P > 4096:
                raise Refuse("FIG", "the figure could not be decided with 4096 bits")

    def ok(a):
        g = block_cert(U, Ls, a, B, sbits)
        return g is not None and g > 0
    Ac = last_true(ok, At + 1)
    Rc = last_true(lambda a: rank_cert(U, Ls[1], a, B, sbits), Rt + 1)
    if Ac is None or Rc is None:
        return None
    assert ok(Ac) and (Ac == At or not ok(Ac + 1))
    return dict(block=Ac, block_true=At, rank=Rc, rank_true=Rt, bits=P,
                slack=float(block_cert(U, Ls, Ac, B, sbits) / ((1 << sbits) * U["W"])))


# =====================================================================================================================
# 3. the check
# =====================================================================================================================
KEYS = ("format", "h", "v", "R", "N", "cst", "ports", "frames", "start", "final", "ext", "A", "ret", "scat", "B", "blocks")
KINDS = {("x", "s"), ("s", "s"), ("s", "y"), ("x", "y"), ("x", "x"), ("y", "y")}       # gx:161, core:238
KINDS_A = {("x", "s"), ("s", "s")}                                                     # gx:185, core:249
CLS = "xysc"


def check(c, opt, say):
    res = {}
    # ---- (E0) sizes and ports -----------------------------------------------------------------------------------
    need(type(c) is dict, "F0", "the file is not a JSON object")
    for k in KEYS:
        need(k in c, "F0", "the key %r is missing" % k)
    need(c["format"] == "gcert/1", "E0", "format is not gcert/1")                       # gx:131, core:21
    h, v, R = c["h"], c["v"], c["R"]
    need(all(isint(x) for x in (h, v, R, c["N"], c["cst"])), "F0", "h, v, R, N, cst must be whole numbers")
    need(h >= 1 and v >= 1 and R >= 0, "F0", "h, v, R out of range")
    nreg, full = 2 * v + R, (1 << h) - 1                                                # gx:133
    cls = lambda r: "x" if r < v else "y" if r < 2 * v else "s"                         # gx:148, Lean Data/Raw.lean:8
    ports = c["ports"]
    need(islist(ports) and all(isint(q) for q in ports), "F0", "ports")
    need(len(ports) == v and len(set(ports)) == v and all(0 < q <= full and wt(q) % 2 == 1 for q in ports),
         "E0", "ports: not v distinct labels of odd weight in 1 .. 2^h - 1")            # gx:135, core:85
    e8set = set(q for q in range(512) if wt(q) in (3, 7))
    res["e8_family"] = (h == 9 and v == 120 and set(ports) == e8set)
    if opt["e8"]:
        need(res["e8_family"], "E8", "the family is not exactly the 120 E8 ports (h = 9, weights 3 and 7)")
    # ---- (E0) the frame table ------------------------------------------------------------------------------------
    fr = c["frames"]
    need(islist(fr) and len(fr) >= 2, "E0", "frame table")                              # core:86
    nfr, dim, piv, els, seen = len(fr), [], [], [], {}
    small = h <= 12
    for i, f in enumerate(fr):
        need(islist(f) and all(isint(b) and 0 < b <= full for b in f), "E0", "frame %d: entries" % i)   # core:87
        cf = canon(f)
        need(tuple(f) == cf, "E0", "frame %d is not written as a reduced echelon basis" % i)            # gx:30-34,137
        need(cf not in seen, "E0", "frames %d and %d are the same subspace" % (seen.get(cf, -1), i))    # gx:137, core:88
        seen[cf] = i
        dim.append(len(cf))
        piv.append({b.bit_length() - 1: b for b in cf})
        els.append(elements(cf) if small else None)
    need(fr[0] == [] and fr[1] == [1 << i for i in range(h - 1, -1, -1)], "E0", "frame 0 is not zero or frame 1 is not the full space")  # gx:136
    sub_cache = {}

    def inside(o, f):
        """is frame o contained in frame f (two methods when h <= 12; they must agree)"""
        if (o, f) not in sub_cache:
            a = all(in_span(u, piv[f]) for u in fr[o])
            if small:
                assert a == (els[o] & ~els[f] == 0), "the two containment tests disagree"
            sub_cache[o, f] = a
        return sub_cache[o, f]
    # ---- (E1) where every register starts and ends ---------------------------------------------------------------
    start, final = c["start"], c["final"]
    need(islist(start) and islist(final) and len(start) == len(final) == nreg, "E0", "start / final: not one entry per register")  # gx:140
    need(all(isint(f) and 0 <= f < nfr for f in start + final), "F0", "start / final: a frame number outside the table")
    need(c["ext"] == [], "EXT", "`ext` is not empty: the tools print no figure for such a file (gxdry.py:45,53)")
    for T in range(v):
        need(tuple(fr[start[T]]) == (ports[T],), "E1", "x_%d does not start on the line of its port" % T)          # gx:143
        need(final[T] == 1, "E1", "x_%d does not end at the full space" % T)                                        # gx:143
        f = fr[final[v + T]]
        need(start[v + T] == 0, "E1", "y_%d does not start at the zero frame" % T)                                  # gx:145
        need(len(f) == h - 1 and all(wt(u & ports[T]) % 2 == 0 for u in f), "E1",
             "y_%d does not end at the hyperplane of its port" % T)                                                 # gx:144-145
        if small:
            assert els[final[v + T]] == sum(1 << u for u in range(1 << h) if wt(u & ports[T]) % 2 == 0)
    for r in range(2 * v, nreg):
        need(start[r] == 0 and final[r] == 1, "E1", "helper %d does not start at zero / end at the full space" % r)  # gx:146-147
    # ---- the gates, parsed (gx:120-126; core:32-36; Lean Data/Raw.lean:21-27) -------------------------------------
    def parse(g, where):
        need(islist(g) and len(g) >= 1 and type(g[0]) is str, "F0", "gate %s: not a list" % where)
        if g[0] == "out":                       # every tgt += (num/den) * src
            need(len(g) == 5, "F0", "gate %s: an 'out' gate has 5 fields" % where)
            f, s, tg, ex = g[1:]
            need(isint(f) and isint(s) and islist(tg) and islist(ex) and all(isint(e) for e in ex), "F0", "gate %s: fields" % where)
            need(all(islist(a) and len(a) == 3 and all(isint(z) for z in a) for a in tg), "F0", "gate %s: an add is [register, num, den]" % where)
            need(all(a[2] > 0 for a in tg), "E0", "gate %s: a denominator is not positive" % where)               # core:25-27
            return f, [s] + [a[0] for a in tg] + ex, [(a[0], s, a[1], a[2]) for a in tg]
        need(g[0] == "in", "E0", "gate %s: unknown kind %r" % (where, g[0]))                                        # core:35
        need(len(g) == 4, "F0", "gate %s: an 'in' gate has 4 fields" % where)
        f, t, sr = g[1:]                        # tgt += sum of (num/den) * src, one after the other
        need(isint(f) and isint(t) and islist(sr), "F0", "gate %s: fields" % where)
        need(all(islist(a) and len(a) == 3 and all(isint(z) for z in a) for a in sr), "F0", "gate %s: an add is [register, num, den]" % where)
        need(all(a[2] > 0 for a in sr), "E0", "gate %s: a denominator is not positive" % where)
        return f, [t] + [a[0] for a in sr], [(t, a[0], a[1], a[2]) for a in sr]
    need(islist(c["A"]) and islist(c["B"]), "F0", "A / B are not lists")
    G = {ph: [parse(g, "%s%d" % (ph, i)) for i, g in enumerate(c[ph])] for ph in "AB"}
    # ---- the totals and the scatter, parsed (gx:111-117, 166-171; core:37-41, 223-228) ----------------------------
    ret = c["ret"]
    need(islist(ret) and all(islist(z) and len(z) == 3 and all(isint(q) for q in z) for z in ret), "F0", "ret")
    nt = len(ret)
    need(sorted(z[0] for z in ret) == list(range(nt)), "E2", "the totals are not numbered 0, 1, 2, ..")             # gx:166
    tot_reg = {k: s for k, s, _ in ret}
    sc = c["scat"]
    need(type(sc) is dict, "F0", "scat")
    if "table" in sc:
        tb = sc["table"]
        need(islist(tb) and all(islist(row) and all(islist(a) and len(a) == 3 and all(isint(z) for z in a) for a in row) for row in tb), "F0", "scatter table")
        need(len(tb) == v and all(0 <= a[0] < nt for row in tb for a in row), "E2", "scatter table: not v rows, or a total that does not exist")  # gx:168
        need(all(a[2] > 0 for row in tb for a in row), "E0", "scatter table: a denominator is not positive")
        rows = [[(a[0], a[1], a[2]) for a in row] for row in tb]
    else:
        need("inside" in sc and "outside" in sc, "F0", "scat: neither a table nor the star rule")
        for z in (sc["inside"], sc["outside"]):
            need(islist(z) and len(z) == 2 and isint(z[0]) and isint(z[1]) and z[1] > 0, "E0", "star rule: coefficients")
        need(nt == h, "E2", "star rule: not exactly one total per coordinate")                                      # gx:171
        rows = [[(k,) + tuple(sc["inside"] if q >> k & 1 else sc["outside"]) for k in range(h)] for q in ports]     # gx:116-117
    # ---- (E1, E2, E3, E6) the replay of the frames ---------------------------------------------------------------
    cur = list(start)
    chain = [[f] for f in start]
    Hc = {k: Counter() for k in CLS}

    def climb(r, f, where):
        o = cur[r]
        if o != f:
            need(dim[o] < dim[f], "E1", "%s: register %d would go from dimension %d to dimension %d" % (where, r, dim[o], dim[f]))  # gx:157
            need(inside(o, f), "E1", "%s: register %d: its frame is not inside the frame of the gate" % (where, r))                 # gx:157
            Hc[cls(r)][dim[f] - dim[o]] += 1                                                                                       # gx:159
            cur[r] = f
            chain[r].append(f)
    ysum, pivs, ytg = Counter(), set(), set()
    nadds = visits = most = 0
    kinds = Counter()
    for ph in "AB":
        if ph == "B":                           # the scatter cut (gx:165-175; core:223-233)
            for k, s, f in ret:
                need(2 * v <= s < nreg, "E2", "total %d is not held by a helper" % k)                               # gx:173
                need(0 <= f < nfr and cur[s] == f, "E2", "total %d: helper %d does not stand at the frame the file names" % (k, s))  # gx:173
                Hc["c"][dim[f]] += 1                                                                                # gx:174
            need(all(cur[v + t] == 0 for t in range(v)), "E2", "a y left the zero frame before the scatter")       # gx:175
        for i, (f, regs, adds) in enumerate(G[ph]):
            w = "gate %s%d" % (ph, i)
            need(0 <= f < nfr, "F0", "%s: frame number outside the table" % w)
            need(all(0 <= r < nreg for r in regs) and len(set(regs)) == len(regs), "E3", "%s: a register that does not exist, or one register twice" % w)  # gx:178
            need(ph == "B" or all(cls(r) != "y" for r in regs), "E2", "%s: a y is named before the scatter" % w)   # gx:190
            for r in regs:
                climb(r, f, w)                                                                                      # gx:180-181
            assert all(cur[r] == f for r in regs)                # every register named stands at the frame of the gate
            visits += len(regs)
            most = max(most, len(regs))
            for t, s, a, b in adds:
                kd = (cls(s), cls(t))
                need(kd in KINDS and t != s, "E3", "%s: an addition %s -> %s is not allowed" % (w, kd[0], kd[1]))  # gx:184, core:248
                need(ph == "B" or kd in KINDS_A, "E3", "%s: an addition %s -> %s before the scatter" % (w, kd[0], kd[1]))  # gx:185
                if kd == ("y", "y"):                                                                                # gx:186-189, core:250-254
                    need(6 % b == 0, "E4", "%s: y reads y with a denominator that does not divide 6" % w)          # core:251
                    ysum[s, t] += Q(a, b)
                    pivs.add(s)
                    ytg.add(t)
                nadds += 1
                kinds[ph, kd] += 1
    for r in range(nreg):
        climb(r, final[r], "final climb")                                                                           # gx:191-192
    need(not (pivs & ytg), "E4", "a y that is read by a y is itself the target of an addition reading a y")        # gx:193
    need(all(x == 0 for x in ysum.values()), "E4", "the reads of one y by another do not cancel")                  # gx:194
    # every register's chain, tested once more on its own: strictly growing subspaces from start to final
    for r in range(nreg):
        ch = chain[r]
        assert ch[0] == start[r] and ch[-1] == final[r]
        for a, b in zip(ch, ch[1:]):
            assert dim[a] < dim[b] and inside(a, b)
            if small:
                assert els[a] & ~els[b] == 0 and els[a] != els[b]
    # ---- (E6) blocks, N, cst (gx:195-199; core:215-219) ----------------------------------------------------------
    mine = {k: {str(r): n for r, n in sorted(Hc[k].items())} for k in CLS}
    need(type(c["blocks"]) is dict and all(type(w) is dict and all(isint(n) for n in w.values()) for w in c["blocks"].values()),
         "F0", "blocks: not {class: {rank: whole number}}")
    need(c["blocks"] == mine, "E6", "the block list of the file is not the one counted by the replay; counted: %s" % json.dumps(mine))  # gx:196
    N = sum(r * n for k in CLS for r, n in Hc[k].items())
    cst = sum(r * n for r, n in Hc["c"].items())
    need(N == c["N"], "E6", "N of the file is %d, the replay counts %d moves" % (c["N"], N))                        # gx:199
    need(N == R * h + 2 * v * (h - 1) + c["cst"], "E6", "N is not R h + 2 v (h-1) + cst")                           # gx:199
    need(cst == c["cst"], "E6", "cst of the file is %d, the totals stand at dimensions that sum to %d" % (c["cst"], cst))  # core:219
    assert N == sum(dim[final[r]] - dim[start[r]] for r in range(nreg)) + cst
    res.update(h=h, v=v, R=R, N=N, cst=cst, gates_A=len(G["A"]), gates_B=len(G["B"]), frames=nfr, single_adds=nadds,
               scatter_adds=sum(map(len, rows)), visits=visits, most_registers_in_a_gate=most, blocks=mine,
               totals=nt, total_dims=sorted(set(dim[f] for _, _, f in ret)))
    say("frames: %d subspaces; every register climbs a strictly growing chain; every register named by a gate stands at the gate's frame" % nfr)
    nb = {k: Counter() for k in "xys"}
    for r in range(nreg):
        nb[cls(r)][len(chain[r]) - 1] += 1
    res["blocks_per_register"] = {k: dict(sorted(nb[k].items())) for k in "xys"}
    say("blocks per register {number of blocks: registers}: x %s  y %s  helpers %s" % tuple(dict(sorted(nb[k].items())) for k in "xys"))
    say("h=%d v=%d R=%d  gates A=%d B=%d  single additions=%d (+ %d of the scatter = %d)  most registers named by one gate=%d  totals=%d at dimension %s" % (
        h, v, R, len(G["A"]), len(G["B"]), nadds, res["scatter_adds"], nadds + res["scatter_adds"], most, nt, res["total_dims"]))
    res["additions_by_kind"] = {"%s: %s -> %s" % (ph, a, b): n for (ph, (a, b)), n in sorted(kinds.items())}
    say("additions by phase and kind (source -> target; s = helper): %s; scatter: helper -> y %d" % (
        ", ".join("%s: %s" % kv for kv in res["additions_by_kind"].items()), res["scatter_adds"]))
    say("moves of one invocation N=%d = R h + 2 v (h-1) + cst;  copy moves cst=%d;  blocks by class %s" % (N, cst, json.dumps(mine)))
    # ---- (E5) exact replay of the contents (gx:209-250; core:268-315) --------------------------------------------
    t0 = time.time()
    reg = [dict() for _ in range(nreg)]
    for T in range(v):
        reg[T][T] = Q(1)                                                                                            # gx:213
    dn = {"x": 1, "y": 1, "s": 1}
    mx = {"x": Q(0), "y": Q(0), "s": Q(0)}

    def axpy(t, src, a, b, w, E=None):
        if not src:
            return
        co, d, kk = Q(a, b), reg[t], cls(t)
        for key, u in src.items():
            # self-test (h <= 12): an x or a helper receives a source only at a frame that contains the label of
            # that source.  This follows from the rules (contents move only inside one frame, frames only grow).
            assert E is None or kk == "y" or E >> ports[key] & 1, "a source arrived outside its label's frames"
            inc = co * u
            # the mirror keeps contents in sixths and refuses an addition whose product is not a whole number of
            # sixths (core:237, 277-278): (6 u) |a| must be divisible by b
            need(6 % inc.denominator == 0, "E5", "%s: register %d would receive %s of source %d: not a multiple of 1/6" % (w, t, inc, key))
            x = d.get(key, 0) + inc
            if x:
                d[key] = x
                if x.denominator != 1 and dn[kk] % x.denominator:
                    dn[kk] = dn[kk] * x.denominator // gcd(dn[kk], x.denominator)
                if abs(x) > mx[kk]:
                    mx[kk] = abs(x)
            else:
                d.pop(key, None)

    def run(ph):
        for i, (f, regs, adds) in enumerate(G[ph]):
            w = "gate %s%d" % (ph, i)
            E = els[f] if small else None
            if c[ph][i][0] == "out":            # the source is read once, before the additions (gx:237)
                src = dict(reg[adds[0][1]]) if adds else {}
                for t, s, a, b in adds:
                    axpy(t, src, a, b, w, E)
            else:                               # one source after the other (gx:241-242)
                for t, s, a, b in adds:
                    axpy(t, reg[s], a, b, w, E)
    run("A")
    tot = {k: dict(reg[s]) for k, s in tot_reg.items()}                                                             # gx:244
    for S in range(v):
        for k, a, b in rows[S]:
            axpy(v + S, tot[k], a, b, "scatter row %d" % S)                                                         # gx:245-247
    after_scatter = [dict(reg[v + S]) for S in range(v)]
    run("B")
    for T in range(v):
        need(reg[T] == {T: 1}, "E5", "x_%d does not hold exactly its own source at the end (X3)" % T)              # gx:249
    for S in range(v):
        need(reg[v + S] == {S: 1}, "E5", "y_%d does not hold exactly 1 x source %d at the end (hid)" % (S, S))     # gx:250
    res["content_denominators"] = dict(dn)
    res["content_max"] = {k: str(x) for k, x in mx.items()}
    res["helpers_not_empty_at_end"] = sum(1 for r in range(2 * v, nreg) if reg[r])
    say("contents, exact (vectors over the %d sources): every x holds 1 x its own source, every y_S holds 1 x source S and nothing else  [%.1f s]" % (v, time.time() - t0))
    say("  denominators met {class: lcm} %s   largest entries %s   helpers not empty at the end: %d of %d" % (
        dn, res["content_max"], res["helpers_not_empty_at_end"], R))
    # what the scatter alone gives y_S: its own source with coefficient 1, and what else
    own = all(after_scatter[S].get(S) == 1 for S in range(v))
    foreign = sum(len(d) - (1 if S in d else 0) for S, d in enumerate(after_scatter))
    known = all(wt(ports[T] & ports[S]) % 2 == 0 for S, d in enumerate(after_scatter) for T in d if T != S)
    res["scatter_gives_own_source"] = own
    res["scatter_foreign_entries"] = foreign
    res["scatter_foreign_all_in_hyperplane"] = known
    say("  right after the scatter: every y_S holds its own source with coefficient 1: %s; other sources to be removed in phase B: %d entries, "
        "every one with its label inside the hyperplane of S: %s" % (own, foreign, known))
    # ---- (E5 again) the same replay on random values, twice ------------------------------------------------------
    if not opt["norandom"]:
        t0 = time.time()
        for run_no in range(2):
            seed = opt["seed"] + run_no if opt["seed"] is not None else int.from_bytes(os.urandom(16), "big")
            rnd = random.Random(seed)
            val = [Q(rnd.getrandbits(64) - (1 << 63), rnd.randint(1, 64)) for _ in range(v)]
            z = [Q(0)] * nreg
            z[:v] = val
            for ph in "AB":
                if ph == "B":
                    tv = {k: z[s] for k, s in tot_reg.items()}
                    for S in range(v):
                        z[v + S] += sum((Q(a, b) * tv[k] for k, a, b in rows[S]), Q(0))
                for i, (f, regs, adds) in enumerate(G[ph]):
                    if c[ph][i][0] == "out":
                        if adds:
                            sv = z[adds[0][1]]
                            for t, s, a, b in adds:
                                z[t] += Q(a, b) * sv
                    else:
                        for t, s, a, b in adds:
                            z[t] += Q(a, b) * z[s]
            need(all(z[T] == val[T] and z[v + T] == val[T] for T in range(v)), "E5", "random-value run %d (seed %d): the end state is wrong" % (run_no, seed))
            res.setdefault("random_seeds", []).append(seed)
        say("contents, two runs on fresh random rational values (seeds %s): x and y end with the right values  [%.1f s]" % (res["random_seeds"], time.time() - t0))
    # ---- the unit of five stages (unit:22-36; fold:24) -----------------------------------------------------------
    inv = Counter()
    for k in CLS:
        for r, n in Hc[k].items():
            inv[r] += n                                                                                             # core:369-372
    H = Counter()
    for r, n in inv.items():
        H[r] += 5 * n                                                                                               # unit:29-30
    for r in (h - 1, 2 * h - 2, 2 * h + 2, 4):
        H[r] += 2 * v                                                                                               # unit:31-32, fold:24
    m, W = 5 * h, 4 * v + R                                                                                         # unit:33
    D = W * m - sum(r * n for r, n in H.items())                                                                    # unit:34
    need(D == 4 * v - 5 * cst, "UNIT", "moves saved %d is not 4 v - 5 cst = %d" % (D, 4 * v - 5 * cst))             # unit:35
    need(all(1 <= r <= m - 1 for r in H), "UNIT", "a block of the unit has a rank outside 1 .. m-1")
    U = dict(m=m, W=W, D=D, H=dict(sorted(H.items())))
    res.update(m=m, W=W, D=D, unit_blocks=sorted(H.items()), invocation_blocks=sorted(inv.items()))
    say("one invocation, blocks (rank, count): %s" % sorted(inv.items()))
    say("unit of five stages: block size m=%d  arrays W=%d  moves saved D=%d  moves=%d  blocks (rank, count): %s" % (
        m, W, D, W * m - D, sorted(H.items())))
    need(D > 0, "UNIT", "the unit saves no move")
    # ---- the figure (fold:8, 56-68, 86-111; unit:39-47; rate:26-32; gxdry.py:49-52) ------------------------------
    t0 = time.time()
    for B, sb in ((10, 40), (8, 13)):
        fg = figures(U, B, sb)
        need(fg is not None, "FIG", "no figure at %d decimals" % B)
        res["figure_%d" % B] = fg
        say("%d decimals, fill 1 - 2^-%d: whole-block %d (the inequality is true up to %d and false at %d); per-rank %d (true up to %d)%s" % (
            B, sb, fg["block"], fg["block_true"], fg["block_true"] + 1, fg["rank"], fg["rank_true"],
            "  [relative slack of the certificate %.2e; %d-bit interval arithmetic; %.1f s]" % (fg["slack"], fg["bits"], time.time() - t0) if B == 10 else ""))
    res["figure"] = res["figure_10"]["block"]
    # ---- Lean-facing extras (not rules of the two checkers) ------------------------------------------------------
    extras = []

    def extra(name, ok, text):
        extras.append((name, bool(ok), text))
        say("extra %-3s %s  %s" % (name, "pass" if ok else "FAIL", text))
    extra("X1", all(q != full for q in ports), "no port is the all-ones vector (Lean Labels/EndDef.lean:30; gxgen.py:33)")
    extra("X2", all(dim[f] >= 1 for _, _, f in ret), "every total stands at a frame of dimension at least 1 (Lean Labels/EndDef.lean:49-52)")
    extra("X3", len(set(dim[f] for _, _, f in ret)) == 1, "all totals stand at frames of ONE dimension (gxbind.py:232-233): %s" % res["total_dims"])
    extra("X4", [z[0] for z in ret] == list(range(nt)), "the totals are listed in the order 0, 1, 2, .. (gsmirror.py:98)")
    extra("X5", h <= 255, "h <= 255 (Lean Labels/Def.lean:53)")
    net_ok = 4 % dn["x"] == 0 and 4 % dn["s"] == 0 and 24 % dn["y"] == 0
    extra("X6", net_ok, "net contents: x and helpers in quarters, y in twenty-fourths (the units gsmirror.py:119-121 tries)")
    if not opt["noparts"]:
        t0 = time.time()
        sp = parts(v, R, G, rows, tot_reg)
        if sp is None:
            extra("X7", False, "replay with separate positive and negative parts: no unit choice of the grid passes")
        else:
            res["SPar"] = sp["spar"]
            extra("X7", sp["tag_ok"], "replay with separate positive and negative parts (Lean Scalar/Def.lean:62-112, 185-218): passes; "
                  "SPar d sw ux us uy = <%d, %d, %d, %d, %d>; largest digit %d; additions with a division %d  [%.1f s]" % (
                      tuple(sp["spar"]) + (sp["digit"], sp["divs"], time.time() - t0)))
    res["extras"] = {n: ok for n, ok, _ in extras}
    res["extras_ok"] = all(ok for _, ok, _ in extras)
    return res


# =====================================================================================================================
# 4. the replay Lean makes: positive and negative parts kept apart, fixed units (own code, written from the Lean text
#    Work/GCert/Scalar/Def.lean: gW :85-91, gDiv :62-66, gAcc :95-99, gFin :185-192; unit grid of gsm:117-133)
# =====================================================================================================================
class Fail(Exception):
    pass


def parts_run(units, mode, v, R, G, rows, tot_reg):
    ux, us, uy = units
    v2, nreg = 2 * v, 2 * v + R
    unit = lambda r: ux if r < v else uy if r < v2 else us
    P = [dict() for _ in range(nreg)]
    N = [dict() for _ in range(nreg)]
    st = dict(digit=max(ux, uy), cost=0, divs=0, adds=0)
    for T in range(v):
        if mode == "x":
            P[T][T] = ux
        else:
            P[v + T][T] = uy

    def add(t, s, num, den):
        A, Bb = abs(num) * unit(t), den * unit(s)
        g = gcd(A, Bb)
        a, b = A // g, Bb // g                  # the weight in digits, reduced (Def.lean:85-91)
        st["adds"] += 1
        st["cost"] += 2 * a + (2 * b if b > 1 else 0)
        sp, sn = (P[s], N[s]) if num >= 0 else (N[s], P[s])
        if b > 1:                               # both parts of the source are divided by b, exactly (Def.lean:62-66, 96)
            if any(x % b for x in sp.values()) or any(x % b for x in sn.values()):
                raise Fail()
            st["divs"] += 1
        if a == 0:
            return
        for dst, src in ((P[t], sp), (N[t], sn)):
            for k, x in src.items():
                if x:
                    y = dst.get(k, 0) + a * (x // b)
                    dst[k] = y
                    if y > st["digit"]:
                        st["digit"] = y
    if mode == "x":
        for f, regs, adds in G["A"]:
            for t, s, a, b in adds:
                add(t, s, a, b)
        for S in range(v):
            for k, a, b in rows[S]:
                add(v + S, tot_reg[k], a, b)
    for f, regs, adds in G["B"]:
        for t, s, a, b in adds:
            if mode == "x" or v <= s < v2:      # the y check replays only the additions that read a y (Def.lean:21-22)
                add(t, s, a, b)

    def net(r):
        d = {}
        for k in set(P[r]) | set(N[r]):
            x = P[r].get(k, 0) - N[r].get(k, 0)
            if x:
                d[k] = x
        return d
    for T in range(v):
        if mode == "x" and net(T) != {T: ux}:
            raise Fail()
        if net(v + T) != {T: uy}:
            raise Fail()
    return st


def parts(v, R, G, rows, tot_reg):
    best = None
    for ux in (1, 2, 4):
        for us in (1, 2, 4):
            for uy in (1, 2, 3, 6, 12, 24):
                try:
                    s1 = parts_run((ux, us, uy), "x", v, R, G, rows, tot_reg)
                    s2 = parts_run((ux, us, uy), "y", v, R, G, rows, tot_reg)
                except Fail:
                    continue
                dg = max(s1["digit"], s2["digit"])
                sw = dg.bit_length() + 1        # every digit below 2^(sw-1) (Def.lean:15-16)
                cand = (sw, s1["cost"] + s2["cost"], ux, us, uy, dg, s1["divs"])
                if best is None or cand < best:
                    best = cand
    if best is None:
        return None
    sw, _, ux, us, uy, dg, divs = best
    nreg = 2 * v + R
    d = max(1, (nreg - 1).bit_length())
    half = 1 << (sw - 1)
    # Def.lean:207-218: units below half; the 64-bit tag (a sum of digit * weight, weight < 2^32) stays below 2^63
    tag_ok = ux < half and uy < half and v * half < (1 << 31)
    return dict(spar=[d, sw, ux, us, uy], digit=dg, divs=divs, tag_ok=tag_ok)


# =====================================================================================================================
def main():
    args = sys.argv[1:]
    files = [a for a in args if a not in ("e8", "json", "noparts", "norandom") and not a.startswith("seed=")]
    if len(files) != 1:
        sys.stderr.write(__doc__)
        sys.exit(2)
    opt = dict(e8="e8" in args, noparts="noparts" in args, norandom="norandom" in args, seed=None)
    for a in args:
        if a.startswith("seed="):
            opt["seed"] = int(a[5:])
    path = files[0]
    t0 = time.time()

    def say(s):
        print("  " + s, flush=True)
    res, verdict, code = {}, None, 1
    try:
        c, sha = load(path)
        print("replay.py: %s  sha256 %s" % (os.path.basename(path), sha), flush=True)
        res["sha256"] = sha
        res.update(check(c, opt, say))
        if res["extras_ok"]:
            verdict, code = "ACCEPTED", 0
        else:
            verdict, code = "ACCEPTED BY THE RULES OF THE TWO CHECKERS, BUT NOT LEAN-READY (extras failed: %s)" % ", ".join(
                n for n, ok in res["extras"].items() if not ok), 3
        print("REPLAY %s: R=%d W=%d D=%d cst=%d N=%d figure=%d%s  (%.1f s)" % (
            verdict, res["R"], res["W"], res["D"], res["cst"], res["N"], res["figure"],
            "  E8 family: %s" % res["e8_family"], time.time() - t0), flush=True)
    except Refuse as e:
        verdict = "REFUSED"
        res["refused"] = str(e)
        print("REPLAY REFUSED: %s" % e, flush=True)
    except Exception as e:                      # anything unforeseen counts as a refusal
        verdict = "REFUSED"
        res["refused"] = "CRASH: %r" % (e,)
        print("REPLAY REFUSED: CRASH: the program stopped with %r" % (e,), flush=True)
    res["verdict"] = verdict
    res["exit"] = code
    if "json" in args:
        print("JSON " + json.dumps(res, sort_keys=True), flush=True)
    sys.exit(code)


if __name__ == "__main__":
    main()
