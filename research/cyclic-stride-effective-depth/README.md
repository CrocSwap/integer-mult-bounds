# Cubic precision at arbitrary strides, with no length admission

PR846's clean-tape stride inverse had a precision admission depending on
`log log L`. This package removes that condition. Rounded chain coefficients
become exactly zero after at most `2g+ceil(log2 W)+4` effective levels when
`beta=2^-g` and `W>=2g+8`. The unchanged solver's remaining zero-coefficient
subtree is exactly pointwise rounding, so its original output and 40L
traffic bound are preserved. An optional early-exit version is retained
for direct comparison and charged at 44L, including head returns.

Combining that result with PR862's existing common-operator inverse bound
gives **working precision `W<=p+m+9r^3` for every cycle length and stride**,
under the inherited certified prime-power preparation hypotheses. The
input norm is at most `2^m`, and the target error is `2^-p`. Root preparation
has an explicit cubic budget too. The complete proof and cost bill are in
[PROOF.md](PROOF.md).

This is the original clean-scratch tape model. It is separate from PR951's
neighboring-cycle construction without a borrowed data array. It does not
supply bit-reversible arithmetic, physical common labels, transform-level
composition or a multiplication theorem. **No new kappa.**

## Replay

Python 3.11+, standard library only, offline:

```sh
python3 -I -O -B research/cyclic-stride-effective-depth/verify.py
python3 -I -O -B research/cyclic-stride-effective-depth/test_package.py
```

The expected marker is `PASS_CYCLIC_STRIDE_EFFECTIVE_DEPTH`. The default
replay checks the manifest, 12 retained source SHA256/Git objects, local
module bindings and every field of the recomputed receipt. `--out` writes
a fresh external copy after comparison. `--bindings-only` checks package
bindings. `--write` is explicit authoring mode, not verification.

Evidence includes 423 array comparisons, 90 scalar coefficient paths,
300 original kernel cases, 64 actual cubic-budget kernel executions,
216 exact integer budget rows, three nonnegative polynomial identities,
54 admission checks, 1,545 logarithm boundaries, 12 new mathematical controls, four inherited controls,
12 zero-base checks and 33 tape-traffic cases through length 131,072.
Finite checks and the written all-size argument are distinct.

The original PR846 solver and checker, its five PR628 inputs, and PR862's
proof and notice are retained unchanged. [SOURCE-PINS.json](SOURCE-PINS.json)
and [NOTICE.md](NOTICE.md) identify their exact versions and contributions.
