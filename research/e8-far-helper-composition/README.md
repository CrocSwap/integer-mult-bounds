# Far retiming, two complex helper substitutions and exact composition

**Conditional Îº = 200010933894259105209673 / (2 Ã— 10Â²â¶)
â‰ˆ 0.0010000546694712955 > 1/1000.**

This package composes Chafik Boukhalfa's unchanged
[PR378 far-retimed E8 word](https://github.com/CrocSwap/integer-mult-bounds/pull/378)
with two fixed helper substitutions and two nested frame reductions, admits that derived word in Zhihao Chen's
[PR377 compressed nine-stage construction](https://github.com/CrocSwap/integer-mult-bounds/pull/377),
and uses the already verified unsplit R822 bit supplier. Both upstream packages
and the frozen `e8-nine-stage-composition` baseline remain unchanged.

| Quantity | Baseline | This package |
| --- | ---: | ---: |
| Complex local helpers | 783 | 781 |
| Complex live / physical stock | 14727 / 15520 | 14709 / 15500 |
| Complex coarse saving | 999240641319551 / 10Â¹â¸ | 3128299315561 / 3125000000000000 |
| Bit coarse saving | 8128527708459 / (8 Ã— 10Â¹âµ) | unchanged |
| Conditional Îº | 199648631038144442893941 / (2 Ã— 10Â²â¶) | 200010933894259105209673 / (2 Ã— 10Â²â¶) |

The complex supplier still binds. The bit word, its 128 frame changes, 43 helper
reuses, unsplit idle profile, and finite coefficient 56223565806031 are unchanged.
The excess over 1/1000 is exactly 10933894259105209673 / (2 Ã— 10Â²â¶). No new search runs
inside the helper reconstruction; PR378's own full verifier regenerates its
upstream far-retimed certificate.

## Replay offline

```sh
python3 -B verify.py /fresh/output/directory
```

Default sibling dependencies are `../e8-nine-stage-composition`,
`../e8-bit-helper-reuse`, `../e8-bit-seven-stage`, `../nine-stage-complex-e8`, and
`../e8-complex-far-retiming`. The corresponding overrides are `--baseline`,
`--bit`, `--bit-parent`, `--complex`, and `--far`. `SOURCE.json` pins their exact
source manifests and the local witness/replay modules. The package ships
only text; the candidate certificate is regenerated from pinned upstream input.

Use Python 3.12+ with the pinned bit requirements, bash, `sha256sum`, GNU g++
C++17 and Boost. Assertions must be enabled. Apple clang's `g++` alias needs
a `bits/stdc++.h` compatibility shim. Input/output/interpreter paths must have
no whitespace because of the inherited shell entry points. Allow roughly five
minutes for a local full replay.

The default entry point freshly replays a source-bound portable copy of the complete
frozen baseline, the full
PR378 verifier including certificate regeneration, and all source-adapted PR377
checks. The derived work tree records every changed file in `SOURCE-DIFFS.json`;
the source integrity pass is explicitly for the original tree, not its derived
copy. Fresh admission checks both 1021-column dirty scalar maps, gx/gxcore,
950 Clifford frames, 3120 used directed edges, endpoint adapters, exact phases,
72 invocation owner maps, bank assignments, paid profile and finite invoice.

Both complex moment engines and fallback are rerun at the derived saving and
next 10â»Â¹â¸ tick. The unchanged baseline assembly then reruns both bit moments,
all eight counted-bill bootstrap cutoffs, the 47 strict constraints, adjacent
10â»Â²â· rejection and complex-cap rejection. Changed-source, wrong-donor,
self-substitution and retained-helper controls must fail. Expected values are
comparisons, never substitutes for fresh construction or verification.

## Portable baseline receipts

The frozen baseline hashed the compressed bit-word container in one receipt.
Python 3.12's gzip operating-system byte differs between macOS and Linux; Python
3.13 uses another fixed value. The hosted and local decompressed witnesses and
all mathematical outputs were identical. `baseline_portable.py` verifies all 14
original files, copies them to the output directory, and changes only that
receipt expression to hash decompressed native bytes, its expected receipt
digest, and the copy's manifest. It checks the complete old reference receipt
against the frozen expected digest before deriving the new digest. All original
assertions and controls remain enabled, and the originals are checked again
after the complete replay. `SOURCE-DIFFS.json` exposes both literal changes.

The same portability repair can replay the baseline alone:

```sh
python3 -B baseline_portable.py /fresh/baseline/output
```

This command supports `--baseline`, `--bit`, `--bit-parent`, and `--complex`;
it needs no PR378 dependency or stronger supplier. The derived complex transport
uses `transport.py`: fixed gzip metadata and stored DEFLATE blocks produce exact
bytes independently of the operating system or zlib encoder. The certificate's
canonical decompressed JSON is unchanged. Derived gzip and source-pin hashes
are freshly checked in the full replay.

## Conditional scope

The result retains the explicit PR377 compressed-window and arbitrary correlated
bank-dirt arguments, general Clifford/compiler and local invocation interfaces,
complete-stream routing, common-grid precision, restored rows, recovery and
analytic transfer. The bit side retains its E8 positive-form/rational-routing,
nine-total and signed-decoder admissions. Two-level halving is explicitly charged
on both sides; the internal bit row reserve is separate from the external complex
allowance. There is no new Lean theorem or astronomical cover enumeration.

As in the frozen baseline, the numeric cutoffs concern the counted finite recipe
coefficient. The inherited existence theorem selects a stage-specific C_full
covering primitive, wrapper, row, setup, padding and previous ordinary constants;
no measured universal machine cutoff is claimed. See `PROOF.md` and `NOTICE.md`.
