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
| kernel | `kernel-selection.json` | response-kernel entries: twin pairs (PR254/#268) and multi-donor families (#272), per-entry cuts, shared donors on nested chains, multi-seed restart packing (#300) | 775 entries (536 pairs, 239 families), total entrance rank 970 |
| restore | `restore-selection.json` | early helper restoration (#280, endpoint-aware #283) | 240 helpers (16, 18, 18, 19), endpoint saving 240 |
| sink | `sink-selection.json` | terminal sinks (#283 rule, #295 screen) | 7 sinks, delta {3:−7, 17:−7}, R 8,230 → 8,223 |
| reorder | `reorder-selection.json` | reordering single additions into a neighbouring incidence frame (#299) | 133 moves, delta {2:+73, 3:−113, 4:+20, 17:−113, 18:+113} |

The kernel packing excluded the seven helpers that the sink screen admits on the post-target word: on that word
the screen finds 7 sinks, and an unrestricted packing consumes 3 of them as kernel members (φ −1,360.3 with 4 sinks
left). The restricted packing (φ −1,355.95) keeps all 7, which is worth more (κ 7.68799e-4 against 7.68628e-4
after the sink stage).

Searched and empty on this word (not stages): a second concave descent (`discovery/descent2_search.py`, with the
#291 constructed join/meet frames and #270 connected blocks) finds 0 gates after the sinks and 0 after the
reorder; a second reorder round finds 0 moves.

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
the restoration saving must be a multiple of 5 for the width-100 banks to tile exactly (970 + 240 = 1,210).
