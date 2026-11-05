# Review verdict and exact source binding

**No material gap found in the least-period and exact-onset implications of PR6689 PROOF sections 2–3, under the stated arithmetic contract.** The pinned algorithm implements those formulas on a nonempty stable list/tuple of positive-job cuts containing valid, unmodified `Menu` instances. This is a source-aware written external audit, with no scientific execution or human/kernel acceptance. SHIN09-git retains theorem and implementation credit.

The complete standalone derivation is [reviews/DERIVATION.md](reviews/DERIVATION.md). The separately authored implementation trace and eight written adversarial controls are [reviews/CODE-BOUNDARY.md](reviews/CODE-BOUNDARY.md). Their immutable first-draft seals predate cross-review. Original source exposure, review roles and limits are disclosed; agreement between AI drafts is corroboration, not a substitute for the displayed argument.

## The implication chain checked

For one finite menu, let `lambda` be the minimum invocation-price density, `B` its cheapest widths, `g=gcd(W)`, `h=gcd(B)`, and `e_w=c_w-lambda*w`. For a cheapest anchor `b`, the residue graph minimizes `(loss, actual amount)` in that order. Positive widths make every nonempty cycle strictly positive in this order, including zero-loss cycles; a minimum therefore has a simple attaining path. Reachability modulo `h` or `b` is exactly the subgroup of multiples of `g`.

Projection to `h` supplies a loss lower bound. Conversely the cheapest widths generate every multiple of `h` modulo `b`, so an attaining path modulo `h` can be completed to any matching anchor residue without more loss. Thus the anchor minimum loss agrees with the `h` prediction, and its second coordinate `A_s` is the **least actual amount attaining that loss**. At amount `n` in residue `s`, equality with the predicted cost holds iff `n>=A_s`: below it, equality contradicts minimality; above it, append actual width-`b` invocations. This statement distinguishes a reachable early hole from a feasible but more expensive fill.

For separate cuts define

`D = lcm_j(g_j/gcd(g_j,q_j))`,
`P = lcm_j(h_j/gcd(h_j,q_j))`.

Outside `D` multiples both actual and predicted excess are infinite. On `D` multiples every predicted cut loss is finite and bounds actual loss below. A positive defect, including infinity, cannot cancel in an additive sum of nonnegative defects. The predicted sequence is `P`-periodic and has zeros precisely at multiples of `P`. A late zero and its shift by any eventual period `T` force `P|T`; this proves leastness even in the presence of infinite values. The normalized bill, which divides by replication, is a different sequence and is not asserted periodic.

Write `a=D*t`, `v_j=D*q_j`, `k_j=b_j/gcd(b_j,v_j)`. For each class `t=u mod k_j`, set `s=v_j*u mod b_j`. The last exception in that class is the largest **positive** integer congruent to `u` at most `floor((A_s-1)/v_j)`. The minus one excludes equality at the attained cutoff. Mathematical floor and nonnegative remainder handle negative limits; the zero class has `A_0=0` and contributes no positive exception. The maximum after this global `D` filter is `L`, or zero if there are none.

All and only global mismatches occur in that finite union. Hence `L+1` is an onset. If `L>0`, its value differs from the prediction while every shifted value `L+T` has reached the prediction for any positive eventual period `T` (necessarily a multiple of `P`). Periodicity therefore fails at `L` for every such `T`. This proves the smallest positive onset, including the stronger reading that permits a larger period. No infinity-minus-infinity operation is used.

## Literal code and caller boundary

Line numbers refer to the exact retained [pricing.py](inputs/pricing.py), blob `1c01686eca090070c10e2bbd33913d915e573f01`.

| Source location | Audited obligation |
| --- | --- |
| 18–37, `residue_table` | Exact lexicographic labels, attaining counts, stale-entry handling; one witness, without a uniqueness claim for tied count vectors. |
| 54–79, `Menu` | Positive distinct widths and rational prices; nonnegative losses; positive moduli; refined table uses anchor `b`, reusing the `h` table only when equal. |
| 95–108, `optimum` | Permanent unreachable residue is `None`; a smaller amount in a reachable residue uses exact-prefix handling instead of assuming attainment. This branch was read, not run. |
| 127 | Quotient-before-LCM expression is exactly `P`; the complete floor search is outside this review. |
| 140–153 | `accessible=D`, `step=v`, `classes=k`, residue and strict bound are exact. Since `g` divides both `v` and `b`, sampled labels cannot be `None`. Initial maximum zero discards all nonpositive class candidates. |

The low-level graph helper trusts its positive-modulus/nonnegative-weight arguments. `Menu` supplies those hypotheses. The cut functions traverse their input more than once: a one-shot generator is outside this reviewed API path, and mutated menu attributes are outside the construction invariant. This qualification is explicit rather than a claim that arbitrary iterables or forged objects are validated. The inert [checks.py](inputs/checks.py), at `direct_crosscheck`, constructs `cuts` as a list of `(q, Menu(rows))` before invoking the reviewed routines; its displayed fixtures also use lists. This is a static caller association, not execution coverage of all call sites.

Written controls cover permanent versus temporary holes, modulus one, no positive exception, exact equality, multiple cheapest widths, job scaling, lexicographic order, and invalid pricing/additivity premises. Hand deductions in the code note are **unexecuted**, and the source masking fixture remains credited source evidence. Cross-review corrects one first-draft overstatement in code note §6.2: replacing floor by truncation in the bound alone does not change the onset anywhere in this legal domain. The only negative numerator is `A_0-1=-1`; truncation gives zero and the resulting candidate is still discarded. All other numerators are nonnegative. The original draft and seal remain unchanged, and this qualification supersedes its claimed discrimination.

Nonnegative remainder is a separate requirement. As an unexecuted portability deduction, take widths `{2,3}`, prices `{2,3}`, and `q=3`. Then `D=1`, `b=2`, `k=2`; at `u=1`, `A_1=3` and the bound is zero. Python's nonnegative remainder yields candidate `-1`, correctly discarded. A remainder with the sign of the negative dividend would instead yield candidate `1`, a false exception even though the amount at replication one already attains its cheapest fill. This is a written arithmetic control, not an observed run or a defect in Python/source code. No source edit, formula correction or API repair is requested by this bounded review.

## What remains

No full Pareto/rank-12 audit or census was performed. A separate kernel development, executed certificate check, actual compatible native program and complete physical caller invoice would add different evidence. Native all-columns, ownership/erasure, adapters/chronology, compiler, precision/tape, analytic/outer budgets and every selected framework assumption remain. No full multiplication theorem, κ/frontier change, adoption or merge follows. Nick Petalas6658, Mihir4507 and the source's retained construction/compiler and classical-method lineage retain predecessor credit.
