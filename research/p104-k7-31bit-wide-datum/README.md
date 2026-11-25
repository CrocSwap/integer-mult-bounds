# 31-bit K7 profile at installer datum width 2^41 (paid child sum 2925)

**Label: enlarged budget (resource tradeoff) and one changed setup hypothesis.**

The signed price certifies conditional κ **0.003900866740647** at recurring `log₂ C = 1374400932409`. The exact gain over the [#8099 head `dc475d6a`](https://github.com/CrocSwap/integer-mult-bounds/commit/dc475d6a16e6d0d2f863a562725843c95fb14c5c), κ 0.003900866113430, is **0.000000000627217**, or **+0.0000160789%**. The remaining gap to the K7 binary ceiling `BINARY_C ≈ 0.003900867368050` falls from 1.255·10⁻⁹ at #8099 to 6.274·10⁻¹⁰ at this head.

The word, caller, receiver, Gaussian producer, periodic-integral price, full `256/255` reserve and all five signed premises are #8099's. Three parameters change. [Proof and invoice](PROOF.md) · [Installed price](RESULT.json)

1. **Child geometric sum 2925.** Pricing #8098's `N≥16` mean at contraction `2924/2925` fits the same five-bit entry and three-bit-per-stage terminal clock allowances: `(7·2925/10)² < 2²²` and `2925 < 8·376`. 2926 fails the first one. The ordinary debit falls from `1411927/2^20` to `1411814/2^20`, checked in both directed implementations.
2. **Installer datum width `w = 2^41` instead of `2^40`.** This changes one hypothesis of the fixed setup bound. Raising it moves the sharp `1024H + 3 < w` height limit from 30 to 31 bits. The inherited serial setup formula then gives fewer than `2^231` setup transitions instead of `2^230`. [Setup note](WIDE-SETUP.md)
3. **Six-stage 31-bit profile** `(16096, 254464, 4023296, 63614464, 2079574939, 2^31−1)`, `G = 52367`, `η = 1/256`.

**Same-budget control.** With only change 1, at #8098's own 28-bit heights, `G` and `log₂ C`, the booked rate is 0.003900862349569 (+4.01·10⁻¹³). It needs no width change, and the package asserts it as a control.

## Replay from a clean checkout

Use Git and CPython 3.12 with assertions. The `calendar` mode literally replays the stage-6 seam at 31-bit width. It needs **at least 32 GiB RAM** (30.7 GiB measured peak) and about 22 minutes. The other modes fit in 8 GiB. Keep 8 GiB free on the checkout and scratch volumes.

```sh
scratch="$(mktemp -d)"
TMPDIR="$scratch" python3.12 -IB scripts/research_package.py --package research/p104-k7-31bit-wide-datum
TMPDIR="$scratch" python3.12 -IB research/p104-k7-31bit-wide-datum/verify.py census
```

The registered modes `price`, `calendar`, `raw`, `exterior`, `nested`, `product` and `setup` authenticate #8097's archive, #8098's transfer and domain overlays and the new `wide` layer. `census` runs the ten-recipe installed constructor at the new heights with every calendar forbidden. All nine modes, including `inputs`, passed locally at this head (see [replay log](REPLAY.md)). See [VERIFY.json](VERIFY.json) for the registered scopes and [local replay log](REPLAY.md).

## Open next questions

- **Log-domain seam proof.** Larger heights are limited by the literal `verify_stage` replay, not by the price. Each further bit halves `BINARY_C − κ`: about 0.003900866740739 at 31 bits (reached here) and 0.003900867054394 at 32 bits, with `w = 2^41`, `2^42`. A first step is a log-domain mirror of `ordinary_carrier.stage_body` dispatch, cross-checked against the literal replay at 28–31 bits. Blocker: reviewers must accept the symbolic replay in place of literal integers.
- **Local optimality evidence.** At 31 bits, the exact Fraction-neighbor ceiling comparison cannot tie — the ceiling saturates at the grid floor (frozen at κ in both forms across ±16 any-free-height shifts). The strict `n <= ordinary_upper(ranks)` control was replaced by the honest 10^-15 κ-grid form; see [PROOF.md](PROOF.md).
- **Width hypothesis.** Is `w = 2^40` used anywhere outside the fixed serial setup bound, for example in the portable WASI trace? A first step is to trace every consumer of `max_datum_bits` and of #8055's `w`.
- **The binary word itself.** Beyond the K7 ceiling, further gains need a better binary word, not pricing.

## Credit

The construction is entirely upstream's. SYLforge supplied #8097's ten-shortcut word, three-type producer, periodic-integral price and six-stage profile, and the #8052 K7 word. ToikY supplied #8098's `N≥16` domain, the 2401 contraction pricing, the directed screens and the census. Ali Romman supplied #8042's quotient law and clock, #8055's serial setup and #8057's signed machinery. Clear1nsight's #8081 supplied the expanded installer argument, and floration's #8088/#8090/#8094 supplied the predecessor words, profiles and verification patterns. The #8076 contributors supplied the charged clock. [Full attribution and license](NOTICE.md)

This package does not use any idea or technique from exact-DFT (Fourier) submissions. Those include our own, and Kuznetsov's and KARTAL's. Prepared by Clear1nsight with OpenAI Codex materially assisted on the parameter search, source-assembly edits, exact replay and evidence preparation. An earlier exploratory arithmetic screen that ChatGPT assisted first noticed the 2925 headroom and the height scaling.
