# Bit role sharing: a budget gate before supplier construction

This continues PR673 at `bfff94e78f0e75ebd2593e3cc7710ae5290e8be3`.
The user selected a bit-first sharing investigation. All comparisons below
use PR589's actual punctured/tuned local word and its frozen nine-stage
hosting invoice. No new supplier, all-size theorem or kappa is asserted.

## 1. The complete retained invoice

The ambient rank is m=64, the live volume denominator is W=28416, and there
are 9 stages times 32 replicas, or 288 local invocations. Replaying every
Boolean column and every nested frame of the actual local word gives

    Hlocal = {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}.

Its rank mass 5129 is the sum of source growth 777, target growth 777,
helper growth 3512, and nine rank-7 COPY charges 63. The first three
quantities equal 7v, 7v and 8R for v=111 and R=439. Cleanup is executed,
not discarded; all 661 independent source/target/dirty columns have the
required restored endpoint. The COPY response matrix has Boolean rank 9,
and its nine input totals are independent in the full dirty-input domain.
Thus a linear response encoder of these same totals needs at least nine
independent encoded scalars. This does not restrict a different producer.

The unchanged hosting remainder is

    Hidle = {2:13920, 4:14208, 6:14208, 7:21312, 42:288}.

The full invoice is 288 Hlocal + Hidle. Its rank mass is 1808352, its
deficit from Wm is 10272, and the local part's rank mass is 1477152.
These figures are recomputed and compared with the pinned global receipt.
This is an independent local replay and invoice check, not a fresh physical
hosting or all-size audit of PR589.

For saving c, the charged moment, including the retained bad-class fallback,
is

    Phi(H,c) = sum_r H[r] r/(mW) (m/r)^c
               + 32m sum_r H[r]/(10^16 W) m^c.

Each fallback has at most 32m² width-1 children on a bad fraction below
10^-16. The moment at c=1/99 is approximately 1.027739494928555. The outer
assembly requires BOTH supplier savings strictly above kappa/(1-kappa),
so 1/99 is a necessary threshold for kappa=0.01. Even equality of a supplier
root to 1/99 would be insufficient. The complex endpoint is unchanged here.

The inherited live denominator is used exactly. The receipt separately
records physical storage 28425, including nine typed center slots whose
copy work is charged. Those slots do not become free arbitrary-data roles
for a new sharing scheme. A new private array requires an actual ownership,
hosting and endpoint contract; increasing W by a fictitious free role is
not permitted in any comparison below.

## 2. Pooling equal work across arbitrary roles

Suppose B independent roles need the same nonidentity address permutation P.
Batching their calls changes B dispatches of volume V/W into one dispatch
of volume BV/W. Since the retained child bound is linear in data volume,

    B C(V/W, re/m) = C(BV/W, re/m)

at the level of the charged leading coefficient. This also holds for the
fallback: each bad child acts on the whole batch. Remainders in a partial
batch must retain their own volume. Encoding, decoding, moving and restoring
data adds nonnegative work. Even granting all that work free leaves exactly
the original moment. For fixed B, linear XOR/routing passes may affect
constants but do not reduce the paid recursive coefficient. No fixed-tape
implementation of a new pooling adapter is needed to reject this budget.

Could an XOR encoding reduce the queried volume instead? In the following
explicit model it cannot. Permit arbitrary invertible row charts S tensor I
over F2, interleaved with calls applying the fixed P to one role. Any number
of arbitrary dirty private roles may be included and must be restored.
Require P on B active roles and identity on the private roles.

P fixes the nonzero constant-address vector. Restricted to this invariant
sector, every query is identity, so the product of all role charts must be
identity. Move these charts to the end by conjugation and cancel their
product. Each remaining query Q satisfies

    rank(Q-I) = rank(P-I).

Conjugation preserves this rank. The product inequality
rank(AB-I) <= rank(A-I)+rank(B-I) therefore bounds the final displacement
rank by q rank(P-I), where q is the number of one-role queries. The required
endpoint has displacement rank B rank(P-I), so q>=B. If a query applies P
to b roles at once, it contributes b rank(P-I), giving sum b>=B: the same
volume floor. B direct calls attain the query count while preserving dirt.

This is a fixed-P, address-independent invertible-XOR-chart result. It does
not cover address-dependent charts, a different native ADDRESS primitive,
changed endpoint obligations, or a circuit that jointly eliminates distinct
operator types. In particular it does not assert an unrestricted direct-sum
lower bound for algorithms. PR677 treats a different DATA-shear endpoint;
its two/four/one-query conclusions are not used here.

The finite oracle enumerates all 108 choices of GL(2,2) before/after charts
and zero or one query, rejecting each as an all-role implementation. Direct
programs with 1..8 active roles and 0..3 dirty private roles check 384 basis
columns. The arbitrary-size result rests on the rank argument, not those
finite examples.

## 3. Perfect sharing confined to local stage widths still misses 0.01

For 0<c<1, the cost per rank unit at child width r is (m/r)^c/(mW), decreasing
with r. With a preserved rank mass S and a maximum child rank J, the most
optimistic fractional histogram places S/J calls at rank J. It also
minimizes the fallback call count. This is a relaxation: fractions of calls,
merging different roles without paying added volume, and eliminating scalar
work are all granted. Failure of this stronger budget rejects any actual
rank-mass-preserving profile in this class under the retained charge.

Keep Hidle exactly, and set J=8 for all local work. This grants the full
eight-dimensional local frame even though no current local child exceeds 7.
The moment at 1/99 is about 1.016042715946274. Its strict root bracket gives
a bit-only outer ceiling below 0.002644610326897. This does not claim that
the hypothetical consolidation can be implemented.

Now erase ALL nine COPY charges in every invocation as a further gift:
remove 288*63=18144 rank units, while keeping W and Hidle. Consolidate every
remaining local rank unit at rank 8 again. The target moment is still about
1.005854169251071; the bit-only outer ceiling is below 0.007315906873875.
Thus even completely free retained-total copying plus perfect width-eight
sharing does not reach 0.01 with these boundary costs. Real elimination of
COPY obligations is not established or inferred from this relaxation.

This conclusion is about the retained rank mass/boundaries and the stated
rank cap. Sharing that changes the total rank mass or boundary obligations
requires a different invoice and is not excluded.

An exact alternative target quantifies that escape. With ideal rank-8
consolidation and Hidle/W fixed, removing 99 net rank units per local
invocation gives moment 1.0000321425680974 and fails. Removing 100 gives
0.9998704196046815 and passes as an arithmetic relaxation. This is 28800
net units globally, compared with only 18144 from erasing every COPY charge.
The requirement is a reduction of the complete paid invoice AFTER hosting.
Reducing helper count alone need not deliver it: the retained rank-mass
identity fixes the deficit independently of R, and unoccupied owner
directions return as paid idle work. Scalar shortening alone is insufficient.

## 4. A concrete cross-stage target and its very small repair allowance

Retain Hidle and the original local rank mass. Evaluate the fractional lower
bound for every cap J=1..63 at c=1/99. Cap 55 still fails; cap 56 is the first
that passes. If ALL rank mass, including Hidle, may be repacked freely, cap
36 still fails and cap 37 is the first passing relaxation. These thresholds
are necessary conditions for the respective preserved-mass classes, not
existence claims for operators or charts.

There is a useful but restricted stage-fusion ansatz. For a fixed port q,
the positive-stage active spaces are the common line P_q plus disjoint
seven-dimensional exterior blocks. Stage zero is the original eight-space.
A union of s such active spaces has dimension at most 1+7s. Under this
fixed-port restriction, seven stages give cap 50 and still fail with the
fixed remainder; at least eight are needed. If the whole remainder is also
redesigned, five give cap 36 and at least six are necessary.

This is NOT an unrestricted stage-count lower bound for role sharing. The
port lines collectively span eight dimensions: seven positive stages with
different ports can span 8+7*7=57, while the fixed-port calculation gives
only 50. The checker explicitly records this countercontrol. Changed helper
hosting/charts also need their own support calculation. The rank-cap
threshold 56 is unaffected, but it cannot be converted to a universal
eight-stage requirement. No span calculation supplies an admissible operator.

For an explicit arithmetic target, pack the local mass into as many rank-J
calls as possible plus one remainder call, and retain Hidle. This produces
integer hypothetical invoices with the same total rank mass and W. All
fallback children are charged. The following are whole-program allowances,
across all 288 local invocations, at the threshold c=1/99:

| J | Target moment | Additional rank-1 child allowance | Local mass needing fusion from ideal rank-8 calls |
|---|---:|---:|---:|
| 56 | 0.9998980605101204 | 177 | more than 99.3681% |
| 57 | 0.9997526042747312 | 431 | more than 98.4812% |
| 63 | 0.9989309632236760 | 1864 | more than 93.7523% |

The allowances include the additional fallback charge and have exact integer
fences: that many extra rank-1 children still have a strict passing interval,
and one more fails. Higher-rank repair children generally consume more of the
budget. Extra volume, new private rows, changed existing boundaries or a
different fallback rule require repricing the entire invoice. Routing and
scalar constants are not silently converted into negative recursive work.

The coverage column linearly interpolates between the rank-8 relaxation and
the fully fused fractional cap-J relaxation, including their fallback counts.
It is an optimistic minimum on the *rank mass* needing the larger children,
not a percentage of original instructions. The integer invoice/allowance and
fractional coverage screen are distinct diagnostics.

This makes the next possible construction specific: a joint high-rank
operator at fixed live volume, accomplishing almost all the retained local
work with rank-57 children, while leaving fewer than 432 new rank-1 repair
calls in the full program. The fixed-port version would span at least eight
stages; cross-port fusion is a different, potentially wider class. One extra
rank-1 repair per local invocation (288
total) fits this generous invoice; two per invocation (576) do not. No such
operator, legal chronological frame path, common-label realization, or
hosting plan is supplied. Consequently we stop before implementing a supplier.
Passing this arithmetic target is a gate for further research, not admission.

## 5. Independent arithmetic and controls

The checker reads and hashes the pinned inputs, reconstructs the local word
profile, and adds the literal frozen remainder from fastc.py. Its interval
engine is independent of the inherited Mercator implementation: after binary
argument reduction it uses 96 positive terms of

    log x = 2 sum_(j>=0) z^(2j+1)/(2j+1), z=(x-1)/(x+1),

and a geometric upper bound on the remaining tail. A degree-28 exponential
polynomial and a geometric remainder bound enclose exp on [0,0.1). Outward
224-bit dyadic rounding preserves inclusion. The original bit root is checked
at both adjacent 10^-24 endpoints, providing an external arithmetic control.

Meaningful false-gain controls omit the pool volume, omit Hidle, check only
the zero-saving deficit, or allow a rank-m recursive call. All are rejected
as admissions. The full harness supports isolated optimized Python; checks
do not depend on assertions. Exact endpoints are in evidence/PRICE.json.

Credit: PR589 and eumemic's punctured/tuned word; DreamingOfClouds' geometry
and nine-stage chain; chafreaky's whole-residual hosting; their preserved
OpenAI/Claude and construction notices. PR679 (Greer Guthrie) independently
emphasizes the volume charge for a different complex selector construction.
PR677 (commdata2338) audits fixed-native-query DATA shear contracts. Elementary
matrix-rank and concave-moment arguments carry no priority claim. Prepared
for @androolloyd with substantial OpenAI Codex assistance. Apache-2.0.
