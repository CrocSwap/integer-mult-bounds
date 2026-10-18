# Optional Mathlib-only universal lemmas

Checked with Lean 4.33.0 and Mathlibv 4.33.0 in fresh kernel subprocesses,
followed by independent axiom inspection. Every theorem uses at most
propext, Classical.choice and Quot.sound. CHECKS.json binds the exact sources.

In a compatible Mathlib checkout, run `lake env lean /path/to/Factors.lean`
and `lake env lean /path/to/Feedback.lean`. Factors proves weighted Gaussian
shifts commute and words preserve their action under permutations that retain
physical family tags; address translations commute too. Feedback proves a
sufficient contraction inequality and a reserve monotonicity inequality.

These eleven universal lemmas are useful sufficient algebraic facts. They do
not certify a particular owner table, reflect the Python computations, prove
the retained all-size compiler, or establish the multiplication bound in Lean.
No file imports a personal Mathproof module. To reproduce the full axiom
inspection, append `#print axioms` for each qualified theorem in CHECKS.json.
