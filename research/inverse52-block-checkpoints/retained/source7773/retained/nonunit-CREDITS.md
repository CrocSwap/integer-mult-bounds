# Exact sources and attribution

Ali Romman supplied the complementary-tail formulas, ordered column-leaf
selection, two-mode reversible circuit, exact bill and complete-domain
checker with substantial OpenAI Codex assistance in research, implementation,
verification and writing. New material uses Apache-2.0.

Nick Petalas supplied the Boolean primitives, clean-oracle construction
and fixed-pair arithmetic model in
[PR #7746](https://github.com/CrocSwap/integer-mult-bounds/pull/7746), head
`71fdb2cf1ec973b5402c4d3c2466864014a1ccda`. The complete seven-file package
is retained. Its [circuit primitives](https://github.com/petalas/integer-mult-bounds/blob/71fdb2cf1ec973b5402c4d3c2466864014a1ccda/research/paired-ddg-arithmetic-step/circuit.py)
are inherited unchanged with an explicit new wire layout. No source
function or global is patched. Its
[verifier](https://github.com/petalas/integer-mult-bounds/blob/71fdb2cf1ec973b5402c4d3c2466864014a1ccda/research/paired-ddg-arithmetic-step/verify.py)
runs unchanged. Its modulus-169 gate count is prior evidence, not the new
modulus-thirteen bill.

JoyboyBrian supplied the actual inverse residue domain and nonadaptive
numerator window in
[PR #6096](https://github.com/CrocSwap/integer-mult-bounds/pull/6096), head
`e56f5094c83f3e514d9936fa7b1c8027745a0a00`. Its
[domain proof](https://github.com/JoyboyBrian/integer-mult-bounds/blob/e56f5094c83f3e514d9936fa7b1c8027745a0a00/research/inverse-residue-domain/README.md),
[basis and owner constructor](https://github.com/JoyboyBrian/integer-mult-bounds/blob/e56f5094c83f3e514d9936fa7b1c8027745a0a00/research/inverse-residue-domain/verify.py)
and [mode columns](https://github.com/JoyboyBrian/integer-mult-bounds/blob/e56f5094c83f3e514d9936fa7b1c8027745a0a00/research/coded-native-caller/NORMALIZERS.json)
are retained. The bounded-owner functions run for all 384 source pairs;
the full kernel fixture suite does not run. Its Dillon normalizer,
Dugongue/mdumitrean coded producer and inverse lineage stay credited.

Ali Romman supplied the exact entry classification and remaining mixed-tail
question in [PR #7757](https://github.com/CrocSwap/integer-mult-bounds/pull/7757),
head `5640f56b63ea04afc8505d45a4df1ea35466a94e`, with substantial OpenAI Codex
assistance. The [proof](https://github.com/aliromman/integer-mult-bounds/blob/5640f56b63ea04afc8505d45a4df1ea35466a94e/research/inverse52-phase-entry/PROOF.md),
[interface](https://github.com/aliromman/integer-mult-bounds/blob/5640f56b63ea04afc8505d45a4df1ea35466a94e/research/inverse52-phase-entry/interface.py),
guide and credit record are retained. Its first-entry boundary obligation
is not removed by the new inside-tail inverse.

The packed gate interpreter and separate scalar checks adapt Ali Romman's
[PR #7755 verifier](https://github.com/aliromman/integer-mult-bounds/blob/d6babec41a3d01928c3dbdb896ea2adf051ba305/research/runtime-paired-ddg-arithmetic/verify.py),
head `d6babec41a3d01928c3dbdb896ea2adf051ba305`, prepared with substantial
OpenAI Codex assistance. That file is retained for attribution; its full
runtime package is not replayed. The original ordered paired graph and
probability proof are zxv's
[PR #6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072), with
its exact [source guide](https://github.com/zxv/integer-mult-bounds/blob/9011bf83e85ecd0443c789cf03259442f750877d/research/paired-residue-sampler/README.md)
retained. The source notices also credit JoyboyBrian's reversal/lifecycle
work and the original dyadic decision-graph method.

All 19 retained files keep their exact notices and have Git-blob and
SHA-256 pins. The base manifest records provenance without unmerged
ancestry. No global novelty, gate optimum, complete physical supplier,
independent human review or formal-kernel acceptance is asserted.
