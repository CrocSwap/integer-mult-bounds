# Source-restoring echoes in five rows

## Entry and exit contracts

Let V be an abelian group and A_0,...,A_(n-1) exact additive endomorphisms.
An atomic leaf on distinct source s and target t performs

    row[t] += q A_i(row[s]),  q in {+1,-1},

preserving its immediate source and all other data rows and restoring its
separately priced private work. Descriptors are immutable; data rows do not
alias. Exact additivity and independence from incoming scratch are required.
No observer may read temporarily borrowed rows before the enclosing call
returns. There are no unhandled exceptions or concurrent mutations midway
through a call.

A complete M invocation promises the product shear for
`A_(last)...A_(first)` and restoration of all other rows. It promises nothing
about those rows at internal prefixes. The external source is therefore
allowed to be an internal connector. Its final value, and its exact residue
bit pattern in the finite backend, are unchanged.

All five data rows are available. Excluding s,t leaves three connectors, so
every node of arity k=2,3,4 has enough distinct chain ports. Descendants receive
the same pool. This holds at every depth. No data-row initialization, copy,
clear or allocation-time conversion is used. A negative invocation reverses
all leaf records and changes every sign.

For comparison, R protects physical row zero at every prefix and starts with
source zero. Its pool contains the output and three helpers. A node whose
source is zero can use three connectors (k<=4). A node with both immediate
ports in that mutable pool has only two other mutable rows (k<=3): type T.
Only the first child of an R node retains source zero; every other child is T.
Direction reversal does not swap ports. This classification is exact for
these templates, even with arbitrary legal connector assignments. It does
not bound other identities or overlapping/aliased chains.

## All-tree restoration

This uses the credited PR673/758/822/1057/1164 echo. Let an internal node's
completed child maps be B_0,...,B_(k-1), with chain ports
`z_0=s, z_1,...,z_(k-1), z_k=t`. Write U_i for
`z_(i+1) += B_i z_i`. By induction, U_i is the exact boundary map of its
recursive word for every incoming dirty state, restoring every other row.
Thus a child can be replaced by U_i at completed-child boundaries even when
its descendants borrow another chain port.

In left-to-right execution order, put

    C = U_0 ... U_(k-2),    D = U_1 ... U_(k-2).
    E = C; U_(k-1); C^-1; D; U_(k-1)^-1; D^-1.

After C, the last connector equals its initial value plus

    sum_(j=0,...,k-2) (B_(k-2)...B_j) z_j^initial.

After C^-1 and D, it has the same value without the final source term.
The two signed U_(k-1) calls therefore add precisely
`B_(k-1)...B_0 z_0` to the target. The inverse ladders restore all connectors.
No factors commute past one another; additivity gives the cancellation.
Other rows restore at each completed child boundary by induction. This proves
M, R and T for every finite tree, arbitrary dirty rows and both signs.

The change from the predecessor proof is M's admissible port set. Its source-
restoring contract is closed under this induction. The externally protected
source contract is not: the certificate contains source writes and exhibits
a nontrivial source prefix. A protective copy would require an extra row and
paid conversion/restoration, losing the same-cap statement.

## Exact restricted recurrence

The first/last children occur twice; every middle child occurs four times.
For complete, sign-symmetric, port-independent prices,

    W(leaf i) = c_i,
    W(node) = 2W(first) + 4 sum W(middle) + 2W(last) + G(node).

G pays internal control/instruction/routing work. A flat unrolled program
instead pays construction and per-record dispatch, without an additional
runtime recursive interpreter. For port-dependent costs, sum the literal
(s,t,factor,sign) records including every inverse. The following optima count
unit-price leaf occurrences; other costs are invoiced separately below.

Let T(1)=R(1)=M(1)=1 and w=(2,4,...,4,2). For positive contiguous parts
`n_0+...+n_(k-1)=n`,

    T(n) = min_(k=2,3) sum_i w_i T(n_i),
    R(n) = min_(k=2,3,4) [2 R(n_0) + sum_(i>0) w_i T(n_i)],
    M(n) = min_(k=2,3,4) sum_i w_i M(n_i).

Every permitted root has one listed partition and the stated child types.
The restoration induction admits every joining of minimizing children.
Induction on n proves both lower bounds and attainment in this class. The
deterministic allocator realizes each type in five rows. The argument does
not optimize arbitrary programs, other echoes, larger arities, early matrix
product evaluation or uncharged role/frame changes.

The primary implementation prices compositions. A separate min-plus path
algorithm selects lengths as transitions across k layers and agrees on every
T/R/M value through 56. Independent exhaustive trees check the small domain.

    (T,R,M)(51) = (1328,1040,928),
    (T,R,M)(56) = (1568,1248,1088).

Frozen PR1057 reproduces the complete T table and tie-broken trees. M(56)
corroborates PR1164's four-way count while requiring three extra dirty rows
instead of four. R, rather than T, is the stronger comparison for the claim.

This recurrence concerns supplied factor count, not integer multiplication's
input size. The inherited direct all-role adapter still fails. A root of k
leaves has N=4k-4. Replacing any leaf by a subtree of s>=2 leaves, with parent
occurrence weight at least two, raises work by at least
`2((4s-4)-1) >= 4(s-1)`. Induction gives N>=4n-4 for every nontrivial tree.
Thus `3N/(2n^(1-b)) >= 3` at b=0 for n>=2, and rises for b>0. M(51) gives
the optimistic bill 464/17. This does not establish an improved kappa.

## Exact modular realization

Use PR1159's contract: V=(Z/(2^w)Z)^L, with integer L-by-L matrices reduced
modulo 2^w. Addition, subtraction and multiplication commute with reduction.
Leaves are exact additive maps, so all five data rows have the promised
endpoint for arbitrary residue patterns. No field assumption, matrix inverse
or division by two is used.

Only the external integer source and initial output have infinity norm <=D=7.
Set K_i=max_r sum_j |A_i[r,j]| and R=D(1+product_i K_i). Choosing
`w=bit_length(max(D,R))+1` gives 2^(w-1)>max(D,R). The final integer output
lies strictly inside the signed decoding interval and is uniquely recovered.
Helpers need no small-norm hypothesis. This guard uses individual norms;
complete product matrices are computed only for verification, not assumed
available without preparation cost.

The main factors have K_i=2, giving w=55 at n=51 and w=60 at n=56. All
intermediate data are residues even if the unbounded integer lift is much
larger. There is no rounded-child accuracy or nonlinear restoration claim.

## Complete cost and storage

The backend has five L-cell data rows and a read-only nL^2-cell coefficient
table, with w-bit cells. Four clean owned scalar registers are admitted and
cleared at startup: accumulator (w+1 unsigned bits), value (w+2 signed bits),
coefficient (w bits), product (2w bits), totalling 5w+3 bits. Clearing and
reduction are paid ordinary operations, not free or logically reversible
erasures. Arbitrary dirty restoration concerns the five data rows.

For each target coordinate, clear the accumulator. For each source coordinate,
read source/coefficient, multiply, reduce, add to the accumulator and reduce.
Read the old target, add/subtract the accumulator, reduce and write back.
After every leaf clear all four private registers and return the data head
to zero. The product is <2^(2w), the accumulator sum <=2^(w+1)-2, and the
signed target update lies between -(2^w-1) and 2^(w+1)-2. The specified
private capacities therefore suffice independently of recursion depth.

Per leaf the exact command counts are

    L^2 multiplies; L^2+L adds/subtracts; 2L^2+L reductions;
    L+4 scalar clears; 2L^2+L reads; L writes.

Counted scalar/access commands are `N(6L^2+5L+4)+4`, including startup. Let
MUL(w), ADD_u(w+1), ADD_s(w+2), LOW(b,w) and Z(b) include private-register
access/routing implementation costs. Arithmetic and private work cost exactly

    N L^2 [MUL(w)+ADD_u(w+1)+LOW(2w,w)+LOW(w+1,w)]
    + N L [ADD_s(w+2)+LOW(w+2,w)]
    + [N(L+1)+1] Z(w+1)
    + (N+1)[Z(w+2)+Z(w)+Z(2w)].

Data/coefficient addresses are `sL+j`, `tL+i` and
`5L+(factor*L+i)L+j`. Let E=N(2L^2+2L), d be the literal intercell travel
including every return to zero, and a=ceil(log2(5L+nL^2)). Full-cell scans
return to each cell's left edge. The independently recounted invoice is

    wE data/coefficient bit actions;
    wd+2(w-1)E data-head moves;
    E Address(a) address/control cost.

Private arithmetic travel is included in MUL/ADD/LOW/Z. The model has
separately priced instruction and private/control storage; it is not a
compiled fixed-tape implementation.

An unrolled record has `b=max(1,ceil(log2 n))+7` bits: factor, two three-bit
ports, sign. Pay Nb storage/read bits, 2Nb instruction-head moves and
N Dispatcher(b,a,log L), plus backend control workspace. No recursive child
or inverse is omitted beyond these N leaves. Verifier memory is separate
from this execution data-space claim.

Add in full:

    input/coefficient admission and original descriptor storage;
    norm/width computation, common planning, tree/word construction;
    nL^2+2L input/coefficient reductions and their reads/writes;
    nL^2w coefficient bits and any retained original input/coefficient storage;
    L final output decoding/read/write operations;
    host-specific frame conversions, additional source access, allocation
      and routing not already in the priced leaves.

Planning examines O(n^4) candidates using actual integer cost bit lengths;
table/split storage is O(n), selected-tree storage O(n), and program storage
O(Nb). One common planner computing all three tables gives both comparisons
the same paid planning charge. Program construction/writes remain paid in
proportion to emitted records under the chosen implementation. No cached
plan or preexisting program is assumed. Coefficient preparation, decoding and
common storage use identical inputs/widths in each comparison.

Direct fixed row addresses require no data frame conversion or full-row copy
in this backend. A supplier must supply and pay its own adapters, rather than
inherit that zero. The certificate lowers N, command counts, E, d and program
bits at identical n,L,w and five-row capacity. This is a favorable fully
exposed finite invoice, not a runtime inequality for every compiler or
planning implementation. Source ownership is a material admission condition.
