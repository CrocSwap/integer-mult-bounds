# Endpoint dimension and the cost of linear lifts

All vector spaces in Sections 1--3 are over the field with two elements.
The ambient form is symmetric and nondegenerate. An endpoint subspace is
nondegenerate for the restricted form. Alternating endpoint planes are allowed.
No positivity assumption is used.

## 1. The graph and two exact certificates

Use the 112 binary ports in the selected canonical word. Join distinct
ports a,b when their binary dot product is zero. This is the P112
source/target interaction graph used by the retained scalar identity.
It has 5,824 ordered edges. Each vertex has a label t_a in dimension 9,
with nondegenerate symmetric form S=I9, such that

    t_a^T S t_a = 1;    t_a^T S t_b = 0 on every graph edge.

The verifier reads the selected source bytes, checks all 12,544 binary
pairings, and checks the following two certificates. No graph isomorphism
to a different port model is assumed.

**Certificate A.** The edge tensors `t_a tensor t_b` have rank 80 in the
81-dimensional matrix space. The 80 listed edges form a basis. S is a
nonzero null vector, so every bilinear form K that vanishes on graph edges
is `K = c S`.

**Certificate B.** There is an eight-vertex clique with vertices a_0,...,a_7.
There are 24 further vertices b_ij, one for each edge ij of a graph J on
eight points. J is K8 with one perfect matching removed. Vertex b_ij is
adjacent to every a_k except a_i,a_j. Two b vertices are adjacent exactly
when their J edges have a common endpoint. In particular J is 6-regular.
The certificate lists the 32 distinct vertices. The verifier checks every
required and absent edge, rather than accepting a claimed graph name.

The certificates are finite premises of the following all-size arguments.
The verifier is not a proof-assistant formalization of those arguments.

## 2. Sharp dimension bound for arbitrary two-plane labels

Suppose each graph vertex is assigned a nondegenerate two-dimensional
subspace U_a in an h-dimensional space, and graph edges give orthogonal
subspaces. The assignment need not depend linearly on the old labels.
Then **h >= 18**. The binary tensor construction `U_a = t_a tensor F2^2`
in the form `S tensor I2` attains 18.

The eight anchor planes in Certificate B are mutually orthogonal. Their
orthogonal direct sum E has dimension 16. Thus h >= 16. Put
`H = E_0 perpendicular ... perpendicular E_7 perpendicular Z`.
For h <= 17, the dimension z of Z is zero or one. The plane U_ij lies in
`E_i + E_j + Z` because it is orthogonal to the other six anchor planes.

Choose any basis for each U_ij. Its nondegenerate 2-by-2 Gram matrix is D_ij.
Let K_ij,i be the Gram matrix of its projection to E_i, and let R_ij be
the Gram matrix of its projection to Z. Thus

    D_ij = K_ij,i + K_ij,j + R_ij.                 (1)

For a fixed i, collect the six incident planes in one matrix. Their E_i
projection has a Gram matrix K_i of rank at most two. Their Z projection
has a Gram matrix R_i of rank at most z. Distinct incident planes are
orthogonal, and their other anchor blocks differ. Therefore the off-diagonal
blocks of K_i and R_i agree. Hence

    H_i = K_i + R_i

is block diagonal, with blocks `H_ij,i = K_ij,i + R_ij`, and

    sum_(j:ij in J) rank(H_ij,i) = rank(H_i) <= 2 + z.       (2)

If z=0, (1) gives `2 <= rank(H_ij,i) + rank(H_ij,j)`.
Summing over 24 edges contradicts (2): `48 <= 16`.

If z=1, choose the unit basis of Z. Write its coordinate row on U_ij as
u_ij, so `R_ij = u_ij^T u_ij`. Characteristic two gives

    D_ij = H_ij,i + H_ij,j + u_ij^T u_ij.

Thus `rank(H_ij,i) + rank(H_ij,j) >= 1`. Summing over J and using (2)
gives equality throughout: the total is 24, every vertex contributes 3,
and every edge contributes 1. Also every u_ij is nonzero; otherwise its
edge would need a contribution at least 2.

At each vertex i there are therefore three rank-one diagonal blocks in
H_i and three zero blocks. Let u_i be the concatenation of its six rows
u_ij. It has a nonzero component at every zero block. Consequently
`u_i^T` is not in the image of H_i. A rank-one update by this vector
cannot reduce rank: if `(H_i + u_i^T u_i)x=0`, then
`H_i x = u_i^T (u_i x)`. Since `u_i^T` is not in the image of H_i,
we have `u_i x=0` and `H_i x=0`. The new kernel is contained in the old
kernel. Hence

    rank(K_i) = rank(H_i + u_i^T u_i) >= rank(H_i) = 3,

contrary to `rank(K_i) <= 2`. This excludes h=17 and proves the bound.

This theorem fixes the least ambient dimension. It does not classify all
dimension-18 assignments or bound the cost of every new word on them.

## 3. Rigidity of all coupled linear lifts

Let V have dimension r >= 1. Let `A: F2^9 tensor V -> H` be linear and
write `A(t)v = A(t tensor v)`. Assume all spaces `A(t_a)V` have dimension
r and a nondegenerate restricted form. Require them to be orthogonal on
every graph edge. There is no block-diagonal or independent-copy assumption.

For v,w in V, the function

    K_(v,w)(x,y) = <A(x tensor v), A(y tensor w)>

is a bilinear form on the old nine-dimensional space and vanishes on all
graph edges. Certificate A gives a scalar D(v,w) such that

    K_(v,w)(x,y) = (x^T S y) D(v,w).              (3)

Linearity shows that D is bilinear. Symmetry of the ambient form shows
that D is symmetric. At any vertex t_a, (3) restricts to D because
`t_a^T S t_a=1`. Nondegeneracy of the endpoint makes D nondegenerate.
Thus the pullback Gram matrix of A is `S tensor D`, of rank 9r.
The map A is injective, its image is nondegenerate, and h >= 9r.

For every old subspace U, its image is `A(U tensor V)` and has dimension
`r dim(U)`. Intersections, sums and orthogonal complements inside this
image are the old ones tensored with V. This proves rigidity for every
fibre size, every ambient dimension, and all linear couplings.

## 4. The complete accounting class

The cost conclusion concerns an endpoint lift of a fixed complete supplier
and controller diagram. This condition matters. It does not cover a new
scalar program or a new controller that reuses stages in a different way.

The reference diagram includes every source-access edge, helper edge,
copied-centre edge, restoration edge and idle child. It has ambient width m,
W live role streams of equal volume, and paid edge ranks t_e. Each scalar
gate uses a common exact frame on all its incident streams. In the selected
instance, `m=73`, `W=14336`, and the complete histogram is

    {1:349604, 2:60192, 3:62585, 4:20448,
     5:11808, 7:7, 8:1152, 48:4866}.

The linear lift replaces the old core by its r-fold tensor image. In the
retained nine-stage orthogonal-slot controller, this has width 73r. At each
retained boundary, the lifted subspace has intersection with this core equal
to the image of the old boundary subspace. Additional ambient coordinates
are permitted, with arbitrary slanted subspaces, nonmonotone transitions,
and extra gates. Their entrance quotient dimension is zero and their final
quotient dimension is their full width on every live role. The complete
auxiliary/centre ledger must also be retained. An auxiliary input does not
become a known-zero input. All W physical live streams persist through the
serialized schedule. A local role can use a different owner in a later call;
this does not move a physical stream path to a private centre. Each scalar
operation has the same frame before and after on each incident live path.
Private centre paths can start and end at different padding dimensions.
Their costs are nonnegative. They are not used in the signed sum below.

Each individual retained role-stream edge may use any exact native
factorization, with any number of rank-zero adapters. Joint children that
encode several arrays or combine different frozen edges are outside this class. No assumption that its old child is run r times is
made. Each native child acts on the original role-stream volume; creating
extra role streams does not create extra normalization weight. A factorization
that crosses a retained scalar-gate boundary changes the reference diagram
and is outside this class.

### Source-bound minimum-rank bridge

The selected archive is `research/community-frontier1094-audit/selected-replay.tar.gz`
at the base commit in SOURCES.json. The verifier reads five exact members from
this Git object. It does not use historical files with similar names. Each
member has a SHA256 pin in CERTIFICATE.json.

The source frame lemma in `notes/general-clifford-frames.tex` gives

    rank B(T_V T_U^(-1)) = dim U + dim V - 2 dim(U intersect V).

This is an exact Fourier-rank identity. It applies to degenerate U and V,
and does not require the operators T_U and T_V to commute. The verifier
checks that this note has the same bytes as the copy in the selected source
manifest. Reverse/complement words preserve the same transition distance.

For each of the two emitted local programs, the verifier reads every `climb`
and `center` edge and computes this distance from its actual binary frame
bases. It checks equality with the paid rank, not only a lower bound. There
are 3,494 edges per orientation. All eight private-centre edges go between
the specified rank-eight centre frame and the zero frame. Each has minimum
rank eight. Copying the centre value at its high frame does not erase that
transition. The total local rank mass is 5,586.

The selected global controller contains 144 complete calls. Its 704 local
roles per call have distinct owners in the live range [0,14336); the private
centre range is separate. The verifier checks this assignment, the complete
per-replica event order, and the final live-family range. Thus changing a
helper's owner between calls changes the local role name, not the identity
of a physical stream. The selected owner audit supplies the inherited exact
chart and busy-window validity. This package does not repeat that audit.

For each of the 7,526 idle children, the verifier reads the actual remainder
axes, checks the matching controller row, and checks that they are the exact
suffix of the inherited pending axes. It checks that their Gram matrix is
identity. This is a coordinate Fourier child on that subspace, so its minimum
rank is the number of these axes. Its entrance and exit frames have this
exact distance. The idle histogram is `{1:2276, 3:377, 7:7, 48:4866}`.
Adding the 144 literal local histograms gives the full histogram above and
rank mass 1,041,408. All 510,662 reference native children are included.
There is no unexamined histogram entry that could conceal an overcharged
reference transition.

Exact scalar identities, phases, source wrappers, and the controller's charts
remain inherited from the selected review. The fresh check covers ranks and
stream accounting; it is not a cold replay of the supplier or compiler.

## 5. No native factorization or ambient padding improves the moment

Write `p=1-b`, with `0<p<=1`, and

    M(p) = (1/W) sum_e (t_e/m)^p.

First consider no additional coordinates. Section 3 multiplies each
boundary transition distance by r. Fourier rank is subadditive under exact
Clifford composition: the B block of a product is `A1 B2 + B1 D2`, whose
rank is at most `rank(B1)+rank(B2)`. Thus a factorization into ranks k_j
has `sum_j k_j >= r t_e`. Since `sum_j k_j^p >= (sum_j k_j)^p`, its
moment charge is at least `(r t_e/(rm))^p = (t_e/m)^p`.
One rank-r t_e child attains this lower bound whenever it is available;
granting it for free as an interface is an optimistic relaxation otherwise.

Now add z>0 ambient coordinates. Put `M'=rm+z` and `lambda=rm/M'`.
At a boundary B let q_B be its dimension outside the tensor core.
For an old edge U->V, let `d_e=|q_V-q_U|`. The subspace distance satisfies

    distance(U',V') >= r distance(U,V) + d_e.     (4)

To see this, the core part of `U' intersect V'` has dimension
`r dim(U intersect V)`, and its quotient part has dimension at most
`min(q_U,q_V)`. Substitute in `dim U' + dim V' - 2 dim(U' intersect V')`.
This proof allows slanted frames and does not assume an orthogonal splitting
at each gate. The same native-factorization argument bounds an edge's charge
below by `((r t_e+d_e)/M')^p`.

Sum signed q changes separately along each physical live stream. Scalar
operations do not change q on that path. This includes a copy from a live
stream to a private centre: it creates a private value but preserves the
live path and its frame. Rank-zero adapters preserve the preimage frame.
The native transitions on each live path therefore have net change z.
Their absolute changes sum to at least z. Summing the W live paths gives
`sum_e d_e >= Wz`, before any private-path cost is added. Private descents
cannot cancel this lower bound. New edges have old rank zero. Also
`0<=d_e/z<=1`. Concavity gives, edge by edge,

    ((r t_e+d_e)/M')^p
      >= lambda (t_e/m)^p + (1-lambda) (d_e/z)^p.

Summing, and using `x^p>=x` on [0,1], gives

    M_lift(p) >= lambda M(p) + (1-lambda).        (5)

If the reference moment is at least one, the lifted moment is at least one.
This includes arbitrary padding size, all extra transitions and every native
factorization at the retained boundaries. The unpadded tensor lift attains the
same moment in the ideal native-child model. Thus the optimal complex moment
exponent cannot increase in this class. A second unpaid direction is offset by
the forced growth of every geometric rank and of the ambient denominator.

## 6. Consequence for the selected kappa grid

The exact accounting check reconstructs the selected full histogram and
checks

    M(1-b_low) < 1 < M(1-b_high),
    b_low  = 0.001675462676808103522925,
    b_high = b_low + 10^-24.

It also checks the exact rational inequality

    b_high/(1+b_high) < 0.001672660197076919.

The retained balanced outer reduction requires `kappa < b/(1+b)`.
Equation (5) therefore excludes the next 10^-18 kappa grid point and every
larger one for this lift class, even before new scalar, chart, source-access,
movement, restoration, or finite-invoice costs are imposed. Those costs are
nonnegative. The original bit supplier is retained; its restriction can only
decrease the feasible outer saving. Its raw exponent is not substituted for
an outer kappa. This result neither changes nor reproves the selected supplier.

The all-size compiler, exact common-frame realization, whole-call hosting,
precision/tape, analytic transfer and bit H1--H5 conditions remain inherited.
Arbitrary dimension-18 plane assignments, other interaction graphs, new scalar
programs, and new outer reductions remain outside the no-improvement theorem.

## 7. Relation to general endpoint labels

The arbitrary-plane theorem in Section 2 is stronger than the linear-lift
hypothesis as a statement about dimension. It does not imply Section 5 for
all plane assignments. In dimension 18, a nonlinear assignment might have
other intersections at internal frames and might admit a new scalar word.
No classification or cost bound for those words is proved here.

PR791, at `f80382efd4cd3e37c67b2a966398b55bb56af53c`, proves a separate
rational-idempotent path formula. Its rank-two examples show that a generic
endpoint penalty need not double. This proof does not assume that rule.
Section 3 first forces a tensor pullback form in the linear class. The
actual preimage-frame distances then scale by r. Without that rigidity or
without the retained boundaries, this rank-scaling conclusion is not used.
