# Transcript stages on the p = 10 word

#315 ships the p = 10 paired-cube bit word with no transcript stages: the parity-fused word goes straight to the
five-stage lowering. This package inserts the stage stack of the gen5 Python pipeline (#287, #290, #295, #299,
#306 lineage) between the parity fusion and the global lowering, re-derived on the p = 10 word. Every stage is a
callable transform with a frozen selection that is bound to the exact input word (raw-record and scalar-projection
SHA-256), and every stage is a mandatory proof stage of `verify.py` with its own receipt (`<stage>.json` in the
output directory). The stage list is `portable_bit.STAGES`:

    parity -> descent -> target -> kernel -> restore -> sink -> reorder -> five-stage lowering

## What changed from p = 12

The mechanisms and checks are unchanged. The p = 12 literals were replaced:

- h = 24, v = 1,760, m = 120, centre rank 22, 24 centres, 220 scatter reads and the deficit 4,400 come from
  `word_pins.shape()` (h = 20, v = 960, m = 100, centre rank 18, 20 centres, 144 scatter reads, deficit 2,040);
- counts that p = 12 asserted as literals (selected gates, local histogram deltas, five-stage calls and rank
  masses, entrance histograms, register counts) are pinned in `word-pins.json` through `word_pins.expect`, like
  #315's own word values. A pin name can hold only one value (`discovery/repin.py` rejects a second one).
- the search tools use φ(r) = r ln(100/r); the target-square search uses frame ranks h − 4 = 16 (prefix adds)
  and h − 3 = 17 (close frame).

## Stages

| stage | selection | mechanism (origin) | on this word |
| --- | --- | --- | --- |
| descent | `descent-selection.json` | concave frame retiming of ADD gates to frames on an operand chain (Rohan Arun, #287) | 480 gates, 480 calls removed, delta {1:−960, 2:+480, 16:−480, 17:+960, 18:−480} |
| target | `target-selection.json` | target-prefix squares (eumemic #268/#273, used in #287) | 120 groups, delta {1:−120, 16:−120, 17:+120} |
| kernel | `kernel-selection.json` | response-kernel entries (PR254/#268 pairs, #272 multi-donor families, per-entry cuts), selected as a shared-donor kernel (#319's idea): maximum-weight closure per entrance over alternate response bases (`discovery/coll/closure_pack.py`) | 1,047 entries, total entrance rank 1,200 (ranks 1:1,007, 2:20, 4:5, 5:3, 7:1, 8:3, 10:6, 13:1, 14:1); 1,015 distinct donors, 1–31 donors per entry, a donor shared by up to 30 entries |
| restore | `restore-selection.json` | early helper restoration (#280, endpoint-aware #283) | 240 helpers (16, 18, 18, 19), endpoint saving 240 |
| sink | `sink-selection.json` | terminal sinks (#283 rule, #295 screen) | 7 sinks, delta {3:−7, 17:−7}, R 8,230 → 8,223 |
| reorder | `reorder-selection.json` | reordering single additions into a neighbouring incidence frame (#299) | 133 moves, delta {2:+73, 3:−113, 4:+20, 17:−113, 18:+113} |

**Shared-donor kernel.** For an entrance E (a nondegenerate rank-e subspace) let G_E be the plain helpers whose
first frame contains E. A pivot p in G_E gains φ(d_p − e) − φ(d_p); a donor d pays φ(e) + φ(d_d − e) − φ(d_d)
once, however many entries it serves at E (its path ZERO → E → first frame is the same for every entry). Choosing
a response basis of G_E at a common cut point (all members read before it and untouched until after it), every
dependent member is a candidate pivot whose donors are its basis representation; picking pivots and donors is then
a maximum-weight closure (pivot → its donors), solved exactly by a minimum cut. The search tries several
cost-ordered bases and cut points per entrance, over 24,203 rank-one lines and 10,541 exact pairwise frame
intersections of rank 2–14, and accepts entrances greedily with helper exclusivity (randomised acceptance order,
best of 16 seeds). The transform is #320's `kernel_transform.py` unchanged in mechanism (entries with any number of
donors, a donor reused along a nested chain); the selection gives φ −1,601.47 against #320's packing −1,355.95.
The seven helpers the sink screen admits are excluded (they are worth ≈ −40 φ each as sinks), and the total
entrance rank is trimmed to a multiple of 5 for the width-100 banks. The restorations (240), sinks (7) and reorder
(133) were re-derived on the new word with #320's builders and have the same deltas as in #320.

Searched and empty on this word (not stages): a second concave descent (`discovery/descent2_search.py`, with the
#291 constructed join/meet frames and #270 connected blocks) finds 0 gates after the sinks and 0 after the
reorder; a second reorder round finds 0 moves; a second shared-donor kernel round after the reorder finds 4 entries
(φ −0.77). #312's zero-response singles do not exist here (every plain helper has a nonzero response), and #309's
local dirty-response transport has no positive closure (targets' next frames have rank 16–18 and admit at most one
helper per entrance).

## What each stage checks

- **descent**: every retimed frame is nondegenerate, nests between its operand neighbours and contains the exact
  integer source span of each non-target operand (recomputed from the actual word); scalar and COPY projection
  unchanged; every required frame path rebuilt from scalar/COPY events, both reflected ledgers; rank mass unchanged.
- **target**: literal prefix responses are checked (no selected dependency is trusted); all formal columns
  replayed forward and inverse over F₂; omitting the target-prefix setup is rejected.
- **kernel**: the prefix relation (pivot response = XOR of donor responses) on the literal prefix for every
  entry; every member untouched before its own cut; entrances nondegenerate inside every member's first frame;
  shared-donor chains nested; F₂ replay of every formal column forward and inverse with both omission controls;
  every frame path rebuilt independently of the emitted MOVEs.
- **restore**: the PR280 screen is recomputed on the actual word and must equal the frozen selection; the integer
  commutation contract on the crossed interval; F₂ replay forward/inverse and an omission control; the five-stage
  completion of a restored helper is P_σ + (I − P_E) (rank a + h − dim E), and the banks chart the pair (σ, E).
- **sink**: the PR283 screen with the stricter #295 conditions; F₂ replay with controls; registers compacted, the
  stock and the five-stage profile recomputed, the deficit 4v − 5h(h − 2) rechecked.
- **reorder**: source spans of every gate rechecked, integer replay identical, F₂ replay with controls,
  endpoints, entrances and rank mass unchanged.

The raw ledger is rebound after every stage (`raw_ledger.rebind_*`, `target_transform.rebind`): the helper
histogram is recomputed from the stage receipt and compared with the frozen expected delta, and the five-stage
profile and deficit are rechecked. `finite_check.py` re-asserts every executed stage receipt (both reflected
ledgers, pinned counts, rejected controls) and that the raw ledger holds exactly one receipt per stage.

## Downstream changes

- `code/global_lowering.py`: completions use the helper endpoint (P_σ + I − P_E for restored helpers); the
  register count is the final one (`final_physical_R`, after the sinks).
- `code/geometry527.py`: #315 already checks one actual basis of every entrance rank, so the kernel ranks
  (1, 2, 4, 5, 7, 8, 10, 13, 14) are covered; one restored (σ, E) pair is checked exactly (residual P_E − P_σ,
  completion P_σ + I − P_E, the old FULL formula rejected).
- `bank_check.py`: charts for restored helpers are keyed by (σ, E), with the E-perp rows (`residual_rows`).
- `bank_template.py`: see `BANK-PROOF.md` (economy tiling).
- `prime_check.py`: retimed-away producer frames keep their determinant obligation.
- `scalar_check.py`: the retained source program is checked on its 10,150 columns; the emitted word (after
  the sinks) on its 10,143 columns.
- `math_check.py`, `finite_check.py`: the completion-rank histogram replaces the entrance histogram where
  completions are removed from the priced profile.

## φ ledger and verified values

The deficit is fixed (4v − 5h(h − 2) = 2,040 per replica), so κ is a function of the one-stage helper histogram:
the five-stage profile without completions, normalized ×12, W = (mass + 12·2,040)/100. Each stage was predicted
with this ledger from its frozen local delta before it was built, and verified by a full `verify.replay` of the
package truncated after that stage (record mode). See `README.md` for the table. The total entrance rank plus
the restoration saving must be a multiple of 5 for the width-100 banks to tile exactly (1,200 + 240 = 1,440).
