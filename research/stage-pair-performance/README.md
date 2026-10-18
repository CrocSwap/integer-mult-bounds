# Stage-pair audit performance

Exact-only speedup of the historical two-invocation frame search
(`scripts/audit_stage_pair.py`, h=6, 64 candidates). No new kappa,
no domain change, no weakened check.

## What changed

Two minimal edits, same arithmetic and same control flow:

1. `scripts/audit_fused_block.py` — `rational_rank` skips the redundant
   `Q(x)` construction when an entry is already a `Fraction`
   (`x if isinstance(x, Q) else Q(x)`). `Q(Q)` returns the same value
   after needless normalization (26M `math.gcd` calls in the profiled
   run), so the elimination steps and returned ranks are unchanged.

2. `scripts/audit_stage_pair.py` — `modular_rank` converts each
   denominator with a cached `_mod_inv(d, prime)` helper
   (`@lru_cache`, same `pow(d, -1, prime)` call) instead of one fresh
   `pow()` per matrix entry (~480k calls over the audit). Cache hits
   return the identical inverse; `lru_cache` does not cache exceptions,
   so a non-invertible denominator raises the same `ValueError` as before.

## Equivalence argument

- `Q(x) == x` for `x` a `Fraction`; the guard only skips rebuilding an
  equal object. Integer entries still go through `Q(x)` exactly as before.
- `_mod_inv(d, prime)` calls the same `pow(d, -1, prime)` with the same
  arguments and returns its result unmodified. Misses compute; hits replay.
- No matrix, pivot order, stopping rule, candidate list, incident map, or
  rejection predicate was touched. The outer `rank` cache, the mod-101
  lower-bound-then-exact structure of `candidate_score`, and all
  `require()` failure points are unchanged.

## Coverage preserved

- Full `certificate()` output is identical to the committed
  `certificates/stage-pair-audit.json` in every field except the single
  expected `source_sha256` entry for `scripts/audit_stage_pair.py`
  (the file we edited). Rank sum 8684, 64 candidates, 6 local
  improvements, directions, overlaps, and scaling rows all match.
- `audit_fused_block` and `audit_joint_frames` certificates regenerate
  byte-identical (their source pins do not cover the edited lines, and
  every rational rank agrees).
- `tests/test_stage_pair_performance.py` checks the optimized helpers
  against verbatim base-commit references on edge cases (empty, zero,
  identity, singular, non-square, ints vs Fractions, 30-digit numerators,
  both primes 101/103), including the `ValueError` path for a denominator
  multiple of the prime, and the existing lower-bound property
  (`modular_rank == 1`, `rank == 2` on `((101,0),(0,1/2))`).
- Existing suites pass: `test_stage_pair` (8 tests), `test_fused_block`
  (7 tests), `test_joint_frames` (8 tests), `test_quadratic_affine`
  (4 tests) — all rank consumers of the edited helper.

## Benchmark

Fresh-process timings of `certificate()` (compute only, no file write),
same machine and interpreter, OS caches not flushed, host not isolated.
Timing is descriptive, not a pass threshold.

| run | original (s) | optimized (s) |
|-----|---:|---:|
| 1 | 16.63 | 14.31 |
| 2 | 15.79 | 13.96 |
| 3 | 15.57 | 13.64 |
| median | 15.79 | 13.96 |

Median 15.79 s to 13.96 s: 1.13x faster, 11.6% less wall time.
Microbenchmarks on the same inputs: `rational_rank` 3.05x on 50 sampled
frames; modular denominator conversion 1.42x on 20 sampled matrices.

Reproduce (stdlib only, Python 3.11+):

```sh
python3 -B research/stage-pair-performance/benchmark.py --rounds 3
```

Expected: `PASS_IDENTICAL_STAGE_PAIR_RECEIPTS`.

```sh
python3 -B -m unittest tests.test_stage_pair_performance -v
```

Expected: 6 tests `OK`.

## Scope and limits

- This covers the fixed historical check only (h=6, prime 101, 4082
  baseline edges, 64 candidates, 36x36 matrices). No frontier replay,
  supplier, or multiplication runtime is measured or claimed.
- The 86 s `audit_quadratic_affine` replay was not rerun end to end;
  its 4 unit tests pass and its rank calls go through the same
  provably-identical helper, verified by the equivalence suite.
- Full `make verify` and the selected-supplier cold replay were not rerun
  for this isolated historical-checker change, matching prior tooling PRs.

## Attribution

Contributor: Aaron Wang (navinor). Prepared with substantial AI assistance
(Muse Spark via OpenCode). Predecessor authorship and notices intact.
`upstream/` untouched. Selected frontier and records unchanged.
