# Exact unequal-payload query capacity for bipartite masks

For every finite bipartite permitted-read graph G, every nonnegative integer
payload vector d and every coefficient field, the exact minimum fitting-matrix
rank is

    total payload - maximum integral edge sharing
      = maximum independent-set payload weight.

This is a scoped proof about linear query dimension. Arbitrary rectangular,
nonsymmetric and noncommuting permitted blocks cannot beat coordinate pairing.
It gives no physical supplier, new kappa or selected-frontier change.
[PROOF.md](PROOF.md) gives the full contract, all-field proof and construction.

The three-leaf star with widths (4,1,1,1) has exact query dimension 4. The path
with widths (4,1,1,4) has dimension 8, although each bipartition side has total
width 5. Thus even the larger side total can understate the required capacity.
Integral coordinate sharing attains both answers.

## Contribution and credit

This contribution is produced by Nick Petalas. It extends the unequal-payload
block-fitting interface of [Tekalign's #3362](https://github.com/CrocSwap/integer-mult-bounds/pull/3362)
to the bipartite graph class. The predecessor's nonbipartite C5 result and P112
numbers are cited without replay or audit. Classical weighted matching,
vertex-cover duality and block-fitting methods are credited; no new general
graph-theoretic method or literature priority is claimed.

Credit Sagar Thakrar/#2484, ywz65/#2471, Cinna Davis, Adam Gall, ctoth,
Philippe Van Velzen and the retained P112/E8/native/compiler lineage.
[SOURCES.json](SOURCES.json) binds the historical model and base by exact bytes.
There are no external scientific runtime inputs. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Reproduction and evidence

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/bipartite-query-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/bipartite-query-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bipartite-query-capacity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bipartite-query-capacity --check-source-history
```

Substitute an installed Python 3.12 path on another host. The verifier prints
`PASS_BIPARTITE_QUERY_CAPACITY` after its JSON receipt. An optional
`--receipt /absolute/external/new-file.json` saves the generated receipt with
SHA256 of all six package files. It refuses an existing destination or a path
inside the checkout. Default verification writes nothing.

The replay checks 15,552 weighted cases and 46,656 constructed field ranks.
The separate binary enumeration has 1,297 mask/width/matrix cases, including
repetitions across zero-width masks. Thirteen controls and fixtures pass.

The weighted domain is every one of the 64 bipartite masks on fixed parts of
sizes 2 and 3, with every width vector in {0,1,2}^5. For each recipe an independent
subset enumerator finds the maximum independent weight. The verifier checks
all entries of its expanded matrix and its rank over GF(2), GF(3) and GF(101).
A separate loop enumerates every directed binary fitting matrix on fixed parts
of sizes 2 and 2 for every binary width vector, allowing asymmetric blocks.
Input rejection, false fitting matrices, the unequal star, the path example and
a 4096-bit compressed capacity fixture are also checked.

These are finite corroborations of the written proof. The generic metadata
runner also checks provenance. It is not mathematical acceptance by a reviewer.

## Scope and family decision

The `complex-rank-shape-decoder` card changes to a side result about exact
query capacity. A coefficient search on this graph class cannot improve on the
proved pairing recipe. Stop at that obstruction. No dependent physical
construction round is proposed.

Source access, actual COPY tariffs, frames, dirty restoration, ownership, hosting,
stock, precision/tape, all-size compilation, native realization and complete
supplier/outer transfer remain unproved. A dimension-optimal factorization does
not supply their costs. Nonlinear encoders and nonbipartite masks are outside
the theorem. No selected cold replay, Lean or Docker run is needed or claimed.

## Engineering constraints

Build the Lever supplies a deterministic constructor and verifier. Prove It
Works requires literal fitting entries and actual field ranks, including every
small directed binary completion. Power of Ten bounds the implementation to
at most 14 vertices, 49 edges, 4096-bit widths and 16 dense coordinates. The
scientific driver fixes smaller domains. Residual BFS scans at most V vertices;
Edmonds-Karp uses at most V^3+1 attempts and each path has at most V arcs.
Functions stay below 60 physical lines. All contracts use explicit exceptions
and remain active under optimization. Python's managed allocation is a bounded
rule-3 deviation; allocator internals are not inspected. The proof itself is
unbounded in graph size and dimensions. No metaprogramming, recursion or dynamic
imports are used. Warning-strict normal and optimized runs are registered.
Local Ruff 0.17.1
checks E,F,I,B,UP,SIM,RUF,C4,PIE,PERF,PTH,RET and formatting without suppressions.
The registered scientific replay needs only the Python standard library.

## Open next questions

Can one named triangle-free nonbipartite mask support a block query rate below
its integral coordinate-sharing optimum? Start with an exact fitting identity and price every
required read. The present theorem offers no candidate or native contract.

Can an attaining pair-query factorization fit a fully charged native consumer?
Start with one literal caller and include neighbor reads, frame conversions,
helper restoration and target writes. Physical acquisition and all-size
admission are the blockers. Neither question is reserved by this package.
