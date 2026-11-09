## Result and why it matters

The exact #6937 interval at zero-based events 457..575 needs **at least
three QUERY operations** in the stated fixed q-even linear/affine rewrite
model, even with arbitrary finite helpers, copies and erasures. The public
three-query replacement already attains this count. This rules out reducing
that specific interval to two queries while preserving its full independent
input/output boundary and the charged-operation contract.

The proof evaluates the actual source at q=+1 and q=-1, D9=1. A response
minor on rows/columns 0,1,19 has determinant 8. The classical telescoping
identity bounds response rank by the number of rank-one charged operations,
without requiring invertible helpers or free maps. A forward full-state
rational engine and separately coded reverse-covector engine recover the
same exact certificate.

## Sources, novelty and complete scope

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Original #6937 source: `a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`.
The matching construction is the [published QUERY-only package](https://github.com/CubeJerry/integer-mult-bounds/tree/617903497387a98f7ca929ad0b6928dd32abffec/research/p104-query-only-interval),
which is retained unchanged and credited. The lower bound is new for this
pinned source/model; neither the three-query construction nor the general
rank method is claimed as new. `OVERLAP.md` distinguishes earlier
query-information, affine-tag and #6825/#6800 rank-factorization scopes.

The theorem requires lawful evaluations, regular free denominators,
independent inputs, identical free initialization/output extraction at both
signs and rank-one full-state charged queries. It excludes free odd-q side
information, nonlinear/adaptive coefficients, unpriced wider payloads and
changed endpoints. No complete-caller, native-rank or multiplication lower
bound follows. Existing helper, arithmetic, storage, source access,
precision and compiler costs are not waived or repriced.

## Reproduction and verification

```sh
python3 -I -B research/p104-query-interval-optimum/verify.py
python3 -I -B research/p104-query-interval-optimum/review/check_covectors.py research/p104-query-interval-optimum
python3 -B scripts/research_package.py --package research/p104-query-interval-optimum
python3 -B scripts/check_research_commit.py --package research/p104-query-interval-optimum --check-modes
```

The registered commands include normal and optimized Python executions.
Expected response rank is 3, determinant 8 and 55 nonzero response entries.
Each of six deleted charged-site controls loses rank three. Both complete
source words and the predecessor proof are byte authenticated. The finite
two-point attainment check is not substituted for the predecessor's full
formal identity proof. Universal candidate-rewrite exclusion is the written
telescoping argument, not a finite circuit search.

## Status, limitations and credit

**No new kappa.** This is a rigorous scoped negative result and verification
advance. The accepted bound remains conditional on the five framework
assumptions; no selected artifact changes. Whole-caller rearrangements,
proved reachable subspaces or additional operator relations remain open.

Prepared for @CubeJerry with substantial OpenAI assistance in proof, source
audit, exact checks, separate AI review and packaging. The #6937 authors,
the prior public QUERY-only package and cited query/rank contributors keep
their credit. No independent human or proof-kernel acceptance is claimed.
