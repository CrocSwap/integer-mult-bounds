# 31-bit K7 profile at datum width 2^41 with paid child sum 2925

This package changes three parameters of the [exact #8098 head](https://github.com/CrocSwap/integer-mult-bounds/commit/fae237c8aee774bb2256d4e394fed9f3934147c2). It changes no word, caller, receiver or premise of the signed construction. The authenticated `source/wide` layer edits the #8098 domain assembly. That layer is itself #8097's ten-shortcut source with the #8098 transfer and domain layers applied. [Layer receipt](source/wide/ASSEMBLY.json) · [Edits](source/wide/edits.py)

1. **Child geometric sum 2925** instead of 2401, inside the same charged clock allowances.
2. **Individual installer datum width `w = 2^41`** instead of `2^40`. This changes a stated hypothesis of the fixed setup bound. See [WIDE-SETUP.md](WIDE-SETUP.md).
3. **A 31-bit six-stage ordinary profile** `(16096, 254464, 4023296, 63614464, 2079574939, 2147483647)` with Gaussian height `G = 52367`.

The signed price of the new profile is **κ = 0.003900866740647**. Gain over the [#8099 head](https://github.com/CrocSwap/integer-mult-bounds/commit/dc475d6a16e6d0d2f863a562725843c95fb14c5c) (κ = 0.003900866113430) is **0.000000000627217** (+0.0000160789%). The exact gap to the K7 binary ceiling `BINARY_C ≈ 0.003900867368050` falls from 1.255·10⁻⁹ at #8099 to 6.274·10⁻¹⁰ at this head.

## 1. The paid child sum

Use #8098's installed `N ≥ 16` quotient mean `B = 6277647/2690420` and contraction `ρ = 2924/2925`, so the child tariff is `τ = B/ρ = 3672423495/1573357616`. The geometric sum is `1/(1−ρ) = 2925`.

The recursive sum enters the clock only through the two allowances that #8076 introduced and #8098 restates.

- **Entry.** The square of the per-stage multiplier `7S/10` fits the five extra entry bits: `(7·S/10)^2 < 2^22`.
- **Terminal.** The relative per-stage multiplier `S/376` fits three bits per stage: `S < 8·376`.

#8098 checks both inequalities for `S = 2401` (`receipt.py`, the assertion after `geometric_sum`). They also hold for `S = 2925`: `(7·2925/10)^2 = 4192256.25 < 4194304` and `2925 < 3008`. `S = 2926` fails the first one, and the package asserts that failure. Every other use of the tariff is the factor itself.

The entry bound `40 + 22 + 16384·ΣH + surcharges` and the terminal bound `128 + 3m + 320·ΣH` are unchanged formulas. A search of the assembled sources finds no other occurrence of the sum 2401 outside these assertions and the comparison controls. Reviewers should confirm this point: **the only claimed uses of the child sum are these two allowances.**

The tariff scales #8098's ordinary factor by `1755000/1755131`. Both directed implementations then fund `1411814/2^20` and reject `1411813/2^20`: the 112-bit `receipt.py` path and the independent 192-bit `independent_price.py` path. They also re-derive the three earlier ticks `1412105`, `1411929` and `1411927`.

## 2. Datum width and height limit

Under `w = 2^38` the sharp height limit was `H < 2^28`, because of `1024H + 3 < 2^38`. Under `w = 2^40` it was `H < 2^30`. Under `w = 2^41` it is `H < 2^31`, because `1024·(2^31−1) + 3 = 2199023254531 < 2^41 = 2199023255552 < 1024·2^31 + 3` — and `92·(2^31−1) < 2^41`. The serial setup bound is the inherited formula evaluated at the new width: below `2^231` instead of `2^230`. `check_wide_setup.py` reproduces the inherited total at `w = 2^38` exactly before evaluating `w = 2^41`. The census (`source/wide/check_installed.py`) runs the real ten-recipe constructor and directory serializer with every calendar `open()` and `width` forbidden. It checks that the largest serialized integer and the directory size are below `2^41`. [Setup note](WIDE-SETUP.md)

## 3. Profile and guarded crossing

For ordinary height `H`, `u = min(η, (249(c_B − d/H) + b)/250)`, with `b` booked as `(⌊10^21 u⌋ − 1)/10^21` between stages. Here `c_B = 4391986206293/2^50`, `d = 1411814/2^20` and `η = 1/256`.

| Stage | H | Entrance cut |
| ---: | ---: | ---: |
| 1 | 16096 | 16225 |
| 2 | 254464 | 270753 |
| 3 | 4023296 | 4294113 |
| 4 | 63614464 | 67908641 |
| 5 | 2079574939 | 2147483644 |
| 6 | 2147483647 = 2^31 − 1 | 4294967355 |

The cut rule `cut_{i−1} + 2 < H_i` is tight at stage 6. The penultimate height is the largest one the prefix admits, and the package checks this by bisection. Moving any of the four free heights `(stage 1-4)` by ±16, with the penultimate height re-maximized, does not raise the κ-grid ceiling.

The guarded ordinary ceiling is about `0.003900866740647089`. The installed rate `κ = 0.003900866740647` is strictly below it, and the next `10^-15` tick fails. The Gaussian ceiling `c_G − (32401/262144)/G − 5/10^18` funds at `G = 52367` and fails at `52366`. The funding floors are `(2146006033, 52367)`. Both signed tiers pass 54 strict and four functional outer inequalities.

The local-optimality control uses a 10^-15 κ-grid floor rather than the strict Fraction comparison that the 28–30-bit packages used. At 31 bits the exact comparisons saturate: across every ±16 shift of any free height, every neighbouring profile prices strictly above TERMINAL.κ in Fraction terms (the exact ceiling keeps rising while the displayed grid does not), so no strict `n <= ordinary_upper(ranks)` tie is reachable. The grid comparison is the honest invariant at this width: no neighbour within ±16 raises `κ`'s grid floor. This deviation is documented here rather than hidden, and it should be re-checked in a future log-domain seam argument.

Negative controls rejected at the new rate:

- each height reduced by its minimal failing drop `(None, 15776, 16748, 16814, 71886, 307)` — the stage-1 drop uses the existing `first-ordinary-height-below-8192` control;
- the #8098 28-bit profile;
- the best five-stage 30-bit profile found (`(65536, 2097152, 67108864, 1004469748, 2147483647)`);
- the best six-stage 29-bit profile found (`(8192, 131072, 2097152, 33554432, 501079706, 536870911)`);
- debit `1411927/2^20` (#8098's) and debit `1411815/2^20` (the next tick) at the new heights;
- the inherited recurring cap, and `log2 C − 1`.

## 4. Recurring constant

`log2 B = 128 + 3·6 + 320·ΣH = 1374389410066`. The activation exponent is `A = 4295020054`, the entry premium is `⌈(κ − κ_entry)A⌉ = 1936482`, and the complete recurring `log2 C = 1374400932409`. That is about 8 times #8098's `171810078109`. It is a larger constant, not a change in the exponent.

## 5. Same-budget control

At #8098's unchanged 28-bit heights and `G = 52270`, the 2925 tariff alone books `0.003900862349569` (`+4.01·10^-13` over #8098). It keeps #8098's `log2 C = 171810078109` and needs no width change. `receipt.py` and `check_stage_seam.py` assert this value as a control. It is not the installed selector.

## Why 31 bits

Each extra height bit roughly halves `c_B − κ`, because the last stage carries weight `249/250` of `d/H_6`. The best profiles found reach 0.003900866740739 at 31 bits, below the K7 ceiling 0.003900867368050. This package stops at the largest width that its inherited literal checks can execute. The next bit (32) needs roughly twice the literal replay — about 60 GiB peak RSS (estimated from the measured 31-bit 30.7 GiB) — or a symbolic log-domain expansion of the replay.

## Premises

The conditional all-size claim keeps the five signed premises of the [selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json): native action at every positive column multiplicity, ownership and exact erasure, uniform chronological compilation, fixed-tape movement and precision, and analytic recovery. It adds the changed width hypothesis `w = 2^41` in the fixed setup bound. The finite checks exercise specified cases of the inherited signed contract. They are not a formal verification of the multiplication theorem.

The numerical price flow follows the same five premises and the same recurring formula as #8098. The package does not claim a different signed contract; the selected record is unchanged and unsupported in this PR.

**Asymptotic context (not a claim here).** An OpenAI multitape-tape preprint (November 24, 2026, [The logarithmic exponent of integer multiplication on tapes](https://github.com/openai/math/blob/main/preprints/The-logarithmic-exponent-of-integer-multiplication-on-tapes-November-24-2026/paper.pdf)) gives an asymptotic machine-model result with the optimal exponent 1/2 under variable-count Weak ETH. That result lives in a different model (asymptotic worst-case time for full multiplication on several tapes) and uses short finite Fourier transforms, which are outside this repository's explicit exclusion of exact-DFT/Fourier submissions. It does not supersede, weaken or replace the conditional finite κ records in this repository, which are advisory pre-admission and unreviewed. The finite checks here are consistent with that result.
