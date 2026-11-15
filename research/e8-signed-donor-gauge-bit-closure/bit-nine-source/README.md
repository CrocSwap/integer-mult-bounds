# Conditional κ = 9.98243154231047e-4 > 2^-10

This combines the pinned E8 bit word from [PR #370](https://github.com/CrocSwap/integer-mult-bounds/pull/370) with the compressed nine-stage complex component from [PR #377](https://github.com/CrocSwap/integer-mult-bounds/pull/377). The new bit construction uses nine stages in dimension 64, eight replicas and exact whole-block banks. Directly pairing #370's original five-stage bit supplier with the new complex supplier would **not** cross `2^-10`.

| Quantity | Verified conditional value |
| --- | --- |
| New bit coarse saving | `1057833103534317 / 10^18` |
| Complex coarse saving | `999240641319551 / 10^18` |
| Final κ | `998243154231047 / 10^18 ≈ 2^-9.9683211064` |
| Excess over `2^-10` | `21680654231047 / 10^18` |

The complex side binds. The final value is about 24.0286% above frozen #361. Two independent rational moment engines and all 47 strict outer constraints are checked; adjacent grid points are rejected. This is a conditional finite construction, with the supplier/compiler/precision/analytic interfaces listed in [PROOF.txt](PROOF.txt). It is not a new Lean proof or a claim of priority.

Run from the repository root with Python 3.11+, NumPy, SymPy, mpmath, a C++17 compiler and Boost headers:

```sh
python3 -B research/e8-bit-complex-nine/verify.py --work /tmp/e8-bit-complex-nine-fresh
```

The destination must not exist. The runner verifies all source manifests, freshly rebuilds the entire #370 package and the eight-stage #377 verification, then runs the new geometry, emitted-word, independent-audit and combined-price checks. The portable standard-header shim only supplies standard C++ includes for Clang; inherited source files are unchanged. Optional OR-Tools is used by #370's separate center-minimality check when installed.

The new finite evidence includes all 120 port routes, 944 exact frame projectors, 3,289 nested and reflected pairs, 8,745 scalar columns, 62,280 bank assignments, 72 actual local invocations and 1,355,328 emitted events. Eight new structural mutations are rejected, in addition to inherited word and record mutations.

The largest bit child is 42 of 64. Two-level halving is proved and charged explicitly. The old five-stage 104-bit prefix assertion is replaced by a freshly derived 117-bit bound with a charged 192-bit allowance; the two-level finite constant fits 512 bits and the row coefficient is 18,355 below the retained 20,161 allowance.

The local E8 bit word and #370's explicit nine-total admission are credited to Dylan Crow with Anthropic Claude assistance. Jacob Sussman's E8 unit and all upstream notices remain intact. This composition and its audit were prepared by Zhihao Chen with substantial OpenAI Codex assistance, under Apache-2.0. See [NOTICE.txt](NOTICE.txt).
