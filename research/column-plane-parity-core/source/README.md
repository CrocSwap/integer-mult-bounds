# Column-column plane orbits

**Result.** Pairs of 2-dimensional F2 column planes with trivial image
intersection fall into infinitely many coordinate-permutation orbits once
every nonzero vector is required only to have weight at least 2. Inside
the equality case, where both planes have weights (2, 2, 2), there are
exactly five orbits. **No new κ.** The selected value remains
`363005817/100000000000`.

A column plane is a 2-dimensional space supported off its column, with
minimum weight at least 2. Its image is the column plus that plane. This
is the column-triple geometry of #7139, Section 2. The question is open
question 1 of #7221.

[PROOF.md](PROOF.md) gives three separate statements.

- **Proof.** One column plane is classified by a sorted triple of
  nonnegative integers α ≤ β ≤ γ with α+β ≥ 2. The nonzero weights are
  α+γ, β+γ, and α+β. There are infinitely many triples.
- **Exhaustive finite census.** Both planes of weight (2, 2, 2) give
  exactly five orbits, listed in the proof. Each such plane is the
  even-weight code on a 3-set, and the pair support has size 6, 7, or 8.
  The case split is the completeness argument. The labeled counts on
  those widths are 900, 2100, and 1120; widths 5 and 9 contribute 0.
- **Proof of infinitude, not a census.** Allowing minimum weight at
  least 2, the printed disjoint pair with 2k duplicated coordinates,
  k = 0, 1, 2, ..., gives support sizes 8+2k and hence infinitely many
  orbits. Pool W of #7221, with weights (2, 2, 4) and (2, 2, 2), is
  another orbit and does not reduce to one of the five by deleting a
  repeated coordinate type.

The five weight-(2, 2, 2) orbits are the mutual cross (support 6), the
hooked overlap (support 6), the one-sided placement (support 7, pool B
of #7221), the shared foot (support 7), and the printed disjoint pair
(support 8, the column-column witness of #7138 and #7139). Support size,
the number of columns that lie in the other plane, and the size of the
support intersection separate them.

This is not a classification of the normal-normal or mixed geometries,
and it is not a finite list of all minimum-weight-at-least-2 pairs.

## Scope and evidence

Catalogue card: `bit-new-register-model`, priority revision 8, base commit
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status: **changed**. The
card asks for a new register alphabet. This package answers the
column-column orbit question left open by #7221. The reason is recorded
in [TASK.json](TASK.json). The original native acceptance gate is unmet,
and the selected frontier is unchanged.

[verify.py](verify.py) enumerates every ordered column pair and every
pair of 3-sets on widths 5 through 9. It checks image rank 3, trivial
intersection, the five invariants, and the labeled counts. It checks the
five representatives and two overlaps that the case split excludes. It
checks the doubling family for k = 0, 1, 2, 3, 4 and checks pool W,
including the deletion that collapses W. It also checks the single-plane
weight formula for every class size at most 6. These scans are exhaustive
on the weight-(2, 2, 2) domain named above. They do not enumerate planes
of larger support; Theorem C is the explicit family in the proof.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue is
provenance at the base commit, and the selected record is an input
because the verifier reads it. Nothing here reruns the selected baseline
as a scientific replay.

Overlap was checked on 2026-11-11 against upstream main
`e54523517d0f03e58352e647c403a5af3e525a57`. A GitHub search of open
upstream PR titles and bodies found no match for this column-plane orbit
question outside #7138, #7139, and #7221. #7221 states the question and
stops after separating five explicit pools. #7139 prints one
weight-(2, 2, 2) column-column witness and leaves the coordinate
classification open. The normal-normal and mixed questions are not taken.

## Reproduce

From the repository root, with Python 3.12 and the standard library only:

```sh
python3 -B research/column-column-plane-orbits/verify.py
python3 -I -O -B research/column-column-plane-orbits/verify.py
python3 -B scripts/research_package.py --package research/column-column-plane-orbits --check-only
python3 -B scripts/research_package.py --package research/column-column-plane-orbits
```

The verifier prints `PASS_COLUMN_COLUMN_PLANE_ORBITS`.

## Open next questions

1. After deleting, in pairs, every coordinate that duplicates another
   coordinate in both planes, which orbits still have two
   minimum-weight-at-least-2 planes? The doubling family reduces to the
   printed row. Pool W collapses, so a deletion theorem has something to
   separate. The first step is one repeated type in a plane whose three
   type counts are positive. This package does not run that deletion on
   every orbit.

2. Is every dimension-6 pool built from two normal-form triples, or from
   one normal-form triple and one column triple, a coordinate permutation
   of the witness printed in #7139? That is question 2 of #7221. The
   first step is the normal-form uniqueness statement on one 3-set in
   #7139, Section 2. The column-column census does not decide it.

## Credit

The fiber lemma is Nick Petalas, #5921. The total-image bound and Lemma 3
are CubeJerry, #6838. The triple classification and the irreducible bound
3 are #6921. The dimension-4 irreducible 4-cycle is #6962. The
dimension-5 witness is #7094. The weight-1 bound and its printed
dimension-6 column witness are #7138. The three printed dimension-6
witnesses are #7139. The question answered here, and pools W and B, are
#7221. Prepared by unpaidmoon with substantial Cursor Grok assistance.
New work is Apache-2.0.
