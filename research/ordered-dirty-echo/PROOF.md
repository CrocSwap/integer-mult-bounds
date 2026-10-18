# Optimal ordered binary/ternary dirty-echo schedules

This note proves the recurrence used by the optimizer. It extends the schedule
class of [PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673) to
arbitrary contiguous binary and ternary splits with positive integer leaf
prices and a cap on borrowed arrays. The echo identity belongs to PR673.
[PR689](https://github.com/CrocSwap/integer-mult-bounds/pull/689) optimizes
uniform call counts within recursively balanced ternary splits. Our class
also permits unbalanced splits and mixed fanout, without reordering factors.

The result concerns local schedules. It does not supply a transform layout,
recursive multiplication profile, bit supplier, or new kappa.

## Fixed objects and contracts

The base commit is `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The predecessor sources used here are pinned at:

- PR673, `bfff94e78f0e75ebd2593e3cc7710ae5290e8be3`,
  `research/cyclic-dirty-commutator-audit/echo.py` and `ECHO-PROOF.md`.
- PR689, `0dedef12f05f9a06faf9d4e1c8b1462c0e3bff3a`,
  `research/ternary-dirty-composition/README.md` and `ternary.py`.
- PR628, `0768f97d06c623b8211e651543c66135796b62bf`,
  `research/prime-power-cyclic-scan/DIRTY-PROOF.md`, as inherited and credited
  by PR673. Its leaf bounds remain conditional on its stated hypotheses.
- The integration obstruction is in
  `research/dirty-echo-integration/PROOF.md` at the same pinned PR673 commit.

Let `A_0,...,A_(n-1)` be composable linear maps on equal-length arrays.
Their order is fixed. A leaf for index `i` implements the additive action
`y += A_i x` in exact arithmetic. A schedule tree partitions the interval
`[0,n)` into consecutive nonempty child intervals. Each internal node has
two or three children. Thus a subtree for `[i,j)` implements
`y += A_(j-1) ... A_i x`.

For rounded execution, replace a leaf map by a deterministic increment
`f_i(x)` that is independent of its target. A valid leaf restores its source
exactly and its negative subtracts exactly the same represented increment.
All internal arithmetic, accesses and temporary work required to satisfy this
contract belong to the leaf's price. Fixed descriptors and phase data must
remain unchanged and cannot alias any mutable data. Every source, target and
borrowed array used by the schedule is distinct. Arbitrary overlapping views
and hidden stateful callbacks are outside this contract.

At a node with `k` children, reserve `k-1` connector arrays for the node's
whole execution. Every child uses a deeper borrowed pool disjoint from all
ancestor sources, targets and connector arrays. The deeper pool is reused
between calls because each child restores it. This is PR673's allocation
discipline. The claimed optimum is within this discipline; it is not an
optimum over schedules that reuse ancestor storage according to lifetimes.

## Exact linear identity and nonlinear restoration

Write the child maps in order as `B_1,...,B_k` and the connector arrays as
`z_1,...,z_(k-1)`. Let `C` be the sequence

```text
z_1 += B_1 x
z_2 += B_2 z_1
...
z_(k-1) += B_(k-1) z_(k-2).
```

Let `D` omit the first update of `C`. The node executes

```text
C; y += B_k z_(k-1); inverse(C);
D; y -= B_k z_(k-1); inverse(D).
```

Here inverse means reverse the sequence and invert each operation. Merely
changing signs in the original order is not the specified inverse.

Both ladders restore all connectors. Compare their forward states starting
from the same initial dirt. At `z_1` their difference is `B_1 x`. By linearity,
at `z_i` the difference is `B_i ... B_1 x`. The two target updates therefore
sum to `B_k ... B_1 x`. This argument uses no commutativity. Applying it
inductively to consecutive factor intervals proves the advertised ordered
product for every tree in the class.

Restoration requires less than linearity. Suppose by induction each child
adds a deterministic function of its source and initial deeper dirt,
independently of its target, and restores its source and deeper dirt. Every
inverse ladder call sees the same source and deeper dirt as its forward mate:
later ladder calls have already been undone, and the intervening update to
`y` cannot affect a ladder source or its scratch. Hence all connectors and
deeper scratch are restored exactly. The root source never changes after a
completed child call. Each node is itself a target-independent additive
operation with an exact inverse, closing the induction.

For example, write the nonlinear child increments as `f,g,h`, with their
restored deeper dirt suppressed from notation. The binary output increment is

```text
g(z + f(x)) - g(z).
```

The ternary output increment is

```text
h(z_2 + g(z_1 + f(x))) - h(z_2 + g(z_1)).
```

These formulas explain both exact restoration and the possible dependence of
the output on initial dirt. They are generally not the nonlinear composition
`g(f(x))` or `h(g(f(x)))`. For a scalar negative control, `f(x)=x`, `g(z)=z*z`,
`x=1`, and `z=1` give binary increment `3`, whereas `g(f(x))=1`.
The linear product proof must not be applied to rounded nonlinear increments.

The restoration statement assumes valid leaf inputs throughout execution.
It does not promise transactional rollback after invalid coefficients,
arithmetic overflow, an exception, or a stateful callback.

## Complete local accounting

Let `c_i` be the positive integer price of one signed leaf invocation at a
fixed common arithmetic precision and layout. It must be an exact price or
a charged upper bound valid for both signs and every occurrence, including
the permitted transient source values and array roles. The optimizer does
not model prices that change with a leaf's calling context. The two endpoint
children occur twice in the node word; every interior child occurs four
times. In particular, for weighted
price `W`, unweighted leaf count `N`, and borrowed-array count `S`,

```text
W(leaf i) = c_i,                    N(leaf i) = 1, S(leaf i) = 0
W(binary) = 2 W(left) + 2 W(right)
W(ternary) = 2 W(left) + 4 W(middle) + 2 W(right)
S(binary) = 1 + max(S(left), S(right))
S(ternary) = 2 + max(S(left), S(middle), S(right)).
```

The same recurrences for `W` with every `c_i=1` give `N`. Equivalently, a leaf's
multiplicity is the product of the factors `2` or `4` on its root-to-leaf path,
and `W` is the sum of multiplicity times price. The scratch formulas are exact
for the stated reserved-connector allocator, since child calls run serially
and restore the deeper pool. For length `L`, the schedule borrows `L*S` data
words, in addition to source and target, for `S+2` total array roles. These
words may contain arbitrary dirt. No zero initialization, hidden copy or
additional clean length-`L` array is part of this schedule.

Every repetition, including a call inside an inverse ladder, is charged.
The leaf price must cover its forward pass, output pass, source undo,
validation, coefficient/phase accesses and the arithmetic needed for exact
represented subtraction. Routing or frame changes may be included in these
prices only when the same bound applies to every occurrence and context.
Otherwise their costs remain additional explicit terms. Preparation is also
additional unless it is already included. A complete local bill has the form

```text
preparation + sum_i multiplicity_i * charged_leaf_price_i
            + remaining_routing_and_frame_work + schedule_dispatch.
```

The selected schedule tree occupies `O(n)` descriptor records. The iterative
emitter streams its instruction word with `O(N)` dispatch operations. To see
this, expand each invoked binary node into its four child calls and each
invoked ternary node into its eight child calls. The resulting execution tree
has `N` leaves and at most `(N-1)/3` internal nodes, each handled by a constant
number of record operations.

The pending stack executes this tree in depth-first order. At most seven
unvisited sibling calls remain for each ancestor of the current call. With
`h` internal ancestors its size is at most `1+7h`. Each such ancestor reserves
at least one connector, so `h<=S` and the live stack uses `O(S+1)` records.
The small command lists for the currently expanded node have at most eight
entries. The leaf's own clean scalar workspace, factor descriptor storage
and arithmetic workspace remain additional resources. The `O(n)` selected
tree and `O(S+1)` live stack are separate storage charges.

The optimizer minimizes the displayed weighted leaf bill. It cannot infer
prices for an unimplemented source-access mechanism, assume a free phase
table, or omit restoration performed inside a leaf.

## Dynamic programming optimum at each scratch budget

Let `F(i,j,b)` be the minimum weighted leaf bill for `[i,j)` with at most `b`
borrowed arrays in this allocation discipline. Infeasible values are infinity.
The base cases are `F(i,i+1,b)=c_i` for `b>=0`; every state with `b<0` is
infeasible. For intervals with at least two factors,

```text
F(i,j,b) = min of

  2 F(i,m,b-1) + 2 F(m,j,b-1)                  for i < m < j,

  2 F(i,m,b-2) + 4 F(m,l,b-2) + 2 F(l,j,b-2)  for i < m < l < j.
```

Any legal nonleaf schedule has a binary or ternary root and one of the listed
contiguous partitions. Its child budgets are at most `b-(k-1)`, so induction
on interval length bounds its cost below by the corresponding displayed sum.
Conversely, concatenate child minimizers for any finite displayed sum using
the node word. They restore the common deeper pool and use at most `b` arrays,
so the sum is attainable. Taking the minimum proves both completeness and
optimality. Every child is shorter than its parent, and the number of trees
is finite; there is no search cutoff in this recurrence. Ties may choose any
attaining tree without changing the proof.

The offline optimizer has at most `O((b+1)*n^2)` interval-budget states.
Each state considers `O(n)` binary cuts and `O(n^2)` ternary cut pairs, using
a constant number of cached-state accesses and integer arithmetic/comparison
operations per choice. Thus planning takes `O((b+1)*n^4)` such operations and
stores `O((b+1)*n^2)` states. For `b>=1` these are `O(b*n^4)` operations and
`O(b*n^2)` states. Each retained state stores a price and at most three
references to child trees, so it does not copy a full tree per state. These
are operation and record counts; integer bit complexity and the implementation
cost of memo-table accesses remain additional. Arbitrarily large prices are
not treated as constant-bit integers.

Planning is separate from executing the selected schedule. The complete cost
of finding and running a schedule is this planning cost plus the local bill
above, including preparation, routing/frame work and dispatch. Reusing a
previously computed tree can amortize planning only when that reuse is part
of the application. The call-count improvements alone do not establish an
end-to-end runtime improvement after planning is charged.

Useful invariants are independent of the objective values:

- `F(i,j,b)` is nonincreasing in `b`.
- A nonempty interval of length `n` is feasible exactly when `n<=2^b`.
  Inductively a node with `k` children holds at most
  `k*2^(b-(k-1))<=2^b` leaves for `k` equal to `2` or `3`. Recursively balanced
  binary splits attain scratch `ceil(log2 n)`.
- Every tree uses at most `n-1` connector arrays along a path. Each node on
  that path contributes `k-1` off-path child subtrees, each containing at least
  one distinct leaf. Thus budgets above `n-1` cannot improve the optimum.

This is an exact finite-class optimization theorem. A finite executable replay
checks an implementation of the recurrence and generated words; it is not a
formal proof of a multiplication theorem or an optimality claim outside this
class.

## Finite witnesses

The implemented recurrence and the pinned PR689 resource function give these
uniform-price results. Every row uses the same scratch cap for both schedules.

| Factors | Borrowed arrays | Total roles | PR689 balanced calls | Optimized calls |
|---|---:|---:|---:|---:|
| 27 | 6 | 8 | 512 | 464 |
| 56 | 8 | 10 | 2112 | 1600 |

The 27-factor witness has a root partition into `9,7,11` consecutive factors.
It lies outside recursively balanced ternary splitting, so the improvement
does not repeat PR689's placement optimization. The corresponding pinned
PR673 counts are `512` and `2144`; the table uses the stronger balanced
predecessor. These are local leaf counts, not completed outputs on every role.

For the fixed ordered prices `(3,2,1,9,8,7,6)`, scratch cap `4` yields weighted
price `180` with `36` leaf calls. Cap `5` yields weighted price `168` with `40`
leaf calls. This example separates the weighted objective from invocation
count and motivates reporting both. The weights are an abstract scheduling
fixture, not measured supplier costs.

## Precision and the inherited integration obstruction

Weighted prices must be fixed before optimization. If two trees have different
leaf counts, minimizing their weighted prices at one precision need not
minimize their total bit complexity after precision is increased separately.
Report `N`, `W` and `S` separately and reprice any selected implementation at
its required precision.

For the pinned PR628 leaves, retain all PR673 hypotheses and notation:
`n=r-1`, `0<beta<=1`, grid `u=2^-w`, initial joint norm at most `D`,
`K=r/beta`, `a=13(r+1)/beta^3`, and `G=2+K`. The leaf error on norm at most `B`
is bounded by `a(B+1)u`, and its ideal shear has Lipschitz norm at most `1+K`.
Under `a*u<=1` and `u<=beta^2/2`, the actual expanded word of `N` leaves obeys

```text
M_j + 1 <= G^j (D+1)
E_N <= N a (D+1) u G^(N-1).
```

The second inequality follows by propagating each local error through the
remaining ideal shears and bounding each of the `N` resulting terms by
`a(D+1)u G^(N-1)`. The actual source and scratch restoration is exact; the
target error can still depend on their initial dirt. A sufficient execution
precision for error at most `2^(-p-1)` is

```text
w >= p+1 + ceil(log2(N*a*(D+1))) + (N-1)*ceil(log2(G)),
```

together with the two leaf precision conditions. Coefficient and phase
preparation errors retain their separate inherited budget and source-norm
scaling. The schedule changes `N`; it does not remove those conditions.

The earlier all-role integration rejection also survives these splits.
For every tree with `n>=2`, `N>=4n-4`. First, induction gives `N>=2n-1` for
every subtree: every child is invoked at least twice and the root has at most
`n` children. More explicitly, summing `2(2n_i-1)` gives `4n-2k>=2n` at an
internal node, and the leaf case is equality. At the root, each endpoint
therefore contributes at least `4n_i-2`; each interior contributes at least
`4n_i`, using `N_i>=n_i`. Summing gives `4n-4`.

In the pinned three-shear all-role adapter, even granting one recursive child
per additive leaf and making every wrapper free gives the moment
`Phi(b)=3N/(2*n^(1-b))`. At `b=0`, it is at least `6-6/n>=3`; it increases for
`b>=0`. Thus the same optimistic admission test rejects every positive-saving
profile obtained solely by this adapter. This is a scoped negative result for
that integration, not a lower bound for arbitrary suppliers. Neither smaller
local counts nor an unequal leaf-price witness is a new kappa certificate.

## Attribution

The multiway echo identity, restored-input interface and local error budget
are credited to PR673 and its author, androolloyd, building on Chafik Boukhalfa's
PR628 rounded leaf and Ali Romman's PR621 kernel. PR689 supplies the balanced
ternary comparison and explicitly leaves unbalanced splits and unequal leaf
prices open. Their notices and the repository's Apache-2.0 terms apply to
their work. This note and its accompanying optimizer were prepared with
substantial OpenAI Codex assistance; contributor details are in the claim.
