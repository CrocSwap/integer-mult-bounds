# P112 masked completions: the sharp two-column rank boundary

**Scoped proof with a finite certificate; no supplier or new κ.** A genuinely
masked rank-two correction on **53 rows and two columns** raises the P112 Gram
matrix rank from eight to **nine**, rather than ten. This is a sharp failure of
rank additivity in the two-column family. Every correction in that family
supported on at most 52 rows is additive. The new proof uses explicit finite
P112 geometry and does not need the E8 hyperplane-flat classification premise.

The sparse-block theorem in [PR1447](../p112-sparse-completion-rank/README.md)
remains valid: its row and column caps are both 52. Its displayed 53-row
counterexample is unmasked. The construction here supplies a masked boundary
example, and settles that package's proposed rank-one follow-up: a nonzero
odd-only rank-one correction has at most 52 rows **and** 52 columns, so a
53-by-53 rank-one odd rectangle cannot exist.

## Exact model and result

Let `X` be `root_lines[8:]` in the pinned
[PROTOTYPE.json](../direct-delivery504-global/inputs/hamming/PROTOTYPE.json).
Its 112 integer rows have squared norm four. Put `R=X/sqrt(2)` and
`G=XX^T=2RR^T`. All transposes are ordinary transposes. Off-diagonal entries
of G are `0,+2,-2`. The binary pairing is `B_ij=(G_ij/2+1) mod 2`.
An **odd-only correction** satisfies `Q_ij=0` unless `G_ij=+2` or `-2`,
equivalently unless `B_ij=0`. Diagonal edits are forbidden.

All ranks below are ordinary matrix ranks over **C**. For a correction with
at most two nonzero columns, the complete classification is:

| Correction | Possible rank of G+Q |
| --- | --- |
| Q=0 | 8 |
| rank(Q)=1 | 9 |
| rank(Q)=2; the two changed columns are orthogonal roots | 10 |
| rank(Q)=2; the two changed columns are an odd root pair | 9 or 10, both attained for every such pair |

There is an exact criterion, not a coefficient search:

```
rank(G+Q) = 8 + rank((56 I - G) Q)             (at most two changed columns).
```

In addition, **every nonzero odd-only rank-one correction**, with no restriction
on its number of columns, gives `rank(G+Q)=9`.

A rank-nine completion requires at least nine rank-one factors, including
cost-zero factors. This is not a lower bound on binary COPY cost or on recursive
child rank. In fact the explicit nine-factor construction below has separate
COPY ranks `(8,8,8,8,8,8,8,8,1)`, totaling **65**; it supplies no COPY improvement.
No optimization over its other factorizations is claimed.

## The boundary construction

For **any** odd pair of columns j,k, let e_j be the j-th coordinate vector and
write `g_j=G e_j`. Set

```
Q[:,j] = -g_j + 4 e_j,
Q[:,k] = e_j,
Q[:,other] = 0.
```

The first column has exactly 52 nonzero entries, all in the odd neighborhood
of j. The second changes only `(j,k)`, another allowed entry. Their supports
are disjoint, so Q has rank two, exactly 53 nonzero rows, and 53 nonzero entries.

The completed column j is `4 e_j`. Every column outside `{j,k}` is unchanged
and those 110 columns span the eight-dimensional root code `C=col(X)`.
Also `e_j` is outside C. All completed columns lie in `C + span(e_j)`.
Therefore the completion has rank exactly nine.

For explicit factors, let A equal `X^T` with column j set to zero and put
`b=4 e_j^T+e_k^T`. Then `G+Q = X A + e_j b`. The last term's diagonal entry
is part of this factorization; the **net correction Q** still has zero diagonal.
The verifier checks every entry of this identity and all nine binary COPY ranks.
The stored witness uses zero-based columns `(0,1)`.

Rank ten is also attainable for every pair: choose two distinct row indices
u,v with `G_uj` and `G_vk` odd, and take `Q=e_u e_j^T+e_v e_k^T`.
Each odd neighborhood has 52 choices. Deleting any two rows leaves X of rank
eight, so `span(e_u,e_v)` meets C trivially. This proves rank ten. The stored
examples cover an odd pair `(0,1)` and an orthogonal pair `(0,3)`.

## Proof of the classification and the 53-row minimum

The certificate establishes four finite facts, by explicit nonzero integer
minors or exact integer identities:

1. `X^T X=56 I_8`. Every root has 52 odd neighbors. For every j, the roots on
   `S_j={i:G_ij is not +2 or -2}` span dimension eight.
2. Deleting any two rows of X leaves rank eight.
3. For all 6,216 unordered column pairs, the roots on `S_j intersect S_k`
   span dimension eight when j,k are orthogonal, and dimension six when
   they are an odd pair. In the latter case their span is precisely the
   perpendicular complement of the two independent roots `X_j,X_k`.
4. For every odd pair, every nonzero complex vector in the pencil
   `span(G[:,j],G[:,k])` has support at least 53, and 53 is attained.

The first three facts give the rank classification. Unchanged columns outside
the two-column support J span C, so the columns of `G+Q` span exactly
`C+col(Q)`. The map `56I-G` has kernel C, giving the displayed rank criterion.
No nonzero allowed column of Q lies in C: such a column would be `Xa`, vanish
on S_j, and force a=0 by fact 1. Thus a nonzero correction adds at least one
quotient dimension. A rank-two correction can add only one or two.
For orthogonal j,k, any vector in `col(Q) intersect C` vanishes on
`S_j intersect S_k`; fact 3 forces it to be zero, so both dimensions are added.

For the 53-row minimum, a failure of additivity needs a nonzero `Xa` in
`col(Q) intersect C`. Only an odd column pair can permit this. By fact 3,
`a` lies in `span(X_j,X_k)`, so `Xa` belongs to the pencil in fact 4.
Consequently its support has at least 53 rows. Its support is contained in
the row support of Q. This proves the minimum, without appealing to a global
root-code distance theorem. The construction attains it. One changed column
has rank at most one and cannot fail additivity, so two columns are minimal too.

Fact 4 covers all complex coefficients by an elementary finite arrangement
argument. A row of a pencil has value `a G_ij+b G_ik`. If at least one of
those two integers is nonzero, it vanishes at precisely one projective
direction `(a:b)=(G_ik:-G_ij)`. Enumerate these primitive integer directions;
all other complex directions have the same support as the generic `(1:3)`.
The certificate records every exceptional direction and its exact support for
all 2,912 odd pairs. Each pencil has minimum 53. This is an exhaustive
classification of zero patterns, not numerical sampling of C.

Finally, for an arbitrary nonzero rank-one correction `Q=u v^T`, the mask
forces `supp(u) x supp(v)` to be an odd rectangle. Each support is contained
in one 52-element odd neighborhood. Fact 1 shows both u and v are outside C.
Both `[X,u]` and `[X,v]` have full column rank nine, so their product
`XX^T+u v^T` has rank nine over C. This proves the unrestricted rank-one claim.

## Certificate and reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/p112-two-column-completion --check-only
python3 -B scripts/research_package.py --package research/p112-two-column-completion
```

Expected replay markers:

```
PASS_P112_TWO_COLUMN_COMPLETION pairs=6216 odd=2912 orthogonal=3304 boundary_rows=53 correction_rank=2 completion_rank=9 controls=8
PASS_P112_TWO_COLUMN_INDEPENDENT integer_minors=12544 pencils=2912 witnesses=5 root_isometry=120
```

The primary checker reconstructs every census record and compares both complete
JSON artifacts. It uses modular elimination only for nonzero-minor lower bounds;
upper bounds come from dimension, orthogonality or exact factorizations.
The separately written checker imports neither the primary nor predecessor
code. It enumerates the standard E8 roots used by PR1447, applies the exact
block transform `(x,y) -> ((x+y)/2,(x-y)/2)`, and checks equality with all 120
pinned root lines up to sign. Thus the two P112 coordinate conventions are
explicitly related; the transformed removed frame is the first eight axes.
It checks **12,544 integer minors** with Bareiss determinants, all **2,912
projective pencils**, and five full correction/completion matrices with
integer elimination over Q. It also recomputes the separate COPY65 invoice.

[CENSUS.json](CENSUS.json) contains all singleton and pair minor witnesses,
pair-deletion witnesses, and pencil strata. [RESULT.json](RESULT.json) contains
summary counts, the canonical census hash, five sparse exact matrices and eight
failure controls. There are 2,912 odd pairs and 3,304 orthogonal pairs. These
implementations are by the same assisted contributor, not independent human
review or proof-assistant formalization.

Both direct checkers support `-I -O -B` and ordinary replay is read-only.
`verify.py --write-to NEW_DIRECTORY` regenerates both certificates without
overwriting existing files; `--write` creates initial certificates in the package. Source bytes and historical provenance are pinned in
[SOURCES.json](SOURCES.json); the registered hook declares both live inputs.
Focused tests exercise exact arithmetic, the mathematical boundaries, malformed
certificates, source changes and a Gaussian-integer completion.

## Scope and attribution

The claim is in [discussion #2006](https://github.com/CrocSwap/integer-mult-bounds/discussions/2006).
The chooser selected `complex-rank-shape-decoder`, priority revision 3, nonce
`46dd6716742415eb113c9b4830c4ada9`, at main
`1ff9c501b624ec354e1330b1b9be571a6adba9cb`. The scope is explicitly **changed**
from physical block-climb synthesis to an algebraic masked-completion boundary.
The original five-percent construction gate is not met. Rank additivity does
not provide a paid local profile, so applying the packing-ceiling calculator to
these ordinary matrix ranks would be invalid. The selected word, its κ and all
predecessor files remain unchanged.

Credit woklerx / PR1447, head `5f784a84bbe80879b5bd7ae9b48dd28a5765863d`,
for the sparse-block theorem and its explicit open masked-boundary question;
DreamingOfClouds / PR717 for the masked decoder model; themilkman216 / PR968
and woklerx / PR1077 for the geometry and complex ordinary-transpose conventions;
and the PR523/514/507/425/433 lineage for the pinned Hamming/root data.
This account's PR1375, and PR1331/1432/1468/1473, concern separate COPY costs
under restricted factor mixing. This result concerns completion matrix rank
and does not repeat or extend those COPY lower bounds. No pending PR code is
imported. Source licenses and notices are retained; new material is Apache-2.0.

## Open next questions

Does another exact factorization of the displayed
53-by-2 completion improve on its direct COPY65 bill, perhaps approaching or
beating the original COPY64 decoder? A feasible first step is to parameterize
its rank-nine factors in the fixed nine-dimensional column and row spaces,
then check exact identities and all support-pairing ranks under candidate
basis changes. The blocker is the coupled support-sensitive factor search;
rank nine alone proves no COPY saving. Even a favorable COPY bill would still
need source access, frames, dirty-state restoration, hosting, precision/tape,
complete recursive pricing and the inherited all-size/analytic obligations.
Those obligations, a full selected cold replay, Lean, hosted CI and independent
human review have not been supplied. Structured next questions and overlap
context are recorded in [TASK.json](TASK.json).

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
