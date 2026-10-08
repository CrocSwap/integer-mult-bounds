# Integer multiplication with conditional saving 1.884586e-6

\[
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{942293}{500000000000}=1.884586\times10^{-6}.
\]

This construction extends [PR #10](https://github.com/CrocSwap/integer-mult-bounds/pull/10).
Partial-swap frames remove the source rank penalty. A retained-total triple
producer over the binary field, compatible carrier reuse, positive frames,
and a common rational basis give the selected tensor dimensions `(25,23,57)`.
The paired auxiliary boundary uses five recursive blocks. Whole-residual
batching also improves the retained complex network.

The result remains conditional on the pinned upstream analytic and tape
interfaces. Exact finite calculations support the written construction;
they do not constitute formal verification of the complete theorem.

## Proof and reproduction

- [Current proof](artifacts/partial-swap-note.pdf) and [LaTeX source](notes/partial-swap-note.tex).
- [Exact certificate](certificates/partial-swap-network.json): both moments,
  the precision guard, 29 strict constraints, and seven assembly margins.
- [Producer reconstruction](scripts/partial_swap_producer.py) and
  [finite input data](certificates/partial-swap-input.json).
- [Reproduction instructions](docs/reproducibility.md) and [source provenance](SOURCES.json).

```sh
make verify
make partial-swap-note
```

Verification requires Python 3.11+, a C++17 compiler, Git, and Make.
Selected producer graphs, carrier matches and positive frames are rebuilt
from source in temporary storage. No large binary graph dumps are committed.
For only the current exact arithmetic, run `make partial-swap-certificate`.

The component savings are `188459/50000000000` (bit) and `417/100000000`
(complex). The final strict absorption margin exceeds `4.4822e-13`.
The corrected Gaussian input enclosure from #10 is retained with `P=34p`.

The [#10 proof](artifacts/batched-23-note.pdf) and
[combined manuscript patch](patches/batched-23.patch) remain the inherited
baseline. The new standalone proof supplies the stronger construction and
parameters; the older patch does not contain this extension.

## Attribution

The partial-swap construction and integration are contributed by **icekylinx**,
with substantial OpenAI GPT-6 Astra and Codex assistance. This work builds on
**Douglas Colkitt**'s framework, **Zhihao Chen (jacklightChen)**'s finite network
and paired producers, and contributions by **Bortlesboat**, **eumemic**, and
**dleen**. Original notices are retained in [NOTICE](NOTICE).

OpenAI's manuscript is pinned at `adc7f1241b42e322a6451854ab7e4b4c146bf78a`.
The repository uses Apache-2.0; see [LICENSE](LICENSE) and
[upstream/LICENSE](upstream/LICENSE).
