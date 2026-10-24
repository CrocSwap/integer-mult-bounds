# Outer routing and Fourier component limits

This package retains three completed component arguments from the October 12 run. It gives no new complete supplier or multiplication kappa.

- Polylogarithmic spectator fields suffice for the retained arbitrary ADDRESS router. Under the inherited full binary-box, equal-width interchange, complete scalar-record, and fixed-tape contracts, the bound remains `O(V p^tau polylog p + poly p)`. This removes the old `epsilon > a` short-width condition.
- For the retained periodic Gaussian sampler, every complete tensor left inverse has infinity norm greater than `2^(d(u/3-1))`. This includes inverses that do not factor by axis. The resulting normalization charge remains `Omega(d*u)`.
- For every odd prime `q`, an explicit polynomial search selects a unit `a` such that every Newton prefix product has magnitude between `2^(-1000 h^3)` and `2^(1000 h^3)`, where `h=ceil(log2(q))`. The accompanying common-carry argument states why one fixed sector gauge does not itself give the missing full convolution supplier.

The written proofs and their historical independent reviews are under `source/`. Finite exact checks support them; those checks alone do not prove the all-size claims. The old canonical-root cost comparisons in the checks are historical diagnostics. They are not publication results. The root choice repairs coefficient conditioning in that component. A complete paid sector-packing method remains absent.

## Source credit and scope

The router inherits the RaD project (hipotures) arbitrary-routing and semantic-bulk interfaces from [PR #20](https://github.com/CrocSwap/integer-mult-bounds/pull/20), commit `4f8d6c8272b5ff307a0da51df545ec3cd96a8b6e`, and RaD commit `45d9b60355872041f9275f77c057514def0d45bc`. The exact source records, license, and notice are in `vendor/references/semantic-bulk/rad20/`. The retained repository source pin is `a900f98be8ff2c09d3292b5112d4731dbd0c8438`.

The Gaussian and Newton arguments use the [OpenAI manuscript](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026) at `adc7f1241b42e322a6451854ab7e4b4c146bf78a`. The Newton/carry source record also credits the [eumemic exact-DFT note](https://github.com/eumemic/exact-dft-bounds/blob/6f87d1a0c9ae462cdcb2034a1361c87623221e66/notes/batched-dft-note.tex) at revision `6f87d1a0c9ae462cdcb2034a1361c87623221e66`. The common-carry proof is `source/cyclic-hybrid/independent/COMMON-CARRY-GAUGE.md`. The historical omnibus proof and its incomplete supplier branches are excluded. Exact inspected files and both Apache licenses are in `source/cyclic-hybrid/sources/`. No contributor identity is inferred from a submitter account. OpenAI Codex assisted the mathematics, checks, reviews, and this extraction. No literature-priority claim is made.

Current-main comparison used `cef4b52f2a59009865bf8eabde1be3f159063703` and the 315 open PR descriptions fetched on 2026-10-22. [PR #3910](https://github.com/CrocSwap/integer-mult-bounds/pull/3910) bounds a forward Gaussian row norm; it does not bound every complete inverse. [PR #647](https://github.com/CrocSwap/integer-mult-bounds/pull/647) supplies an exact-complex-RAM corollary and Newton identities while excluding numerical stability. It does not supply this root-choice conditioning lemma. This is a bounded source comparison, not an exhaustive literature review.

## Reproduce

Use Python 3 with the standard library, assertions enabled, and at least 3 GiB of free space. From this folder:

```sh
python3 -B verify.py --work /absolute/path/to/a-new-directory
```

The last line must be `PASS_LEGACY_OUTER_ANALYSIS checks=6`. The driver checks all frozen input hashes, copies the source, and runs six exact checks. `PORTABILITY.diff` changes only a source-revision receipt lookup: the isolated router reads the frozen revision file instead of invoking Git. The original checker remains byte-exact under `source/`. No mathematical instruction or expected result is changed.

The driver removes `PYTHONOPTIMIZE` from the child-process environment so that child checks and their descendants keep assertions enabled. `OPTIMIZATION-ENV-VALIDATION.json` records a fresh replay with `PYTHONOPTIMIZE=1` and an isolated parent interpreter.

## Open next questions

Can the root choice support a complete fixed-tape cyclic supplier? The first useful step is to supply an exact sector-packing contract and charge all movement and scalar precision. That contract is absent here. Can another sampler avoid the Gaussian inverse charge? A proposed sampler must first give a complete stable inverse under the same arbitrary-input disk interface. This package neither constructs nor excludes such a sampler.
