# Unsplit R822 bit supplier with the compressed nine-stage complex supplier

**Conditional κ = 199648631038144442893941 / (2 × 10²⁶)
≈ 0.0009982431551907223.** This is greater than 1/1024.

This additive package composes the R822 seven-stage bit word
from [PR376](https://github.com/CrocSwap/integer-mult-bounds/pull/376) with the
unchanged compressed nine-stage complex construction from
[PR377](https://github.com/CrocSwap/integer-mult-bounds/pull/377). It reconstructs
both suppliers afresh and checks their common assembly interface. It introduces
no new local word, frame selection or helper selection. Its new bit profile pays
the full rank-34 and rank-28 idle projector gaps, replacing the decompositions
34 = 27 + 7 and 28 = 27 + 1. Exact all-port geometry and a charged two-level
restored-row bound certify this change.

| Quantity | Value |
| --- | ---: |
| Bit coarse saving | 8128527708459 / 8000000000000000 |
| Complex coarse saving | 999240641319551 / 10¹⁸ |
| Binding supplier | Complex |
| Bit dimension / live stock | 56 / 10794 |
| Complex dimension / live stock | 73 / 14727 |
| Bit finite coefficient | 56223565806031 |
| Outer η / β | 10⁻²⁴ / 10⁻⁹ |
| Finite bootstrap steps / assembly grid | 8 / 10⁻²⁷ |

PR377 alone used the older fixed PR361 bit supplier. The contribution here is
the source-bound composition and an unsplit idle-child bit construction. With the original
PR373 bit word and the same nine-stage complex supplier and assembly parameters,
κ would be 483630502007744002880417 / (5 × 10²⁶), approximately
0.000967261004015488. The default replay computes this comparison as well: the
128 frame changes and 43 helper reuses improve the available bit saving.
Using the split R822 profile with PR377 gives the verified fallback
κ = 990900380113016169436889 / 10²⁷. The new unsplit profile lifts the bit
saving above PR377's complex saving, so the complex side now limits the result.

## Reproduce offline

From this directory:

```sh
python3 -B verify.py /fresh/output/directory
```

Default dependencies are unchanged sibling directories `../e8-bit-helper-reuse`,
`../e8-bit-seven-stage`, and `../nine-stage-complex-e8`. Exact commits and manifest
hashes are in `SOURCE.json`. The options `--bit`, `--bit-parent`, and `--complex`
accept identical copies elsewhere. Assertions must be enabled. Use Python 3.12+
for the pinned full bit recipe, with its numpy, mpmath and sympy dependencies,
bash, `sha256sum`, GNU g++ with C++17, and Boost. Apple clang's `g++` alias needs
a compatible `bits/stdc++.h` include shim. The inherited bit shell requires
interpreter, input and output paths without whitespace; the wrapper rejects them.

The verifier runs both complete original entry points, including PR376's full
PR373 replay. It then runs exact unsplit geometry for all 120 ports, native
1542-column scalar checks and 12 omission controls, literal banks, dual bit
moments and a source-bound finite adapter. The adapter changes only the
half-shrink guard and explicit internal row-depth charge, retaining all
original route and finite-cost assertions. It then binds the emitted complex template, paid profile and finite
invoice, reruns both exact complex moment engines with the fallback envelope,
and checks the next 10⁻¹⁸ complex point is rejected. It independently reruns both
bit moment engines, all eight finite bootstrap cutoffs and all 47 assembly
inequalities; the adjacent 10⁻²⁷ assembly point and complex leaf cap are rejected.
All parent source files remain unchanged. Stored receipts are comparison values,
never substitutes for fresh checks. The final `RECEIPT.json` has no machine paths
or timing fields. Allow several minutes for a complete local replay.

## Scope

This is a conditional composition, not an unconditional integer multiplication
theorem. PR377's compressed-window lift and arbitrary correlated bank-dirt
composition use its explicit mathematical argument, not a new Lean proof.
Its rank-48 children in dimension 73 require its checked two-level halving
model; no one-level half-rank condition is asserted. The bit side likewise uses degree two, 56² > 2·34², and explicitly charges
6274w⌈log₂(max(2,n))⌉ restored internal rows plus the inherited leaf reserve.
These internal rows are separate from the complex external reserve 20161.
The adapter preserves all
endpoint, final `X_q`, cover `X_delta`, padding, owner and scalar checks.

PR376's nine retained totals at h = 8, rational E8 routing/positive-form bank
extension, source527 lowering and signed-integer-decoder admissions remain.
Both suppliers retain their local theorem, Clifford/compiler, complete-stream
tape, common-grid precision, row allowance, recovery, prime supply and analytic
transfer interfaces. There is no new Lean kernel build, astronomical cover
enumeration, E8 certificate-producer regeneration or signed E8 integer decoder.
See `PROOF.md`, `NOTICE.md` and both unchanged upstream packages.

The reported eight cutoff inequalities use the counted finite recipe coefficient.
The inherited finite theorem chooses a stage-specific C_full dominating primitive,
wrapper, row, setup, padding and previous ordinary constants. These are conditional
counted-bill cutoffs, not a measured universal machine cutoff; the existence argument
and asymptotic saving retain that larger-constant interface.
