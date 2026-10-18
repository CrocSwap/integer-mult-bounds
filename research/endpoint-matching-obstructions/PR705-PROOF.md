# A determinant obstruction for rank-homogeneous path collisions

This is a written proof in a formal group algebra, followed by finite exact
hypothesis checks. It is not a proof-assistant verification or a new integer
multiplication bound. No literature-priority claim is made.

## 1. General statement

Let G be a group and let r:G -> Z_{≥0} satisfy

    r(gh) <= r(g) + r(h),     r(1) = 0.

Fix W registers and L >= 1 arbitrary invertible scalar matrices
B_1,...,B_L over a field K. On the two boundaries put

    U = diag([u_1],...,[u_W]),   V = diag([v_1],...,[v_W]).

For each interior layer 1 <= k < L put

    D_k = diag([g_{k,1}],...,[g_{k,W}]).

All u,v,g are fixed group elements; the B matrices can have any coefficients
and zero pattern compatible with invertibility. Consider

    S = V B_L D_{L-1} B_{L-1} ... B_2 D_1 B_1 U

over K[G]. An interior path a=(a_1,...,a_{L-1}) has ordered product and degree

    h(a) = g_{L-1,a_{L-1}} ... g_{1,a_1},
    d(a) = sum_k r(g_{k,a_k}).

For L=1 the only interior path is empty, with product 1 and degree 0.

**Hypothesis (finite path homogeneity).** Whenever h(a)=h(b), d(a)=d(b).
This concerns this finite collection of paths. It does not assert that rank
is a grading or a homomorphism on G.

**Endpoint assumption.** In every entry of S, every group element with a
nonzero coefficient has rank at least m. Different entries may use different
group elements; no shared final frame is required by this assumption.

Then

    W*m <= sum_i r(u_i) + sum_i r(v_i) + sum_{k,i} r(g_{k,i}).       (1)

Thus any word whose right side is less than W*m and satisfies path
homogeneity is impossible for **all** invertible choices of the B matrices.
There is no restriction on L, on the scalar zero patterns, or on the size of
the scalar coefficients.

## 2. Proof

Replace each interior D_k by the commuting scalar diagonal matrix

    T_k(t) = diag(t^{r(g_{k,1})},...,t^{r(g_{k,W})}),

and form the ordinary polynomial matrix

    T(t) = B_L T_{L-1}(t) B_{L-1} ... B_2 T_1(t) B_1.

Its determinant is exactly

    det T(t) = c * t^D,
    c = product_k det B_k != 0,
    D = sum_{k,i} r(g_{k,i}).                                      (2)

For fixed output i and input j, group the paths in the entry T_ij(t) by
their ordered product h. Homogeneity assigns each such product a single
degree d_h, so

    T_ij(t) = sum_h c_{ij,h} * t^{d_h}.

The same coefficient c_{ij,h} is the coefficient of [v_i h u_j] in S_ij.
Left and right multiplication by fixed group elements are injective, so
distinct h cannot merge in this latter coefficient comparison.

If c_{ij,h} != 0, the endpoint assumption and subadditivity give

    m <= r(v_i h u_j)
      <= r(v_i) + r(h) + r(u_j)
      <= r(v_i) + d_h + r(u_j).

Consequently every nonzero term of T_ij(t) has degree at least
m-r(v_i)-r(u_j). Cancellation between different h at the same degree can
only increase that lower bound; an identically zero entry causes no problem.

Every term in the ordinary Leibniz determinant expansion therefore has
degree at least

    sum_i (m-r(v_i)-r(u_{sigma(i)}))
      = W*m - sum_i r(v_i) - sum_j r(u_j).

This remains valid if some entry bounds are negative. Since (2) is nonzero,
its degree D is at least this quantity. Rearranging proves (1).

The argument never maps the whole noncommutative group algebra into K[t].
Only the coefficients of this fixed path expansion are compared.

## 3. Why the collision hypothesis matters

Without homogeneity, a group coefficient can cancel between different
powers of t. The weighted scalar coefficient then need not vanish.

For example, take an element C of positive rank, and in two interior layers
use diag(1,C) and diag(1,C^{-1}), with identity mixing between them. The two
constant-role paths have product 1 but degrees 0 and 2 when both ranks are 1.
With A=[[1,1],[1,-1]] at entry and A^{-1} at exit, the unweighted group word
is the identity. The weighted matrix is

    A^{-1} diag(1,t) diag(1,t) A
      = (1/2) [[1+t^2, 1-t^2], [1-t^2, 1+t^2]].

The off-diagonal group coefficients vanish, but the displayed polynomials
do not. The verifier includes this control and rejects a forged homogeneous
classification of an exact Clifford inverse-pair word.

Failure of homogeneity is only a necessary escape from this obstruction.
It is not a construction or evidence that invertible coefficients exist.

## 4. Clifford specialization and scope

The finite checker uses the same three-qubit projective Clifford group
algebra as PR #680. For a Clifford symplectic matrix [[A,B],[C,D]], define
r(g)=rank_F2(B). Composition gives B_{gh}=A_g B_h+B_g D_h, hence the required
subadditivity. Every listed free monomial operation has rank zero; each
paid C_v=((1+i)/2)I+((1-i)/2)X_v has rank one. The rank of a complete unary
layer is therefore no larger than its literal paid-call count.

The usual endpoint condition, one full-rank left monomial coset for each
input stream, implies the weaker endpoint assumption above with m=3.
For W=3 and eight paid calls the right side of (1) is at most eight, which
contradicts nine whenever path homogeneity holds.

Projective equality here retains Pauli conjugation signs and quotients only
scalar phase. The supplied rational-Gaussian generators have central phases
in {1,-1,i,-i}; the intended tensor realization removes them when the tensor
multiplicity is divisible by four, as in the predecessor model. The result
is stated in that formal group algebra. It does not infer formal linear
independence from the concrete 8-by-8 representation. That representation
is used only to independently check group equalities and ranks.

## 5. What the supplied words establish

All 73 literal words have eight paid calls. The criterion excludes 64:

- Eight four-block descendants previously left unresolved by bounded
  support/polynomial searches.
- Twenty-three of 32 words from two generations of a collision generator.
- All 33 three-block words already excluded by PR #680, as regressions.

Nine evolved words fail the homogeneity hypothesis and remain unclassified
by this theorem. The cases are not an exhaustive enumeration of any
four-block family or of the full register model. The fixed unary words and
mixing locations matter. Inserting or changing unary operations can change
the hypothesis.

The proof supplies a search filter: a successful word with paid cost below
W*m must admit coincident interior products of different accumulated ranks.
Merely counting repeated products, including repetitions of the same unary
choice on different registers, is insufficient. The new criterion is
independent of the support, torus and polynomial solvers used in PR #680.
