# Paired query blocks cannot supply six minimal commuting stages at defect two

**Scoped obstruction; no new κ.** This addendum tests a proposed use of
synchronized pairs of native copies sharing one fresh body variable. The
aggregate query has rank two and its proposed productive stage has rank four.
The following theorem permits arbitrary other queries, ordinary changes of
basis, and arbitrary mixing within the four-dimensional productive stages.

## Statement

Let the ground field have characteristic different from two. On n independent
coordinates, let

\[
R_i=X_iY_i,\qquad Y_iX_i=0,\qquad
\operatorname{rank}X_i=\operatorname{rank}Y_i=r_i,
\]

and suppose the complete chronological query word satisfies

\[
(I-2R_s)\cdots(I-2R_0)=-I_n.
\]

Define the **rank defect** by

\[
\delta=\sum_{i=0}^{s}r_i-n.
\]

Assume δ=2. Select full positions with r_i=2, each supplied with a rank-four
idempotent P_i satisfying P_iR_i=R_iP_i=R_i. If these P_i commute pairwise,
there are at most five selected full positions.

No actual-prefix commutation is needed for this theorem. Consequently it
also applies to the stronger caller contract requiring that commutation.
In particular, nine rank-two full blocks formed from eighteen native copies
cannot have commuting rank-four productive stages at rank defect two,
regardless of the number or placement of thin rank-one queries.

This concerns the explicit square-zero block model. It does not classify
arbitrary shared-variable calls whose aggregate query is not square-zero,
higher rank defect, paid higher-rank stages, or noncommuting outputs. The
bound five is not claimed sharp.

## 1. Defect two fixes the cross-Gram blocks

Stack X by block columns and Y by block rows. Put L=Σr_i, G=YX, and

\[
A=I_L+2\operatorname{lower}_{\mathrm{block}}(G).
\]

The same ordered-product expansion as the scalar query-defect identity gives
product(I−2R_i)=I_n−2XA⁻¹Y. Thus XA⁻¹Y=I_n. The matrix Q=A⁻¹YX is an
idempotent of rank n, so

\[
H=A-G=A(I_L-Q),\qquad \operatorname{rank}H=L-n=2.
\]

Its diagonal blocks are I_(r_i), and H_ij=sign(i−j)G_ij off the diagonal.
Factor H=UV through a two-dimensional space. The block factors obey
U_iV_i=I_(r_i). At every selected rank-two position, U_i and V_i are
inverse square matrices. The factor gauge X_i↦X_iU_i and Y_i↦U_i⁻¹Y_i
leaves R_i unchanged and makes both of its defect factors equal to I₂.
Therefore selected positions have

\[
Y_iX_j=\operatorname{sign}(i-j)I_2\quad(i\ne j),
\qquad Y_iX_i=0.
\tag{1}
\]

This step includes every other query in A, G and the rank defect. It does
not omit the cost or rank of thin queries. The block extension retains the
query-defect mechanism of CrocSwap/integer-mult-bounds#6832; no new claim of
priority is made for that mechanism.

## 2. Six selected queries require twelve dimensions

Take six selected positions in chronological order. Their Gram is S₆⊗I₂,
where S₆[i,j]=sign(i−j). This matrix has rank twelve over every field: the
integer inverse of S₆ has entries (−1)^(i+j)sign(i−j), using zero-based
indices. Hence the twelve query columns span twelve independent dimensions.
Every supporting stage union must contain them.

Commuting idempotents admit a common coordinate basis over the ground field
by successively splitting into images and kernels. In this basis each P_i
has a four-element support C_i. The support equations imply P_iX_i=X_i
and Y_iP_i=Y_i because the query factors have full rank. Consequently the
rank-two product in (1) passes through C_i∩C_j, giving

\[
|C_i\cap C_j|\ge2\qquad(i\ne j).
\tag{2}
\]

We show that six such supports satisfying (1) have union of size at most
ten, contradicting the twelve-dimensional requirement.

## 3. The set-family bound away from a common pair

Consider m four-element supports satisfying (2), allowing repetitions. If
every pair intersects in at least three elements, fixing one support shows
that each later one adds at most one element. The union has size at most m+3.

Otherwise choose C₁=A∪B and C₂=A∪C, where A, B and C are disjoint pairs.
If every support contains A, proceed to Section4. Otherwise choose E missing
at least one element of A. Meeting C₁ and C₂ twice forces E to contain at
least three elements of their six-element union, or all four if E misses
both elements of A. Thus T=C₁∪C₂∪E has size at most seven.

Any further support D adds at most one element to T. If it added two or
more, its at most two old elements would have to be exactly A to meet C₁
and C₂ twice. It would then meet E at most once, contradicting (2). Therefore

\[
\left|\bigcup_i C_i\right|\le 7+(m-3)=m+4.
\tag{3}
\]

## 4. The ordered signs bound the common-pair case

Suppose every support contains a fixed pair A, and write E_i=C_i∖A. The
two-element outside sets E_i form the edges of a graph.

That graph cannot contain three pairwise disjoint edges E_i, E_j, E_k.
Order their query indices i<j<k. Their stage intersections are exactly A.
Let α_l=X_l[A,:] and β_l=Y_l[:,A]. These square two-by-two matrices are all
invertible, since their cross-products in (1) are invertible. The equations

\[
\beta_i\alpha_j=\beta_i\alpha_k=-I_2,\qquad
\beta_j\alpha_i=\beta_k\alpha_i=I_2
\]

force α_j=α_k and β_j=β_k. But then β_jα_k=β_kα_j, whereas (1) requires
the first product to be −I₂ and the second I₂. Characteristic different
from two rules this out.

Thus the outside graph has matching number at most two. If it has v incident
vertices, e distinct edges and c connected components, then v≤e+c: every
component has at least its vertex count minus one edges. Selecting one edge
in every component gives c≤2. Since e≤m, including repeated supports,

\[
\left|\bigcup_i C_i\right|=2+v\le2+e+2\le m+4.
\tag{4}
\]

For m=6, both cases give union size at most ten. This contradicts the rank
twelve Gram and proves the theorem.

## Exact controls and the limits they check

Run `python3.12 -I -B verify_paired_defect.py` or its optimized `-O` variant.
Both return `PASS_PAIRED_DEFECT_TWO_STAGE_CAP`. The verifier uses only the
Python standard library and exact rational or finite-field arithmetic.

It verifies the integer sign-matrix inverse, 671 normalized set-extension
cases, extremal ten-coordinate families in both set-family cases, and
repeated supports. A three-full-block defect-two root with stages I₄ is a
positive control, showing the hypotheses are nonempty.

The omission controls are mathematical boundary examples. A literal
seven-block defect-two root on twelve coordinates admits six rank-four
supporting projectors with eleven noncommuting pairs; the commutation gate
rejects it. A characteristic-two sunflower realizes six rank-two queries
with the stipulated Gram and commuting rank-four supports on fourteen
coordinates. This latter example concerns the isolated Gram/support lemma,
not a native caller: it shows why the sign contradiction needs its stated
characteristic restriction. An altered sign-matrix inverse is also rejected.

The universal theorem is proved above; these finite checks are controls of
its premises and algebra, not a finite-search impossibility claim. The
optimistic positive cost margin for nine rank-four stages cannot yield a
caller because those stages do not exist in this model. No κ is changed.

Prepared for @CubeJerry with substantial OpenAI GPT-6 Astra Pro assistance.
Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Credit the retained query/controller lineage and the defect identity in
CrocSwap/integer-mult-bounds#6832. Related coupled geometry in
CrocSwap/integer-mult-bounds#6773 and #6781 concerns different four-field
stage budgets. The set-family/sign obstruction above is the present addition.
