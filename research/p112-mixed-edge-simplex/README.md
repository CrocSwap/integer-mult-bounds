# P112 mixed-edge simplex exclusion

Nick Petalas. Apache-2.0.

The twelve-piece TWOSIDE `(b,t)=(8,4)` profile `4,5^2,6^9` is impossible
over every characteristic-zero field under the piece/code-intersection
hypotheses in [PROOF.md](PROOF.md). This removes one actual profile from
DreamingOfClouds's pinned PR3154 residue. It does not settle the cell, C5,
`C(P112)>=64`, supplier admission or kappa. The selected frontier is unchanged.

The small pieces permit 32 support lines. The quotient basis fits at `52<53`,
but pair supports can reach 72, so the earlier root-only premise fails.
The new finite lemma includes all 128 eligible D7-normal directions as well
as 120 root directions.

```
One normalized non-root edge
  248 projective directions
  58 possible further vertices, 595 compatibility edges
  10,520 seven-cliques, 608 of rank eight
  endpoint support >=182 after 32 arbitrary live-line deletions

All-root branch
  rank-eight root simplex
  endpoint support >=204

Actual nine-endpoint allowance = 9*20 = 180
Contradiction margin >=2
```

The proof explains alphabet completeness, arbitrary characteristic-zero
coefficients, the fixed puncture, common shifts and deletion quantifiers.
`RESULT.json` retains the complete finite histograms and a sharp mixed-branch
relaxation witness. Its one-extra-cut control lowers 182 to 179.

## Reproduction

Python 3.12, standard library only. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p112-mixed-edge-simplex
```

The registered replay runs:

```sh
python3.12 -B research/p112-mixed-edge-simplex/verify.py
python3.12 -B research/p112-mixed-edge-simplex/independent.py
python3.12 -B research/p112-mixed-edge-simplex/test_verify.py
```

Expected final lines include `PASS_MIXED_EDGE_SIMPLEX`,
`PASS_INDEPENDENT_MIXED_EDGE` and `Ran 15 tests ... OK`.
The verifier compares its fresh receipt with the committed `RESULT.json` and
never overwrites it. To retain a fresh receipt, pass
`--output /absolute/external/directory/fresh.json`; the destination must not
already exist or lie inside the checkout.

The live external input is
`research/one-sided-six-multisets/data/data.txt`. Its labels and root ordering
are bound by SHA256 and reconstructed independently of its text. A Git-free
source export needs the entire package and that file at the same relative
path. Direct verifier commands work without Git; generic metadata checks need
Git provenance. `CHECKS.json` records the exact local environment and commands.

The second finite algorithm reconstructs intersections by Gram systems,
joins three- and four-cliques, uses integer row elimination and counts
coordinate equalities directly. It agrees with the primary minor-based,
stack-based, rational-elimination implementation. Both share the retained E8
reconstruction and the written classification premises. These are local
cross-checks, not independent human or proof-kernel review.

## Scope and credit

This takes the concrete C5 handoff in [discussion 3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156),
rather than the catalogue card's proof-assistant task. `TASK.json` records the
changed scope and the boundary/expansion decision. `SOURCES.json` pins main
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6 and exact
retained bytes.

Credit DreamingOfClouds/PR3154 at
`708f0ad8928c383de8294aea3c126e9461d2066d` for the TWOSIDE reduction,
original residue filters and handoff. Credit Nick Petalas/PR3164 at
`857384079ab640a949fb7618b7909664d3e737e5` for the retained geometry and
root-simplex proof, and PR3175 at
`2393963d835a60b8524e986b969c8a87b26a07e3` for the root-star stabilizer
coverage and support-spectrum method. The retained proofs preserve the
E8/P112 decoder lineage and predecessor notices. No frozen input was changed.
Development and local verification used substantial automated assistance.

The Weyl-chamber theorem and original decoder reduction remain explicit
mathematical dependencies. No physical ownership, restoration, consumer,
precision or full supplier invoice is supplied or needed for this scoped
piece exclusion. Such costs are not being declared zero.

## Open next questions

- Can the actual union of one rank-four and two rank-five piece supports
  exclude the adjacent `(7,4)` profile `4,5^2,6^8`? This would advance another
  named remaining cell. First retain that union in the root-only branch;
  arbitrary 32-line deletion is not sufficient to assume a contradiction.
  The blocker is its actual binary-flat support geometry, not another seed
  for the mixed graph. No exclusion of this adjacent profile is claimed here.
- Can the 248-direction alphabet and finite mixed-simplex lemma be formalized?
  This would reduce the proof-kernel gap. First formalize the rational two-ray
  intersection coverage and exact clique receipt, keeping the standard
  Weyl-chamber classification as an explicit assumption until separately
  supplied.

## Implementation bounds

The new code has no recursion. Its graph has 58 vertices; the primary clique
stack has at most 407 pending states and a fail-closed 40,000-state allowance.
Every relevant loop has a finite domain. Rational elimination is at most
8 by 8. Retained inputs are regular files of at most 2 MB.

Python and its standard library allocate during execution, so strict
allocation-free operation is not available. This is a scoped Power of Ten
rule 3 deviation. Fixed inventories, bounded work stacks and matrix dimensions
bound live data; no solver, service or concurrent worker is used. A native
fixed-capacity implementation would be needed only if this becomes a
resource-constrained runtime component. The inherited geometry and original
filter script remain byte-identical; this contribution does not rewrite their
style or expand their input domains. Diagnostics cover all new Python files.
The unittest dispatch is the standard library's bounded 15-test framework,
a scoped rule 9 indirect-call deviation confined to testing.
