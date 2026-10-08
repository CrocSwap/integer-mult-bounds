# Conditional final κ = 1099/10^8 > 2^-17

The final multiplication saving is **κ=1099/10^8=1.099×10^-5**, under the documented analytic and fixed finite-alphabet multitape interfaces. It exceeds 2^-17 and is below 2^-16.

This composes our unchanged [PR21](https://github.com/CrocSwap/integer-mult-bounds/pull/21) finite bit/complex interfaces with the semantic precision, arbitrary-coordinate router, phase-cell inverse and bulk resampling constructions exposed by [RaD/hipotures PR20](https://github.com/CrocSwap/integer-mult-bounds/pull/20). [PR19](https://github.com/CrocSwap/integer-mult-bounds/pull/19) independently places partial swaps on a ternary producer; its saving is not additive with ours. Its graph is not imported. Concurrent PR22 refines PR21's numerical slack; this composition retains PR21's conservative bit saving 11×10^-6.

The new contribution is the compatibility proof, **actual** scalar bound G=8702721518400, near-parent-child semantic induction, and **product** row stock for our dimensions. It uses bit saving 11×10^-6 and complex saving 18×10^-6, beta=1/4, C1=1, bit/complex halving depths 494/544, and a joint reservoir bounded by p^89000. The original FFT prefix layout suffices. RaD's graph, old reservoir and gate count are not substituted for ours.

[New proof](../../notes/semantic-bulk-17-note.tex), [compiled PDF](../../artifacts/semantic-bulk-17-note.pdf), [exact certificate](certificate.json). The complete retained finite proof remains [here](../../artifacts/translated-partial-18-note.pdf). Pinned attributed analytic arguments and code are under [references/rad20](../../references/rad20), with their license and source manifest.

## Reproduction and validation

```sh
python3 research/semantic-bulk/verify.py
python3 -m unittest discover -s tests -p 'test_semantic_bulk.py'
# Optional fresh replay of the imported finite transfer controls:
python3 research/semantic-bulk/controls.py --output-dir /fresh/output/directory
make semantic-bulk-note
```

The exact certificate checks **47 positive constraints and seven final margins**, with absorption gap >9×10^-9. Negative controls reject reuse of the old quadratic guard, old separate exposures, and a claimed 2^-16 saving. Explicit compressed integer powers check compact widths, phase-cell separation, row stock, stopping and precision cutoffs. The numeric bound is log2(input-bit-length) ≥ 528959471617; native setup, prime existence, record domination and strict asymptotic absorption retain additional eventual thresholds. This is not a practical cutoff or runtime benchmark.

Fresh imported controls pass: all 4280 small routing address permutations plus 450 larger/boundary probes; 84824 joined bulk output records; four bulk boundary negatives; banded/phase inverse tests against dense rational solutions; 1130200 exact fine-grid halvings; 55180 nested row returns. Balanced-layout controls also pass as a dependency regression, although the new headline uses the original prefix. PR20's original twelve-row arithmetic replay passed separately. None of these controls simulates the full asymptotic Turing machine or constitutes formal verification or external expert review.

The large PR21 finite producers and their endpoint/basis/phase controls are unchanged, validated by source hashes and their existing complete reports. They are not rerun merely to republish a different analytic assembly.

## Credit

**Zhihao Chen (jacklightChen)** supplied this PR21-specific composition and certificate, with substantial OpenAI Codex assistance. The earlier **GPT-6 Astra** assistance attribution remains as recorded; no runtime-model identity is inferred.

Credit **RaD/hipotures** for the new analytic/tape mechanisms and their recorded Codex and GPT-6.1-Sol Ultra assistance; **icekylinx** for PR18 partial swaps and PR10 batching; **eumemic** for PR13 source frames and preceding analytic work; **Zhihao Chen** for PR7/16/21; **Rohan Arun** for PR14/17/19 geometry and composition; and all earlier authors in NOTICE. In particular this is not a claim to have originated RaD's semantic or bulk arguments.

Future research using this contribution should acknowledge **Zhihao Chen (jacklightChen)** and cite the relevant work, together with the other dependencies used. This request adds no license condition. No global priority or optimality is asserted.
