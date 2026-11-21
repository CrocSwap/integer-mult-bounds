# Reproduce the evidence

Use CPython 3.12 with assertions enabled. The registered suite uses the standard library. Run it from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/single-band-native-carriers
```

Each of the eight checks prints `PASS_NATIVE_SCALE` and its case name. The repository runner then prints `PASS_REGISTERED_RESEARCH_PACKAGE research/single-band-native-carriers outcome=completed`. Each command works from the portable package with its contents read-only. The source loader writes its private files into a temporary directory. [Verification manifest](VERIFY.json) · [Command entry](verify.py)

| Check | What it establishes |
| --- | --- |
| price | Reconstructs both changed circuits. Recomputes the three installations, funded stages, positive allowances, reserves and full outer entrances. Checks 1,060 geometry and precision cases, four positive dispatch boundaries, 100 band-divisibility patterns and four generated 349,526-bit sides. |
| band | Recomputes 90 exact rational flow censuses. Checks ordered simultaneous loans, non-coordinate projectors, nonzero fringe, and a tagged powered source. A rank-323 epoch ran recursively on 128 independent owners, returned to byte 654 from end offset 8,481, read 271,392 bytes and sought through 271,392 bytes. |
| dense | Compares all 2,097,152 dense Gaussian output entries of a finite physical epoch with independent spectral transforms on all 32 input owners. |
| binary | Checks all 636 binary frames, 2,352 projector differences, 44,825 frame instructions and 3,433 private clears. The 36-call word serves 104,904 paid occurrences and returns 18,906 labelled outputs. One- and two-column probes use moduli 3 and 9. A separate rational log/exp enclosure reconstructs both prices from raw source events. Restoring the higher-rate source's old productive cutoff defeats its certificate. |
| grid | Checks 25,146,238 literal products on the actual Gaussian graph. The Gaussian graph has 60,206 distinct scalar literals. Its exact common multiplier is 154113755636630124932500335624192000. |
| atlas | Generates all 2,971 Clifford transports and 104 actual ports. Verifies the absolute phases, 1,944,576 affine and phase basis images, and 6,656 contact values. The 48-call source binds 9,840 main owners and 42,768 helpers. |
| physical | Sends dense Gaussian payloads forward and backward through each of the 21 additional transports. Separately serves all 281,568 returns of the actual 48-call word. That probe has a nonzero helper and 512 nonzero final records. The probe represents its constant spectators and zero fields compactly. The all-input proof and production machine pay for dense arbitrary fields. |
| product | Returns the exact signed integer −345550037539 and the five base-256 digits before carry. The original inputs, their head positions and out-of-interval destination bytes are checked. The two-axis finite test used 157,248 numerical H calls, 138 physical rank-two CRT shuttles and 633,744 padded bytes at their entrances. A separate execution checks all 6,561 cells of the actual post-admission stage body at ternary width four. |

The matched previous and current pack schedules can be compared from a checkout. These comparisons use real coefficient generation, two normalized forward transforms, pointwise products, the opposite transform, true-coordinate extraction, inverse addressing, rounding and carry. Host multiplication and direct digit convolution supply independent expected values after execution.

```sh
python3.12 -B research/single-band-native-carriers/check_product.py
```

| True geometry | Operands | Previous setup / product | New setup / product | Numerical H calls on each |
| --- | --- | ---: | ---: | ---: |
| 9, padded to 16 | signed 120-bit by 120-bit | 2.652 s / 107.851 s | 2.691 s / 108.840 s | 332,904 |
| 3 × 5, padded to 32 | −741503 by 466013 | 0.885 s / 71.412 s | 0.889 s / 90.224 s | 157,248 |

These are single measurements on an Apple-silicon Mac with CPython 3.12. Other verification ran on the same machine. Setup in this table is per-geometry coefficient generation. The two-axis test returned [11811, 10996, 4152, 868, 77] followed by ten zeros before carry. All 138 shuttles on its ordinary production selector were below the first native cutoff. The separate rank-two test in the registered suite ran the physical root receiver on those shuttles. The finite positive path uses the actual elementary H on the small packs. The large all-column word is checked separately. These timings establish execution at the stated geometries. They give no estimate of a production speedup or of a crossover against a conventional multiplier. [Product checks](check_product.py) · [Physical Gaussian replay](check_strong_raw_word.py)

## Kernel checks and dependencies

Use Lean 4.34.1 and the mathlib revision in the Lake manifest. Initialize the pinned dependencies with Lake or use a local cache of that revision. With the matching `lake` in PATH, run the following from the repository root.

```sh
python3.12 -IB research/single-band-native-carriers/verify_formal.py
python3.12 -IB research/single-band-native-carriers/verify_sources.py .
```

The first command builds with warnings as errors, checks the expected declarations and their axioms, and calls `leanchecker` on each of the three local objects. The reported axioms are `propext`, `Classical.choice` and `Quot.sound`. The second command needs the pinned Git objects for the dependency chain. It compares all 158 imported runtime and review members with their original Git content and their recorded SHA-256. The standard portable replay checks the content hashes without Git. [Source bindings](SOURCES.json) · [Core finite-flow and loan mathematics](lean/BandFlow.lean) · [Sieve and all-width space](lean/SquareSieve.lean) · [All fourteen stage prices and three numerical consumers](lean/Profiles.lean)

The Lean kernel checks the finite weighted identities, integer fringe bounds, nested chart return on the formal operator model, sieve indicator inequality, dyadic jump, three full-width stripe inequalities, and the exact funding comparisons. The mapping from Python tapes to the fixed-alphabet model, bounds on sequential visits and bit heights, number-theoretic interval estimates, numerical radius and coefficient recovery depend on the written proofs and named predecessors. No production-dimensional program or multiplier was run. Independent scientific review of the complete argument remains open. [Complete implementation and cost](APPLICATION.md) · [Joint resource calculation](REQUIREMENTS.json)
