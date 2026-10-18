# Validation receipt

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
Recorded 2026-10-13 on macOS 26.5.2 arm64, CPython **3.12.14**.
The bundled interpreter was used because the system Python is 3.9.6 and
lacks `int.bit_count`, which the original checker already requires.

## Completed checks

- `python3 -I -B research/sparse-fusion-orbits/verify.py`: all 12 tests pass;
  complete source-bound certificate and h=22,25,28 screen receipts match.
- `python3 -I -O -B research/sparse-fusion-orbits/verify.py`: all 12 tests pass
  with the same final marker. The two initial finalized runs executed
  concurrently, taking 24.509 and 24.668 seconds; these are not benchmark data.
- Six unchanged `tests/test_sparse_fusion.py` tests pass with the original
  screen. The same six tests pass with the accelerated screen under `-O`.
- All **29** manifested SHA-256 and Git blob identities match the exact base
  Git objects. The original upstream check remains active in full replays.
- Independent row elimination covers **455,424** frame/triple cases. Direct
  conjugation covers every triple in the three retained h cases. Each screen
  retains all **8,256** predicate/message checks.
- Controls detect wrong multiplicity, missing orbit, wrong representative,
  source/certificate corruption, zero/deficient rank kernels, and invalid h.
  A separate hidden-minimum control establishes that an incorrect
  representative can leave the final minima unchanged while the independently
  computed per-block sums detect it.
- A fresh minimal closure containing only this package and the 29 manifested
  inputs passes all 12 tests under `-I -O -B`, from `/`, in a temporary path
  containing spaces, without Git or unmanifested repository files.
- Changing an expected Boolean to integer 1 in that relocated package is
  rejected. An h=22 integer-to-float output substitution is rejected. Direct
  controls confirm `True`, `1` and `1.0` are not interchangeable JSON receipts.
- The benchmark refuses an existing output path before running and preserves
  that file's contents.
- `python3 -I -B scripts/verify_selected_result.py` passes with the original
  selected `1661634653669567/10^18` record and source/proof hashes.

The first pilot control compared only the final receipt and failed to detect
the hidden-minimum mutation. The independent per-block test was added before
the finalized successful runs. Review also corrected proof wording from
"full rank" to "exact matrix rank" and applied type-preserving comparison to
the supplementary screen receipts. The argument and actual rank computations
were unchanged by those corrections.

## Final benchmark

`BENCHMARK.json` contains raw samples and every exact timed receipt from five
alternating fresh-process A/B pairs for each of three inputs. All **30** timed
receipts match. It records the final accelerator and benchmark source hashes
and the source-manifest hash. Only documentation and comparison guards outside
the timed code changed afterward.

| Same input | Original median seconds | Accelerated median seconds | Ratio |
|---|---:|---:|---:|
| Complete h=25 certificate | 0.376574 | 0.084435 | 4.460x |
| Central screen h=25 | 0.382510 | 0.060782 | 6.293x |
| Central screen h=28 | 0.517353 | 0.061301 | 8.440x |

The final benchmark ran after the finite-test workers completed. The host
was not isolated and caches were not flushed. Process startup, both source
digest checks, imports, exact checks and JSON serialization are included.
Timing has no pass threshold and is not a claim about integer multiplication.

## Review and limits

A separate Codex worker verified the permutation argument and compared the
adapted function's AST with the original: only representative enumeration,
triple count, weighted unary sum and local aliases differ. Another worker
implemented the independent rank tests. The coordinator inspected the work
and ran the final checks. These are AI reviews, not independent human review.

All original files and `upstream/` remain unchanged; only this opt-in package
is contributed. Full `make verify`, selected cold supplier reconstruction,
Lean and hosted CI were not run or claimed. The default generators and
selected construction are unaffected. The affected historical checks and
source-bound package checks were run; no global artifact regeneration was
needed.

Before publication, main remained at the recorded base. Open tooling PRs,
the sparse-fusion search and spectator-related PR metadata were refreshed;
no duplicate of this exact routine/mechanism was found. PR871 and PR824 are
credited as related, distinct work. No pending dependency was introduced.
