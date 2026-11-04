# Proof: which plane-level signatures an invertible 4x4 basis can have

Setting, as in [PR3997](../rational-joint-support-screen/README.md): four ports
split into plane A = {0, 1} and plane B = {2, 3}, and four messages. For an
invertible matrix P over a field K, with inverse Q, message j has a *source
support* (the nonzero entries of column j of P) and a *reader support* (the
nonzero entries of row j of Q). Each support is replaced by the set of planes it
meets, encoded 1 = A, 2 = B, 3 = both. The **signature** of P is the four pairs
(source mask, reader mask). A column of an invertible matrix and a row of its
inverse are nonzero, so all eight masks are nonempty. PR3997 prices a basis from
its signature alone.

Notation: `e_j` is the j-th coordinate row vector of K^4 and
`H_j = {x : x_j = 0}` is the j-th coordinate hyperplane. The standard bilinear
form `x.y = sum x_i y_i` is nondegenerate on K^4, so `(W^perp)^perp = W` for every
subspace W (the dimensions agree and `W` lies in `(W^perp)^perp`).

## Lemma 1: the signature only sees two complementary planes

Let T and U be the 2x4 blocks formed by rows 0,1 and rows 2,3 of P, and let
`W_A = rowspace(T)`, `W_B = rowspace(U)`. Then `K^4 = W_A + W_B` (direct), and for
every message j:

* (a) A is in the source mask of j iff `W_A` is not contained in `H_j`; B is in
  it iff `W_B` is not contained in `H_j`.
* (b) A is in the reader mask of j iff `e_j` is not in `W_B`; B is in it iff
  `e_j` is not in `W_A`.

Conversely, every ordered pair of complementary 2-planes arises, by stacking a
basis of each as rows.

*Proof.* The four rows of P are independent, so the sum is direct. (a) Column j
of T is zero iff every row of T has j-th coordinate 0, iff `W_A` lies in `H_j`.
The same holds for U and `W_B`. (b) Write `Q = [Q_A | Q_B]` with 4x2 blocks for
columns 0,1 and columns 2,3. The identity `PQ = I` gives `T Q_B = 0` and
`U Q_B = I_2`. The second equation shows `rank Q_B = 2`; the first shows that
the column space of `Q_B` lies in `ker T`, which has dimension 2. Hence
`col(Q_B) = ker T = W_A^perp`. Row j of `Q_B` is zero iff every vector of
`W_A^perp` has j-th coordinate 0, iff `e_j` lies in `(W_A^perp)^perp = W_A`.
So B is in the reader mask of j iff `e_j` is not in `W_A`. Exchanging T with U
(and A with B) gives the statement for A. The converse is the choice of rows. QED

Nothing here depends on the values of the entries of P: two matrices with the
same pair of row spaces have the same signature, whatever cancellations occur.

## Lemma 2: three necessary conditions

Put `E_X = {j : e_j in W_X}` and `F_X = {j : W_X inside H_j}` for X = A, B. Then

1. `E_A` and `E_B` are disjoint, and so are `F_A` and `F_B` (a common j would put
   `W_A + W_B = K^4` inside `H_j`, or `e_j` in `W_A` and `W_B`, whose intersection is 0);
2. `E_X` and `F_X` are disjoint, because `e_j` is not in `H_j`;
3. `|E_X| <= 2`, because the `e_j` are independent and `dim W_X = 2`, and
   `|F_X| <= 2`, because `W_X` lies in a subspace of codimension `|F_X|` and has dimension 2;
4. if `|E_X| = 2` then `W_X` is spanned by those two coordinate vectors, so
   `F_X` is the complement of `E_X`; if `|F_X| = 2` then
   `W_X = intersection of the two H_j`, the span of the other two coordinate
   vectors, so `E_X` is the complement of `F_X`.

By Lemma 1 and item 1, the source mask of j is exactly {A} iff `j in F_B`, exactly
{B} iff `j in F_A`; the reader mask of j is exactly {A} iff `j in E_A`, exactly
{B} iff `j in E_B`. The conditions below follow.

* **C1.** No message has (source, reader) = ({A},{B}) or ({B},{A}). Otherwise
  `j in F_B and E_B`, or `j in F_A and E_A`, contradicting item 2.
* **C2.** At most two messages have source mask {A}, at most two {B}, and the
  same for reader masks. These counts are `|F_B|, |F_A|, |E_A|, |E_B|`; use item 3.
* **C3.** If two messages have source mask {A}, the other two have reader mask
  {B}; if two have source mask {B}, the other two have reader mask {A}. If two
  messages have reader mask {A}, the other two have source mask {B}; if two have
  reader mask {B}, the other two have source mask {A}. These are item 4: for
  example `|F_B| = 2` makes `E_B` the complement of `F_B`.

Let N be the set of signatures satisfying C1, C2 and C3. Then:

**Theorem.** For every field K, the signature of every `P in GL_4(K)` lies in N.
`|N| = 439`, counted by enumerating all `9^4 = 6561` candidate signatures
(`verify.py`). Over Q the signatures of integer matrices with entries in
{-1, 0, 1} already fill N: `verify.py` exhibits one explicit integer witness per
element and checks each by exact rational inversion. So over Q, and over every
field of characteristic 0, the set of realizable signatures is exactly N.

N equals the set of 439 signature codes that PR3997 records in
`TERNARY-SCREEN.txt` (`verify.py` compares the two code sets). PR3997's verifier
equates that set with its generic-support census, so the realizable set is the
generic census, with no cancellation signature added.

## Consequence for the PR3997 invoice

PR3997's pricing of a basis on a plane pair is `sum over the four messages of
cost(source mask, reader mask)`, a function of the signature only. Its
`RESULT.json` records the minimum over the 439 generic signatures as 8 on each of
the 1,540 plane pairs, with no strict improvement. Because every invertible basis
over any coefficient field has a signature in N, the minimum over all bases is the
same 8: special rational values cannot lower the two-plane copy invoice below the
separate-plane baseline in this model. This is a consistency check, not a new
result: [PR4365](https://github.com/CrocSwap/integer-mult-bounds/pull/4365)
(`research/two-plane-copy-floor`) proves the stronger statement that COPY mass 8 is a
floor for any finite scalar factorization on two matched planes, over every field.
What is new here is the classification of the signatures themselves.

## What the three conditions cost

Dropping one condition enlarges the candidate set (`RESULT.json`): without C1 the
set has 555 elements, without C2 805, without C3 1,771. None is redundant. The
439 signatures that survive all three are all realized, so the conditions are
also sufficient over Q.

## Scope

The theorem is about plane-level signatures of invertible 4x4 matrices with two
planes of two ports. It does not classify the finer joint zero pattern of P and
`P^-1`, price any coefficient arithmetic, or treat three or more planes,
overcomplete factorizations or physical routing; PR3997 lists these as outside its
scope as well.
