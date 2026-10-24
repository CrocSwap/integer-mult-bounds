# Exact grid of the complete selected #5413 caller

**Positive scoped result; no new κ.** One controller level of the selected caller needs **exactly 73 extra
fractional bits**. The body needs `ceil(9 lambda/2) + 6`. Both bounds are attained. This continues the merged
[selected-word-exact-grid](../selected-word-exact-grid/README.md), which covers the eight-relation word alone, from
the word to the complete caller of [PR #5413](https://github.com/CrocSwap/integer-mult-bounds/pull/5413). The
caller's own precision record (`FRESH-PRECISION.json`) has only crude heights: about 19,452 bits per local body
and 377,688 for the global word. This is target 7 of [PR #5428](https://github.com/CrocSwap/integer-mult-bounds/pull/5428).

## Body

Only backward bodies run: 18 calls, with no forward macro calls. [verify.py](verify.py) executes the literal
`NEUTRAL-BACKWARD-v16c` body, with `PROVIDER_5402` expanded by its schedule:

- wrappers;
- mode scalars;
- the 834-instruction input and output basis programs;
- the 21,473-event provider word;
- cache SWAP and CLEAR.

Monomials, Gaussians and warps stay symbols, so terms through different operator paths never merge; adjacent
inverse warps cancel. The 240-map monomial block consists of maps, ADDs and the exact inverse maps. Each y-field
pair therefore composes to the identity and is omitted. The verifier checks this directly.

| Check | Result |
|---|---|
| Odd denominators | none, including the `ZW = 14 I` provider |
| Owned fields at exit | all 17 zero |
| Maximum `v2` | 6, attained by a single-occurrence rank-9 helper term (coefficient `-1/64`) |
| Main-data / helper maxima | `v2 <= 4` / `v2 <= 6` with local rank `<= 9` |
| Final X rows | `x_p - y_p` on all 112 ports |

## Controller

For each port, `A_x` is the `backward_input_X` wrapper followed by `Delta_{I_x}^-1`; `A_y` is defined likewise.
Let `Q_p = A_y` followed by `A_x^-1`. On every port `Q_p` has Fourier rank 1 and `Q_p^2` rank 0. Since the final
rows are `x_p - y_p`, the body computes `X = Phi (x - Q_p y)`, so `Q_p` is the controller's Q.

The verifier replays the controller in the exact Laurent ring of `check_wholecaller_v1`. It has 32 banks with
integer coefficients and reproduces the diagonal endpoint. The global data live on 145 axes: the central axis plus
eight private axes per stage. A component `Q^q prod_{t in T} D_t` therefore carries private Fourier rank `8|T|`.

| Region | Exact maximum |
|---|---|
| Calls before the last (`|T| <= 16`) | `4 + ceil((128+9)/2) = 73`; helpers `<= 11` |
| Last call, in-word cuts | 73 |
| Last call, t-field after the paid C8 job | 73 |
| Last call, cache cuts | 73 |
| 224 rank-145 targets | 73 (necessary) |

In the last call (stage 32, pair 15), original bank 31 enters x as `Q^2 D_T` and y as `Q D_T`, with `|T| = 17`.
Its two paths meet on `Phi_x Q^2` with coefficient `c_x + c_y`. Each such term is evaluated with exact nine-plane
ranks, with warps taken from the native table and admitted as in kappa-round3-warp-20261022. Treated separately,
the paths would suggest 74 to 76 bits. Merged, they cancel down to 73. **The guard of one controller level is
therefore exactly 73.** The body's `2^-6` adds nothing on top of the target requirement.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/selected-caller-exact-grid
python3.12 -I -B research/selected-caller-exact-grid/verify.py
python3.12 -I -B research/selected-caller-exact-grid/test_verify.py
```

The verifier uses the standard library and the pinned repository Clifford compiler. It takes under a minute and
prints `PASS_SELECTED_CALLER_BODY_6_CONTROLLER_EXACTLY_73`. The controls reject six mutations:

- a drifted input;
- an odd division;
- a block map that is not inverted;
- a missing controller `Q_POWER`;
- a missing owned CLEAR;
- a tampered RESULT.json.

## Scope

Several premises are inherited and not re-proved here:

- native operator correctness;
- the canonical-chart, wrapper and warp conventions;
- the identification of the controller's Q with the body's Q through `X = Phi (x - Q y)`.

The last of these is the body's specified endpoint and is checked through its final rows. The result is an
exact-grid statement, not a rounded execution, a recursive price or a supplier admission. The selected record is
unchanged.

## Open next questions

- What does the attained 73-bit controller guard cost in the recursive invoice? First compare it with the retained
  precision_tape packing. #5419 shows that a uniform paid-precision factor above about 1.0046 removes the 0.0033 margin.

## Credit

Clear1nsight (#5413), dillona (#5402), Ali Romman (#5383, #5398) and Cao Yifan (#4610) supplied the caller, provider
and word. Ross Richardson supplied the Clifford denominator lemma. The coded-native-caller normalizers and the
kappa-round3-warp native table supplied the wrappers and warps. Prepared by Mark (Matarener) with substantial
Claude Code assistance. New work is Apache-2.0.
