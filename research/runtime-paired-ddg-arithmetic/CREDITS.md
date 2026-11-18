# Sources and attribution

Ali Romman supplied the runtime-parameter construction, shared residue
arithmetic, full gate bill and complete checks, with substantial OpenAI
Codex assistance in research, implementation, verification and writing.
New code and prose are Apache-2.0.

Nick Petalas supplied the fixed-pair arithmetic circuit and explicit
runtime-parameter question in
[PR #7746](https://github.com/CrocSwap/integer-mult-bounds/pull/7746), head
`71fdb2cf1ec973b5402c4d3c2466864014a1ccda`. Its
[circuit](https://github.com/petalas/integer-mult-bounds/blob/71fdb2cf1ec973b5402c4d3c2466864014a1ccda/research/paired-ddg-arithmetic-step/circuit.py)
supplies the unchanged Boolean primitives and modular addition. Its
[proof](https://github.com/petalas/integer-mult-bounds/blob/71fdb2cf1ec973b5402c4d3c2466864014a1ccda/research/paired-ddg-arithmetic-step/PROOF.md)
supplies the shared phase and compute-copy-swap-uncompute method. The new
subclass changes only the wire layout and allocation bound; no source
global or function is replaced. All seven source package files are retained,
and the original fixed-pair verifier runs unchanged.

zxv, with substantial OpenAI Codex assistance, supplied the complete paired
decision graphs, probability law and expected-bit optimum in
[PR #6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072), head
`9011bf83e85ecd0443c789cf03259442f750877d`. Its
[constructor](https://github.com/zxv/integer-mult-bounds/blob/9011bf83e85ecd0443c789cf03259442f750877d/research/paired-residue-sampler/verify.py)
and [proof](https://github.com/zxv/integer-mult-bounds/blob/9011bf83e85ecd0443c789cf03259442f750877d/research/paired-residue-sampler/README.md)
are retained. The unchanged constructor runs for all 144 pairs. The original
full probability/mean catalogue entry point was not run. Its classical DDG,
JoyboyBrian inverse and Nick Petalas stochastic-prefix credit remains intact.

JoyboyBrian, with substantial OpenAI Codex assistance, supplied the inverse
and counter-based lifecycle context in
[PR #6102](https://github.com/CrocSwap/integer-mult-bounds/pull/6102), head
`0422af13625c2e7e8ece28bdd74364a61764c64a`. Its
[proof](https://github.com/JoyboyBrian/integer-mult-bounds/blob/0422af13625c2e7e8ece28bdd74364a61764c64a/research/paired-ddg-reversal/PROOF.md)
and README are retained. Its complete suite was not run and its physical
counter obligations are not discharged by a circuit step.

Related work, not executable input: Nick Petalas's
[PR #7187](https://github.com/CrocSwap/integer-mult-bounds/pull/7187), head
`5504be187271a90a3a46e497ed2d5b4196c5df8a`, gives the
[resident table bank](https://github.com/petalas/integer-mult-bounds/blob/5504be187271a90a3a46e497ed2d5b4196c5df8a/research/signed-swap-residue-bank/PROOF.md)
under an output-relabelling contract. It was read for overlap. His
[PR #6127](https://github.com/CrocSwap/integer-mult-bounds/pull/6127) supplies
a different owned-delimiter boundary for the fixed pair. This package does
not claim those earlier table or tape results and does not transfer their
tariffs to the new circuit.

All eleven retained files have Git-blob and SHA-256 pins and keep their
original notices. The base manifest records provenance only; no unmerged
source ancestry is asserted. Separate finite checks do not constitute
independent human or formal-kernel acceptance.
