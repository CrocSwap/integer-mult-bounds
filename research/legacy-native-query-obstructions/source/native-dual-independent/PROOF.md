# Independent audit of the monomial native-word lower bound

The proposed proof is valid in the stated native word model. A word
with p productive roles, m rational ADDRESS coordinates, and the
productive endpoint -I_m needs at least p m negative-determinant
rank-one monomial queries. Thus its total query count is at least p m.
The old four-role, three-coordinate target needs at least twelve calls.
Its ten-call and eleven-call cases are both excluded.

This is a query-count theorem. It gives no complete supplier or integer
multiplication exponent. It does not apply to genuine nonmonomial
ADDRESS shears or to free events that change ADDRESS indices.

## The precise model

Use the native query from PR 521 at
a190fdb39f31647fc6f651625353710624627348. Its query operator is

    H_N(g) = I + N tensor (g - I)

over the binary group algebra of the rational ADDRESS maps. The native
lift Phi is an injective group map, so one can use g before its doubled
ADDRESS lift. This keeps m, rather than 2m, as the representation size.
N is a binary rank-one role matrix. The source uses idempotent N; the
lower bound below does not need that condition.

Every counted g in this theorem is an invertible rational monomial
matrix with rational rank(g-I) = 1. It has one nonzero entry in each row
and each column. Arbitrary nonzero rational weights are allowed.

Free DATA events in the extended statement are binary linear maps on
the role file, applied at each unchanged ADDRESS index. They can be
noninvertible. This includes scalar copies, clears, and XOR operations.
Zero helper inputs are binary input embeddings. Productive output
selection is a binary output projection. None of these events can hide
an uncharged ADDRESS map or a nonlinear VALUE operation.

Require the productive endpoint on all productive input arrays at all
allowed ADDRESS precisions. If helpers are dirty, require the stated
DATA endpoint independently of their inputs. A proof for one finite
orbit or one residue modulus does not give this formal endpoint.

## 1. A valid representation of the monomial group

Let R = F2[epsilon]/(epsilon^2), and let t = 1+epsilon. Then t^2 = 1.
For a nonzero rational q, define s(q) = 1 if q is positive and t if q
is negative. This is a group homomorphism from Q* to the units of R.

For a monomial g, keep its permutation support and replace each weight
q by s(q). Call the result phi(g). A product of two monomial matrices
has one contributing term in each nonzero entry. Its weight is the
product of the two corresponding weights. Therefore

    phi(gh) = phi(g) phi(h).

The identity maps to the identity. Inverse monomials map to inverse
matrices. Extend phi linearly from the monomial group to its F2 group
algebra. This gives a ring homomorphism to Mat_m(R).

This is not an entrywise map on arbitrary rational matrix sums. That
distinction is required. For example, a positive shear I+E01 squares
to I+2E01 over Q. The entrywise sign images of both shears are I+E01
over R, but the square of that image is I. Thus this entrywise rule
does not extend to the full rational general linear group.

## 2. Every relevant query has one outer factor over R

Decompose the permutation of g into cycles. A cycle of length a has
rank a-1 in g-I if the product of its weights is one, and rank a if
that product differs from one. The equation g x = x gives this claim
directly: its nullspace on that cycle has dimension one or zero.

Since the total rational rank is one, the only nonidentity cases are:

1. One fixed coordinate has weight q different from one. Every other
   coordinate has weight one. A positive q maps to no change. A
   negative q gives phi(g)-I = epsilon e_i e_i^T.
2. One two-cycle has reciprocal weights. Every other coordinate is
   fixed with weight one. The two weights have the same sign. On its
   two coordinates, phi(g)-I is [[1,s],[s,1]], where s is 1 or t. It is
   the outer product (1,s)^T (1,s), since s^2 = 1.

The two-cycle has determinant -1. A coordinate scaling has negative
determinant precisely when q is negative. Thus every positive-
determinant rank-one monomial query maps to the identity. Every other
query difference has one outer factor over R.

Write N = a b^T over F2. If phi(g)-I = u v^T, then

    phi(H_N(g))-I = (a tensor u) (b tensor v)^T.

So each negative-determinant query adds at most one outer factor.

## 3. The product difference factors through the query count

First take a word with no free DATA events. Let P_i = A_i P_(i-1),
with P_0 = I and A_i-I = x_i y_i^T. Then

    P_i - P_(i-1) = x_i (y_i^T P_(i-1)).

Sum these k differences. The result P_k-I factors as B C, with k
columns in B and k rows in C. This is valid over R, which has zero
divisors. It does not use a field rank assertion over R.

The same form permits noninvertible free DATA events. Let S be the
ordinary binary scalar replay with every ADDRESS query replaced by
identity. Inductively maintain

    P = S tensor I_m + sum_i b_i c_i.

A free binary role map A left-multiplies S and every b_i by A, with the
identity on ADDRESS coordinates. A counted query adds x_i(y_i^T P),
one new outer factor; it leaves S unchanged. A positive-determinant
monomial query has no represented change, so it adds no outer factor.
Binary input embeddings and output projections preserve this form.
Neither invertibility of the free events nor a dirty-helper endpoint
is needed for this algebraic step.

## 4. The inner-rank argument

At the productive endpoint, phi(-I_m) = t I_m. Group-algebra
augmentation sends each ADDRESS group element to one. It therefore
gives S_prod = I_p. On the productive input and output blocks,

    epsilon I_d = B C,       d = p m.

Let B = B0 + epsilon B1 and C = C0 + epsilon C1, with binary matrices
B0, B1 of size d by k and C0, C1 of size k by d. Compare coefficients:

    B0 C0 = 0
    B0 C1 + B1 C0 = I_d.

The first equation puts the image of C0 inside the kernel of B0.
Hence rank B0 + rank C0 is at most k. The second equation gives

    d <= rank B0 + rank C0 <= k.

Thus at least p m negative-determinant queries are necessary. The same
argument proves that the inner rank of epsilon A over R equals the
binary rank of A: the lower bound follows as above, and a binary rank
factorization of A gives the matching upper bound.

For p=4 and m=3 the bound is twelve. Twelve coordinate flips attain
it. The checker verifies their full group-algebra endpoint as well as
their represented product and telescoping factorization.

## 5. Scope at helper boundaries

Count productive flipped roles, not every allocated role. For a target
diag(z,z,z,1) with z=-I_3, the epsilon target has rank nine. This proof
gives nine calls, not twelve. It does not exclude a ten-call or eleven-
call word for that different endpoint.

The old contract explicitly gives all four roles the z endpoint, so its
twelve-call conclusion is sound. Additional helper rows that return
identity do not weaken the bound for those same four flipped roles.
Clean-zero helper embeddings and discarded helper outputs also preserve
the bound for the productive block under the scalar-only free-event
model in section 3. Their physical costs remain separate obligations.

## 6. Why the all-size identity gives formal coefficients

A finite word has finite support in rational ADDRESS maps. The native
lift Phi is injective. Choose one ADDRESS vector outside the kernels of
every pairwise difference of the distinct lifted maps. Such an integer
vector exists because a finite union of proper rational linear
subspaces cannot contain all integer vectors.

Choose an allowed odd prime for which the word's rational maps and
inverses have unit denominators. Each pairwise image difference has a
nonzero coordinate with finite prime-adic valuation. At sufficiently
large precision, all images of the chosen vector are distinct modulo
the prime power. A DATA delta at that vector then separates every
coefficient in the finite group-algebra sum.

Thus a zero operator on all full DATA arrays at all allowed precisions
has every formal coefficient zero. This also applies to a productive
input block with zero helpers. It does not apply when inputs are
restricted to one special orbit or a smaller promised subspace.

## Checks and prior context

Run python3 -B check.py. The checker uses only the standard library.
It tests the ring laws, all signed three-coordinate products, all
two-coordinate weighted products in a six-weight pool, and all rank-
one monomials in that pool through dimension three. It checks all 225
binary rank-one role matrices, including the 120 idempotents. It also
checks small inner-factor obstructions and a noninvertible copy/clear
control with a zero helper. The written proof, not finite enumeration,
establishes the result for arbitrary dimensions and rational weights.

The pinned PR 521 proof supplies the native operator, not this lower
bound. The older B3 contract proves an eleven-call determinant-parity
obstruction and leaves ten calls unresolved by its solver. The pinned
algebraic section of the cited Swapnil Jain source uses the determinant
character into dual numbers and discusses broader rank-one relation
bounds. The targeted passages checked here do not contain this matrix
sign representation and inner-rank proof. This is not a global novelty
claim or a complete literature search.
