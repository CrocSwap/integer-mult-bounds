# After stage 0, a leaf-supported correction misses the g=13 block

**Proof, for one balanced placement.** The five rank-8 bundles at g = 13,
q = 8 sum to the swap K forced by every D_j = 1. Subtract a matrix
supported on the two leaf-0/leaf-1 blocks from that internal sum, add the
same matrix after both halves of stage 0, and read the leaf-0 ← leaf-1
block. For the exhibited legal pair, that block equals

```text
D_1^{-1} (D_0+1) (B + (A_Q+B) C)
```

and is nonzero whenever D_0 ≠ 1. The same schedule, with one of the five
named bundles moved instead, leaves the nonzero block
D_t^{-1}(D_0+1) B π_{S^c}.

A different rank-8 coordinate map, on coordinates {0, 2, 8, 9}, does clear
every leaf-to-leaf block while keeping the D_j = 1 swap. That is a witness
for the block only. At the two tested points its defect has rank 32, so no
second balanced matrix of rank at most 8 repairs the endpoint there.

Selected κ stays `781451/250000000`. This is not a native caller and not a
change to the selected frontier.

The argument and the limits are in [PROOF.md](PROOF.md). The evidence class
is a proof under the after-stage-0 split and the exhibited legal pair, with
exact finite corroboration over GF(16). It is not an exhaustive census of
rank-8 supports. A failure for the leaf-supported insertion is not
unrestricted nonexistence of a cancelled block, and the coordinate witness
is not an endpoint.

## Scope and evidence

Original card: `joint-query-controller`. Scope status: **refined**. The card
asks whether a changed query demand removes real work. The assigned
question is open next question 1 of open PR #7026: one rank-8 map in the
gap after stage 0, the leaf-0 ← leaf-1 block, and the same D_j = 1 swap.
The first step named there is the leaf-supported insertion. The five named
bundles are the maps that sum to that swap. The coordinate witness is the
boundary of the same identity, not a second schedule.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 781451/250000000. This package uses
that record and edits neither file.

Overlap was refreshed on 2026-11-10 (`python3 scripts/find_overlap.py`,
339 open PRs, 7013 discussion records, local inventory complete at
`17469fff78c22941280f04d39dc5a1faee09c840`). The nearest records are:

- Open PR #7026, head `99b5ed6d80ca3d97cf5f7176bf8b3557d67662bb`, proves the
  internal gap with every thin map between the halves of stage 0, and asks
  this after-stage-0 question. It does not evaluate the split. Canonical
  note: discussion #5593, comment 19514179. Handoff pointer: #1166,
  comment 19514180.
- Open PR #7010, head `32999d634cdd718ce6fb77648f54e4e674d7f395`, proves the
  adjacent-halves count. No thin map stands between the halves there.
- Open PR #7005, head `1750566c34c9fb117dc4afc4ce2bdacca7da036b`, is the
  g = 31, q = 26 consecutive bound. This package does not enter it.
- Open PR #7011, head `9a63d6d99158f5ced1058df403d3e3b9847fcc17`, is a
  three-leaf F_2 census. It does not lift to thirteen leaves.

No open PR in that snapshot evaluates this after-stage-0 split at g = 13,
q = 8. Source commits, Git blobs, and SHA256 pins are in
[SOURCES.json](SOURCES.json). The selected record, the catalogue, and the
paired-star contract are historical provenance. PR #7026 is not an ancestor
of this branch, so its tree is cited by commit and is not a live pin.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-g13-after-stage0-block
```

The registered replay runs `verify.py` twice, once with `-O`. Both print
`PASS_PAIRED_STAR_G13_AFTER_STAGE0_BLOCK`. The checks raise, so `-O` does
not strip them. Directly:

```sh
python3 -B research/paired-star-g13-after-stage0-block/verify.py
```

The g = 13 identities are sections 4 through 6 of `PROOF.md`. The two field
points check that the updater matches them. They are not an interpolation
on thirteen variables.

## Open next questions

- For a legal off-diagonal B other than E_{0,8}+E_{9,2}, with the same
  A = diag(I_8, 0), can (A+B)C = B or (A'+B)C = B? The functionals in
  section 4 use these two corners. A solvable B would be the first
  leaf-supported matrix that cancels the block. Nothing external blocks
  the trial of one other legal B. This is not the stage-0-not-first
  schedule and not the g = 31 profile.
- Does one balanced constant matrix of rank 16 clear the section 6 witness
  at D = (2, 3, ..., 14)? A rank-8 partner changes the final coefficient by
  rank at most 16 and cannot meet a rank-32 defect. Rank 16 meets that
  ceiling. The first step is the coordinate map on
  {1, 3, 4, 5, 6, 7, 10, 11}, balanced across the same gap, at that one
  point and one half order. One matrix is not a classification.

## Credit

The paired-star contract and the rank floor are from PR #5747 (Ali
Romman), including PR #5673, PR #5631, and PR #5617. The internal gap that
asks this question is PR #7026. The adjacent-halves count is PR #7010.
The consecutive bound at the other profile is PR #7005.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent
human review and a proof-assistant proof are unclaimed.
