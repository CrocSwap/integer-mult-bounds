# Direct geometric tails and adaptive compiler parameters

**Conditional κ = 0.0030266747680744.** This is a tiny increase of **3.0744 × 10⁻¹²** over PR #5387’s 0.003026674765 on exactly the same complete eight-relation paid/target profile. The useful companion result is a smaller finite compiler at the unchanged predecessor saving: tensor power 1024 → 505, logarithmic power 1000 → 484, and the sufficient exponent H in N = 2^H decreases by a factor of about 2.105. This is not a practical runtime speedup or a new native mechanism.

The new endpoint and smaller matched compiler are two distinct parameter choices. At the higher κ, the much smaller outer gap requires a larger threshold; we do not claim simultaneous improvement of both κ and H relative to the predecessor’s original parameters.

## Positive sufficient theorem

Take a fully charged finite provider with target moment T_t, paid moment P_t, B productive fields and raw ambient rank m. Let t = 1 − C, choose integer cutoffs 1 < c < b < m, and u ≥ C. Suppose rational envelopes satisfy

`α = P_t/T_t ≤ 1 − ρ`, `γ = P_(t+u)/(c^u T_t) ≤ g`, `δ = Bb/(c^C T_t) ≤ d`,

where 0 < ρ, g, d < 1. The paid product/completion/splitting theorem from zxv’s `higher-moment-strictification` bounds the complete normalized paid moment by `α^v + 2 γ^v + 2 δ^v`. Therefore the sufficient bound

`B(v) = 1/(1 + vρ) + 2 g^v + 2 d^v < 1`

certifies a strict completed moment advantage, with every split and completion charged.

Proof: `(1 − ρ)^(-v) ≥ (1 + ρ)^v ≥ 1 + vρ`, hence `α^v ≤ 1/(1 + vρ)`. Bound the other two terms by their rational envelopes. Each term of B(v) decreases with v, and B(v) tends to zero, so a finite integer v exists. Doubling followed by binary search returns the least positive integer satisfying this sufficient bound. This is not a minimum over actual native constructions, and no geometric-tail term is discarded.

For a separated unit, let θ be a valid rational exit exponent and let rational η_lower and initial_upper bound `(1−C)m^(-C)` from below and `m^C` from above. Since θ^p tends to zero and 2^p tends to infinity, a finite positive integer p satisfies `θ^p < η_lower` and `2^p > initial_upper`. The same doubling/binary method finds the least admissible p for these supplied bounds. Under the retained shifted-exit hypothesis, zxv’s logarithmic majorant then gives `L(n) ≤ n^(1−C)(1 + log₂ n)^p` for all positive integer n.

For any positive rational saving gap ε, choose s = ceil(1/ε), then an integer j with `(sj + 1)^p < 2^j`, and set H = sj. Such a j exists because exponential growth dominates polynomial growth. Since εH ≥ j, `(H+1)^p < 2^(εH)`. The function `εh log(2) − p log(1+h)` is strictly convex, vanishes at zero and is positive at H, so it is increasing and positive thereafter. Consequently the logarithmic factor is absorbed for all n ≥ 2^H. This proves a sufficient finite uniform threshold, not a minimum native program.

`strictify.py` implements these three rational searches without floating-point decisions. The completion theorem and arbitrary-positive-logarithm majorant are inherited from zxv, not newly invented here. The contribution is the reusable parameter selection and its fully checked application to this frozen supplier.

## New conditional endpoint

The complete inventory remains 64,148 paid jobs, 10,800 productive fields and rank surplus 752. The new point uses:

| Parameter | Exact choice |
|---|---:|
| Claimed κ | 0.0030266747680744 |
| Tested saving C | 0.0030266747680745 |
| Reserve ρ | 10⁻¹⁷ |
| Gamma envelope g | 957/1000 |
| Delta envelope d | 952/1000 |
| Tensor power v | 757 |
| Cutoff / completion floor | 20 / 21 |
| Tail offset u | 1/5 |
| Exit exponent θ | 63/64 |
| Logarithmic power p | 725 |
| Outer gap | 1/70,000,000,000,000,000 |
| H in N = 2^H | 3,634,890,000,000,000,000,000 |

The fixed-profile root is enclosed by `(0.0030266747680745498, 0.0030266747680745499)`. The compiler saving is strictly below that interval. Two rational interval engines check the full moments. Every source-exit, complement-capacity and initial-range inequality is checked at the new v and p. All 54 strict and four functional outer predicates pass. The old coarse `4/2^32` tail allowance fails at the new power/reserve; the direct geometric tail bound succeeds. The preceding v and p fail their respective sufficient tests.

All native costs remain charged. The scalar allowance is 158,776, route allowance 4,834,000 and complete raw nonrecursive bound 181,098,496 < 10⁹. The eight private helper pivots and eight simultaneously live snapshots are retained, as are their lost productive targets. The enormous expanded product/compiler word is specified algorithmically and not materialized.

## Matched comparison at the previous κ

Keep PR #5387’s κ = 0.003026674765, tested saving 0.003026674766 and reserve 10⁻¹² unchanged. Fresh moment/tail/capacity checks with the same rational envelopes give:

| Quantity | PR #5387 | Direct tails |
|---|---:|---:|
| Tensor power | 1024 | 505 |
| Logarithmic power | 1000 | 484 |
| H in N = 2^H | 409,549,000,000,000,000 | 194,586,000,000,000,000 |

The H reduction factor is approximately 2.10472. Since the threshold is 2^H, this is a reduction in the exponent of a sufficient threshold, not a measured speedup. No paid-profile or asymptotic κ gain is attributed to this matched comparison.

## Source binding and verification

```sh
python3 -B scripts/research_package.py --package research/geometric-tail-compiler
python3 -B scripts/check_research_commit.py --package research/geometric-tail-compiler
```

Python 3.12, standard library only. Both registered normal and optimized runs are read-only. `verify.py --write` regenerates only this package’s RESULT.json after checking the frozen native word. VENDOR.json pins exact retained files from PR #5387 commit `b1ab650d36f59e5be682a813145b7c67e219e341`; no pending Git object is required for replay. SOURCES.json pins every external runtime input on canonical main. Vendor files and all predecessors remain unchanged.

Fresh checks reconstruct the native word, all 632 forward persistent inputs, all 624 retained backward inputs, 17 owned entry fields, eight independent relations, sixteen source identities, frame/paid-rank constraints and all helper returns. They check the p16 Laurent controller and entire inventory, both interval engines, completion, finite compiler, outer predicates and predecessor-matched comparison. Invalid/inexact parameter inputs, wrong pivot signs, wrong snapshot/gauge, missing clears, corrupted ranks and invalid outer claims are rejected. The coarse-tail failure and preceding-power failures guard the parameter change. Engines are adapted from the retained predecessor implementations; no independently authored full native interpreter is claimed.

Scope remains conditional on the selected source’s native/all-size, whole-job, permitted-erasure, precision/tape, analytic, prime and exact-recovery contracts. Source phase evidence and the stronger ordinary BIT supplier are authenticated and reused. Physical tape/precision execution, full phase lowering, analytic decomposition, Lean/kernel verification, expanded word materialization, hosted CI and independent human acceptance are not supplied. Selected-result metadata is unchanged. Full-history ancestry checking is not claimed for the shallow checkout.

## Open next questions

Recent PRs #5385 and #5388 were inspected: neither claims a completed higher bound. The former repairs a reference transcription; the latter supplies funded helper queries but leaves caller integration open. Bounded saved-row-span, exact-cache and controller-parameter screens found no better paid profile in their tested families. They are discovery checks, not global impossibility claims, and are not used as proof evidence for this positive result. Discussion and literature coverage are incomplete.

The next useful application is another fully charged provider profile: supply exact rational envelopes to strictify.py, then recheck every compiler and outer condition. There is no guaranteed improvement for arbitrary suppliers. TASK.json records the concrete first step and remaining admission obligation.

## Attribution

zxv: higher-moment paid-tail theorem, logarithmic majorant and productive-helper/compiler machinery. Ali Romman: PR #5377’s helper-relation implementation and PR #5383’s eight-relation construction. Cao Yifan: PR #4610 native source, phase evidence and prior compiler tightening. Cinna Davis: PR #4470 p16 controller/helper lineage. Chris R: independent PR #5241 source admission and PR #5384 single-relation audit, neither of which automatically admits this endpoint. Jacob Alan Sussman: mixed-target recursion. Dugongue: PR #5387’s frozen compiler certificate and this adaptive direct-tail application. ToikY and all retained Clifford, native, BIT, precision and analytic contributors retain source credit. This does not claim novelty for the geometric-tail theorem, binary search or logarithmic majorants.

Prepared by Dugongue with substantial OpenAI Codex assistance, solo. Apache-2.0.
