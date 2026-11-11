# Characteristic-3 rank-32 pattern on P120 (no new κ)

**No new κ.** The selected record stays `781451/250000000`. This package
exhibits one 1-block pattern of rank 32 on `P120` over every field of
characteristic 3, together with a `120 × 32` factorisation over `F_3`. The
same matrix has principal rank 32 on `P104` and on both copies of `P112`.
It does not build a word or a paid profile.

The argument is in [PROOF.md](PROOF.md). The exact checks are in
[verify.py](verify.py).

## Result

`P120` is the odd graph on the 120 vectors in `F_2^9` of weight 3 or 7.
`P104` is the port list of PR #6933, the file already vendored by #6953.
A 1-block pattern has nonzero diagonal and zeros on both off-diagonal
positions of every orthogonal pair.

1. **The previous point still has rank 37.** The free-zero degree-at-most-2
   pattern of #6953 is rebuilt and still has rank 37 on `P120`. Its columns
   span a 37-dimensional space `S`.
2. **Eight columns are rigid inside that span.** The weight-7 vectors that
   omit coordinate 8 have a unique legal column in `S`. Those eight columns
   are independent.
3. **One canonical hyperplane of `S` has a rank-32 pattern.** In the kernel
   basis of those eight columns, the second basis vector cuts `S` to a
   36-dimensional space that still meets every legal flat. The free-zero
   point in the basis carried from `S` is a 1-block pattern of rank 32.
   Scalar extension preserves the rank, so `w(P120; F) ≤ 32` for every field
   `F` of characteristic 3. The principal submatrices on `P104` and both
   `P112` extensions also have rank 32.
4. **The same space has another point of rank 36.** Free-zero coordinates in
   the kernel basis of the nine coefficient relations give a different legal
   pattern, of rank 36. Rank 32 is attached to the basis in item 3, not to
   every pattern with columns in the space.

Accepting the lower bounds in #6933, Theorem 4, without replaying them, the
characteristic-3 window now satisfies `w(P120; F) ∈ [15, 32]`, and the same
upper bound 32 holds for `P104` and both copies of `P112`. #6953 had upper
bounds 37, 36, 36 and 37 on these sets. No equality is claimed. No κ changes.

The census of the 29 kernel-basis vectors is exhaustive for that basis. It
is not a census of all hyperplanes, and a failed search for a smaller
pattern is not part of the claim.

## Scope

Original card: `complex-rank-shape-decoder`. Scope status: **changed**. The
card asks whether a decoder or coframe change improves the signed moment.
This package does not change a word or a moment. It answers the P120 half of
the question left open by #6953: whether characteristic 3 admits a 1-block
pattern of rank 36 on `P120`. The witness here has rank 32, which is stronger
than that requested ceiling. Base commit
`17469fff78c22941280f04d39dc5a1faee09c840`, priority revision 8. The selected
κ in `certificates/selected-result.json` is `781451/250000000`; the older
decimal quoted in `docs/research/current-priorities.md` is not the live
frontier.

The `F_5` rank-13 factorisation is open in #7014 and is not investigated.
The degree-at-most-2 family is not searched beyond the two explicit points.
Characteristic 2 is not reopened.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3 -B research/p120-char3-rank32-window/verify.py
python3 -I -O -B research/p120-char3-rank32-window/verify.py
python3 -B scripts/research_package.py --package research/p120-char3-rank32-window
```

Expected final line: `PASS_P120_CHAR3_RANK32 rank=32 p104=32 p112=[32, 32]`,
then `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `partial`.

The port file is a live input, the bytes already pinned by #6953. The
catalogue and the selected record are provenance pins at the base commit.

## Open next questions

1. Does `P120` admit a 1-block pattern of rank at most 31 in characteristic 3?
   The witness is one free-zero point of one hyperplane of the #6953 column
   span. Inside that 36-dimensional space the legal fibers have affine
   dimensions 0, 2 and 5, and this point was not minimized over them. Another
   basis of the same space has a legal point of rank 36. A first step is one
   other explicit pattern of rank at most 31, inside this space or outside
   degree at most 2. A failed search is not a lower bound.
2. Does every 1-block pattern on `P120` in characteristic 3 have rank at
   least 32? The cited lower bound is 15, and the class-constant ansatz has
   rank 120. The rank-36 point in the same space shows that this column space
   does not by itself force rank 32. A first step is one linear condition
   satisfied by every legal column, strong enough to force rank at least 32,
   with the hypotheses written down.

## Credit

DreamingOfClouds, PR #6933, for the window, the port list, and Theorem 4.
The predecessor pattern of rank 37 on `P120` and rank 36 on `P104` is
#6953. Prepared by unpaidmoon with substantial Cursor Grok assistance.
New work is Apache-2.0.
