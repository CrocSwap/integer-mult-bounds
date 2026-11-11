# A sharp balanced rank-one cycle for refined recovery

This scoped proof and construction were produced by Nick Petalas. Apache-2.0.

## Premises and exact scope

Armin Pourshafeie / apoursh's #6853 asks for a structured frame construction
matching #6852's existential asymptotic rate. We use the affine family in
#6851, derived from Nick Petalas's #6660 integer frames. CubeJerry's #6327
and zxv's #5444 supply the retained rounded-native interface and matrix.
These predecessor theorems are premises, not results proved again here.

Let C be the binary self-dual [8,4,4] code. Its unique weight-eight word is
omega = (1,...,1); its other fourteen nonzero words have weight four. Put
Q = F2^8/C, so C = Q*. The predecessor's binary space decomposes as

    V = im(mu) direct-sum R,    dim Q = 4,    dim R = d = 100.

In the affine family, every stage has phi_j(q) = mu(q) + psi_j(q), with
arbitrary binary linear psi_j: Q -> R and psi_1 = 0. Characters are pairs
(c,b) in C x R*. Their codewords and total weights are

    h_j(c,b) = c + psi_j* b,
    W(c,b) = sum_j wt(h_j(c,b)).

The Fourier error term from #6851 is

    S = sum_{(c,b) != (0,0)} 13^(-W(c,b)).

We prove a new sharp lower bound and an explicit equality construction
within this family. All claims about arbitrary other mode-preserving frames
are excluded. The combinatorial proof below works for every d >= 1; the
integer construction specializes it to the actual d = 100.

## Theorem

Write L = 2^d and N = 16L. At every positive depth t,

    S >= B_d(t) := (N-2) 13^(-4t) + 13^(-8t).

Equality is attainable if and only if L divides t. At every positive
multiple of L, the rank-one maps

    psi_v(q) = omega(q) v,    v ranging once over R per cycle,

attain equality. One can start with v = 0, so psi_1 = 0.

For the actual d = 100, this gives the exact minimum of S at every positive
multiple of 2^100. Using the predecessor's zero-fiber formula and small-error
max-fiber theorem, the exact minimum maximum fiber in this affine family is

    [13^(8t) + (2^104-2) 13^(4t) + 1] / 2^104,
    t a positive multiple of 2^100.

This is an exact symbolic formula, not an enumeration of that depth.
The same explicit infinite periodic sequence has error exponent

    lim_{t -> infinity} -log2(S(t))/t = 4 log2(13).

Thus it answers #6853's structured-construction question, with an enormous
period. It does not improve the practical depth-28 to depth-30 certificates.

## Lower bound

For b = 0 the contribution is exactly 14*13^(-4t) + 13^(-8t).
Fix b != 0. At every stage, c -> c + psi_j* b permutes C. Consequently

    sum_{c in C} W(c,b) = t sum_{c in C} wt(c) = 64t.

Strict convexity of x -> 13^(-x) gives

    sum_{c in C} 13^(-W(c,b)) >= 16*13^(-4t),

with equality exactly when W(c,b) = 4t for every c. Sum over the L-1 nonzero
b and add the fixed b = 0 contribution. This gives B_d(t), with equality
exactly when all W(c,b) equal 4t for b != 0.

## Rank-one equality construction

For psi_v(q) = omega(q) v, its adjoint sends b to b(v) omega.
For each b != 0, exactly half of R has b(v) = 0 and half has b(v) = 1.
Complementary codewords obey

    wt(c) + wt(c + omega) = 8.

One cycle therefore gives W(c,b) = (L/2)*8 = 4L for every c and b != 0.
Repeat the cycle to attain the bound at t = mL. The sole b = 0 character
of weight eight has total weight 8t. Every other nonzero character has
weight 4t. There are N-2 of the latter, proving the asserted spectrum.

## No shorter equality length

This argument permits arbitrary maps psi_j, not merely rank-one maps.
For fixed b != 0 let n_b(a) count the j for which psi_j* b = a in C.
Since wt(a) = 4 - 4*1[a=0] + 4*1[a=omega],

    W(c,b) = 4t - 4 n_b(c) + 4 n_b(c+omega).

Equality in the lower bound forces n_b(c) = n_b(c+omega) for every c.
Choose any q in Q with omega(q) = 1. Pairing c with c+omega then gives

    0 = sum_c n_b(c) (-1)^(c(q))
      = sum_j (-1)^(b(psi_j(q)))        for every b != 0.

Let m(v) count the occurrences of v in the multiset {psi_j(q)} in R.
Every nontrivial Fourier coefficient of m vanishes, while its trivial
coefficient is t. Fourier inversion on R gives m(v) = t/L for every v.
These are integer multiplicities, so L divides t. In particular 2^100
is the least positive equality depth for the actual affine family.

## Integer realization and random access

Use E selecting owners 0,1,2,4 and the 100 integer lifts k_i retained in
#6660's FRAMES.json. They satisfy M^T k_i = 0 and E k_i = 0; their binary
reductions form a basis of R. Define the integer row

    lambda = e_1^T + e_2^T + e_4^T.

For the literal source M, lambda M mod 2 = omega. For 0 <= a < 2^100,
let g(a) = a XOR (a >> 1), the reflected Gray index, and put

    v_a = sum_i bit_i(g(a)) k_i,
    W_a = I + v_a lambda.

Then lambda v_a = 0, so W_a^(-1) = I - v_a lambda over the integers.
Also M^T W_a = M^T. Its binary action on M is exactly
mu(q) + omega(q) red2(v_a), as required. In particular W_0 = I.
The Gray map permutes all d-bit indices. Adjacent cyclic indices differ
in one Gray bit, including the last-to-first transition. Thus

    U_a = W_(a+1)^(-1) W_a = I + (v_a-v_(a+1)) lambda

uses a signed single lift k_i. Both each frame change and every transition
have rank at most one relative to I. The constructor computes any frame
using at most 100 retained lifts; it never materializes the whole period.
No physical instruction price for these integer maps is asserted.

## Maximum fibers and the infinite sequence

At t = m*2^100, B_100(t) < 2^104*2^(-4t) < 2^(-296), since t >= 100
and 13 > 2. The inherited threshold epsilon* from #6848 is larger than
2^(-296). For example (23/12)^8 < 256 gives
epsilon* = 1/[13*((23/12)^8-1)] > 1/3315 > 2^(-12).
Thus the predecessor's theorem makes the maximum fiber the zero fiber
for this construction. Every competing affine sequence has maximum fiber
at least its zero fiber. The Poisson formula and the sharp S bound prove
the claimed exact optimum. The formula is integral: writing A=13^(4t),
its value is A+(A-1)^2/2^104; 2^104 divides A-1 because
v2(13^(4t)-1) = 4+v2(t) >= 104.

For arbitrary t, a partial cycle adds only nonnegative weights, so

    B_100(t) <= S(t) <= (2^104-1) 13^(-4L floor(t/L)).

With the fixed constant L = 2^100, taking logarithms and dividing by t
proves the explicit sequence's exponent. This limit does not promise useful
convergence before a complete period.

## Evidence and remaining obligations

The universal statements rest on this written proof and the cited premises.
The verifier exhausts reduced dimensions, arbitrary-map small cases and small
Fourier occupancy multisets, and checks random-access frames against the
actual integer matrix. Its generated hash-bound receipt states exact coverage.
It neither enumerates the 2^100-stage period nor replays a predecessor's
scientific verifier. No codec, physical tag acquisition, caller acceptance,
restoration price, supplier invoice, new kappa, selected-frontier change or
complete multiplication theorem is supplied. Independent human and formal
proof-kernel review are unclaimed.
