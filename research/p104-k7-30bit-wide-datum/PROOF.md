# 30-bit K7 profile at datum width 2^40 with paid child sum 2925

This package changes three parameters of the [exact #8098 head](https://github.com/CrocSwap/integer-mult-bounds/commit/fae237c8aee774bb2256d4e394fed9f3934147c2). It changes no word, caller, receiver or premise of the signed construction. The authenticated `source/wide` layer edits the #8098 domain assembly. That layer is itself #8097's ten-shortcut source with the #8098 transfer and domain layers applied. [Layer receipt](source/wide/ASSEMBLY.json) · [Edits](source/wide/edits.py)

1. **Child geometric sum 2925** instead of 2401, inside the same charged clock allowances.
2. **Individual installer datum width `w = 2^40`** instead of `2^38`. This changes a stated hypothesis of the fixed setup bound. See [WIDE-SETUP.md](WIDE-SETUP.md).
3. **A 30-bit six-stage ordinary profile** `(16096, 254464, 4023296, 63614464, 1005833115, 1073741823)` with Gaussian height `G = 52354`.

## 1. The paid child sum

Use #8098's installed `N ≥ 16` quotient mean `B = 6277647/2690420` and contraction `ρ = 2924/2925`, so the child tariff is `τ = B/ρ = 3672423495/1573357616`. The geometric sum is `1/(1−ρ) = 2925`.

The recursive sum enters the clock only through the two allowances that #8076 introduced and #8098 restates.

- **Entry.** The square of the per-stage multiplier `7S/10` fits the five extra entry bits: `(7·S/10)^2 < 2^22`.
- **Terminal.** The relative per-stage multiplier `S/376` fits three bits per stage: `S < 8·376`.

#8098 checks both inequalities for `S = 2401` (`receipt.py`, the assertion after `geometric_sum`). They also hold for `S = 2925`: `(7·2925/10)^2 = 4192256.25 < 4194304` and `2925 < 3008`. `S = 2926` fails the first one, and the package asserts that failure. Every other use of the tariff is the factor itself.

The entry bound `40 + 22 + 16384·ΣH + surcharges` and the terminal bound `128 + 3m + 320·ΣH` are unchanged formulas. A search of the assembled sources finds no other occurrence of the sum 2401 outside these assertions and the comparison controls. Reviewers should confirm this point: **the only claimed uses of the child sum are these two allowances.**

The tariff scales #8098's ordinary factor by `1755000/1755131`. Both directed implementations then fund `1411814/2^20` and reject `1411813/2^20`: the 112-bit `receipt.py` path and the independent 192-bit `independent_price.py` path. They also re-derive the three earlier ticks `1412105`, `1411929` and `1411927`.

## 2. Datum width and height limit

Under `w = 2^38` the sharp height limit was `H < 2^28`, because of `1024H + 3 < 2^38`. Under `w = 2^40` it is `H < 2^30`, because `1024·(2^30−1) + 3 = 1099511626755 < 2^40 < 1024·2^30 + 3`. The serial setup bound is the inherited formula evaluated at the new width: below `2^230` instead of `2^228`. `check_wide_setup.py` reproduces the inherited total at `w = 2^38` exactly before evaluating `w = 2^40`. The census (`source/wide/check_installed.py`) runs the real ten-recipe constructor and directory serializer with every calendar `open()` and `width` forbidden. It checks that the largest serialized integer and the directory size are below `2^40`. [Setup note](WIDE-SETUP.md)

## 3. Profile and guarded crossing

For ordinary height `H`, `u = min(η, (249(c_B − d/H) + b)/250)`, with `b` booked as `(⌊10^21 u⌋ − 1)/10^21` between stages. Here `c_B = 4391986206293/2^50`, `d = 1411814/2^20` and `η = 1/256`.

| Stage | H | Entrance cut |
| ---: | ---: | ---: |
| 1 | 16096 | 16225 |
| 2 | 254464 | 270753 |
| 3 | 4023296 | 4294113 |
| 4 | 63614464 | 67908641 |
| 5 | 1005833115 | 1073741820 |
| 6 | 1073741823 = 2^30 − 1 | 2147483707 |

The cut rule `cut_{i−1} + 2 < H_i` is tight at stage 6. The penultimate height is the largest one the prefix admits, and the package checks this by bisection. Moving any of the four free heights by ±16, with the penultimate height re-maximized, does not raise the ceiling.

The guarded ordinary ceiling is about `0.003900866113430039`. The installed rate `κ = 0.003900866113430` is strictly below it, and the next `10^-15` tick fails. The Gaussian ceiling `c_G − (32401/262144)/G − 5/10^18` funds at `G = 52354` and fails at `52353`. The funding floors are `(1073162143, 52354)`. Both signed tiers pass 54 strict and four functional outer inequalities.

Negative controls rejected at the new rate:

- each height reduced by its minimal failing drop `(5061, 7171, 7365, 7378, 7379, 34)`;
- the #8098 28-bit profile;
- the best five-stage 30-bit profile found;
- the best six-stage 29-bit profile found;
- debit `1411927/2^20` (#8098's) and debit `1411815/2^20` (the next tick) at the new heights;
- the inherited recurring cap, and `log2 C − 1`.

## 4. Recurring constant

`log2 B = 128 + 3·6 + 320·ΣH = 687194642706`. The activation exponent is `A = 2147536386`, the entry premium is `⌈(κ − κ_entry)A⌉ = 968252`, and the complete recurring `log2 C = 687206162189`. That is about four times #8098's `171810078109`. It is a larger constant, not a change in the exponent.

## 5. Same-budget control

At #8098's unchanged 28-bit heights and `G = 52270`, the 2925 tariff alone books `0.003900862349569` (`+4.01·10^-13` over #8098). It keeps #8098's `log2 C = 171810078109` and needs no width change. `receipt.py` and `check_stage_seam.py` assert this value as a control. It is not the installed selector.

## Why 30 bits

Each extra height bit roughly halves `c_B − κ`, because the last stage carries weight `249/250` of `d/H_6`. The best profiles found reach 0.003900866740739 at 31 bits and 0.003900867054394 at 32 bits, below the K7 ceiling 0.003900867368050. The literal stage-seam replay (`verify_stage`) materializes the scanned field `2^(round(9H))` and `2^(8H)` of the last stage as Python integers. At 30 bits it peaked at 15.6 GiB RSS. At 31 bits it would need roughly twice that. Larger profiles therefore need either a log-domain proof of the same dispatch or more memory. This package stops at the largest width that its inherited literal checks can execute.

## Premises

The conditional all-size claim keeps the five signed premises of the [selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json): native action at every positive column multiplicity, ownership and exact erasure, uniform chronological compilation, fixed-tape movement and precision, and analytic recovery. It adds the changed width hypothesis `w = 2^40` in the fixed setup bound. The finite checks exercise specified cases of the inherited signed contract. They are not a formal verification of the multiplication theorem.
