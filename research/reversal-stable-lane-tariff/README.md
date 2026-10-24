# Exact stable-lane pass count for reversal

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: **scoped constructive proof with exact finite corroboration**.
In the abstract stable-lane split/merge model, reversal of n distinct records
is feasible in k passes with capacities T_1,...,T_k exactly when

    n <= product(T_i).

Thus the minimum for fixed T >= 2 is ceil(log_T n). The construction handles
arbitrary incomplete mixed-radix grids while routing only the real records.
For example, seven records need exactly two three-lane passes, with no
padding records. Empty lanes and identity passes are allowed. A pass may
arbitrarily split and interleave its lanes while preserving each lane's
input order. It cannot copy or delete a record.

[PROOF.md](PROOF.md) proves necessity by distinct lane-choice tuples and
attainment by complementing one mixed-radix digit per pass. The lower-bound
method is credited to Matarener's [#3825](https://github.com/CrocSwap/integer-mult-bounds/pull/3825)
pass-model obstruction. James Reed's
[#3839](https://github.com/CrocSwap/integer-mult-bounds/pull/3839) supplies the
earlier finite composition census. Neither predecessor's computations are
replayed. The new step is an attaining all-size reversal route and exact
heterogeneous capacity criterion. No historical priority is claimed for
radix routing, the chain partition lemma or the lower-bound method.

This is an abstract layout tariff. It supplies neither an admitted physical
tape implementation nor a lower bound for unrestricted multitape machines.
Routing descriptions, splitting, merge control, physical head movement,
storage, return and reversible cleanup have no paid implementation here.
There is no new kappa or selected-frontier change.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/reversal-stable-lane-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/reversal-stable-lane-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/reversal-stable-lane-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/reversal-stable-lane-tariff --check-source-history
```

Any CPython 3.12 interpreter can replace the local path. The direct verifier
writes no files and runs from a Git-free copy of the six package files.
It prints `PASS_REVERSAL_STABLE_LANE_TARIFF` and a generated JSON receipt
bound to SHA256 hashes of those six files. No receipt is handwritten or
stored as a separate expected result. Publication preflight requires Git.

The route census covers every n from one through product(T_i) for all
341 capacity tuples of lengths zero through four over 1,2,3,4. It also
checks three 4,096-record boundary fixtures, including a virtual grid of
16^12 positions without materializing that grid. In total it checks
11,114 routes and 43,237 stages. All 341 next-size capacity failures are
rejected. A separate checker compares each lane's actual input/output
streams, every stage seam and the final endpoint, using no virtual-coordinate
formulas. This checks record identities and therefore arbitrary payloads.

An independent breadth-first search finds exact reversal distances for
orders one through six at lane counts 2,3,4, giving 18 contexts. It enumerates
all permutation generators with decreasing-subsequence length at most T,
using a quadratic dynamic program separate from the constructor. The written
chain partition lemma proves that these are exactly the permitted passes.
The search agrees with the theorem in every context. Six malformed-input
controls and six route mutations are rejected, with explicit exceptions
that remain enabled under optimization. The universal claim rests on the
written proof, rather than extrapolation from these finite checks.

## Scope and provenance

The canonical base is `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority
revision 7. [TASK.json](TASK.json) preserves the original formal-interface-lemma
card and declares a changed scope to a combinatorial side result. This
does not formalize a selected interface or establish a supplier saving.
The card's historical first command, `scripts/research_baseline.py`, fails
with `KeyError: 'bit_lower'` under the selected schema. The current-priorities
replacement, `scripts/research_selected_baseline.py`, passes its metadata
binding check. Neither command is a scientific replay of this result.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144274)
was preceded by a question-specific local reservation, live handoff and
active-Discussion checks, recent same-account contribution checks, and
distinctive all-main README and merged-PR searches. The overlap helper's
remote snapshot covered 305 open PRs and 4,293 Discussion records with
complete pagination. Its sparse local search covered 127 of 6,918 tracked
README/TASK notes; relevant predecessors were materialized and all-main
README searches supplemented it. Arbitrary diffs and unpublished work are
outside that coverage. No search proves absence of overlap.

[SOURCES.json](SOURCES.json) binds the two predecessor READMEs and the
catalogue/selected record as historical provenance. The proof and verifier
are self-contained, and there are no external runtime inputs. No frozen
predecessor or selected artifact is changed. Credit Matarener for the
bit-free supplier and pass obstruction, James Reed for the finite product
census, and their retained native/Walsh/compiler/coverage predecessors.

Independent human and formal proof-kernel review are unclaimed. Lean,
Docker and the selected scientific cold replay were not run. Optimal
depth for arbitrary other permutations, physical route execution,
ownership/frame restoration, precision, stock, recursive consumer pricing
and outer admission remain outside scope. Unknown costs are not zero.

## Engineering and executable bounds

The Autonomous local run playbook stops at this first exact tariff.
Build the Lever led to the route constructor; Prove It Works led to an
independent lane-stream checker and literal shortest-path minima.
The verifier has no recursion, subprocesses, network access, shared-state
mutation or dynamic imports. Every loop has fixed bounds or is bounded by
validated n <= 4,096, at most 12 stages and at most 16 lanes. Virtual
coordinates are below 16^12. The BFS is limited to six records, so its
generator, frontier and visited collections each have at most 720 entries.
The largest route stores at most 12 stages of three 4,096-entry tuples.
Functions are at most 23 physical lines. Warnings are errors in both
registered normal and optimized runs. No external static analyzer is claimed.

Power of Ten rule 3 deviation: CPython allocates integers and collections
during construction, sorting, hashing and BFS. Fixed preallocation cannot
prevent those managed-runtime allocations. The validated bounds above
limit live state; census routes are discarded between cases. Boundary
fixtures exercise maximum record/stage capacity. Increase these executable
limits only after reviewing live memory. The mathematical proof has no
corresponding dimension restriction.

Power of Ten rule 8 deviation: the standard-library frozen dataclass
decorator constructs methods for the closed four-field Stage record.
It provides immutable stage data; no user-defined registration or runtime
code input is accepted. All construction and validation paths are exercised
by normal/optimized replays. A different record representation would need
the same immutable data and lane-contract checks.

## Open next questions

Can an actual fixed-tape caller realize the mixed-radix reversal routes with
a fully priced controller and cleanup? Begin by lowering the explicit
seven-record, two-pass, three-lane fixture to one named caller's instruction
vocabulary. Lane selection, merge control, head movement, returned state
and reversible cleanup are the blockers. The abstract minimum alone does
not pay these costs. This question is unclaimed here.
