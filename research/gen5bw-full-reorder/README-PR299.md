# five-stage-gen5b-kernels-restorations-sinks

**Conditional κ = 374949607659749 / (5·10¹⁷) = 7.49899215319498·10⁻⁴** (+0.427% over #296's
7.46709720962478·10⁻⁴; +0.587% over #295's 7.45513573133379·10⁻⁴).

Base: the gen5b package of #296 (README-STAGEALT.md) — #287's package with the bit word regenerated from #285's generator
using #285's pair module, an alternative 28/12 local design and a 35-addition debt-10 all-but-one module (virtual R
17,160, physical R 15,434, 1,726 reuse pairs, entrances {20: 2,182, 21: 34, 18: 16, 17: 2}), #287's descent (904 gates)
and 220 target squares re-derived on it, and PR #233's complex certificate. On top, in this order after the target
stage, the three transcript stages of #290/#295, each re-screened on this word:

| stage (census on this word) | local delta | φ-ledger | κ predicted = verified | gain |
| --- | --- | ---: | ---: | ---: |
| base (stagealt) | — | — | 7.46709720962478·10⁻⁴ | — |
| **kernel**: 1,720 entries (920 twin pairs: 904 e=1, 16 e=3; 800 families: 375 quads, 425 triples), entrance rank 2,192 | {1:+3294, 2:−611, 3:−1164, …} | −3,799.1 | 7.49121118627047·10⁻⁴ | +0.3229% |
| **early restoration**: 440 helpers (20/22/22 → join 23), cut 757,526 | {1:+1320, 2:−880} | −886.6 | 7.49686102247225·10⁻⁴ | +0.0754% |
| **terminal sinks**: 7 (9 clean before the kernel; 2 became kernel donors), R 15,434 → 15,427 | {3:−7, 21:−7} | −333.7 | 7.49899215319498·10⁻⁴ | +0.0284% |

Bit coarse 7.50461986477241·10⁻⁴; complex coarse 7.54736418878859·10⁻⁴ (#233), so the bit side binds (0.57% margin).

Census on the post-target word: 13,200 plain helpers, responses of F₂ rank 1,760 (nullity 11,440); 952 twin pairs with
a common cut and nondegenerate common line (880 generic in (2,2) first frames, 72 e_i−e_j); 1,632 class triangles and
10,041 class quadruples; candidates with a common cut and nondegenerate entrance: 952 pairs, 2,104 triples, 3,807 quads;
greedy φ packing keeps 1,720. Because 1,574 pivots have residual 23, the pivot banks are (r⁴, 24, 4²⁴⁻ʳ) instead of
(r⁴, 4³⁰⁻ʳ) (the rank-4 blocks of (4³⁰) would not suffice); every bank is still 120 wide and full, so the stock is
unchanged by the choice. Literal stock 1,236,750 → 1,229,750; banks 807,350; charts 910; entrances 3,954.

Mechanisms and checks: [KERNEL-PROOF.md](KERNEL-PROOF.md) (kernel entries), [LEVERS-PROOF.md](LEVERS-PROOF.md)
(early restoration from PR #280 / #283, terminal sinks from PR #283). Conditional finite construction under the retained
public all-size hypotheses of the source527 lineage (no Lean certificate); inherited stages are not re-proved.

## Verify

    python -m pip install -r requirements.txt    # sympy 1.14.0
    python3 -B verify.py --output /tmp/gen5alt-krs-verification   # about 5 minutes; not under -I

Twelve fresh stages (virtual, raw, bit with descent/target/kernel/restore/sink, kernel, restore, sink, scalar, primes,
banks, complex, math, finite) with twelve omitted-stage controls; all changed literals re-pinned in
`expected/kernel-pins.json` (recording mode refused under verify.py).
