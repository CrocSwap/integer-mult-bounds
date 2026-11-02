# Exact signed-idle bill for an overlapping stage contract

Scoped proof with exact finite corroboration. No new kappa is claimed.
This contribution was produced by Nick Petalas.

For six independent main fields with stage sets ABC, ABC, AB, AB, BC, BC,
and one native query-pair use of each stage, the determinant deficit is
(2,4,2). Allow arbitrary constant invertible mixing and forward or inverse
whole-idle calls on any nonempty stage subset. The exact idle-inventory
minimum, for every nondecreasing concave tariff H with H(0)=0, is

    2H(24) + 2H(8).

For a strictly concave tariff the unique optimal signed subset multiset has
two positive ABC calls and two positive B calls. The proof covers all finite
inventories, with no search cutoff. It does not construct a chronological
caller with that inventory.

The corresponding target-minus-idle reward strictly exceeds the uniform
six-ABC completion reward for every power tariff H(r)=r^s, 0<s<1. The exact
positive difference is

    4H(17) + 2H(24) - 2H(8) - 4H(25).

Four explicit balancing transfers prove this sign for the whole interval.
The comparison cancels identical full-call/helper charges. Thin queries,
ordinary work and other changed costs still need separate bills. This is a
strict improvement of an optimistic necessary budget, not a physical
construction, paid-profile improvement of the selected supplier or bound on
all possible native callers.

[PROOF.md](PROOF.md) specifies the formal Laurent-variable contract, proves
the determinant requirement, supplies an exact signed dual, classifies
optimal inventories and proves the reward comparison. A specialized
finite-order native action need not satisfy the formal identity hypothesis.

## Reproduce

From the repository root, Python 3.12 and the standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/signed-overlap-idle-completion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/signed-overlap-idle-completion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/signed-overlap-idle-completion
```

Another host may substitute its CPython 3.12 executable. The scientific marker
is `PASS_SIGNED_OVERLAP_IDLE_COMPLETION`; the launcher adds
`PASS_REGISTERED_RESEARCH_PACKAGE`. Replays read and compare the generated
[RESULT.json](RESULT.json), including hashes of every source, proof and
metadata file in this package. Explicit `--write-receipt NEW_PATH` generates
an additional receipt and refuses an existing destination.

The verifier checks 42 signed subset/dual inequalities on the three extreme
nondecreasing concave cardinality tariffs. Those tariffs generate the full
three-point cone by nonnegative combinations. It separately checks 100 hinge
inequalities for the four balancing transfers, ten independent exact bounded
lattice shortest paths on five tariffs and two deficits, an attaining
inventory, the determinant degree debit and six rejecting controls. The
lattice search grants all fourteen forward/inverse subset moves. Its cube
[-4,4]^3 is finite corroboration only; the written dual proves the
unbounded-inventory claim. No predecessor executable or scientific suite is
run as this contribution.

The Python verifier has no recursion and uses explicit finite loops. The
shortest-path oracle has 729 vertices and fourteen directed moves per vertex;
at most 10,207 pushes and 10,935 pop attempts are allowed per run. Capacity
errors fail closed. Functions stay below sixty lines. Explicit exceptions
preserve acceptance under optimization. For Power of Ten rule 3, Python and
Fraction require runtime allocation; this bounded command has at most 729
distance entries, 729 settled entries and 10,207 queued entries. It owns no
persistent resource beyond optional exclusively created receipt output.
No stricter static analyzer configuration or production code is changed.

## Provenance and credit

Base main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The selected-source positive control passed. [TASK.json](TASK.json) records
an explicit change from constructing a complete caller to solving its signed
idle-inventory relaxation. [SOURCES.json](SOURCES.json) pins the catalogue,
selected record and predecessor proof as historical provenance; there are
no external scientific runtime inputs. Source authentication is not review
of predecessor mathematics.

[Ali Romman's released overlapping AB/BC proposal](https://github.com/CrocSwap/integer-mult-bounds/discussions/5593)
supplies the motivating changed demand. His [PR6348 proof](https://github.com/CrocSwap/integer-mult-bounds/blob/9894015d6f380206f990ad5fd14bc49bbd26b0d0/research/balanced-query-tree/PROOF.md)
supplies the full-query, eight-fresh-axis and whole-idle conventions. Cinna
Davis supplies the thin-query/controller interface. DreamingOfClouds and the
retained P104 helper, native, compiler and outer authors retain their credit.
Submodular greedy duality, determinant multiplicativity and concavity are
classical. The new result is this signed completion theorem and strict
comparison for the changed overlapping contract. The predecessor module,
native realization and tree are not reverified or optimized here.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19358970)
reserves this determinant-level question. Searches included live open PRs,
recent claims, local reservations, merged keyword results and current-main
README text. Sparse cached notes and unpublished work remain coverage limits.
The proof adds no literature-wide novelty claim.

Independent human and formal proof-kernel review are unclaimed. New files
are Apache-2.0 under the repository license.

## Open next questions

1. Can any six-field chronological word realize the overlapping query and
   Gaussian outputs at the certified idle minimum? First solve the exact
   Laurent endpoint with all six independent inputs, then price its thin
   queries. The determinant inventory does not settle query coefficients.
2. If minimum-idle placement is impossible, what additional paid inventory
   is necessary? Start with the four tight atoms and prove or falsify their
   compatibility with three full-query stages. No placement obstruction is
   supplied here.

Native frames, absolute phases, autonomous helper preservation, owned
erasure, ordinary operations, precision, stock, tape, compiler and outer
funding remain open. The five selected framework assumptions retain their
status. No selected cold replay, native execution, Lean, Docker or complete
rounded multiplication proof was run.
