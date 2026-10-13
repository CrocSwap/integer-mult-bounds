# Varying unit phases need no cycle-length precision guard

This extends the neighboring clean-array inverse in PR628 to a different
unit phase at every position. It does not complete the multiplication
algorithm, its recursive composition, or dirty-scratch restoration.

Let `(Wx)_i = tau_i x_(i-d)` on a cycle of length L, where d is 1 or -1
and every |tau_i|=1. W and W^-1 have infinity operator norm 1. Let P be
the prime-power kernel and Q its certified approximate factorization from
PR628. All its coefficient preparation, factor margin beta, prefix bounds,
and rounding budgets remain applicable to P(W).

## A first-order scan with varying coefficients

For arbitrary exact rational complex b_i with |b_i|<=1-beta, solve

    y_i - b_i y_(i-d) = x_i.

Traverse the cycle in direction d, first with zero seed. Maintain z by
z <- x_i+b_i*z and c by c <- b_i*c, starting c=1. At the end, the exact
periodic seed is z/(1-c). Repeat the traversal with that seed. The affine
return map is s -> z+c*s, which proves periodicity, including L=1.

Round each complex multiply-add, running product, and closure division on
the u=2^-w grid. Each error has modulus at most u. All recurrence error
multipliers are bounded by 1-beta, so both first-pass errors are <=u/beta.
The exact product has modulus <=(1-beta)^L, hence |1-c|>=beta. If
u<=beta^2/2, the rounded denominator has modulus >=beta/2.

The periodic solution is bounded by B/beta for ||x||<=B, using the Neumann
series of the weighted contraction. Thus, exactly as in PR628, division
perturbs the seed by at most

    2u/beta^2 + 2B*u/beta^3 + u.

The second scan attenuates that seed error and adds at most u/beta. Its
total error is <=6(B+1)u/beta^3, independent of L and of the pattern of b_i.
The running product remains rounded throughout: its representation length
does not grow with the number of phases.

## Factor execution and the inverse-phase index

For an outer approximate root rho, apply the varying scan with
b_i=tau_i/rho, then round multiplication by -1/rho.

For an inner root, W^-1 acts as

    (W^-1 x)_i = tau_(i+d)^-1 x_(i+d).

Apply the reverse scan with b_i=rho/tau_(i+d), then apply W^-1 to its
output. The phase index is i+d, not i. This implements

    (W-rho I)^-1 = W^-1 (I-rho W^-1)^-1.

The final unit multiplication contributes at most u per coordinate. Both
factor types therefore obey PR628's 7(B+1)u/beta^3 bound. Their norms are
at most beta^-1, and scalar r is applied initially. The identical cascade
recurrence and explicit budgets yield error <=2^-p for every L. Neither
Fourier diagonalization nor a computed L-th root of the total phase is
needed for this argument.

## Approximate phase oracles

Suppose sigma_i are exact rational units and max_i|tau_i-sigma_i|<=nu.
Let V be the corresponding weighted shift. Then ||W-V||<=nu and
||W||=||V||=1. The noncommutative telescoping identity gives

    ||W^j-V^j|| <= j*nu,
    ||P(W)-Q(V)|| <= epsilon + nu*sum_j j*|Q_j|.

There is no factor L. Choosing nu<=epsilon/(n*2^r), as in PR628, gives
perturbation at most 2*epsilon and the same inverse perturbation bound.
The stereographic projection described there produces each sigma_i with
exact unit modulus using O(p+r^4) approximation bits. Phase-oracle calls
and reading the phase descriptions must be charged for every supplied
phase; only the kernel factor preparation is independent of L.

## Layout, cost and scope

Store phases in a sequential array aligned with the numerical array.
Reverse passes reverse both streams; the inner phase stream uses one
cyclic rotation. A bounded number of sequential passes implements each
factor. Coefficients can be formed on demand during each pass. If rational
phase representations have at most T bits, scalar operands have
O(p+r^4+T) bits, and the clean-array execution costs

    soft-O(L*r*(p+r^4+T)).

Add PR628's kernel preparation and all phase-oracle/input costs. O(LB)
storage suffices for aligned phase and alternating value arrays, with
B=O(p+r^4+T), plus setup and scalar arithmetic scratch. This remains a
neighboring-cycle claim. Other strides need their charged routing; full
transform composition and reversible restoration are separate obligations.

## Evidence and attribution

`weighted.py` uses PR628's exact complex arithmetic, kernel enclosures and
factor certificates, copied unchanged beside it. It checks varying
contraction magnitudes and phases, both directions and short cycles,
including L=1. It also compares radix 4, 9 and 16 cascades with independently
expanded weighted polynomial matrices and exact Gaussian solves. Tests
include a certified rational-unit approximation to exp(2*pi*i/7), with the
phase perturbation charged. Wrong inverse-phase indexing, constant-phase
substitution and malformed inputs are rejected. The JSON output records
the actual coverage; finite tests support the implementation, while the
inequalities above prove the all-length claim.

The periodic affine closure and weighted-shift identities are standard
algebra. No literature-priority claim is made. This extension was prepared
with OpenAI Codex for chafreaky. PR628 supplies the uniform factorization
and rounding budgets and preserves the underlying PR621, Pan and Brent
attributions and theorem dependencies.
