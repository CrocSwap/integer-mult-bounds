# Conservative outer transfer for completed selected callees

We compose the pending [ordinary-interchange](https://github.com/CrocSwap/integer-mult-bounds/pull/2234)
and [complex-layer](https://github.com/CrocSwap/integer-mult-bounds/pull/2287)
contracts with a concrete outer multiplication caller. Under those contracts,
we derive `O(n (log n)^(1-1/20000000))` with exact binary output.
We retain the original Gaussian resampling algorithms and the nonadjacent
CRT/axis schedule. We leave the selected frontier unchanged.

[PROOF.md](PROOF.md) supplies the dimension extension from PR2287's
`epsilon=997/1000` to `1/40`, matches the actual layer headers and long
records, and follows the signed packing, normalization, error and carry
boundaries through recovery. The narrowest cost margin is
`169711/2000000000000`; its gap above the target is
`69711/2000000000000`. We retain the exact-K transposition cost.

The contribution is this source-bound admission and composition. We do not
claim new FFT, Gaussian, CRT or Kronecker-substitution methods. The callee
authors still need independent review of their proposed all-size algorithms.
We have not executed the full selected suppliers or a complete Gaussian
multiplier, and we have not obtained new formal or human verification.

## Evidence

The local verifier checks:

* 264 Gaussian polynomial products through signed packing, negative
  sign-extension recovery, negacyclic wrapping and output serialization.
* 32 rounded synthetic-convolution executions with the retained physical
  layout model, real coefficient channels, actual per-round truncation and
  packed products. Each fixture incurs nonzero rounding.
* 16,608 padded CRT records with signed multiword payloads, changed widths
  before the inverse and an incorrect update-order control.
* 285 input pairs through both source scales and exact carry/output recovery.
* Exact rational costs and five compressed large-parameter descriptions,
  including one with room for the guard, row/core reserve and prime intervals.

These finite experiments target caller boundaries. We use indexed address
models for the layouts and Python multiplication as the small exact-product
backend; the written time proof uses the named fixed-tape callees. We reuse
Philipp's authenticated physical-layout model. The Gaussian routines and
pending supplier proofs remain named mathematical dependencies.

## Reproduction

Use Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/selected-conservative-outer
```

The hook runs normal and optimized replays. To print a fresh receipt without
writing files, run `python3 -I -B research/selected-conservative-outer/verify.py --emit`.
[RESULT.json](RESULT.json) records the scope and fault controls.

## Open next questions

Review the complete selected-callee proofs and this outer composition as one
dependency chain. Start with the extended dimension domain, complete-field
callee boundaries and the exact word widths after normalization. A second
implementation could execute the Gaussian caller at feasible test dimensions;
it would need rigorous phase and Gaussian approximations, not floating-point
agreement alone. [TASK.json](TASK.json) records concrete review steps.

Jose Manuel ([jmbarrancoml](https://github.com/jmbarrancoml)) prepared this
contribution with substantial OpenAI Codex assistance. [NOTICE.md](NOTICE.md)
retains predecessor credit. We coordinate through
[Discussion2291](https://github.com/CrocSwap/integer-mult-bounds/discussions/2291).
