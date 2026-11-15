#!/usr/bin/python3 -I
"""gx-scalar: Python mirror of GS.scalCheck / GS.yCheck (Work/GCert/Scalar/Def.lean).

usage: gsmirror.py <gcert1.json[.gz]> [emit=<Name>] [cuts=i,j,..]
  prints the parameters (d, sw, ux, us, uy) for which both checks pass, and sizes;
  emit=<Name> writes TEST modules Work/GCert/Scalar/Gen/<Name>.lean (scalar fields of GXD.Raw only),
  <Name>Scal0.lean (one evaluation), <Name>Y.lean, and with cuts= <Name>Seg.lean (segments cut before these items).
As a library (gx-data): params(c), bigreplay(c, pr, lo, n, itemsA, itemsB, cuts), lean_state(name, state).
"""
import sys, json, gzip, os
from math import gcd

import gxpaths
ROOT = gxpaths.OUT.rstrip('/')


def load(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        return json.load(f)


def adds_of(g):
    if g[0] == "out":
        return [(t, g[2], a, b) for t, a, b in g[3]]
    if g[0] == "inn" or g[0] == "in":
        return [(g[2], s, a, b) for s, a, b in g[3]]
    raise SystemExit("unknown gate %r" % (g[0],))


def scat_rows(c):
    sc = c["scat"]
    if "table" in sc:
        return [[(k, a, b) for k, a, b in row] for row in sc["table"]]
    (ia, ib), (oa, ob) = sc["inside"], sc["outside"]
    return [[(k, ia, ib) if p >> k & 1 else (k, oa, ob) for k in range(c["h"] - 1, -1, -1)] for p in c["ports"]]


class Fail(Exception):
    pass


def replay(c, units, mode):
    """mode 'x': scalCheck with one batch (0, v); mode 'y': yCheck.  Returns the largest digit."""
    v, R = c["v"], c["R"]
    v2, nr = 2 * v, 2 * v + R
    ux, us, uy = units
    unit = lambda r: ux if r < v else uy if r < v2 else us
    P = [dict() for _ in range(nr)]
    N = [dict() for _ in range(nr)]
    mx = [max(ux, uy)]
    nadd = [0, 0, 0]
    if mode == "x":
        for t in range(v):
            P[t][t] = ux
    else:
        for t in range(v):
            P[v + t][t] = uy

    def add(t, s, a, b, ok):
        if not ok or t == s or not (t < nr and s < nr) or b <= 0:
            raise Fail("kind / bounds: %d += (%d/%d) %d" % (t, a, b, s))
        A, B = abs(a) * unit(t), b * unit(s)
        g = gcd(A, B)
        wa, wb = A // g, B // g
        nadd[0] += 1
        nadd[1] += 2 * wa + (2 * wb if wb > 1 else 0)
        sp, sn = (P[s], N[s]) if a >= 0 else (N[s], P[s])
        if wb > 1 and any(x % wb for x in sp.values()) or wb > 1 and any(x % wb for x in sn.values()):
            raise Fail("digit not divisible by %d" % wb)
        if wb > 1:
            nadd[2] += 1
        if wa == 0:
            return
        for dst, src in ((P[t], sp), (N[t], sn)):
            for k, x in src.items():
                if x == 0:
                    continue
                y = dst.get(k, 0) + wa * (x // wb)
                dst[k] = y
                if y > mx[0]:
                    mx[0] = y

    okA = lambda t, s: v2 <= t and (s < v or v2 <= s)
    okS = lambda t, s: v <= t < v2 and v2 <= s < nr
    okB = lambda t, s: (v <= t or s < v) and (s < v or v2 <= s or v <= t < v2)
    if mode == "x":
        for g in c["A"]:
            for t, s, a, b in adds_of(g):
                add(t, s, a, b, okA(t, s))
        rows = scat_rows(c)
        if len(rows) != v:
            raise Fail("scatter rows")
        for t, row in enumerate(rows):
            for k, a, b in row:
                if not k < len(c["ret"]):
                    raise Fail("scatter total")
                s = c["ret"][k][1]
                add(v + t, s, a, b, okS(v + t, s))
    for g in c["B"]:
        for t, s, a, b in adds_of(g):
            if mode == "x" or v <= s < v2:
                add(t, s, a, b, okB(t, s))
    net = lambda r: {k: x - N[r].get(k, 0) for k, x in P[r].items() if x != N[r].get(k, 0)}
    for r in range(nr):
        if any(k not in P[r] for k in N[r]):
            for k in N[r]:
                P[r].setdefault(k, 0)
    for t in range(v):
        if mode == "x" and net(t) != {t: ux}:
            raise Fail("X3 at %d" % t)
        if net(v + t) != {t: uy}:
            raise Fail("identity at y %d" % t)
    return mx[0], nadd


def params(c):
    best = None
    for ux in (1, 2, 4):
        for us in (1, 2, 4):
            for uy in (1, 2, 3, 6, 12, 24):
                try:
                    m1, n1 = replay(c, (ux, us, uy), "x")
                    m2, n2 = replay(c, (ux, us, uy), "y")
                except Fail as e:
                    continue
                sw = max(m1, m2).bit_length() + 1
                cand = (sw, n1[1] + n2[1], ux, us, uy, m1, m2, n1, n2)
                if best is None or cand < best:
                    best = cand
    if best is None:
        raise SystemExit("REJECTED for every unit choice")
    return best


TAU = lambda T: (2654435761 * (T + 1)) % 4294967296


def bigreplay(c, pr, lo, n, itemsA, itemsB, cuts=()):
    """EXACT mirror of GS.segCheck on Python integers (leaves with tags).
    itemsA / itemsB: the chunks of gates (lists of gates) of A and B as in raw.A / raw.B; item index:
    A chunks 0 .. len(itemsA)-1, the scatter = len(itemsA), B chunks after it.
    cuts: item indices i; the state BEFORE item i is returned as a sorted list of (register, leaf), leaf != 0.
    Raises Fail if a test of the kernel check fails."""
    d, sw, ux, us, uy = pr
    v, R = c["v"], c["R"]
    v2, nr, hi = 2 * v, 2 * v + R, lo + n
    K = 64 + sw * n
    m2 = 1 << K
    rep = sum(1 << (sw * i) for i in range(n))
    tm = ((rep << (sw - 1)) << 64) | (1 << 63)
    half = 1 << (sw - 1)
    if not (ux >= 1 and us >= 1 and uy >= 1 and sw >= 1 and nr <= 1 << d and hi <= v and ux < half and uy < half):
        raise Fail("parameters")
    unit = lambda r: ux if r < v else uy if r < v2 else us
    P, N = [0] * nr, [0] * nr
    for T in range(n):
        P[lo + T] = (ux << (64 + sw * T)) + ux * TAU(T)

    def div(b, X):
        if b == 1:
            return X
        q = X // b
        if q & tm or q * b != X:
            raise Fail("division by %d" % b)
        for j in range(1, b + 1):
            if (j * q) & tm:
                raise Fail("division mask")
        return q

    def addn(acc, q, a):
        for _ in range(a):
            acc += q
            if acc & tm:
                raise Fail("digit overflow")
        return acc

    def add(t, s, ca, cb, ok):
        if not ok or t == s or cb < 1:
            raise Fail("kind / bounds: %d += (%d/%d) %d" % (t, ca, cb, s))
        A, B = abs(ca) * unit(t), cb * unit(s)
        g = gcd(A, B)
        a, b = A // g, B // g
        qp, qn = div(b, P[s]), div(b, N[s])
        if ca < 0:
            qp, qn = qn, qp
        pt, nt = addn(P[t], qp, a), addn(N[t], qn, a)
        if not pt < m2:
            raise Fail("positive part too long")
        P[t], N[t] = pt, nt

    inr = lambda t, s: t < nr and s < nr
    okA = lambda t, s: inr(t, s) and v2 <= t and (s < v or v2 <= s)
    okS = lambda t, s: v <= t < v2 and v2 <= s < nr
    okB = lambda t, s: inr(t, s) and (v <= t or s < v) and (s < v or v2 <= s or v <= t < v2)
    out = {}
    snap = lambda: sorted((r, P[r] + (N[r] << K)) for r in range(nr) if P[r] or N[r])
    idx = 0
    for gs in itemsA:
        if idx in cuts:
            out[idx] = snap()
        for g in gs:
            for t, s, ca, cb in adds_of(g):
                add(t, s, ca, cb, okA(t, s))
        idx += 1
    if idx in cuts:
        out[idx] = snap()
    rows = scat_rows(c)
    ret = [s for _, s, _ in sorted(c["ret"])]
    for t, row in enumerate(rows):
        for k, ca, cb in row:
            if not k < len(ret):
                raise Fail("scatter total")
            add(v + t, ret[k], ca, cb, okS(v + t, ret[k]))
    if len(rows) != v:
        raise Fail("scatter rows")
    idx += 1
    for gs in itemsB:
        if idx in cuts:
            out[idx] = snap()
        for g in gs:
            for t, s, ca, cb in adds_of(g):
                add(t, s, ca, cb, okB(t, s))
        idx += 1
    for S in range(v):
        E = lambda u: (u << (sw * (S - lo))) if lo <= S < hi else 0
        if (P[S] >> 64) != (N[S] >> 64) + E(ux) or (P[v + S] >> 64) != (N[v + S] >> 64) + E(uy):
            raise Fail("final test at %d" % S)
    return out


def lean_state(name, st, size=100):
    """Lean text of a cut state: chunk definitions and `name : List (List (Nat × Nat))` (argument of GS.loadK)"""
    out, names = [], []
    for i in range(0, len(st), size):
        nm = "%s_%d" % (name, i // size)
        names.append(nm)
        out.append("noncomputable def %s : List (Nat × Nat) := [\n  %s]" % (
            nm, ",\n  ".join("(%d, 0x%x)" % rw for rw in st[i:i + size])))
    out.append("noncomputable def %s : List (List (Nat × Nat)) := [%s]" % (name, ", ".join(names)))
    return "\n".join(out)


def co(a, b):
    return "⟨%s, %d, %d⟩" % ("true" if a < 0 else "false", abs(a), b)


def lgate(g):
    if g[0] == "out":
        return "(.out %d %d [%s] [%s])" % (g[1], g[2], ", ".join("(%d, %s)" % (t, co(a, b)) for t, a, b in g[3]),
                                         ", ".join(map(str, g[4])))
    return "(.inn %d %d [%s])" % (g[1], g[2], ", ".join("(%d, %s)" % (s, co(a, b)) for s, a, b in g[3]))


CH = 150


def emit(c, name, pr, cutlist):
    """TEST modules: data (scalar fields only), one-evaluation check, y check, and (if cutlist) a segmented check"""
    d, sw, ux, us, uy = pr
    gen = ROOT + "/Work/GCert/Scalar/Gen"
    os.makedirs(gen, exist_ok=True)
    out = ["import Work.GCert.Scalar.Seg", "/-! generated by checks/wht26/gx-scalar/py/gsmirror.py: SCALAR TEST DATA (frames, pairs, cuts left empty) -/",
           "set_option maxRecDepth 100000", "namespace GS.Gen.%s" % name, "open GXD"]
    chunks = {}
    for ph in ("A", "B"):
        chunks[ph] = [c[ph][i:i + CH] for i in range(0, len(c[ph]), CH)]
        for i, gs in enumerate(chunks[ph]):
            out.append("noncomputable def %s%d : List Gate := [\n  %s]" % (ph, i, ",\n  ".join(map(lgate, gs))))
        out.append("noncomputable def %s : List (List Gate) := [%s]" % (ph, ", ".join("%s%d" % (ph, i) for i in range(len(chunks[ph])))))
    sc = c["scat"]
    if "table" in sc:
        scat = ".table [\n  %s]" % ",\n  ".join("[%s]" % ", ".join("(%d, %s)" % (k, co(a, b)) for k, a, b in row) for row in sc["table"])
    else:
        scat = ".star %s %s" % (co(*sc["inside"]), co(*sc["outside"]))
    out.append("noncomputable def ports : List Nat := [%s]" % ", ".join(map(str, c["ports"])))
    out.append("noncomputable def scat : Scat := %s" % scat)
    out.append("noncomputable def raw : Raw :=\n  { h := %d, v := %d, R := %d, N := %d, cst := %d, ports := ports, frames := [], start := [], final := [],\n"
               "    ret := [%s], scat := scat, A := A, B := B, pairs := [], cuts := [], ext := [], obase := [] }" % (
        c["h"], c["v"], c["R"], c["N"], c["cst"], ", ".join("(%d, %d)" % (s, f) for _, s, f in sorted(c["ret"]))))
    out.append("end GS.Gen.%s" % name)
    open("%s/%s.lean" % (gen, name), "w").write("\n".join(out) + "\n")
    v = c["v"]
    par = "⟨%d, %d, %d, %d, %d⟩" % pr
    tpl = ("import Work.GCert.Scalar.Gen.%s\nset_option maxRecDepth 100000\nnamespace GS.Gen.%s\n" % (name, name))
    open("%s/%sScal0.lean" % (gen, name), "w").write(
        tpl + "theorem scal0_ok : GS.scalCheck raw %s 0 %d = true := by decide +kernel\n#print axioms scal0_ok\nend GS.Gen.%s\n" % (par, v, name))
    open("%s/%sY.lean" % (gen, name), "w").write(
        tpl + "theorem ychk_ok : GS.yCheck raw %s 0 %d = true := by decide +kernel\n#print axioms ychk_ok\nend GS.Gen.%s\n" % (par, v, name))
    if cutlist:
        nA, nB = len(chunks["A"]), len(chunks["B"])
        items = ["Item.cA A%d" % i for i in range(nA)] + ["Item.scat"] + ["Item.cB B%d" % i for i in range(nB)]
        sts = bigreplay(c, pr, 0, v, chunks["A"], chunks["B"], cutlist)
        body = [tpl.replace("import Work.GCert.Scalar.Gen.%s" % name, "import Work.GCert.Scalar.Gen.%s" % name) + "open GS"]
        for i in cutlist:
            body.append(lean_state("L%d" % i, sts[i]))
            body.append("noncomputable def T%d : SSC.Trie := loadK %d L%d" % (i, d, i))
        bounds = [0] + list(cutlist) + [len(items)]
        for j in range(len(bounds) - 1):
            pre = "none" if j == 0 else "(some T%d)" % bounds[j]
            post = "none" if j == len(bounds) - 2 else "(some T%d)" % bounds[j + 1]
            body.append("theorem seg%d_ok : segCheck raw %s 0 %d %s [%s] %s = true := by decide +kernel" % (
                j, par, v, pre, ", ".join(items[bounds[j]:bounds[j + 1]]), post))
        body.append("end GS.Gen.%s" % name)
        open("%s/%sSeg.lean" % (gen, name), "w").write("\n".join(body) + "\n")
        print("segments at items", cutlist, "of", len(items), "; state sizes (non-zero leaves):", [len(sts[i]) for i in cutlist])
    print("emitted", name)


def main():
    path = sys.argv[1]
    opts = dict(a.split("=") for a in sys.argv[2:])
    c = load(path)
    sw, _, ux, us, uy, m1, m2, n1, n2 = params(c)
    nr = 2 * c["v"] + c["R"]
    d = max(1, (nr - 1).bit_length())
    print("file", os.path.basename(path), "h v R", c["h"], c["v"], c["R"], "registers", nr)
    print("SPar d sw ux us uy = ⟨%d, %d, %d, %d, %d⟩" % (d, sw, ux, us, uy))
    print("largest digit: x-replay %d, y-replay %d; adds x-replay %d (bignum additions %d, adds with a division %d), y-replay %d (%d)" % (
        m1, m2, n1[0], n1[1], n1[2], n2[0], n2[1]))
    print("vector bits (one batch):", sw * c["v"])
    pr = (d, sw, ux, us, uy)
    chA = [c["A"][i:i + CH] for i in range(0, len(c["A"]), CH)]
    chB = [c["B"][i:i + CH] for i in range(0, len(c["B"]), CH)]
    bigreplay(c, pr, 0, c["v"], chA, chB)
    print("exact mirror of segCheck (integers with tags): ACCEPTED; items", len(chA) + 1 + len(chB))
    if "emit" in opts:
        emit(c, opts["emit"], pr, [int(x) for x in opts["cuts"].split(",")] if "cuts" in opts else [])


if __name__ == "__main__":
    main()
