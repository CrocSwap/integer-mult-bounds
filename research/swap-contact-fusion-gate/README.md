# No one- or two-region moment gain after PR4971's carried-frame swaps

**Exact scoped obstruction with executable witnesses; no new κ.** On the
changed scalar representation of [PR4971](https://github.com/CrocSwap/integer-mult-bounds/pull/4971)
at `0130b196145a43a7d305de41f49e56e8e8556378`, recharting at most two
source-defined constant-frame regions cannot lower the recursive moment for
any `0<t<1`, where t=1-C. This is stronger than a failed floating search and
narrower than a global optimum. The selected conditional κ stays 0.00302015.

The source replaces 534 three-ADD swaps per orientation with weighted field
exchanges carrying their charts, including 43 swaps with unequal incoming
charts. That opens a changed representation for rank-shape optimization. We
keep this source scalar order, signed address maps, center queries and boundary
contracts, then test the complete local cost of changing chart regions.

| Exact check | Forward | Backward |
|---|---:|---:|
| Contact graph nodes / strand edges | 15,959 / 29,966 | 15,959 / 29,974 |
| Source constant-frame regions | 1,045 | 1,037 |
| Movable regions | 768 | 768 |
| Adjacent movable-region pairs | 1,474 | 1,474 |
| Candidate two-region assignments | 59,231 | 59,231 |
| Feasible assignments, all non-improving | 2,090 | 2,090 |
| Adjacent identity-edge pairs admitting constant-chart fusion | 0 / 1,438 | 0 / 1,438 |

All 768 one-region intervals have quotient dimension at most one: 642 are
rigid and 126 have two chart choices. The two-region enumerator includes
every subspace in each actual outer interval, including noncoordinate lines,
then enforces every connecting and internal operator constraint. Nonadjacent
two-region changes separate into the already checked single-region problems.
Sorted integer rank majorization and three explicitly proved power inequalities
certify every feasible price comparison at every exponent in the stated range.
[PROOF.md](PROOF.md) defines the replacement class and proves the implications.

Both orientations keep the complete recursive profile
`{1:2201,2:412,3:510,4:127,5:40,8:8}`, rank mass 5,327. The unchanged
predecessor replay checks all 632 arbitrary input rows and all 408 helpers;
the new graph code recounts exactly that paid profile and checks signed
operator-to-chart consistency before pricing it. This is not a new physical
Clifford or all-column audit.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/swap-contact-fusion-gate
python3.12 -I -O -B research/swap-contact-fusion-gate/verify.py
```

The registered hook runs both normal and optimized variants. Default verification
is read-only and compares the complete fresh result and every witness against
`RESULT.json` and `WITNESSES.json.gz`. Compressed-container bytes are not a
mathematical equality test: the canonical decompressed witness bytes are compared.
`--write` explicitly regenerates only these two new artifacts. The original
retained verifier never receives the new command's arguments and cannot enter
its own authoring mode.

Checks reject a false zero-to-full native warp, missing unequal-chart carry,
broken graph containment, an omitted paid rank and a profitable fusion being
misclassified as a negative result. A complete quotient fixture includes the
noncoordinate line. The original swap sign/frame mutations also replay.
All checks use explicit exceptions and run under `-O`.

## Sources, scope and limits

Scientific base is canonical main `b91956876e5b4122fd89179f1b57557ff8378f15`,
priority revision 7. The rank-shape card was proposed with seed
`b139e45c9b653201499030c31dc4fe8f`. This changes its historical decoder premise
to the concrete carried-swap representation, with that change recorded in
[TASK.json](TASK.json). [SOURCES.json](SOURCES.json) pins the selected context,
card and exact retained inputs. `inputs/ORIGINS.json` maps every unchanged
predecessor file to the public PR4971 head and SHA-256; these bytes are committed
locally before the new analysis so replay needs no side-branch Git history or
network. The main-tree #4948 source word is the same compressed payload, retained
as provenance. This checkout is shallow; full-history ancestry audit is not claimed.

A region is an identity-map zero-edge component in the SOURCE graph, and its
internal identity edges must remain zero. The theorem changes charts on at most
two intact free regions. It keeps the owned-center copy/query/clear boundaries,
scalar dependencies, field exchanges and start/end charts fixed. It does not
exclude a larger simultaneous change, splitting regions by new paid transitions,
nonmonotone transports, changed centers, changed native operators or a new
scalar word. No target credit, complete supplier, fixed-tape implementation,
completion/compiler extension, BIT/outer transfer, Lean proof, human review or
higher κ is supplied. The inherited physical phase premises remain explicit.

Initial exploratory scripts also found the smallest-frame chronology fragments
the paid calls and loses moment. Those temporary scripts and floating comparisons
are not certificate dependencies or claims of optimality. The committed result
uses exact enumeration and written all-exponent inequalities only.

## Open next questions

Try one fully specified interaction among at least three intact free regions,
or change the scalar dependency graph or split a region with a charged new
transition. First check exact containment and the full affected-edge histogram;
then lower a positive candidate physically with absolute phases, arbitrary-input
returns and every scalar/movement/precision cost. A new graph optimum would
still need complete supplier and outer accounting. Structured first steps and
blockers are in TASK.json. The present result gives no reason to rerun broader
one/two-region searches on the same source.

## Credit

Prepared by Cinna Davis / 1337isnot1337 with substantial OpenAI Codex assistance;
solo, no subagents, no independent human review. Apache-2.0. Credit Dugongue for
PR4971's changed word, construction and replay, and PR4935/4948 source binding;
Cao Yifan / intqwq for the round-three source beyond PR4610; the Cinna Davis
scalar/helper and PR4440/4470 lineage; zxv, Jacob Alan Sussman and all authors in
the unchanged retained NOTICE. Credit James Reed / jwr404 for #4571's
operator/frame gap, #4979 for its exact event guard, and James Reed's independent
PR4971 review. Existing fixed-eight-array and monotone-frame obstructions are
distinct precedents, not global barriers applied to this changed graph.
