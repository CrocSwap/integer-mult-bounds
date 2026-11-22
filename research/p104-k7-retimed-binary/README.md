# Conditional Retimed κ Improvement via Constructive Binary Graph Reduction (`seed_k7`)

The selected frontier remains on canonical `main`; independent scientific acceptance is open.

This package applies a constructive, verified binary-word improvement (`strong-bit-k7.json.gz`) onto the unpowered retimed multiplier architecture of PR `#8042` (`research/retimed-native-multiplier`, commit `dfd25d55`) and compares directly against the latest public endpoint PR `#8050` (`research/p104-retimed-dyadic-endpoint`, commit `328b858e`). Under the exact same inherited five all-size framework obligations and an **unmodified** 2-scale `(1, 8)` Gaussian receiver (`GAUSSIAN_C = 2092819/2^29`), replacing the PR `#8027` binary word lifts conditional `κ` across matched, compact, and extended operating profiles.

## Summary Comparison (`log2_fixed_setup_and_install_le = 513`)

| Profile / Prior Work | Model | `BINARY_C` | `GAUSSIAN_C` | Binary Stages (`rank_logs`) | `numerical_H` | Public Exponent `A` | Conditional `κ` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PR `#8035` (`ea776471`) | Powered 6-stage retimed | powered (`v=228`) | powered | 6 stages | `19,000` | `> 10^15` | `0.0038901152865907` |
| PR `#8042` (`dfd25d55`) | Unpowered 7-stage retimed | `4484997569314581/2^60` | `2092819/2^29` | 7 (`5.70e9`–`9.56e16`) | `19,000` | `101,973,332,976,357,367` | `0.003890115286594445` |
| PR `#8050` (`328b858e`) | Unpowered 7-stage dyadic endpoint | `287039844436133239/2^66` | `2092819/2^29` | 7 (`2.00e12`–`3.36e19`) | `36,000` | `~3.58e19` | `0.003890115286594461` |
| **`present` `conservative-36k`** | Unpowered 2-stage retimed (`k7`) | `4391986206293/2^50` | `2092819/2^29` | **2 (`60,000`, `960,000`)** | `36,000` | `1,056,618` | **`0.003893947`** |
| **`present` `compact-1m`** | Unpowered 2-stage retimed (`k7`) | `4391986206293/2^50` | `2092819/2^29` | **2 (`60,000`, `960,000`)** | `1,000,000` | `2,020,618` | **`0.003898026`** |
| **`present` `extended-10m`** | Unpowered 2-stage retimed (`k7`) | `4391986206293/2^50` | `2092819/2^29` | **2 (`60,000`, `960,000`)** | `10,000,000` | `11,020,639` | **`0.003898163`** |
| **`present` `extended`** | Unpowered 2-stage retimed (`k7`) | `4391986206293/2^50` | `2092819/2^29` | **2 (`60,000`, `960,000`)** | `20,000,000` | `21,020,646` | **`0.003898171`** |

## What Changed in the Binary Word (`strong-bit-k7.json.gz`)

- Six documented constructive graph-rewrite rounds (`k=2..7`, recorded in `K7-STACK-LEDGER.json`) eliminate 7 `MOVE` instructions across the 36 `LOCAL` calls (`2803 -> 2796`), reduce dirty private clears (`3433 -> 3426`), add one delta chart pair (`2352 -> 2353`) while reducing total frame gates (`44,825 -> 44,734`), and reduce binary paid ports from `104,904` (linear sum `285,600`) to `104,652` (linear sum `284,592`) over the exact same `18,906` targets (linear sum `286,098`).
- In unpowered moment pricing, the raw binary crossing jumps from `~0.003890115286594` to above `4391986206293 / 2^50 ≈ 0.003900867368050`. Thus binary ceases to be the ceiling: `BINARY_C` requires only a 50-bit dyadic denominator (`2^50` vs `#8050`'s `2^66`) and only 2 tiny binary stages `(60_000, 960_000)`, leaving the unmodified Gaussian complex word (`GAUSSIAN_C = 2092819/2^29 ≈ 0.003898179158568`) minus `39/(256 * numerical_H)` as the active bound.
- Negative control: `check_binary_k7.py` extracts PR `#8027`'s original `strong-bit.json.gz` from `predecessor/predecessor-8030.tar.gz` and confirms it fails unpowered certification at `k7`'s `BINARY_C = 4391986206293/2^50`.

## Scope, Inherited Premises, and Restraint

1. **Five Inherited All-Size Framework Obligations** (unchanged from `#8027` / `#8030` / `#8035` / `#8042` / `#8050`):
   - `native_all_columns`
   - `owned_erasure_and_restoration`
   - `compiler_transfer`
   - `precision_and_tape_services`
   - `analytic_recovery`
2. **Finite Replay vs Production Size / Formal Proof**: The 8 executable modes verify finite register semantics, sparse weighted `mod 3` / `mod 9` transport, retimed moment couplings, clock/budget arithmetic, finite product (`-345550037539`), and profile consistency. They do **not** constitute production-scale payload execution or an independent theorem-prover (Lean 4) certificate for `seed_k7` or for the five inherited obligations.
3. **AI-Assistance Disclosure**: Circuit search tooling, package integration, and verification automation were built with AI assistance and validated directly through clean `TemporaryDirectory` installs and `scripts/research_package.py`.

## Verification

Run the official package validator from the repository root (`0618e75a22cec54d1651394ef83d088551b7f026` base):

```bash
python3.12 -IB scripts/research_package.py --package research/p104-k7-retimed-binary
```

Full official validator result:

- `PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)`
- `PASS_REGISTERED_RESEARCH_PACKAGE research/p104-k7-retimed-binary outcome=completed` in **`597.74 s`** total wall time across all 8 declared checks:

| Mode | Command | Declared Timeout | Observed Timing & Key Output |
| --- | --- | --- | --- |
| `binary` | `python3.12 -IB research/p104-k7-retimed-binary/verify.py binary` | `45 s` | `15.83 s` (`moves=2796`, `dirty=3426`, `paid=104652`, `cells=24`, `control_8027=rejected`) |
| `cost` | `python3.12 -IB research/p104-k7-retimed-binary/verify.py cost` | `35 s` | `7.07 s` (all 7 profiles checked against `RESULT.json`; `24` binary / `54` numerical pairs) |
| `schedule` | `python3.12 -IB research/p104-k7-retimed-binary/verify.py schedule` | `40 s` | `16.15 s` (`nested same-program stream restored both complete 2,048-row schedules`) |
| `install` | `python3.12 -IB research/p104-k7-retimed-binary/verify.py install` | `240 s` | `117.249 s` instrumented install + `fiscal_scans` (`peak resident bytes 663986176`) |
| `physical` | `python3.12 -IB research/p104-k7-retimed-binary/verify.py physical` | `280 s` | `137.93 s` (`binary=18906/104652`, `positive=105216/564144`, `extended_stop` at `H=20,000,000`) |
| `receiver` | `python3.12 -IB research/p104-k7-retimed-binary/verify.py receiver` | `400 s` | `237.38 s` (`physical cells 1112292`, `64800` noncommuting direct checks) |
| `slabs` | `python3.12 -IB research/p104-k7-retimed-binary/verify.py slabs` | `25 s` | `0.39 s` (`125062` charged movements, `Gaussian sibling base 128`) |
| `product` | `python3.12 -IB research/p104-k7-retimed-binary/verify.py product` | `135 s` | `57.0261 s` (`physical_product(EXTENDED)` at `numerical_H=20000000`, `product=-345550037539`) |

(Single-mode timings for `binary`, `cost`, `schedule`, `physical`, `receiver`, `slabs` were measured directly prior to the final `VERIFY.json` timeout tune; `install` instrumented seconds and `product` seconds are directly from the final `597.74 s` full `scripts/research_package.py` run.)

## Open next questions

1. **Gaussian Complex Word Optimization**: Because `seed_k7` raises raw binary capacity to `~0.003900867` while the unmodified PR `#8042` 2-scale `(1, 8)` Gaussian supplier caps at `GAUSSIAN_C = 2092819/2^29 ≈ 0.003898179`, improving or splitting the complex word offers a direct path toward `0.003900+`.
2. **Lean 4 / Independent Audit**: Formalizing the 7 removed binary `MOVE` transitions and independently verifying all five inherited all-size obligations remain open.
