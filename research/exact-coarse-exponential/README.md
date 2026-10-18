# Exact integer evaluation of the coarse exponential

This opt-in adapter evaluates the retained 24-degree exponential polynomial and geometric tail over one integer denominator. It returns **exactly the original dyadic interval**. It eliminates large intermediate Fraction normalizations; it does not change degree, precision, tail, moment weights, surcharge or logarithms.

The previous PR2044/PR2161 replay exposed this computation at a 30000-digit endpoint. This package starts from refreshed canonical main, and pins the same ordinary engine source. It does not edit that frozen engine or any selected certificate. No new kappa, complete supplier admission or whole-repository green result is claimed.

Run `python3 -B research/exact-coarse-exponential/verify.py` for the short gate. The registered research-package hook also reruns the 30000-digit original-oracle comparison and compares its committed evidence without writing artifacts. The replay checks 96 exponential cases against both the unmodified source and a separate literal sum, 24 whole-moment cases (including 1000-digit endpoints), and eight rejection controls. BENCHMARK-30000.json records an actual unmodified-oracle comparison at 30000 digits; it is not a fabricated receipt or cache hit. The slow comparison can be repeated with `benchmark.py --digits 30000 --out OUTPUT_FILE`. Machine timing and hardware details are excluded from public artifacts.

Use `integer_exp.exponential(lower, upper, engine.DYAD)` directly, or `integer_exp.moment(engine, H, m, W, endpoint, bad)` with the unchanged original engine. Default frozen callers are unchanged. PROOF.md derives the common-denominator identity for every supported rational input.

Credit Douglas Colkitt and the retained PR547/548/559, ordinary-cost, mixed-supplier and T74 engine lineage; PR2044 and PR2161 supply the observed high-precision replay context. Source notices and attribution remain intact. Prepared under dataisfire with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

Integrate the exact adapter through a separately pinned caller derivation, and compare every affected admission and rejection receipt with the baseline. This package closes the arithmetic-equivalence step and leaves that default integration separate.
