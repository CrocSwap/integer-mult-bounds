# Exact planning under a borrowed-array cap

This is a written proof about a restricted recursive interface, accompanied by
finite checks. It is not a proof-assistant formalization. The multiway echo and
its nonlinear restoration argument are credited to androolloyd's PR673; PR689
by Dillon Amburgey supplies the balanced ternary baseline. Our addition is
optimization over **all contiguous partitions and all arities** under a fixed
peak-space cap, including nonuniform positive integer leaf prices.

Concurrent PR730 (Sagar Thakrar) published the analogous interval optimization
for binary/ternary trees during this work; PR744 (Ali Romman) independently
audits strict ternary trees. We claim no priority for their shared optimization
or proof principles. Our k>=2 recurrence admits higher arities, and the pinned
comparison in CONCURRENT.json shows the strict gain from doing so.

## 1. Contract and admitted program class

There are ordered factors F_0,...,F_(n-1), a source x, a target y and S arbitrary
borrowed length-L arrays. All arrays are distinct. A positive leaf adds a
deterministic function of its source to its target, preserves the source, and
restores any scalar/data work it borrows. The increment is independent of the
target. A negative leaf subtracts exactly that same value. Factor descriptors,
phase data and every other read-only dependency are fixed and do not alias
mutable arrays. Stateful callbacks and overlapping views are outside this API.

An internal node has k>=2 **nonempty consecutive** children. It reserves k-1
distinct arrays for its complete duration. Its children run sequentially and
share a deeper pool that excludes every reserved array and every ancestor
source/target. A leaf has no borrowed-array requirement. Thus these are ordered
rooted trees without unary nodes. The optimization does not cover arbitrary
pebbling, simultaneous children, borrowing idle ancestor arrays, alternative
echo words, commuting-factor reordering, or deletion of identity factors.

For child maps A_1,...,A_k, let C be the ascending ladder

```
z_1 += A_1(x); z_2 += A_2(z_1); ...; z_(k-1) += A_(k-1)(z_(k-2)).
```

Let D be that ladder with its first instruction omitted. PR673's word is

```
C; y += A_k(z_(k-1)); C^-1;
D; y -= A_k(z_(k-1)); D^-1.
```

The inverses reverse chronological order AND signs. A child inverse encounters
the same source and deeper dirt as its forward mate: later ladder changes have
already been undone, and target updates touch only y. Consequently source and
all dirt are restored, even for nonlinear deterministic leaves. The result is
an additive, target-independent increment. It can depend on dirt when leaves
are nonlinear. For ideal linear leaves the difference between the C and D
states propagates as A_j...A_1 x, giving exactly A_k...A_1 x. Commutativity is
not assumed. This proves the recursive contract by induction.

The first and last children occur twice; every interior child occurs four
times. There is no free cleanup pass or clean length-L copy.

## 2. Bellman recurrence and its scope of optimality

Let c_i be a positive integer price for one complete signed invocation of
factor i, equal for the two signs. Prices are fixed at the chosen L and working
precision, and include whatever operation is being optimized. For instance,
c_i=1 counts completed leaves; c_i=(5L-2) or (6L-2) counts the actual PR628
outer/inner phase reads. Phase reads alone are not total runtime.

Define D(i,j,s) as the minimum price in the stated tree class for factors
[i,j) using at most s borrowed arrays. A singleton costs c_i for every s>=0.
A nonsingleton with s=0 is infeasible. For all other states:

```
D(i,j,s) = min over 2 <= k <= min(j-i,s+1), i=t_0<...<t_k=j of
           2 D(t_0,t_1,s-k+1)
         + 4 sum_(a=1,...,k-2) D(t_a,t_(a+1),s-k+1)
         + 2 D(t_(k-1),t_k,s-k+1).
```

An infeasible child makes its candidate infeasible. Ties are broken by the
smaller total number of completed leaf calls, then deterministic enumeration
order. This secondary objective has the same positive multipliers, so the
Bellman argument also applies to lexicographic (price, calls) pairs.

**Completeness.** Every admitted nonsingleton tree has exactly one root arity
and set of contiguous cuts appearing in this minimum. Reserving k-1 arrays
leaves each child at most s-k+1. Induction bounds every child price below by its
corresponding D. Conversely the minimizing children are composable using the
same deeper pool, because every invocation restores it, so the minimum is
attained. This proves optimality in this class, not among all reversible
implementations of the operator.

`planner.py` evaluates the root partitions using a prefix dynamic program;
`verify.py::cuts_oracle` separately enumerates every subset of root cuts and
uses no prefix DP, capacity pruning or producer witness. Its primary-domain
agreement checks two implementations of the recurrence. A second oracle
enumerates every whole tree through eight leaves, without either optimizer.
Those finite checks support the implementation; the induction supplies the
general argument.

**Safe capacity pruning.** A tree using s arrays has at most 2^s leaves.
For a k-child root, induction bounds its leaves by k*2^(s-k+1)<=2^s, because
k<=2^(k-1). Conversely a balanced binary tree fits n leaves in ceil(log2 n)
arrays. Thus the planner's rejected states j-i>2^s are exactly infeasible.
Clamping s to n-1 also loses no tree: along any root-to-leaf path, each of the
sum(k-1) side subtrees contains a distinct leaf other than the final leaf.

## 3. Literal primary result

Assignment seed 58 selects radix 16 from the predeclared eight-radix list;
there are 15 factors, kept in their original order. At the five-array budget
used by PR689, the uniform-price optimum is **152** complete leaf calls, versus
160 for PR689's optimized balanced ternary word and 208 for PR673's original
ternary partition. The optimum tree, with zero-based leaves, is

```
(((0,1),2,(3,4)), (5,6,7,8), ((9,10,11),(12,13,14))).
```

Its root child counts are 20, 12, 32 and child spaces are 3, 3, 3. Hence
N=2*20+4*12+2*32=152 and S=2+3=5. All restoration is already in these counts.
The middle child has arity four, outside PR730's class. Its pinned optimum is
160 here, so the improvement is not merely a different optimum tree within
that concurrently published class.
Leaf multiplicities are

```
8,8,8,8,8,8,16,16,8,8,16,8,8,16,8.
```

At four arrays the class optimum is 224. At fourteen arrays the flat word
reaches 56. These comparisons are a space/work tradeoff, not a free removal
of scratch. `EXPECTED.json` retains every optimum for caps 4 through 14, each
checked by the all-cuts oracle, and the phase-read-weighted radix-16 instance.

At cycle length L=5 the pinned radix-16 factors have phase-read prices
`23,28,28,28,23,23,23,23,23,23,23,23,23,28,23`. Optimizing these prices at
five arrays retains 152 calls but selects a different last root child:
`((9,10),(11,12),(13,14))`. Its complete phase bill is **3656**, compared with
3696 for the uniform-price tie choice and 3840 for PR689's balanced word.
This is the exact phase-read minimum in the stated tree class at this fixed
length. The optimum is not asserted to minimize total bit work.

## 4. Complete execution, preparation and precision bill

For a literal tree t, let v_i(t) be its occurrence vector. At an internal node
the vectors of the two endpoint children are doubled and those of interior
children quadrupled. Then

```
N(t) = sum_i v_i(t),
S(t) = (k-1) + max_child S(child),
T_t(L,w) = 2 T_first(L,w) + 4 sum_interior T_child(L,w)
           + 2 T_last(L,w) + control_t.
```

The complete external charge is

```
P_plan(n,S,c) + P_factor_phase(n,L,w) + P_admit(n,S,L)
  + sum_i v_i(t) * [A_i(L,w) + Q_i(L,w) + R_i(L,w)]
  + P_schedule(t) + P_boundary(t,L,w).
```

Here A_i pays the leaf's arithmetic, coefficient work, validation, normalization
and exact source undo; Q_i pays all source/phase/table access; R_i pays each
leaf's required routing. P_factor_phase pays certified coefficient and phase
preparation, with original-input scaling. P_admit includes array-length,
alias, descriptor and unit-phase admission. No fixed-tape route is free.
P_boundary is zero only at this array-level interface, where every factor
already shares a layout; a supplier integration must supply and charge its
layout, frame, hosting and final-boundary work. There is no newly inserted
copy, erase, transform, or clean length-L workspace in this dispatcher.

In the pinned PR628 leaf, each invocation executes three L-loop traversals,
plus stability/grid scans. All are retained. Its complete phase accesses are
(5L-2) for an outer factor and (6L-2) for an inner factor, including inverse
source lifts. Instrumented real-leaf execution checks these formulas separately
from the planner's weights. Mutable storage is source, target and S(t) borrowed
arrays; a test-only spectator is never touched. Scalar arithmetic workspace and
the immutable O(n) factor/tree descriptors are additional, not clean data arrays.

Planning is also paid. This implementation is an exact indexed-RAM reference,
not a fast uniform tape compiler. With the clamped S<=n-1 and B-bit input
prices, it has O(S*n^2) interval states and O(S^3*n^4) candidate evaluations.
Prices have O(B+S+log n) bits. Including tuple bookkeeping gives the deliberately
loose O(S^4*n^4*(B+S+log n)) bit-work bound, plus input/output, in an ordinary
RAM implementation. Retained trees and temporary prefix tables can safely be
bounded by O(S^2*n^3) references. The emitted execution word is streamed, with
O(n) stored tree nodes and O(S) active child descriptors along a path. For this
fixed 15-factor contribution the supplied literal tree needs no runtime search;
for growing n the planning term must not be suppressed. We claim no new
asymptotic exponent or measured wall-time acceleration.

For rounded execution inherit PR628/PR673's hypotheses: ideal factor norms
at most K=r/beta; deterministic completed-leaf error at most a(B+1)u on source
norm B; a=13(r+1)/beta^3; u=2^-w; au<=1 and u<=beta^2/2. Set G=2+K and let D
bound all initial arrays, including dirt. After j completed leaves,

```
M_j+1 <= G^j(D+1),
E_(j+1) <= (1+K)E_j + a*u*G^j(D+1),
E_N <= N*a*(D+1)*u*G^(N-1).
```

These inequalities concern the complete word, including every inverse leaf.
Actual source and scratch restoration is exact by Section 1; the target has
the bounded rounding error. Sufficient working precision is

```
w >= p+1+ceil(log2(N*a*(D+1)))+(N-1)*ceil(log2 G),
```

together with the two leaf conditions. Factor/phase preparation must separately
consume at most the other half of the 2^-p error budget, scaled by the original
source norm. The retained finite root fixtures are not asserted to meet an
arbitrary stronger preparation target. Our tests check represented-factor
execution against the complete polynomial and separately run their original
root certificate. They do not reprove the analytic preparation algorithm.
The new dispatcher changes neither leaf semantics nor the inherited estimates.

## 5. Why the local saving does not imply a new kappa

PR673's later [all-role adapter analysis](vendor/pr673/INTEGRATION-PROOF.md)
already prices the missing outputs on borrowed roles. Its optimistic moment
is 3*N(n)/(2*n^(1-b)), even granting one recursive child per additive leaf and
zero routing, phase, preparation and precision work. For our primary count at
n=15 and b=0 it is **76/5**, still far above 1. This is a hypothetical price
for 15 equal-width factor groups in that adapter, not an assertion that the
radix-16 cyclic factors implement its Clifford endpoint.

The inherited general tree bound N(n)>=4n-4 survives arbitrary partitions and
arities: first inductively N(n)>=2n-1; then endpoint children contribute at
least 4n_i-2 each, and interior children at least 4n_i. Summation gives 4n-4.
Thus even the flat optimum has moment at least 6-6/n>=3 for n>=2 and b>=0.
We do not reopen that closed direct-adapter search. The useful result here is
a smaller **local restored-array bill**, with its exact space/weight contract.

The selected construction remains #626/#543 at
51110230636731/31250000000000000. The complex supplier still binds there. No
selected child histogram, owner schedule, supplier exponent or outer inequality
is changed. All-size compilation, common-label/mutable-basis realization,
physical hosting, fixed-tape implementation, precision/exact recovery and
analytic transfer remain inherited or unresolved.
