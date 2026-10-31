# Independent review of the retained-route G20 lower bound

Prepared for @CubeJerry with substantial OpenAI Codex assistance by worker B.
Apache-2.0. This is an independent mathematical/source review and a separate
graph implementation; it is not human or proof-kernel acceptance.

## Reviewed scope

The exact question is one A2 conjugation or commuting cancellation on the
final #5708 scalar word, retaining correction frames, public boundaries, owned
lifetimes and the row-sensitive emitter contract. Every frame demand may use
any finite directed path made of the existing `PATHS.json` edges. Primitive
edge extension, moved corrections and a second rewrite are outside this
review's single-rewrite scope.

The source route-table SHA-256 is
`f4dd58b78121040b1f054c0f7a626b25f6ef8d39f3de044d3456ea7dea8a6a5e`.
The independent graph implementation imports neither the author's verifier
nor the predecessor executable.

## Graph and all-path argument

`independent_graph.py` parses the 2,369 singleton routes and independently
computes shortest positive-rank distances from each of the 636 vertices using
Dijkstra's algorithm. It establishes:

- Frame 1 is the unique zero-indegree root and reaches every vertex.
- Root distances give levels 0, 1, 2, 4, 6, 7, 8 with populations
  1, 120, 180, 70, 153, 111, 1.
- Every edge rank equals its target level minus its source level.
- All 23,560 positive reachable ordered pairs have shortest rank equal to
  that same potential difference. Including identity pairs gives 24,196.
- A separate increasing-level longest-hop pass gives maximum path length six.

Both normal and optimized execution passed. Four controls reject a changed
edge rank, a backward edge, a zero rank and a nonsingleton source entry.

Since every edge rank is positive, the potential strictly increases. Every
path is finite and its rank sum telescopes; the independent complete graph
closure therefore covers all permitted paths, without an arbitrary path-length
cutoff. Strict subadditivity for `0<t<1` gives

`sum edge_rank^t >= (sum edge_rank)^t`.

Equality holds for a single edge and is strict for two or more positive edges.
Thus charging the endpoint rank difference is a valid optimistic lower bound
for every paid requested path, even when no direct edge realizes that rank.
This is the mathematical mechanism distinguishing the new result from the
earlier direct-table search.

## Independent interval-domain check

A separate full interior scan of every pair of equal ordered ADDs in the
source scalar word gave 2,787 pairs. Exactly 517 have a reversed ADD inside;
none contains an ERASE/INIT of an outer operand. The remaining 2,270 are
eligible, including exactly these two zero-contact cancellations:

| Left index | Right index | Destination | Source |
|---:|---:|---:|---:|
| 5846 | 5852 | 467 | 33 |
| 7339 | 7340 | 241 | 349 |

Indices refer to the 11,930-record scalar list after removing Q/ZERO_Q. This
check independently confirms the domain, rather than borrowing the author's
eligibility counts. It did not rerun every candidate's emitted invoice.

## Whole-emitter source comparison

The reviewed `collapsed_invoice` follows the source `construct.py` on the
proof-relevant cases: zero-source ADDs omit both frame visits; a zero
destination still requires a reachable path but contributes no paid query;
only an unframed whole-zero owned role initializes freely; owned ERASE and
INIT retain their checks; every public role returns to its prescribed final
frame; owned teardown requires zero. Destination and source routes are both
included before a nonzero-source ADD.

The normalized scalar rows do not depend on the chosen route. This uses the
retained invertible native-frame/telescoping interface, which this package
states as inherited. It is therefore valid to use one scalar replay to
determine paid versus zero-payload demands across all path choices. Every
nonzero signed-delta shape accepted by `sign_certificate` is either positive
termwise or a positive rank partition replacing its single sum-rank term;
strict subadditivity proves the claimed sign on the whole exponent interval.

For a zero collapsed delta, the explicit test that all **paid** demands have
direct retained edges supplies an attaining route choice. Reachable demands
on zero rows may use longer paths at zero paid-query tariff. This establishes
attainment for the stated paid-query component; it does not make ordinary
route work free in a complete supplier invoice.

`independent_cases.py` separately replays the 20 newly reachable outcomes and
all 22 neutral attainers. It represents every row as a set of initial column
labels, instead of the author's integer bitmaps, and uses independent Dijkstra
rank distances. Each complete changed word is reconstructed and emitted through
all final returns. Every exact signed invoice and new requested edge agrees
with the primary receipt. All 42 full endpoints and zero/owned conditions
pass; all 22 zero deltas have no new paid edge. Nineteen new-route losses have
shape `H1+H3-H4`, and the other has shape `2H1+H5`. This checks the newly enabled
routes and every attainer, rather than duplicating the whole census.

The remainder of the author's 2,035 unreachable and 193 already-reachable
strict-loss outcomes is primary computational evidence, not independently
replayed here. The independent case selection uses the primary certificate;
the full candidate domain, graph/path mechanism, sign proof and emitter
accounting were independently evaluated as described above.

## Verdict and limitations

The all-path lower-bound argument is valid within its explicit fixed edge
alphabet, correction frames and row-sensitive boundary. It supports a
source-bound paid-query obstruction, not a universal BIT barrier or a new
κ. Native phases, ordinary scalar allowances, stock/precision/tape costs,
complete caller admission and the outer multiplication theorem remain
inherited or unrun. Ali Romman (#5708), unpaidmoon (#6290), Nick Petalas
(#6305), and the retained geometry/native/controller lineage keep their credit.
