# Sprint claim — independent verification

- Assignment seed: **78**, generated once with Python `secrets.randbelow(100)`
  (operating-system randomness).
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Track: independent verification or formalization.
- Claimed at: 2026-10-13 04:36 UTC (10:06 IST).
- Expected finish: 2026-10-13 05:31 UTC (11:01 IST).
- Exact object: the 672 rational frames in the selected PR543 R420 word,
  `research/e8-bit-r420/data/bitE8mut-r420.json.gz`, source head
  `2065fe4f72a914d907f1046603f5a36f17018535`.
- Hypothesis: an independent exterior-algebra implementation can certify the
  frame ranks, orthogonal projections and root-line closures, and determine
  exactly which odd primes (if any) invalidate those finite certificates.
- Method: integer exterior products and contraction identities; no imported
  producer, row-reduction, Gram determinant, or prime-witness engine. Seed 78
  rotates the root order when selecting a spanning blade and selects adversarial
  controls. All 672 frames and all 120 root memberships per frame are covered;
  there is no adaptive search or early-success stopping rule.
- Deliverable: scoped mathematical note, self-contained exact checker, pinned
  inputs, deterministic certificate and meaningful rejecting controls. No new
  kappa or full multiplication theorem is claimed.
- Time allocation: one hour from 04:31 UTC; selection completed within the first
  20%; stop implementation by 05:16 UTC and reserve the remaining 15 minutes for
  verification, overlap refresh and a single focused PR or patch handoff.

## Selection and overlap

Three narrow candidates were considered:

1. Independent enclosure of the selected bit moment: already covered by #678;
   #706 has also just appeared for the complex moments.
2. Direct amplitude identities for selected cold wrappers: #702 already covers
   all selected four-dimensional wrappers by a different exact engine.
3. Exterior-algebra certificates for the R420 frame geometry: selected. #612
   formalizes frame-table boundaries and B-XOR interfaces; #661 optimizes fixed
   B-frame paths. Neither supplies this exterior projector/prime-specialization
   check. Newly opened #707 accelerates the existing Bareiss Gram engine on the
   same frames; this work independently checks geometry with exterior products,
   without using that engine or its adapter. It makes no performance claim.

The accepted #626/#543 certificate and actual construction/review were read,
including the conditional compiler, hosting and analytic boundaries. The PR
ledger, research integration index and archived frame-search negatives were
consulted. This is verification of a fixed object, not reopening a closed search.
The initial queue contained 523 open PRs through #704; the immediate follow-up
was refreshed through #708 at 04:35 UTC. GitHub reports no pinned issues and
Discussions disabled; the only open issue is #650 requesting Discussions.
Accordingly the claim is recorded locally, without creating a reservation issue.

Prepared for Ishan (@ishan-1729), with substantial OpenAI Codex assistance.

## Owner-directed extension within the claimed object

The owner requested ideas from `math_prime`, including Ghost Parametrization
and Ghost Properties. The bounded extension uses the same fixed R420 word:
test correctness of the target translation separately from restoration of
source/helper state, then price gifting its full-frame scalar cleanup while
retaining every frame endpoint, copy, child and hosting obligation. It does
not start a new supplier search. The owner subsequently requested multiple
GPT Astra subagents; seven bounded reviews cover frame geometry, independent
F2 replay, dirty-state compatibility, overlap, provenance, adversarial scalar
controls, and mathematical limits within the existing recursive interface.

## Result

Completed at the owner's wind-down request. No new exponent is claimed.
The exact ghost screen records rank-539 restoration debt, rank-120 source
readout drift and the helper-251 counterexample to unchanged second-call use.
Gifting all cleanup leaves the fixed recursive profile unchanged; the selected
complex supplier excludes the next recorded exponent grid tick under the
inherited framework. Ten focused tests, both receipt checks, the selected
record check and unchanged predecessor scalar/Gram checks pass.

The final overlap review found concurrent #737 had submitted the same main
exterior geometry result first. We credit Sagar Thakrar and retain that part as
independent corroboration; the ghost return/carryover evidence is central.
#710's restored-cleanup cost observation and #731's different compensation
matrix are also credited. Reviewed heads are in README.md.

Result: [reviewable contribution branch](https://github.com/ishan-1729/integer-mult-bounds/tree/research/r420-exterior-frames-seed78/research/r420-exterior-frames).
See README.md and VALIDATION.md for commands, scope, provenance and outcomes.
