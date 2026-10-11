# E8 helper reuse and exact assembly refinement

**Conditional κ = 465956978619683677193229 / 500000000000000000000000000
≈ 0.0009319139572393673.**

The increase over [PR373](https://github.com/CrocSwap/integer-mult-bounds/pull/373) is
**7.27277354386458 × 10⁻¹³ and comes entirely from tighter outer assembly parameters**.
The same refinement on PR373's original word gives the same κ. This package also improves
the bit supplier through 128 frame changes and 43 helper reuses, but that component remains
above the unchanged complex bound and does not cause the headline increase.

| Quantity | PR373 | This package |
| --- | ---: | ---: |
| Local helpers | 865 | 822 |
| Bit coarse saving | 968197503705007 / 10¹⁸ | 247970809397543 / (25 × 10¹⁶) |
| Complex coarse saving | 932783231884153 / 10¹⁸ | unchanged |
| Outer eta | 10⁻¹² | 10⁻²⁴ |
| Outer beta | 10⁻⁹ | unchanged |
| Bootstrap steps | 3 | 8 |
| Assembly grid spacing | 10⁻¹⁸ | 10⁻²⁷ |

The bit coarse saving improves by 2.446374%. The helper count drops by 43, with 43 explicit
uncomputes and their inverse cleanup, for 14689 local scalar ADDs. The bit construction uses
seven stages, h = 8, m = 56, nine retained totals, and seven literal replicas. Its W = 10794,
rank mass = 602952, deficit = 1512 and maximum child = 27 < 56/2. Exactly 822 width-56 banks
hold the 7 × 822 rank-8 residuals. No padding or fictitious helpers are used.

## Reproduce

```sh
python3 -B verify.py /fresh/output/directory
```

The default parent is the adjacent unchanged `../e8-bit-seven-stage` package at PR373 commit
`3ff87b5dc0b22a57958547ee347d5da25b7f9401`. Use `--parent PATH` for an identical copy.
Requirements: Python 3.11+, numpy, mpmath, sympy, bash, `sha256sum`, and GNU g++ with C++17
and Boost. Apple clang's `g++` alias requires a compatible `bits/stdc++.h` include shim.
Assertions must be enabled. The inherited shell entry point requires parent, output and
interpreter paths without whitespace; the wrapper rejects them before starting.

The default entry point checks every source hash, runs the complete unchanged PR373 replay,
reconstructs the frame and helper witnesses, and verifies the resulting word afresh. Checks
include all 1062 local F₂ columns, all 1542 global columns through seven stages, chronological
native legality, exact frame determinants/prime witnesses, rational port geometry, literal
bank tiling, both moment engines and the full fallback, the finite invoice and mutation
controls. The complex saving comes from this run's fresh B3 certificate and is bound to
its fresh histogram, dimensions, deficit and precision guard.

The new assembly uses that freshly priced word and finite invoice. It checks both moment
engines at the selected saving, all eight bootstrap cutoffs, all 47 strict constraints,
the rejected adjacent 10⁻²⁷ grid point and the rejected complex leaf cap. It also repeats
the refinement on the original PR373 word and asserts identical κ, making the cause of
the headline gain explicit. Stored expected values are comparisons, never substitutes
for fresh checks. The final `RECEIPT.json` contains no clocks or workstation paths.

The finite coefficient is 56827881566191 < 2⁸⁰, with q³¹³⁷ row bound and a 61-bit payload
below 104 bits. The refinement uses the same fixed coefficient for each of its eight
finite bootstrap cutoffs. Exact output hashes and deterministic receipt fields are pinned
in `EXPECTED.json`; all source and witness bytes are covered by `MANIFEST.sha256`.

## Scope and open obligations

This remains a conditional finite construction. All PR373, PR370 and PR363 admissions
remain, including:

- no Lean proof of the B3 bridged word on either side; PR363's complex exchange check is
  at the header abstraction, and G5/G6 frame/owner names remain generated recipe data;
- nine retained totals at h = 8; the invoice charges all nine and 441 copy/erase episodes;
- PR234 bank/routing generalization to positive-definite E8 labels and rational
  non-permutation port isometries; the source527 lowering program is not rerun;
- source527's signed integer decoder is not run on this E8 word, whose scalar identity is
  checked over F₂;
- the all-size compiler, common ancestor chart, restored-row constants 9909 + 252 and
  external reserve 20161, routing, prime supply, precision/recovery, complex symbolic
  correctness and analytic transfer interfaces.

The finite bill retains the parent's seven-stage formulas and proof lineage. Neither
helper reuse nor tighter arithmetic resolves those obligations. See `PROOF.md` and
`NOTICE.md` for the construction argument and attribution.
