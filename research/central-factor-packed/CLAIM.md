# Seed 93: exact central-factor verification

- Track: verification engineering; OS assignment seed **93** from
  `secrets.randbelow(100)` at 2026-10-13 14:01:44 UTC.
- Base: `47481c89fd30a43f8f882eb4b391e89c29273fd0` (`origin/main`, fetched).
- Local claim: 2026-10-13 14:05 UTC. Expected finish: 14:33 UTC
  (01:33 AEDT on October 14); final eight minutes reserved for verification
  and handoff. No pinned issue or open sprint coordination issue was present.
- Object: `scripts/experiments/complex_centers.py::verify_factor`, especially
  the historical h=26 dyadic central factor's 6,760,000 integer coefficients.
- Hypothesis/method: injectively encode complete coefficient rows in integers
  using a proved input-dependent radix, retaining every supplied gather/scatter
  entry and all original structural and scalar-charge checks. Compare the full
  original receipt and benchmark the same factor and complete historical audit.
- Deliverable: opt-in source-pinned accelerator, radix argument, differential
  and corruption controls, reproducible before/after timings, and a focused PR.
  No new kappa, construction, search or impossibility claim.

## Selection and overlap

Three candidates considered: historical scratch-pooling interval bounds,
historical disjoint-tensor frame traversal, and historical dyadic central
factor coefficient checking. The first already intersects pending
logarithm/interval accelerators #667/#672; the second would require broader
graph changes. The central factor has a small complete exact oracle,
and the original h=26 check measured 3.495 seconds on this host.
The assignment seed also fixes the alternative-basis permutations and the
64 large signed-entry cases, including first/last/random row selection and
parameter choices h=8,10,12,14. Scope diversity comes from the different
verified product, not from rerunning an existing search with a new seed.

The 717-open-PR snapshot and focused all-state/current searches were checked.
#809 changes this historical factor by a basis shear; this work changes only
verification of supplied factors. #898/#752/#778 use related exact integer
packing for other matrices. Their technique is credited, with no pending code
import. #849 changes a selected scalar replay, #818 changes R420 RREF, #921
schedules test modules, and #946 handles byte/container portability. None
reserves this coefficient verifier. Closed negative results are not reopened.

The selected base record is PR890's conditional
`1661957774647029/10^18`, with PR869/870, Hao Yan's PR858 T16 construction,
and PR589 on PR555. It was traced through `selected-result.json`, the current
status/review ledger, `community-frontier890-review.md`, and the literal T21
construction/proof. Earlier local checkout material described PR799; the new
worktree and exact-base records supersede that initial reading.

## Result

Completed: [source, proof and reproduction](README.md),
[exact timings](BENCHMARK.json), and [validation](VALIDATION.md).
The complete historical audit's median fell from 5.629786 s to 3.489217 s
(1.613481x), with byte-identical certificates in all six complete-audit timed
runs. Factor-only median improved 18.332397x. Eleven test groups pass on
Python 3.14.6 normally and under `-O`, and on Python 3.12.12. A minimal offline
relocation and selected-record integrity check pass. No kappa change.

The final complete snapshot contains 701 open PRs through #948. An immediate
pre-submission refresh also found #949's distinct factory-scale optimum.
New #947 and predecessor
#937 concern changed historical factors/shear optimality, not this verifier;
their exact heads and distinction are credited in NOTICE.md. #809/#898 heads
remain unchanged. No coordination issue is pinned. Main advanced to
`007664306fff84fbb1c9a1b4053b69f439764034`; all 43 inherited pins still match its
Git blobs and PR890 remains selected. The branch keeps its exact starting base.
The implementation was frozen before the final verification phase; no further
investigation or delegated work was launched.
