# Handoff: e8-bit package

**Status.** `bash verify.sh <fresh dir>` passes end to end in about 2.5 minutes. `VERIFY-LOG.txt` is a clean run. The
final line is

    PASS conditional kappa = 875481145306751/1000000000000000000 = 0.000875481145306751 (complex-bound; bit coarse 452036410121261/500000000000000000 = 0.000904072820242522 )

## File map

| path | content |
| --- | --- |
| `data/bit/bitE8-r865.json.gz` | the word (format `bitE8/1`: lines, frames as root-line lists, start/final, ret, scatter, gate lists D/A/B/C) |
| `data/bit/RECORD-SHA256SUMS` | hashes of the exported PR249 records/states/frames |
| `code/bit/producer/` | the design code: `e8lib`, `frames`, `ham1`/`ham2` hierarchy, `compile`/`compile2` compiler, `fullword` (word + dirt + cleanup), `search2` (local search), `params-r865.json` |
| `code/bit/export_records.py` | bitE8 → PR249 records (MOVE/ADD/COPY/ERASE), B/A integer frame bases |
| `code/bit/independent/` | `checkword.py` (independent all-column checker), `mutate.py` (6 controls), `centres_sat.py` (no 8-centre decoder) |
| `code/bit/checkers/` | generalized official checkers: `legality_h.cpp`, `columns_h.cpp` (NCOPY); `gram_frames.py`; `geometry_g.py`; `tile_g.py`; `certify_bit_g.py` (+ `cost.py`); `finite_g.py` |
| `code/bit/regression/` | the unmodified PR #346/#352 sources the generalizations are compared against |
| `code/bit/receipts_e8.py`, `code/bit/mutate_records.py` | finite-bill inputs from this run's receipts; record-level controls |
| `code/complex/`, `code/pricing/` | PR #352's complex checks and PR #315's engines, unchanged |
| `code/secondary/` | PR #363's `bridged.py` (unchanged); `seven_stage.py` (κ under b₃; the bit word in B₃) |
| `data/regression-p10/` | PR #325 p10b base word (from #352's `data/bit`); agent G's p = 10 loans receipts (raw/scalar/banks/math/finite/global_result) |

## How the numbers relate

- **Bit side.** c = 9.0407e-4. The deficit is 120 = 4·120 − 5·72, and W = 1345.
- **κ under each complex supplier:**
  - with #352's b = 8.7625e-4: complex-bound, κ = 8.7548e-4;
  - with #363's seven-stage b₃ = 9.3278e-4: bit-bound, κ = 9.0326e-4 (reported, not claimed);
  - with a seven-stage *bit* layout (an estimate, c = 9.682e-4) and b₃: κ = 9.3191e-4.
- **Bit-side headroom.** The search stopped at R = 865 (`search2.py` plateau). Further gains on the bit side do not move
  κ while #352's complex supplier binds. Known slack:
  - about 500 dead non-host helper registers that could be reused;
  - frame retiming;
  - carriers for single lines (274).

## What a reviewer should look at

1. The NCOPY admission: 9 retained totals at h = 8. See the README section on retained totals.
2. PR234 for a non-paired-cube family. Port isometries are W(E8) reflection words, rational with denominators 2 and 4;
   every port route is checked as an exact elementary program with power-of-two denominators, so they are units modulo
   any odd prime. The original uses coordinate permutations.
3. Two finite-bill quantities, both computed by the original formulas:
   - K uses the identity chart only, since every helper starts at frame 0;
   - T = 1 replica, since all residual widths are h = 8 and 5 ∣ R.

## Regenerate

```sh
cd code/bit/producer && E8COORD=ham python3 -B fullword.py params-r865.json /tmp/w.json.gz       # the word
E8COORD=ham python3 -B search2.py SEED ITERS [start.pkl]                                        # the local search (pickle params)
```

Prepared by Dylan Crow, with Anthropic Claude assistance.
