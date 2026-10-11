#!/usr/bin/python3 -I
"""gxrun.py.  usage:
   nice -n 10 /usr/bin/python3 -I -B gxrun.py <gcert0.json[.gz]> [out=<gcert1.json[.gz]>] [mut] [seg=K] [noscalar]
Converts a gcert/0 file to gcert/1, checks it (gx.check1), prints the kernel-size statistics, the segment plan
for a split label check, and (mut) runs the mutation suite on the gcert/1 file."""
import sys, json, gzip, time, copy
import gxpaths
HERE = gxpaths.HERE + '/'
sys.path.insert(0, HERE)
from collections import Counter
import gx


def load(p):
    return json.load(gzip.open(p, "rt") if p.endswith(".gz") else open(p))


def dump(c, p):
    f = gzip.open(p, "wt") if p.endswith(".gz") else open(p, "w")
    json.dump(c, f, separators=(",", ":"))
    f.close()


def segments(c, K):
    """moves and blocks per segment when the gate list A ++ B is cut into K runs of about equal moves."""
    v, R = c["v"], c["R"]
    dim = [len(f) for f in c["frames"]]
    cur = list(c["start"])
    per = []
    for g in c["A"] + c["B"]:
        m = b = 0
        for r in gx.gate_regs(g)[0]:
            if cur[r] != g[1]:
                m += dim[g[1]] - dim[cur[r]]
                b += 1
                cur[r] = g[1]
        per.append((m, b))
    fm = sum(dim[c["final"][r]] - dim[cur[r]] for r in range(2 * v + R))
    fb = sum(1 for r in range(2 * v + R) if c["final"][r] != cur[r])
    tot = sum(m for m, _ in per)
    out, acc, accb, lo, k = [], 0, 0, 0, 1
    for i, (m, b) in enumerate(per):
        acc += m
        accb += b
        if acc >= tot * k / K and k < K:
            out.append((lo, i + 1, acc - sum(x[2] for x in out), accb - sum(x[3] for x in out)))
            lo, k = i + 1, k + 1
    out.append((lo, len(per), acc - sum(x[2] for x in out), accb - sum(x[3] for x in out)))
    return out, (fm, fb), len(c["A"])


def mutants(c):
    """(name, mutated certificate); every one must be REJECTED."""
    import random
    rnd = random.Random(20261009)
    v = c["v"]
    B = c["B"]

    def pick(pred, lst):
        idx = [i for i, g in enumerate(lst) if pred(g)]
        return rnd.choice(idx) if idx else None
    cls = lambda r: "x" if r < v else "y" if r < 2 * v else "s"
    is_kind = lambda a, b: (lambda g: g[0] == "out" and cls(g[2]) == a and g[3] and cls(g[3][0][0]) == b)
    out = []

    def add(name, f):
        d = copy.deepcopy(c)
        if f(d) is not False:
            out.append((name, d))

    def drop(ph, pred):
        def f(d):
            i = pick(pred, d[ph])
            if i is None:
                return False
            del d[ph][i]
        return f

    def flip(ph, pred):
        def f(d):
            i = pick(pred, d[ph])
            if i is None:
                return False
            d[ph][i][3][0][1] = -d[ph][i][3][0][1]
        return f

    def reframe(ph, pred, to):
        def f(d):
            i = pick(pred, d[ph])
            if i is None:
                return False
            d[ph][i][1] = to
        return f
    add("helper gate dropped (A)", drop("A", is_kind("s", "s")))
    add("helper gate dropped (B)", drop("B", is_kind("s", "s")))
    add("helper gate sign flipped (B)", flip("B", is_kind("s", "s")))
    add("injection dropped", drop("A", is_kind("x", "s")))
    add("slot read by y dropped", drop("B", is_kind("s", "y")))
    add("slot read by y: coefficient flipped", flip("B", is_kind("s", "y")))
    exts = set(r for r, _ in c["ext"])
    add("read of an exterior-gauged slot dropped", drop("B", lambda g: is_kind("s", "y")(g) and g[2] in exts))
    hosts2 = set(c.get("two_hosts", []))
    add("late read of a reused slot dropped", drop("B", lambda g: is_kind("s", "y")(g) and g[2] in hosts2))
    add("late read of a reused slot: coefficient flipped", flip("B", lambda g: is_kind("s", "y")(g) and g[2] in hosts2))
    add("late read with extra targets dropped", drop("B", lambda g: g[0] == "out" and len(g) > 4 and g[4]))
    add("x -> y gate dropped (K delivery)", drop("B", is_kind("x", "y")))
    add("x -> y gate sign flipped", flip("B", is_kind("x", "y")))
    add("fan-in into x dropped (K block)", drop("B", lambda g: g[0] == "in"))
    add("halving into x dropped (K block)", drop("B", is_kind("x", "x")))
    add("y reads y: one gate of a bracket dropped", drop("B", is_kind("y", "y")))
    add("y reads y: sign flipped", flip("B", is_kind("y", "y")))
    add("gate moved to the zero frame", reframe("B", is_kind("s", "s"), 0))
    add("gate moved to the full frame (later steps not nested)", reframe("A", is_kind("s", "s"), 1))
    add("slot read by y at the full frame", reframe("B", is_kind("s", "y"), 1))

    def infl(d):
        i = pick(lambda g: g[0] == "in", d["B"])
        if i is None:
            return False
        d["B"][i][3][0][1] = -d["B"][i][3][0][1]
    add("fan-in: one coefficient flipped", infl)

    def indrop(d):
        i = pick(lambda g: g[0] == "in" and len(g[3]) > 1, d["B"])
        if i is None:
            return False
        del d["B"][i][3][-1]
    add("fan-in: one source dropped", indrop)

    def scat(d):
        if "table" in d["scat"]:
            d["scat"]["table"][3][0][1] = -d["scat"]["table"][3][0][1]
        else:
            d["scat"]["inside"] = [1, 2]
    add("scatter coefficient changed", scat)

    def retf(d):
        d["ret"][0][2] = 1
    add("retained total at the wrong frame", retf)

    def ymove(d):
        i = pick(lambda g: g[0] in ("out", "in") and any(v <= r < 2 * v for r in gx.gate_regs(g)[0]) and gx.gate_regs(g)[1], d["B"])
        if i is None:
            return False
        d["A"].append(d["B"].pop(i))
    add("a gate on a y role moved before the scatter", ymove)

    def intox(d):
        i = pick(is_kind("x", "s"), d["A"])
        g = d["A"][i]
        d["A"][i] = ["out", g[1], g[3][0][0], [[g[2], 1, 1]], []]
    add("gate from a slot INTO an x role", intox)

    def ys(d):
        i = pick(is_kind("s", "y"), d["B"])
        if i is None:
            return False
        g = d["B"][i]
        d["B"][i] = ["out", g[1], g[3][0][0], [[g[2], 1, 1]], []]
    add("gate from a y role into a slot", ys)

    def frm(d):
        f = [x for x in d["frames"] if len(x) >= 2][5]
        f[0], f[1] = f[1], f[0]
    add("frame table entry not in echelon form", frm)

    def blk(d):
        k = sorted(d["blocks"]["s"])[0]
        d["blocks"]["s"][k] += 1
    add("price: one block count changed", blk)

    def fin(d):
        d["final"][2 * v] = 0
    add("a slot does not end at the full frame", fin)
    return out


if __name__ == "__main__":
    t0 = time.time()
    path = sys.argv[1]
    opt = dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a)
    c0 = load(path)
    if c0["format"] == "carrier-cert/1":
        import cc2g
        c1 = cc2g.convert_cc(c0)
        c0 = dict(name=path.split("/")[-1], events=[], v=c0["v"])
    else:
        c1 = gx.convert(c0)
        c1["two_hosts"] = sorted(2 * c0["v"] + i for i, hs in enumerate(c0["hosts"]) if len(hs) > 1)
    if "noext" in sys.argv and c1["ext"]:
        # every exterior-gauged slot starts at the zero frame instead: its first block (zero -> gauge) is paid
        # inside the invocation.  Gates, frames and scalars are unchanged; rule (2) is then not used at all.
        for r, f in c1["ext"]:
            d = str(len(c1["frames"][f]))
            c1["start"][r] = 0
            c1["blocks"]["s"][d] = c1["blocks"]["s"].get(d, 0) + 1
            c1["N"] += int(d)
        c1["blocks"]["s"] = {k: c1["blocks"]["s"][k] for k in sorted(c1["blocks"]["s"], key=int)}
        c1["derived_from"] += ", exterior gauges turned into first blocks"
        c1["ext"] = []
    st = {}
    gx.check1(c1, scalar="noscalar" not in sys.argv, stats=st)
    ev = Counter(e[0] for e in c0["events"])
    negs = sum(1 for g in c1["A"] + c1["B"] if g[0] == "neg")
    print("ACCEPTED gcert/1 of %s: h=%d v=%d R=%d N=%d frames=%d  (%.1fs)"
          % (c0["name"], c1["h"], c1["v"], c1["R"], c1["N"], len(c1["frames"]), time.time() - t0))
    print("  gcert/0 events %d %s" % (len(c0["events"]), dict(ev)))
    print("  gcert/1 gates A=%d B=%d (neg %d), exterior gauges %d, stats %s" % (len(c1["A"]), len(c1["B"]), negs, len(c1["ext"]), st))
    K = int(opt.get("seg", 3))
    sg, fin, nA = segments(c1, K)
    print("  segment plan K=%d (gate range, moves, blocks): %s; final climbs: moves %d blocks %d; scatter after gate %d"
          % (K, sg, fin[0], fin[1], nA))
    if "out" in opt:
        dump(c1, opt["out"])
        print("  written %s" % opt["out"])
    if "mut" in sys.argv:
        bad = 0
        ms = mutants(c1)
        for name, d in ms:
            try:
                gx.check1(d)
                print("  MUTANT WRONGLY ACCEPTED: %s" % name)
                bad += 1
            except AssertionError as e:
                print("  rejected: %-58s %s" % (name, str(e)[:70]))
        print("  mutants: %d, wrongly accepted: %d  (%.1fs)" % (len(ms), bad, time.time() - t0))
