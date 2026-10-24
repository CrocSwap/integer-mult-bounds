"""gxconv.py: gcert/0 -> gcert/1 for files whose in-place pair op SCALES its target
(`op dest ctrl ca cb`: dest := ca dest + cb ctrl with ca not in {1}; #193 has ca = -2), questions.md D2.
COPY of `convert` of gx.py with ONE change: a scaling is not a gate, it changes the
UNIT in which the register is stored.  wanted(r) = lam[r] * stored(r), lam = 1 at the start;
    op dest ctrl ca cb :  lam[dest] *= ca ;  stored(dest) += (cb lam[ctrl] / lam[dest]) stored(ctrl)
    any other add t += k s :  stored(t) += (k lam[s] / lam[t]) stored(s)
    scatter y_t += coef(t, k) total_k :  coefficient coef(t, k) * lam[slot of total k]   (a TABLE if some lam != 1)
Only slots may be scaled (tested: lam = 1 on every x and y register, always), so the x / y rows and columns of
the product (E5: hx, hy, hid) are those of the unscaled circuit; frames, blocks and N are untouched.
The result is tested by the reference checker `gx.check1` (labels and scalars) before it is written.

usage: gxconv.py <gcert0.json[.gz]> out=<gcert1.json[.gz]> [noext]
"""
import sys, time
from fractions import Fraction as Fr
import gxpaths
import gx
import gxrun
need = gx.need


def convert(c0):
    need(c0["format"] == "gcert/0", "input is not gcert/0")
    v, h, R = c0["v"], c0["h"], c0["R"]
    ev = c0["events"]
    cen = [n for n, e in enumerate(ev) if e[0] == "centre"]
    need(cen == list(range(cen[0], cen[0] + len(cen))), "centres are not contiguous: no single scatter cut")
    A, B, ret = [], [], []
    neg, openq, lam, nsc = set(), {}, {}, 0
    L = lambda r: lam.get(r, Fr(1))

    def co(t, s, a, b=1):                       # stored coefficient of the wanted add t += (a/b) s
        w = Fr(a, b) * L(s) / L(t)
        return [w.numerator, w.denominator]

    def o(f, s, tg, ex=()):
        return ["out", f, s, [[t] + co(t, s, a, b) for t, a, b in tg], list(ex)]

    def i(f, t, sr):
        return ["in", f, t, [[s] + co(t, s, a, b) for s, a, b in sr]]
    scat_lam = None
    for n, e in enumerate(ev):
        k = e[0]
        out = A if n < cen[0] else B
        if k in ("read0", "undo", "uninj"):
            continue
        if k == "inj":
            need(e[2] not in neg, "inj reads a negated x register")
            out.append(o(e[3], e[2], [[e[1], 1, 1]]))
        elif k == "op":
            if e[3] != 1:
                need(e[3] != 0 and e[1] >= 2 * v, "op scales a register that is not a slot (or by 0)")
                lam[e[1]] = L(e[1]) * e[3]
                nsc += 1
            out.append(o(e[5], e[2], [[e[1], e[4], 1]]))
        elif k == "centre":
            ret.append([e[2], e[1], e[3]])
            if scat_lam is None:
                scat_lam = dict(lam)
        elif k == "gread":
            hit = set(t for t, _, _ in e[3])
            out.append(o(e[2], e[1], [[v + t, a, b] for t, a, b in e[3]], [v + t for t in e[4] if t not in hit]))
        elif k == "rread":
            out.append(o(e[2], e[1], [[v + t, a, b] for t, a, b in e[3]]))
        elif k == "ysh":
            out.append(o(e[4], e[2], [[e[1], e[3], 1]]))
        elif k == "yw":
            out.append(o(e[4], e[2], [[e[1], e[3][0], e[3][1]]]))
        elif k == "kd":
            out.append(o(e[3], e[2], [[e[1], -1 if e[2] in neg else 1, 1]]))
        elif k == "ktr":
            q = tuple(e[1])
            need(e[2] == gx.KJ, "ktr matrix is not 1 - J/2")
            x1, rest = q[0], list(q[1:])
            if q not in openq:
                out.append(i(e[3], x1, [[r, 1, 1] for r in rest]))
                out.append(o(e[3], x1, [[r, -1, 2] for r in rest]))
                out.append(i(e[3], x1, [[r, 1, 1] for r in rest]))
                openq[q] = n
                neg.add(x1)
            else:
                out.append(i(e[3], x1, [[r, -1, 1] for r in rest]))
                out.append(o(e[3], x1, [[r, 1, 2] for r in rest]))
                out.append(i(e[3], x1, [[r, -1, 1] for r in rest]))
                del openq[q]
                neg.discard(x1)
        else:
            raise AssertionError("unknown event kind %r" % k)
        need(all(r >= 2 * v for r, x in lam.items() if x != 1), "an x or y register is scaled")
    need(not openq and not neg, "a K block is not closed")
    ret = sorted(ret)
    need([z[0] for z in ret] == list(range(len(ret))), "retained totals are not 0 .. n-1")
    sin, sout = Fr(*c0["scat"]["inside"]), Fr(*c0["scat"]["outside"])
    sl = [(scat_lam or {}).get(z[1], Fr(1)) for z in ret]
    if all(x == 1 for x in sl):
        scat = dict(inside=c0["scat"]["inside"], outside=c0["scat"]["outside"])
    else:
        need(len(ret) == h, "star rule with a number of totals other than h")
        scat = dict(table=[[[kk, (w * sl[kk]).numerator, (w * sl[kk]).denominator]
                            for kk in range(h) for w in [sin if c0["ports"][t] >> kk & 1 else sout]] for t in range(v)])
    ext = sorted([z[3], z[1]] for z in c0["gauge"] if z[5])
    c1 = dict(format="gcert/1", derived_from=c0["name"] + " (gcert/0; %d scalings as units, gxconv.py)" % nsc, p=c0["p"],
              h=h, v=v, R=R, cst=c0["cst"], N=c0["N"], ports=c0["ports"], frames=c0["frames"], start=c0["start"],
              final=c0["final"], ext=ext, ret=ret, scat=scat, A=A, B=B, blocks=c0["blocks"])
    return c1, nsc, sorted(set(str(x) for x in lam.values())), sum(1 for x in sl if x != 1)


if __name__ == "__main__":
    t0 = time.time()
    opt = dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a)
    c0 = gxrun.load(sys.argv[1])
    c1, nsc, lams, nsl = convert(c0)
    c1["two_hosts"] = sorted(2 * c0["v"] + i for i, hs in enumerate(c0["hosts"]) if len(hs) > 1)
    if "noext" in sys.argv and c1["ext"]:        # as gxrun.py: exterior gauges become first blocks
        for r, f in c1["ext"]:
            d = str(len(c1["frames"][f]))
            c1["start"][r] = 0
            c1["blocks"]["s"][d] = c1["blocks"]["s"].get(d, 0) + 1
            c1["N"] += int(d)
        c1["blocks"]["s"] = {k: c1["blocks"]["s"][k] for k in sorted(c1["blocks"]["s"], key=int)}
        c1["derived_from"] += ", exterior gauges turned into first blocks"
        c1["ext"] = []
    st = {}
    gx.check1(c1, scalar=True, stats=st)
    print("ACCEPTED by gx.check1: %s h=%d v=%d R=%d N=%d gates A=%d B=%d ext=%d; scalings %d, final units %s, scaled totals %d, "
          "scatter %s, stats %s (%.1fs)" % (c0["name"], c1["h"], c1["v"], c1["R"], c1["N"], len(c1["A"]), len(c1["B"]),
                                           len(c1["ext"]), nsc, lams, nsl, "table" if "table" in c1["scat"] else "star", st,
                                           time.time() - t0))
    if "out" in opt:
        gxrun.dump(c1, opt["out"])
        print("written", opt["out"])
