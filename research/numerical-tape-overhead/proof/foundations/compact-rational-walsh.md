# Compact rational Walsh execution without spectral lookup tables

Status: **proved conditional numerical component; independently reviewed
by the lead** in [review-compact-rational-walsh.md](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S003/lead/review-compact-rational-walsh.md). The remaining
premise is a compact physical interchange caller,
specified below. This note does not establish that premise or a complete
multiplication overhead bound.

The construction uses S002's [pairwise-newton-division.md](pairwise-newton-division.md),
[polynomial-auxiliary-cost-audit.md](polynomial-auxiliary-cost-audit.md), and the actual OpenAI
`math@3344da59991ed94f9ba711217b29c1d760badfa6` sources:
Fourier `build/kernel.tex` and `build/binary.tex`; tape `build/walsh.tex`,
`build/permutations.tex`, and the uniform precision mechanism in
`build/uniformity.tex`. In particular, the scalar selectors below are the
explicit linear/bilinear functions in those sources, not arbitrary
exponential lookup tables.

All polynomial bounds below have one absolute exponent, independent of m,
the target exponent, the active width, and the input length. The exponent
can be enlarged between displays. The cutoff m>=m0 is fixed and effective;
the bounded initial range uses an exact direct template.

## 1. Numerical template and physical interface

Use odd m with the accepted binary-label guards

    q_F^L <= m^3,  D_F <= m,  A=2(m+D_F-1) <= 4m.

The S002 pairwise/Newton/division template has W0=O(m) seed rows per label,
degree D_pred<=7sqrt(m), and two repair phases each occupying one eighth
of the rows. Unroll it to depth ceil(log2(m)/4), with direct A-axis leaves.
The completed independent batch width W, number of spatial/axis calls
sigma, numbers of finite maps, and all row dimensions are at most m^C.
Retain the exact shared endpoint schedule; only ordinary work may be
overcounted. Assume its verified strict margin

    sigma/W <= A^rho/4,       1/2<rho<1.                (CW1)

The numerical component calls the following **compact physical interface**:
on encoded bit volume V, interchange of width-u address fields with
arbitrary prefix/gap/suffix ranges takes

    m^C V(1+u)^rho

steps and visits at most m^C V cells, with actual generation and retained
description at most m^C. The same bound covers the direct small-width base.
Any separately stated descriptor setup is a polynomial of absolute degree
in log(V+2), with coefficients at most m^C. This is the interface sought
by the new compact characteristic-two routing construction; it is not
assumed from its sparse symbolic matrices.

The source packed-XOR and bit-position reductions use that interchanger,
binary record operations and fixed-degree address arithmetic. Repeating
their guard argument with the known m^C coefficients gives

    m^C V(1+u^rho)(1+log(2+k)) + m^C(1+k)^E,           (CW2)

for an absolute E, when the total numerical address has k bits. To see
uniformity, select a guard of order `(E+C log2(m+2)+4)log2(2+k)`; its
exceptional fraction pays for the stated polynomial record/address work.
Narrow guarded slots are handled directly. Its O(log m) increase stays
polynomial in m. The source functions involved are binary additions,
comparisons and fixed short-axis constructions, with fixed polynomial
degree; no degree depending on an arbitrary embedded program is used.

## 2. Every scalar selector is computed from the address

At each spectral coordinate the j-th binary query has sign (-1)^k_j,
where the source kernel gives

    k_j = sum_columns [X_j Z_j + sum_aux X_i Z_i] mod2. (CW3)

There are O(m) axes. A source/destination coordinate change is an explicit
binary matrix of dimension at most 4m, applied separately to each column.
Initial/final phases and changes of representatives are bilinear forms in
these binary columns. Their coefficients and bases are constructed by
finite-field elimination on polynomial-m matrices. Thus each column costs
poly(m) binary operations. There are at most k columns/bits to examine.

On fixed tapes one may copy the relevant slots from the address counter,
scan all columns, accumulate the O(m) parities, and rewind, as in the
actual tape Walsh proof. Even deliberately scanning the entire k-bit
address for each required selector costs only m^C k per numerical record.
It is paid by that record's Theta(k) encoded width. It is not charged as
a unit-cost random-access lookup. The same argument computes all
coordinate/sign choices used by a routed pencil.

Given k=(k_1,...,k_m), enumerate the W0=O(m) seeds and compute their
pairwise-independent shifts and counts c_t. For each seed evaluate the
integer Newton sum

    p_t = gamma_t sum_(h=0)^D_pred (-2)^h binom(c_t-u,h).

Use the exact integer recurrence for generalized binomial coefficients,
including negative c_t-u. All intermediate bit lengths are
O(sqrt(m)log(m+2)); the safe bound m^C suffices. Compute z=(-1)^sum k_j
and the actual defect set J={t:p_t!=z}. Its size is at most W0/16. No
zero discrepancy is ever divided by.

For nodes x_i=i/W0, use the first |J| rows of the Vandermonde matrix on
J. Its inverse, the nonzero discrepancies, and its transposed inverse
define exactly the division-repair map from S002. The empty set uses a
zero map. Padding to the paid check width is explicit. All of this is
computed from the address key in m^C bit operations and m^C bits.

## 3. Uniform rational heights

The Vandermonde entries x_i^h have numerator/denominator bit lengths
O(m log(m+2)). Clearing denominators and applying the determinant bound
to matrices of side O(m) gives polynomial-m bit lengths for all minors,
inverse entries and fraction-free elimination intermediates. Nonzero
Newton gaps are integers of polynomial-m bit length. Multiplying their
denominators into the two inverse Vandermonde factors still gives only
polynomial-m bit length: the number of factors is O(m), not exponential.

All numerical coefficients therefore have exact representations a/b,
b>0, with

    bitlength(a), bitlength(b) <= B_m <= m^C.           (CW4)

This includes predictor coefficients, source rectangle weights, check and
lift coefficients, and spectral repair coefficients. The actual source
binary normalization cancels every power of two depending on the slot
width f: common and free kernels receive the same 2D_F normalized axis
calls, and complete conversion normalizations cancel across repair.
Only the separately handled one-bit butterfly needs 1/sqrt(2). No
unaccounted f-dependent rational height is present.

## 4. Bounded-divisor preparation is linear in numerical precision

**Lemma CW-D.** Given a signed rational a/b with numerator and positive
denominator at most B bits, one can produce a dyadic approximation with
absolute error less than 2^(-p) in

    O(B^2+p B)

actual steps on a fixed number of ordinary tapes, using O(B+p) visited
cells. Constants are absolute.

**Proof.** Divide |a| by b for the integer part with ordinary binary long
division, costing O(B^2). Keep the remainder r<b in at most B bits. For
each of p fractional bits, double r, compare with b, subtract b if
necessary, and append the resulting quotient bit. Each step scans and
rewinds O(B) bits on a fixed number of tapes. The remainder invariant
gives the usual error below 2^(-p); apply the sign at the end. Output-head
motion and erasure are linear in the written output. QED.

For p=O(k) and k>=B_m, this is m^C k work **per record**, even if the
rational coefficient changes at every address. The divisor has B_m bits,
not k bits. Thus schoolbook preparation here is not an uncharged k-squared
operation. Each multiplication of the prepared coefficient by a record
uses the source's fixed O(k log(2+k)) short-integer multiplier. This pays
for all record products. The O(m^C) scalar operations per record and the
selector work in section 2 together cost m^C k log(2+k) per record.

The approximate coefficient's error is included in the numerical error
ledger; the ideal circuit still uses the exact rational. No 2^m-entry
spectral table, 2^(4m)-entry column table, sorting pass, or per-record
scan of such a table is required.

## 5. Actual local construction and ordinary work

The guarded binary-label family has polynomially many labels, incidences,
rectangles, matrices and row roles. Its bases, paired duals, complements,
binary elimination factors and rational rectangle weights have polynomial
dimensions and bit lengths. Enumerating every label pair and retaining
the source shared call order is polynomial work. Predictor/control code
uses the explicit algorithms above. The finite contraction tree has
polynomially many nodes and polynomial batch width. Hence

    generation, retained description, local scalar workspace <= m^C.

For physical execution, serialize the polynomially many row roles and
incidences by scans, as the source uniformity construction does. A row
matrix of polynomial dimension may use one scan per input/output role;
even this deliberately slow execution costs only polynomial-m passes.
Keep the original rows, destination accumulators and current rectangle
scratch; release scratch before the next rectangle. All data movements,
returns and erasure are within m^C V. The recursive calls remain in their
original shared endpoint order, so no extra calls are introduced by this
ordinary-work bound.

All scalar intermediates from the address-key compiler fit m^C bits. Above
k>=m^C they fit within O(k) record workspace. A fixed number of physical
tapes suffices by binary tracks and serial scans; no number of heads
depending on m is assumed. The exact interchanger permutes encoded
records, so rational coefficients are never reduced into its data field.

## 6. Uniform node count, norms and precision

At one Walsh recursion node there are at most m^C numerical array steps,
and every coefficient has magnitude at most 2^(m^C). A crude uniform bound
for the product of their norm bounds is therefore

    log2 C_level <= m^C.                               (CW5)

Completed child Walsh transforms are unitary; completed exact address
permutations are isometries. The internal binary states of the exact
interchanger are not numerical arrays on which rounding occurs. They
need no Euclidean norm claim. Only numerical arithmetic boundaries enter
this error estimate.

The arity A>=m and branching sigma<=m^C imply at most m^C(1+k)^C nodes
and array operations, with an **absolute** exponent C in k. Applying the
source path-to-common-ancestor argument gives logarithmic propagation
gain at most

    m^C(1+log2(2+k)).                                  (CW6)

Choose an explicit polynomial cutoff k>=K_m=m^C, enlarged so that (CW4),
(CW6), all descriptor workspace, and the absolute-degree setup polynomial
are respectively bounded by fixed fractions of k or by 2^(k/4), as
appropriate. This is possible effectively: for k>=16, log2 k<=sqrt(k),
so increasing the exponent and an absolute multiplicative constant in
K_m pays for m^C log k. Likewise any fixed-degree polynomial m^C k^E is
below 2^(k/4) above an effectively enlarged polynomial K_m.

For input norm at most 2^(Lk), the ideal intermediate norms are then
at most 2^((L+1)k). The number of rounding events, coefficient errors,
sqrt(N)-type array-rounding factors and propagation gains fit the same
2^(O(k)) error ledger as the source. Choosing p=C0 k for one absolute
C0 depending only on the requested L and error exponent D gives error
at most 2^(-Dk). Integer widths also equal an absolute multiple of k.
All rational preparation and its rounding errors from section 4 are
included. Certified bisection prepares the single constant 1/sqrt(2)
in a fixed polynomial in k during setup.

## 7. Walsh recurrence, padding and visited space

For s selected bits with s<=c k/log(2+k), use the source base-A pieces and
pad the leading spectator count to a multiple of W^j at depth j. Because
W<=m^C and A>=m,

    W^j <= m^C(1+s)^C.

Above the same polynomial K_m the genuine spectator count is at least
2^(k/2), so leading padding is at most two. Every child then receives
exactly V/W volume; W-way extraction is polynomially many serial scans.
No hidden exponential number of tapes, roles or batches appears.

At active width a, sections 1--6 give the normalized recurrence

    T(a)<=m^C(1+a^rho)(1+log(2+k))+(sigma/W)T(a/A),    (CW7)

plus the stated absolute-degree setup terms. By (CW1), normalized
recursive terms contract by at most one quarter. The sum over the base-A
pieces costs a further polynomial-m factor, since rho>=1/2 and A<=4m.
Thus the selected-bit layer has the actual bound

    time <= m^C N k(1+k)^rho(1+log(2+k)),
    visited cells <= m^C N k,                        (CW8)

for k>=K_m, with absolute numerical width multiples and error exponent
as above. Descriptor/setup polynomials have an absolute degree and are
absorbed at K_m, not silently treated as constants.

The depth-first schedule parks a polynomial-m multiple of local volume;
spatial child volume is V/W<=V/2, and finite repair child volume is V/8.
Their geometric parked sums preserve the polynomial coefficient. Full
pieces and siblings reuse marked regions. Descriptor workspace fits the
same threshold. This bounds cells ever visited, not only simultaneous
live arrays. Smaller k use direct transforms and are excluded from the
fast asymptotic branch by an actual threshold test.

## 8. What this closes

Under the compact interchange interface of section 1, the rational Walsh
side has polynomial-m prefactors, actual construction/description and
space coefficients, and a polynomial-m threshold in k. In an integer
caller where k is comparable to log n, the corresponding input threshold
is at most 2^(m^C), apart from the source's separate absolute prime-shape
cutoff. No all-frequency preparation table is necessary.

The remaining complete-theorem obligations are the compact interchanger's
actual grouped calls, endpoint maps, masks and repair; full integer
assembly; and a common-space-cap scheduler. This note supplies none of
those by assumption of the desired final time bound. It is a concrete
conditional numerical component with explicit local interfaces.

Credits: OpenAI tape/Fourier source proofs; S002 pairwise-shift, Newton and
division-repair construction and operation audit; elementary bounded-
divisor long division; Jerry Chen (@CubeJerry); AI-assisted S003 physical
and quantitative refinement. No complete tape multiplier or formal build
has been executed.
