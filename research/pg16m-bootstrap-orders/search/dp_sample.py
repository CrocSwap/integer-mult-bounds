import json, random
from math import gcd
import numpy as np
from merge_dp import tables, dp, N
from core import load
nbr = load("graph16_59.txt")
Dp = np.array(sorted(int(x) - N for x in nbr[0]), np.int64)
units = [u for u in range(1, N) if gcd(u, N) == 1]
rng = random.Random(20261016)
trip = [(118, 118, 81), (118, 118, 199), (118, 118, 236), (155, 155, 81), (155, 155, 199), (155, 155, 236), (118, 155, 81)] + [(rng.choice(units), rng.choice(units), rng.randrange(N)) for _ in range(40)]
out = []
for mp, ml, c in trip:
    cP, cL = tables(Dp, mp, ml, c)
    out.append(dict(mp=mp, ml=ml, c=c, value=int(dp(cP, cL)[N, N])))
json.dump(out, open("dp_sample.json", "w"))
print(out[:5], min(o["value"] for o in out[3:]))
