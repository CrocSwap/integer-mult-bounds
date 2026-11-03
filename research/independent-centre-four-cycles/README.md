# Independent four-cycles keep a sharp positive paid cost

Every induced four-cycle in the fixed retained 640-input centre graph raises
the complete paid moment by at least

    2(1 + 7^theta - 8^theta) > 0,   0<theta<1,

when its four empty charts move independently to nontrivial one-transvection
neighbours and every helper target stays fixed. One cycle and one label
assignment attain the bound for every such theta. The internal graph's only
connected four-vertex blocks are 716 paths, 160 claws, and 62 four-cycles.
PR6336 prices the paths and the claws. This certificate prices the cycles.

This is a **scoped proof with an exact finite certificate**. The selected
frontier remains κ = 781451/250000000 from PR6030. No supplier is admitted.

## Result and predecessors

[PR6336](https://github.com/CrocSwap/integer-mult-bounds/pull/6336) proves the
tree bound `3 - 2^theta + 7^theta - 8^theta` and leaves the 62 induced
four-cycles unpriced. Its first open question asks whether one of those cycles
can improve the same fixed-graph invoice. This package answers that question:
the cycle prefix floor is `(2,2,2,2,2,2,2,0,0)`, strictly above the tree floor
on prefixes 2 through 7, and the paid moment is strictly positive. The cycle
on vertices `10875,10876,10898,10899`, with label 59 at each vertex, attains
the bound. Its paid-histogram change is `{0:-2,1:2,7:2,8:-2}`. The four
internal edges stay at rank 0. Eight external edges move, as listed in
[PROOF.md](PROOF.md). All 408 helper targets and the zero independent centre
reward stay fixed.

The tree argument is the published predecessor. This checker loads its pinned
`geometry.py` for the census, the adjacency walk, and literal frame rank. It
does not import that package's verifier, and it does not modify predecessor
files. The cycle partition and the fixed-endpoint transform live here.

[PR6306](https://github.com/CrocSwap/integer-mult-bounds/pull/6306), by Nick
Petalas, is the three-contact theorem that PR6336 extends. Chris R /
Clear1nsight's [PR4867](https://github.com/CrocSwap/integer-mult-bounds/pull/4867)
and [PR4888](https://github.com/CrocSwap/integer-mult-bounds/pull/4888) supply
the retained graph. unpaidmoon's
[PR6289](https://github.com/CrocSwap/integer-mult-bounds/pull/6289) posed the
independent-chart question. Dugongue's
[PR5693](https://github.com/CrocSwap/integer-mult-bounds/pull/5693) and the
restricted-Gaussian identity coframes of
[PR5698](https://github.com/CrocSwap/integer-mult-bounds/pull/5698) are
different contracts: conjugation and transports, and identity-versus-original
coframes on another word. They are not reused as hypotheses or as search
alphabets.

The certificate visits all 62 induced cycles and all nine capped-rank tariffs.
Componentwise minima are `(2,2,2,2,2,2,2,0,0)`. One cycle meets that vector,
and the named label tuple meets it simultaneously.

Family status, revision 8, treats a local geometry obstruction as a place to
stop unless a changed producer still has a fully charged consumer. Paths,
claws, and cycles are now all priced, and each raises the paid side. This
package stops there.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -W error -B research/independent-centre-four-cycles/verify.py
python3 -W error -O -B research/independent-centre-four-cycles/verify.py
python3 -B scripts/research_package.py --package research/independent-centre-four-cycles
python3 -B scripts/check_research_commit.py --package research/independent-centre-four-cycles --check-source-history
```

Expected markers are `PASS_INDEPENDENT_CENTRE_FOUR_CYCLES`,
`PASS_REGISTERED_RESEARCH_PACKAGE`, and `PASS_RESEARCH_COMMIT_BYTES`.
`VERIFY.json` registers both complete normal and optimized checks with
180-second limits. Set `TMPDIR` to an existing scratch directory to place the
temporary graph and source-control files there. Optional
`--output /absolute/external/path.json` writes a generated receipt containing
package-file hashes, the prefix floor, and the literal attaining witness.
Writing that receipt inside the checkout is rejected.

The direct checker compares every label pair in widths 1 through 5 with the
paired geometry, 52 four-label products with exhaustive minimization, and 24
of those products with the fixed-endpoint transform. The sharp source cycle is
solved both ways at all nine prefixes. A single-diagonal cost and a
four-distinct-pair cost are included. Five invalid minimizer inputs, three
changed graph contracts, and five source-byte mutations are rejected. One
in-process unary mutation drops the sharp prefix-1 minimum below 2. Proof
checks use explicit exceptions and remain active under `-O`. The
selected-binding orientation passed at the pinned base:
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.

[SOURCES.json](SOURCES.json) pins base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, catalogue revision 8, and every
runtime source. [TASK.json](TASK.json) records the changed task premise.
Generated evidence stays outside the checkout.

## Limits

The optimistic paid moment of this chart contract is strictly higher while the
408 productive targets stay fixed. Unknown native, delivery, and restoration
costs are outside the priced bill, and the paid side is already strictly
worse. The result is specific to this retained graph and to the
one-transvection alphabet. Five-contact blocks, changed routes, and changed
helper targets remain open. No native amplitudes, physical caller, restoration
schedule, rounding, precision or tape proof, compiler closure, selected cold
replay, Lean proof, or outer theorem was run. All five selected framework
assumptions remain. Independent human and formal proof-kernel review are
unclaimed.

## Open next questions

1. Can a five-contact tree, or a changed route or helper target, produce a
   favourable complete bill on this graph? Every connected four-contact block
   is now priced, and each one raises the paid moment under independent
   one-transvection charts, so a larger block is a new endpoint problem rather
   than a missing case inside four contacts. Internal degree is at most 3, so
   the next tree is a longer path or a claw with one extra edge. A changed
   physical mechanism still needs its own endpoints and a complete
   paid/productive bill. Neither object is enumerated here. Family status says
   to stop after this local obstruction; the question stays open because it
   has not been priced.

## Implementation bounds

New loops have finite domains: widths at most 10 in the controls and 1,022
labels on the source, 511 pairs, 16 tag tuples, four-pair search windows,
176 empty-chart contacts, 62 cycles, nine prefixes, and the 34,830-edge source
graph. The fixed-endpoint transform is used on the sharp cycle and on small
products, not on all 62 cycles at all nine prefixes. No recursion is used.
Source-byte hashes are checked before import. The original builder, its two
pinned imports, and the predecessor geometry are unchanged. Each returned
minimizer is checked against its invoice, and every source minimizer is
checked against the incident-edge histogram.

Power-of-Ten rule 3 deviation: CPython and its standard library allocate during
execution. Live collections are bounded by the domains above, with at most
`176*9*1022` unary entries. Temporary outputs have one context-managed
lifetime. Fixed memory pools would require a different runtime. If this
checker becomes a service or accepts a larger graph, add an enforced input
capacity and a separate measured memory budget before widening these bounds.

Rule 8/9 deviation: the authenticated graph builder and the pinned predecessor
geometry are loaded through Python's module loader. Both targets are fixed
pinned files. There is no plugin dispatch. Warning-strict normal and optimized
checks, together with the source and graph mutations, cover that boundary. No
repository-wide tooling change is included.

## Credit

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Credit unpaidmoon / PR6336 for the four-contact census, the tree theorem, and
the cycle question; Nick Petalas / PR6306 for the three-contact theorem and the
paired transform; unpaidmoon / PR6289 for the independent chart question;
Chris R / Clear1nsight / PR4867 and PR4888 for the retained graph and
coherent/pair ceilings; Cinna Davis / PR4694, PR4698, and PR4690 for the
retained-centre interface; Cao Yifan / PR4610 for the native word; David Ganz /
Dugongue / PR4841 for the chart-neighbour framework and PR5693 for the separate
coframe-cut handoff. Binary Lagrangian geometry, min-plus elimination, and
concave summation by parts are classical. The new contribution is the sharp
four-cycle certificate. Predecessor files and notices remain unchanged.
