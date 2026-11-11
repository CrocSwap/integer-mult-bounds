# The g=13 two-prefix leaf block is still `(D_0+1) B`

**Proof, for the two-stage schedules of open PR #7096.** Complete stage `s`
and then a different stage `r` as adjacent pairs, put the constant thin sum
`K` between the halves of stage 0, and complete the remaining stages
afterwards. The block from the earlier prefix leaf into leaf 0 is
`(D_0+1) D_r B` after the first half of stage 0, and `(D_0+1) B` after the
second half and at the end of the word. The assigned order is stage 1 then
stage 3, so the intermediate factor is `D_3` and the final block is still
`(D_0+1) B`.

The first-half polynomial is not `(D_0+1) B`. Setting `D_3 = 1` makes them
agree, which is why one field point is not this expansion. With `K` between
the halves, `D_3` cancels. If `B ≠ 0` and `D_0 ≠ 1`, the final block is
nonzero, so these constant thin maps miss the endpoint. At `g = 13` and
`q = 8` the same five rank-8 bundles realize `K`.

Selected κ stays `363005817/100000000000`. This is not a native caller and
not a change to the selected frontier.

The argument and the limits are in [PROOF.md](PROOF.md). The evidence class
is a proof under the stated schedule and legal-pair hypotheses, with exact
symbolic corroboration. The `g = 5` run is an exhaustive finite check of the
192 literal two-stage words at `q = 2` described in the proof. It is not a
census of projectors or of the `g = 13` prefixes. A failure on these
schedules is not unrestricted nonexistence of an interleaved word.

## Scope and evidence

Original card: `joint-query-controller`. Scope status: **refined**. The card
asks whether a changed query demand removes real work. The assigned question
is open question 1 of open PR #7096: when two adjacent stages are completed
before the gap, is the block from the earlier prefix leaf into leaf 0 still
`(D_0+1) B`? The required reading is the leaf-1 column through `U_3` for the
prefix order stage 1 then stage 3, then through the first half of stage 0.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is `363005817/100000000000`. This
package uses that record and edits neither file.

Five rank-8 maps have total rank 40, which is the chronological floor at
`g = 13`, `q = 8`. The floor does not forbid them. The adjacent-halves
theorem does not apply, because a thin map stands between the halves of
stage 0. PR #7096 already shows that a nonempty proper prefix still misses
through a tail leaf, and that a single prefix leaf has final block
`(D_0+1) B`. This package identifies the earlier leaf of a two-stage prefix.
The intermediate block carries `D_r`, and the final block does not.

Overlap was checked on 2026-11-11 against open upstream PRs. Upstream `main`
was re-fetched at session start and was still
`e54523517d0f03e58352e647c403a5af3e525a57`. Issue search for the phrases
“two adjacent stages are completed”, “earlier prefix leaf”, and “stage 1
then stage 3” finds this question in open PR #7096 and in no other paired-star
result. `python3 scripts/find_overlap.py --offline` had no remote snapshot;
its local notes do not contain this expansion. The live PR list is the
overlap evidence.

- Open PR #7096, head `bfef0c9787f13a8052190bfefaf62ba1400e1177`, proves the
  tail-leaf block when stage 0 is not first and leaves the two-stage leaf
  column open. This package answers that column. It does not re-prove the
  tail theorem.
- Open PR #7097 is the after-stage-0 correction. The thin maps here stay
  between the halves of stage 0.
- Open PR #7026 is the stage-0-first gap and the source of the five bundles.
  Open PR #7010 is the adjacent-halves count.
- Open PR #7005 and open PR #7025 are the `g = 31`, `q = 26` profile. This
  package does not enter it.

No open PR in that search expands the leaf-1 column through `U_3` and the
first half of stage 0. Source commits, Git blobs, and SHA256 pins are in
[SOURCES.json](SOURCES.json). The selected record, the catalogue, and the
paired-star contract are historical provenance.

## Reproduce

Python 3.12.3, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-g13-two-prefix-leaf
```

The registered replay runs `verify.py` twice, once with `-O`. Both print
`PASS_PAIRED_STAR_G13_TWO_PREFIX_LEAF`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/paired-star-g13-two-prefix-leaf/verify.py
```

The block identity is sections 4 through 8 of `PROOF.md`. The checker
recomputes those matrix polynomials, including a frame with `B^2 ≠ 0`, and
compares them with the literal conjugated word at `g = 5`. It does not sample
`D_j`.

## Open next questions

- If every stage `1` through `12` is completed before stage 0, does any
  leaf-to-leaf block that avoids leaf 0 stay nonzero? Section 8 cancels one
  later scalar `D_r`. A longer prefix needs the entering column proved
  equal to `(product of the later D_j) I` on the core, `I` on that leaf, and
  zero on other leaves, and then a block from leaf 1 into leaf 2. The first
  step is that column for the prefix `1,2,...,12` in that order, not one
  field point. Nothing external blocks the calculation. This package does
  not claim it.
- If the two halves of the later stage are not adjacent, does the extra
  factor still cancel? The scalar `U_r` uses both halves before the gap.
  The first step is the leaf-1 column with one half of stage 3 before stage
  0 and the other half after `K`. A thin map after stage 0, a full call
  between the halves of stage 0, and the `g = 31`, `q = 26` gap are
  different questions.

## Credit

The paired-star contract, the rank floor, and the commuting map-count are
from PR #5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617.
The adjacent-halves count is PR #7010. The stage-0-first gap and the five
bundles are PR #7026. The schedule and the question answered here are PR
#7096.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent
human review and a proof-assistant proof are unclaimed.
