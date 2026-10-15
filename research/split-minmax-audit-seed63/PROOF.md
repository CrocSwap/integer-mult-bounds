# The split min–max is a linking-system min–max

This audit confirms the identity quoted without a precise reference in
[PR2162, §3](https://github.com/CrocSwap/integer-mult-bounds/pull/2162), at
`113a718265c62aec301c5695f4bfb9c421bef7ab`. The retained statement and full-source
hash are in `SOURCE-STATEMENT.md` and `SOURCES.json`. The result below is a
written application of a standard theorem, with finite executable checks. It
is not a proof-assistant verification, a proof of target (A), or a new bound
for multiplication.

## 1. Statement, with independent row and column choices

Let `V` be a finite set of size `v`, let `F` be a field, and let `C` be a
nonempty finite set of colors. For each `c`, let `H_c` be a `V × V` matrix over
`F`. Define `P` to be the largest sum of sizes of nonsingular square minors

`H_c[U_c, W_c]`,

where the `U_c` are pairwise disjoint and, separately, the `W_c` are pairwise
disjoint. Empty minors are allowed and have determinant one. There is no
requirement that `U_c = W_c`. Then

```
P = min_{S,T ⊆ V} |V \ S| + |V \ T| + Σ_c rank_F H_c[S,T].             (1)
```

For the decoder statement take `F = F2` and

`H_c = diag(1_{R_c}) B diag(1_{A_c})`.

Zero padding does not change submatrix rank, so the final summand in (1) is
exactly `rank_F2 B[S ∩ R_c, T ∩ A_c]`. Neither a rational realization nor
admissibility of `B` is needed for this algebraic identity.

## 2. Precise literature dependency and its application

Use A. Schrijver, *Matroids and Linking Systems*, J. Combinatorial Theory B
26 (1979), 349–369, [Theorem 3.6, pp. 363–364](https://ir.cwi.nl/pub/9901/9901D.pdf#page=15),
[DOI](https://doi.org/10.1016/0095-8956(79)90011-X). It maximizes the size of a
linked pair whose two sides are independent in specified matroids. Its dual
is the minimum of the two matroid ranks plus the linking rank on the two
complements. The matrix linking system is the nonsingular-minor system.

Here is the complete mapping of the present problem into that theorem.
Take disjoint row and column universes

```
X = {(row,t,c) : t ∈ V, c ∈ C},
Y = {(col,t,c) : t ∈ V, c ∈ C}.
```

Put `H = blockdiag_c H_c`, regarded as a matrix with row set `X` and column
set `Y`. Use the linking system whose linked pairs are precisely the square
nonsingular minors of `H`. On each side use the partition matroid allowing
at most one copy of each original element `t`, across all colors. Its rank
on a subset is the number of original elements represented by that subset.

A nonsingular minor of a block diagonal matrix must select equally many rows
and columns in each color: if a color has more selected rows than selected
columns its row block is deficient, and if it has fewer, another color has
more. When the counts agree, its determinant is, up to sign, the product of
the color determinants. The partition-matroid conditions impose precisely
the two disjointness conditions defining `P`. Thus Schrijver's primal is `P`.

Writing `r_X`, `r_Y` for the two partition ranks, its dual is

```
min_{D ⊆ X, E ⊆ Y} r_X(D) + r_Y(E) + rank_F H[X \ D, Y \ E].           (2)
```

Any `D` can be saturated by including **all** color copies of every original
row represented in `D`. This leaves `r_X(D)` unchanged and can only decrease
the last rank. Saturate `E` in the same way. Consequently an optimum of (2)
exists among saturated pairs. If `S` and `T` are the original elements whose
copies were not deleted, the partition ranks are `|V \ S|` and `|V \ T|`.
The remaining matrix is block diagonal with blocks `H_c[S,T]`, so its rank
is their rank sum. This gives exactly (1).

All sets are finite, both specified independence systems are matroids, and
the linking system is a matrix linking system over the **same field** used
for the block ranks. These are the required hypotheses. In particular, no
field-size assumption, generic specialization, geometric representability,
or interchange of a minimum and maximum has been added. The theorem applies
also when some masked rows or columns are zero: their copies still exist in
the partition matroids, and no nonsingular minor can use such a zero row or
column. Schrijver proves the standard theorem using his induced-matroid
result and Edmonds' matroid-intersection theorem. Those standard results are
the literature dependency of this written proof; they are not formalized here.

## 3. Identification with SPL and generic rank

For pairwise disjoint row sets `R'_c ⊆ R_c` and column sets `A'_c ⊆ A_c`,
shrink each block `B[R'_c,A'_c]` to a nonsingular minor of its rank. This
preserves disjointness and shows that the maximum of the rank sum is at most
`P`. Conversely a packing attaining `P` is already such a choice, so the
maximum over partial partitions equals `P`.

In the decoder model every row and column has a nonempty support. Any partial
partition can therefore be completed by assigning each unused row, and each
unused column separately, to a color in its support. Adding rows and columns
cannot lower rank. Thus the maximum over full partitions used by PR2162 is
also `P`. Our finite checker permits empty supports too; there it checks the
partial-partition extension (1), rather than asserting that a nonexistent
full partition exists.

For completeness, the generic matrix in PR2162 has entries

`N_ts = B_ts Σ_c x_{t,c} y_{s,c}`

with the variables allowed only on their respective supports. In the
determinant expansion of any square minor, a monomial fixes one color for
each selected row and column. Its coefficient is zero if those color counts
disagree. Otherwise its coefficient, up to sign, is the product of the
corresponding color-block determinants. Different color assignments give
different monomials. A minor is therefore nonzero as a polynomial exactly
when at least one such packing fills it. Taking the largest nonzero minor
gives `GR(B) = P = SPL(B)`. This argument is symbolic; a single evaluation in
a finite field can lose rank and is not used as a generic-rank certificate.

## 4. The universal corollary and its quantifiers

Let a class of configurations be closed under deleting lines, with the
restricted supports and restricted admissible pairings inherited. For example,
the class of all exact three-total rational decoder configurations has this
closure property: restricting the two vector lists preserves nonzero
diagonals and the required off-diagonal zeros.

Suppose target (A) holds **for every configuration in that class and every
admissible pairing**. Fix one such configuration and one admissible `B`.
For any `S,T ⊆ V` put `I = S ∩ T`. The pairing `B[I,I]` is admissible for
the restricted configuration, so the assumed target gives

```
Σ_c rank_F2 B[I ∩ R_c, I ∩ A_c] ≥ |I|.
```

Each of these is a submatrix of `B[S ∩ R_c,T ∩ A_c]`. Hence every cut in (1)
has value at least

```
2v − |S| − |T| + |S ∩ T| = 2v − |S ∪ T| ≥ v.
```

As `P ≤ v` by row disjointness, (1) forces `P = v`. An attaining packing
uses every original row and every original column, giving a perfect split
into square nonsingular blocks. Empty colors are allowed.

Conversely a perfect split has total rank `v`, and each block is a submatrix
of its full support block. It follows that `cost(B) ≥ v`. Thus the two
**universal**, configuration-class assertions are equivalent, as claimed.
The argument does not prove either universal assertion for `T = 3`.

For a fixed `B`, the sufficient hypothesis used above is the collection of
all principal-restriction cost inequalities. Its full cost alone does not
justify this step. A diagnostic example in the more general masked-matrix
model is `H_0 = diag(C,1)`, `H_1 = H_2 = diag(0,0,0,1)`, where

```
C = [1 1 0]
    [0 1 1]
    [1 0 1]  over F2.
```

The full rank sum is `3+1+1=5 ≥ 4`, but on the first three indices the sum
is only `2 < 3`. Its packing optimum is three. This example has a unit
diagonal common `B`, but no rational decoder realization is supplied: it
is a control on an invalid inference, **not a counterexample to (A)**.

## 5. Independent finite evidence and weak duality

`verify.py` enumerates nonsingular minors, combines them with dynamic
programming using disjoint row and column masks, and independently minimizes
the expression in (1) over every pair of masks. It recertifies each distinct
problem's attaining minors and selected cut using permutation determinants
and exhaustive minor ranks, without Gaussian elimination in that check.

These certificates have an elementary weak-duality interpretation, independent
of the min–max theorem: deleting the rows outside `S` and columns outside
`T` reduces each packed block's rank by at most the number of deleted rows
and columns. Summing those losses counts any original row or column at most
once. The surviving ranks are bounded by `Σ_c rank H_c[S,T]`. Thus every cut
upper-bounds every packing. An attaining packing and an equal-valued cut
certify that finite instance without assuming the identity being audited.

The finite coverage, deterministic sampling rule and meaningful false-variant
controls are described in `README.md`; `EXPECTED.json` binds their output.
The general result rests on the written argument above and the identified
standard theorem, not on extrapolating the finite coverage.

Prepared by Charan (@theon199) with substantial OpenAI Codex assistance.
Credit DreamingOfClouds for PR2162's statement and split polynomial argument,
the PR1590/PR2111 decoder work for its model, and A. Schrijver for the
linking-system theorem. New text and code are Apache-2.0.
