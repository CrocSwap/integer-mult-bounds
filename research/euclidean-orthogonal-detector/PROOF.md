# A Euclidean guard for complete orthogonal register programs

This contribution was produced by Nick Petalas. Apache-2.0.

This is a scoped written proof. The finite checker corroborates its identities
and implementation; it is not a formal proof-kernel certificate.

## Exact boundary

There are finitely many independent real registers, each in R^d. All registers
are returned. Instructions are:

- `apply`: replace a register by O or O^T applied to its old value;
- `query`: add c O or c O^T applied to an old source to an old destination;
- `linear`: replace a register by a finite rational linear combination of old
  registers, including repeated occurrences and its own old value.

Each named O is exactly orthogonal. Queries may alias source and destination.
The two program sides receive the same exact initial bank, whose register
Euclidean norms are at most R>=1. Initial coordinates belong to the working
grid h Z, h=2^-p. The special basis input of PR5339 satisfies this condition
for every p. Arbitrary nongrid inputs need their own input-error term.

Truncate every forward matrix entry toward zero to h Z. The stored inverse
is the transpose of this table. At each instruction form the complete new
destination using old register values and exact rational scalar arithmetic,
then truncate each of its coordinates toward zero once to h Z. Other
registers retain their values. These are the numerical semantics of Ali
Romman's [PR5339](https://github.com/CrocSwap/integer-mult-bounds/pull/5339),
now bounded with a different bank norm. Rounded matrices need not be
orthogonal; the proof explicitly charges their perturbation.

## Per-instruction constants

Use the bank norm ||x||=max_j ||x_j||_2. Let s=ceil(sqrt(d)). Set

| Instruction | beta | gamma |
| --- | --- | --- |
| linear with coefficients c_j | max(1, sum_j abs(c_j)) | 0 |
| apply | 1 | d |
| query with coefficient c | 1+abs(c) | d abs(c) |

The exact bank operator has norm at most beta. Each entry error is less
than h, so the matrix perturbation has Frobenius, and hence operator, norm
at most d h. Transposition preserves this bound. The rounded bank operator
therefore has norm at most beta+gamma h and differs from the exact one by
at most gamma h. These inequalities hold on alias because both summands
use the same old source. A linear assignment sums repeated old values.
Unchanged registers explain the harmless maximum with one.

The final coordinate truncations produce a bank residual of norm at most
sqrt(d) h <= s h. This residual is charged for every instruction, even
when the actual arithmetic is exact on the grid.

## Whole-side error bound

For one side of length m, define

    G_i = product_(j<=i) beta_j,  G=G_m,
    A = sum_i gamma_i/beta_i,
    K = G (R A + s m).

Empty products are one and empty sums are zero. Exact prefix magnitudes are
at most R G_i. If E_i is the bank error after instruction i, then

    E_i <= (beta_i+gamma_i h) E_(i-1)
           + gamma_i h R G_(i-1) + s h.                 (1)

This compares the two maps on the exact input and applies the rounded map
to the previous error. It does not assume the approximate bank stays below
the exact bank's magnitude envelope.

For nonnegative a_i=gamma_i/beta_i and h A<1,

    product_i (1+h a_i) <= 1/(1-h A).                  (2)

Indeed the coefficient of h^k in the finite product is at most A^k, so the
product is bounded by the geometric series. The same bound applies to
every suffix. Unrolling (1) and dividing a suffix product by G_i gives

    E_m <= h G/(1-h A)
           [R sum_i gamma_i/beta_i + s sum_i 1/G_i]
         <= h K/(1-h A).                              (3)

The last inequality uses beta_i>=1, hence G_i>=1. Equation (3) is zero
for an empty side. If h A<=1/2, it gives E_m<=2h K. It also bounds every
prefix using that prefix's own G,A,K.

For the two sides let A_max=max(A_left,A_right) and K_total=K_left+K_right.
Every coordinate of their returned difference has error at most

    2 K_total h,

provided h A_max<=1/2. Both sides' errors and every returned role are
included. No factor of the number of registers occurs in this bank norm.

## A funded exact endpoint decision

Assume a positive rational eta such that a selected exact endpoint f either
vanishes or has abs(f)>=eta. It suffices to choose integer p>=0 with

    2^p >= max(1, 2 A_max, 8 K_total/eta).              (4)

Then the returned difference f_hat has abs(f_hat-f)<=eta/4. Consequently
abs(f_hat)>eta/2 decides f!=0. A zero at one tuple is not a universal
program-identity certificate.

For the rational Cayley path parameter t=A0/B in lowest terms, 0<t<=1/4,
dimension d, and q named calls across both sides, PR5339 supplies the cited
separator

    eta = 1/[C (3B)^(dq)],

where C is the product of every scalar coefficient denominator occurrence.
This separator and its source proof are premises here; their mathematical
verification is not this contribution. No refined matrix-denominator or
program-cancellation result is used.

The allocator uses this coarse separator for the source basis input or an
integer initial bank. Integer linear combinations of the same input columns
retain its common denominator. A noninteger grid input requires its input
denominator in the separator as well; the allocator supplies no such
extension. The error theorem (1)-(4), with a separately justified eta,
still applies to exact grid inputs under its stated radius contract.

For apply-only programs, G=1, A=d m, and K=m(Rd+s). At R=1 the new rounding
factor is linear in m and d. The older guard uses the product d^q as a
coordinate-norm gain, although its operators are exactly orthogonal.
For one side with d=4, q=m=12, B=4 and no scalar coefficients, the same
coarse eta gives 182 bits by (4), versus 228 by the old sufficient guard.
These are sufficient bounds, not minimum precisions. No universal strict
improvement over the old guard is asserted for arbitrary scalar programs.

## Arithmetic work and limitations

The new allocator uses rational products and sums over the explicit program.
Its coefficients and precision requirement have polynomial binary size in
the program, scalar, parameter and dimension input sizes. After the path
and rational matrices are supplied, the literal integer-grid replay still
uses q d^2 matrix-entry products and m d coordinate truncations, plus all
scalar linear combinations, parsing, preparation and returned-bank work.
This result reduces a sufficient data precision. It supplies no wall-clock
speedup, cheaper native invocation or full tape invoice.

Orthogonality is an essential premise. General approximately unitary or
nonorthogonal generators need their own exact gains. Nongrid inputs, complex
coordinate rounding, floating hardware, and repeated use of a stored inverse
as an exact undo are outside this stated implementation. Dirty values are
covered within the radius and grid contract; the detector does not erase or
restore them by fiat. Native compatibility, physical allocation, compiler,
stock, selected precision/tape policy and analytic recovery remain separate.

## Credit and relation to prior work

Ali Romman / PR5339 supplies the complete numerical detector, coarse
separator and open optimization question. His PR5315 supplies the rational
orthogonal witness. Krzysztof Wojt / PR5262 supplies the complete inverse
grammar and shortest-word compiler; zxv / PR5235 and the retained
dirty-echo/tensor/phase lineage keep their credit. Nick Petalas / PR5941
changes the separation lattice through exact matrix denominators. This
proof holds that lattice bound fixed and changes error amplification. It
does not pursue PR5941's cancellation or native-binding questions.

Euclidean orthogonal invariance, Frobenius domination and forward-error
propagation are classical. The new result is the explicit complete-grammar
guard (3)-(4), its allocator, and the strictly smaller sufficient grid for
the specified literal consumer. No general literature priority is claimed.
