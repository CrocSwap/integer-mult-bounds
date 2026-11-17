# Exact mixed rechart optimization with linear rank prices

This contribution was produced by Nick Petalas. It is a scoped written proof
with exact finite corroboration. For one common hyperplane H and transverse line L, each helper's
allowed subspaces

```text
U intersect H, U, (U intersect H)+L, U+L
```

form a Boolean lattice with one or two bits. On any original nesting graph,
all replacement nesting constraints become at most four implications per edge.
Arbitrary rational dimension-linear signed invoices and fixed endpoint options
therefore reduce exactly to maximum-weight closure on at most two nodes per
helper. The result holds over every field. [PROOF.md](PROOF.md) gives the
representation, objective, min-cut construction and infeasible-pin criterion.

A sharp small example has original rank gap 1, one-sided growth optimum 2,
one-sided shrinkage optimum 2 and mixed optimum 3. Separate one-sided screens
therefore do not bound the mixed family. Two additional examples explain the
scope: positive productive gaps need not define an implication-closed family,
and nonlinear power prices do not become unary linear bit weights. The latter
does not exclude richer cut constructions with pairwise terms.

## Evidence and reproduction

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/mixed-rechart-closure/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/mixed-rechart-closure/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/mixed-rechart-closure
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/mixed-rechart-closure --check-source-history --check-modes
```

Other installations may substitute their CPython 3.12 path. Each registered
command has a 120-second limit. Direct replay prints a generated
`PASS_MIXED_RECHART_CLOSURE` JSON receipt bound by SHA256 to all six package
files. It writes no files and also works in a Git-free export.

The exhaustive checker generates every subspace of F_2^n for n=2,3,4 and
checks every hyperplane/transverse-line pair and every originally nested edge.
It covers 154 flags, 8,518 local lattices, 63,480 nested edges and 552,408 option
pairs. Direct subspace containment agrees with the compiled implications in
every case. A separate direct enumeration of physical subspace options checks
the min-cut objective on 1,950 signed integer price cases, 548 rational-price
fixed-option cases and 83 graph/cycle cases. Eight invalid-domain controls
require the exact rejection reason. The written proof supplies the universal
claim; these finite computations are corroboration, not proof-kernel acceptance.

## Sources and overlap

ToikY [PR #7459](https://github.com/CrocSwap/integer-mult-bounds/pull/7459),
head `4f3dc4a40e2a3bee5fc0d6d5dfd7e4e95614fc22`, leaves mixed growth/demotion
open after its common-hyperplane screen. It supplies the source question and
one-sided motivation. Its #7456/#7454/#7334/#7113 lineage keeps its credit.
No predecessor scientific program, numerical bound or receipt is replayed,
imported or relied on to prove this result. The proof is self-contained.
David Ganz / Dugongue's merged [PR #556](https://github.com/CrocSwap/integer-mult-bounds/pull/556)
already gives a binary frame/projection cut theorem, including monotone
nonlinear paid tariffs. Its two options are U and its oblique projection;
the present four options, mixed growth/demotion and signed linear objective
are different. The new claim is the explicit two-bit representation, rather
than the use of cuts in frame search. Its theorem is pinned as background.
Maximum closure/min-cut and distributive lattices are classical methods;
no literature-wide priority is claimed for them. New work is Apache-2.0.

The `p104-side-correction` card changes scope to an abstract optimization
interface. [TASK.json](TASK.json) preserves the original card and declares
this side result. [SOURCES.json](SOURCES.json) pins the selected record,
catalogue and prior projection theorem as historical provenance. None is a
scientific runtime input.
Base canonical main is `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8, with selected #7000 unchanged. The contextual picker reports that
the catalogue's older #5599 assessment differs from that selected record.
The source-binding orientation command passed; it is not a selected replay.

Live open PRs, recent own PRs, handoff claims, local reservations, merged
searches and distinctive main-tree terms were checked. The cached overlap
search had complete remote pagination but omitted 9,979 sparse local notes;
main-tree Git searches supplement that omission. No claim of complete novelty
coverage follows from absence of matches. Related one-sided open work includes
#7459, #7456 and #7454. #7458 tests a different two-plane growth family.

## Limitations

This is an enabling scoped proof with no new kappa, physical word, supplier
admission, selected-frontier change or complete multiplication theorem. All
five selected framework assumptions remain. No selected scientific cold replay,
predecessor suite, Lean or Docker run was performed. Independent human and
formal proof-kernel review are unclaimed.

## Open next questions

- Can the actual nonlinear signed power invoice be optimized on this mixed
  lattice? Start with its paid/productive edge mixed differences. Positive
  productive-rank constraints and complete charges remain blockers.
- Does a current P104 public-component inventory have a useful mixed rechart?
  First bind the exact word, eligible components, endpoint contracts and every
  incident edge. Scalar/native legality, ownership, dirty restoration,
  precision and stock must be priced before claiming a supplier improvement.

Structured next questions are in [TASK.json](TASK.json). The first proved
reduction is the deliverable; no larger construction search is included.

## Verifier constraints

All functions are below 60 lines. The checker has no recursion, network,
subprocess, dynamic code loading or output file creation. Subspace domains
stop at dimension four. Graphs have at most eight vertices, sixteen bits,
64 edges and sixteen pins; brute-force assignments are at most 4^8. BFS scans
at most eighteen vertices. Edmonds-Karp uses an explicit vertex/arc-derived
augmentation cap and fails on exhaustion. Mathematical guards use explicit
exceptions and remain enabled under optimization. Normal/optimized warning-strict
replay and source compilation supply the available Python diagnostics.

Power-of-ten rule 3 deviation: CPython allocates managed integers, Fractions,
containers and queue nodes during this one-shot check. Fixed fixture domains,
sequential processing and the bounds above limit live collections. Package
reads are limited to 128 KiB per file. No fixed-allocation claim is made; a
fixed-allocation runtime would need a separate representation. Rule 9 deviation:
eight local rejection callbacks have fixed targets and exact expected reasons;
all propagate unexpected exceptions. No general callback input is accepted.
