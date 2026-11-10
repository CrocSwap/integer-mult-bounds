# Characteristic-3 rank-36 pattern on the P104 window (no new κ)

**No new κ.** The selected record stays `781451/250000000`. This package
exhibits one 1-block pattern of rank 36 on `P104` over every field of
characteristic 3. It does not build a word or a paid profile.

The argument is in [PROOF.md](PROOF.md). The exact checks are in
[verify.py](verify.py).

## Result

`P120` is the odd graph on the 120 vectors in `F_2^9` of weight 3 or 7.
`P104` is the port list of PR #6933, vendored byte-for-byte. A 1-block
pattern has nonzero diagonal and zeros on both off-diagonal positions of
every orthogonal pair.

1. **Class-constant ansatz, proved impossible at rank 36.** In
   characteristic 3 the adjacency matrix satisfies `A^2 = 0`. Every matrix
   that is constant on the diagonal, on edges, and on non-edges is then
   either illegal (zero diagonal) or invertible of rank 120. The matrix
   `3I − A` is the illegal case. This is not an unrestricted nonexistence
   theorem.
2. **Witness, outside that ansatz.** The 46 monomials of degree at most 2,
   including the constant, give a 1-block pattern over `F_3` of rank 37 on
   `P120` and rank 36 on `P104`. Scalar extension preserves both ranks, so
   `w(P104; F) ≤ 36` and `w(P120; F) ≤ 37` for every field `F` of
   characteristic 3. One of the two `P112` extensions has rank 36 and the
   other has rank 37.
3. **The witness is one point of a positive-dimensional family.** With the
   diagonal normalised to 1, the coefficient spaces have dimensions 4 and 9,
   and the legal columns have dimensions 3 and 8. Free coordinates were set
   to 0. That choice was not minimised over the family.

The same solver without the constant term reproduces the predecessor's rank
38 on `P120` and gives rank 37 on `P104`. The predecessor recorded only the
bound 38. The constant term is the step from 37 to 36 on `P104`.

Accepting the lower bounds in #6933, Theorem 4, without replaying them, the
characteristic-3 window now satisfies `w(P104; F) ∈ [13, 36]`. The matching
upper bound 36 was previously known only off characteristic 3. No equality
is claimed.

## Scope

Original card: `complex-rank-shape-decoder`. Scope status: **changed**. The
card asks whether a decoder or coframe change improves the signed moment.
This package does not change a word or a moment. It answers the
characteristic-3 half of the question left open by the predecessor finding
on discussion comment 19492602: whether characteristic 3 admits a rank-36
pattern on the P104 window. Base commit
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.

The `F_5` rank-13 factorisation is a different question and is not
investigated. Characteristic 2 is not reopened.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3 -B research/p104-char3-rank36-window/verify.py
python3 -I -O -B research/p104-char3-rank36-window/verify.py
python3 -B scripts/research_package.py --package research/p104-char3-rank36-window
```

Expected final line: `PASS_CHAR3_RANK36 p104=36 p120=37 class_constant=120`,
then `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `partial`.

The port file is an input copied from #6933 because that commit is not in
this repository's history. Its sha256 is pinned in `verify.py`. The
catalogue and the selected record are provenance pins at the base commit.

## Open next questions

1. Does `P120` admit a 1-block pattern of rank 36 in characteristic 3? The
   witness here has rank 37, and one of the two `P112` extensions also stops
   at 37. A first step is one explicit `120 × 36` factorisation over `F_3`,
   or a lower bound of 37 with the hypotheses written down. Nothing in this
   package shows that every pattern has rank at least 37.
2. Does any other point of this degree-at-most-2 family, with the recorded
   nullities 4 and 9, have rank 36 on `P120`? The free-coordinate-zero point
   has rank 37. The family was not searched. A partial search would not
   decide the question.

The rank-13 factorisation over `F_5` is open in the predecessor note and is
intentionally not a next step of this package.

## Credit

DreamingOfClouds, PR #6933, for the window, the port list, and Theorem 4.
The predecessor finding (discussion comment 19492602, fork PR 151) proved the
rank-36 pattern off characteristic 3 and the rank-38 degree-2 pattern in
characteristic 3. Prepared by unpaidmoon with substantial Cursor Grok
assistance. New work is Apache-2.0.
