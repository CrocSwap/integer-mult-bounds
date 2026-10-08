# Integer multiplication with a conditional saving beyond 2^-21

\[
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{7699}{10^{10}}>2^{-21}.
\]

This is **6.26 times** the bulk-recursion witness `6149999/50000000000000 > 2^-23`
of [PR #10](https://github.com/CrocSwap/integer-mult-bounds/pull/10). The
finite networks are unchanged. Two choices change:

- **Auxiliary source frames.** An auxiliary role may start in any fixed frame
  `M`, provided it ends in `I+M`; its endpoint difference is still `I`.
  Every stage-two auxiliary role now starts in the frame `P_{D_0}` of its
  first gate. Its rank-`(h^2-h)` entrance edge disappears and its exit becomes
  one projector of rank `m-h`, compiled as `h` singleton pivots and one
  contiguous block of `m-2h` fields. The rank sum and deficit are unchanged.
  Under PR #10's batched recurrence the interchange saving rises from
  `246/10^9` to **`154/10^8`**.
- **A third complex residual class.** The stage-three data entrances, of rank
  `(h^2-1)(h-1)`, become whole-residual children. PR #10's dependency-path
  guard still allows at most one selected residual per path. The complex
  saving rises from `7/10^7` to `18/10^7`, so the complex network does not bind.

**[Proof note (PDF)](artifacts/source-frame-21-note.pdf)** ·
[source-frame sections](notes/source-frame-bit.tex) ·
[exact certificate](certificates/source-frame-network.json) ·
[combined manuscript patch](patches/source-frame-21.patch) ·
[summary](docs/research/source-frames.md)

The batched construction of PR #10 is described below. The conclusion is
conditional on the retained upstream multiplication framework and the written
interface proofs.

## Proof and reproduction

- [Proof note](artifacts/batched-23-note.pdf) and [LaTeX source](notes/batched-23-note.tex).
- [Exact certificate](certificates/batched-network.json): rank moments, guard,
  29 strict constraints, and seven assembly margins.
- [Combined manuscript patch](patches/batched-23.patch) and [application instructions](PATCHING.md).
- [Review guide](docs/research/batched-review.md) and [source provenance](SOURCES.json).

```sh
make verify
make source-frame-note TEX_ENGINE=tectonic
make batched-note
```

Verification requires Python 3.11+, a C++17 compiler, Git, and Make. It includes
retained producer checks, the new certificates, regression tests, and patch
application checks. The PDF target requires pdfLaTeX.
For just the new arithmetic and manuscript patch:

```sh
make source-frame-certificate source-frame-patch
make batched-certificate batched-patch
```

The bit and complex savings are `246/10^9` and `7/10^7`; the precision guard
exponent is `11999/10000`. The final absorption gap is
`362000001/80000000000000000000000 > 0`.
The retained Gaussian input scaling proof uses the corrected enclosure
`F = 2^ceil(1.14 alpha^2)`, with the existing precision `P = 34p`.

## Attribution

The auxiliary source frames and the third complex residual class are
contributed by **eumemic**, with substantial assistance from Claude (Anthropic).
Bulk recursion and this integration are contributed by **icekylinx**, with
substantial OpenAI GPT-6 Astra and Codex assistance. The finite ternary network
and paired producers are due to **Zhihao Chen (jacklightChen)**. The construction
builds on **Douglas Colkitt**'s compact-control framework and contributions by
**Bortlesboat**, **eumemic**, and **dleen**; see [NOTICE](NOTICE).

OpenAI's manuscript is pinned at
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`; its files under `upstream/` are
unchanged. The repository and retained source use Apache-2.0; see
[LICENSE](LICENSE) and [upstream/LICENSE](upstream/LICENSE).
Exact certificates and finite tests do not constitute formal verification
of the full multiplication theorem.
