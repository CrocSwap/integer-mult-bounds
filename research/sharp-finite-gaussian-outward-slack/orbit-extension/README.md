# Bounded W(D4) orbit-flow sweep

This package records exact finite matching evidence for (U=H_4/2), error
cap one, on only the Gaussian integer balls (S_R) with (R=6,7,9,11).
The script constructs sorted-absolute-coordinate/product-sign orbit
representatives and their exact (W(D_4)) capacities; it never enumerates all
points and then applies 192 group elements.

## Results

| Radius | Inputs / candidate outputs | Tested threshold | Threshold flow / inputs | Exact finite optimum | Strict optimum cut \(|T|/|N(T)|\) |
|---:|---:|---|---:|---|---:|
| 6 | 6,577 / 10,713 | \(\sqrt{21}-\sqrt{19}\) (inherited beta_2) | 6,545 / 6,577 | \(\sqrt{31}-\sqrt{28}\) | 3,569 / 3,537 (deficit 32) |
| 7 | 11,833 / 18,457 | \(\sqrt{43}-\sqrt{39}\) (beta_3) | 11,833 / 11,833 | \(\sqrt{31}-\sqrt{28}\) | 3,569 / 3,537 (deficit 32) |
| 9 | 32,633 / 46,401 | \(\sqrt{73}-\sqrt{67}\) (beta_4) | 32,633 / 32,633 | \(\sqrt{78}-\sqrt{73}\) | 23,561 / 23,497 (deficit 64) |
| 11 | 72,465 / 96,449 | \(\sqrt{111}-\sqrt{103}\) (beta_5) | 72,465 / 72,465 | \(\sqrt{78}-\sqrt{73}\) | 23,561 / 23,497 (deficit 64) |

The exact orbit-flow and Hall-cut receipts, including every orbit capacity,
positive quotient flow, and complete cut neighborhood, are in
[`RESULT.json`](RESULT.json). A quotient matching lifts to a full finite
injection by distributing each orbit-pair flow uniformly over its
biregular edge set and applying Hall's theorem; the proof is in
[`PROOF.md`](PROOF.md).

## Replay

From this directory, run:

```sh
python3 -I -B sweep.py > /tmp/finite-radii-result.json
cmp /tmp/finite-radii-result.json RESULT.json
python3 -I -B verify.py
python3 -I -O -B verify.py
```

`verify.py` checks flow conservation, orbit capacities, target and optimum
cuts, exact complete neighborhoods, and two deliberately corrupted
certificates. Its default behavior reads the saved receipt and emits a
summary. The bounded gap search checks 380, 608, 1,287, and 2,346 distinct
attainable radicals at radii 6, 7, 9, and 11, using 9, 10, 11, and 12 exact
flow probes respectively. The sweep result is byte-identical under normal
and optimized Python execution; the frozen output hashes are in FREEZE.md.

No PR is proposed from these bounded radius checks alone. The results are
finite evidence only and do not establish a pattern for other radii or a
global construction.
