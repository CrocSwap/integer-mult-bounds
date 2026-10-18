# Exact lookup for triple-line source complements

This note isolates one bounded part of the source-factor compiler for the
bit construction in `upstream/build/sections/03-motifs.tex`: the exact
rational alphabet of its ordered elimination. The source form, triple
lines, and neighboring relation come from the pinned original OpenAI
manuscript preserved under `upstream/` in this repository, maintained by
Douglas Colkitt. The upstream motif section credits the underlying
degree-one intersection construction to Alon (1998, Section 3,
remark after Theorem 1.1).
The contraction argument and certificate below were developed in an
unpublished local Tintagel audit packet. The complete proof and checker
needed for this scoped claim are reproduced here. This contribution
does not assert a new multiplication exponent or a physical provider.

## Statement

Let \(h\geq3\) (\(h\geq5\) if \(T\) is present), let
\(S\subseteq\{0,\ldots,h-1\}\) have size three, and optionally let
\(T\) also have size three with \(|S\cap T|=1\). Set
\(G=I-J/9\) and \(u_L=1_L\) for each chosen triple. For \(r=1\) or \(2\),
form \(U=[u_S]\) or \(U=[u_S,u_T]\) and \(V_L(j)=(3\,1_{j\in L}-1)/6\).
The rational source complement is \(A=I-UV^{\mathsf T}\). Process rows in
ascending order, choosing the **rightmost nonzero unused column** of each
row. For a pivot \(p=A_{i,c}\), update nonzero earlier unused columns
\(j<c\) by \(C_j\leftarrow C_j-A_{i,j}C_c/p\), clear nonzero entries below
the pivot with row operations, then normalize the pivot row. Record the
initial matrix, every completed scalar update, pivot, and operation
coefficient. `replay.py` specifies this exact reference order.

**Computer-assisted theorem, conditional on that reference semantics.** For every
such \(h,S,T\), all recorded matrix values belong to the 20-element
`VALUES` table and all nonzero column, row, and normalization
coefficients belong to the 17-element `COEFFICIENTS` table in `replay.py`.
The reference processes exactly \(h\) rows and has \(h-r\) pivots. In
particular this applies to every valid \(h=100\) one-line or neighboring
two-line source input. This is an exact-rational statement about the
reference and lookup domain. It is not a Lean theorem or an execution of
all physical input tapes.

## Projector and rank

Since \(Gu_L=u_L-\mathbf1/3\) and
\(u_K^{\mathsf T}Gu_L=|K\cap L|-1\), the selected line Gram matrix is
\(U^{\mathsf T}GU=2I_r\). The corresponding projection coefficient is
\(V_L=Gu_L/2\). For any triples \(L,K\),
\[
V_L^{\mathsf T}u_K=(|L\cap K|-1)/2.
\]
Thus \(V^{\mathsf T}U=I_r\), including the neighboring two-line case.
Consequently \(A^2=A\), \(\ker A=\operatorname{im}U\), and
\(\operatorname{rank}A=h-r\). The coefficient is \(+1/3\) inside a
triple and \(-1/6\) outside; the latter sign means an exterior column
starts as \(e_j+(u_S+u_T)/6\) in the two-line case. These signs matter
to the contraction below. This projector identity does not rely on
nondegeneracy of the ambient form at every auxiliary height.

At each pivot, updates to unused columns left of the chosen column
zero the pivot-row entries there. Entries to its right are zero by
the rightmost rule, while previously pivoted columns were already
cleared below. The pivot row is therefore exactly \(p e_c\) after
the column updates. Each row clear changes only column \(c\) in the
target row. Column updates, row clears and normalization preserve
rank; the final matrix is a partial permutation matrix with one unit per pivot.
Its rank is thus the pivot count \(h-r\). The reference loops over
exactly \(h\) rows.

## Adjacent-exterior contraction

Call indices outside \(S\cup T\) *exterior*. Let \(a<b=a+1\) be
adjacent exterior indices. Compare the full elimination with the run
obtained by deleting coordinate \(a\) and order-preservingly relabeling
the rest. The comparison is made after complete pivot blocks, not in
the middle of separate column updates.

Before row \(a\), induction over earlier complete blocks gives:

1. Row \(a\) remains \(e_a\) and column \(a\) has not pivoted.
2. If column \(b\) is unused, row \(b\) remains \(e_b\); columns \(a,b\)
   agree at **every other retained row**, including transformed exterior
   rows.
3. If column \(b\) has pivoted, its row \(b\) has entry \(-1\) in
   column \(a\); all other rows outside \(a,b\) have zero there.

Initially these properties follow from the exterior-column formula.
The full matrix's initial extra row and column entries are already
in the contracted initial matrix or among \(0,1\).
An earlier pivot column \(c<a\) does not target \(a,b\). When \(c>b\),
their equal entries in the pivot row force equal column coefficients
while \(b\) is unused; row \(a,b\) have zero in \(c\), so clearing below
does not change them. The rightmost rule therefore cannot select \(a\)
while \(b\) remains an eligible identical entry. If \(c=b\), the
column-\(a\) coefficient is \(-1\); it clears column \(a\) in every
other retained row and leaves \(-1\) in row \(b\). The ensuing
row-\(b\) clear removes the pivot-column entry there and leaves its
column-\(a\) entry equal to \(-1\); its other retained entries need
not be zero. Later earlier-row blocks preserve this column-\(a\)
invariant: every earlier candidate pivot row has zero in column
\(a\), so it neither pivots there nor makes a column update targeting
it; row clears also preserve that column's entries. This rules out a
pivot at \(a\) after \(b\) has pivoted.
There is no pivot index strictly between
\(a\) and \(b\).

The column condition must not be strengthened to a unit-row claim.
For \(h=5\), \(S=\{0,1,2\}\), \(a=3\), \(b=4\), the first pivot is
\((0,4)\), and its complete block leaves row \(4\) equal to
\((-4,2,2,-1,0)\), not \(-e_3\). `replay.py` checks this exact
counterexample. Every later use above and below concerns column \(a\)
or entries retained after deleting \(a\); neither requires the other
entries of row \(b\) to vanish.

At row \(a\) the pivot value is \(1\). Its block changes no retained
matrix entry. If \(b\) is unused, the row-\(a\) clear at each later row
uses \(-A_{i,b}\), exactly the coefficient of the contracted row-\(b\)
block. This includes previously transformed exterior rows. If \(b\)
has pivoted, only row \(b\) has a nonzero entry in column \(a\), and
the clear has coefficient \(+1\). Prior column updates targeting \(a\)
duplicate the corresponding column-\(b\) arithmetic or use \(-1\);
normalization adds only \(0,1,-1\). The omitted typed block consists of
column updates targeting \(a\), row-\(a\) clears, row-\(a\)
normalization, and its pivot marker. Omitting only the marker would not
give the contracted run. After deleting that block, retained matrix
states, later pivot choices, and operations agree in order. The full
run's extra values and coefficients are therefore either in the
contracted run or among \(0,1,-1\).

Delete the left member of every adjacent exterior pair until each gap
before, between, and after support indices retains at most one exterior
index. This is a height-independent induction. A one-line support has
three labeled positions and four gaps, giving \(2^4=16\) forms. A
two-line support has five positions labeled one intersection `X`, two
`A` only, and two `B` only: \(5!/(2!2!)=30\) orders and \(2^6=64\) gap
masks, giving 1,920 forms. Every normal form has height at most 11.

## Finite certificate and replay

Run from the repository root with Python 3 and no package installation:

```sh
python3 -I -B research/tintagel-source-lookup/replay.py --stress
```

The script constructs all 1,936 forms over exact `Fraction` values and
checks the explicit 20/17 tables, 65,416 word records, 11,584 pivots,
and digest `adf555d553a11c9f2862ddf6a7206fd03428ec657763f60f9aecfc6d4850ec7d`.
It also checks the nonunit row-\(b\) counterexample to guard the proof
against an invalid strengthening of the column invariant.
The optional stress flag checks all 6,090 neighboring two-line inputs
at heights 7–9 against their compressed forms. The stress is finite
corroboration; the induction supplies the all-height step. The program
records completed scalar updates, so it does not certify the internal
states or time of a machine implementation of rational arithmetic.

## Scope and provenance

The base triple-line geometry and source schedule are attributed to
the cited original OpenAI manuscript and its upstream references;
Douglas Colkitt maintains the repository and its community research.
The local v9
Tintagel packet, frozen at SHA256
`1978c40c7b5f23a818096df10f713e23d95b7f27a1e97550093d2ce3e02cbb09`,
contains the corrected sign and all-row contraction proof. An
independent local audit accepted that paper argument and separately
replayed the finite certificate. This unpublished provenance is not
itself publicly reproducible; the argument and exact checker needed
for the present claim are included here. See `CLAIM-AND-SOURCE.md` for
evidence boundaries.
This package was prepared with substantial AI assistance.

The result only closes the exact source lookup for the specified
one/two-line complements. General-width setup, the recursive Q>11
pivot child, heterogeneous bank consumer, packed entry, arbitrary
phase/native/root composition, physical cost, and all-size physical
execution remain open. The broader fixed-\(W\) grouping, its
S0-transformed-input premise, and exceptional
\(M A^3+\delta M A(R+A)\) terms are not addressed by this note. No global
multiplication theorem or new \(\kappa\) follows from this note.
