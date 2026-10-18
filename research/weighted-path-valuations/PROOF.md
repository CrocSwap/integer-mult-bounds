# A determinant obstruction from freely chosen path valuations

This is a written proof in a formal group algebra, with finite exact checks
of its hypotheses. It is not proof-assistant formalization or a new integer
multiplication bound. It extends the fixed-rank path argument in littleBro's
[PR705](https://github.com/CrocSwap/integer-mult-bounds/pull/705); see NOTICE.md.

## Statement

Let G be a group, K a field, and B_1,...,B_L arbitrary invertible scalar
W-by-W matrices over K. Fix boundary group elements u_j, v_i and interior
group elements g_{k,r}, for 1 <= k < L and 1 <= r <= W. Define

    S = diag([v_i]) B_L diag([g_{L-1,r}]) ...
                          B_2 diag([g_{1,r}]) B_1 diag([u_j])

as a matrix over K[G]. Specify an allowed subset A_ij of G for each entry.
The desired endpoint condition is that S_ij has zero coefficients outside
A_ij. Allowed elements may differ by entry; they need not form a subgroup.

An interior path p=(p_1,...,p_{L-1}) has group endpoint and scalar coefficient

    h_ij(p) = v_i g_{L-1,p_{L-1}} ... g_{1,p_1} u_j,
    c_ij(p) = (B_L)_{i,p_{L-1}} ... (B_2)_{p_2,p_1} (B_1)_{p_1,j}.

For L=1 the path is empty and these expressions have their usual empty-path
interpretation. Choose arbitrary integer weights w_{k,r} and integer row and
column potentials a_i, b_j. Write d(p)=sum_k w_{k,p_k}. Assume:

1. For each fixed i,j and each forbidden h outside A_ij, **all paths with
   h_ij(p)=h have the same d(p)**. No homogeneity is required for allowed h.
2. Every allowed path satisfies d(p) >= a_i+b_j.
3. sum_i a_i + sum_j b_j > sum_{k,r} w_{k,r}.

Then no invertible choices of B_1,...,B_L satisfy the endpoint condition.
Zero matrix entries and arbitrary scalar magnitudes are permitted. Rational
weights and potentials give the same criterion after clearing denominators.

## Proof

Replace each interior group diagonal by the scalar Laurent diagonal

    D_k(t) = diag(t^{w_{k,r}}),
    T(t) = B_L D_{L-1}(t) ... B_2 D_1(t) B_1.

Negative weights are allowed: entries lie in K[t,t^{-1}]. Direct determinant
multiplication gives

    det T(t) = (product_k det B_k) t^D,
    D = sum_{k,r} w_{k,r}.                                  (1)

The coefficient is nonzero. For fixed i,j, expand T_ij as the sum of
c_ij(p) t^{d(p)} over its paths. For a forbidden h, hypothesis 1 gives a
single exponent d_h for all paths contributing that group element. Their
combined Laurent term is

    t^{d_h} sum_{p : h_ij(p)=h} c_ij(p).

The endpoint condition says the sum is zero. Thus every forbidden group
class disappears from T_ij. Every remaining path has exponent at least
a_i+b_j by hypothesis 2. Further cancellation can only increase the least
exponent. The valuation of zero is understood as +infinity.

Every product in the Leibniz determinant expansion therefore has valuation
at least sum_i a_i+sum_j b_j. The nonzero determinant in (1) has valuation
D, contradicting hypothesis 3. This compares coefficients in a fixed path
expansion; it does not claim a homomorphism from K[G] to Laurent polynomials.

## Relationship to the predecessor

PR705 fixes w_{k,r}=rank(g_{k,r}) and assumes homogeneity for **every** middle
group class. With subadditive rank, boundary choices
a_i=m-rank(v_i), b_j=-rank(u_j) then supply its determinant obstruction.

Here the weights are variables and only forbidden classes need to be
homogeneous. This can separate words whose equal group products have
different accumulated Fourier ranks. The distinction is substantive:
`evolved-27` has three heterogeneous middle classes under the predecessor's
rank weights, but satisfies the present criterion with

    w_1 = ( 1,  0, 1)
    w_2 = (-1, -1, 0)
    w_3 = ( 0,  0, 0)
    a   = (-1,  0, 0)
    b   = ( 0,  1, 1).

Thus D=0 while sum a+sum b=1. Set A_ij to **all rank-three group elements**.
The scalar weighted matrix must have entry valuations bounded below by

    [ -1  0  0 ]
    [  0  1  1 ]
    [  0  1  1 ].

All six determinant products have valuation at least one, contradicting
its nonzero constant determinant. This excludes the whole literal word,
even without requiring a common final frame for each input column.

## Clifford specialization and completeness of the finite frame census

The supplied words use PR680's three-qubit projective Clifford group algebra
with W=3. Paid C_v=((1+i)/2)I+((1-i)/2)X_v has rank one; S, X, Z, CX and CZ
are free. The rank is rank_F2(B) of the symplectic B block. A usual endpoint
requires all nonzero group coefficients in an input column to have rank
three and one common left monomial frame. `model.py` retains Pauli signs;
it quotients only central scalar phase.

The supplied rational Gaussian generators have phases in {1,-1,i,-i}; the
intended tensor interpretation eliminates these for tensor multiplicities
divisible by four. As in the predecessor, the result is **in that formal
group algebra**. A concrete 8-by-8 realization is used to check group
equalities, ranks and frames independently, never to assert that its group
matrices are linearly independent. It is not a statement about every possible
complex circuit representation or about an abelian bit model such as PR720.

For a fixed literal word, enumerate every path before choosing scalar matrix
entries. The candidate frames for column j are precisely the rank-three
frames appearing on at least one such path. Any successful invertible word
has a nonzero entry in every input column, since S itself is invertible over
K[G]. Therefore its endpoint frame belongs to this finite set. It suffices
to enumerate their Cartesian product. A zero coefficient can remove a
candidate frame; it cannot create one absent from every path.

For a chosen frame triple f, take A_ij to be the elements of rank three with
frame f_j. The checker reconstructs this classification rather than trusting
a supplied list of allowed paths. It verifies all certificate equalities,
inequalities and strict gaps exactly. An absent certificate means only
unclassified; numerical LP infeasibility is not used as a proof.

## What the finite results establish

The original 73-word corpus is retained byte for byte after decompression.
PR705's rank-homogeneity test excludes 64; the present package examines all
nine remaining words. One global certificate and 918 frame-specific
certificates exclude 1,093 of 1,152 frame triples, leaving 59 unclassified.

Of the 1,152 choices, 865 already fail the elementary allowed-entry perfect
matching test. We do **not** claim these as new weighted exclusions. The
valuation criterion removes 228 additional choices that pass that baseline,
and closes `evolved-27` outright. Other predecessor support/polynomial methods
may already exclude additional choices; no exhaustive comparison with those
methods is claimed.

These are nine fixed words with four scalar blocks and eight paid calls.
They do not exhaust the four-block search space or the general register
model. Changing unary operations or mixing locations changes the hypotheses.
The eight remaining words are still unclassified as whole words here. The
59 surviving frame triples are not constructions or evidence of feasibility.
