# Sprint claim: CK two-sided compensation (seed 38)

- Track: complex supplier; OS-random assignment seed **38** (`secrets.randbelow(100)`).
- Start: 2026-10-13 12:01:59 UTC. Expected finish: **2026-10-13 12:42 UTC** (23:42 Melbourne).
- Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- Selected record at base: reviewed conditional PR799, kappa `0.001661634653669567`.
- Object: historical PR626 CK provider's frame-zero arbitrary-helper compensation.
- Hypothesis: after a signed target-forest transform, disjoint signed helper shears
  can reduce the complete compensation bill further. Reprice the transformed
  matrix; do not add independent savings from PR807 and PR816.
- Method: exact dyadic matrix arithmetic, a signed target forest, then a bounded
  all-ordered-helper-pair/sign census and deterministic disjoint greedy selection.
  Seed 38 diversifies forest/pair tie breaks. Charge preparation and restoration
  on both sides, literal coefficient work, source reads, and unchanged children.
- Expected deliverable: one executable finite circuit with exact replay and pins,
  or a scoped negative result if the complete budget fails. No new kappa.
- Candidates considered: X4 helper pairs (obvious follow-up to PR901); this
  two-sided CK compensation (selected); JP8 coefficient routes (crowded by
  PR793/811/837/839/882). This changes the search class, not only its seed.
- Coordination: GitHub returned zero pinned issues. Local claim used. Refreshed
  703 open PRs through #912 before claiming; read PR807/816/901/909 and relevant
  accepted ledger/review. PR807 changes helpers alone; PR816 targets alone.
  No pending source code is imported. Credit and exact predecessor pins will
  accompany the result. Delegated work stays within this compensation scope.
- Budget: at most first 8 minutes for orientation; final 10 minutes reserved
  for verification and handoff.

## Completed result (single claim update)

Completed finite circuit construction: 106 target-forest edges and 112 disjoint
helper pairs reduce the complete compensation bill from 49,624 to 11,965
component primitives. Both full orientations save 75,318 real primitives,
including 8,798 beyond the target-only forest. All 725 arbitrary input columns,
both arithmetic engines, native frame/wrapper checks, 10 new and 25 inherited
controls pass. Prefixes are 41/65 bits; denominator budgets remain 3/8 bits.
No new kappa and no claim of joint optimality or global admission.

Result: [exact receipt](EXPECTED.json), [construction proof](PROOF.md), and
[validation/handoff](VALIDATION.md). Branch: `research/complex-seed38`.
The final refresh found no pinned issue and 705 open PRs through #915; no
overlapping two-sided CK contribution was found. PR807/816 are credited as
precursors, with complete repricing rather than an additive savings claim.
