# Weighted clique certificate for scalar Gaussian decoders

The exact certificate gives a copy-charge lower bound of **40 Gaussian rank
units**, or **80 rational rank units**, for every decoder in the class below.
It does not assert a new multiplication bound.

Let V index the 60 Gaussian lines obtained from the E8 roots in Q^8 by the
complex structure J with J e_(2a) = e_(2a+1) and
J e_(2a+1) = -e_(2a), for a=0,...,3. For a line set S, let X_S be the
rational span of its representatives and their J-images. Write

    c(R,A) = rank_Q(V_R V_A^T) / 2,

where V_S has rows spanning X_S. This is the Gaussian pairing rank, in
Gaussian rather than rational rank units. It is not the dimension of the
source span, and it is not the binary rank of a decoder submatrix.

Consider any finite scalar-total binary factorization

    B = sum_j 1_(R_j) 1_(A_j)^T  over F2,

with B_tt=1 and B_ts=0 when distinct Gaussian lines t,s are nonorthogonal.
Reader/source supports may differ; orthogonal off-diagonal entries are free.
The abstract copy charge is C=sum_j c(R_j,A_j).

## Certificate theorem

Let K be any finite collection of pairwise nonorthogonal cliques. Assign
nonnegative rational weights lambda_Q to its cliques. Suppose that, for
every ordered pair of flats F,G of the Gaussian line matroid,

    sum_(Q in K) lambda_Q [Q meets F and Q meets G] <= c(F,G).    (1)

Then every fitting scalar-total factorization satisfies

    C >= sum_(Q in K) lambda_Q |Q|.                             (2)

Proof: the fitting constraints force B[Q,Q]=I_|Q|. A rectangle restricted
to Q has binary rank one exactly when both supports meet Q, and has rank
zero otherwise. Binary rank subadditivity therefore gives

    |Q| <= sum_j [Q meets R_j and Q meets A_j].

Multiply by lambda_Q, sum over Q, and apply (1) to each term. The reduction
from arbitrary supports to flats in that last step is justified below.
There is no assumption on the binary rank of B, the number of totals, or
symmetry of the factorization. Zero-charge terms are allowed.

## Why all flat pairs suffice

Define cl(S)={t in V: X_{t} is contained in X_S}. This closure contains S
and spans exactly X_S. Consequently

    c(cl(R),cl(A)) = c(R,A).

Each clique-hit indicator is nondecreasing when either support grows, so
its value on (R,A) is at most its value on (cl(R),cl(A)). Thus (1), checked
on all flat pairs, covers every one of the 2^60 by 2^60 support pairs.
This is a completeness argument, not an inference from sampled supports.

All flats can be generated starting with the empty flat and adjoining one
line outside a previously generated flat, followed by exact closure.
Completeness follows by induction on rank: choose a line basis of any
nonempty flat, remove its last line, and use the lower-rank closure as its
parent. The rank is at most four, so this process terminates after rank
four. The verifier checks exact closure, Gaussian invariance, and that the
basis equals the canonical span of the stated lines. An independent Fraction
elimination checks fixed rank cases and the sharp witness's Gram matrix.

For zero pairing rank the left side of (1) is automatically zero. If a
clique met both supports, a chosen reader/source pair would either be the
same nonzero line or two distinct nonorthogonal lines. Either choice has a
nonzero Gram block, contradicting zero pairing rank.

## Uniform weights and their exact limitation

For equal-size cliques of size q, let n=|K| and

    h(F,G) = number of cliques meeting both F and G;
    rho = max_(c(F,G)>0) h(F,G)/c(F,G).

The largest valid uniform weight is exactly 1/rho, and the resulting floor
is n*q/rho. An exhaustive exact maximum over flat pairs therefore certifies
both the bound and optimality within this uniform-weight method. A pair
attaining rho is a useful witness against every larger uniform weight.

Here n=640, q=12, and rho=192. The committed certificate records all 2,272
flats, including the empty flat, and all 2,579,856 unordered pairs of nonempty
flats. Symmetry of both the Gram rank and joint-hit count covers both orders.
Empty supports have zero charge and zero hits.

For a pair with h>0 and flat ranks r,s, the proof above gives c>=1.
Sylvester's rank inequality on the real Gram product gives c>=r+s-4.
The verifier therefore accepts h<=192 max(1,r+s-4) directly. It computes
the exact rational Gram rank for every remaining pair. This partitions the
entire domain into 2,725 zero-hit pairs, 1,827,741 rank-bound pairs and
749,390 exact-rank pairs. No candidate is skipped on a numerical tolerance.

With the lexicographic line numbering in `geometry.py`, the pair

    F = {0,1,2,11,12,45}
    G = {0,3,4,5,6,7,8,9,10,54,55,56,57,58,59}

has ranks 2 and 3, pairing rank 1, and joint-hit count 192. Thus 1/192 is
valid and is the largest uniform weight on these 640 cliques. Applying the
certificate theorem gives C>=640*12/192=40. The witness is also a concrete
reason that replacing pairing rank by a support's dimension would be invalid.
This sharpness concerns the certificate method; it does not exhibit a
cost-40 decoder.

There is also a limitation independent of the computed maximum. Take both
supports to be the full ground set. Its cost is four and it meets every
nonempty clique, so every feasible system of nonnegative clique weights
must satisfy sum_Q lambda_Q <= 4. If the maximum nonorthogonal clique size
is 12, no such weighted-clique certificate can prove a floor larger than
48, even with nonuniform weights or with smaller cliques included. This is
a limitation of this certificate method, not an upper bound on the true
minimum copy charge.

For comparison, every fitting B has an abstract decomposition of cost 60:
take one rectangle per row, with R={t} and A equal to that row's nonzero
support. Its Gram pairing has rank one because B_tt=1, while every other
possible nonzero entry in that row lies on a line orthogonal to t. This
upper bound does not establish a physical supplier or attainability without
additional expenses.

## Conditional three-stage consequence

Under the separate Dfc accounting of #595 and the Gaussian scaling argued
in #620, v=60 and each line has rational rank k=2. For T replicas and s
stages, the optimistic deficit therefore satisfies

    D/T = (s-1) v k - s cst <= 120(s-1) - 80s = 40s-120.

At s=3 this is nonpositive. Under the same pressure identity with
nonnegative paid children and fallback cost, a positive supplier saving
requires positive deficit. Thus this three-stage Gaussian format cannot
give a positive saving, even before charging helper preparation, source
access, frame changes, restoration, or recursive children. Those required
costs cannot repair a nonpositive optimistic deficit.

The bound allows positive deficit at s>=5. It does not decide the best
decoder cost, construct a complete supplier, or price the other supplier
and outer assembly. No kappa improvement follows. Changing stage accounting
or allowing sub-line/vector-valued operations is outside this consequence.

## Provenance and scope

The Gaussian object above is exactly the object in Joel Pulikkan /
GamingPuzzled's #620 `gauss_geom.py`: its J is also exactly the block-diagonal
`Li` in `algebra_lines.py: left_quat()`. Each rational Gaussian root line
contains its four roots r,Jr,-r,-Jr; changing representatives only permutes
the line indices and multiplies rows by invertible Gaussian scalars.

The weighted-clique argument extends the method of Douglas R. Colkitt /
Mister-Meeseeks' concurrent PR #703, at commit
358383e2f1b0f292d4d6eb897c06fd8558a4f5e6. That work proves a sharp bound for
the ten Hurwitz lines using 32 orthogonal-pair transversals. Its numerical
Hurwitz bound is not imported here.

The result concerns whole Gaussian-line supports, scalar binary totals and
the declared pairing-rank charge. It does not cover arbitrary rational
sub-line supports, vector-linear totals, modified fitting patterns, or
other geometries. Translating it into a supplier obstruction requires the
repository's separate frame and accounting assumptions. Finite exact replay
is not a proof-assistant formalization of the multiplication theorem.

Prepared by Sagar Thakrar (@thakrarsagar) with substantial OpenAI Codex
assistance in the proof, implementation, review and documentation.
Apache-2.0, as specified by the repository license.
