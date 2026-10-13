"""Recompute the cited PRs' own kappa from the (c, b) recorded in their receipts, through this package's outer assembly:
the per-supplier loop of vendor/pr510/e8-r480-nine-stage/code/assemble9.py (PR #493's six-level chain, the 47 strict
inequalities of PR #315's outer engine and four controls). Compare kappa and the binding side with each receipt, and,
where an exact-assembly receipt records them, all 47 constraint values, the six bootstrap gaps and cutoffs and the
rejected controls. This shows the cited PRs and this package compose with the same assembly; the compositions with this
package's bit c are computed by verify.sh (assemble9.py and PR #493's eleven-stage assemble.py).
usage: receipt_kappa.py PACKAGE_DIR
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

H = Path(sys.argv[1])
eng = H / "../e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/outer.py"
spec = importlib.util.spec_from_file_location("e_outer", eng)
Outer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Outer)
J = lambda p: json.loads((H / p).read_text())


def ceil(x):
    return -((-x.numerator) // x.denominator)


def assemble(c, b, charged):
    """assemble9.py's per-supplier loop, unchanged apart from taking (c, b, charged coefficient bits) as arguments."""
    eta = beta = Q(1, 10 ** 18); grid = Q(1, 10 ** 18); s = min(c, (1 - beta) * b) - Q(1, 10 ** 24)
    assert 0 < s < c and s < (1 - beta) * b
    chain = [Q(384599, 10 ** 10)]; cutoffs = []
    for j in range(6):
        old = chain[-1]; a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s); assert old < a < s < 1 - a and gap > 0
        cutoff = max(ceil(36 / gap ** 2), ceil(2 * (4 + charged) / gap))
        assert cutoff * gap ** 2 >= 36 and cutoff * gap >= 2 * (4 + charged)
        cutoffs.append(dict(gap=str(gap), cutoff_log2=str(cutoff))); chain.append(a)
    q = chain[-1] * (1 - 2 * eta); margin = (1 - eta) * q / (1 + q); ticks = margin / grid
    k = grid * ((ticks.numerator - 1) // ticks.denominator)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
              'rows': {'degree_gap': Q(10 ** 6) - Q(51 * 20161, 25)}}
    a = Outer.assembly(chain[-1], b, bridge, k, eta=eta, beta=beta)
    assert len(a['strict_constraints']) == 47 and all(x > 0 for x in a['strict_constraints'].values())
    controls = []
    for cname, kk, ee, bb in [('next_grid', k + grid, eta, beta), ('zero_eta', k, Q(0), beta),
                              ('zero_beta', k, eta, Q(0)), ('unit_beta', k, eta, Q(1))]:
        try:
            Outer.assembly(chain[-1], b, bridge, kk, eta=ee, beta=bb)
        except AssertionError:
            controls.append(cname)
        else:
            raise AssertionError(cname)
    return dict(kappa=k, binding='bit' if c < (1 - beta) * b else 'complex', strict=a['strict_constraints'],
                bootstrap=cutoffs, controls=controls)


def check(label, rec, charged_field=None):
    c, b = Q(rec["bit_lower"]), Q(rec["complex_lower"])
    charged = rec[charged_field] if charged_field else 512
    r = assemble(c, b, charged)
    assert r["kappa"] == Q(rec["kappa"]), (label, r["kappa"], rec["kappa"])
    assert r["binding"] == rec.get("binding_component", r["binding"]), (label, r["binding"])
    extra = ""
    if "strict_outer_constraints" in rec:
        mine = {n: str(v) for n, v in r["strict"].items()}
        assert mine == rec["strict_outer_constraints"], (label, "constraint values differ")
        assert r["bootstrap"] == rec["bootstrap"] and r["controls"] == rec["outer_controls"], (label, "bootstrap/controls")
        extra = "; all 47 constraint values, 6 bootstrap cutoffs and %d rejected controls equal the receipt's" % len(
            r["controls"])
    print("   %s: c %s, b %s -> kappa %s = %s (%s-bound), as in the receipt%s"
          % (label, rec["bit_lower"], rec["complex_lower"], rec["kappa"], format(float(r["kappa"]), ".18f"), r["binding"],
             extra))


check("PR #548 EXPECTED.json", J("data/complex/pr548/EXPECTED.json"))
check("PR #548 EXACT-ASSEMBLY.json", J("data/complex/pr548/EXACT-ASSEMBLY.json"), "bit_charged_two_level_coefficient_bits")
check("PR #544 EXPECTED.json", J("data/complex/pr544/EXPECTED.json"))
check("PR #544 EXACT-ASSEMBLY.json", J("data/complex/pr544/EXACT-ASSEMBLY.json"), "bit_charged_two_level_coefficient_bits")
check("PR #535 EXPECTED.json", J("data/complex/pr535/EXPECTED.json"))
check("PR #535 EXACT-ASSEMBLY-PR493.json", J("data/complex/pr535/EXACT-ASSEMBLY-PR493.json"),
      "bit_charged_three_level_coefficient_bits")
