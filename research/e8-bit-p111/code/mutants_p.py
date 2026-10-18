"""Negative controls aimed at the punctured design, run through the independent checker code/xcheck_p.py.
usage: mutants_p.py XCHECK_P.py WORD.json.gz [--json OUT]
  1 drop the line read of a pseudo-target total (its single d-line): the exact replay must fail;
  2 drop one phase-A mini-node gate (a helper written at a frame that also hosts phase-B block-node gates): the exact
    replay must fail;
  3 move the last phase-A gate of a total to the full frame: legal and exact, but the total is COPYed at rank 8, so
    the decoder constant is 64, not 63 (the claim this package prices is refused);
  4 drop the receiver read of a total at p-perp (one of p's needers): the exact replay must fail.
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import copy
import gzip
import importlib.util
import json
import sys

sp = importlib.util.spec_from_file_location("xcheck_p", sys.argv[1])
X = importlib.util.module_from_spec(sp)
sp.loader.exec_module(X)
w0 = json.load(gzip.open(sys.argv[2], "rt"))
v = w0["v"]
ret = set(w0["ret"])


def dims(w):
    W = X.Word(w)
    return W.fdim


fd = dims(w0)
bframes = {g[0] for g in w0["B"] if fd[g[0]] == 4}


def evaluate(w):
    try:
        W, lab, fl, H, C, info = X.check(w)
    except X.Reject as e:
        return "rejected", "replay: %s" % e
    cst = sum(x["rank"] for x in fl["totals"])
    if not (all(H.values()) and all(C.values())):
        return "rejected", "interface"
    if cst != 63:
        return "rejected", "decoder constant %d != 63 (COPY ranks %s)" % (cst, [x["rank"] for x in fl["totals"]])
    return "accepted", "accepted"


def first(pred):
    return next(i for i, g in enumerate(w0["A"]) if pred(g))


def cmirror(w, i):
    """index in C of the literal inverse of A gate i (C = reverse of the z-destination gates of A then B)"""
    zg = [("A", k) for k, g in enumerate(w["A"]) if not (v <= g[1] < 2 * v)] + \
         [("B", k) for k, g in enumerate(w["B"]) if not (v <= g[1] < 2 * v)]
    return len(zg) - 1 - zg.index(("A", i))


def m1(w):
    i = first(lambda g: g[1] in ret and fd[g[0]] == 1)
    j = cmirror(w, i)
    del w["C"][j]
    del w["A"][i]
    return "drop the line read of a pseudo-target total (A gate %d) and its cleanup inverse" % i


def m2(w):
    i = first(lambda g: g[0] in bframes and g[1] >= 2 * v and g[1] not in ret)
    j = cmirror(w, i)
    del w["C"][j]
    del w["A"][i]
    return "drop a phase-A mini-node gate at a block frame (A gate %d) and its cleanup inverse" % i


def m3(w):
    last = {}
    for i, g in enumerate(w["A"]):
        if g[1] in ret:
            last[g[1]] = i
    i = last[w["ret"][0]]
    full = next(k for k, d in enumerate(fd) if d == 8)
    w["A"][i][0] = full
    return "a total's p-perp read moved to the full frame (A gate %d)" % i


def m4(w):
    last = {}
    for i, g in enumerate(w["A"]):
        if g[1] in ret:
            last[g[1]] = i
    i = last[w["ret"][0]]
    j = cmirror(w, i)
    w["A"][i][2] = w["A"][i][2][1:]
    w["C"][j][2] = w["C"][j][2][1:]
    return "a total drops one needer read at p-perp (A gate %d; cleanup inverse changed alike)" % i


ok = True
res = []
for m in (m1, m2, m3, m4):
    w = copy.deepcopy(w0)
    name = m(w)
    st, why = evaluate(w)
    res.append(dict(control=name, outcome=st, reason=why))
    ok &= st == "rejected"
    print("   %-9s %s :: %s" % (st.upper() if st == "rejected" else st, name, why))
base = evaluate(w0)
assert base[0] == "accepted", base
print("PASS punctured-design controls: %d/%d rejected; the shipped word passes" % (sum(r["outcome"] == "rejected" for r in res), len(res))
      if ok else "FAIL")
if "--json" in sys.argv:
    json.dump(dict(controls=res, all_rejected=ok), open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
sys.exit(0 if ok else 1)
