# The rooted binary repair is optimal at its fixed ports

This is a scoped routing lower bound and an independent scalar audit of
[PR #7786](https://github.com/CrocSwap/integer-mult-bounds/pull/7786)
at `ff6f1d8ab3fafb71ea12ccd943013d058c0f5847`. It does not change the
construction or its complete multiplication exponent.

## Exact class and result

Fix four rational chart ports with strictly nested subspaces and ranks
0,4,6,7. One independent value u is available at the rank-zero port.
The other three ports must each receive u. They have no initial
information about u. Auxiliary inputs may be arbitrary, but independent
of u. Permit any finite straight-line linear computation within a port,
any finite number of scalar paid transfers in either direction between
these four ports, and arbitrary temporary local storage. There is no
additional port, pre-existing copy, free cross-port communication or
shared broadcast. Each transfer between ranks a and b costs
H_(|a-b|), where H_r=r^t and t>0.

The exact minimum paid cost is

```text
H_4 + H_2 + H_1.
```

Every minimum uses the three adjacent port pairs, once each. Information
must travel outward from the rank-zero port. Local linear computations
need not be unique. The bound covers arbitrary finite linear routing,
not only a list of candidate trees. It includes the recursive tariffs
t=1-kappa for 0<kappa<1.

## Proof of the lower bound

Form an undirected graph on the four ports. Include an edge for each
pair that exchanges at least one paid value. If a demanded port were
in a component without the source, fix all other inputs and change u.
Every local state in that component would stay unchanged. Its output
could not equal u in both cases. Therefore the graph is connected.

Select a spanning tree. Every selected edge was used at least once, and
all transfer costs are positive. The total paid cost is at least the
cost of this tree. This argument remains valid with repeated transfers,
linear mixing and arbitrary local storage.

The chain of adjacent ranks is the unique minimum spanning tree for
every t>0. For the cut after rank 0, the unique shortest crossing pair
is (0,4). For the cut after rank 4, it is (4,6). For the cut after rank
6, it is (6,7). Strict increase of r^t preserves those comparisons.
If a minimum tree omitted one of these edges, inserting it would form
a cycle. That cycle contains a different edge across the same cut.
Replacing that longer edge strictly lowers the cost, a contradiction.

Thus all three chain edges are necessary in a minimum tree. Sending u
along the chain attains the bound. Additional paid transmissions cost
strictly more. With only one transmission per chain edge, causality
forces the outward direction and order. This proves the result.

The exact finite certificate separately enumerates all 64 undirected
graphs on four labeled vertices. It finds 38 connected graphs and 16
spanning trees. The sorted rank list of every tree is componentwise at
least (1,2,4), with equality only for the chain. Every connected graph
contains one of the checked trees. This corroborates the proof through
a different finite calculation.

## Binding to the actual owner-411 repair

The [source binary proof](https://github.com/Clear1nsight/integer-mult-bounds/blob/ff6f1d8ab3fafb71ea12ccd943013d058c0f5847/research/p104-iterated-returns/binary/PROOF.md)
identifies the four ports as charts 0,509,390,517. The checker reads
their actual rational bases from the frozen word. Exact rational row
reduction verifies ranks 0,4,6,7 and every pairwise containment. Chart
1 has rank eight, so the separate owner-411 bridge to chart 509 has
grade four.

The checker interprets all 42,958 literal instructions without importing
any predecessor execution engine. It assigns a separate GF(2) variable
to every one of the 680 public inputs. Forward interpretation gives

```text
X_i -> X_i,          0 <= i < 111,
Y_i -> Y_i + X_i,    Y_i has address 111+i,
h_j -> h_j,          222 <= j < 680.
```

Reverse interpretation transposes each ADD, reverses each MOVE, and
exchanges activation with retirement. It gives the full adjoint.
All 462,400 matrix coefficients agree in each direction. Chart tags,
local ADD contacts and private lifetimes are checked. All 3,554 private
retirements carry nonzero values in each orientation; this is evidence
under the source's owned-erasure semantics, not a physical erasure proof.

A separate extraction replaces each paid arrival with an independent
symbol, then transposes those local linear equations. Expanding this
packet graph gives the same complete adjoint as the literal interpreter.
In this independently numbered graph, the rooted chain is

```text
packet 2944: chart   0 -> 509, with 55 direct exterior donors,
packet 2943: chart 509 -> 390, copies packet 2944,
packet 2942: chart 390 -> 517, copies packet 2943.
```

The expanded root is exactly the 55-input form specified in the
[source feedback receipt](https://github.com/Clear1nsight/integer-mult-bounds/blob/ff6f1d8ab3fafb71ea12ccd943013d058c0f5847/research/p104-iterated-returns/binary/intermediate/OWNER411.json).
These packet numbers are ordinals in the final emitted word. They are
not the original recipe labels 2329,2590,2944.

The separate packet 3553 sends x_411 from chart 1 to chart 509. Its
only sender is input 411, and output 411 reads only this packet. The
root form contains no input 411 and is nonzero. Thus the two required
values are independent; the root cannot replace the helper bridge.

Replacing the rooted chain by three equal-value cycle equations leaves
an undetermined common value. The chronological scheduler rejects it.
Setting the root to zero also changes the complete operator. Neither
operation gives a valid cheaper realization of the specified value.

Every one of the 55 direct root terms is essential to this fixed word.
Let v_j be the expanded value of one donor, and let h be the complete
output response to a unit pulse at the root. The dependency graph is
acyclic, so deleting that donor changes the operator by h times v_j.
The checker proves h and all 55 v_j are nonzero. These are nonzero
rank-one faults over GF(2). A complete recomputation for one donor
agrees coefficient by coefficient with that outer product. This does
not exclude a different algebraically equivalent expression for the
root; it establishes the role of each term in the published expression.

## Consequence for further searches

The source already uses the minimum (4,2,1) route at these ports. A
different chronological tree, repeated messages or local XOR mixing
cannot improve that route's signed invoice. The separate grade-four
helper bridge is preserved in this comparison. To seek a gain, change
the ports, available information or consumer contract, then price that
new boundary. This result is not an optimum for the whole binary word.

## Evidence, limits and open next questions

The checker authenticates seven retained files, checks both full scalar
operators, both independent graph/word calculations, the rational port
geometry, the complete graph census and root/bridge omission effects.
It rejects an unrooted cycle, a missing private CLEAR and an altered
port subspace. Deleting the helper bridge changes exactly coefficient
(411,411). The certificate records the root faults' exact supports.

The predecessor's eight-birth construction and intermediate quotient
history are not regenerated. Full physical chart validity, the paired
caller, ordinary compiler, finite stock, precision and outer services
are not replayed. The complete source kappa and ordinary saving are not
recertified. No Lean, Docker, selected cold replay or independent human
acceptance is claimed. All five framework assumptions and the selected
frontier remain unchanged.

An open next question is whether another already-paid observation or an
additional chart can deliver the same value more cheaply under a fully
charged interface. Such an extension is outside the fixed-port theorem.
