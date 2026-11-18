# Arbitrary paid relays cannot improve nine BIT arrivals

At each of the nine forward rank-seven arrivals into chart 0, the original
price `7^t` is minimum even with an arbitrary finite network of paid nested
relay transfers on the retained charts, for `0<t<=1`. This extends the
direct-delivery result in PR7741. It permits new intermediate XOR forms,
branching, merging, cycles and cancellation. It does not extend this relay
conclusion to the other 5,733 arrivals or to new charts.

## 1. Contract and retained evidence

Use the native word, fixed charts, independent inputs and nine deadlines
from [PR7741's retained proof](retained/pr7741/PROOF.md). The deadlines are
`26861+8i`, `0<=i<9`, and the old source charts are 510 through 518.
At every chart, grant its complete original library strictly before the
deadline. Grant storage, local XOR and access to all this earlier stock
for free. A paid call transfers a scalar row between two nested retained
charts, with positive rank equal to their dimension difference. Its price
is that rank to power `t`. New calls can create and forward new linear
forms. Every such call is charged. The required row and deadline stay fixed.

This is an optimistic algebraic communication model. It does not supply
physical storage or a uniform compiler. Arbitrary extra zero scratch is
free. Extra independent dirty inputs cannot help a required identity on
all inputs; setting those inputs to zero gives the same necessary test.
No new chart, helper promise, changed required row or uncharged transfer
is admitted.

The source certificate uses a fixed projection `Q` whose kernel is the
initial chart-0 library. Later free chart-0 rows give a space `F_i` of
dimension `i`. The target cosets `g_i+F_i` have minimum Hamming weights

```text
56, 58, 52, 50, 51, 50, 50, 48, 48.
```

All 514 positive-dimensional charts below dimension seven have fixed
projected support inventories over these deadlines. Their maximum support
union sizes at dimensions `1,2,4,6` are `1,2,17,30`. A union of basis
supports contains the support of every form in that library. The source
replay checks the actual inventories and all 511 target-coset vectors.

The complete retained chart dimensions are:

| Dimension | Charts |
|---|---:|
| 0 | 1 |
| 1 | 111 |
| 2 | 153 |
| 4 | 70 |
| 6 | 180 |
| 7 | 120 |
| 8 | 1 |

Chart 0 is the unique zero chart. Distinct equal-dimensional charts are
not nested. The exact rational geometry check verifies this premise.

## 2. A cheaper network has a small connected component

For positive call ranks `s_e`, write `R=sum_e s_e`. The concave tariff
inequality gives `sum_e s_e^t>=R^t` for `0<t<=1`. Thus a network cheaper
than `7^t` must have integer `R<=6`.

Form an undirected graph on chart labels, with one edge for every paid
call. Its edge cost is the absolute difference of endpoint dimensions.
Direction, chronology and repeated calls can be ignored for a necessary
information bound. The final row at chart 0 lies in the span of the original
libraries in its connected component. This follows by induction on local
XOR and transfers: no operation imports information from outside that
component. Giving every library in the component to the receiver for free
only enlarges what the network can compute.

Choose any spanning tree of this component. Its total cost is at most six.
All edges have positive integer cost, so it has at most six nonroot vertices.
For any vertex of dimension `d`, the root-to-vertex path has cost at least
`d`, by the triangle inequality. Therefore no dimension-seven or
dimension-eight chart can occur in the component of a cheaper network.

If a dimension-six vertex occurs, its path already costs at least six.
The tree has no other edge, and equality in the dimension triangle
inequality makes this path strictly increasing from dimension zero to six.
It is a chain of nested retained charts, with optional dimensions one,
two and four. If no dimension-six vertex occurs, all nonroot labels have
dimensions one, two or four. These two cases cover every finite network,
including networks with cycles or repeated calls.

## 3. Low-dimensional trees have support at most 37

Give an abstract vertex of dimension one, two or four weight `1,2,17`.
For any actual tree, its total projected support union is at most the sum
of these weights. Drop rational nesting and chart identity restrictions,
but require different dimensions at each edge and cost `|d-e|`. Permit
arbitrarily many vertices with the same dimension. This enlarges the class.

Let `A_d(b)` be the maximum weight of a tree rooted at dimension `d` with
edge budget at most `b`, including its root weight `w_d`. Removing one
root branch gives the finite recurrence

```text
A_d(b) = w_d + max(0,
    A_d(b-c)-w_d + A_e(c-|d-e|))
```

where the maximum ranges over `e in {1,2,4}`, `e!=d`, and
`|d-e|<=c<=b`. Both recursive budgets are smaller than `b`, so the
recurrence is well founded. Conversely, join the two trees by the stated
edge to attain every candidate in this abstract class. For the dimension-zero
root, use weight zero and edge cost `d` to each attached branch. The bounds
at budgets zero through six are

```text
0, 1, 3, 5, 20, 22, 37.
```

The abstract tree with edges `(0,1),(1,2),(2,4),(2,4)` has cost six and
weight 37. This proves sharpness only for the abstract sum-of-weights
relaxation, not for actual distinct chart supports or a target row.

A separate coarse argument already suffices for exclusion. If `k` vertices
have dimension four, count edges crossing each dimension level. Levels one
and two have at least one crossing. Levels three and four each have at least
`k`, because no edge joins two dimension-four vertices. Hence total cost
is at least `2+2k`, so `k<=2`. There are at most six nonroot vertices.
Their total weight is at most `17k+2(6-k)<=42<48`. This gives an independent
check on the tree conclusion without its sharper dynamic program.

## 4. Every dimension-six chain has support at most 35

Use the exact rational nesting graph and the source's fixed support masks.
For each strictly increasing chain starting at chart 0, take the union of
the projected supports at all its nonroot vertices. The complete census is:

| Last dimension | Chains | Maximum union size |
|---|---:|---:|
| 0 | 1 | 0 |
| 1 | 111 | 1 |
| 2 | 459 | 2 |
| 4 | 2,224 | 17 |
| 6 | 37,872 | 35 |

The chain `0,7,113,506,348` attains union size 35. The receipt pins the
ordered chain/support trace. One enumeration extends paths from their
first vertex. A second builds paths from their final chart, in increasing
dimension order. The complete sets of 40,667 paths and all maxima agree.
No assumption that a short chain extends to a full flag is used.

The union bound grants all source information on a chain simultaneously,
even if a one-row transfer schedule could not carry it all. It is therefore
a valid necessary bound for actual relay computation. It does not claim
that support 35 is an achievable target or communication capacity.

## 5. Separation and exact price floor

Every cheaper relay network has a relevant component whose projected
nonroot stock has support at most `max(37,35)=37`. Free chart-0 information
is already represented by `F_i`. If the required row could be supplied,
some member of `g_i+F_i` would be in the span of that stock and would have
weight at most 37. Every such member has weight at least 48. This is a
contradiction.

The original single rank-seven transfer is feasible by the retained
source-attainment checks. Hence the minimum price is exactly `7^t` at
each of these nine deadlines. Additional nonnegative formation, storage,
transport or restoration charges preserve the exclusion. No compatible
saving at these nine rows follows from fixed-chart relays.

The other 5,733 arrivals remain covered by the predecessor's direct-bundle
theorem only. Its all-donor test does not automatically cover nonnested
source information carried through relays. No whole-word relay floor or
new kappa is claimed here.

## 6. Verification and next boundary

The verifier authenticates and reruns the complete retained PR7741 package.
That includes source geometry, both paid-row interpretations, every original
source attainment, all support inventories, the nine cosets and its controls.
It then checks the tree recurrence, coarse cut bound, all increasing paths,
the second path enumeration and the strict separation. Controls include a
real chain that violates the old direct-only support cap of 30, a false
strict-separation bound, a support-union check and charged branch/extra-edge
checks. Source geometry remains shared code.

A new chart changes the dimension alphabet and the available nesting graph.
For example, a dimension-three relay can collect three dimension-four
sources for rank one each and send their sum to chart 0 for rank three.
The total rank is six. Whether actual source stocks and a common rational
three-dimensional chart can supply a target remains unproved. Its ordinary,
ownership and physical costs are also open. This is a changed contract,
not a survivor certified by the present result.

All five framework assumptions remain. The selected cold replay, unrelated
historical suites, Lean, Docker and physical relay execution were not run.
No independent human or formal-kernel acceptance is claimed. The selected
frontier is unchanged.
