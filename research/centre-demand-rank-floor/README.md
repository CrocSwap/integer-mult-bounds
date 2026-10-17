# Copied-information floor of the selected centre path

**Scoped exact obstruction for the `centre-path-sharing` card, hard-search reading
of its lower-bound method ("prove a lower bound on copied information per call for
the selected decoder contract"). No shared centre is constructed, no endpoint is
changed, and no kappa, supplier admission or frontier change is claimed.**

The card asks whether the 64-per-call centre path (eight rank-8 COPY/ERASE totals
through the private temporary) can be shared across calls or shrunk. This package
settles the smallest instance of the **shrunk** half for the pinned selected
decoder contract: the eight totals are independent at the consumer, so the copied
information per call cannot drop below eight independent totals without changing
what the consumer requests. The **shared** half is resolved at the demand level
and its remaining physical datum is recorded exactly.

## The pinned centre path, as bytes

Everything is recomputed from one frozen member of the selected replay archive:
`candidate/strict/global/base/split-centres/GLOBAL-TEMPLATE.json.gz` inside
[the selected replay](../community-frontier1094-audit/selected-replay.tar.gz).
Both orientations (`local_programs.forward`, `local_programs.backward`) parse to
the same structure:

- the centre phase is exactly 256 macros: eight blocks of 32;
- per centre `k`: a CLEAR of private scratch `C_k`, one COPY/ERASE total, one
  rank-8 `center` ascent at frame `414+k`, and exactly 28 fanout (forward) or
  gather (backward) scalar events at coefficients `+1/4` or `-1/4`;
- the eight source rows are `S = (229, 224, 227, 225, 243, 241, 259, 257)`, the
  scratch roles `C_0..C_7` sit in the private namespace `[23408, 23416)`, and the
  consumer rows are exactly `112..223` (112 rows, 28 per total, overlapping
  between totals);
- centres 0 and 4 fan out with all `+1/4`; the other six use mixed signs.

## Result 1: the eight totals are demand-independent (exact)

Let `D` be the `112 x 8` consumer demand matrix: `D[r,k]` is the coefficient with
which total `k` enters consumer row `r`. Over the rationals:

- `rank(D) = 8`, both by exact Gaussian elimination and by the explicit nonzero
  minor on rows `(112, 117, 118, 120, 113, 116, 115, 123)`, whose determinant is
  exactly `-1/16384` (that is `-1` after scaling by `4^8`);
- the backward gather matrix equals the forward fanout matrix entry for entry,
  so the pinned forward/backward pair is an exact adjoint pair on this demand.

Consequence: the pinned consumer endpoint determines all eight totals
independently. Any replacement copied-total contract that delivers the same
endpoint must move at least eight independent scalar totals per call; merging
totals is impossible, and a rank-deficient demand would be a different endpoint.
With the per-total pairing-rank floor of eight for root-code factors
([`p112-batch-centre-floor`](../p112-batch-centre-floor/README.md) and its
credited predecessors, PR845/PR1098/PR1180), the charged `8 x 8 = 64` per call is
rank-forced. The centre path cannot be **shrunk** under the pinned endpoint; the
only escape is a cheaper per-total pairing rank (outside-code factors, an open
question) or a changed endpoint.

This is the bridge the lever screen lacks: the favourable relaxations "centre
path free" (2.80x) and "shared by two calls" (1.90x) in
[`complex-local-word-ceiling`](../complex-local-word-ceiling/README.md) assume
away charges that the pinned contract's demand actually forces.

## Result 2: the sharing half, demand level and the recorded physical datum

The selected record's 144 calls (80 forward, 64 backward; 16 calls per stage over
nine stages) each carry their own centre block in their own call-local space, and
the pinned replica lift declares a direct-sum instantiation ("direct sum of data
and dedicated banks; share only restored private streams"). For any k-call
window the requested matrix is therefore block diagonal in disjoint variables:
the coupling matrix is `C = I_k`, and the `64 rank(C)` law of
[`p112-batch-centre-floor`](../p112-batch-centre-floor/README.md) gives the floor
`64k`. Sharing one centre path across calls is admissible only if the consumer
requests a lower-rank combination (for the pinned two-panel shared-sink contract,
`C` is all-ones and both panels request the image of the sum): that is a
different endpoint, exactly as the floor package records.

The remaining datum is physical, not algebraic: which calls, if any, literally
share sink rows, return operator and chart within one uninterrupted window. This
package could not decode it from the pinned owner nominations: the `owners` maps
carry the centre source rows in only 16 of 1,152 lookups, and the data-row
instantiation lives in `route_semantics` (`cover class d*rho(stage,port)`). No
eligible pair is exhibited and none is excluded at the physical level; the exact
missing map is named in TASK.json's open questions.

## Acceptance-gate statement

There is no changed centre charge or copy profile to price: the profile remains
eight rank-8 totals per call and the comparison ceiling is the unchanged baseline
`a < 0.001690054109089` (the card's positive control,
[`complex-local-word-ceiling`](../complex-local-word-ceiling/README.md), is run
as a registered command). Charging nothing for restoration, hosting or precision
is not needed to state the floor: those charges only make the unchanged profile
more expensive, never cheaper.

## Scope and limits

- The floor holds for the pinned selected decoder contract (the split-centres
  global template of the frozen selected replay) and its literal consumer
  endpoint. Changed endpoints, changed alphabets and outside-code factors are
  outside it.
- The per-total pairing-rank-eight factor is inherited from the root-code floor
  of `p112-batch-centre-floor` (credited); this package does not reprove it and
  does not price outside-code terms.
- The demand rank is a statement about linear information at the consumer, not a
  physical circuit, tape, precision or hosting claim. No selected cold replay is
  run; the frozen archive is read-only.
- No kappa, supplier admission, eligible window or frontier change is claimed.

## Reproduce

Python 3.12 and its standard library only. From the repository root:

```sh
python3.12 -B research/centre-demand-rank-floor/verify.py
python3.12 scripts/research_package.py --package research/centre-demand-rank-floor
```

Expected first output:
`PASS_CENTRE_DEMAND_RANK_FLOOR demand_rank 8 totals 8 consumer_rows 112 minor_det -1/16384 calls 144 owner_lookups_missing 1136 no_new_kappa`.
`verify.py --write` regenerates `RESULT.json`; the normal run requires the
committed file to equal the recomputation byte for byte. Four rejection controls
are enforced: a zeroed demand column and a merged column pair each drop the rank
below eight, a fanout sign flip fails gather equality, and a source-row swap
fails the pinned source tuple.

## Open next questions

- **Decode the physical instantiation of the centre source rows** across the 144
  calls via `route_semantics` (`cover class d*rho(stage,port)`), then compare the
  eight source rows of every call pair at k = 2. This is the eligibility blocker
  for the sharing half.
- **A cheaper per-total pairing rank** (outside-code overcomplete factors) would
  shrink the charge without changing the endpoint; test one specified family by
  exact full-matrix replay, following `p112-batch-centre-floor`'s first open
  question. Failed search is not exclusion.
- **A rank-deficient caller demand** would allow a reduced copied-total contract
  at the price of a different endpoint; derive one realized caller with a
  complete paid restoration, hosting and precision bill.

## Credit

The packing-ceiling model, the lever table and the coverage identity are Douglas
Colkitt's [`complex-local-word-ceiling`](../complex-local-word-ceiling/README.md)
(PR1012). The coupling-rank law and its `64 rank(C)` floor are
[`p112-batch-centre-floor`](../p112-batch-centre-floor/README.md) (prepared for
alephnan with OpenAI Codex assistance); the one-call support census is Mihir
Srivastava's PR845, independently corroborated by Adam Gall's PR1098, and the
one-call factor-linear floor is woklerx's PR1180. The pinned two-panel
shared-sink contract is ToikY's
[`centre-shared-return-guard`](../centre-shared-return-guard/README.md), built on
1337isnot1337's PR1708 and ToikY's PR1748; the k-call charged relaxation is
[PR 3075](https://github.com/CrocSwap/integer-mult-bounds/pull/3075) (Aaron Wang
with help from opencode). The frozen selected replay and the selected
construction lineage (PR1094 and its recorded predecessors) are unchanged.
Prepared by Aaron Wang with help from opencode (substantial AI assistance; no
model named; no independent human review claimed). New work is Apache-2.0.
