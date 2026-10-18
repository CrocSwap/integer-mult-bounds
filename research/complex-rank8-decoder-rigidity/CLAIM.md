# Local sprint claim (no pinned coordination issue exists)

- Recorded: 2026-10-13T17:00Z; result recorded 2026-10-13 evening (UTC).
- Track: 40–49, structural decoder research. Assignment seed **47**, drawn once with
  `python3 -c "import secrets; print(secrets.randbelow(100))"` (OS randomness) at 2026-10-13T16:59:56Z.
- Start commit: `2921874911956718fcaaaf9396fe8267b3cfa9f0` (main at 17:00Z, selected κ 0.001661960547713947, PR942,
  complex side binds). Rebased before submission onto main `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe` (selected κ 0.001672660197076918, PR1094);
  the package is additive and its statements do not depend on the selected record.
- Object: rank-8 decoders in PR717's E-graph-only copy-cost model (D1(a)) on P112: is every rank-8 real
  matrix with K_ii = 4 and K_ij = 0 on orthogonal root pairs diagonally gauge-equivalent to 2G? This is the
  step PR717 D1(b) records as ARGUED (local rigidity D1(d) plus a sampled global search), and the model
  PR968 lists as not covered.
- Method: pivot reduction on a live frame; D4-block / S(3,4,8) structure; propositional zero-exclusion with a
  shipped DRUP refutation replayed by an independent RUP checker; exact algebra for the class and gluing
  lemmas; exact rational checks of the corollary; numerical random-start probes as non-proof evidence.
- Candidates considered and not chosen: (1) the n ≥ 9 mixed-β floor on P112 (PR717 open problem; SAT/CP-SAT
  attempts recorded as killed; too risky for the window); (2) k = 2 labellings of punctured in-cap graphs in
  dimension ≤ 17 (PR446 §6.2 covers only the full graph; value for the construction unclear);
  (3) realization pricing of PR968's asymmetric centres (requires the complex word compiler; PR717 recorded
  the price without shipping it).
- Expected deliverable: research note / scoped structural result with a written proof and an exact
  verifier. No κ claim.
- Expected finish: same day (hard stop 2026-10-13 23:01 UTC).

## Result

- Delivered as `research/complex-rank8-decoder-rigidity/` (research note / scoped structural result, no κ claim).
- Theorem: on P112 and P120 every rank-≤8 solution of the E-graph system is D(2G)D^{-1}. Corollary: eight
  costly terms in the E-graph model have PR968 normal-form supports, hence cst ≥ 64 (P112) / 72 (P120).
- Extension (same PR, second commit batch): the theorem transfers to the 336 P104 units of type (2,2,2,2)
  (cst ≥ 56); zero exclusion holds on P111 and all 1260 P104 units; the missing proof input for the other
  P104 types and P111 is recorded.
- Reproduce: `python3 -I -B research/complex-rank8-decoder-rigidity/verify.py` (and `--live P120`), about 10 s CPU (up to ~30 s wall) each; 61 checks on P112, 41 on P120.
- Overlap re-checked against the PR list (through #1210) and the discussion board before submission; the concurrent
  #1191 (one-sided mask rigidity, any term count) and #1180 (all-pairs, both factors root-linear) are complementary,
  not duplicates; see README.
- Submitted: https://github.com/CrocSwap/integer-mult-bounds/pull/1212 (status: research note / scoped structural result, no κ claim).
