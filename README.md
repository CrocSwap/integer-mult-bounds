# Conditional multiplication saving 1.3001411 × 10^-5

Near-balanced bit dimensions **(33,31,34)** and two compatible A1 blocks give
**κ = 13001411/10^12 = 1.3001411 × 10^-5** in `O(n (log n)^(1−κ))`,
under the documented mathematical and fixed-tape hypotheses.

See the [construction and reproduction guide](docs/research/near-balanced-bit.md),
[proof extension](notes/near-balanced-bit.tex), and
[exact certificate](certificates/near-balanced-network.json).
Run `make near-balanced-producer near-balanced-certificate` or `make verify`.
The inherited PR27 and earlier contributions follow.

# Conditional multiplication saving 1.19720853 × 10^-5

This branch composes PR24's endpoint-gauge bit interface with PR23's semantic
precision and bulk assembly, retaining PR21's complex circuit. It gives
**κ = 119720853/10^13 = 1.19720853 × 10^-5** in `O(n (log n)^(1−κ))`,
under the documented mathematical and fixed-tape hypotheses.

See the [dependency argument and reproduction commands](docs/research/endpoint-semantic-composition.md),
[proof extension](notes/endpoint-semantic-composition.tex), and
[exact certificate](certificates/endpoint-semantic-composition.json).
Run `make endpoint-semantic-composition` or the full `make verify`.
The contribution creates no PDF. The inherited PR23 record follows.

# Conditional multiplication saving beyond 2^-17

This branch composes the unchanged PR21 finite interfaces with RaD/PR20's semantic precision and bulk resampling arguments, giving **κ=1099/10^8=1.099×10^-5 > 2^-17** under the documented analytic and fixed-tape hypotheses.

See [the composition and reproduction guide](research/semantic-bulk/README.md), [the proof](notes/semantic-bulk-17-note.tex), and [compiled PDF](artifacts/semantic-bulk-17-note.pdf). The original prefix layout suffices. The native graphs remain unchanged. The earlier results below are dependencies.

# Conditional multiplication saving beyond 2^-18

The latest construction on this branch gives **κ=5499/10^9=5.499×10^-6 > 2^-18** in `O(n (log n)^(1−κ))`, under the retained analytic and fixed-tape hypotheses. It translates the middle auxiliary source frames of PR18 and strengthens the independent complex phase interface.

See [the construction, exact parameters and reproduction commands](research/translated-partial/README.md), [the complete proof](notes/translated-partial-note.tex), and [the compiled PDF](artifacts/translated-partial-18-note.pdf). Zhihao Chen (jacklightChen), with substantial OpenAI Codex assistance; preceding attribution is retained in NOTICE.

The PR18 sources and their prior result are retained below as dependencies.

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
