# Exact scratch/work obstruction for historical complex boundaries

**Scoped negative result; no new kappa.** The five moved registers at a
historical CK/JP8 2+3-cycle boundary cannot implement that permutation in eight
or fewer PR696 real primitives without a temporary register. The existing
PR971 circuit uses eight with one temporary register. Unlike the concurrent
PR1095 monomial-prefix audit, this exclusion allows arbitrary mixed dyadic
intermediate rows and unbounded coefficient magnitudes.

| Permutation | With scratch, existing witness | Without scratch, proved range |
|---|---:|---:|
| two-cycle | 4 | 4 exactly |
| three-cycle | 5 | 6 exactly |
| disjoint two- and three-cycle | 8 | 9–10 |

The precise restriction is **exactly the moved coordinates**: no fixed register
may be borrowed. Each circuit must implement its permutation for arbitrary
incoming values. Both qualifications matter; this is not a general claim
that temporary registers cannot be eliminated from the supplier.

The complete source census finds 28 two-cycles and 14 two-plus-three-cycles in
each of four CK/JP8 orientation programs, 168 boundaries in total. Under this
interface the boundary invoice increases from 224 to at least 238 primitives
per real component, or **at least 28 additional real primitives per complete
orientation**. Exact witnesses give an upper bound of 252 per component.
Other operations still use coefficient work; no whole-supplier scratch saving
or changed paid recursive profile follows.

## Reproduce

Python 3.9+ and a C++17 compiler; standard libraries only, no network or Git:

```sh
python3 -I -O -B research/complex-scratch-free-boundaries/verify.py
```

Expected final line:

```text
PASS_COMPLEX_SCRATCH_FREE_BOUNDARIES boundaries=168 states=509157 costs=4,6,>=9 scratch_costs=4,5,8 no_new_kappa
```

The command rebuilds all three radius-four balls modulo three and independently
compiles a C++ implementation. Every state and minimum distance must match
exactly. It then checks the full meet-in-the-middle result, literal rational
witnesses, 37 gate omissions, all source pins and the complete source census.
It compares the entire fresh receipt against EXPECTED.json and writes nothing.
`CXX` can select a C++17 compiler. A missing compiler or failed independent
check is an error, never a skipped pass.

```sh
python3 -I -O -B research/complex-scratch-free-boundaries/test_package.py
```

Additional tests cover an independent dense GL(2,3) oracle, all ordered
two-dimensional matrix products, quotient halving, generator/depth omissions,
modular false positives, wrong signs and boundary barriers, every source
corruption, complete receipt corruption, and an isolated minimal offline
relocation. See [VALIDATION.md](VALIDATION.md) for executed checks and limits.

[PROOF.md](PROOF.md) gives the rank argument excluding destructive operations,
the dyadic reduction, completeness of the radius-four intersection test and
the precise scope. [EXPECTED.json](EXPECTED.json) contains all actual boundary
indices and exact witnesses. The search has no timeout or heuristic pruning;
the five-coordinate question at length nine remains open here.

## Provenance, coordination and credit

Exact research base: `ba82555c64e1879e4b7decce28186f208fcb8262`.
The selected result at that base is PR1042, conditional
`kappa = 1672188119205421/10^18`. Its actual construction, assembly and review
were followed; this contribution deliberately concerns historical PR626
boundaries. [SOURCES.json](SOURCES.json) pins seven replay inputs by SHA256
and Git blob, plus five base-context documents separately. No pending PR code
is imported. Input archive hashes bind immutable source containers; this
package does not regenerate those archives.

The submission refresh is `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`, where
upstream now selects PR1094, kappa `0.001672660197076918`. All seven historical
inputs are unchanged. This package edits neither selected record.

[CLAIM.md](CLAIM.md) records OS seed 24, three candidates, overlap checks,
bounded domain and stopping rule. There was no pinned coordination issue.
PR1118 covers CK grid synthesis and PR1116 restored helper butterflies; both
were excluded from task selection. PR1095 provides the adjacent one-scratch,
monomial-prefix lower bound. This contribution changes both premises: no
scratch and arbitrary mixed rows. A different seed alone is not the novelty.

Credit **ToikY / Eva Ayala (PR971)** for the deferred-swap construction,
boundary inventory and existing 4/8-primitive witnesses; **woklerx (PR1095)**
for the adjacent scoped lower-bound question; **Sagar Thakrar (PR696)** for
the primitive lowering; **Chafik Boukhalfa (PR626)** and **Jeremy Kothe (PR622)**
for the historical words and interfaces; and icekylinx, DreamingOfClouds,
eumemic, Rohan Arun and the retained source lineage. No priority claim is made
for elementary permutation identities, modular group bounds or BFS.

Prepared for **Ross Richardson / @RossRichardson**, with substantial
**OpenAI Codex assistance**, including the separately implemented checker.
Apache-2.0; repository notices and upstream sources remain unchanged. No
independent human review, full theorem proof, new kappa or measured
multiplication speedup is claimed.
