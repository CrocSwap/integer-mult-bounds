# New rational relay charts do not lower nine BIT arrival prices

At each of the nine original forward rank-seven arrivals into chart 0,
the minimum price remains `7^t` for `0<t<=1`, even with arbitrary new
rational relay subspaces in the eight-dimensional ambient space. New
charts have no additional source information. The proof permits any
finite number of paid transfers and intermediate XOR operations.

This extends PR7750 beyond its fixed chart set. It does not prove a relay
floor at the other 5,733 arrivals, a joint-network additive lower bound,
or a new kappa. Exact source and credit links are in [CREDITS.md](CREDITS.md).

## 1. Contract and source evidence

Keep the nine required binary rows and deadlines `26861+8i`, `0<=i<9`,
the 659 independent inputs, and all original chart libraries strictly
before the chosen deadline. Grant those libraries, retention and local
scalar XOR for free. A transfer between nested rational subspaces carries
one unchanged normalized binary scalar form. Its rank is the dimension
difference and its price is that rank to power `t`.

The retained charts lie in `Q^8`. Permit arbitrary additional rational
subspaces of that space. They start with zero scratch and no new source
observations. Any information delivered to them must use charged transfers.
Identify equal subspaces, including different labels for the same frame;
free communication within one subspace does not add source information.
Every remaining transfer has positive integer rank. Branching, merging,
cycles, cancellation and arbitrary finite programs are permitted.

The complete retained PR7750 replay supplies the original dimensions,
source supports, rational nesting, paid rows, source attainments and
fixed-quotient target cosets. In that quotient, the nine target coset
distances are

```text
56, 58, 52, 50, 51, 50, 50, 48, 48.
```

Original nonroot chart dimensions are `1,2,4,6,7,8`. The maximum projected
library support unions at dimensions `1,2,4,6` are `1,2,17,30`. These
libraries stay fixed over the nine deadlines. The chart-0 information is
handled separately by the free coset space. A new chart has support weight
zero until a paid transfer brings information to it.

## 2. Exact separation of original dimension-four charts

There are 70 original dimension-four charts. The full unordered pair
census contains 2,415 pairs. Their intersections have dimensions:

| Intersection dimension | Pairs |
|---|---:|
| 0 | 1,155 |
| 2 | 1,260 |

In particular, no distinct pair shares a three-dimensional subspace.
The proposed new dimension-three hub therefore cannot be contained in
even two such source charts, much less the three required by its rank-six
star proposal.

For each chart, the retained source gives a full rank-four orthogonal
complement. Stack the complements of a pair. Its rank is six or eight,
so the intersection dimension is eight minus that rank. The new checker
uses integer row elimination with primitive-row division, then separately
checks rank modulo the verified prime 1,000,003. All ranks agree. The
source checker verifies the complementary bases and their orthogonality.
[RESULT.json](RESULT.json) lists every pair and exact rank.

## 3. Subspace distance controls every new relay path

For arbitrary rational subspaces define

```text
delta(A,B) = dim(A)+dim(B)-2 dim(A intersect B).
```

This is a metric on subspaces. For its triangle inequality, the intersection
of `A intersect B` and `B intersect C` lies in `A intersect C`, and

```text
dim(A intersect C)
  >= dim(A intersect B)+dim(B intersect C)-dim(B).
```

Substitution gives `delta(A,C)<=delta(A,B)+delta(B,C)`. For nested charts,
`delta` is exactly the paid dimension difference. Thus the cost of any
relay path, through any new charts, is at least the distance between its
endpoints.

Every original dimension-four chart is distance four from chart 0.
Section 2 puts distinct original dimension-four charts at distance at
least four from each other. Any tree that connects chart 0 and three of
these charts therefore costs at least eight. To see this, traverse every
tree edge twice, starting and ending at chart 0. List the three other
terminals in order of first visit. The four successive walk segments,
including the return to zero, each have length at least four. The whole
walk has length twice the tree cost, so that cost is at least eight.

The argument permits arbitrary Steiner vertices. It uses actual pair
distances, not a restriction to the original dimension alphabet.

## 4. Every cheaper information component has small support

Let `R` be the sum of all positive transfer ranks. Concavity gives

```text
sum_e s_e^t >= (sum_e s_e)^t = R^t,    0<t<=1.
```

A network cheaper than `7^t` must have integer `R<=6`. Form its undirected
chart graph after identifying equal subspaces. The target lies in the span
of all original libraries in the component of chart 0. Local XOR and
transfers cannot import information from outside that component. Granting
the entire component's initial stock to the receiver is a relaxation.

Choose a spanning tree of that component. It has cost at most six and at
most six nonroot vertices, since every edge has positive integer cost.
Its path from zero to a dimension-`d` vertex costs at least `d`. Hence
no original dimension-seven or dimension-eight stock can occur.

If an original dimension-six chart occurs, its path from zero uses the
entire rank budget. The whole tree is that path. Equality in the dimension
triangle inequality makes its subspaces strictly increasing. Remove the
new charts, which have no initial stock. The remaining original charts
form one of the nested chains already checked in PR7750. Their total
projected support is at most 35. Optional new dimensions three or five
do not change this stock bound.

Otherwise, all original nonroot stocks have dimensions one, two or four.
Section 3 allows at most two original dimension-four vertices: three
would require tree cost at least eight. Let their number be `k<=2`.
Each contributes support at most 17. Every other original nonroot stock
contributes at most two, and new vertices contribute zero. There are at
most six nonroot vertices in total, so the union of all original stock
supports has size at most

```text
17k + 2(6-k) <= 42.
```

This bound intentionally counts every remaining vertex as if it held
original dimension-two stock. No attainability or optimal-support claim
is made for 42. Both cases give a necessary component support bound below
48, independently of the number or choice of new rational charts.

## 5. Coset separation gives the price floor

If a network supplies the required target with free chart-0 XOR, some
member of its target coset must lie in the span of the component's nonroot
initial stock. That member has support at most 42 by Section 4. Every
target-coset member has weight at least 48 by the exact retained certificate.
This contradiction excludes every cheaper network.

The original single rank-seven transfer remains feasible by the source
attainment checks. Therefore the minimum is exactly `7^t` at each of
the nine deadlines. Extra nonnegative formation, retention, transport or
restoration fees cannot create a saving.

## 6. A changed geometry shows why the pair premise matters

The rank-six star is possible in other source geometries. In `Q^8`, let
`H=span(e0,e1,e2)` and take three four-spaces formed by adjoining `e3`,
`e4`, and `e5`, respectively. Each contains `H`. Three rank-one transfers
to `H` followed by its rank-three transfer to zero have total rank six.
The pair distances are two, and the four-terminal tour bound is six,
not eight. The pair certificate rejects this control, as well as a duplicate
four-space pair. This distinguishes the source-specific geometry theorem
from a false universal claim about all four-spaces.

The local program checks this positive geometric control but does not claim
that its arbitrary invented stock supplies any of the actual BIT targets.

## 7. Scope and evidence status

The new contribution is the exact pair-intersection certificate and the
metric tree argument that admits arbitrary new zero-initialized charts.
The support and coset certificates, the 35-chain bound and the original
attainments are unchanged predecessor evidence and are replayed first.
New integer and modular elimination agree on all 2,415 pairs. Geometry
preparation and other source checks remain shared code. This is not
independent human or formal-kernel acceptance.

The theorem concerns one chosen original arrival and its fixed original
earlier stocks. Its nine separate minima must not be added as a lower bound
for a jointly changed multi-output network. Paid work that changes stock
before several later deadlines needs a complete shared bill. The other
5,733 arrivals need a separate relay audit. New source promises, changed
required rows or deadlines, and uncharged cross-chart operations are also
outside this result.

No physical implementation of the granted free storage or new charts is
supplied. All five framework assumptions remain. The selected cold replay,
unrelated historical suites, Lean, Docker and physical relay execution were
not run. No new kappa or selected-frontier change follows.
