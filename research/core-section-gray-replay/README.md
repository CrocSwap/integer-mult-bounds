# Complete core-section replay with 79.02% less wall time

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped implementation-equivalence proof, exact finite conformance
and local performance evidence. The complete authenticated PR3773 scientific
consumer takes 79.02% less median wall time locally, from 0.654020 s to
0.137189 s across five alternating fresh-process pairs. All ten outputs agree
and every pair improves, with zero failures. Optimization stopped at this first
verified improvement.

The new enumerator packs the coordinate bits into columns, then walks every
nonzero functional by binary reflected Gray code. Each step needs one packed
XOR and one population count. [PROOF.md](PROOF.md) proves the exact mask-table
identity and its whole-consumer substitution. The adapter changes one expression
in private, authenticated source. All original root construction, exact rational
coordinates, binary rank checks, 3,780 core visits, per-core histogram checks,
aggregate and RESULT.json comparison still execute. The predecessor files remain
unchanged. This is an opt-in consumer, with no shared implementation changes.

## Credit and scope

James Reed / jwr404's [PR3773](https://github.com/CrocSwap/integer-mult-bounds/pull/3773),
head `83cb934664879552405c60987ceca100f9656a49`, supplies the complete consumer,
root geometry and section histogram. Credit conorholds for the recorded
section-histogram premise, Nick Petalas for the retained E8 root geometry, and
the P112 lineage retained in those sources. Their mathematical results are
cited inputs, not audited or claimed as new. Gray-code subset enumeration and
packed binary columns are classical. The new result is this exact replacement,
its complete source-bound consumer and measured replay saving.

Canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The replay-runtime card is refined to this consumer without
changing its coverage requirement. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371293)
records the scope. Live open/account PRs, recent handoffs, active Discussions,
local reservations and main/merged object and implementation searches were
checked. Sparse local notes, arbitrary historical diffs and unpublished work
remain limits of the overlap picture.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/core-section-gray-replay
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/core-section-gray-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/core-section-gray-replay/replay.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/core-section-gray-replay/benchmark.py --pairs 5
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/core-section-gray-replay --check-source-history
```

Another CPython 3.12 path may replace the shown interpreter. The verifier prints
`PASS_CORE_SECTION_GRAY_REPLAY` in its generated JSON. The direct scientific
consumer prints `PASS_CORE_SECTION_CAPACITY pairs=3780 sections=127 no_new_kappa`.
Use `replay.py --engine original` for the same authenticated original consumer.
To save a fresh package-hash-bound verification receipt, pass `--receipt` with
an absolute path outside the checkout. Default execution writes no artifacts.

## Exact conformance

The verifier checks all 5,058 coordinate lists of lengths 0..3 in dimensions
0..4, including repetitions, zero coordinates and deficient spans. All 74,958
mask entries agree with independent direct parity evaluation. A separate
256-coordinate, dimension-ten case checks all 1,024 masks at the API limits.

At the complete scientific consumer, every reached mask table agrees before
histogram grouping. This covers 3,780 cores and 480,060 nonzero-mask sections.
The source expression's 11,521,440 parity evaluations become 635,040 column
bit tests and 480,060 packed XOR updates. These are exact loop-work counts,
not equal-cost instruction counts. The source retains its own mathematical
success checks and full output comparison.

Seventeen boundary controls reject malformed domains, an unknown engine,
and modified or missing bytes at each of the three live source inputs.
Six scientific controls reject inclusion of mask zero, a missing mask,
complemented parity, a missing coordinate, a wrong expected histogram and
a wrong core rank. Each control requires its expected failure reason.
Registered replay includes warning-strict normal and optimized conformance,
plus an uninstrumented fast consumer. Timing is an optional local check.

## Local timing evidence

The separate profile attributes 1.788 s of the source consumer's 1.988 s
profiled cumulative time to section construction and Counter accumulation.
Those profiled times are excluded from the wall-time comparison. The candidate
replaces the measured bottleneck and has no persistent cache or tuned option.

The benchmark times interpreter startup, source authentication and the complete
scientific main function. Every subprocess must exit successfully, produce the
exact full scientific stdout and have empty stderr. Metadata validation and
added conformance checks run separately. The original arithmetic-only
`test_verify.py` is outside this measured scientific command; its four identities
are already checked in the complete consumer's count and aggregate comparisons.

| Pair | Original seconds | Gray seconds |
| ---: | ---: | ---: |
| 1 | 0.654254 | 0.139853 |
| 2 | 0.652888 | 0.137321 |
| 3 | 0.654020 | 0.135996 |
| 4 | 0.660023 | 0.137189 |
| 5 | 0.653303 | 0.136774 |
| Median | 0.654020 | 0.137189 |
| Range | 0.652888..0.660023 | 0.135996..0.139853 |

The host is macOS 27.0.1 arm64, CPython 3.12.15, with 18 logical CPUs.
Load averages before the pairs were 1.66, 1.96 and 2.03. Other work shared
the host; alternating runs give both engines comparable exposure. All five
pairs improve, and the two timing ranges do not overlap. This is local evidence,
with no portable runtime guarantee. The measured reduction is below the
profiled bottleneck's share of the complete consumer.

## Limits and engineering inspection

The executable accepts dimension 0..10 and at most 256 coordinates. Its Gray
loop has at most 1,023 iterations, with ten columns of at most 256 bits and
1,024 output counts. Small-list enumeration has 5,058 cases; scientific
conformance has 3,780 calls. The benchmark permits 5..15 pairs and bounds each
child to 60 seconds. All new functions are shorter than 60 physical lines.
There is no recursion or network access in the package.

Python allocation and exact integer objects are managed-runtime deviations
from fixed preallocation. Every new data structure has the preceding finite
capacity. Source loading compiles one hash-authenticated predecessor program;
the sole replacement string is required to occur exactly once. This private
source adapter is a bounded dynamic-code exception. Verification callbacks
have a closed set of six scientific controls and one conformance observer.
They do not change the timed consumer. The inherited exact geometry code
retains its resource behavior and source notice.

No predecessor scientific result is independently audited, and the written
replacement proof is not proof-kernel checked. Linux timing, physical native
execution, source ownership/restoration, precision, stock, tape movement,
complete supplier/outer invoices and the five selected framework assumptions
remain outside this result. No Lean, Docker or selected supplier replay was
run. No new kappa or selected-frontier change is claimed. Independent human
and formal proof-kernel review are unclaimed. Hosted CI status belongs in the
PR body.

## Open next questions

Should a maintained consumer adopt this enumerator? First review the single
expression substitution and reproduce its complete benchmark on one Linux
host. Maintainer adoption and Linux performance evidence remain separate;
this package reserves no continuation or wider geometry census.
