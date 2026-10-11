"""gxcore.py: gcert/1 JSON -> normal data D, PYTHON MIRROR of the two Lean checks
(label side: E0 frames, E1 pairs, E1/E2/E6 replay in segments; scalar side: E3 kinds, E4 bracket, E5 replay
in source batches, E7), derived data (distinct climbs, cut states, block histogram) and kernel sizes.
Own code; the reference is gx.py (check1), not imported.  Python 3, standard library only."""
import json, gzip
from collections import Counter
from math import gcd


class Reject(Exception):
    pass


def need(c, msg):
    if not c:
        raise Reject(msg)


def load(path):
    c = json.load(gzip.open(path, "rt") if path.endswith(".gz") else open(path))
    need(c.get("format") == "gcert/1", "E0: format is not gcert/1")
    return c


def co(num, den):
    need(den > 0, "E0: denominator")
    return (num < 0, abs(num), den)


def normal(c):
    """the Lean-facing data: gates as tuples, coefficients (neg, num, den), ret by total"""
    def gate(g):
        if g[0] == "out":
            return ("out", g[1], g[2], [(t, co(a, b)) for t, a, b in g[3]], list(g[4]))
        need(g[0] == "in", "E0: unknown gate kind %r" % (g[0],))
        return ("in", g[1], g[2], [(s, co(a, b)) for s, a, b in g[3]])
    ret = sorted(c["ret"])
    need([k for k, _, _ in ret] == list(range(len(ret))), "E2: retained totals numbered 0..")
    sc = c["scat"]
    scat = ("table", [[(k, co(a, b)) for k, a, b in row] for row in sc["table"]]) if "table" in sc else \
        ("star", co(*sc["inside"]), co(*sc["outside"]))
    return dict(h=c["h"], v=c["v"], R=c["R"], N=c["N"], cst=c["cst"], ports=list(c["ports"]),
                frames=[list(f) for f in c["frames"]], start=list(c["start"]), final=list(c["final"]),
                ext=[tuple(e) for e in c.get("ext", [])], ret=[(s, f) for _, s, f in ret], scat=scat,
                A=[gate(g) for g in c["A"]], B=[gate(g) for g in c["B"]],
                blocks={k: {int(r): n for r, n in c["blocks"][k].items()} for k in "xysc"})


def regs(g):
    return [g[2]] + [t for t, _ in g[3]] + (g[4] if g[0] == "out" else [])


def adds(g):
    """single adds (tgt, src, coef) in order"""
    return [(t, g[2], k) for t, k in g[3]] if g[0] == "out" else [(g[2], s, k) for s, k in g[3]]


def reduce(u, basis):
    for b in basis:
        if u >> (b.bit_length() - 1) & 1:
            u ^= b
    return u


def echelon_ok(f):
    piv = [b.bit_length() - 1 for b in f]
    if any(b == 0 for b in f) or any(piv[i] <= piv[i + 1] for i in range(len(piv) - 1)):
        return False
    return all(not (b >> p & 1) for i, b in enumerate(f) for j, p in enumerate(piv) if i != j)


def par(x):
    return bin(x).count("1") & 1


def cls(D, r):
    return "x" if r < D["v"] else "y" if r < 2 * D["v"] else "s"


# ---- label side ------------------------------------------------------------------------------------------
def chk_frames(D):
    """E0: ports; frame table reduced echelon, no repeats, zero first, full second"""
    h, v, fr = D["h"], D["v"], D["frames"]
    p = D["ports"]
    need(len(p) == v == len(set(p)) and all(par(q) and 0 < q < 1 << h for q in p), "E0: ports")
    need(len(fr) >= 2 and fr[0] == [] and fr[1] == [1 << i for i in range(h - 1, -1, -1)], "E0: frames 0 and 1")
    need(all(echelon_ok(f) and all(b < 1 << h for b in f) for f in fr), "E0: frame table not reduced echelon")
    need(len(set(map(tuple, fr))) == len(fr), "E0: frame table has repeats")
    return [len(f) for f in fr]


def derive(D):
    """distinct climbs in order of first use (NOT a check: plain replay of the frame ids)"""
    cur, seen, pairs = list(D["start"]), set(), []

    def go(r, f):
        o = cur[r]
        if o != f:
            if (o, f) not in seen:
                seen.add((o, f))
                pairs.append((o, f))
            cur[r] = f
    for g in D["A"] + D["B"]:
        for r in regs(g):
            go(r, g[1])
    for r, f in enumerate(D["final"]):
        go(r, f)
    return pairs


def chk_pairs(D, dim, pairs):
    """E1, level 2: every listed pair is a nested pair of the table; returns the mask-operation count"""
    fr, n, work = D["frames"], len(D["frames"]), 0
    for a, b in pairs:
        need(a < n and b < n and dim[a] < dim[b], "E1: pair (%d, %d) does not climb" % (a, b))
        need(all(reduce(u, fr[b]) == 0 for u in fr[a]), "E1: pair (%d, %d) is not nested" % (a, b))
        work += dim[a] * dim[b]
    return work


def cut_points(D, gmax, wmax=210000):
    """replay segments: each phase (A, B) is cut into k pieces of equal gate count, k = the least number with at
    most `gmax` gates AND at most `wmax` work per piece on average (work = sum over gates of the dimension of the
    gate's frame; measured at h = 22: about 1 ms of kernel time per unit, NOTES.md).
    Cut points = gate counts in A ++ B (always 0, |A| and the end)."""
    nA, nB = len(D["A"]), len(D["B"])
    cuts = [0]
    for off, gs in ((0, D["A"]), (nA, D["B"])):
        n = len(gs)
        k = max(1, -(-n // gmax), -(-sum(len(D["frames"][g[1]]) for g in gs) // wmax))
        cuts += [off + (n * i) // k for i in range(1, k + 1)]
    return sorted(set(cuts))


def label_data(D, dim, cuts):
    """for gx-labels (gcert-interface.md LABELS v1): ordered block ranks per replay segment, the final climbs as
    gates without adds (same final frame, at most 32 registers, only registers that still climb), their ranks,
    the largest number of registers named by one gate.  Plain replay (the mirror has accepted the file)."""
    cur, G = list(D["start"]), D["A"] + D["B"]
    rs, most = [], 0
    for a, b in zip(cuts, cuts[1:]):
        r = []
        for g in G[a:b]:
            most = max(most, len(regs(g)))
            for x in regs(g):
                if cur[x] != g[1]:
                    r.append(dim[g[1]] - dim[cur[x]])
                    cur[x] = g[1]
        rs.append(r)
    by = {}
    for x, f in enumerate(D["final"]):
        if cur[x] != f:
            by.setdefault(f, []).append(x)
    fins, rF = [], []
    for f in sorted(by):
        for i in range(0, len(by[f]), 32):
            xs = by[f][i:i + 32]
            fins.append(("out", f, xs[0], [], xs[1:]))
            rF += [dim[f] - dim[cur[x]] for x in xs]
    return dict(rs=rs, fins=fins, rF=rF, most=max(most, 32 if fins else 0))


def chk_replay(D, dim, pairs, cuts):
    """E1 (labels), E2 (scatter cut), E6 (price), in the segments given by `cuts`.
    Returns (states at the cuts, histogram by class, visits per segment)."""
    h, v, R, fr = D["h"], D["v"], D["R"], D["frames"]
    n = 2 * v + R
    start, final, ext = D["start"], D["final"], dict(D["ext"])
    need(len(start) == len(final) == n, "E0: start / final")
    for t in range(v):
        need(fr[start[t]] == [D["ports"][t]] and final[t] == 1, "E1: x start / final")
        f = fr[final[v + t]]
        need(start[v + t] == 0 and len(f) == h - 1 and all(par(u & D["ports"][t]) == 0 for u in f), "E1: y start / final")
    for r in range(2 * v, n):
        need(start[r] == ext.get(r, 0) and final[r] == 1, "E1: slot start / final")
    ok = set(pairs)
    need(len(ok) == len(pairs), "E1: pair list has repeats")
    cur = list(start)
    H = {k: Counter() for k in "xysc"}

    def climb(r, f, where):
        o = cur[r]
        if o != f:
            need((o, f) in ok, "E1: climb (%d, %d) is not a tested pair (%s, register %d)" % (o, f, where, r))
            H[cls(D, r)][dim[f] - dim[o]] += 1
            seg[dim[f] - dim[o]] += 1
            cur[r] = f
    seg, segs = Counter(), []
    G, nA = D["A"] + D["B"], len(D["A"])
    states, visits = [], []
    need(cuts[0] == 0 and cuts[-1] == len(G) and cuts == sorted(cuts), "cut points")
    for a, b in zip(cuts, cuts[1:]):
        states.append(list(cur))
        vs = 0
        for i in range(a, b):
            if i == nA:
                scatter_cut(D, cur, dim, H, seg)
            g = G[i]
            rs = regs(g)
            need(all(0 <= r < n for r in rs) and len(set(rs)) == len(rs), "E3: registers of gate %d" % i)
            need(i >= nA or all(r < v or r >= 2 * v for r in rs), "E2: y role named in phase A (gate %d)" % i)
            vs += len(rs)
            for r in rs:
                climb(r, g[1], "gate %d" % i)
        visits.append(vs)
        if b < len(G):
            segs.append(seg)
            seg = Counter()
    if nA == len(G):
        scatter_cut(D, cur, dim, H, seg)
    states.append(list(cur))
    for r in range(n):
        climb(r, final[r], "final")
    segs.append(seg)
    Hb = {k: dict(sorted(w.items())) for k, w in H.items()}
    need(Hb == D["blocks"], "E6: block histogram differs from `blocks`")
    N = sum(r * c for w in H.values() for r, c in w.items())
    need(N == D["N"] and N + sum(dim[f] for f in ext.values()) == R * h + 2 * v * (h - 1) + D["cst"], "E6: N")
    need(sum(r * c for r, c in H["c"].items()) == D["cst"], "E6: cst")
    return states, Hb, visits, [[w[r] for r in range(h + 1)] for w in segs]


def scatter_cut(D, cur, dim, H, seg):
    v = D["v"]
    if D["scat"][0] == "table":
        need(len(D["scat"][1]) == v and all(k < len(D["ret"]) for row in D["scat"][1] for k, _ in row), "E2: scatter table")
    else:
        need(len(D["ret"]) == D["h"], "E2: one retained total per coordinate (star rule)")
    for s, f in D["ret"]:
        need(s >= 2 * v and cur[s] == f, "E2: retained slot %d is not at its frame" % s)
        H["c"][dim[f]] += 1
        seg[dim[f]] += 1
    need(all(cur[v + t] == 0 for t in range(v)), "E2: a y role left frame 0 before the scatter")


# ---- scalar side -----------------------------------------------------------------------------------------
SC = 6            # all scalar entries are kept as integers in units of 1/6
KINDS = {("x", "s"), ("s", "s"), ("s", "y"), ("x", "y"), ("x", "x"), ("y", "y")}


def chk_shape(D):
    """E3 kinds, E4 bracket"""
    ysum, piv, ytg = Counter(), set(), set()
    for ph in "AB":
        for i, g in enumerate(D[ph]):
            for t, s, (ng, a, b) in adds(g):
                kd = (cls(D, s), cls(D, t))
                need(kd in KINDS and t != s, "E3: gate kind %s -> %s (gate %s%d)" % (kd + (ph, i)))
                need(ph == "B" or kd in {("x", "s"), ("s", "s")}, "E3: bank gate before the scatter (gate A%d)" % i)
                if kd == ("y", "y"):
                    need(SC % b == 0, "E4: denominator beyond sixths")
                    ysum[s, t] += (-a if ng else a) * (SC // b)
                    piv.add(s)
                    ytg.add(t)
    need(not (piv & ytg), "E4: a pivot is the target of a gate reading y")
    need(all(x == 0 for x in ysum.values()), "E4: y-reads of a (pivot, target) pair do not cancel")
    return len(ysum)


def scat_row(D, t):
    sc = D["scat"]
    if sc[0] == "table":
        return sc[1][t]
    return [(k, sc[1] if D["ports"][t] >> k & 1 else sc[2]) for k in range(D["h"])]



def replay(D, init, count=None):
    """exact replay through A, scatter, B of sparse vectors with entries in sixths; `init` = register -> {key: 6}"""
    v = D["v"]
    reg = [dict(init.get(r, ())) for r in range(2 * v + D["R"])]

    def axpy(t, src, k):
        ng, a, b = k
        d = reg[t]
        for key, u in src.items():
            w = u * a
            need(w % b == 0, "E5: an entry needs a denominator beyond sixths (register %d)" % t)
            w = w // b
            w = d.get(key, 0) + (-w if ng else w)
            if count is not None:
                count[key] += 1
            if w:
                d[key] = w
            else:
                d.pop(key, None)

    def run(gates):
        for g in gates:
            if g[0] == "out":
                src = dict(reg[g[2]])
                for t, k in g[3]:
                    axpy(t, src, k)
            else:
                for s, k in g[3]:
                    axpy(g[2], reg[s], k)
    run(D["A"])
    afterA = sum(len(d) for d in reg)
    tot = [dict(reg[s]) for s, _ in D["ret"]]
    for t in range(v):
        for k, cf in scat_row(D, t):
            if tot[k]:
                axpy(v + t, tot[k], cf)
    run(D["B"])
    return reg, afterA


def chk_scalar(D, batches=1):
    """E5 (+ E7 when `ext` is non-empty).  Returns stats: denominators and largest numerators per class in the
    units of the spec (x halves, y sixths, slots integers), updates per source batch, entries after A."""
    v = D["v"]
    count = Counter()
    reg, afterA = replay(D, {t: {t: SC} for t in range(v)}, count)
    need(all(reg[t] == {t: SC} for t in range(v)), "E5: an x role is not restored (X3)")
    need(all(reg[v + t] == {t: SC} for t in range(v)), "E5: a target does not receive exactly its source (hid)")
    if D["ext"]:
        rg, _ = replay(D, {r: {r: SC} for r, _ in D["ext"]})
        need(all(not rg[v + t] for t in range(v)), "E7: the dirt of an exterior-gauged slot reaches a y role")
    step = -(-v // batches)
    per = [sum(count[k] for k in range(lo, min(lo + step, v))) for lo in range(0, v, step)]
    return dict(updates=sum(count.values()), per_batch=per, afterA=afterA,
                batches=[(lo, min(lo + step, v)) for lo in range(0, v, step)])


def digits(D):
    """largest |entry| met and denominators per class, by a second replay that watches every write (slow path
    kept separate from the check): returns {class: (lcm of denominators, largest |numerator| in units 1/den)}"""
    v = D["v"]
    den = {"x": 1, "y": 1, "s": 1}
    mx = {"x": 0, "y": 0, "s": 0}
    reg = [({r: SC} if r < v else {}) for r in range(2 * v + D["R"])]

    def axpy(t, src, k):
        ng, a, b = k
        d, kk = reg[t], cls(D, t)
        for key, u in src.items():
            w = d.get(key, 0) + (-(u * a // b) if ng else u * a // b)
            if w:
                d[key] = w
                q = SC // gcd(w, SC)
                if den[kk] % q:
                    den[kk] = den[kk] * q // gcd(den[kk], q)
                if abs(w) > mx[kk]:
                    mx[kk] = abs(w)
            else:
                d.pop(key, None)
    for g in D["A"]:
        for t, s, k in adds(g):
            axpy(t, reg[s], k)
    tot = [dict(reg[s]) for s, _ in D["ret"]]
    for t in range(v):
        for k, cf in scat_row(D, t):
            axpy(v + t, tot[k], cf)
    for g in D["B"]:
        for t, s, k in adds(g):
            axpy(t, reg[s], k)
    return {k: (den[k], mx[k] * den[k] // SC if (mx[k] * den[k]) % SC == 0 else "%d/6" % mx[k]) for k in "xys"}


def mirror(D, gmax=12000, batches=1, pairs=None, cuts=None):
    """both checks; returns everything the generator and the dry run need"""
    dim = chk_frames(D)
    pairs = derive(D) if pairs is None else pairs
    work = chk_pairs(D, dim, pairs)
    cuts = cut_points(D, gmax) if cuts is None else cuts
    states, H, visits, segH = chk_replay(D, dim, pairs, cuts)
    ysh = chk_shape(D)
    S = chk_scalar(D, batches)
    hist = Counter()
    for k in "xysc":
        for r, n in H[k].items():
            hist[r] += n
    return dict(dim=dim, pairs=pairs, pair_work=work, cuts=cuts, states=states, H=H, visits=visits, ysh=ysh,
                scal=S, hist=dict(sorted(hist.items())), segH=segH,
                lab=label_data(D, dim, cuts))
