"""Local search over the parameters of PR #370's producer (ham2) with the elimination-reuse pass inside the objective.
Not run by verify.sh: the shipped parameters (data/params/params-r740.json) are an input, and the word is rebuilt and
checked from them alone. The objective is a floating-point estimate of the compressed nine-stage saving (moment
equation s with sum n_r (r/m)^(1-s) = W, profile 72 L + 48v{7} + 32v{14, 28, 42}, m = 64, W = 64v + 9R); it only
nominates. The parameters shipped here came from 4 seeds x 6000 iterations of an earlier version of this loop, started
from PR #370's params-r865.json.
usage: python3 -I search_params.py SEED ITERS START_PARAMS.json OUT_PREFIX
Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
import ast
import json
import os
import random
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["E8COORD"] = "ham"
sys.path.insert(0, os.path.join(HERE, "..", "code", "bit", "producer"))
sys.path.insert(0, os.path.join(HERE, "..", "code", "reuse"))
import compile2 as C2  # noqa: E402
import frames as Fm  # noqa: E402
import fullword  # noqa: E402
import ham2  # noqa: E402
from ham1 import blocks, cw_lines  # noqa: E402
from reuse import reuse  # noqa: E402


def local_hist(w):
    fd = [Fm.closure(sum(1 << s for s in f))[1] if f else 0 for f in w["frames"]]
    cur = list(w["start"])
    H = Counter()

    def climb(r, f):
        if cur[r] != f:
            H[fd[f] - fd[cur[r]]] += 1
            cur[r] = f
    for ph in ("D", "A"):
        for f, d, s in w[ph]:
            for x in [d] + s:
                climb(x, f)
    for q in w["ret"]:
        H[fd[cur[q]]] += 1
    for ph in ("B", "C"):
        for f, d, s in w[ph]:
            for x in [d] + s:
                climb(x, f)
    for r in range(len(cur)):
        climb(r, w["final"][r])
    return H


def nine(w):
    v, R = w["v"], w["R"]
    m, W = 64, 64 * v + 9 * R
    prof = Counter({r: 72 * n for r, n in local_hist(w).items()})
    for r, n in ((7, 48 * v), (14, 32 * v), (28, 32 * v), (42, 32 * v)):
        prof[r] += n
    lo, hi = 0.0, 0.05
    for _ in range(100):
        s = (lo + hi) / 2
        if sum(n * (r / m) ** (1 - s) for r, n in prof.items()) < W:
            lo = s
        else:
            hi = s
    return lo


def evaluate(Pd):
    ham2.P.clear()
    ham2.P.update(Pd)
    w, _ = reuse(fullword.build(C2.compile2(ham2.build(0, True))))
    return nine(w), w["R"]


keys = []
for c in blocks:
    for t in cw_lines(c):
        keys += [(("fold", t), 2), (("l5", t), 2), (("pair", c, t), 3)]
for m in range(8):
    keys += [(("fc0", m), 7), (("fn", m), 3)]
ham2.build(0, True)
keys += [(k, 3) for k in sorted(ham2.LSKEYS)]
seed, iters, start, pref = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
Pd = {ast.literal_eval(k): v for k, v in json.load(open(start))}
rng = random.Random(seed)
t0 = time.time()
best, R = evaluate(Pd)
print("start nine %.6e R %d" % (best, R), flush=True)
for it in range(iters):
    k, n = rng.choice(keys)
    old = Pd.get(k, 0)
    Pd[k] = (old + rng.randrange(1, n)) % n
    try:
        s9, R = evaluate(Pd)
    except AssertionError:
        Pd[k] = old
        continue
    if s9 > best - 1e-12:
        if s9 > best + 1e-12:
            print(it, "improved nine %.6e R %d" % (s9, R), k, Pd[k], "%.0fs" % (time.time() - t0), flush=True)
            json.dump([[repr(a), b] for a, b in Pd.items()], open(pref + "-params.json", "w"))
        best = s9
    else:
        Pd[k] = old
print("final", best)
