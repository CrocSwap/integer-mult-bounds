# Extreme-frame retiming on #284's gen4 word

Conditional finite saving:

```
kappa = 726319877913758986831841 / 10^27 = 0.000726319877913758986831841
```

That is **+2.8186e-8 (+0.00388%) over #284** (`181572923056461298166587/(25·10^25)` = 0.000726291692225845), the strongest gen4-word construction. It is **not** a repository record: #285's gen5 word (0.000742785663120535) is higher. The method is word-agnostic. On gen5's raw word the same scan rediscovers #279/#280's 880 source-pair retimings and finds 135 further gate moves (proxy price about 0.0007435), but that composition needs a gen5 admission path and is not claimed here. The change is small and purely local: 95 ADD retimings in two passes on #284's final word. Every other record keeps its position and bytes.

## Change

An ADD's frame must contain its operands' current frames (MOVEs only go up) and lie inside the frames their next uses need. Between those bounds the choice is free, and the price depends on it. Each operand role pays one recursive child for each frame jump, of width equal to the rank jump. At fixed rank mass, the moment cost falls when mass collects into fewer, wider children (roughly `−Σ r ln r`). Since `r ln r` is convex, the best frame for a unit is one of two extremes:

- the **join** of the operands' previous frames (the smallest legal frame), or
- the **meet** of the frames their next uses require (the largest).

Neither need be an existing frame. Each one is constructed exactly here.

| pass | unit | moves | histogram delta |
| --- | --- | --- | --- |
| 1 | equal-frame ADD component (54 gates) | 21 joins: 14→13 ×12, 16→15 ×4, 12→11 ×4, 12→10 ×1 | `{1:+21, 2:−26, 3:−9, 4:+12, 5:+3, 6:+15, 7:−19, 8:+8, 9:−5, 10:−8, 11:+9}` |
| 2 | single ADD (components split) | 40 meets (10→15 ×20, 18→19 ×16, 12→13 ×2, 15→16, 17→18) and 1 join (12→10) | `{1:+28, 2:+63, 3:−33, 4:+1, 5:+20, 6:−1, 7:−39, 10:−20, 12:−2, 13:+2, 15:+19, 16:+1, 17:−1, 18:−15, 19:+16}` |

Rank mass is unchanged in both passes (422,388 local), and stock is unchanged (2,549,300 literal, 509,860 normalized). All changed gates are category-12 helper additions, plus four in category 28. After pass 2, fresh scans of both unit types find no improving extreme, so the word is locally optimal for this move.

The same scan applied to #283's word gives +2.4958e-8 there. On #280's word it finds nothing: every component there already sits at an extreme where moving loses. The slack comes from the response-kernel pivots and target-prefix squares.

## Reproduce

Requirements are the same as for #284: Python 3.11+, SymPy 1.14.0, a C++17 compiler with `<bits/stdc++.h>` and `__int128` (GCC), and Boost headers. Check out #284 at `2c991a3ac400057059145c837e8b32bba9128346` separately, then run:

```sh
python3 -B research/gen4-extreme-frame-retiming/verify.py \
  --pr284 /path/to/pr284-checkout/research/gen4-collective-families-283 \
  --output /tmp/extreme-frame-replay [--cxx g++] [--boost-include /path]
```

The verifier works as follows:

1. It checks #284's pinned manifest and runs #284's **complete** verifier freshly: all nine PR276 stages, sinks, kernels with the 91 collective families, retiming, transport, restorations, targets and #284's own checks. Its certificate must pass.
2. It applies the frozen passes. Before each pass, `code/frames_audit.py` checks every new frame against the word it is applied to:
   - it is an exact integer basis/annihilator pair of complementary rank;
   - it contains every previous boundary frame and lies inside every next one;
   - its dimension equals the rank of the union (join) or 24 minus the rank of the stacked annihilators (meet).
3. `code/emit.py` asserts that the ordered non-MOVE stream changes only in the selected frame fields.
4. It reruns #284's own native checkers on the new word: legality, multi-cut prefix, exact bank charts and allocation, all five-stage formal columns, the rational price, the finite invoice, and the fixed-prime 47-constraint assembly with adjacent-grid rejection. It compares κ and the word hash only after those finish.

A local replay takes about 10 minutes, almost all of it #284's own verifier; the extra stages take about 30 seconds. `code/scan.py` is the discovery scan and is not needed for verification.

## Scope

This is a conditional finite construction under #284's (and #283's) retained interfaces: all-size compiler, common weighted chart, restored rows, selectors, routing, prime supply, precision/recovery, complex symbolic correctness and analytic reduction. Nothing beyond #284's word and checkers is assumed. It is not an unconditional theorem, a Lean proof or a runtime result. No priority or global optimality is claimed.

See `PROOF.md` and `NOTICE.md`.
