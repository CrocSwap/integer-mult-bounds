# Auxiliary charts do not reduce a nested broadcast tariff

This is a scoped routing theorem with exact finite corroboration. It
removes the fixed-port restriction from
[PR #7790](https://github.com/CrocSwap/integer-mult-bounds/pull/7790)
for increasing concave rank tariffs. No new kappa follows.

## Contract and theorem

Fix any finite strict chain of terminal subspaces
`U_0 < U_1 < ... < U_m`, with dimensions `d_0 < ... < d_m`.
One independent scalar u is available at one terminal. Every other
terminal must receive u. All initial states outside the source are
independent of u. Other inputs can be arbitrary. A circuit must work
for every value of those inputs and u.

Allow arbitrarily many additional chart ports, chosen from subspaces
of any common finite-dimensional ambient space. A finite circuit can
use arbitrary local linear operations, temporary storage, repeated
messages and either transfer direction. A paid transfer carries one
scalar between strictly nested subspaces A and B, at cost
`H(|dim A-dim B|)`. There is no free cross-port communication, shared
broadcast or second initial copy of information about u. Local work
and storage have no charge in this routing comparison.

Let `H:[0,infinity)->[0,infinity)` be nondecreasing and concave, with
H(0)=0. Then the exact minimum paid transfer cost is

```text
sum_(i=1)^m H(d_i-d_(i-1)).
```

The adjacent chain attains it. This includes `H(r)=r^t` for every
0<t<=1. The theorem covers every finite number of auxiliary charts,
including charts incomparable with some terminals. Only actual
transferred pairs must be nested. It makes no uniqueness claim for
an optimal route.

The theorem prices this one-scalar information boundary. It is not an
optimum for a complete supplier, arbitrary initial source stock,
multiple dependent demands, shared broadcasts or changed tariffs.
It does not declare physical preparation, storage or restoration free.
Those charges are omitted only from this explicit lower-bound model.

## 1. Information forces a connected graph

Make an undirected graph whose vertices are the used ports and whose
edges are pairs that exchange a scalar. If a demanded terminal is in
a component without the source, hold every other input fixed and vary
u. Every state in that component remains unchanged, so its output
cannot equal u for both inputs. All terminals therefore lie in the
source component. This argument uses only the declared information
boundary; linearity is more than is needed for this step.

Take a spanning tree of that component. Each tree edge was used at
least once. Costs are nonnegative, so the complete paid cost is at
least this tree's cost. Extra components, repeats and cycles cannot
invalidate that bound. The tree may have any finite number of
nonterminal vertices.

## 2. Relax to a line and remove auxiliary vertices

Replace each chart by its dimension. Permit an edge between every pair
of real coordinates, at cost H of their absolute difference. This
relaxes subspace containment and even the integer-rank condition.
Every original tree remains available at the same cost. Coincident
coordinates have zero edge cost in this relaxation.

Consider a nonterminal vertex at x, with neighbor coordinates
`a_1,...,a_k`. Its incident cost is

```text
F(x) = sum_(j=1)^k H(|x-a_j|).
```

If x is outside the interval spanned by its neighbors, move it to the
nearest endpoint. Every incident length weakly decreases, so its cost
does not increase. If x already equals a neighbor coordinate, no move
is needed. Otherwise x lies strictly between two consecutive distinct
neighbor coordinates a<b. On [a,b], every distance `|x-a_j|` is an
affine nonnegative function of x. Concavity of H makes F concave on
this interval. Hence

```text
F(x) >= ((b-x)/(b-a)) F(a) + ((x-a)/(b-a)) F(b)
     >= min(F(a),F(b)).
```

Move x to an endpoint with no greater cost. It now coincides with a
neighbor. Contract their zero-length connecting edge, retaining the
neighbor's label. Because x was not a terminal, every terminal stays
fixed. The graph remains a tree; one nonterminal and one edge disappear.
All other edge lengths after contraction equal their values after the
move. This step also handles nonterminal leaves.

Repeat. The original tree is finite, so the procedure terminates with
a tree on the terminals alone. Its cost is no greater than the
original cost. Intermediate coordinate trees need not correspond to
legal physical charts. They are used only in a relaxation that gives
a lower bound, not as a proposed native circuit.

## 3. The adjacent terminal chain is minimum

On the terminal-only complete graph, consider the cut between d_(i-1)
and d_i. Every crossing edge has length at least their gap. The adjacent
edge is therefore a minimum-weight crossing edge for every
nondecreasing H. If a terminal tree omits that edge, insert it and
remove another edge of the resulting cycle that crosses this cut.
The cost cannot increase.

Do this for each adjacent pair. A previously inserted adjacent edge
does not cross any other such cut, so it need not be removed. The
result is the adjacent chain, of cost given in the theorem. Combining
the two reductions proves the lower bound for every finite circuit.
Sending u outward along this chain from its source terminal attains
the bound, using one scalar transfer per edge. The original terminal
subspaces are nested, so those transfers are legal in the stated model.

## 4. Binding to the actual rooted binary route

The retained
[source proof](https://github.com/aliromman/integer-mult-bounds/blob/8cae9a6b7fed315f704144f27a89bf9b0ad9fd6e/research/binary-rooted-routing-optimum/PROOF.md)
independently interprets the frozen binary word from
[PR #7786](https://github.com/CrocSwap/integer-mult-bounds/pull/7786)
at `ff6f1d8ab3fafb71ea12ccd943013d058c0f5847`. Its actual chart
chain and final emitted packet ordinals are

```text
charts:  0 -> 509 -> 390 -> 517,
ranks:   0 ->   4 ->   6 ->   7,
packets:     2944   2943   2942.
```

The root is a nonzero 55-input form. The next two packets copy it.
Exact rational row reduction verifies every containment. The new
theorem gives the same sharp cost `H(4)+H(2)+H(1)` even after allowing
arbitrarily many auxiliary charts, under the same one-source boundary.
It does not assert that every other bank in the complete supplier is
independent of this form. A proposal that uses such a bank changes the
information contract and needs a separate analysis.

The separate owner-411 bridge has grade four and is preserved. The root
preparation, all other packets, productive targets and cleanup are
outside this route comparison. The source's full conditional kappa is
not recertified. Its PR can advance without changing this frozen claim.

## 5. Exact finite corroboration

The checker decodes every labeled tree by its unique Prufer sequence
and independently checks connectivity, edge count and uniqueness.
For terminal ranks 0,4,6,7 it tests every assignment of each auxiliary
rank in {0,...,9}, including repeated ranks.

| Auxiliary vertices | Labeled trees | Placements per tree | Cases |
|---:|---:|---:|---:|
| 0 | 16 | 1 | 16 |
| 1 | 125 | 10 | 1,250 |
| 2 | 1,296 | 100 | 129,600 |
| Total | | | 130,866 |

For each case it checks all nine tariffs `H_s(r)=min(r,s)`, s=1,...,9.
Their minimum costs are `[3,5,6,7,7,7,7,7,7]`. These checks cover
every nondecreasing concave tariff on this integer grid. To see this,
let `Delta_r=H(r)-H(r-1)`. Then

```text
H(r) = sum_(s=1)^8 (Delta_s-Delta_(s+1)) min(r,s)
       + Delta_9 min(r,9),       0<=r<=9.
```

Every coefficient is nonnegative. The checker reconstructs all 512
binary combinations of these basis tariffs as a separate check.
This finite domain is corroboration, not the arbitrary-size proof.

A separate contraction calculation uses all 1,296 six-vertex trees,
three auxiliary coordinate pairs `(-2,9)`, `(1/2,11/2)` and `(4,4)`,
and caps 1,3,9. All 11,664 exact traces preserve the terminals and
connectivity, decrease the vertex count, and never increase cost.
They test 23,328 contractions, including fractional, outside-interval
and coincident positions. Hashes identify the complete deterministic
censuses; representative traces and aggregate counts are in RESULT.json.

## 6. Controls and limits

Concavity is necessary. With `H(r)=r^2`, the original terminal-chain
cost is 21. An extra rank-two port gives the legal nested chain
`0,2,4,6,7`, of cost 13. The checker rejects that convex tariff and
verifies the strict gain. If u is supplied free at rank four as well
as rank zero, the linear-tariff cost drops from seven to three. Thus
the unique-source premise cannot be dropped. Additional controls
reject a decreasing tariff, a nonzero origin and a false strict floor;
a disconnected demand graph is also detected.

The entire 17-file source package is retained unchanged. Its verifier
runs in both modes and checks all 462,400 scalar coefficients in each
orientation, the actual chart geometry, the independent packet graph,
root/bridge faults and 3,554 dirty retirements per orientation. This
is reuse of the source implementation, not a new independent replay
of those facts. The new census and contraction code is separate.

The earlier construction history, physical erasure, paired caller,
ordinary compiler, finite stock, precision and outer services are
not replayed. No Lean, independent human acceptance or global
literature-priority claim is made. The proof uses elementary
concavity and minimum-spanning-tree exchange. All five framework
assumptions and the selected frontier remain unchanged.

## Open next questions

Identify another already-paid observation that reduces the source
information requirement. Give its exact location, time, extraction
cost and restoration before comparing invoices.

State a joint multi-value demand matrix and initial information
contract. Shared coded messages between different demands are outside
this one-scalar theorem and can require a different lower bound.
