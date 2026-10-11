#!/usr/bin/python3 -I
"""gx.py.  OWN code (imports nothing of port-producer, nothing outside).
(1) convert(c0): gcert/0 (port-producer's event list) -> gcert/1, the LEAN-FACING NORMAL FORM:
    only the main phase (no read0 / undo / uninj: the invocation theorem derives the dirt gate and the undo
    gate from the product), every gate an elementary fan-out or fan-in add, the 4x4 K block written as three
    such adds plus a sign carried by one register, the star scatter as a table.
(2) check1(c1): the local decidable conditions of EXTENDED-CERT-SPEC.md on a gcert/1 file:
    E0 sizes, E1 labels (nested subspaces by containment, equal frame at a gate), E2 scatter cut,
    E3 shape (kinds of gates; X1; S1), E4 bracket rule S2, E5 scalar (x-content replay: hid and X3),
    E6 price data (block histograms, N), E7 exterior gauges only (Q2).  Raises AssertionError("<rule>: ...").
"""
from fractions import Fraction as Fr
from collections import Counter
from math import lcm


def need(c, msg):
    if not c:
        raise AssertionError(msg)


def reduce(u, basis):
    """basis: reduced echelon, pivot = leading bit, descending.  Returns u modulo the span."""
    for b in basis:
        if u >> (b.bit_length() - 1) & 1:
            u ^= b
    return u


def echelon_ok(f):
    piv = [b.bit_length() - 1 for b in f]
    if any(b == 0 for b in f) or piv != sorted(piv, reverse=True) or len(set(piv)) != len(piv):
        return False
    return all(not (b >> p & 1) for i, b in enumerate(f) for j, p in enumerate(piv) if i != j)


def inside(a, b):
    return all(reduce(u, b) == 0 for u in a)


def par(x):
    return bin(x).count("1") & 1


KJ = [[[1, 2] if i == j else [-1, 2] for j in range(4)] for i in range(4)]


def convert(c0):
    need(c0["format"] == "gcert/0", "input is not gcert/0")
    v, h, R = c0["v"], c0["h"], c0["R"]
    ev = c0["events"]
    cen = [n for n, e in enumerate(ev) if e[0] == "centre"]
    need(cen == list(range(cen[0], cen[0] + len(cen))), "centres are not contiguous: no single scatter cut")
    A, B, ret = [], [], []
    neg = set()            # x registers currently holding MINUS their value (between the two K blocks)
    openq = {}
    for n, e in enumerate(ev):
        k = e[0]
        out = A if n < cen[0] else B
        if k in ("read0", "undo", "uninj"):
            continue
        if k == "inj":
            need(e[2] not in neg, "inj reads a negated x register")
            out.append(["out", e[3], e[2], [[e[1], 1, 1]], []])
        elif k == "op":
            if e[3] == -1:
                out.append(["neg", e[5], e[1]])
            else:
                need(e[3] == 1, "op ca")
            out.append(["out", e[5], e[2], [[e[1], e[4], 1]], []])
        elif k == "centre":
            ret.append([e[2], e[1], e[3]])
        elif k == "gread":
            hit = set(t for t, _, _ in e[3])
            out.append(["out", e[2], e[1], [[v + t, a, b] for t, a, b in e[3]], [v + t for t in e[4] if t not in hit]])
        elif k == "rread":
            out.append(["out", e[2], e[1], [[v + t, a, b] for t, a, b in e[3]], []])
        elif k == "ysh":
            out.append(["out", e[4], e[2], [[e[1], e[3], 1]], []])
        elif k == "yw":
            out.append(["out", e[4], e[2], [[e[1], e[3][0], e[3][1]]], []])
        elif k == "kd":
            out.append(["out", e[3], e[2], [[e[1], -1 if e[2] in neg else 1, 1]], []])
        elif k == "ktr":
            q = tuple(e[1])
            need(e[2] == KJ, "ktr matrix is not 1 - J/2")
            x1, rest = q[0], list(q[1:])
            if q not in openq:          # first block: x := M x, register x1 keeps the sign
                out.append(["in", e[3], x1, [[r, 1, 1] for r in rest]])
                out.append(["out", e[3], x1, [[r, -1, 2] for r in rest], []])
                out.append(["in", e[3], x1, [[r, 1, 1] for r in rest]])
                openq[q] = n
                neg.add(x1)
            else:                       # second block: the three adds undone in reverse order
                out.append(["in", e[3], x1, [[r, -1, 1] for r in rest]])
                out.append(["out", e[3], x1, [[r, 1, 2] for r in rest], []])
                out.append(["in", e[3], x1, [[r, -1, 1] for r in rest]])
                del openq[q]
                neg.discard(x1)
        else:
            raise AssertionError("unknown event kind %r" % k)
    need(not openq and not neg, "a K block is not closed")
    ext = sorted([z[3], z[1]] for z in c0["gauge"] if z[5])
    c1 = dict(format="gcert/1", derived_from=c0["name"] + " (gcert/0)", p=c0["p"], h=h, v=v, R=R, cst=c0["cst"],
              N=c0["N"], ports=c0["ports"], frames=c0["frames"], start=c0["start"], final=c0["final"],
              ext=ext, ret=sorted(ret), scat=dict(inside=c0["scat"]["inside"], outside=c0["scat"]["outside"]),
              A=A, B=B, blocks=c0["blocks"])
    return c1


def scat_row(c, t):
    """the scatter of target t: [(k, coefficient)], from the table or from the star rule"""
    sc = c["scat"]
    if "table" in sc:
        return [(k, Fr(a, b)) for k, a, b in sc["table"][t]]
    sin, sout = Fr(*sc["inside"]), Fr(*sc["outside"])
    return [(k, sin if c["ports"][t] >> k & 1 else sout) for k in range(c["h"])]


def gate_regs(g):
    if g[0] == "neg":
        return [g[2]], [], []
    if g[0] == "out":
        return [g[2]] + [t for t, _, _ in g[3]] + list(g[4]), [(t, g[2], Fr(a, b)) for t, a, b in g[3]], g[4]
    if g[0] == "in":
        return [g[2]] + [s for s, _, _ in g[3]], [(g[2], s, Fr(a, b)) for s, a, b in g[3]], []
    raise AssertionError("E0: unknown gate kind %r" % (g[0],))


def check1(c, scalar=True, stats=None):
    need(c.get("format") == "gcert/1", "E0: format")
    h, v, R = c["h"], c["v"], c["R"]
    nreg = 2 * v + R
    ports, fr = c["ports"], [tuple(f) for f in c["frames"]]
    need(len(ports) == v == len(set(ports)) and all(par(q) and 0 < q < 1 << h for q in ports), "E0: ports")
    need(fr[0] == () and fr[1] == tuple(1 << i for i in range(h - 1, -1, -1)), "E0: frames 0 and 1")
    need(all(echelon_ok(f) for f in fr) and len(set(fr)) == len(fr), "E0: frame table not reduced echelon / repeats")
    dim = [len(f) for f in fr]
    start, final = c["start"], c["final"]
    need(len(start) == len(final) == nreg, "E0: start / final")
    ext = {r: f for r, f in c["ext"]}
    for t in range(v):
        need(fr[start[t]] == (ports[t],) and final[t] == 1, "E1: x start / final")
        f = fr[final[v + t]]
        need(start[v + t] == 0 and len(f) == h - 1 and all(par(u & ports[t]) == 0 for u in f), "E1: y start / final")
    for r in range(2 * v, nreg):
        need(start[r] == ext.get(r, 0) and final[r] == 1, "E1: slot start / final")
    cls = lambda r: "x" if r < v else "y" if r < 2 * v else "s"
    cur = list(start)
    H = {"x": Counter(), "y": Counter(), "s": Counter(), "c": Counter()}
    steps = set()

    def climb(r, f, where):
        o = cur[r]
        if o != f:
            if (o, f) not in steps:
                need(dim[o] < dim[f] and inside(fr[o], fr[f]), "E1: step not nested (%s, register %d)" % (where, r))
                steps.add((o, f))
            H[cls(r)][dim[f] - dim[o]] += 1
            cur[r] = f
    okind = {("x", "s"), ("s", "s"), ("s", "y"), ("x", "y"), ("x", "x"), ("y", "y")}
    ysum, piv, ytg = Counter(), set(), set()
    inc = 0
    for ph, gates in (("A", c["A"]), ("B", c["B"])):
        if ph == "B":      # ---- E2: the scatter cut
            need(sorted(k for k, _, _ in c["ret"]) == list(range(len(c["ret"]))), "E2: retained totals numbered 0..")
            if "table" in c["scat"]:
                need(len(c["scat"]["table"]) == v and all(0 <= k < len(c["ret"]) for row in c["scat"]["table"] for k, _, _ in row),
                     "E2: scatter table")
            else:
                need(len(c["ret"]) == h, "E2: one retained total per coordinate (star rule)")
            for k, s, f in c["ret"]:
                need(cls(s) == "s" and cur[s] == f, "E2: retained slot %d is not at its frame" % s)
                H["c"][dim[f]] += 1
            need(all(cur[v + t] == 0 for t in range(v)), "E2: a y role left frame 0 before the scatter")
        for i, g in enumerate(gates):
            regs, pairs, _ = gate_regs(g)
            need(all(0 <= r < nreg for r in regs) and len(set(regs)) == len(regs), "E3: registers of gate %s%d" % (ph, i))
            inc += len(regs)
            for r in regs:
                climb(r, g[1], "%s%d" % (ph, i))
            for t, s, co in pairs:
                kd = (cls(s), cls(t))
                need(kd in okind, "E3: gate kind %s -> %s (gate %s%d)" % (kd + (ph, i)))
                need(ph == "B" or kd in {("x", "s"), ("s", "s")}, "E3: bank gate before the scatter (gate A%d)" % i)
                if kd == ("y", "y"):
                    ysum[s, t] += co
                    piv.add(s)
                    ytg.add(t)
            need(ph == "B" or all(cls(r) != "y" for r in regs), "E2: y role named in phase A")
    for r in range(nreg):
        climb(r, final[r], "final")
    need(not (piv & ytg), "E4: a pivot is the target of a gate reading y")
    need(all(x == 0 for x in ysum.values()), "E4: y-reads of a (pivot, target) pair do not cancel")
    Hs = {k: {str(r): n for r, n in sorted(w.items())} for k, w in H.items()}
    need(Hs == c["blocks"], "E6: block histograms")
    N = sum(r * n for w in H.values() for r, n in w.items())
    tails = sum(dim[f] for f in ext.values())
    need(N == c["N"] and N + tails == R * h + 2 * v * (h - 1) + c["cst"], "E6: N")
    if stats is not None:
        stats.update(steps=len(steps), incidences=inc, blocks=sum(sum(w.values()) for w in H.values()),
                     step_work=sum(dim[a] * dim[b] for a, b in steps), ysh_pairs=len(ysum))
    if scalar:
        scal(c, stats)
        q2(c)
    return True


def scal(c, stats=None):
    """E5: exact replay of the x-content of every register through A, scatter, B."""
    h, v, R = c["h"], c["v"], c["R"]
    nreg = 2 * v + R
    reg = [({r: Fr(1)} if r < v else {}) for r in range(nreg)]
    den = {"x": 1, "y": 1, "s": 1}
    mx = {"x": Fr(0), "y": Fr(0), "s": Fr(0)}
    cls = lambda r: "x" if r < v else "y" if r < 2 * v else "s"

    def axpy(t, src, co):
        d = reg[t]
        for k, u in src.items():
            w = d.get(k, 0) + co * u
            if w:
                d[k] = w
                kk = cls(t)
                if w.denominator != 1:
                    den[kk] = lcm(den[kk], w.denominator)
                if abs(w) > mx[kk]:
                    mx[kk] = abs(w)
            else:
                d.pop(k, None)

    def run(gates):
        for g in gates:
            if g[0] == "neg":
                reg[g[2]] = {k: -u for k, u in reg[g[2]].items()}
            elif g[0] == "out":
                src = dict(reg[g[2]])
                for t, a, b in g[3]:
                    axpy(t, src, Fr(a, b))
            else:
                for s, a, b in g[3]:
                    axpy(g[2], reg[s], Fr(a, b))
    run(c["A"])
    tot = {k: dict(reg[s]) for k, s, _ in c["ret"]}
    for t in range(v):
        for k, co in scat_row(c, t):
            axpy(v + t, tot[k], co)
    run(c["B"])
    need(all(reg[t] == {t: 1} for t in range(v)), "E5: an x role is not restored (X3)")
    need(all(reg[v + t] == {t: 1} for t in range(v)), "E5: a target does not receive exactly its source (hid)")
    if stats is not None:
        stats.update(den=dict(den), maxabs={k: str(x) for k, x in mx.items()},
                     gates_A=len(c["A"]), gates_B=len(c["B"]))


def q2(c):
    """E7 (only for files with exterior gauges, rule (2)): for every slot q that starts off the zero frame, the
    column of q in the y rows of the product is zero (its dirt is removed in line, the derived dirt gate at
    frame 0 does not touch it).  Replay with the gauged slots as variables, x = 0."""
    h, v, R = c["h"], c["v"], c["R"]
    ext = [r for r, _ in c["ext"]]
    if not ext:
        return True
    reg = [dict() for _ in range(2 * v + R)]
    for r in ext:
        reg[r] = {r: Fr(1)}

    def axpy(t, src, co):
        d = reg[t]
        for k, u in src.items():
            w = d.get(k, 0) + co * u
            if w:
                d[k] = w
            else:
                d.pop(k, None)

    def run(gates):
        for g in gates:
            if g[0] == "neg":
                reg[g[2]] = {k: -u for k, u in reg[g[2]].items()}
            elif g[0] == "out":
                src = dict(reg[g[2]])
                for t, a, b in g[3]:
                    axpy(t, src, Fr(a, b))
            else:
                for s, a, b in g[3]:
                    axpy(g[2], reg[s], Fr(a, b))
    run(c["A"])
    tot = {k: dict(reg[s]) for k, s, _ in c["ret"]}
    for t in range(v):
        for k, co in scat_row(c, t):
            if tot[k]:
                axpy(v + t, tot[k], co)
    run(c["B"])
    need(all(not reg[v + t] for t in range(v)), "E7: the dirt of an exterior-gauged slot reaches a y role (Q2)")
    return True
