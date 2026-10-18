# Cycle-local resolvents and the bilinear dual

## Exact obligation

Let L >= 1, s be any integer, and tau_i be complex scalars of modulus one.
Indices are modulo L. Define (W x)_i = tau_i x_(i-s). The permutation splits
into g = gcd(L,s) cycles of length m = L/g; gcd(L,0)=L. For a cycle C put
h_C = product_(i in C) tau_i. On that cycle W^m = h_C I.

For any scalar rho such that h_C != rho^m on every cycle, define

    R_C = [sum_(j=0)^(m-1) rho^(m-1-j) W_C^j] / (h_C-rho^m).

Multiplying the numerator by W_C-rho I on either side telescopes to
W_C^m-rho^m I. Consequently R_C is a two-sided inverse of W_C-rho I.
The direct sum of these inverses, scattered back to the original indices,
is (W-rho I)^(-1). This is a written elementary proof for all L and s,
not an inference from the finite receipt and not a proof-assistant result.

If |rho| != 1, all denominators are nonzero because |h_C|=1. In particular,
this applies to the tested inner and outer roots. It also handles rho=0,
L=1 and s=0. At rho=0, rho^0 in the final summand means 1.
No prime-power or polynomial-kernel nonvanishing theorem is needed here.
The oracle constructs these finite sums without a Gaussian solver or the
predecessor's affine two-pass recurrence.

## The inverse transpose is not the inverse adjoint

For the complex bilinear pairing x^T y, direct expansion gives

    (W^T x)_i = tau_(i+s) x_(i+s).

Thus W^T is a weighted shift of stride -s and phases
sigma_i = tau_(i+s), without complex conjugation. Substituting sigma,-s
in the preceding formula gives (W-rho I)^(-T). The checker compares this
matrix with the transpose of the independently constructed forward inverse,
then checks both matrix products against the identity. For the Hermitian
adjoint the phases AND rho would instead be conjugated. Confusing those
two interfaces is explicitly rejected, but this is not a claim that PR628
uses the wrong pairing: its submitted neighboring forward factor is valid
on the checked inputs.

## Reduction to the pinned rounded neighboring factor

Enumerate each cycle as a,a+s,...,a+(m-1)s. In these coordinates its shift
is PR628's direction +1. Reversing that cycle order, while keeping its first
entry fixed, gives direction -1. Gather values and phases with the same
permutation, call the pinned factor, then scatter using the inverse map.
The execution is a direct sum, not a product, of the cycle calls.
PR628's LAYOUT.md already uses cycle decomposition and this direct-sum norm
argument for a constant scalar gauge, with two explicitly charged sorts.
They are not new claims here; the present obligations concern varying
phases, the bilinear dual and an independent exact implementation.

Both gather and scatter preserve the infinity norm. Suppose either
|rho| <= 1-beta or |1/rho| <= 1-beta, 0 < beta <= 1, and u=2^(-w) <= beta^2/2.
The neighboring single-factor bound from PR628 WEIGHTED-PROOF.md is

    error <= 7 (B+1) u / beta^3,    ||x||_infinity <= B.

Every cycle input has norm at most B. Taking the maximum of the cycle
errors gives the SAME bound, without a factor g or L. The transpose phase
shift also preserves unit modulus, so the same argument applies to it.
This implication inherits the neighboring rounding estimate; the finite
checks corroborate that estimate but do not prove it for arbitrary inputs.
The two selected roots have beta=1/2: their stable coefficients have squared
moduli 5/64 and 16/65, both at most 1/4.

The reference adapter invokes unchanged scan/apply definitions from the
pinned weighted.py and unchanged arithmetic from scan.py. It sets radix=1
only to omit an initial scalar and isolate ONE factor. This is not a
radix-1 kernel certificate, a full factor cascade, or a new prime-power
construction. The parser selects complete function ASTs without rewriting
them and binds c to the same pinned scan module; unrelated kernel setup
and the predecessor's main test harness are not executed.

## An exact counterexample to a tempting extension

Take L=6, s=2 and phases

    [1, i, (3+4i)/5, (-5+12i)/13, -1, -i].

The even and odd cycles have holonomies

    h_even = (-3-4i)/5,    h_odd = (-5+12i)/13.

The global product is (63-16i)/65, which is neither local holonomy.
Replacing each cycle denominator by this global product minus rho^3,
with rho=1/4+i/8, produces a matrix that fails the exact inverse identity.
Using L instead of m in the denominator also fails. These are concrete
counterexamples to those ADAPTER MUTANTS, not counterexamples to PR628,
which explicitly restricts its submitted weighted layout to neighbors.

## Cost and unresolved obligations

Only algebra and numerical error transport are settled here. A complete
implementation would have cost

    C_gather(L,s) + sum_C C_neighbor(|C|) + C_scatter(L,s),

plus every phase read/preparation, allocation and restoration required by
the target model. The Python adapter uses random indexing and clean arrays;
it does not implement or price a fixed-tape permutation, dirty reversible
storage, native-frame changes, recursive hosting or common-label access.
No routing term is assumed free. The inherited direct-sum argument prevents
a spurious cycle-count precision multiplier; no established paid expense
is reduced. The existing LAYOUT.md charge is not replaced by a free RAM
permutation.

Kernel preparation, arbitrary growing radices, full-transform composition,
H1-H5, compiler/tape/precision/exact recovery and analytic transfer are not
verified or discharged. There is no new kappa or integer multiplication
bound. This is a scoped independent implementation and written identity
proof, not independent human review or a formal full-theorem verification.
