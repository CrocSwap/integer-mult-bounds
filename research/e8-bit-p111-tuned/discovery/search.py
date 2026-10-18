# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Search of the plan_thirds seed (free-keeper lines and their (z,z) D6 assignment) and of the receiver choices of the
pseudo-target totals for the smallest R of the punctured word with a given P (not run by verify.sh; the shipped
parameters, data/punct.json, are seed 552 with the listed receivers, R = 439, found in seeds 0..1700 with 3-6 receiver
draws per seed).  usage: python -I discovery/search.py P SEED0 SEED1 TRIES"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import gen_p3  # noqa: E402
from geom import Geom  # noqa: E402
from planio import load_plan  # noqa: E402

gen_p3.NODEOPT[0] = 1          # block-node realisation effort does not change R
P = sorted(int(x) for x in sys.argv[1].split(","))
G = Geom()
sol = load_plan(os.path.join(HERE, "..", "data", "plan-l3.json"))
best = None
for seed in range(int(sys.argv[2]), int(sys.argv[3])):
    pt = gen_p3.plan_thirds(G, sol, random.Random(seed))
    if pt[0] == "failed":
        continue
    freeline, assign = pt
    rr = random.Random(1000 + seed)
    for trial in range(int(sys.argv[4])):
        sel = None if trial == 0 else {p: rr.choice((1, 2, 3)) for p in P}
        extras, res = {}, None
        for _ in range(20):
            try:
                res = gen_p3.build(G, sol, P, freeline, assign, extras=extras, verbose=False, rcvsel=sel)
            except AssertionError as e:
                res = ("err", str(e)[:80])
                break
            if res[0] == "missing":
                for B, ls in res[1].items():
                    extras[B] = sorted(set(extras.get(B, [])) | set(ls))
                continue
            break
        if res[0] in ("err", "missing"):
            continue
        R = res[1]["R"]
        if best is None or R < best[0]:
            best = (R, seed, sel)
            print("seed", seed, "trial", trial, "R", R, res[1]["stats"], "receivers", sel, flush=True)
print("best", best)
