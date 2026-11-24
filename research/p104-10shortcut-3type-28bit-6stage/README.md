# Ten-Shortcut 3-Type Gaussian Word + Periodic-Integral Suffix at 28-Bit 6-Stage (Full `256/255` Reserve)

**Label: enlarged budget (resource tradeoff).** This package extends [#8094](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) (`kappa = 0.003900857267786`) — while **retaining the full `256/255` ordinary summation reserve** instead of `#8082`'s reserve-drop heuristic — by stacking:

1. **Five new pure-identity chart-3 relays (`w5664_shortcut10.json.gz`, `5,674 -> 5,664` transfers):** Building on `#8088`'s 5 relays + 44 chart-3 re-encodings, we identify and eliminate 5 additional single-term chart-3 relays `(95397, 95845)`, `(96740, 96744)`, `(96274, 96750)` (sign `-1`), `(96263, 100093)` (sign `-1`), `(95405, 100650)` as synthetic moves `104494..104498`. Verified by 3-prime forward + transpose linear equivalence, exact `literal_grid` (`25,142,049` products), and 2,961-pair Clifford catalogue (`check_w5664.py`).
2. **Three-type `(1, 2, 3)` Gaussian producer (`WEIGHTS = (1, 45, 2025)`):** Lifts `GAUSSIAN_C` to `17166573920/2^42 = 0.003903227006958` (`POSITIVE_DEBIT = 32401/262144`, `LOWER = 1164`, `UPPER_DIVISOR = 1724`, `ambient = 459`, `actual_roles = 1,002,096 < 2^20`, `grade_count = 72 < 2^8`).
3. **Exact Periodic-Integral `(1 - delta)` Suffix Theorem + `#8076` `2401/1024` Child Tariff (with FULL `256/255` reserve):** At optimal `ORDINARY_FLOOR = 1156`, yields `ORDINARY_DEBIT = 1418665/2^20`, strictly below `#8090`/`#8094`'s `1420718/2^20` even without dropping `256/255`.
4. **Sharp 28-bit (`w = 2^38`) 6-stage `eta = 1/256` allocation (`SETUP-28BIT.md`):** Because `1024 * (2^28 - 1) + 3 = 274,877,905,923 < 2^38 < 1024 * 2^28 + 3`, `H < 2^28` is the exact sharp limit of `#8081`'s `w = 2^38` datum premise. A 6-stage chain `(8192, 63614, 1005821, 15903360, 251454111, 268435455)` with `G = 52,270` reaches **κ = 0.003900862325217** (`complete_log2_C = 171,810,078,109`), strictly beating `#8094` (`0.003900857267786`) by `+5.057431e-9` and halving the remaining gap to `BINARY_C = 0.003900867368050`.

## Verified Benchmark Table (All Controls Retain Full `256/255` Reserve)

| Matched Ceiling / Tier | Schedule `(H_1, ...; G)` | Regime / Cap | Our `κ` | Our `complete_log2_C` | Comparator PR & `κ` (`log2_C`) |
|---|---|---|---|---|---|
| **Primary (28-bit 6-stage)** | `(8192, 63614, 1005821, 15903360, 251454111, 268435455; 52270)` | `η=1/256`, `w=2^38` | **0.003900862325217** | **171,810,078,109** | **#8094**: `0.003900857267786` (`85,945,126,846`) |
| 27-Bit 5-Stage (`#8094` cap) | `(31808, 502922, 7951910, 125730700, 134217727; 52158)` | `η=1/256`, 27-bit | **0.003900857282381** | **85,910,697,946** | **#8094**: `0.003900857267786` (`85,945,126,846`) |
| 25-Bit 4-Stage (`#8090` cap) | `(125432, 1988431, 31439869, 33554431; 51501)` | `η=1/256`, 25-bit | **0.003900827024476** | **21,485,944,123** | **#8090**: `0.003900826966095` (`21,518,289,843`) |
| `#8089` Match (`κ = 0.0039`) | `(8192, 106000, 1656186; 38302)` | `η=1/256`, `m=3` | **0.0039** | **574,949,140** | **#8089**: `0.0039` (`593,252,820`) |
| 20-Bit Cap (`H <= 2^20-1`) | `(62350, 985843, 1048575; 33856)` | `η=39/10000`, 20-bit | **0.003899576196608** | **678,415,820** | **#8088**: `0.003899574328473` (`685,495,960`) |
| Strict `#8073`/`#8072` Cap | `(26960, 426219, 524288; 25003)` | `η=39/10000`, `<=318291911` | **0.003898283457829** | **318,291,840** | **#8073**: `0.003898219753506` (`318,291,911`) |

## Verification Commands

```sh
python3.12 -IB scripts/research_package.py --package research/p104-10shortcut-3type-28bit-6stage
```

Or directly inside this directory:

```sh
for mode in price calendar raw exterior nested product setup; do python3.12 -IB verify.py $mode; done
```

## Open next questions

With `H < 2^28` hitting the sharp `1024 * H + 3 < 2^38` datum limit and sitting within `5.043e-9` of `BINARY_C = 0.003900867368050`, can constructive transfer reductions in `strong-bit` raise `BINARY_C` without relaxing the five signed premises?
