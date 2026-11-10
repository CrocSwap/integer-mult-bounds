# A concrete fixed-grid completed-call contract for C0 and C2

JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.

## Scope and existing work

PR4743 supplies the literal two- and three-call triangular ports, their inverse
schedules and arbitrary dirty-bank interpretation. `native-error-channel-amplification`
already proves source-ordered completed-call error amplification. That result
assumes an implementation returns its exact Gaussian transform of its **actual
stored input** within a requested complex-coordinate radius. This package
constructs one such implementation, including internal range and direct work.

This is not the first deterministic native rounding example. Arham Tahir's
PR3036 and the retained `qq16-native-rounded-components` implement pair-first
native Gaussian interiors with floating significands and prove a whole-F0
failure. We reuse its conventional butterfly lowering and signed ties-to-even
method as credited precedent. Our new scope is a uniform fixed-grid accuracy
service for the actual C0/C2 tensor letters, with a completed-call theorem and
all four PR4743 port schedules. We do not rerun or claim novelty for full F0.

## Actual arithmetic ABI and operation order

Let h=2^-g. Store each real/imaginary component as a signed integer times h.
All inputs to a call have this form. The Cj base letter is

    Cj = ((1+i) I + (1-i) Xj)/2.

On a complex pair `(a+ib,c+id)` of grid integers, form EXACT integer values

    sr=a+c; si=b+d; dr=a-c; di=b-d;
    n0=sr-di; n1=si+dr; n2=sr+di; n3=si-dr.

Store nearest-even(n0/2),...,nearest-even(n3/2). For the adjoint use
`sr+di, si-dr, sr-di, si+dr`. Overflow checks precede every numerator storage.
For every signed integer n, put q=n>>1 with arithmetic right shift (floor), and

    nearest_even(n/2) = q + ((n & 1) & (q & 1)).

For even n this is exact. For odd n the two nearest integers are q and q+1;
the expression selects the even one, also when n<0. This is an explicit
arithmetic-shift ABI, not a division-free claim for a machine lacking that
instruction. No floating exponent, division oracle or unbounded-word primitive
is used. Pair sums are exact on the grid, so intermediate rounding at those
sums would do nothing; rounding occurs at the four final halves.

On N=8^f entries apply this butterfly on bit positions3k+j for k=0,...,f-1,
in that declared order, j=0 or2. These commuting exact coordinate factors
produce Cj^tensor f before rounding; the rounded factors need not commute.
`rounded.call` executes the stated order and charges all fN/2 butterflies.

## Uniform completed-call defect and internal range

For one butterfly, each real component error has absolute value at most h/2,
so each complex coordinate has error at most h/sqrt2. The coordinate infinity
norm of one exact Gaussian factor is sqrt2. If delta_k is the maximum error
versus the exact first k factors applied to the actual stored input, then

    delta_0=0;
    delta_(k+1) <= sqrt2 delta_k + h/sqrt2.

Thus for every f>=1, both axes and both adjoint choices,

    delta_f <= eta_f h,
    eta_f = (2^(f/2)-1)/(2-sqrt2) < 2 * 2^(f/2).

This is a sufficient bound; no sharpness of eta_f for deterministic arithmetic
is claimed. The proof uses actual errors on actual perturbed inputs, not a
promise valid only at an ideal input. Correlations cannot invalidate the upper
bound. If the call's stored input has complex magnitude at most U, after k
stages it is at most `2^(k/2) U + eta_k h < 2^(k/2)(U+2h)`.
Each integer numerator formed at the next stage is at most four times the
component bound divided by h. These are explicit internal cuts, not merely
endpoint conditioning.

To meet a requested completed-call tolerance rho=2^-q choose

    g = q + ceil(f/2) + 1.

Then `eta_f 2^-g < rho`. Nearest-even input quantization at the same grid has
complex error at most h/sqrt2 < rho. This does not require extra free fault
variables or independence between the actual roundings.

## Source-ordered port substitution and sufficient widths

Retain the actual P=S U S,Q=S V01 S,W=Z0 Z2,M=Z1 V01 monomials and their global
phases. The three-call forward order is A on x; the two separately conjugated
P and Q additions into y; A on y; W on y; C2 on y; M on y. The reverse order
is M^-1,C2^-1,W^-1,A^-1 on y; subtract the two monomial terms from retained x;
then A^-1 on x. Two-call variants omit the extra C2/M/W layer. Each free update
really maps x, adds to y, then restores x. Integer scaling by2 is a left shift.
These monomial/integer operations are exact on the common grid and checked
against word bounds. The completed C2 defect is before M, not after it.

The predecessor's proved external tolerance for final error2^-P is2^-q with:

| schedule | q |
|---|---|
| two-call forward |P+f+3|
| three-call forward |P+ceil(3f/2)+3|
| two-call reverse |P+ceil(f/2)+2|
| three-call reverse |P+f+2|

Choose g=q+ceil(f/2)+1 as above. Every completed call satisfies that tolerance,
and so does initial quantization. Substitution into the credited source-ordered
error-channel proof gives final complex-coordinate error at most2^-P on both
banks, for every f>=1 and P>=0. Independence of actual defects is unnecessary:
the predecessor bound holds for every choice in the enclosing balls. There is
no new proof of its sharp external constant or claim that our implementation
attains it.

For original complex coordinate magnitudes at most2^H, H>=0, the predecessor's
port-entry/internal-between-call allowance2^(H+2f+4) remains valid since each
new completed-call defect is below its requested rho<=1/8. Put U equal to that
allowance. Since h<=1 and U>=1, the call-internal prefix is below2^(ceil(f/2))(U+2h)
<=3*2^(ceil(f/2))*U. Numerators are less than12 times that binary U factor.
Consequently the conservative signed component width

    w = H + g + 2f + ceil(f/2) + 9

suffices for all exact pair sums, differences, numerators, rounded outputs,
integer mix intermediates and phase negations. The extra fixed margin covers
sign and the factor12; no wraparound is allowed. For f,H,P=O(log n), this width
is O(log n); it is not a numerical constant independent of the input size.
The verifier actively rejects insufficient width at a numerator before rounding.

## Costs, workspace and restoration

Each butterfly uses8 signed additions/subtractions and four half-even operations.
Each half uses one arithmetic shift, three ANDs and one ADD:28 elementary
integer operations per butterfly, plus4 real reads and4 real writes. One call
therefore costs14 f N integer operations and2 f N real reads plus2 f N writes,
before bounded loop/address overhead. It uses eight real scratch words and
constant loop indices; the arrays are updated in place. Both forward and inverse
call cost this same direct bound. This is O(fN) work, NOT the recursive rank-one
child's advertised accelerated tariff. All calls in both port directions are
counted. The implementation is a sufficient accuracy backend and control, not
an admissible faster multiplication supplier.

The executable monomial backend builds N address/phase records in O(fN) bounded
word work, traverses cycles with N owned visited bytes and two held complex
values, then explicitly zeros the route/visited fields. This is O(N) owned
control workspace, not a clean independent productive bank. Metadata,
allocation, initialization, clearing, sign operations and mixing retain their
O(fN)/O(N) costs. Source/native O(N) monomial implementations may replace this
conservative backend only with their own source-bound proof. The reference
oracle and optional verifier cut snapshots allocate extra arrays as proof
instrumentation; they are not claimed production scratch or included in the
small-workspace algorithm. No actual caller dirty array is cleared or borrowed.
Only owned work is initialized/cleared; approximate forward/reverse composition
need not restore arbitrary numerical input exactly.

## Realizable defects are more constrained than independent balls

For one pair, all four numerator parities equal a+b+c+d modulo2. Therefore
all four real rounding defects are zero together, or all four have magnitude
h/2. An isolated one-real-component defect is permitted by an independent-ball
relaxation but impossible at this cut. The grid input `(1,0),(0,0)` rounds to
zero on both output coordinates, while the exact C0 image is nonzero: a concrete
reachable half-grid loss, with no injected fault. This is compatible with the
sufficient error bound; it is not a failure at the guarded requested tolerance.
The parity argument is uniform over every integer input; the625-case census
corroborates it and does not establish it by extrapolation.

## Evidence and limitations

The source-authenticated exact sparse-matrix engine is retained from
`native-error-channel-amplification`, credited rather than claimed new. Production
monomial/rounding code imports none of it. Exact tensor matrices independently
check actual C0/C2/adjoint output errors on nonzero-rounding inputs through f=3;
all twelve complete port cases compare against exact rational trajectories,
including an off-grid original input quantized to the stored grid. Every paid
cut is compared to the exact transform of its actual stored input. Signed tie,
wrong-axis, adjoint, overflow and domain controls reject. The all-f theorem is
the recurrence proof above, not the finite checks. Complete recursive substitution,
fast Gaussian call implementation, fixed tapes, native supplier/outer admission,
and selected5413 reproduction remain outside scope.

## Register allocation and instrumentation distinction

The eight-word butterfly allocation is an explicit overwrite schedule: load
a,b,c,d into slots0..3; place sr,si,dr,di in slots4..7; overwrite0..3 with the
four numerators; round/store those four slots. Python retains extra named
intermediate objects as a semantic reference and is not the register allocator.
`port` defaults to in-place operation with no cut snapshots. Only the verifier
requests `capture=True`, making copied inputs and per-call before/after arrays
for independent checks. The verifier separately requires the production default
to return the identical objects, outputs and trace with no captured arrays.
