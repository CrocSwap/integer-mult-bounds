# Two constant thin maps miss one g=5 paired-star word

**No new kappa.** At q=1, for one fixed legal pair with nonzero off-diagonal
block B, two constant thin maps do not meet the paired-star endpoint on the
stage order 0, 1, 2, 3, 4. That includes every placement in which a thin
map sits between a stage's two halves. A foreign full call between those
halves misses the pure factor for every longer word that uses this same
pair on every stage. One mixed order that separates a diagonal stage and
keeps the pure factor is inconsistent for two maps as well. The three-map
word on the same stage order still meets the endpoint. Selected κ stays
363005817/100000000000.

This is the first step left open by
[PR #7090](https://github.com/CrocSwap/integer-mult-bounds/pull/7090):
q=1, one fixed legal pair, and one order that separates a stage, solved by
the specialization formula from the three-leaf census. It is not the
five-map question at g=13 or g=31, and it does not re-prove the one-map
theorem or the adjacent-halves count.

The statement, the two-stage quotient, and the limits are in
[PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
caller or query demand removes real work. This package refines that to the
paired-star map count at g=5: whether two constant thin maps, one fewer
than ceil(g/2), meet the endpoint for the named first step. It is not a
caller, a native bill, or a change of kappa. Source commits, Git blobs and
SHA256 pins are in [SOURCES.json](SOURCES.json). The catalogue is pinned
as provenance. The selected record is a declared input: the verifier
requires its kappa to stay 363005817/100000000000.

Evidence class: **proof** under the hypotheses in [PROOF.md](PROOF.md).
The two-stage half is an exhaustive census of 24 orders. The two-map half
is an inconsistent linear system for each of the 55 gap pairs, at two
explicit GF(256) points. The three-map word is a polynomial identity. None
of these is a partial search.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 363005817/100000000000. This
package uses that record and edits neither file.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-g5-two-constant-maps
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_PAIRED_STAR_G5_TWO_CONSTANT_MAPS`. The checks raise, so `-O` does
not strip them. Directly:

```sh
python3 -B research/paired-star-g5-two-constant-maps/verify.py
```

Observed counts: `two_stage_orders` 24, `two_stage_pure_hits` 8,
`identity_gap_pairs` 55, `identity_separating_gap_pairs` 40,
`mixed_gap_pairs` 55, `sharp_ranks` [4, 4, 4].

Not run: a proof assistant, a census of the other adjacent-block orders, a
census of the other legal pairs, any q>1, and
`scripts/research_selected_baseline.py`. The selected record is read only
to pin κ.

## Open next questions

- Does any other adjacent-block order of this same legal pair admit two
  constant thin maps? Λ is the identity order with half A before half A'.
  The first step is the transposition of stages 0 and 1, with maps in the
  gaps between those two blocks' halves, and the same two-point system.
  Nothing in the star contract blocks that calculation. A failure on
  further orders is still not a proof for all 5! · 2^5 orders.
- Does the pure-correct mixed order stay empty when two diagonal stages
  are wrapped, rather than one? The single wrap solved here uses B=0 on
  stage 0 and the nonzero pair on stages 1 through 4. The first step is
  the order (0a, 1a, 1b, 0b, 2a, 3a, 3b, 2b, 4a, 4b) with B=0 on stages
  0 and 2. If the pure product misses, that order is not a two-map
  candidate.
- Does the identity-order obstruction survive at q=2 for the same block
  pattern, read as 2-by-2 blocks tensored with I_2? A q=1 proof does not
  lift. The first step is one specialization of that 18-dimensional system
  at the same stage order. This is not the five-map question at g=13 or
  g=31.

## Credit

The paired-star contract, the rank floor, the commuting map-count, and the
three-map word are from PR #5747 (Ali Romman), including the predecessor
statements in PR #5673, PR #5681, PR #5631, and PR #5617. The
adjacent-halves count that does not cover a thin map between halves is
PR #7010. The one-map theorem that left two maps at g=5 open is PR #7090.
The specialization formula is the one in the three-leaf census, PR #6922.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Independent human review and a proof-assistant proof are unclaimed.
