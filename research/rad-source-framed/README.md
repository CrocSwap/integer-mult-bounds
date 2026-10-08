# RaD source-framed h53 research record

This draft contributes an alternative finite construction and a conditional assembly for review:

$$
T(n)=O(n(\log n)^{1-\kappa})
$$

$$
\kappa=\frac{5834475279233921242758637328164947}{5\cdot10^{39}}\approx1.1668950558467842\times10^{-6}>2^{-20}
$$

The multiplication theorem, computational model and most analytic interfaces are inherited. This package represents a limited contribution within that collective work. It is conditional on the retained assumptions and the linked written transfer arguments. Separate research agents reviewed the finite graph, transfer and exact arithmetic; this is not external human peer review, a formal proof, an unconditional theorem, or a practical multiplication benchmark.

Newer [PR17](https://github.com/CrocSwap/integer-mult-bounds/pull/17) and [PR18](https://github.com/CrocSwap/integer-mult-bounds/pull/18) state larger savings. We do not assert a current-best result, first threshold, global optimality or priority. Their claims are separate and were not independently validated by this publication package.

## Credit and scope of our contribution

The result depends on other authors' work. In particular:

| Author or contributor | Contribution and source | Relationship to this package |
|---|---|---|
| **OpenAI** | Original *Integer multiplication below n log n*, pinned at `adc7f1241b42e322a6451854ab7e4b4c146bf78a` ([original source](../../upstream/README.md)) | Retained multiplication theorem and machine framework; its assumptions remain in force. |
| **Douglas Colkitt** | This repository's finite-network, routing and compact-control development at `6e564879f51ae16f23d392e9e196c605f36d90df` ([compact-control review](../../docs/research/compact-control-review.md)) | The principal inherited construction and movement interface, including exceptional-address repair and distinct bit/complex arities. |
| **eumemic** | Auxiliary source-frame lemma and basis extension in [PR13](https://github.com/CrocSwap/integer-mult-bounds/pull/13), pinned at `3ef246fa4f69c87ebfed78376418afa9ffcad145`; earlier complex compression, resampling and centers in [PR3](https://github.com/CrocSwap/integer-mult-bounds/pull/3), [PR5](https://github.com/CrocSwap/integer-mult-bounds/pull/5), [PR6](https://github.com/CrocSwap/integer-mult-bounds/pull/6) | The final nonzero auxiliary-source mechanism is explicitly adopted from PR13. Its stated substantial Claude assistance is retained in this attribution. The other PRs are credited predecessor work. |
| **icekylinx** | Contiguous recursive batching, whole complex residuals, mixed-width transfer and dependency-path precision in [PR10](https://github.com/CrocSwap/integer-mult-bounds/pull/10), pinned at `62691e395a0458ce089a1c7b5d89e74291e95e29` | Closely related batching/transfer framework is credited. Our common ambient isometry and separately reviewed tape/precision arguments do not import PR10's controlled-corner basis or its ternary producer. |
| **Bortlesboat** and **dleen** | Aligned pairing in [PR2](https://github.com/CrocSwap/integer-mult-bounds/pull/2); retained totals, shared exclusions and stage sharing in [PR4](https://github.com/CrocSwap/integer-mult-bounds/pull/4) | Predecessor finite-network and register-sharing contributions in this research lineage. |
| **Zhihao Chen (jacklightChen)** | Ternary five-subset networks and paired producers in [PR7](https://github.com/CrocSwap/integer-mult-bounds/pull/7), pinned at `6725c6a17b17871a35353fd29157f4ed851bc114`; nested basis in [PR16](https://github.com/CrocSwap/integer-mult-bounds/pull/16) | Important parallel/predecessor work, explicitly credited. Our selected circuit is a binary triple network; neither their ternary producer nor the later nested basis is imported into this witness. PR7 records substantial GPT-6 Astra assistance. |
| **Rohan Arun (rohanarun)** | Geometric/dimension/matching development in [PR8](https://github.com/CrocSwap/integer-mult-bounds/pull/8), [PR9](https://github.com/CrocSwap/integer-mult-bounds/pull/9), [PR11](https://github.com/CrocSwap/integer-mult-bounds/pull/11), [PR12](https://github.com/CrocSwap/integer-mult-bounds/pull/12), and data corners/composition in [PR14](https://github.com/CrocSwap/integer-mult-bounds/pull/14), [PR17](https://github.com/CrocSwap/integer-mult-bounds/pull/17) | Related and stronger contemporary work; those producers and data-corner refinements are not imported here. |
| **Aurel Prosz (Paureel)** | Exact parameter and fixed-exponent analysis in [PR1](https://github.com/CrocSwap/integer-mult-bounds/pull/1) | Predecessor parameter-analysis contribution, acknowledged separately from this independently replayed certificate. |
| **David Harvey and Joris van der Hoeven** | [Integer multiplication in time O(n log n)](https://www.texmacs.org/joris/nlogn/nlogn.pdf), cited by the retained upstream audit | Analytic multiplication/FFT/Gaussian background in the inherited chain. |

Our limited contribution is the searched and separately checked **h53 binary triple graph with R=529181**, actual-frame controller-chain cloning and allocation, a constructive **common rational ambient metric-isometry** that makes three disjoint boundary families eligible for long recursive runs, the **h28/R88377 shared complex construction**, and their reviewed tape/resampling/precision composition. The source-frame step uses eumemic's lemma on this different graph. No ownership of the inherited theorem, source-frame idea, or whole-residual batching is claimed.

## Reproduce the arithmetic package

Use Python 3.10 or newer; the portable entry point uses only the standard library:

```sh
python3 research/rad-source-framed/verify.py
```

Or run `make rad-source-framed-check`. An optional `--output /fresh/path/result.json` retains a new replay record. The check hashes the copied inputs and sources, reconstructs the physical budget, recertifies all three native variants and the complex phase saving with outward rational logarithms, and compares all twelve complete assembly rows to the separately produced certificate. It also checks the preserved predecessor summaries.

This is an **arithmetic replay**. It does not replay the 86 million finite coefficients or materialize the gigantic common basis, native table or eligible odd prime. The compact normal input is an explicitly documented extraction from the original full case; it is not a replacement for that case. Full finite checks, proof arguments, source, protocols and whole gzip evidence are recoverable from the pinned [RaD record](https://github.com/hipotures/rad/tree/45d9b60355872041f9275f77c057514def0d45bc/research/integer-multiplication-bounds), [reproduction instructions](https://github.com/hipotures/rad/blob/9d4bed0f4c99760a1d545f5a72fb21faff6cecfb/research/integer-multiplication-bounds/reproduce.md), and [artifact manifest](https://github.com/hipotures/rad/blob/9d4bed0f4c99760a1d545f5a72fb21faff6cecfb/research/integer-multiplication-bounds/artifact-manifest.json). `provenance.json` pins every copied input, proof and source.

`code/` preserves the original reviewer files unchanged. Their historical standalone main functions reference the original campaign workspace. Use the fresh portable `verify.py` for this package; full historical replay must follow the pinned RaD protocols and recovered full inputs.

## Review the mathematical transfer

Start with [the derivation and dependency guide](notes/derivation.md). The final parameters use bit saving `583448208746222253/(5*10^23)`, complex phase saving `7/(5*10^6)`, `beta=1/8`, and joint row stock `p^123000`. All native bit wrappers remain charged at the bit exponent. The complex phase saving is not silently substituted for their runtime.

The numeric balanced-row cutoff `log2(b_input)>=258254417031933722624` only covers the explicit checked parameter thresholds. Native layout/alphabet constants, a constructively specified but unmaterialized basis/table/shared prime, complete record domination, strict absorption and the retained upstream-machine thresholds remain separately eventual. This does not make the algorithm practical at that cutoff.

This is a standalone **draft research-review package**, rather than a replacement of the current release manuscript and certificate. A combined manuscript integration patch is not supplied in this draft. Its result and proof boundary should be reviewed before any such integration. `upstream/` remains unchanged. Existing Apache-2.0 attribution is retained; see [NOTICE](NOTICE).

The campaign clock ran from 2026-10-07T22:25:21Z to the user-extended 2026-10-08T10:00:00Z deadline. Subsequent work prepared and checked this publication package without reopening mathematical searches or changing the witness.

Analysis and pull request prepared with Codex and GPT-6.1-Sol Ultra.
