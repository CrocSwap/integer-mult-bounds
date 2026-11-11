# One internal gap misses the five-map g=13, q=8 paired star

**Proof, for one schedule.** In the paired-star contract, put every thin
map between the two halves of stage 0, in either order, and run stages 1
through 12 as adjacent pairs with no further thin maps. If the off-diagonal
block B is nonzero, the normalized coefficient is not I. Its block from
leaf t into leaf 0 equals `(D_0+1) D_t^{-1} B`.

At g = 13 and q = 8 the five rank-8 maps forced by setting every D_j = 1
sum to that unique matrix and fail. Both half orders were evaluated at two
GF(16) points with D_0 ≠ 1. The pure product is still the target. The
failure is the coefficient of e.

Selected κ stays `781451/250000000`. This is not a native caller and not a
change to the selected frontier.

The argument and the limits are in [PROOF.md](PROOF.md). The evidence class
is a proof under the pattern and the legal-pair hypotheses, with exact
finite corroboration. It is not an exhaustive census of interleavings, and
a failure on this pattern is not unrestricted nonexistence of an
interleaved word.

## Scope and evidence

Original card: `joint-query-controller`. Scope status: **refined**. The card
asks whether a changed query demand removes real work. The assigned
question is the interleaved remainder of open PR #7010: one declared
pattern that separates at least one stage's halves, the thin maps forced
by every D_j = 1, and the normalized coefficient at two field points
before any native bill. The pattern fixed here is the first-stage internal
gap.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 781451/250000000. This package uses
that record and edits neither file.

Five rank-8 maps have total rank 40, which is the chronological floor at
g = 13, q = 8. The floor does not forbid them. The adjacent-halves theorem
does not apply, because a thin map stands between the halves of stage 0.
The commuting-projector theorem already excludes five maps when B = 0; the
new hypothesis is B ≠ 0.

Overlap was refreshed on 2026-11-10 against open upstream PRs and
discussions (`python3 scripts/find_overlap.py --refresh`). The nearest
records are:

- Open PR #7010, head `32999d634cdd718ce6fb77648f54e4e674d7f395`, proves the
  adjacent-halves count and leaves an interleaved word open. That open
  question is the source of this pattern. Its canonical note is discussion
  #5593, comment 19507682, with the handoff pointer on #1166, comment
  19507683.
- Open PR #7005, head `1750566c34c9fb117dc4afc4ce2bdacca7da036b`, proves the
  consecutive rank bound at g = 31, q = 26. Its internal-gap question is
  that other profile. This package does not answer it.
- The g = 3 censuses in PR #6922, PR #6940, PR #6956, and open PR #7011
  fix three leaves. They do not lift to thirteen leaves or eight ports.

No open PR in that snapshot proves or exhibits this first-stage internal
gap at g = 13, q = 8. Source commits, Git blobs, and SHA256 pins are in
[SOURCES.json](SOURCES.json). The selected record, the catalogue, and the
paired-star contract are historical provenance.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-g13-q8-internal-gap
```

The registered replay runs `verify.py` twice, once with `-O`. Both print
`PASS_PAIRED_STAR_G13_Q8_INTERNAL_GAP`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/paired-star-g13-q8-internal-gap/verify.py
```

The g = 13 identity is the block calculation in `PROOF.md`. The two field
points check that the updater matches it. They are not an interpolation on
thirteen variables.

## Open next questions

- Can one of the five rank-8 maps sit in the gap after stage 0 and cancel
  the leaf-0←leaf-1 block, while the sum at every D_j = 1 stays the same
  swap? This package puts every thin map in one internal gap. A map in the
  next gap is scaled only by completed stage factors, so its leaf-to-leaf
  block carries a different monomial. The first step is to subtract a
  rank-8 matrix supported on the two leaf-0/leaf-1 blocks of B from the
  internal sum, add that matrix after stage 0, and recompute the block at
  D = (2, 3, ..., 14). Nothing external blocks that calculation.
- Does the same block stay nonzero when stage 0 is not first, so an
  earlier adjacent stage has already scaled the state? The scalar prefix
  here is trivial. The first step is to complete stage 1, open stage 0
  around the same five maps, and read the leaf-0←leaf-2 block at one point
  with D_1 ≠ 1. Nothing external blocks that calculation.

A full call of another stage between the halves, and the g = 31, q = 26
internal gap, are different questions. This note does not search them.

## Credit

The paired-star contract, the rank floor, and the commuting map-count are
from PR #5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617.
The adjacent-halves count that leaves this pattern open is PR #7010. The
consecutive rank bound at the other profile is PR #7005.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent
human review and a proof-assistant proof are unclaimed.
