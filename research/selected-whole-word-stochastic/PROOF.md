# Whole-word stochastic precision for selected PR6030

## Result and exact source

This is a conditional completed-operation precision theorem for the current
selected [PR #6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030)
word. The input is `research/p104-helper470-twin-rung-removal/WORD.json.gz`
at canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
[SOURCES.json](SOURCES.json) binds its exact bytes. The construction's audited
head is `772dd10a5859a1d15f4851feb371519789213ad8`. The current selected
conditional kappa remains 0.003125804. All five framework assumptions remain.

The word has 22,803 events, 770 public fields and 29 owned labels. The new
certificate covers the whole word, including every MOVE. It does not
transfer the historical PR5599 prefix constants from
[PR #6026](https://github.com/CrocSwap/integer-mult-bounds/pull/6026).
The [released whole-word idea](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19226301)
is credited to Nick Petalas. Its unpublished numerical constants are not used.

Assume B > 0. Under the contract below, for every integer t >= 0:

| Common relative allowance u | Guarantee |
|---|---|
| u <= 2^(-t-13) | Each field at each prefix has RMS error below B 2^-t. Final public RMS is at most rho B 2^-t, with rho = 24842101/31854592 < 1. |
| u <= 2^(-t-16), B > 0 | Probability that any field at any prefix has error norm at least B 2^-t is strictly below 2^-41. |
| u <= 2^(-t-17) | The matched absolute-error formula gives error below B 2^-t for every allowed defect sequence. |

These are different guarantees. They are sufficient guard parameters in a
completed-error model, not least machine precisions or a physical speedup.
For B = 0 every error is zero almost surely. The positive-threshold tail
statement has this separate zero case; it never asserts Pr(0 >= 0) < 1.
No new complete kappa, physical supplier or selected assumption discharge
follows from this result.

## Completed-operation contract

Each field is a vector in a finite-dimensional complex Hilbert space. Inputs
have no initial error and each public input has norm at most B >= 0. All
public fields carry arbitrary inputs, including dirty helpers.
Owned labels are inactive until their exact INIT. Use deterministic unitary
native charts with the source's exact phases. In decoded coordinates a MOVE
is the identity; coframed ADD, SCALE and COPY use the word's rational scalar.
This retained native premise is not proved here. It must hold at the actual
column multiplicity where this theorem is applied.

Let u >= 0. INIT, COPY and CLEAR are exact. A completed MOVE, ADD or SCALE can add one
vector defect delta_j to its destination after the exact operation on the
actual inputs. Conditional on the full past, E[delta_j | F_(j-1)] = 0.
No independence between defects is assumed. The pathwise bounds are:

| Event | Bound on the defect norm |
|---|---|
| MOVE r | u times norm of actual input r |
| ADD r += q s | u times (norm of actual r + abs(q) times norm of actual s) |
| SCALE r *= q | u times abs(q) times norm of actual input r |

The word, coefficients and charts are fixed, not chosen from the noise.
All internal rounding and native errors must fit this completed contract.
Unconditional mean zero alone is insufficient. No physical algorithm that
provides this contract for every native event is supplied here.

## Exact transfer certificate

Let R(t,r) be the rational initial-input row of field r after t events, and
p(t,r) its L1 norm. The ideal field norm is at most p(t,r) B. At event j set

```text
MOVE:   a_j = p(j,r),                     c_j = 1
ADD:    a_j = p(j,r) + abs(q) p(j,s),      c_j = 1 + abs(q)
SCALE:  a_j = abs(q) p(j,r),               c_j = abs(q).
```

Weights at exact events are not used for injection. Let C(t,r,j) be the
signed scalar coefficient of defect j in field r at cut t. CLEAR removes
its own row; it cannot remove errors already copied to another field. COPY
replaces its destination row. The exact error is

```text
e(t,r) = sum_(j<t) C(t,r,j) delta_j.
J2(t,r) = sum_j C(t,r,j)^2 a_j^2
K2(t,r) = sum_j C(t,r,j)^2 c_j^2.
```

A Fraction input-row interpreter and a separate integer-row interpreter
with binary denominators agree on every operand weight. A forward signed
error interpreter and a separate transpose agree on all coefficients and
all four scores at each of the 799 final fields. Reverse substitution also
checks every attained peak score and the maximum ideal input row.

The all-prefix maxima are:

```text
max J2 = 48438375
max K2 = 5490111/32
max sum_j abs(C) a_j = 233317/2
max sum_j abs(C) c_j = 13578.
```

All four occur at cut 20644, field 558. Cuts count completed events.
The maximum ideal-row L1 norm is 850 at cut 20479, field 558. These values come
from the selected source, not an older word. [RESULT.json](RESULT.json)
retains every final score, coefficient digest, exact peak and guard comparison.
For the bounds below use the integer upper square roots J = 6960 and K = 415.
Integer arithmetic verifies J^2 >= max J2 and K^2 >= max K2.

## RMS bound with actual-input feedback

For i < j, delta_i is measurable before delta_j. Conditional zero mean
therefore makes E Re<delta_i,delta_j> = 0. Multiplication by deterministic
signed coefficients preserves this orthogonality. Thus

```text
E ||e(t,r)||^2 = sum_j C(t,r,j)^2 E ||delta_j||^2.
```

Let E_* be the maximum individual RMS error over all fields and cuts. This
is a maximum of expectations, not the RMS of the maximum. The triangle
inequality in L2 gives

```text
||delta_j||_(L2) <= u (a_j B + c_j E_*).
```

Apply the Euclidean triangle inequality to the coefficient-weighted vectors
(a_j) and (c_j). It gives E_* <= u (J B + K E_*). If u K < 1, then

```text
E_* <= B u J / (1-u K).
```

At u = 2^-13 this is B 6960/7777 < B. Since the normalized bound increases
with u, u <= 2^(-t-13) gives E_* < B 2^-t for every integer t >= 0 and B > 0.
For a final row let j_r and k_r be the integer upper square roots of its
exact J2 and K2 scores. Then

```text
RMS_final(r) <= B u (j_r + k_r u J/(1-u K)).
```

At guard 13 the largest normalized bound is rho = 24842101/31854592, at
field 558. Guard 12 gives 4003111/2512896 > 1 for this formula. Every smaller
guard is also checked. Thus 13 is the least integer accepted by this stated
integer-ceiling certificate. It is not a lower bound on actual rounding.

For comparison, omit conditional zero mean and apply the triangle inequality
to signed defect transfer. The matched absolute constants are J_abs =
233317/2 and K_abs = 13578. The same feedback formula requires guard 17 for
all prefixes. Its final guard is also 17; guard 16 gives
29461326645/27240955904 > 1. This is a comparison on identical source bytes
and relative allowances, not a transfer of a predecessor's guard count.

## A dimension-independent Hilbert tail lemma

Let X_j be Hilbert-space martingale differences with deterministic bounds
||X_j|| <= b_j. Set S = sum_j X_j and V = sum_j b_j^2. For R > 0 and V > 0,

```text
Pr(||S|| >= R) <= 2 exp(-R^2/(2V)).
```

Here is a proof, to make the dimension and constants explicit. For fixed x,
let a = ||x|| and let ||h|| <= b. For a,b > 0 write d = Re<x,h>/a. Then
-b <= d <= b and ||x+h||^2 <= a^2+b^2+2ad. The function
F(s) = cosh(lambda sqrt(s)) has a power series with nonnegative coefficients,
so it is increasing and convex on s >= 0. Bound it by the secant between
(a-b)^2 and (a+b)^2. This gives

```text
cosh(lambda ||x+h||)
 <= cosh(lambda a) cosh(lambda b)
    + (d/b) sinh(lambda a) sinh(lambda b).
```

The a=0 or b=0 cases follow directly. On conditioning, E[h | past] = 0
removes the second term. Iterate and use cosh(z) <= exp(z^2/2), which follows
term by term from (2k)! >= 2^k k!. Therefore
E cosh(lambda ||S||) <= exp(lambda^2 V/2). Markov's inequality and
cosh(lambda R) >= exp(lambda R)/2 give the tail bound after lambda = R/V.
If V=0, S=0 almost surely. The argument applies to real or complex Hilbert
spaces and requires neither coordinate independence nor fixed dimension.
These martingale and exponential-moment methods are classical.

## Stop at the first prefix error excursion

Assume B > 0 and put R = B 2^-t. Let tau be the first event after which any
field has error norm at least R. Define stopped defects

```text
delta'_j = delta_j * 1_{tau >= j}.
```

The indicator depends only on earlier events, so the stopped defects still
have conditional mean zero. Before the first excursion all operand errors
are below R. Thus every stopped defect has the deterministic bound
u B (a_j + c_j 2^-t). At the first excursion, the actual error and the
stopped linear error sum agree. Later resets cannot hide that first event.
For any fixed cut and its updated field, the tail lemma applies with

```text
V <= u^2 B^2 (J + K 2^-t)^2 <= u^2 B^2 (J+K)^2.
```

There is one changed field per event. An unchanged field cannot create a
first excursion. A union over the 22,803 event destinations therefore covers
all 799 fields at all cuts; an extra factor 799 is not needed. For
u <= 2^(-t-16), the failure probability is at most

```text
45606 exp(-2147483648/54390625) < 2^-41.
```

The strict inequality has a rational certificate: with
x = 2147483648/54390625, the positive sum sum_(k=0)^64 x^k/k! exceeds
45606 * 2^41. Since exp(x) is strictly larger than that sum, no numerical
logarithm or floating-point exponential is needed. The full rational sum
is retained in RESULT.json.

For B = 0, induction on events gives zero ideal values and zero actual
values: the relative allowance is zero, and exact COPY and resets preserve
zero. Errors are identically zero. In particular Pr(max error > 0)=0,
whereas Pr(max error >= 0)=1. This resolves the released handoff's failed
zero-threshold corollary without changing a probability event silently.

For M separate complete invocations satisfying the contract, a union bound
gives failure below M 2^-41. No independence between invocations is required
for that union bound. A complete multiplier must choose its own invocation
count and recovery budget. The 13-bit RMS bound alone also gives the weaker
output union bound 770 rho^2 2^(-2s) with s extra bits and a positive
threshold. Neither bound identifies maximum individual RMS with RMS of a
maximum.

## Checks and remaining obligations

Normal and optimized verifiers use explicit conditions. All 22,803 ideal
weight pairs agree between Fraction and integer arithmetic. All 799 final
error rows agree coefficient by coefficient between forward and transpose
engines. All four peaks and the ideal peak have reverse checks. The exact
certificate tests every smaller candidate guard for its stated formulas.
There are 36 fully enumerated adaptive-noise fixtures with 218 terminal
states and 900 integer square-root cases. Controls detect reused randomness,
bias, omitted feedback, wrong COPY/reset semantics, an erased prefix
excursion and the false non-strict zero-threshold probability claim. A
changed source file fails authentication. These are author-side executable
checks, not independent human or proof-kernel acceptance.

The ideal ledger confirms that 30 of 31 CLEAR events erase nonzero ideal
data. Exact reset is a supplied premise, not a known-zero erasure proof.
Small stochastic error does not give exact dirty restoration. Native
unitarity/absolute phases, completed conditional mean-zero errors, initial
conversion, overflow bounds, random-bit access, native internal precision,
fixed tapes, storage, erasure, compiler, analytic recovery and a complete
multiplier remain separate obligations. No physical rounder or selected
cold replay is supplied. No paid/target profile or selected file is changed.

## Credit

DreamingOfClouds / @DreamingOfClouds supplied PR6030 and its source edit.
Its [retained README](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/p104-helper470-twin-rung-removal/README.md)
credits the full P104/native/caller lineage and the maintainer's gzip repair.
Ali Romman's [PR #5819](https://github.com/CrocSwap/integer-mult-bounds/pull/5819)
and [completed-error proof](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/p104-sharp-norm-error/PROOF.md)
supply the operand-weighted feedback method, with Adam Gall, ywz65 and the
[PR #2878](https://github.com/CrocSwap/integer-mult-bounds/pull/2878) lineage retained. Nick Petalas / @petalas supplied the released idea,
its disclosed probability error and PR6026's distinct
[historical prefix proof](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/p104-stochastic-prefix/PROOF.md).
Classical martingale orthogonality, stopping and second-moment/exponential
bounds are not claimed new. The contribution is the complete selected-word
ledger and the source-specific feedback, Hilbert-tail and zero-scale bounds.
Prepared by Ali Romman with substantial OpenAI Codex assistance. New work is
Apache-2.0; all predecessor notices remain applicable.
