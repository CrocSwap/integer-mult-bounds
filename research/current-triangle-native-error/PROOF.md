# Complete local error operator in the actual triangle charts

## Quantified contract

Use the exact three-field blocks of PR #7669, candidate
`ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d`.
The source and edit are pinned at
`95d476623f1468822057554475dc8badb19bfa44`. The copied PR #7671 verifier
reconstructs the complete candidate and binds both local windows. The
source's later documentation head does not change those words or tapes.

Let H be the complex Hilbert space of a complete native field, including
all positive column multiplicities and complete spectators. Let T_A,T_B,T_C
be the exact unitary frames for A=265, B=751 and C=927. Write

```text
U = T_B T_A*,   V = T_C T_A*,   W = T_C T_B*.
V = WU.
```

At entry, x=role236 and z=role1000 are in A; y=role544 is in B. Reference
MOVE applies its exact frame quotient. Each actual MOVE can return that
reference value plus a local error vector. Each fractional scalar ADD
can also return its exact value plus an error vector. Integral scalar
ADDs are exact under the stated no-overflow contract. This proof does
not construct the error allowances or establish an admitted input grid.

The comparison is between each actual block and its exact evaluation on
the same entry fields. Earlier input error is not silently set to zero:
relative to a different ideal entry it must also pass through the source
rational matrix M. This result gives the additional local error.

At exit, the old charts are `(B,C,B)` and the new charts are `(C,C,B)`.
For the output norm, represent all three fields in C. The old x and both
z outputs are transformed only in this mathematical comparison. These
isometries are not added program operations or free physical conversions.

## Native frames and all-size lift

The retained direct frame implementation expresses a frame as phase and
permutation conjugation of Gaussian gates. One gate is

```text
C_v = ((1+i)/2) I + ((1-i)/2) X_v,
```

where X_v is a self-adjoint involution. The squared moduli of the two
coefficients sum to one, and their cross term has zero real part. Thus
`C_v* C_v = I`. The opposite sign gives its adjoint. Address permutations
and phases in `{1,i,-1,-i}` are unitary. Their products and conjugates
are therefore unitary, with the exact global phase retained.

A tensor product of these frames remains unitary for every positive
column multiplicity. A tensor identity on complete spectators also
preserves the norm. The quotient relation `V=WU` holds in each case.
This supplies the mathematical frame property used below. It does not
construct a finite-tape provider at any proposed error or time allowance.

The verifier checks all 512 forward/adjoint columns of each of the three
literal one-column frames. It also executes both local tapes on complete
512-component complex fields. These finite checks bind the exact source
formula and phase. The preceding tensor argument gives the stated lift.

## New block: all six residuals

Name the residuals in chronological order:

| Name | Literal operation | Frame of the residual |
| --- | --- | --- |
| e1 | x += z/4 | A |
| m1 | MOVE x from A to C | C |
| m2 | MOVE z from A to B | B |
| e2 | y += z/2 | B |
| m3 | MOVE y from B to C | C |
| e3 | x += y/2 | C |

The integral updates `z-=2x`, `z+=2y`, and `y-=x` remain in the tape.
Substitution through all nine events gives the exit error in physical
charts `(C,C,B)`:

```text
error_x = (1/2)m1 + (1/4)Wm2 + (1/2)We2 + (1/2)m3 + e3
error_y = -2Ve1 - m1 + (1/2)Wm2 + We2 + m3
error_z = -4Ue1 + 2m2 + 2e2.
```

The first scalar residual cancels from x. It remains in y and z. The
native MOVE residuals do not share that cancellation.

Align the residual vector as
`d_new=(Ve1,m1,Wm2,We2,m3,e3)`. Align z to C. The complete output error
is exactly `N d_new`, with scalar coefficients acting on H:

```text
N = [ 0   1/2   1/4   1/2   1/2   1 ]
    [-2   -1    1/2    1     1    0 ]
    [-4    0     2     2     0    0 ].
```

The input alignment is unitary on each port. It preserves the sum of
squared residual norms. This identity applies to any realized errors,
including errors that depend on the current fields or on earlier errors.
No statistical or algebraic independence is needed for the upper bound.

## Old block and direct comparison

Let m1o be the old x MOVE residual in B, m2o the old z MOVE residual in B,
e0 the old quarter-ADD residual in B, and m3o the old y MOVE residual in C.
After alignment to C, use `d_old=(Wm1o,Wm2o,We0,m3o)`. The error is
exactly `O d_old`, where

```text
O = [ 0   1/4   1   0 ]
    [-2    0    0   1 ]
    [-4    1    0   0 ].
```

Both exact blocks have the same aligned output, so the difference of
actual outputs is `[N|-O](d_new,d_old)`. This comparison retains every
local error from both executions. It does not identify errors at two
different sites merely because their nominal operations have equal cost.

## Exact induced constants

For any real scalar matrix K acting on H-valued columns,
`||K tensor I_H||_2 = sqrt(lambda_max(K K^T))`. An upper bound follows by
diagonalizing the real Gram matrix. Equality is attained by a largest
left singular vector and any unit vector of H. Because each port's
frame alignment is a unitary bijection, the same sharp constant applies
to arbitrary residual vectors in their physical frames.

This sharpness statement concerns the stated unrestricted residual
contract. It does not assert that independent extremal errors are
reachable under a particular floor quantizer or caller input.

The integer matrices below are 16 times the three Gram matrices:

```text
16 O O^T = [17   0    4]
           [ 0  80  128]
           [ 4 128  272]

16 N N^T = [29  10   24]
           [10 116  176]
           [24 176  384].

16 [N|-O][N|-O]^T is the sum of these two matrices.
```

Their characteristic polynomials are respectively

```text
p_old(t) = t^3 - 369t^2 + 11344t - 90112
p_new(t) = t^3 - 529t^2 + 27392t - 372736
p_difference(t) = t^3 - 898t^2 + 74468t - 1614336.
```

For each polynomial, divide its largest root by 16 and take the square
root to obtain the induced constant. Exact rational intervals certify:

```text
4.582849288401 < C_old < 4.582849288402
5.435547392075 < C_new < 5.435547392076
7.107859846622 < C_difference < 7.107859846623.
```

The receipt gives rational endpoints for each squared constant, separated
by less than 10^-20. At the upper endpoint all leading principal minors
of `qI-G` are positive, so it is positive definite. At the lower endpoint
the first two minors are positive and the determinant is negative, so it
has one negative eigenvalue. This isolates the largest eigenvalue. The
stated square-root intervals are also checked by exact rational squaring.
No floating-point eigenvalue is used in the certificate.

If E_new is the square root of the sum of all six squared residual
norms, the new local error is at most `C_new E_new`. Corresponding bounds
hold for the four old ports and the ten-port difference. These constants
use a joint error budget; they are not a comparison at an equal per-site
allowance or a claim that the new tape has smaller error.

For example, if all three fractional scalar operations have grid spacing
Delta on N complex coordinates and all stored operands are on that grid,
their squared error allowances sum to at most `17N Delta^2/8`. If the three
native residual norms are at most rho1,rho2,rho3, then

```text
new local error <= C_new sqrt(rho1^2+rho2^2+rho3^2+17N Delta^2/8).
```

This is a valid upper bound under those premises. It is not claimed sharp
for floor rounding. The native allowances and grid/range premises remain
to be supplied. A later caller must also propagate earlier input error
through its exact rational map and account for later work.

## Verification and limits

The symbolic derivation follows the literal event order, tracks all
current charts and inserts one formal residual at each listed site. It
matches the separately derived matrices above. A distinct exact Gaussian
field execution checks each of the ten ports on all 512 complex
coordinates, with the actual native quotients and output alignment. Each
one-port squared gain is also checked directly. Four controls detect an
omitted native residual, a lost factor two, a native global-phase fault
and a missing old x exit alignment.

The proof does not choose native quantizers, prove reachable residues,
set signed widths, construct physical conversion services or price a
complete caller. Full native/caller replay, analytic recovery and all
five inherited framework assumptions remain open. No new kappa or
selected-frontier change is claimed.
