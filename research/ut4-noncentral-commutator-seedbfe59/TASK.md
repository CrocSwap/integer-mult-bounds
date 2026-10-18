# Cycle 3 task card: sharing two noncentral UT4 commutators

- Accepted seed: `bfe59e1502f6168422d1d522f30c3fba`
- Track: `bit-mechanisms`
- Catalogue card: `bit-new-register-model` (one selector suggestion; helper-contract was excluded as saturated R439 scope)
- Catalogue priority revision: 3
- Catalogue SHA-256: `6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075`
- Exact base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`
- Refined scope key: `bfe59e1502f6168422d1d522f30c3fba/UT4-F2/r4/noncentral-root-pair/q4`

## Object and question

Let `G=UT4(F2)`, with adjacent transvections
`x=I+E12`, `y=I+E23`, and `z=I+E34`. Put
`u=xyxy=I+E13` and `v=yzyz=I+E24`. In the full formal group algebra
`F2[G]`, can
`diag([u],[v],[1],[1])` be realized using at most four paid calls
`D_N(g)=I+([g]+[1])N`, where the paid labels are exactly `{x,y,z}` and
`N` is any rank-one idempotent in `M4(F2)`? Arbitrary dirty registers and free
scalar `GL4(F2)` mixing are allowed by normalization to per-call idempotents.
The target root elements are noncentral in `UT4(F2)`.

## Changed hypothesis and price screen

The direct word `xyxy` on role 1 and `yzyz` on role 2 costs 8 calls. In the
natural homogeneous 4-dimensional representation, each target displacement
has rank one, so the combined floor is 2. Each allowed generator displacement
and each `N` have rank one, hence a paid call changes this represented rank by
at most one. A four-call exact word would halve the direct paid-call count and
leave four calls of headroom over the optimistic floor. Charge every scalar
call one unit; no physical, helper, recursive, copying, hosting, precision,
frame, interface, or restoration price is admitted. Even a positive word would
not change kappa without a realized supplier and complete interface bill.

## Method and stopping rule

Enumerate all 120 rank-one idempotents and three labels (360 factors) in the
full 64-element group algebra. Use exact meet-in-the-middle multiplication to
exhaust all words of lengths 2, 3, and 4, with rank excluding length 1. Check
the direct 8-call positive control and omitted-call / wrong-label controls.
Stop after q=4 coverage; do not extend to q=5..8 in this cycle. A projected
matrix match alone is not a formal endpoint; any positive candidate must be
replayed in the full group algebra.

## Predecessors and overlap

- Closed PR #1333 proves the rank-sum optimum when all rank-one affine labels
  are paid. This task restricts the alphabet to three fixed generators.
- Open PR #1662 and PR #1680, plus PR #1690, concern UT4 central targets and
  workspace tariffs. This target uses the noncentral roots E13 and E24.
- Active Discussion #1738 is a three-register UT3 central pair; Discussion
  #1740 is a four-register S4 noncommuting 3-cycle pair. Neither has this
  group or these target elements.
- The helper-contract suggestion was not selected: overlap found many prior
  R439 boundary packages, and the active Discussion #1743 concerns a related
  helper-star boundary.

The live PR refresh at 08:40 UTC covered 428 open PRs with complete
pagination. GitHub GraphQL rate limiting blocked a fresh Discussion scan; the
last complete scan was 08:34 UTC (383 records). The public Discussions index
was refreshed at 08:41 UTC, and the direct #1738/#1740 pages were checked.

A GitHub claim could not be posted during the first rate-limit window, so the
local card was used while the search continued. After the API reset, the
refreshed overlap scan covered 434 open PRs and 392 Discussions with no
warnings, and the claim was posted as Discussion #1759 at 09:02:54 UTC. Its
finding and handoff were posted at 09:07:24 UTC after opening PR #1761.

## Handoff

- PR #1761 is open: https://github.com/CrocSwap/integer-mult-bounds/pull/1761
- Discussion finding update: https://github.com/CrocSwap/integer-mult-bounds/discussions/1759#discussioncomment-18920217
- The q<=4 result is complete; q=5..7 and Python 3.12 hosted replay remain
  open questions/validation obligations. No kappa or supplier claim is made.

## Expected evidence

One exact full-algebra q<=4 witness with a reproducible product certificate, or
a complete q<=4 no-witness result scoped to this alphabet and tuple. Neither
outcome excludes q=5..8 or changes the selected kappa by itself.

## Result

The exact full-algebra search found no word of length at most four. It
enumerated all 129,600 ordered two-factor products, checked all 360 possible
three-factor endpoints and all 129,600 four-factor suffixes, and independently
cross-checked all 4,096 UT4 group products against ordinary matrix
multiplication. The direct eight-call control equals the target; deleting its
last call or replacing its first x-label with z changes the endpoint.

The formal minimum is therefore between five and eight in this fixed model;
q=5..7 remain unsearched. The result does not provide a supplier or kappa.
Reproduction and the exact certificate are in README.md and certificate.json.
The GitHub claim was kept local while the Discussion API was rate-limited;
refresh and attempt the claim before the recorded expiry.
