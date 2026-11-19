# Sources and credit

Ali Romman (@aliromman) prepared the direct-residue finite-window circuit,
the telescoping depth word, exact bill and checks with substantial OpenAI
Codex assistance. New material is Apache-2.0. No independent human or
formal proof-kernel acceptance is claimed.

Nick Petalas (@petalas) supplied the Boolean primitives, clean-oracle
construction and fixed-pair model in
[PR #7746](https://github.com/CrocSwap/integer-mult-bounds/pull/7746).
His [circuit](https://github.com/petalas/integer-mult-bounds/blob/71fdb2cf1ec973b5402c4d3c2466864014a1ccda/research/paired-ddg-arithmetic-step/circuit.py)
and [verifier](https://github.com/petalas/integer-mult-bounds/blob/71fdb2cf1ec973b5402c4d3c2466864014a1ccda/research/paired-ddg-arithmetic-step/verify.py)
remain byte-exact with the full seven-file package. The verifier runs
unchanged. The new twelve/thirteen-bit operations follow the same
full-adder identity under separate names; no source routine is patched.
Compute-copy-uncompute and ripple arithmetic are classical methods.

JoyboyBrian (@JoyboyBrian) supplied the
[actual source-domain proof](https://github.com/JoyboyBrian/integer-mult-bounds/blob/e56f5094c83f3e514d9936fa7b1c8027745a0a00/research/inverse-residue-domain/README.md),
[basis and owner functions](https://github.com/JoyboyBrian/integer-mult-bounds/blob/e56f5094c83f3e514d9936fa7b1c8027745a0a00/research/inverse-residue-domain/verify.py)
and [mode columns](https://github.com/JoyboyBrian/integer-mult-bounds/blob/e56f5094c83f3e514d9936fa7b1c8027745a0a00/research/coded-native-caller/NORMALIZERS.json)
in [PR #6096](https://github.com/CrocSwap/integer-mult-bounds/pull/6096).
All 2,704 bounded-owner witnesses are checked. The full kernel fixtures
are not run. Dillon's normalizers, Dugongue/mdumitrean's coded producer
and the earlier native/inverse lineage remain credited in the retained
source notices.

zxv (@zxv) supplied the ordered paired graph and its floor-count law in
[PR #6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072).
The [source guide](https://github.com/zxv/integer-mult-bounds/blob/9011bf83e85ecd0443c789cf03259442f750877d/research/paired-residue-sampler/README.md)
is retained unchanged. The dyadic decision-graph method and its
probability proof are credited classical inputs, not new sampling theory.

Ali Romman's [PR #7757](https://github.com/CrocSwap/integer-mult-bounds/pull/7757)
supplied the [prefix/tail collision and entry classification](https://github.com/aliromman/integer-mult-bounds/blob/5640f56b63ea04afc8505d45a4df1ea35466a94e/research/inverse52-phase-entry/PROOF.md)
and [unchanged four-coin prefix](https://github.com/aliromman/integer-mult-bounds/blob/5640f56b63ea04afc8505d45a4df1ea35466a94e/research/inverse52-phase-entry/interface.py).
Four notes and interface files are retained. All 43,264 four-coin source
outputs are compared. The complete phase-entry suite is not rerun.

Ali Romman's [PR #7760](https://github.com/CrocSwap/integer-mult-bounds/pull/7760)
supplied the [remaining prefix/return handoff](https://github.com/aliromman/integer-mult-bounds/blob/2a79ceb497c8b76a44cd3a9f706becdf9bbb8b7a/research/nonunit52-tail-circuit/PROOF.md).
Its proof, guide and credit record remain intact. Its specialized tail
circuit is not called or compared as a matched physical implementation.
The packed and scalar interpreters follow Ali Romman's
[PR #7755 verifier](https://github.com/aliromman/integer-mult-bounds/blob/d6babec41a3d01928c3dbdb896ea2adf051ba305/research/runtime-paired-ddg-arithmetic/verify.py)
and the retained Nick Petalas checker. The full runtime suite is not run.
All these source contributions retain their stated AI assistance.

SOURCE-PINS.json authenticates all 21 retained files; SOURCES.json records
canonical-main provenance. Source pins do not assert ancestry. No global
literature priority, gate optimum, minimum space or complete physical
supplier is claimed.
