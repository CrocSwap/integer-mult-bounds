"""kappa with cited complex savings when the bit side is this word in B_4 (or B_3).

The bit coarse saving c is read from certify_bit_k.py's receipt (PR #381's checker, unchanged). For every cited
complex supplier b, kappa is computed by PR #417's bootstrap.refine (chafreaky's reimplementation of rohanarun's PR #392
refined pricing tail: six fixed bootstrap levels, PR #315's outer assembly, 47 strict constraints, next grid point and
invalid parameters rejected) and must equal the value cited with b. Since c > b for every cited supplier, the result is
complex-bound and does not depend on c; it is recomputed with the best previously published bit c as a control.
usage: kappa_b4.py KAPPA.json (certify_bit_k receipt) CONTROL_C COMPLEX_B.json OUT.json
Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
import json
import os
import sys
from fractions import Fraction as Q

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tail"))
from bootstrap import refine  # noqa: E402  (PR #417, unchanged)

rec = json.load(open(sys.argv[1]))
c = Q(rec["bit_coarse"])
c0 = Q(sys.argv[2])
out = dict(K=rec["K"], m=rec["m"], bit_coarse=str(c), control_bit_coarse=str(c0), kappa={})
for s in json.load(open(sys.argv[3]))["suppliers"]:
    b = Q(s["b"])
    k, rej = refine(b, c)
    k0, _ = refine(b, c0)
    assert c > b and c0 > b and k == k0 == Q(s["kappa"]), (s["name"], str(k), s["kappa"])
    out["kappa"][s["name"]] = dict(b=str(b), kappa=str(k), kappa_float=float(k), binding="complex", rejected=rej,
                                   bit_headroom_percent=100 * float(c / b - 1), source=s["source"])
    print("   with %s b = %.12e: kappa = %s = %.15e (complex-bound, equal to the cited value and unchanged with the"
          " control bit c; bit headroom c/b - 1 = %.3f%%)" % (s["name"], float(b), k, float(k), 100 * float(c / b - 1)))
json.dump(out, open(sys.argv[4], "w"), indent=1)
