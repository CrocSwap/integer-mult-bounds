# Production cached update columns for the historical data-corner checker

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`research/copied-fixed/data_corners.cpp` still rescanned all 47 columns for
every lower-row update. The opt-in adapter `research/data-corner-performance/`
already proved an exact per-pivot cached-column list with identical receipts.
This package wires that equivalent loop into the **production** checker used by
`research/copied-fixed/producer.py` / `make copied-fixed-verify`.

Only the `local_sha256` entry for `research/copied-fixed/data_corners.cpp`
changes inside `research/copied-fixed/certificate.json`. The complete domain of
4,073,300 pairs, every assertion, modular fallback recovery and the pinned
`data-corners.json` receipt stay identical. Selected frontier untouched.

The pairwise-era digest in `research/data-corner-performance/SOURCE.json` is
demoted: that package now vendors `baseline.cpp` and treats working
`data_corners.cpp` as the optimized production source, so research-packages /
local replay do not fail working-source drift.

## Reproduce

Python **3.12**, a C++17 compiler (`CXX`, default `c++`), standard library only,
from the repository root:

```sh
python3.12 -I -B research/data-corner-production/verify.py
python3.12 -I -O -B research/data-corner-production/verify.py
python3.12 -B scripts/research_package.py --package research/data-corner-production
python3.12 -I -B research/data-corner-production/benchmark.py --rounds 5 --out /tmp/data-corner-production-result.json
```

Expected:

```text
PASS_DATA_CORNER_PRODUCTION pairs=4073300 good=4073290 fallback=10 corruption=… certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/data-corner-production outcome=completed
PASS_IDENTICAL_DATA_CORNER_PRODUCTION_RECEIPTS
```

Default verify is read-only. Temp-copy column-fill foil rejects via receipt
mismatch or subprocess failure. Package gates under `-O` still launch
assertion-enabled C++ children (`NDEBUG` is rejected at compile time). Full
`make verify`, selected cold replay, Lean, and multiplication-theorem
obligations were not rerun for this isolated historical-checker change.

## Result

On Linux / CPython 3.12.3 with g++ (taskset CPU 0), five alternating
fresh-process pairs gave median wall time **170.101 → 110.463 seconds
(1.54×)**. Timing is host-descriptive and is not a correctness gate; all
samples and environment pins are in [`RESULT.json`](RESULT.json). Every stdout
receipt matches the pinned `data-corners.json` fieldwise. An unpinned multi-core
screen on the same host was noisier (~1.38×); the reported figure is the pinned
five-pair series.

## Why the cached columns are equivalent

After accepting pivot `(i,c)`, neither `available` nor pivot row `M[i]` changes
during the lower-row update loop. Collecting

```text
columns = [j | available[j] && M[i][j]]
```

once per pivot, then iterating that list for every lower row `r` with
`M[r][c] != 0`, performs the same modular updates in the same column order as
the historical nested scan. See `research/data-corner-performance/README.md`.

## Overlap and credit

Closest priors (different delivery):

- `research/data-corner-performance/` — opt-in cached-column adapter; this is
  the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2039/#2054
  shared-point, #2100 ternary, #2117 DisjointTensor, #2150 mixed-point,
  #2194/#2210/#2231/#2239/#2257/#2263/#2276 production rewrites; #1076
  quadratic-affine) was not reopened. Soft note: #2263/#2276 touch
  `e8-bit-r420/MANIFEST.sha256`; this tip does not.

Credit the authors of `research/data-corner-performance/` and the copied-fixed
lineage. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should adjacent historical copies under `research/pair-assembly/`,
   `research/skip-strips/`, and `research/split-skip/` adopt the same cached
   columns in a follow-up tip?
   **Why it matters:** Those trees still pin pairwise-era digests without a
   registered VERIFY matrix; a coordinated refresh would remove stale inventory
   digests without changing receipts.
   **First step:** Diff each `data_corners.cpp` against the production transform
   site and list which SOURCE inventories would need provenance demotion.
   **Blocked by:** Out of this session’s one-object stop rule.

2. **Question:** Should `make copied-fixed-verify` grow a microbenchmark gate
   for the full 4,073,300-pair replay?
   **Why it matters:** A future edit could restore the nested scan without
   failing equivalence tests.
   **First step:** Decide whether RESULT.json medians belong in CI or remain
   descriptive.
   **Blocked by:** Maintainer CI-budget preference.
