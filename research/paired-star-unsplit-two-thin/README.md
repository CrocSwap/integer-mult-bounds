# One unsplit call per stage still needs two thin maps of total rank 8

**No new kappa.** Over F_2, with block size 2 and three paired leaves, place
one unsplit full call on each stage. Two constant thin maps do not meet the
paired-star endpoint at total rank 6 or 7. Every solution has rank sum at
least 8, and 8 is attained. The selected frontier stays
781451/250000000.

The argument, the two affine families, and the limits are in
[PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
query demand removes real work. This package answers the two-map question
left open by PR #6956: the pure determinant allows exactly one unsplit call
E_j on each stage, and the chronological floor at this size is still 6.
The field stays F_2 and the thin maps stay constant. It is not a caller, a
native bill, or a change of kappa. Source commits, Git blobs and SHA256
pins are in [SOURCES.json](SOURCES.json). The selected record and catalogue
are historical provenance.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 781451/250000000. This package uses
that record and edits neither file.

The endpoint equation separates by matrix entry because the pure factors
I + x_j E_j are diagonal. All 6 orders and all 6 pairs of gaps are solved.
Eighteen pairs are impossible by a monomial mismatch. The other eighteen
are leaf permutations of two explicit families:

- Family A, twelve systems. A block calculation gives rank sum at least 8,
  and the 2-by-2 lemma is checked on all 256 pairs. Both 16^4 parameter
  forms are also ranked directly.
- Family B, six systems. The affine space is every 8-tuple of 2-by-2
  matrices, 2^32 points. The compiled census visits every point. A branch
  is skipped only when six already-complete leaf rows have rank sum at
  least 8. The counter is exactly 2^32, and the minimum is 8.

One thin map, and two thin maps in the same gap, fail with the one-monomial
equation. Same-gap multiplication is the identity
(I + e Z)(I + e W) = I + e (Z + W). The zero-parameter words of both
families match the target in F_2[D_0, D_1, D_2, e] / (e^2). Moving a
diagonal block onto only one map, or deleting a map, misses it.

This is an exhaustive finite census of a proved affine space, together with
a block-rank proof for family A. It is not a sample, and a failed search is
not the claim. It is not an unrestricted nonexistence theorem.

Overlap was checked against open upstream PRs and discussions at
2026-11-10, including the open two-call three-map witness PR #7011, the
partial F_4 census PR #7006, and the adjacent-halves arguments PR #7010 and
PR #7005. None of those places one unsplit call on each stage. The question
is the first open question of merged PR #6956.

## Reproduce

Python 3.12 and gcc. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-unsplit-two-thin
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_PAIRED_STAR_UNSPLIT_TWO_THIN`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/paired-star-unsplit-two-thin/verify.py
```

The C census is compiled by the verifier and is not a checked-in binary.

## Open next questions

- With the same one unsplit call on each stage, can three constant F_2 thin
  maps meet total rank 6? Two maps now need 8, so three maps are what
  remains of the chronological floor under this call shape. The first step
  is to fix order (0, 1, 2), place the maps in three distinct gaps, and
  solve the three-term entry equation. The rank-6 word in PR #7011 uses two
  full calls per stage, so it does not answer this.
- Can a thin map whose entries lie in F_2[D_0, D_1, D_2], rather than in
  F_2, bring the unsplit two-map rank below 8? The constant census does not
  apply. The first step is to let one diagonal block be linear in a single
  D_j and test the same two gap families.

Block entries outside F_2, a stage factor that is not the unsplit
projector, and the profiles g=13, q=8 and g=31, q=26 stay separate
questions.

## Credit

The paired-star contract, the local form, and the rank floor are from PR
#5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617. The
one-unsplit-call opening is PR #6956. The two-call rank-8 census is PR
#6940, and the one-map census is PR #6922. Prepared by unpaidmoon with
substantial Cursor Grok assistance. Independent human review and a
proof-assistant proof are unclaimed.
