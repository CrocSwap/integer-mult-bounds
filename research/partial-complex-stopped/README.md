# Partial complex readouts with whole-projector stopped interchange

This parallel research witness combines a new complex readout schedule with the
stopped product-ring interchange of [PR104](https://github.com/CrocSwap/integer-mult-bounds/pull/104),
applied to [Swapnil Jain's round-seven bit word](https://github.com/Swapnil-jain/integer-mult-kappa/tree/741e7aa078392553815df7926ee17ac5e25a8c38).
The selected **conditional** exponent is

\[
\kappa=\frac{942802139}{10000000000000}=0.0000942802139.
\]

This is 54.47% above `2^-14`. The bit primitive has ordinary saving
`1240183559/10^13`; the complex primitive has saving
`5893637/62500000000`. These are exponent improvements, not practical timing
measurements. The checked finite word and arithmetic do not formally verify
the complete integer multiplication theorem. The source's stage-two bit
reversal and the retained analytic and fixed-tape interfaces remain premises.

The selected value exceeds [PR113](https://github.com/CrocSwap/integer-mult-bounds/pull/113)'s
`469537/5000000000` by `3728139/10^13`, approximately 0.397%.
PR110 independently developed closely related deferred readouts. We use
PR113's composition with PR111 cyclic strip sums, then add partial subframe
selection, full signed-rational adjoint replay, the repaired physical access
closure, and the independent finite kernel audit. This comparison is against
the pinned PR113 witness, rather than a claim of optimality.

The complex producer is the exact cyclic-strip and dual-suffix producer from
[PR113](https://github.com/CrocSwap/integer-mult-bounds/pull/113), pinned at
`0eee4d507092a96bde88de703f07574ba17401a8`. Its sources are PR111's cyclic
strips and [PR108](https://github.com/CrocSwap/integer-mult-bounds/pull/108)'s
dual-suffix pair stars, with their original attribution retained.

The complex change uses the exact signed adjoint of the retained scalar word
to read old scratch directly. A physical event closure computes retained
centers first, preserving all carrier dependencies. We delay 9,356 untouched
scratch readouts to nondegenerate subframes, including alternating frames,
that form a nested chain at every target. Source and sink phases change
together, so every scratch role still receives the required completed tensor
operator. Partial subframes widen auxiliary recursive children without changing
the rank sum. Every endpoint copy and retained-center correction remains paid.

The bit change uses a common rational basis and the opposite-bank factorization
of PR104 for each proper round-seven projector. It replaces fragmented
implementations with a single reversed child of the projector's full rank.
The atom adapters, old ordinary leaves, and final ordinary wrapper are paid.

The larger children require new constants: the explicit scalar toll is
`758385205952` and the simultaneous row reserve is `p^27000`. Reusing the old
scalar or row bounds would not certify this witness. [PROOF.md](PROOF.md)
states the physical and all-size transfers and their inherited assumptions.
[EXPERIMENTS.md](EXPERIMENTS.md) records the broader search and rejected ideas.

The package supplies a portable reconstruction of the matched complex word,
the selected subframes, exact rank and moment checks, signed assembly
inequalities, and an independent Lean kernel certificate. The reproduction
instructions and source manifest are included alongside these files.

## Reproduction

The bundled arithmetic and phase checks need only standard-library Python 3:

```sh
make -C research/partial-complex-stopped verify
```

To rebuild both physical inventories, prepare immutable predecessor checkouts:

```sh
git clone https://github.com/Swapnil-jain/integer-mult-kappa /tmp/kappa-round7
git -C /tmp/kappa-round7 checkout 741e7aa078392553815df7926ee17ac5e25a8c38
git clone https://github.com/icekylinx/integer-mult-bounds /tmp/kappa-pr104
git -C /tmp/kappa-pr104 fetch origin 948ce1510df750f4c18b96bdaef436a86f8bf834
git -C /tmp/kappa-pr104 checkout 948ce1510df750f4c18b96bdaef436a86f8bf834
make -C research/partial-complex-stopped verify-sources \
  SWAPNIL_SOURCE=/tmp/kappa-round7 PR104_SOURCE=/tmp/kappa-pr104
```

The source reconstruction needs a C++17 compiler. It uses temporary build
directories, checks source hashes, rebuilds the matching and exact adjoint,
and binds all selected role supports and the full histogram to the assembly.
The bundled producer is an exact byte copy of PR113's credited source.

For the independent finite Lean checks, with Lean 4.34.1 installed:

```sh
cd research/partial-complex-stopped/kernel
python3 generate.py
lean KernelNew.lean
```

All three printed theorem axiom lists are empty. These checks establish the
finite arithmetic scope described in [kernel/README.md](kernel/README.md).

## Attribution

The bit network is Swapnil Jain's. The stopped product-ring construction and
rational-center producer are icekylinx's PR104. Their dependencies include the
PairedTriple producer, copied-center and complex endpoint work, legal carrier
matching, and the retained OpenAI #109 framework. Original notices and source
attribution are preserved in the imported files. Related concurrent work
includes Rohan Arun's PR107/108/111/113, Avi Eisenberg's PR110, and Rohan
Gupta's dual-suffix strips in PR55. icekylinx's PR115 independently combines
partial source gauges with compatible frame enlargement and cube producers.

The partial complex readout construction, its selection, audits, and packaging
were prepared with OpenAI Codex assistance and GPT-6-sol research agents. New
contributions are under the repository's Apache-2.0 license. This submission
claims no authorship of the predecessor networks or unconditional theorem.
