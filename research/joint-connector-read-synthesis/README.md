# Joint read-decomposition and root-transfer synthesis

**Exact small-instance synthesis; no new kappa.** This answers the explicit
joint-optimization handoff in conorholds's [PR2208](https://github.com/CrocSwap/integer-mult-bounds/pull/2208).
Its compiler chooses one minimum-read decomposition before placing reads and
root transfers. Here the entire read-vector availability set is part of the
shortest-path state, so the chosen decomposition is postponed until after
transfer optimization. The result minimizes transfers over **all** decompositions
with the minimum read bill, for the specified fixed source word and source colors.

For the predecessor's retained counterexample, the exact optimum is six root
XORs and fourteen readouts. The six-XOR attaining program was already supplied
by its reviewer; it is not a new witness claim. The new result proves the lower
bound across all minimum-read decompositions and provides a reusable complete
state model, an emitted word, and a separately implemented full lower-frontier
check. The pinned predecessor compiler still reports ten XORs for that fixture.

| Source word | Colors, in source-label order | Minimum reads | Minimum transfers at that read bill |
|---|---|---:|---:|
| 2,0,1,2,1,0 | 1,2,1 | 14 | 6 |
| 0,1,2,0,1,2 | 1,2,3 | 15 | 12 |
| 3,2,0,1,3,2,1,0 | 1,2,1,3 | 33 | 12 |
| 0,1,2,3,0,2,3,1 | 1,1,2,3 | 33 | 12 |

Each fixture requests every nonzero source mask. These are fixed-word optima,
not optima over source order, colors, root stock, ports, read/transfer tradeoffs,
or a physical supplier. The three-color fixtures also exercise targets needing
more than two reads; this is not limited to paired readouts.

## Exact interface

Over F2, take immutable source rows x_j, two arbitrary dirty roots z0,z1, and
distinct arbitrary dirty output rows y_m. Fixed linear maps B_j and A_m may be
singular and need not commute. The endpoint is

`y_m += A_m(sum_{j in m} B_j x_j)`, with every source and both roots restored.

All B and A children use physical z0. Allowed operations are complete calls
`B_j: z0 += B_j x_j`, `A_m: y_m += A_m z0`, and paid root shears
`C_p: z_p += z_(1-p)`, p=0,1. Children restore their own disjoint scratch and
prescribed heads; none of the data ports is child scratch. Outputs are never
read and have no intermediate delivery deadlines. There are no source shears,
extra roots, overwrites, clean-state assumptions or combined map calls.

The source label sequence is fixed, each label occurring exactly twice. A fixed
nonzero logical source color v_j in F2^2 is supplied. Integers 1,2,3 encode its
two bits. At a source event the physical frame G must satisfy G v_j=e0. This
fixes the normalized source path while allowing every legal paid root-frame
word. Initial and final frames are identity.

## Completeness argument

After t source events let Q(t) be the two normalized source coefficient rows.
The physical roots are `G(d + Q(t) X)`, where d contains their arbitrary initial
dirt and X_j denotes B_j x_j. A read through z0 has coefficient vector
`(l, l Q(t))`, with l the first row of G. Encode this vector in F2^(n+2).
For each target m, the sum of its read vectors must be `(0,m)`. This condition
is necessary and sufficient for all allowed maps and dirty inputs: the two dirt
coordinates cancel and A_m distributes across the specified source sum.
No A/B operator factors are commuted.

First collect the three possible nonzero l at every source cut. BFS in the
additive vector space finds each target's minimum read distance d_m. These
individual minima are simultaneously attainable: both root shears generate
GL2(F2), so one can visit all three read directions at every cut, move to a
legal source frame, and finally return to identity. Targets are independent
and unread. Thus the minimum total read bill is sum d_m, and every program
with that bill realizes each individual d_m.

The joint graph state is `(t,G,S)`, where S is the set of read vectors available
at any already visited cut/frame. The current vector is inserted automatically.
There are two types of edges:

- A legal next B event advances t at cost zero, keeping G and adding the new
  current read vector. Its fixed complete price is common to all candidates.
- Either root shear changes G, adds the newly exposed read vector and costs one.

A terminal state has t equal to the source-word length, G=I, and every target
has distance d_m using only S. Dijkstra then minimizes the number of root
shears among all programs with the minimum read bill. Conversely, any actual
legal program projects to such a graph walk. Every accepting graph walk emits
an actual program: choose the target decompositions over S, and place each
read at its first visited occurrence. Multiple targets using one vector each
pay their own complete A call. Repeated identical reads of one target cancel
in F2 and cannot be required in a minimum decomposition. Hence there is no
hidden read capacity, lifetime or delivery constraint omitted from S.

This proves the reduction, not merely the correctness of the four examples.
The implementation accepts n=1..6 but imposes a 250,000-state resource cap;
overflow raises an error and supplies no optimum. There is no transfer-depth
cutoff or truncated-success mode. No feasibility guarantee for every n<=6 is
claimed. The mathematical graph is finite for any fixed instance.

## Independently reconstructed lower frontiers

`synth.py` uses normalized cuts, integer availability masks and Dijkstra.
`independent.py` instead evolves the two actual physical formal root rows,
stores available vectors as sets, and closes every free source transition
before taking another shear layer. It calculates read distances by repeated
set XOR products. It does not import the first solver or the predecessor.

For every cost below the claimed optimum, **every reachable state** is
reconstructed. After converting representations, both engines compare the
canonical SHA256 of the entire sorted lower frontier and all its layer sizes.
An accepting state must be absent below the optimum and present at it.
For the first fixture the complete lower-layer sizes are
`[3,9,22,41,67,111]` at costs 0 through 5. `RESULT.json` binds all four full
frontier digests, emitted words, distances and observed state counts. The
receipt is checked by recomputation, not accepted as a standalone proof hash.

A separate dense binary matrix interpreter checks the emitted words on 2,112
dirty basis columns forward and in reverse, across sixteen deterministic map
fixtures per word, including singular and noncommuting maps. Five controls
reject an omitted source call, omitted transfer, wrong read port, a false
five-transfer optimum, and a state cap of one. The written completeness proof
and fully replayed state graph carry the finite optimality claim; the dense
samples alone would not.

## Reproduce and complete cost boundary

Python 3.12, standard library, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/joint-connector-read-synthesis
python3.12 -I -O -B research/joint-connector-read-synthesis/verify.py
```

Expected direct marker: `PASS_JOINT_CONNECTOR_READ_SYNTHESIS`.
Default verification is read-only; explicit `--write-receipt` refuses to
overwrite an existing receipt. Exact SHA256 and Git-blob pins are checked before
loading the retained predecessor compiler. It is used solely to reproduce its
credited 14-read/10-transfer baseline, not by either new solver.

For complete positive fixed child prices b_j,a_m and a common root-shear price
tau, a certified word has bill

`I + P + E + 2 sum_j b_j + sum_m d_m a_m + T tau`.

I includes admission/hosting and two dirty root rows; P includes preparation;
E includes emission, descriptors and dispatch not already in the complete
operation prices. Each child price includes access, frames, its scratch
restoration and head return. Each shear price includes the full length-L row
pass and routing. For the first fixture, relative to the predecessor compiler,
the difference is `-4 tau + Delta(I+P+E)`. This is favorable only when the actual
extra costs are below four complete shears. No free preparation or physical
runtime saving is inferred. With unequal shear prices or accepting more reads
to save transfers, a different objective is required.

## Sources and scope

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
OS nonce `2707d343e3a9073791753d906ef09c58` selected recursive-interfaces.
The task is explicitly changed from a new alphabet experiment to the PR2208
solver handoff. `TASK.json` records coverage and limitations of the PR/Discussion
metadata search; it does not certify novelty or cover every code diff.

Credit conorholds PR2208, head `28480ef4fdb4caeab89765ea56595bf1f6f37688`, for
the fixed-color compiler, its explicit limitation and retained reviewer
counterexample. Credit its reviewer for the six-transfer witness. Exact source
bytes and Apache-2.0 license are retained under `sources/` and pinned in
`PREDECESSORS.json`. Ross Richardson's PR934/943 supplies the generic dirty
connector and prefix-read lineage; Cinna Davis PR1887 and conorholds PR2182
supply nearby fixed-port constructions/boundaries. PR2182's five-source
two-call optimum is a different result and is not reasserted here.

## Open next questions

Can safe dominance pruning make this joint model practical for PR2208's n9/n12
walks? First prove a same-cut/frame superset dominance rule, then apply it to
one pinned word while preserving a lower-bound certificate. The present state
cap and examples supply no larger-walk optimum or scalable runtime bound.

Can a concrete recursive caller host this two-root interface at a favorable
complete tariff? Bind the actual child ports and price stock, routing,
preparation, restoration, precision and tape return before making a supplier
claim. No such caller, selected assembly change, kappa improvement, full selected
cold replay, proof-assistant formalization or hosted CI result is supplied.

Prepared for ywz65 with substantial OpenAI Codex assistance in derivation,
implementation, experiments, review and prose. Both new implementations were
written by the same AI assistant; independent human review is not claimed.
New material is Apache-2.0.
