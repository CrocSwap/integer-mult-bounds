# Integrated phase-retaining cascade consumer on restricted Word RAM

## Sufficient runtime theorem

Fix W >= 1, choose q = 2 for pure XOR Pauli couplers or q = 4 for arbitrary
quarter-phase Pauli couplers, and let n be the number of complex entries PER
role. In this note N = W n is the TOTAL number of complex observation entries.
Assume the caller actually supplies

    v = (I + U/2) y,
    (U y)_k = H_k y_((k+1) mod W),

with the phase-retaining unit Pauli monomials H_k and all scalar coefficients
in the stated representation. No observation producer is supplied by this
theorem. If the caller wants y_k = K x_k, those actual independent target
observations, not a matrix merely containing K, are its prerequisite.

The factored decoder of cascade_free.py and the fixed_divisor.py arithmetic
supply y to prescribed accuracy using no further recursive Gaussian child,
no word multiplication and no word division. With both logical shifts as
primitives, its work is

    O((W + q) N D_W(h) + W N),
    D_W(h) = O_W(log(2 + h)),

including literal return-map compilation, all scalar rounding, routing,
initialization and cleanup. Thus for FIXED W it is O(W N log(2 + h)), with
constants depending on the fixed rational coefficients. If one instead uses
n per role, the same bound is O(W^2 n log(2 + h)). No factor W disappears.
If W varies, keep the coefficient-dependent bound below rather than claiming
a uniform W-linear tariff. No new kappa follows without a favorable paid
producer and the remaining complete caller and transfer contracts.

## Exact denominator and pass counts

Put beta = (-1/2)^W and V = U^W. The exact decoder is

    S_W(U) [sum_(j=0)^(q-1) beta^j V^j] / (1 - beta^q),
    S_W(U) = sum_(j=0)^(W-1) (-U/2)^j.

It needs W + q - 2 full monomial passes and as many complex ADD passes,
followed by one real fixed-rational scale on each real and imaginary part.
A full pass visits all N entries. The normalization is

    gamma = 2^(q W) / (2^(q W) - 1).

The source examples give:

| Roles and phase contract | Monomial passes | ADD passes | Final gamma |
|---|---:|---:|---|
| W = 3, pure XOR, q = 2 | 3 | 3 | 64/63 |
| W = 13, pure XOR, q = 2 | 13 | 13 | 67108864/67108863 |
| W = 3, quarter phase, q = 4 | 5 | 5 | 4096/4095 |

The original h-bit value is not multiplied by the large gamma numerator in
an unbounded register: its fixed binary expansion is applied with the constant
q W + 1 guard bits already reserved. Dyadic Horner multipliers are likewise
prescribed fixed-rational operations, with exact remainder-based rounding.

A deliberately conservative supplied-emulator data-operation bound for one
fixed-rational real scale at working width h is

    D_W(h) <= 100 (q W + 1)^2 (ceil(log2 h) + 1) + 12.

Here the largest divisor bit length is q W, and the gamma numerator has only
one nonzero binary digit. The first and second Horner coefficients have no
larger divisor. This bound counts emulated Boolean, shift, scalar modular
weight and sign/rounding data operations; loop/control, memory access and
signed ADD instructions have additional constant tariffs. It is not a
cycle-accurate processor count. The fixed program performs at most
2 N (W + q - 1) such real scales, including the final normalization, plus
2 N (W + q - 2) real ADDs and the stated routing passes. Multiplication by
powers of two may be implemented more cheaply, but this bound grants no
unstated fast primitive.

## Precision and explicit error propagation

Use the maximum absolute REAL COMPONENT norm on complex vectors. Let the
exact observations have each component at most B, and suppose stored input
components have error at most epsilon_in. Let every Horner scalar update
and final scale introduce at most epsilon additional component error after
its prescribed rounding; signs, quarter phases and permutations are exact.
ADD can be exact on the common grid with the guarded signed-magnitude format.

The first Horner recurrence has contraction 1/2. Its accumulated arithmetic
error is at most 2 epsilon, independently of W. Let a = |beta| <= 1/2.
The second Horner recurrence retains the first output as its source. Its
error is at most (2 epsilon + epsilon)/(1-a) <= 6 epsilon. The last scale
has gamma <= 4/3 because q is even and at least two; rounding adds epsilon.
Hence internal arithmetic contributes at most

    (4/3) 6 epsilon + epsilon = 9 epsilon.

The exact complete inverse has coefficient absolute sum exactly 2, so input
perturbation contributes at most 2 epsilon_in. Therefore the component error
of the final answer is at most

    2 epsilon_in + 9 epsilon,

and its ordinary complex Euclidean error is at most

    sqrt(2 N) (2 epsilon_in + 9 epsilon).

These estimates are independent of tensor width and do not substitute the
small return-block condition number for the complete observation operator.
For example, rounding on a grid of step 2^-p with epsilon_in <= 2^-p and
all local errors <= 2^-p gives error <= 11 sqrt(2 N) 2^-p. The conservative
choice

    p >= max(0, ceil(log2(22 N / eta)))

therefore suffices for a requested Euclidean error eta > 0. Input scale and
magnitude still need to be represented; this is not a precision oracle.
Exact observations on the grid have epsilon_in = 0 and permit the sharper
9 epsilon version.

For the actual nearest-ties-even implementation one can do better. Let u be
the grid unit, so every individual real scale rounds with error at most u/2.
The first Horner error is at most u. The second Horner error is at most
(u + u/2)/(1-a) <= 3u. The normalization error is at most
(4/3)3u + u/2 = 4.5u. Therefore 5u safely bounds the component error versus
the exact inverse of the SAME stored grid observations. If the original
observations were first rounded to that grid, their component perturbation
is at most u/2, which contributes at most u through the inverse. The total
is at most 5.5u, so 6u is a safe advertised bound. The global Euclidean bound
is 6 sqrt(2N) u. One sufficient choice is

    p >= max(0, ceil(log2(12 N / eta))).

The constants 5 and 6 are safe upper bounds, not claimed optimal constants.
Exact signed ADDs and phase operations must preserve the common grid; a
separately rounded ADD would require its own error term.

Exact first-stage intermediates have components at most 2 B and exact
second-stage intermediates at most 4 B. For epsilon <= 1 and epsilon_in <= 1, a safe stored
component majorant throughout is 6 B + 16, including the final output.
Consequently it suffices to reserve p fractional bits, an integer magnitude
field for 8(B+2), and q W + 4 fixed guard bits for numerator products and
sign/rounding temporaries. W is fixed, so these add only a constant to the
payload bit precision. A constant-limb version is possible with its explicit
cross-limb shift tariff; no h-bit word silently holds a larger integer.

## Ownership and address space

The observations stay unchanged. For q = 2, two owned full-size work buffers
suffice: alternate them in the first Horner stage, then use its final buffer
as the retained source of the single V stage and the other as destination.
For q = 4, use three owned full-size buffers: retain S_W(U)v in one and
alternate the other two through the V Horner stage. All buffers are newly
owned or supplied zero scratch. The final answer occupies one work buffer;
other dependent buffers can be explicitly cleared in charged linear passes.
Arbitrary dirty caller banks are never overwritten or assumed zero.

One conservative signed-magnitude layout uses four h-bit words per complex
entry, including separate sign fields. A literal U map and compiled V map
each use one index and one phase word per entry; allowing both costs 4 N
additional words. The fixed-denominator scalar procedure uses at most a fixed
multiple of q W + 1 plane words; reserve 12(q W + 1) + 64 scalar/control words.
Thus, if S other caller words must remain retained, a sufficient uniform
address-headroom condition for either q case is

    2^h >= S + 20 N + 12(q W + 1) + 64.

This is a sufficient allocation allowance, not a minimum or an observed peak
of the Python host. Code and read-only fixed constants are separately finite.
Metadata input labels and any descriptor arrays must be included in S if
not already represented by the two full map tables.

The literal compile_return code walks W routing steps at each of N positions,
so its setup is O(W N), with no hidden W-fold live numeric pass. Alternatively
Pauli descriptors can be composed before enumerating addresses; that optional
implementation is not required by this stated runtime. Index and phase
computation, map storage, cleanup and all fixed-rational scan scratch are
charged. No Gaussian observation schedule or native producer is inferred.

## Evidence and scope

The mathematical proof combines the exact all-width Pauli return identity
from CASCADE-INVERSE.md with the bounded-word fixed-rational theorem from
DIVISION-PROOF.md. An independent review checked 144 extra signed rational
Pauli-routing fixtures, the actual compiled W-step map, a factored wrong-phase
rejection, and the failure of falsely using q = 2 on the genuine order-12
quarter-phase fixture. All three frozen upstream coupler source files were
independently retrieved and matched their pins. Their original LICENSE and
NOTICE files must accompany redistribution. The old source headers' huge
kappa claims are retained provenance, not endorsed by this consumer theorem.
No Lean kernel, hosted CI, original full supplier scientific suite or human
peer review is claimed. Actual observation generation and a favorable complete
paid profile remain unproved.
