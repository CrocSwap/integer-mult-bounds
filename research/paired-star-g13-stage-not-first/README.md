# The g=13 leaf block stays nonzero when stage 0 is not first

**Proof, for one family of schedules.** In the paired-star contract, complete
any nonempty proper set of the stages `1` through `12` as adjacent pairs,
put every constant thin map between the halves of stage 0, and complete the
remaining stages afterwards. If the off-diagonal block `B` is nonzero, the
normalized coefficient is not `I`. From a tail leaf `t` into leaf 0 it equals
`(D_0+1) D_t^{-1} B`.

The assigned schedule completes stage 1 first and reads leaf 2. At
`g = 13` and `q = 8` the five rank-8 maps forced by setting every `D_j = 1`
sum to that unique matrix and fail. Both orders of stage 0 were evaluated
at two `GF(16)` points with `D_1 ≠ 1`. The normalized coefficient does not
depend on `D_1`. The block from leaf 1 into leaf 0 is `(D_0+1) B` on this
single-prefix word, so the stage-0-first factor `D_1^{-1}` is absent, and
the block is still nonzero. The pure product is the target. The failure is
the coefficient of `e`.

Selected κ stays `781451/250000000`. This is not a native caller and not a
change to the selected frontier.

The argument and the limits are in [PROOF.md](PROOF.md). The evidence class
is a proof under the stated schedule and legal-pair hypotheses, with exact
finite corroboration. It is not an exhaustive census of opening orders. A
failure on these schedules is not unrestricted nonexistence of an
interleaved word.

## Scope and evidence

Original card: `joint-query-controller`. Scope status: **refined**. The card
asks whether a changed query demand removes real work. The assigned
question is open question 2 of open PR #7026: the same leaf block when
stage 0 is not first. The first reading is stage 1 completed, stage 0
opened around the same five maps, and the leaf-0←leaf-2 block at one point
with `D_1 ≠ 1`.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is `781451/250000000`. This package
uses that record and edits neither file.

Five rank-8 maps have total rank 40, which is the chronological floor at
`g = 13`, `q = 8`. The floor does not forbid them. The adjacent-halves
theorem does not apply, because a thin map stands between the halves of
stage 0. The commuting-projector theorem already excludes five maps when
`B = 0`; the new hypothesis is `B ≠ 0`. The stage-0-first miss is open PR
#7026. This package keeps that word only as a separation control: at the
first field point the two words share the leaf-2 block and differ on the
leaf-1 block.

Overlap was checked on 2026-11-10 against open upstream PRs and discussions
(`python3 scripts/find_overlap.py`, terms for the stage-not-first block,
317 open PRs in the refreshed cache used by that search). The nearest
records are:

- Open PR #7026, head `99b5ed6d80ca3d97cf5f7176bf8b3557d67662bb`, proves the
  stage-0-first internal gap and leaves this order open. Canonical note:
  discussion #5593, comment 19514179. Handoff pointer: #1166, comment
  19514180. Fork draft:
  https://github.com/unpaidmoon/integer-mult-bounds/pull/202.
- Open PR #7010, head `32999d634cdd718ce6fb77648f54e4e674d7f395`, proves the
  adjacent-halves count. Its internal-gap remainder is the source of #7026.
- Open PR #7005, head `1750566c34c9fb117dc4afc4ce2bdacca7da036b`, and open
  PR #7025, head `ec8ab41023fcf244e2bf790b13e829127d2e08e4`, concern the
  `g = 31`, `q = 26` profile. This package does not enter it.

No open PR in that search evaluates the leaf-2 block after stage 1 has
already been completed. Source commits, Git blobs, and SHA256 pins are in
[SOURCES.json](SOURCES.json). The selected record, the catalogue, and the
paired-star contract are historical provenance.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-g13-stage-not-first
```

The registered replay runs `verify.py` twice, once with `-O`. Both print
`PASS_PAIRED_STAR_G13_STAGE_NOT_FIRST`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/paired-star-g13-stage-not-first/verify.py
```

The block identity is sections 5 and 6 of `PROOF.md`. The two field points
check that the updater matches it. They are not an interpolation on
thirteen variables. The two-stage prefix `{1,3}`, in both orders, is one
corroboration that a tail leaf misses every earlier adjacent stage. It is
not a census of subsets.

## Open next questions

- When two adjacent stages are completed before the gap, is the block from
  the earlier prefix leaf into leaf 0 still `(D_0+1) B`? The tail-leaf
  identity does not cover a leaf whose own stage is in the prefix. Section
  6 uses a prefix of one stage, because only then is the state entering
  stage 0 equal to `T_s`. A later prefix stage scales the core block of
  that column first. The first step is to expand the leaf-1 column through
  `U_3` for the prefix order stage 1 then stage 3, then through the first
  half of stage 0, and compare the final block with `(D_0+1) B`. One field
  point would not be that expansion. Nothing external blocks the
  calculation.
- If every stage `1` through `12` is completed before stage 0, so that no
  tail leaf remains, does any leaf-to-leaf block of these five maps stay
  nonzero? Section 5 needs a tail leaf, and section 6 does not extend to
  twelve prefix leaves. The first step is the same column expansion for
  leaf 1 when the prefix is `1,2,...,12` in that order, at
  `D = (2,3,...,14)`. Nothing external blocks the calculation.

A thin map after stage 0, a full call between the halves, and the `g = 31`,
`q = 26` internal gap are different questions. This note does not search
them.

## Credit

The paired-star contract, the rank floor, and the commuting map-count are
from PR #5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617.
The adjacent-halves count that leaves an internal gap open is PR #7010.
The stage-0-first gap, the five bundles, and the empty-prefix block formula
are PR #7026.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent
human review and a proof-assistant proof are unclaimed.
