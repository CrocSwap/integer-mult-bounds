# Arbitrary four-transfer signed connectors reduce to the unit class

**Scoped theorem; no new kappa.** In the fixed signed 3x3 connector, exactly
12 ordinary signed child queries and four nonzero one-way transfers force every
transfer coefficient to be +1 or -1, even when coefficients may be arbitrary
complex numbers. The six operator ports are also forced:
B0/B1/A2 use w, and B2/A0/A1 use z.

This closes the explicit nonunit-coefficient exclusion in Ross Richardson's
[PR1682](https://github.com/CrocSwap/integer-mult-bounds/pull/1682).
It extends the domain of the existing port/tariff theorem. It does not repeat
its 7,257,600-trace unit census or claim a new circuit construction.
The practical consequence is that choosing nonunit transfer coefficients cannot
move expensive children to cheaper ports or lower the fixed complete additive tariff.

[PROOF.md](PROOF.md) states every hypothesis, the all-input reduction and the cost
boundary. A six-vertex/two-leaf cube argument proves the inherited one-root obstruction
without a census. The new coefficient observation is that a reader's nonzero source coefficient
forces one transfer pair to be unit, while full root restoration forces the other pair.
Arbitrary dirty roots, immutable sources, unread outputs, two roots, four transfers,
ordinary +/-1 queries, one-way transfers, and uniform arbitrary linear maps are material.

## Reproduce

```sh
python3 -I -B research/nonunit-signed-connector-rigidity/verify.py
```

Expected status: `PASS_NONUNIT_SIGNED_CONNECTOR_RIGIDITY`.
The exact receipt has 192 linear systems, 48 unique unit solutions, 720 one-root
walks, 344 signed visited sets, 17 rejected program mutations, and two valid
controls outside the stated class. `VERIFY.json` also registers the optimized replay.

Validation uses different models:

- Generic rational Gaussian elimination and a two-difference closed formula check the unbounded coefficient reduction.
- Event permutations and cube-state dynamic programming agree on the complete one-root finite domain.
- A free noncommutative symbolic interpreter checks the credited witness and inverse.
- Separate 16x16 block-matrix composition checks all dirty basis columns with noncommuting, including singular, maps.
- Scaled ordinary queries allow four half-unit transfers; six transfers allow an extra nonunit identity pair. Both controls preserve the target and violate a named hypothesis.

The universal statement depends on the written program-to-equation argument.
These finite checks are not a proof-assistant or full multiplication theorem.
The implementations are separate models written by the same AI assistant;
independent human review is not claimed. The map interpreters treat each Ai/Bj as an atomic complete child; internal scratch
restoration is an explicit interface hypothesis, not rechecked child code.
Physical hosting, precision, tape costs,
selected supplier admission, and the outer multiplication argument remain separate.

## Credit and sources

Ross Richardson: PR944 signed target/one-root obstruction, PR1651 four-transfer
witness, and PR1682 unit-port theorem. Charles Bethin: PR1637 twelve-query dirty-root
interface. Cinna Davis: PR1675 shorter bidirectional-transfer obstruction.
The source heads and relevant hashes are in `PREDECESSORS.json`; no predecessor
package is modified or re-vendored. The selected main provenance is in `SOURCES.json`.
Substantial OpenAI Codex assistance covers derivation, implementation, verification,
and writing. Apache-2.0. No selected-frontier change.

## Open next questions

`TASK.json` records the next questions and blockers. Additional queries, more
transfers, or bidirectional transfers need their own complete cost comparison.
Physical application requires a concrete selected-supplier seam before implementation.
