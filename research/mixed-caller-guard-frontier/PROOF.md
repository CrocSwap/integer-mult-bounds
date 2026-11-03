# Complete guard frontier for the mixed caller

## The inherited source contract

Freeze PR6473 at `15a7e8d2e90f23977393613e6d0889614b144ad7`.
Its PR6398 caller has 34 fields, 18 stages and 570 events. The exact source
calculation gives four final field-error coefficients

`a=(795/2,28,18,28)`

in the order scalar, LOCAL, QUERY, idle. Field0 attains each of these four
class bounds; it dominates all other 33 rows componentwise. Thus the complete
row-specific sufficient envelope is exactly the one inequality

`sum_i a_i e_i < epsilon`.

This is the inherited sufficient envelope, not the optimal actual error
amplification. PR6473 owns that envelope and its nine-uniform-bit theorem.
ToikY's PR6510 independently audits it. PR6477 concerns a different selected
P104 word and a two-rate contract; its frontier does not transfer here.

The fields use a Hilbert-space 2-norm. Stages are commuting unitaries and
Q is unitary with Q^4=I. Error bounds concern the completed operation on the
actual approximate input. No independence of defects is assumed.

Retain PR6510's clarification. For arbitrary Q, a normalizer needs the
explicit grouped completed-defect premise `9 e_scalar/2`. The literal four
half-field operations require a compatible translation pair, with Q² equal
to the pair swap. Q^4=I alone does not construct that implementation. The
half-field digit tariff and internal normalizer bound below are conditional
on that compatible realization. The abstract frontier needs only the
completed-defect envelope. This older mixed caller is not selected PR6030.

Set epsilon=2^-p and e_i=2^(-p-g_i), with nonnegative integer guards g_i.
The feasible envelope becomes `S(g)=sum_i a_i 2^-g_i < 1`.
We determine all componentwise minimal feasible tuples, without a chosen
search cutoff.

## A finite bound for every positive dyadic envelope

Let a_1,...,a_m be positive dyadic rationals. Choose d≥0 so every 2^d a_i
is an integer. Put

`A=sum_i a_i`, `B=max(0,floor(log2(2A)))`,
`G=m B+(m-1)d`.

Every componentwise minimal nonnegative integer feasible tuple has every
coordinate at most G.

Proof. If all guards are zero, the conclusion holds. Otherwise select a
largest positive guard, and denote its term by t_*. Minimality means that
reducing this guard by one is infeasible. Hence `S(g)+t_*≥1`.
Sort the guards as g_1≤...≤g_m, with this coordinate last. Since
`S+t_*≤2A 2^-g_1`, one has g_1≤B.

For 1≤k<m, let S_k be the sum of the first k terms. Since S_k<S<1,
its distance from one is positive. Its denominator divides 2^(g_k+d), so

`1-S_k ≥ 2^(-g_k-d)`.

All remaining terms, including t_*, have guards at least g_(k+1). Therefore

`2^(-g_k-d) ≤ 1-S_k ≤ (S-S_k)+t_* ≤ 2A 2^-g_(k+1)`.

Taking integer powers of two gives `g_(k+1)≤g_k+d+B`. Induction proves the
bound G. This argument does not assume equal coefficients or a particular
linear tariff. Finiteness of minimal elements in a product order is classical;
the displayed dyadic bound makes this search explicit.

For the present four coefficients, d=1, B=9 and G=39. Every minimal tuple
is therefore inside [0,39]^4. The computed frontier has 61 members and its
largest actual coordinate is 16.

## Exact enumeration and completeness

For the first three guards, enumerate their whole allowed range. Their
individual lower bounds follow from `a_i 2^-g_i<1`. If their sum is less
than one, compute the least possible fourth guard by an exact rational
comparison. Keep a tuple only if it is feasible and reducing any positive
coordinate by one makes S at least one.

These immediate-neighbor tests are sufficient for componentwise minimality.
If any smaller tuple were feasible, at least one immediate decrease from the
candidate would also be feasible, by monotonicity. Conversely every minimal
tuple must use the least possible fourth coordinate. The finite bound proves
that this algorithm misses none.

A second implementation uses integer contributions on one common binary
grid, enumerates the other three coordinates and eliminates the scalar
coordinate instead. It gives exactly the same 61 tuples. All 244 immediate
decreases fail. Each retained tuple is checked against all 34 source rows.
Eighty-four smaller dyadic domains are also enumerated through two exponents
beyond their proved bound, covering 109,525 tuples.

Any strictly increasing componentwise cost attains its minimum on this
frontier. Starting from any feasible nonminimal tuple, repeatedly decrease
a feasible coordinate. This process stops at a frontier point with smaller
cost. In particular, the certificate supports every positive linear tariff,
not just the example below. It does not prove optimality for error allocations
that are feasible in the actual caller but fail this sufficient envelope.

## Count the declared error-output digit volume

Let N be the complex coordinate count of one field. Count one guard digit
for each rounded complex output coordinate at an error site. A constant
factor of two for real and imaginary components can be applied throughout.
This tariff counts a logical precision-output volume, not physical time or
all data movement. Range, routing, conversions, cleanup and exact permutation
work need their own bill.

The literal caller has 277 ADDs, 80 SCALEs, 20 normalizers, 18 LOCALs,
17 QUERYs, 14 two-output IDLEs and two one-output idles. Each compatible
normalizer has four half-field operations. Thus the four field-equivalent
weights are

`w=(277+80+2*20, 2*18, 17, 2*14+2)=(397,36,17,30)`.

The literal primitive error-site counts are instead `(437,36,17,30)`, because
each normalizer has four sites. Both counts are recorded. There are also
126 exact SWAPs and 16 exact Q_POWER instructions; they have no defect site
in this contract. They are not declared free physical operations.

Price a non-scalar output digit by tau>0 times an ordinary output digit.
After division by the common N, the guard part of the tariff is

`V_tau(g)=397 g_scalar+tau*(36 g_local+17 g_query+30 g_idle)`.

The p-digit base is independent of g and cancels between policies under
this tariff. This accounting does not show that a physical backend can
supply arbitrary class tolerances or that its real cost is linear in g.

## All tariff regimes

Exact rational intersections of the 61 cost lines give:

| Open interval for tau | Unique optimal guards (scalar,LOCAL,QUERY,idle) |
| --- | --- |
| 0 < tau < 397/130 | (9,8,9,9) |
| 397/130 < tau < 397/36 | (10,7,7,7) |
| 397/36 < tau < 794/17 | (11,6,7,7) |
| 794/17 < tau | (13,6,6,7) |

At each boundary the two adjacent policies tie, and no other policy ties.
Between all pairwise line intersections, the ordering of the lines is fixed.
Testing one rational point in each such interval and each boundary therefore
proves the full positive-tau diagram. The separate integer frontier is used
for the independent winner checks.

For tau=1, the minimum is 4284 instead of uniform nine's 4320. At tau=10,
it is 9780 instead of 11043. At tau=100, it is 57961 instead of 78273.
The high-price policy has envelope `16155/16384<1`. The least native slope
is 528 instead of uniform nine's 747. Its limiting model reduction is
`(747-528)/747=73/249`. These are exact model comparisons, not measured
speedups, memory savings or kappa improvements.

For comparison, the tempting tuple (9,8,8,9) fails the sufficient envelope.
An arbitrary maximum guard of15 would miss real frontier points. The full
certificate avoids both shortcuts.

## Intermediate range and limits

For any retained tuple, the final envelope is less than 2^-p. Apply the
source unitary-endpoint/prefix argument to any truncated defect history.
Every caller boundary has norm at most `18 M+18*2^-p`. For the compatible
four-operation normalizer, a conservative internal bound is
`36 M+36*2^-p+8*2^(-p-g_scalar)`. For arbitrary Q with only a grouped
completed-defect premise, no internal normalizer bound is supplied.
Native LOCAL, QUERY and IDLE interiors still need their own range proof.

The package regenerates the exact source envelope and authenticates seven
retained files. It does not independently re-audit the source polynomial
operator proof; PR6510 retains that work. Seven invalid-domain checks and
seven source-byte corruptions fail. Exact tariff samples, threshold ties,
128 additional positive tariff vectors and all source rows pass.

No actual rounding backend, coordinate-to-field error conversion, sampler,
relative-error premise, data-grid conversion, native/tape/erasure bill or
complete compiler/outer admission is delivered. All five framework assumptions
remain. The signed recursive invoice and selected frontier stay unchanged.
