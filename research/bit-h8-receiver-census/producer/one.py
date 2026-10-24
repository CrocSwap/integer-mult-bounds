"""Build one punctured L3 word (gen_p3 of PR555/PR589), export its records and price it with tools/price.py."""
import os, sys, random, json, struct, subprocess, tempfile, time
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "repo", "research", "e8-bit-p111")
sys.path.insert(0, os.path.join(PKG, "code"))
sys.path.insert(0, HERE)
import gen_p3
from geom import Geom
from planio import load_plan
from wordkit import save
from price import bit_kappa

PLAN = os.path.join(PKG, "data", "plan-l3.json")
EXPORT = os.path.join(PKG, "..", "e8-bit-carrier-skeleton", "code", "bit", "export_records.py")
_G = _sol = None
_pt = {}


def setup(seed):
    global _G, _sol
    if _G is None:
        _G = Geom()
        _sol = load_plan(PLAN)
    if seed not in _pt:
        _pt[seed] = gen_p3.plan_thirds(_G, _sol, random.Random(seed))
    return _G, _sol, _pt[seed]


def build(P, seed, rcvsel=None, node_seed=0):
    G, sol, pt = setup(seed)
    if pt[0] == "failed":
        return None, "plan_failed"
    freeline, assign = pt
    extras, res = {}, None
    for _ in range(20):
        try:
            res = gen_p3.build(G, sol, sorted(P), freeline, assign, extras=extras, node_seed=node_seed,
                               verbose=False, rcvsel=rcvsel)
        except AssertionError as e:
            return None, "assert:" + str(e)[:100]
        if res[0] == "missing":
            for B, ls in res[1].items():
                extras[B] = sorted(set(extras.get(B, [])) | set(ls))
            continue
        break
    if res[0] == "missing":
        return None, "missing"
    return res[1], "ok"


def profile(word):
    with tempfile.TemporaryDirectory() as d:
        wp = os.path.join(d, "w.json.gz")
        save(word, wp)
        subprocess.run([sys.executable, "-I", "-B", EXPORT, wp, os.path.join(d, "rec")], check=True,
                       stdout=subprocess.DEVNULL)
        raw = open(os.path.join(d, "rec", "249-records.bin"), "rb").read()
    h = Counter()
    for t in struct.iter_unpack("<6i", raw):
        if t[0] == 0 and t[4] > 0:
            h[t[4]] += 1
        elif t[0] == 2:
            h[t[5]] += 1
    return dict(sorted(h.items()))


def evaluate(P, seed, rcvsel=None, nodeopt=2000):
    gen_p3.NODEOPT[0] = nodeopt
    t0 = time.time()
    word, st = build(P, seed, rcvsel)
    if word is None:
        return {"P": sorted(P), "seed": seed, "status": st, "sec": round(time.time() - t0, 2)}
    prof = profile(word)
    return {"P": sorted(P), "seed": seed, "status": "ok", "R": word["R"], "v": word["v"], "stats": word["stats"],
            "profile": prof, "mass": sum(r * n for r, n in prof.items()),
            "kappa": bit_kappa(word["R"], prof, ports=word["v"]), "sec": round(time.time() - t0, 2)}


if __name__ == "__main__":
    P = [int(x) for x in sys.argv[1].split(",")]
    seed = int(sys.argv[2]); nodeopt = int(sys.argv[3])
    sel = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
    if sel: sel = {int(k): v for k, v in sel.items()}
    print(json.dumps(evaluate(P, seed, sel, nodeopt)))
