# five-stage-gen5b-kernels-restorations-sinks (+ post-sink descent)

**Conditional κ = 749920356821633 / 10¹⁸ = 7.49920356821633·10⁻⁴** (+2.114·10⁻⁸, +0.00282% over the five-stage
package's 7.49899215319498·10⁻⁴, recorded below). One stage is added after the terminal sinks: a **second concave-descent
retiming of the final transcript** (`descent2_transform.py`, `descent2-selection.json`), see the section *Post-sink
descent* at the end.

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

Thirteen fresh stages (virtual, raw, bit with descent/target/kernel/restore/sink/descent2, kernel, restore, sink, descent2, scalar, primes,
banks, complex, math, finite) with thirteen omitted-stage controls; all changed literals re-pinned in
`expected/kernel-pins.json` (recording mode refused under verify.py).

## Post-sink descent (second retiming after the terminal sinks)

The kernel, restoration and sink stages change many frames, so the final transcript is retimed again by greedy descent
of the deficit-fixed concave ledger Σ φ(r), φ(r) = r·ln(120/r) (PR #287's rule, rohanarun), with the union of move
types: a single ADD gate to a frame already on one of its operands' chains; to the constructed minimal join of its
operands' preceding chain frames or maximal meet of their following chain frames (PR #291's constructed frames; the
extreme meet/join frames of #286/#289 — for a single gate these are the only optima of the concave cost); to the join
with the operand source span; and connected blocks of chain-adjacent gates moved together to one frame (PR #270
plateau blocks; pairs, triples and runs up to 6 tried, only pairs pay). Search converges in two passes.

| move type | moves | gates |
| --- | ---: | ---: |
| operand-chain frame | 31 | 31 |
| constructed join/meet frame | 34 | 34 |
| connected pair block | 36 | 72 |
| **total** | | **113** (77 new bases) |

Local delta {1:+44, 2:+160, 3:−90, 4:−69, 5:+45, 6:+9, 7:−56, 8:−2, 9:+24, 11:−1, 12:−24, 14:+24, 16:−1, 17:+1, 18:−38,
19:+39}: 65 more local calls at unchanged rank mass 403,900; local φ-ledger −33.287 → predicted = verified κ
7.49920356821633·10⁻⁴. Five-stage calls 486,589 → 486,914, priced banked calls 482,635 → 482,960 (pinned). Registers, entrances,
endpoints, banks, scalar word unchanged.

Checks in `descent2_transform.py` (PR #287's `descent_transform.py` with endpoints generalised to the post-sink word):
byte-identical scalar/COPY projection, every register keeps its actual start and end frame (restored helpers keep
their early endpoints), nested chains with every MOVE rebuilt, unchanged COPY lifetimes, exact integer source span of
every non-target operand inside its new frame, nondegenerate endpoint bases, both reflected annihilator ledgers, and
an F₂ replay forward and inverse. `raw_ledger.rebind_descent2` recounts the profile and rechecks the deficit 4,400;
changed literals are pinned (`descent2_*`, `priced_five_stage_calls`, `kappa`). Discovery: `discovery/descent2_dump.py`,
`descent2_search.py`, `descent2_freeze.py`.
