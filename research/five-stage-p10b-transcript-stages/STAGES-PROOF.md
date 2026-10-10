# Transcript stages on #325's p = 10 word

#325 ships a stronger p = 10 paired-cube bit word (re-annealed pair module, p = 10 local design, balanced cube
orientation, tiered reuse matching) with no transcript stages: the parity-fused word goes straight to the
five-stage lowering. This package inserts the stage stack of our #320 (the gen5 Python pipeline of #287, #290,
#295, #299, #306 lineage) between the parity fusion and the global lowering, re-derived on #325's word. Every stage
is a callable transform with a frozen selection that is bound to the exact input word (raw-record and
scalar-projection SHA-256), and every stage is a mandatory proof stage of `verify.py` with its own receipt
(`<stage>.json` in the output directory) and an omission control. The stage list is `portable_bit.STAGES`:

    parity -> descent -> target -> kernel -> restore -> sink -> descent2 -> reorder -> reorder2 -> five-stage lowering

Relative to #320 two stages are new on this word: the post-sink descent (`descent2`, 47 gates; it found 0 gates on
#315's word, so #320 shipped without it) and a second reorder round (`reorder2`, 2 moves; 0 on #315's word). Both
transforms, their raw-ledger rebinds and their receipt checks are from the p = 12 gen5b pipeline (#299, #306) as
ported to p = 10 for #320's development; they are unchanged here except that `raw_ledger.rebind_descent2` is placed
after the sinks.

## Stages

| stage | selection | mechanism (origin) | on this word |
| --- | --- | --- | --- |
| descent | `descent-selection.json` | concave frame retiming of ADD gates to frames on an operand chain (Rohan Arun, #287) | 480 gates, 480 calls removed, delta {1:−960, 2:+480, 16:−480, 17:+960, 18:−480} |
| target | `target-selection.json` | target-prefix squares (eumemic #268/#273, used in #287) | 120 groups, delta {1:−120, 16:−120, 17:+120} |
| kernel | `kernel-selection.json` | response-kernel entries (PR254/#268 pairs, #272 multi-donor families, per-entry cuts) selected as a shared-donor kernel (#319's idea, #320's closure search) | 1,339 entries, total entrance rank 1,445 (ranks 1:1,296, 2:26, 4:7, 5:3, 7:2, 8:5); 1,128 distinct donors, 1–15 donors per entry, a donor shared by up to 13 entries; delta {1:+2,591, 2:−511, 3:−935, 4:+45, 5:−43, 6:−12, 7:+6, 8:+7, 10:−20} |
| restore | `restore-selection.json` | early helper restoration (#280, endpoint-aware #283) | 240 helpers (16, 18, 18, 19), delta {1:+720, 2:−480} |
| sink | `sink-selection.json` | terminal sinks (#283 rule, #295 screen) | 10 sinks, delta {3:−10, 17:−10}, R 8,100 → 8,090 |
| descent2 | `descent2-selection.json` | post-sink concave retiming with #291 constructed join/meet frames and #270 connected blocks (#299) | 47 gates (5 constructed, 21 pair blocks), delta {1:+15, 2:+3, 3:+21, 4:−13, 5:−34, 7:−8, 8:−5, 9:+26}, φ −49.68 |
| reorder | `reorder-selection.json` | reordering single additions into a neighbouring incidence frame (#299) | 130 moves, delta {2:+90, 3:−112, 5:−16, 7:+18, 17:−110, 18:+110}, φ −296.89 |
| reorder2 | `reorder2-selection.json` | second reorder round (#306) | 2 moves, delta {2:−4, 4:+2}, φ −5.55 |

**Shared-donor kernel.** As in #320: for an entrance E let G_E be the plain helpers whose first frame contains E; a
pivot gains φ(d_p − e) − φ(d_p), a donor pays φ(e) + φ(d_d − e) − φ(d_d) once however many entries it serves at E;
picking pivots and donors at a common cut point is a maximum-weight closure, solved by a minimum cut over several
cost-ordered response bases, and entrances are accepted greedily with helper exclusivity. On #325's word every
plain helper's last dirty read precedes every helper's first touch (census: max last read 296,639 < min touch
296,641), so common cut points always exist; the census has 6,900 plain helpers, 24,127 rank-one lines and 7,045
pairwise frame intersections of rank 2–14. Eighteen seeds (unrandomised and noise 0.3) reach φ −2,376.0 to
−2,376.81 (upper bound of independent line closures 2,418); the frozen selection is the unrandomised run trimmed
to a total entrance rank divisible by 5 (φ −2,376.62). The ten helpers the pre-kernel sink screen admits
(streams 6947, 7141, 7519, 7789, 7793, 8407, 8437, 8501, 8647, 8677) are excluded: without the exclusion the
closure gains 7.9 φ more but consumes seven of them (≈ −40 φ each as sinks).

Searched and empty or negligible on this word (not stages): a late shared-donor kernel round after the reorders
(one rank-2 entry, φ −0.19, removed by the rank-5 trim); eumemic's #322 pre-sink retiming is the same descent
search as `descent2` (it finds the same 47 gates before or after the sinks); #323's late rank-two kernels have no
positive closure here.

## What each stage checks

- **descent, descent2**: every retimed frame is nondegenerate, nests between its operand neighbours and contains the
  exact integer source span of each non-target operand (recomputed from the actual word); scalar and COPY
  projection byte-identical; every required frame path rebuilt from scalar/COPY events, both reflected ledgers;
  rank mass unchanged; for descent2, every register keeps its actual start and end frame (restored helpers keep
  their early endpoints) and the word is replayed over F₂ forward and inverse.
- **target**: literal prefix responses are checked; all formal columns replayed forward and inverse over F₂;
  omitting the target-prefix setup is rejected.
- **kernel**: the prefix relation (pivot response = XOR of donor responses) on the literal prefix for every entry;
  every member untouched before its own cut; entrances nondegenerate inside every member's first frame;
  shared-donor chains nested; F₂ replay of every formal column forward and inverse with both omission controls;
  every frame path rebuilt independently of the emitted MOVEs.
- **restore**: the PR280 screen is recomputed on the actual word and must equal the frozen selection; the integer
  commutation contract on the crossed interval; F₂ replay forward/inverse and an omission control; the five-stage
  completion of a restored helper is P_σ + (I − P_E) (rank a + h − dim E), and the banks chart the pair (σ, E).
- **sink**: the PR283 screen with the stricter #295 conditions; F₂ replay with controls; registers compacted, the
  stock and the five-stage profile recomputed, the deficit 4v − 5h(h − 2) rechecked.
- **reorder, reorder2**: source spans of every gate rechecked, integer replay identical, F₂ replay with controls,
  endpoints, entrances and rank mass unchanged.

The raw ledger is rebound after every stage (`raw_ledger.rebind_*`, `target_transform.rebind`): the helper
histogram is recomputed from the stage receipt and compared with the frozen expected delta, and the five-stage
profile and deficit are rechecked. `finite_check.py` re-asserts every executed stage receipt and that the raw
ledger holds exactly one receipt per stage.

## Downstream changes (from #320, unchanged)

- `code/global_lowering.py`: completions use the helper endpoint (P_σ + I − P_E for restored helpers); the register
  count is the final one (`final_physical_R`, after the sinks).
- `code/geometry527.py`: one actual basis of every entrance rank is checked; one restored (σ, E) pair is checked
  exactly (residual P_E − P_σ, completion P_σ + I − P_E, the old FULL formula rejected).
- `bank_check.py`: charts for restored helpers are keyed by (σ, E), with the E-perp rows (`residual_rows`).
- `bank_template.py`: the economy tiling (`BANK-PROOF.md`, last section).
- `prime_check.py`: retimed-away producer frames keep their determinant obligation.
- `scalar_check.py`: the retained source program is checked on its 10,020 columns, the emitted word (after the
  sinks) on its 10,010 columns.
- `math_check.py`, `finite_check.py`: the completion-rank histogram replaces the entrance histogram where
  completions are removed from the priced profile.

## φ ledger and verified values

The deficit is fixed (4v − 5h(h − 2) = 2,040 per replica), so the bit root is a function of the one-stage helper
histogram: the five-stage profile without completions, normalized ×12, W = (mass + 12·2,040)/100. Each stage was
predicted with this ledger (calibrated on #325's own raw ledger, which it reproduces exactly) from its frozen local
delta, and verified by a full `verify.replay` of the package truncated after that stage (record mode). Every
verified bit root and κ equals its prediction exactly; see `README.md` for the table.
