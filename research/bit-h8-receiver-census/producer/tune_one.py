"""Build one word (P, receivers), run PR589's generic tuner passes (tune/tune.py: transports, Steinberg 3->2,
frame reassignment on A and B to a fixed point, as apply.py --discover) and price base and tuned words.
usage: tune_one.py P RECEIVERS_JSON OUT_PREFIX"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TUNE = os.path.join(HERE, "..", "..", "imb-docking", "research", "e8-bit-p111-tuned", "tune")
sys.path.insert(0, HERE)
import one
from wordkit import save
sys.path.insert(0, TUNE)
import tune, wlib
from price import bit_kappa

P = [int(x) for x in sys.argv[1].split(",")]
sel = {int(k): v for k, v in json.loads(sys.argv[2]).items()}
out = sys.argv[3]
one.gen_p3.NODEOPT[0] = 2000
word, st = one.build(P, 552, sel)
assert word is not None, st
save(word, out + "-base.json.gz")
base = wlib.load(out + "-base.json.gz")
pb = dict(wlib.paid(base))
Tn = tune.Tuner(base, a=0.001733)
total = 0
for _ in range(6):
    n = 0
    for ch in "TSF":
        for sec in "AB":
            V = Tn.view(sec)
            ap = (tune.transport_sweep(V, verbose=False) if ch == "T" else
                  tune.steinberg_sweep(V, verbose=False) if ch == "S" else
                  tune.transport_sweep(V, verbose=False, allow_move=False))
            n += len(ap)
    total += n
    if not n:
        break
w = Tn.word()
w["C"] = wlib.rebuild_C(w)
pt = dict(wlib.paid(w))
wlib.save(w, out + "-tuned.json.gz")
res = {"P": P, "receivers": sel, "R": word["R"], "moves": total, "base_profile": pb, "tuned_profile": pt,
       "base_kappa": bit_kappa(word["R"], pb), "tuned_kappa": bit_kappa(word["R"], pt)}
print(json.dumps(res))
json.dump(res, open(out + "-result.json", "w"), indent=1)
