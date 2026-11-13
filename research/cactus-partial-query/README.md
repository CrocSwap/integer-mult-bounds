# Exact partial-query acquisition on a cactus graph

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration and a bounded
constructive optimizer. For binary edge queries on every finite simple cactus
graph, arbitrary target subspaces have an exact acquisition optimum. Neither
target rank nor target codimension needs to be small. No new kappa is claimed.

Give edge e={u,v} the query x_u+x_v and nonnegative price c_e. The decoder
reconstructs requested parities only from purchased replies. Choose any matrix
R of edge coefficients reconstructing all requested targets, with row r_e.
Then

```text
OPT = sum_(bridge e with r_e != 0) c_e
    + sum_(cycle C) [sum_(e in C) c_e
                     - max_z sum_(e in C with r_e = z) c_e].
```

On each cycle remove the maximum-price bucket of equal rows and translate
all its coefficient rows by that bucket's label. Keep the nonzero rows.
This gives an attaining forest and every reconstruction expression.
[PROOF.md](PROOF.md) proves the lower bound, construction, feasibility test
and independence from the initial coefficient solution. Its cycles may share
vertices, but must be edge-disjoint.

For triangle queries 01,12,02 at prices 4,3,2 and target x_0+x_1, the exact
partial-target bill is four. Pruning the cheapest whole-span basis pays five.
The new result supplies a closed optimum throughout this structured pool,
rather than another bound or a search through target superspaces.

## Reproduce and use

From the repository root, CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/cactus-partial-query/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/cactus-partial-query/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cactus-partial-query
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cactus-partial-query --check-source-history
```

Substitute another CPython 3.12 path on another machine. Run the publication
preflight after committing. Both registered commands have 120-second limits.
They print `PASS_CACTUS_PARTIAL_QUERY` with a generated receipt binding the
SHA256 of all seven package files, and write nothing into the checkout.
No receipt is handwritten. Direct verification needs neither Git nor network.

The optimizer accepts this JSON problem, where vertex bit i is coefficient i:

```json
{"vertices":3,"edges":[[0,1],[1,2],[0,2]],"costs":[4,3,2],"targets":[3]}
```

Save it outside the checkout, then run:

```sh
python3.12 -I -B research/cactus-partial-query/optimizer.py problem.json > certificate.json
python3.12 -I -B research/cactus-partial-query/optimizer.py problem.json --check certificate.json
```

The checker compares all cycle savings and reconstructs every target; it
does not invoke the optimizer. Its graph and base-coefficient routines are
shared with the producer. The independent exhaustive oracle shares neither
routine.

## Exact finite evidence

The verifier enumerates all 1,099 labelled simple graphs on one through five
vertices. A separate edge-subset simple-cycle test finds 691 cacti and rejects
408 noncacti through the optimizer. For every cactus it enumerates every
subspace of its edge-query span, producing 28,305 target bases across graphs.
Each is checked at three explicitly defined integer-price patterns, including
zero prices. All 84,915 optimum comparisons agree with a direct purchased-
subset/XOR-span oracle. The oracle enumerates 39,267 purchased subsets across
graph/price cases. Counts include repeated mathematical spaces in different
labelled graphs or price cases, as stated.

Every optimum certificate and every binary source assignment on its graph
are checked. The 367 cycle occurrences include two cycles sharing a vertex.
Thirty-three larger fixtures include 32 triangles sharing one hub, dependent
and zero targets, and a 128-vertex forest with 128 target columns and prices
10^12. Ten semantic/certificate controls and fourteen invalid-input controls
reject. Normal and optimized Python run the identical explicit checks.
These finite checks corroborate the written theorem; they do not establish
its arbitrary-size quantifiers by extrapolation.

## Scope, provenance and implementation bounds

Ali Romman's [PR #5791](https://github.com/CrocSwap/integer-mult-bounds/pull/5791)
supplies the whole-span acquisition interface and partial-target question.
Its greedy theorem and scientific executable are not replayed. Classical
incidence kernels, cycle spaces, parity and weighted grouping retain credit.
The new step is formula (1) for arbitrary cactus target spaces, its attaining
reconstruction and certificate. Literature-wide priority is unclaimed.
Nick Petalas #5878 and #6654 supply related general-pool approximation and
small-codimension results; their theorems, constructions and code are not used.
Predecessor credit lines and frozen evidence are unchanged.

Canonical base is e54523517d0f03e58352e647c403a5af3e525a57, priority revision 8.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19601550)
states this scope. SOURCES.json pins historical provenance, including #5791's
guide. It is not a runtime import. The selected-baseline binding orientation
passed, with selected #7000 at 0.00363005817; historical priority headlines do
not supersede that record. TASK.json records the changed joint-query-controller
scope and the structured next questions. The card's physical acceptance gate
is not met by this algebraic side result.

Live overlap checked open PRs, this account's recent PRs, handoffs, active
Discussions, merged-PR searches and all-main README searches. The cached helper
covered 846 open PRs and 7,482 Discussion records with complete pagination;
its local scan covered 207 of 10,178 note paths. Targeted Git searches cover
omitted main README text, rather than all historical diffs or unpublished work.
No matching cactus acquisition result was found in that coverage. This is not
a novelty certificate.

The theorem permits real nonnegative prices. The executable restricts prices
to integers in 0..10^12, vertices to 1..128, edges to at most 192 and target
columns to at most 128. Edges have canonical distinct endpoints; duplicates,
loops, noncacti, out-of-range values and infeasible targets reject explicitly.
The implementation is deterministic and polynomial in these input sizes,
with no enumeration of target superspaces. The certificate checker can use
quadratic work in a cycle length to compare every bucket.

Functions stay below 60 physical lines. Loops inherit the fixed input bounds;
the exhaustive graph domain has at most ten possible edges and 1,024 subsets.
The main oracle processes at most 67 target spaces per graph, at most 64
purchases per cactus and at most 32 source assignments per optimum. Inputs and
certificates are capped at 128 KiB; each of seven receipt files at 256 KiB.
There is no recursion, subprocess, network access or code generation in the
scientific checker. Standard-library dispatch and one fixed sibling import
have explicit targets. A local price-key callback only compares bounded rows.

Power of Ten rule 3 deviation: CPython allocates managed integers and
containers during this bounded one-shot computation. The caps above bound
live graph, coefficient, subspace and oracle state. No fixed-allocation or
persistent-service guarantee is claimed. Explicit contracts survive -O.
Warning-strict normal and optimized execution and in-memory syntax/function-
size inspection supply the available diagnostics. No external static analyzer
or proof assistant is required or claimed.

Acquisition prices exclude reconstruction XORs, physical delivery, source
access, chronology, dirty restoration, frames, ownership, storage, precision,
tape costs and a complete paid/productive supplier invoice. No actual native
caller, selected scientific cold replay, Lean, Docker, new kappa, selected-
frontier change or complete multiplication theorem is supplied. Independent
human and formal proof-kernel review are unclaimed. General graphs with
shared cycle edges are outside the theorem.

## Open next questions

- Can one actual native caller supply a cactus query pool whose complete
  partial-target bill improves? First export its queries, targets and prices,
  then charge reconstruction, delivery, storage and restoration. The missing
  physical caller and tariffs prevent a supplier consequence.
- Can the coupled coefficient shifts be optimized for one theta graph? Start
  with its three path coefficient rows. Shared edges couple the cycles, so
  the independent-bucket formula supplies no answer there.
