# Exact finite statement and complete local cost

Let `P(g)` be the positive integer transfer of a sequence of operations
`row[d] += row[s]`, `d != s`, starting from the 6-by-6 identity. The six ordered
registers are `[242,294,296,302,316,501]`. Let `M` be `P` of the source-bound
PR589 phase-A slice `[725:748)`, and let `R` be `P` of that slice in reverse
order. Exact matrices are retained in `CERTIFICATE.json`.

**Finite proposition.** Among sequences on these same six ordered registers
with no extra wires and positive transfer exactly `M`, the minimum length is
11. With the additional constraint `P(reverse(g)) <= R` entrywise, the minimum
length is 12. Repeated destinations, repeated donors and arbitrary interleaving
are permitted. The class does not fix a single-write order or a factor split.
It excludes circuits with a different positive transfer, extra wires,
subtraction gates and altered frames.

## Why the exhaustive graph proves a minimum

Every positive-addition circuit starts at identity and only increases entries,
so every intermediate matrix is entrywise at least identity. Removing its last
operation subtracts the source row from the destination row. Retain precisely
those predecessors that are still entrywise at least identity. Every circuit
therefore gives a path in this graph. Conversely a path to identity reverses to
a valid positive-addition circuit. Each subtraction strictly reduces total
entry mass, since the source row has a positive diagonal. The target has mass
66, so every backward path has length at most 60; sentinel 999 exceeds every
finite distance. The graph is finite without an empirical cutoff assumption.

`search.py` exhausts the predecessor closure and uses a memoized distance
recurrence. `optimality.py` shares no nomination code or stored distances: it
stores flat matrices and performs breadth-first traversal. Identity first
appears at depth 11 after all earlier layers are complete. The explicit
unconstrained 11-gate witness independently gives the upper bound.

For the reverse restriction, augment a state with a second matrix, initialized
at identity. Each last-gate removal is the next operation in the reversed
circuit, so apply that positive addition to the second matrix. Its entries
never decrease. If an entry exceeds `R`, no continuation can satisfy the
constraint. This is a valid monotone prune, not a heuristic.

The independent checker explores these matrix pairs breadth first without
using the searcher's distance-to-identity pruning. It completely enumerates
all reachable admissible pairs through depth 11 and finds no identity first
component. Merging identical pairs is safe: all possible continuations depend
only on the two matrices, and a later visit to the same pair cannot give a
shorter accepted circuit. Together with the checked 12-gate witness this proves
the guarded minimum. Neither verifier reports a minimum on budget exhaustion.

The final witness is selected under the tighter reversed-transfer cap of the
PR936 18-gate frame. That cap is itself no larger than `R`; the verifier checks
both comparisons directly. The baseline-cap exclusion of all lengths through
11 also excludes them under the tighter cap. Hence the 12-gate witness is
minimal under either of these two stated caps.

## Substitution and accounting

The literal witness, in local register indices and execution order, is:

```text
(3,1), (1,4), (4,3), (5,4), (5,2), (1,5),
(0,4), (0,2), (1,0), (2,1), (4,2), (3,2).
```

Exact positive-transfer equality implies equality over F2 for every incoming
state; no helper is assumed zero. Since the replaced slice is contiguous,
all subsequent observations see the same values. Cleanup is rebuilt as the
literal full-frame reverse of all non-target-destination gates in A followed
by B. Elementary XOR gates are involutions, so that reverse restores arbitrary
source/helper dirt. The unchanged H1-H5 checker also validates the whole-word
interface, rather than relying on the local argument alone.

Every original block register still touches the same frame. The verifier
compares all 661 ordered frame paths. No helper, allocation, frame change,
source access, COPY/ERASE, or recursive child is introduced. The complete
scalar invoice, including the required cleanup, is:

| Charge | Original | Replacement |
|---|---:|---:|
| D ADDs | 18,085 | 18,085 |
| A ADDs | 2,130 | 2,119 |
| Scatter ADDs | 527 | 527 |
| B ADDs | 934 | 934 |
| C ADDs | 2,629 | 2,618 |
| **All ADDs** | **24,305** | **24,283** |
| MOVEs | 2,911 | 2,911 |
| COPY / ERASE pairs | 9 | 9 |
| Dirty helpers | 439 | 439 |
| Paid rank mass | 5,129 | 5,129 |

The forward positive block endpoint is identical; its reversed endpoint is
entrywise smaller or equal. Within either positive block each coordinate is
monotone, so its endpoint bounds all its prefixes. Surrounding positive maps
preserve entrywise comparison. Thus the replacement does not increase the
inherited positive envelopes. This is a local algebraic preservation argument;
the package's emitted scalar records are also replayed explicitly.

This result changes finite scalar work, not the paid recursive histogram or
the selected kappa. It does not supply a full hosted construction, an all-size
compiler, a new analytic transfer argument or a formal proof of multiplication.
Source/compiler, geometry, hosting, precision/tape and analytic assumptions
remain those of the pinned supplier.
