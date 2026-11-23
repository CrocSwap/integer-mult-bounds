# Proof Summary: `w5664` 3-Type Gaussian + Periodic-Integral Suffix at 28-Bit 6-Stage

## 1. Ten-Shortcut Word `w5664_shortcut10.json.gz`

On top of `#8088`'s `w5669_shortcut5.json.gz` (`5,669` moves, synthetic moves `104489..104493`, 44 re-encoded chart-3 inputs/consumers), five remaining chart-3 transfer pairs satisfy `len(form[my]) == 1` with `form[my][0] == [mx, ±1]`, `move[mx] = (a, b)`, and `move[my] = (b, c)`:
- `(95397, 95845): 735 -> 798 -> 1079` (`sign = +1`), replaced by `104494`
- `(96740, 96744): 519 -> 1028 -> 1069` (`sign = +1`), replaced by `104495`
- `(96274, 96750): 573 -> 1038 -> 1043` (`sign = -1`), replaced by `104496`
- `(96263, 100093): 572 -> 1037 -> 1042` (`sign = -1`), replaced by `104497`
- `(95405, 100650): 1089 -> 795 -> 898` (`sign = +1`), replaced by `104498`

`check_w5664.py` verifies invariance of `initial`, `final`, `frames`, and `first_output`, exact forward and transpose linear operators over 3 primes, the complete `25,142,049`-product `literal_grid` (`rem == 0`), and the `2,961`-pair Clifford catalogue (`digest = 34eef62b6701db0565dce3471f165f4224194ff2782be822774f9c1255553a8d`).

## 2. Three-Type `(1, 2, 3)` Gaussian Transport (`WEIGHTS = (1, 45, 2025)`)

Combining `w5664` with `SCALES = (1, 2, 3)` and `WEIGHTS = (1, 45, 2025)` (`ambient = 459`, `actual_roles = 1,002,096 < 2^20`, `grade_count = 72 < 2^8`) lifts `GAUSSIAN_C` to **`17166573920/2^42 = 0.003903227006958`** (`17166573921/2^42` fails). Applying the exact periodic-integral `(1 - delta)` suffix bound at `(LOWER = 1164, UPPER_DIVISOR = 1724, scale = 395658)` gives `fringe = 4.556149` and **`POSITIVE_DEBIT = 32401/262144`** (`64801/524288` fails).

## 3. Exact Periodic-Integral Ordinary Suffix + `#8076` Tariff + Full `256/255` Reserve

For K7 binary transport at `ORDINARY_FLOOR = 1156`, the periodic-integral `(1 - delta)` theorem gives `fringe = 4.525997`. Pairing `#8076`'s `CHILD_TARIFF = 2401/1024` (contraction `2400/2401`, geometric sum `2401`, clock extras `+5` entry / `+3m = +18` terminal) while **retaining the full `256/255` summation reserve** gives `ordinary_upper = 2.55432838...`, proving **`ORDINARY_DEBIT = 1418665/2^20`** (`1418664/2^20` fails), strictly below `#8094`'s `1420718/2^20` without dropping `256/255`.

## 4. Sharp 28-Bit 6-Stage `TERMINAL` & 5-Tier Controls

Under [`SETUP-28BIT.md`](SETUP-28BIT.md) (`1024 * (2^28 - 1) + 3 = 274877905923 < 2^38`, 10 recipes with `2*2048*(2^25+1) + 10*2^24 = 137606729728 < 2^40`, `G = 52270 < 2^25`), the 6-stage `TERMINAL = Profile((8192, 63614, 1005821, 15903360, 251454111, 268435455), 52270, Q(".003900862325217"), Q(1, 256))` proves:
- `kappa = 0.003900862325217` (`+5.057431e-9` above `#8094`'s `0.003900857267786`),
- `G = 52,270` (`4×` smaller than `#8094`'s `208,653`),
- `complete_log2_C = 171,810,078,109`,
and `check_stage_seam.py` certifies all 5 matched comparator tiers (`#8073` strict cap `0.003898283457829`, 20-bit `0.003899576196608`, `#8089` `0.0039`, 25-bit 4-stage `0.003900827024476`, 27-bit 5-stage `0.003900857282381`) alongside 20+ negative controls and stages `2..6` direct/compiled seams.
