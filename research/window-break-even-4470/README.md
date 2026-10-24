# Short label windows under the #4470 invoice: break-even line counts vs the Theorem B cap

**Optimistic model screen; no new κ, no supplier, no native word.** Under the
productive-helper accounting of the selected #4470 word, a shorter label window
h (fewer fresh axes d = h − 1 per thick stage) lowers the cost a line system may
pay per line. It also raises the number of lines per dimension the system needs.
For dense units with one deleted frame (the case of every built complex
supplier), the windows h = 3, 4, 5 and 7 need more lines per dimension than the
proven cap v/T ≤ 2^k′ + 1 of
[line-system-saturation](../line-system-saturation/README.md) (Theorem B) allows.
h = 6 misses by about 2%. So a "smaller fresh block" does not by itself pay.
The live cells are the even windows h = 6 and h = 8, and deleting more than one
frame.

## Model

[verify.py](verify.py) rebuilds the complex invoice of
[joint-helper-lattice](../joint-helper-lattice/README.md) (#4470) **exactly**
from its `RESULT.json` local data: 18 full calls, 16 pairs with prefix 7,
15 query shears per port, local helpers and local paid, and a centre of 8 jobs of rank 8.
The targets and paid histograms match bit for bit, and the root is
0.003020165977 (recorded rounding 0.00302015).

It then replaces E8/P112 by a line system with v lines of rank T, window h
(fresh block d = h − 1), decoder cost D, and k deleted lines that become centres:

- ports V = v − k, centre per call D − k (the E8 floor 72 − k of PR968), paid as T jobs;
- the same #4440 controller (main targets 1 + d(p+2), idle pairs d(j+1) → d(j+1)+1, V(p − 1) query shears);
- the #4470 local native word with counts scaled by V/112 and ranks by d/8, which keeps the exact mass neutrality of the fresh-axis work;
- p and a re-optimised (p = 3..40).

The surplus is then exactly **S = (p+2)(v − D) − V** (checked in exact arithmetic
on 16 instances). For E8/P112, (p+2)(v − D) − V = 18·48 − 112 = 752.

This is an optimistic screen, not a lower bound. It assumes that a native word
with free central shears exists for the new unit and that its local profile
scales like the E8 one. The dense estimate D = hT is used where no better
decoder is known.

## Results (RESULT.json)

Named systems, with (v, T, h, D) taken from
[char2-threshold](../char2-threshold/README.md) §2 and
[line-system-saturation](../line-system-saturation/README.md) §8:

| system | v | T | h | D | x = D/v | C | / record |
|---|---:|---:|---:|---:|---:|---:|---:|
| E8 P112 (selected) | 120 | 8 | 9 | 72 | .600 | .00302017 | 1.000 |
| E8 P111 (k = 9) | 120 | 8 | 9 | 72 | .600 | .00305122 | 1.010 |
| E8 P104 (k = 16, not built) | 120 | 8 | 9 | 72 | .600 | .00328625 | 1.088 |
| E7 | 63 | 7 | 7 | 49 | .778 | .00214394 | 0.710 |
| E7, two frames deleted | 63 | 7 | 7 | 49 | .778 | .00249251 | 0.825 |
| E6, D4, D5, D6, Z8 (ties) | | | | = v | 1 | 0 | 0 |
| E8+A3 | 140 | 11 | 11 | 121 | .864 | .00071929 | 0.238 |
| D16⁺ (256 spinors / Delsarte cap 557) | 496 / 557 | 16 | 17 | 272 | .548 / .488 | .00170 / .00196 | 0.565 / 0.649 |
| D24⁺ | 728 | 24 | 25 | 600 | .824 | .00039395 | 0.130 |

The P111 and P104 rows only show the model's dependence on V. They are not
claims about those words.

Dense units **at the Theorem B cap** (lines per dimension 2^k′ + 1 for odd h, 2^k′ for even h),
as a multiple of the record, for k = T, 2T and 3T deleted lines:

| h | cap v/T | dense x | k = T | k = 2T | k = 3T |
|---:|---:|---:|---:|---:|---:|
| 3 | 3 | 1 | 0 | 0 | – |
| 4 | 4 | 1 | 0 | 0 | 0 |
| 5 | 5 | 1 | 0 | 0 | 0 |
| 6 | 8 | .75 | 0.980 | 1.166 | 1.435 |
| 7 | 9 | .778 | 0.710 | 0.825 | 0.983 |
| 8 | 16 | .5 | 1.460 | 1.580 | 1.720 |
| 9 | 17 | .529 | 1.194 | 1.285 | 1.391 |

At k′ ≤ 2 a saturated dense unit has D = hT = v, so it has no saving at all,
whatever the accounting.

Break-even lines per dimension (k = T) to tie the record. Columns: h, needed v/T, cap.
3: 3.34 / 3; 4: 4.72 / 4; 5: 6.29 / 5; 6: 8.05 / 8; 7: 10.06 / 9; 8: 12.36 / 16;
9: 15.0 / 17 (E8 has 15); 11: 21.7 / 33; 13: 31.2 / 65; 15: 45.5 / 129; 17: 69.9 / 257;
19: 119.5 / 513. At h ≥ 21 no v/T up to 200 ties the record. The best known
systems above h = 9 (line-system-saturation §8.1: 12.7 at h = 11, 12.8 at h = 13, 31 at h = 17)
are far below these needs.

Compared with the pre-#4359 fit x\*(h) = .5385 − .01495(h − 9) used by
line-system-saturation, the new break-even dense ratio is much looser at short
windows (h = 7: .696 vs .568) and much stricter at long ones (h = 17: .243 vs .419).
Shorter windows help per line, but the cap on lines per dimension takes it back.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 scripts/research_package.py --package research/window-break-even-4470 --check-only
python3.12 scripts/research_package.py --package research/window-break-even-4470
```

`verify.py` takes about 3 minutes on one core and replays `RESULT.json`
(`--write` regenerates it). `test_verify.py` has rejecting controls (a changed helper count,
a dropped centre, a wrong pair count) and positive controls (a tie unit has no saving,
the saving grows with lines per dimension, the Theorem B caps, the root lies near S/G).

## Limits

- The scaled local word is a proxy. A real native word for E7 or a new unit can price differently,
  and its central shears may not be free.
- Only dense pairings and the D − k centre rule are modelled. Sparser admissible pairings
  (line-system-saturation §11.4) and overcomplete decoders are outside this screen.
- The BIT side (κ = min(complex, BIT)) is not rebuilt. A complex gain above the BIT gate
  needs the same change there.
- The overlap search (`scripts/find_overlap.py`, 2026-10-23, open PRs and discussions refreshed,
  closed PRs from a 2026-10-18 cache) found the earlier paper-side screens (#2244, #2873,
  discussion #3622) and no re-pricing of label windows under the #4470 invoice.

## Open next questions

1. **Even windows h = 6 and h = 8.** Does a saturated even-window system exist (v = 8T with
   1 ∈ col Ā at k′ = 3, or v = 16T at k′ = 4)? These are the only short windows whose
   cap clears the record here. h = 6 needs two deleted frames (×1.17 at the cap),
   h = 8 needs 12.4 of the 16 allowed lines per dimension. First step: extend the
   realisability numerics of line-system-saturation §10 to even windows.
2. **Deleted frames.** Is the centre floor D − k attainable beyond one deleted frame? The h = 6
   and h = 7 verdicts change between k = T and k = 2T or 3T, and for E8 only P112 and P111 are built.
   First step: state the E7 analogue of the PR968 floor and test it on the 63-line unit.

## Credit

Prepared by Mark (Matarener) with substantial Claude Code (Claude) assistance.
It uses the #4470 invoice of joint-helper-lattice (built on zxv's native supplier and the
PR4440/PR4441/PR4447 contributions credited there),
the cost table of char2-threshold and the Theorem B cap and construction table of
line-system-saturation, all unchanged and referenced without vendoring. New work is Apache-2.0.
