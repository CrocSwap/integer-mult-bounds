# Bit operation-frame descent on #168's paired-cube bit word

Under #168's retained interfaces, this finite witness certifies

$$T(n)=O\big(n(\log n)^{1-\kappa}\big),\qquad \kappa=\frac{6105562}{10^{10}}=6.105562\times10^{-4}.$$

That is **+0.151% over #168** (6.096379e-4). The bit supplier binds in #168, and #168 ships its p = 12 bit word with no operation-frame descent. This package descends 1,716 of that word's operation frames; 264 of them leave their original frame, as in #165. The scalar word, gauges, persistent roles and complex supplier are unchanged.

| Bit supplier, p = 12 | Replaced frames | R | W | Coarse saving |
|---|---:|---:|---:|---:|
| #168 | 0 | 22,252 | 25,772 | 6105820/10¹⁰ |
| **this** | **1,716** | 22,252 | 25,772 | **6115023/10¹⁰** |

## Verify

```sh
python3 -B research/paired-cube-bit-descent-168/prove.py      # about 1 minute, standard library
```

- **Bit word.** `word.py` is #165's bit checker, unchanged except for paths. It applies `replacement-frames.json` to #168's committed `research/paired-cube-bit/out` word. It checks every replaced frame:
  - the value span lies inside the frame;
  - the frame is exactly nondegenerate;
  - every physical role chain stays nested;
  - rank mass is preserved and the complete child histogram is recounted.

  Then it checks the complete F2 identity and the defining integer decoder over all source, target and dirty columns. Omitted compensation, a missing partner delivery and a zero frame are rejected.
- **Prime witnesses.** `prime_witnesses.py` (#165's) factors all 1,536 distinct new integer Gram determinants: each has a residual below 2^80 after 2, 3 and 5, so every retained prime q > 2^80 stays valid.
- **Assembly.** #168's own `scripts/paired_cube_network.py` functions, unchanged, certify:
  - the bit moment with its contaminated fallback;
  - the complex supplier and the finite bridge;
  - the balanced-prefix assembly: 47 strict constraints and 7 margins.

  Only the bit row and the two grid points change. The next 10⁻¹⁰ coarse point and the next κ point are both rejected, and the original-prefix control is rejected.
- `certificate.json` and `prime-witnesses.json` must reproduce byte-identically.

`generate.py` regenerates `replacement-frames.json` (about 70 s; numpy not needed). It runs alternating passes over the operations. Each operation's frame moves to:
- the lower bound: the span of both roles' previous frames and the value span; or
- the upper bound: the intersection of their next frames.

A move is taken only when it is nested, nondegenerate, prime-witnessed and lowers the local child cost. It is discovery only; `prove.py` checks its output.

## Scope and credits

All of #168's conditional interfaces remain assumptions. This is not an unconditional multiplication theorem or a runtime claim. No global optimality is claimed.

- Base: #168, eumemic's paired-cube word, at `98c115b53742b6613ad630de4d493f37b0119da7`, with its full lineage.
- Bit-frame replacement format, checker and prime witnesses: chafreaky's #165, with frame descent from #163/#164.
- Frame lemma: #130/#131.

Prepared by Joel Pulikkan (GamingPuzzled) with Anthropic Claude assistance; Apache-2.0.
