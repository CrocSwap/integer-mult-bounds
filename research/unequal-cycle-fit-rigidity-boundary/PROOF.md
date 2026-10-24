# Half-total rigidity and the first unequal-width C5 boundary

## Contract and attribution
Let n=2k+1>=5, over an arbitrary field F, with positive integer widths d_i
and S=sum d_i. Indices are cyclic. A fitting matrix M has diagonal blocks
I_{d_i} and zero ordered blocks between distinct nonadjacent vertices. Allowed
neighbor blocks need not be symmetric, invertible or commuting. Local similarity
means M -> L M L^{-1} for block-diagonal invertible L.
An integral edge/private form assigns x_i nonnegative integer shared channels to
edge (i,i+1) and p_i private channels to vertex i, with
x_{i-1}+x_i+p_i=d_i. Each shared channel is a J_2 all-ones block; each private
channel is [1], after regrouping coordinates by vertex.

JoyboyBrian's PR5023, `odd-cycle-query-capacity/PROOF.md`, proves the minimum
rank max(alpha_d(C_n),ceil(S/2)) over every field and constructs integral
edge/private attainers. We use that rank value, not claim it anew. Nick Petalas's
PR5180, `odd-cycle-fit-rigidity/PROOF.md`, proves all-field width-two rigidity
and explicitly asks about unequal widths. Its intersection argument and the
older PR3248 C5 edge-line argument motivate the following extension. The new
statement classifies every half-total equality case and answers that open
question with the sharp positive-width boundary. These are algebraic fitting
matrices, not physical decoders or a multiplication theorem.

## The universal half-total theorem
If rank(M)=S/2, then M is locally similar to an integral edge form with no
private channels. Its edge multiplicities are uniquely determined by
x_{i-1}+x_i=d_i. Conversely every such nonnegative integral edge form has
rank S/2 over every field. Thus the assertion is conditional on equality,
not a claim that every width vector permits equality. In particular S must
be even. The proof also works with zero widths and empty coordinate spaces.

Factor M=A B through V=F^r, r=rank M, with A injective and B surjective.
Write A_i:V->F^{d_i}, B_i:F^{d_i}->V and U_i=im B_i. Since A_i B_i=I,
B_i is injective, dim U_i=d_i, and A_i is injective on U_i. Also A_i kills
U_j whenever i,j are distinct and nonadjacent.
Put H_i=U_i intersection U_{i+1} and t_i=dim H_i.
The two neighbors i-1,i+1 are nonadjacent, so U_{i-1} intersection U_{i+1}=0:
apply A_{i-1}, which is injective on the former and kills the latter.
Consequently H_{i-1} direct-sum H_i is contained in U_i, and

    t_{i-1}+t_i <= d_i;       sum_i t_i <= S/2.                 (1)

For each i take J_i={i,i+1,i+3,i+5,...,i+2k-1}. Its induced graph is one
edge and k-1 isolated vertices. The subspaces U_j for its isolated vertices
are independent of one another and of U_i+U_{i+1}: apply their respective
A_j to a putative relation. Therefore

    r >= sum_{j in J_i} d_j - t_i.                            (2)

Every vertex occurs k+1 times among the n rotated sets. Summing (2) and
using (1) gives n r >= (k+1)S-sum t_i >= nS/2. If r=S/2,
sum t_i=S/2, and all nonnegative slacks in (1) vanish. Hence

    U_i = H_{i-1} direct-sum H_i.                             (3)

For a vertex j not incident to edge i, at least one endpoint of that edge
is a nonneighbor of j (n>=5). Thus A_j kills H_i. If sum_i h_i=0 with
h_i in H_i, applying A_j yields A_j(h_{j-1}+h_j)=0. The argument lies
in U_j, so injectivity and (3) give h_{j-1}=h_j=0. This holds for all j.
Thus all the H_i are globally independent, and since sum dim H_i=r,

    V = direct-sum_i H_i.                                   (4)

Choose a basis in each H_i. Let C_i include the incident edge coordinates
H_{i-1} direct-sum H_i into V in this basis. Equation (3) gives
B_i=C_i T_i for an invertible T_i. A_i is zero on all other H_j and
A_i C_i=T_i^{-1}; hence A_i=T_i^{-1} C_i^T, where C_i^T is the coordinate
projection (no inner product is assumed). Therefore

    M_ij = T_i^{-1} (C_i^T C_j) T_j.

The middle blocks are exactly the edge-channel form D, proving the claimed
local similarity. Odd cyclic equations x_{i-1}+x_i=d_i have at most one
integer solution: differences alternate sign around an odd cycle, so twice
each integer difference is zero. This dimension argument is over the integers,
even when the underlying field has characteristic two. The converse follows
because every J_2 has rank one over every field. As consequences, M^2=2M
and its characteristic polynomial is X^{S/2}(X-2)^{S/2}, interpreted in F.
Characteristic two does not invalidate the normal form or rank.

## Sharp positive unequal-width C5 boundary over Q
Every positive unequal five-tuple has S>=6. At S=6 it is a cyclic rotation
of (2,1,1,1,1); its independent-set weight is 3. The inherited rank formula
therefore gives minimum rank 3=S/2, and the universal theorem classifies
*every* optimum. Thus no positive unequal-width counterexample has S<7.

For S=7 use widths (1,1,1,2,2). In Q^3 take rows

    v1=(1,0,0), v2=(1,1,-1), v3=(0,1,0),
    v4=(0,1,1), v5=(1,0,1).

Let G_ij=(v_i dot v_j)/(v_i dot v_i). The row divisors are 1,3,1,2,2.
All nonedge dots are zero; each of the five cycle-edge dots is one; the
diagonal is one. The vectors span Q^3 and their real Gram matrix has rank
three (or use the exact rational elimination supplied), so rank G=3.
Adjoin a J_2 channel on vertices 4 and 5, and regroup the seven coordinates
by vertex. This gives a fitting matrix M of rank 4. The inherited lower
bound ceil(7/2)=4 proves it is a minimum-rank fit. Both ordered blocks on
each edge are nonzero, with ranks (1,1,1,2,1) around the cycle.

Local similarity preserves every ordered block rank. Any integral
edge/private form with all five edges nonzero has x_i>=1 on all five
edges, hence uses at least 2 sum x_i>=10 ports, impossible at S=7.
Therefore this optimum is not locally equivalent to any integral
edge/private form. This proves the smallest total width is exactly seven
among positive unequal C5 widths over Q. It does not classify all total-seven
profiles or all their optima, nor assert an all-field version of this witness.

## Zero widths are a different boundary
If zero widths are admitted, the smallest total is three, not seven.
For widths (1,1,1,0,0), use the fitting matrix on its three occupied ports

    [ 1    1    0 ]
    [ 1/2  1  1/2]
    [ 0    1    1 ].

Its rank is two, which is optimal by the independent pair {1,3}. Both
incident edges at the middle width-one vertex are nonzero, impossible in
an integral edge/private form; local block-rank invariance again applies.
For S<=2, the empty or single occupied vertex is an identity block. Two
unit vertices that are nonadjacent give I_2; if adjacent, a minimum-rank
fit is [[1,a],[b,1]] with ab=1, sent to J_2 by the local similarity L=diag(a^{-1},1).
This exhausts nonnegative widths at those totals and proves minimality.

## Evidence, costs and limits
The universal proof above is symbolic and field-independent. The standard-
library Fraction verifier checks the exact two rational witnesses, all ordered
masks and edge ranks, lower bounds, finite normal-form examples and genuine
negative controls. Those fixtures do not prove universal classification.
An elementary explicit S by S rational matrix costs S^2 field entries; ordinary
Gaussian elimination uses O(S^3) field operations and O(S^2) stored entries.
Bit complexity depends on entry heights and is not claimed bounded uniformly.
The proof's basis choices are existence arguments; this package supplies no
physical tape implementation, decoder schedule, centre copy/restore supplier,
recursive child cost, real numeric stability bound, or improvement to kappa.
No growth or full multiplication claim follows from these rank statements.

## Open next questions
Which odd-total optima outside the half-total equality regime admit a useful
classification beyond edge/private channels? In particular, classify total-seven
C5 fits up to local similarity, rather than infer a universal classification from
one witness. A physical decoder using the new noncanonical interface must pay
for its basis changes, queries, copies and restoration before a family expansion.
