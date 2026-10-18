# Borrowing restored sibling connectors

## Statement and exact scope

PR673's dirty echo composes ordered factor shears. PR730 minimizes their
weighted leaf bill over ordered binary/ternary trees, with every node's
connectors reserved throughout every descendant. Here an invocation passes
all its borrowed arrays except the child's immediate source/target to that
child. Other sibling connectors are eligible because the child restores them.
Parent source and target never enter the pool. This changes the allocator;
it does not change the echo identity or the permitted factor order.

For any finite ordered binary/ternary tree, the resulting word implements
`y += A_(n-1) ... A_0 x` for arbitrary composable linear maps and arbitrary
initial borrowed data. Under the nonlinear leaf contract below, it still
restores source and every borrowed array exactly and adds an increment
independent of initial target. The weighted recurrence below is the exact
minimum over this particular allocator and tree class. No optimality over
all reversible programs, all arities, or arbitrary ancestor-port borrowing
is asserted. There is no new multiplication exponent.

## Contracts

Source, target and every borrowed length-L array are distinct, nonoverlapping
storage. Fixed descriptors, phases and coefficients are read-only and do not
alias any mutable array. A leaf for factor i is the ideal additive shear
`target += A_i source`. It can have private, separately charged workspace.

For rounded/nonlinear restoration the contract is weaker: a positive leaf
adds a deterministic represented increment `f_i(source)` independent of its
target, restores its source and private work, and a negative leaf subtracts
exactly that same increment. Represented additions/subtractions are exact
(e.g. an integer grid with enough headroom), with no overflow. Ordinary
floating-point `target += value` is not automatically this interface. Hidden
mutable state, overlapping views and exceptions midway through a leaf are
outside the result. No rollback-on-error property is asserted.

Recursively the increment may depend on the child's incoming dirty pool. It
must remain independent of the child's target, and all other arrays must be
restored on return. It is incorrect to substitute the nonlinear composition
of the leaf functions for the final increment.

## Why sibling borrowing restores correctly

At a node with k children, select k-1 distinct pool arrays z_1,...,z_(k-1).
The child ports form the chain `(x,z_1), (z_1,z_2), ..., (z_(k-1),y)`.
The pool passed to a child is the parent's entire pool with that child's two
ports removed. Thus each child receives distinct storage excluding its ports,
and excludes both outer ports x,y except its designated port.

Induct on the tree. A completed child changes only its target, by an increment
independent of that target, while restoring its source and passed pool.
Temporarily using another connector is permitted; its entry value is restored
before the next child starts. Therefore child boundaries expose precisely
ordinary shears in the ideal linear case. PR673's ladder identity applies:

```
C = child_0; ...; child_(k-2)
D = child_1; ...; child_(k-2)
C; child_(k-1); inverse(C); D; inverse(child_(k-1)); inverse(D).
```

The two forward ladders differ by the propagated source contribution, so
linearity gives the ordered product. No commutativity of factors is used.

For nonlinear leaves, every ladder child is a reversible shear in its target
whose increment can depend on the *other* connectors. Reversing the ladder
restores those other connectors to their values at the matching forward
child. The intervening last-child update changes only y. Crucially, y is
excluded from every ladder child's pool, so it cannot change the increment
to be subtracted. This establishes exact reversal of C and D and restores
all connectors. Both last-child calls are target-independent by induction,
so their difference is independent of incoming y. This closes the induction.
The full negative word is the reverse order with every leaf sign negated.

A source or target of an ancestor is never donated merely because it is
momentarily unused. In particular, permitting y as ladder scratch invalidates
the argument. The executable negative control exercises this failure without aliased leaf
ports: on `((0,1),2,(3,4))` it changes input `[-7,-4,-1,2]` to
`[-7,55,-51,2]`, corrupting connector z_1 from -1 to -51. Its deterministic
nonlinear leaf is `(z mod 17)^2 + (i+1)(z mod 7) - 3`.

## Complete resource and price recurrence

Let S be borrowed-array count and W the charged leaf bill. A leaf i has
`S=0, W=c_i`, with a positive integer price c_i valid at the same precision
for both signs and all occurrences, source sizes and intermediate values.
All source accesses, the leaf's own restore, coefficient/phase reads and
private workspace actions must be included in c_i or separately charged.

For a binary node:

```
S = 1 + max(S_left, S_right)
W = 2 W_left + 2 W_right.
```

For a ternary node:

```
S = max(2, 1 + S_left, 2 + S_middle, 1 + S_right)
W = 2 W_left + 4 W_middle + 2 W_right.
```

Two connectors must exist at the ternary root. Each endpoint child occupies
one connector as a port and can borrow the other; the middle child occupies
both. These constraints are necessary for this allocator. They are sufficient
because a serial child restores its entire pool, which may then be reused.
PR730 instead charges `2 + max(S_left,S_middle,S_right)`.

All calls in both inverse ladders, both target updates and nested restores
are already counted. With c_i=1, W is the complete leaf count N. For example,
`((0,1),2,(3,4))` uses two borrowed arrays and 20 leaf calls; its two binary
endpoint children borrow each other's root connector. The reserved allocator
needs three arrays for that exact tree.

For contiguous interval [i,j) and cap b, let F(i,j,b) be the minimum W.
`F(i,i+1,b)=c_i` for b>=0; negative budgets are infeasible. Other cases are

```
min over i<m<j:
    2 F(i,m,b-1) + 2 F(m,j,b-1)

and, if b>=2, over i<m<l<j:
    2 F(i,m,b-1) + 4 F(m,l,b-2) + 2 F(l,j,b-1).
```

Every admitted root has exactly one listed split and those child capacities.
Induction on interval length gives the lower bound. Joining child minimizers
with the stated allocator attains each finite candidate. This proves the
minimum in this finite class for every positive integer price vector.

As an additional storage consequence, the maximum feasible leaf count obeys
`M_0=1, M_1=2, M_b=2 M_(b-1)+M_(b-2)` for b>=2. Binary roots allow at most
`2 M_(b-1)`; ternary roots attain the larger displayed count. Every smaller
positive count is attainable: prune a deepest pair/triple of leaf children
one leaf at a time (a pair becomes a leaf; a triple becomes a pair), then
relabel consecutively. These prunings never increase storage. Thus feasibility
is exactly n<=M_b. The first values are 1,2,5,12,29,70,169,408,985. This is a
storage theorem for this allocator, not a circuit-size lower bound.

## Planning, execution and precision are separately paid

For n factors and cap b the interval planner has O((b+1)n^2) states and
O((b+1)n^4) exact arithmetic/comparison operations. Integers have their actual
bit lengths; no constant-bit assumption is made. A selected tree has O(n)
descriptor records. Planning is charged once only when reuse of a plan is an
explicit application assumption.

The local complete bill is

```
planning + descriptor/coefficient/phase preparation
+ sum_i (leaf multiplicity_i * c_i at required common precision)
+ remaining source routing/frame work + schedule dispatch.
```

There is no clean length-L array, array copy, array initialization or extra
recursive operation hidden in pool reassignment. The mechanism uses physical
array references; an actual tape/frame implementation must price changes in
where a factor reads and writes. The Python emitter spends O(b N+n) record
operations and O(b^2+n) record storage, besides (b+2)L data words and private
leaf work. These conservative bounds include filtering/copying pool lists at
each recursive invocation; no O(N) wall-time claim is made. Mathematical
S is the minimum pool size for the tree. When a larger cap is supplied, the
API retains that supplied pool; callers can emit with the reported S.

All ancestor sources/targets remain excluded. The printed five-array witness
can be emitted with b=5. Its b=6 word is identical and never addresses the
unused sixth borrowed array. Dynamic physical layouts and shared phase
representations remain outside this implementation.

For the PR628-style rounded leaves, retain PR673's hypotheses, including
`u=2^-w`, initial joint norm <=D, `K=r/beta`,
`a=13(r+1)/beta^3`, `G=2+K`, `a*u<=1`, and `u<=beta^2/2`.
The ideal shear has norm <=1+K and each local error at norm <=B is bounded
by `a(B+1)u`. For the *actual expanded* N-leaf word the same induction gives

```
M_j + 1 <= G^j (D+1)
E_N <= N a (D+1) u G^(N-1).
```

The result does not depend on the scratch addresses: each ideal leaf is still
the same shear on two distinct roles. Thus sufficient execution precision is
`w >= p+1 + ceil(log2(N*a*(D+1))) + (N-1)*ceil(log2(G))`, plus the leaf
conditions. Preparation error keeps its separate inherited allowance. Prices
must be recomputed at that precision before claiming a bit-complexity gain.
This package checks exact nonlinear restoration, not the PR628 numerical leaf
or its analytic error estimates independently.

PR673's all-role integration obstruction also survives. The invocation
multiplicities and ordered tree shapes have not changed. For any such tree,
N>=4n-4 for n>=2, following the credited PR730 note. For completeness,
first induct to obtain N>=2n-1: every child is called at least twice, so an
internal k-child node has N>=4n-2k>=2n-1 since n>=k. At the root, each
endpoint contributes at least 4n_i-2, and a middle child contributes at
least 4n_i using N_i>=n_i. Summation gives 4n-4. Even granting free
wrappers/routing and one recursive child per leaf, the direct three-shear
all-role adapter has moment `3N/(2*n^(1-b)) >= 6-6/n >= 3` at b=0 and larger
for b>=0. Our 59-factor witness gives `3*1712/(2*59)=2568/59` at b=0, so it
cannot supply a positive saving through that adapter. We do not reopen that
negative result. Other integrations, actual suppliers, all-size compiler,
common-label/mutable-basis, physical hosting, fixed-tape, exact recovery and
analytic transfer obligations remain unresolved or inherited.

## What the certificate establishes

The verifier uses a separate exhaustive tree enumerator, literal macro compiler
and a free noncommutative module. It checks 861 trees through seven factors (also replayed with uninterpreted nonlinear
functions as canonical expression DAGs),
all 642 combinations of {1,3} price vectors through six factors and caps
0..n-1, five larger witnesses, 354 capacity cases, and 2,598 nonlinear
restoration/inverse/target-independence fixtures. Finite evidence supports the
written all-tree inductions; it is not a formal proof of integer multiplication.

The selected fixture is n=59 from assignment seed 59. Other fixed fixtures
are 5,15,27 factors. The experiment stops at these domains; no random search,
literature-priority, all-arity optimum, full supplier or new kappa is claimed.
