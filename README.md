# Dimension-30 follow-up candidate

This branch includes a conditional **kappa = 12649/100000000000 = 1.2649e-7**
follow-up to icekylinx's PR #10, approximately 2.84% above its stated witness.
It combines that controlled batching model with the star rules of PR #9
and the geometric bank-matching extension of PR #11. The result remains
unreviewed and conditional. See the [incremental proof and reproduction guide](research/batched-followup/README.md),
[exact certificate](research/batched-followup/certificate.json), and
[updated manuscript patch](patches/batched-dimension30.patch).
The preceding contribution's documentation is retained below for attribution
and its original parameter witness; the new candidate uses the follow-up files.

# Integer multiplication with a conditional saving beyond 2^-23

\[
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{6149999}{50000000000000}>2^{-23}.
\]

The construction batches large rational projector blocks and whole complex
residuals in the finite networks of [PR #7](https://github.com/CrocSwap/integer-mult-bounds/pull/7).
A controlled common basis, mixed-width recursion, and an arithmetic dependency
path bound supply the stated exponent. The conclusion is conditional on the
retained upstream multiplication framework and the written interface proofs.

## Proof and reproduction

- [Proof note](artifacts/batched-23-note.pdf) and [LaTeX source](notes/batched-23-note.tex).
- [Exact certificate](certificates/batched-network.json): rank moments, guard,
  29 strict constraints, and seven assembly margins.
- [Combined manuscript patch](patches/batched-23.patch) and [application instructions](PATCHING.md).
- [Review guide](docs/research/batched-review.md) and [source provenance](SOURCES.json).

```sh
make verify
make batched-note
```

Verification requires Python 3.11+, a C++17 compiler, Git, and Make. It includes
retained producer checks, the new certificates, regression tests, and patch
application checks. The PDF target requires pdfLaTeX.
For just the new arithmetic and manuscript patch:

```sh
make batched-certificate batched-patch
```

The bit and complex savings are `246/10^9` and `7/10^7`; the precision guard
exponent is `11999/10000`. The final absorption gap is
`362000001/80000000000000000000000 > 0`.
The retained Gaussian input scaling proof uses the corrected enclosure
`F = 2^ceil(1.14 alpha^2)`, with the existing precision `P = 34p`.

## Attribution

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
