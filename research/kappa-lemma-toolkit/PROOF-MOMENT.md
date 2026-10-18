# Paid-profile and real-moment transfer

`MomentTransfer.lean` proves 25 reusable lemmas in `IntegerMultBounds.MomentTransfer`. It imports Mathlib only. The principal result is universal: every finite batch of concentration moves satisfying `0 ≤ dᵢ ≤ aᵢ ≤ bᵢ` preserves a strict power-moment budget for every real exponent `0 ≤ p ≤ 1`. No search result, physical gadget, or numerical oracle is assumed.

For the project's saving parameter use `p = 1 - saving`. The normalized theorem applies directly to ranks divided by a positive label dimension. The scaled theorem permits a nonnegative cover/wire normalizer. For example, replacing residual ranks `(7,39)` by `(6,40)` cannot increase their normalized moment at any exponent in this range. This example concerns the moment objective; a proposed owner reassignment must separately satisfy the physical-family, chronology, chart, and stock rules.

The substantive analytic step is `concave_concentration`. For any concave nonnegative-domain cost, it proves

`f(a-d) + f(b+d) ≤ f(a) + f(b)` whenever `0 ≤ d ≤ a ≤ b`.

The proof constructs two explicit convex combinations of the endpoints `a-d` and `b+d`. Their coefficient sums and interpolation identities are proved exactly, and adding the two concavity inequalities yields the result. Applying Mathlib's `Real.concaveOn_rpow` gives the power-cost theorem, including a zero-rank endpoint. `batch_rpow_concentration` and `admission_of_batch_concentration` lift locally checked moves to arbitrary finite batches and a strict total budget.

The profile layer treats a finite signed profile algebraically through `weighted s counts cost`. `replacement_identity` proves the exact change caused by subtracting a removed subprofile and inserting an added one. `replacement_nonneg` supplies sufficient conditions for nonnegative resulting counts. `admission_of_replacement` transfers strict admission whenever added cost is at most removed cost. `admission_with_reserve` allows an explicitly charged new reserve when the old strict margin plus the move's saving pays for it. `conserved_weight_of_replacement` yields stock conservation by choosing unit weights and rank-mass conservation by choosing rank weights; `deficit_preserved` then preserves the rank deficit at fixed capacity. The separate two-bin rank-mass and deficit lemmas are exact identities.

`rational_upper_certificate` is the real/rational bridge: nonnegative rational counts, pointwise rational upper bounds on real costs, and one strict rational weighted-sum inequality imply a strict real weighted-sum inequality. The finite rational inequality can be discharged by kernel computation or exact arithmetic. The theorem does not assume that a floating-point approximation is an upper bound. `normalized_admission` converts a strict sum bound into moment `< 1` using a positive denominator.

Discovery searched all five registered source catalogs and the shared DAG's source overlay. Relevant prior project material included the public Round13 finite rational moment checker and the earlier KappaCheck exponent certificate. Those have different scopes; their finite Boolean results are not presented as real analytic upper bounds. The checked dependency reused here is Mathlib's real-power concavity theorem. No personal Lean module is required by this contribution. Source-only retrieval results were treated as nominations until the final Lean checks.

These lemmas certify moment comparisons and sufficient admission transfers. They do not construct a physical owner assignment, establish the project's all-size compiler or tape/precision bounds, or prove an unconditional multiplication exponent. A concrete improvement must combine them with the independently checked construction and inherited project hypotheses.
