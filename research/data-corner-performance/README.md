# Exact data-corner replay with cached update columns

**Tooling improvement; no new κ or construction claim.** This optional runner
proved a per-pivot cached update-column loop for the historical
`research/copied-fixed/data_corners.cpp` checker. After
`research/data-corner-production/`, that loop is the **production** default;
this package vendors the pairwise-era source as `baseline.cpp` and differential
replays baseline versus production. It preserves the complete domain of
4,073,300 pairs of triples, every existing assertion, and the complete output
receipt, including all ten modular failures. At the recorded base, the selected
#626/#543 conditional result was
κ = 51110230636731/31250000000000000 = 0.001635527380375392.

## Reproduce

Use Python 3.9+ on macOS or Linux and a C++17 compiler, from the repository root:

```sh
python3 -B research/data-corner-performance/replay.py --benchmark 3 --output /tmp/data-corner-result.json
```

Use an output path that does not exist. Expected final line:

```text
PASS_DATA_CORNER_REPLAY pairs=4073300 complete_receipts_equal=true
```

This compiles the pinned original and the optimized source, then runs three
sequential pairs in alternating order. Each process replays the entire domain;
every receipt field must equal the frozen predecessor receipt, and every run's
stdout must be byte-identical. Timings are descriptive, with no pass threshold.
Compilation and receipt comparison are outside the measured process interval.
The interval includes process startup, computation, and captured output.
OS caches are not flushed and other system activity is uncontrolled.

For the faster complete replay alone, omit `--benchmark`. `CXX` selects the
compiler; both variants use the same `-O3 -std=c++17` flags. The runner refuses
changed source or receipt bytes and refuses a build with `NDEBUG` defined.
No Python or C++ package dependencies are required.

Focused controls:

```sh
python3 -B research/data-corner-performance/test_replay.py -v
python3 -O -B research/data-corner-performance/test_replay.py -v
```

## Why the change is exact

After accepting pivot `(i,c)`, the original loop removes `c` from `available`.
For every lower row `r` with `M[r][c] != 0`, it scans all 47 columns, updating
precisely those satisfying `available[j] && M[i][j] != 0`.

Neither `available` nor pivot row `M[i]` changes during that lower-row loop:
all writes have row index `r > i`. The new code collects this exact ordered
column list once per pivot. Each lower row then performs the identical modular
updates in the identical order, with the identical ratio, and clears the same
pivot entry. By induction over rows and pivots, the matrices, pivot products,
zero checks and first-failure positions agree. List construction occurs after
the existing ordered-zero assertions and does not replace any of them.

The pivot order is not natural column order. Eligible columns **left of the
pivot must be included**. The separate `j > c` condition belongs only to the
ordered-zero assertions. A regression embeds
`[[2,1],[1,1]]` with pivot order `[1,0]`: the correct pivot product is −1 modulo
1000003; deliberately omitting left-of-pivot updates gives +1 and is detected.
Reversing the cached list is a positive control: distinct column updates
commute, and both the receipt and complete final matrix remain equal.

The additional stack array holds only 47 integers. The optimization removes
repeated eligibility scans; it does not reuse a result across matrices, omit
pairs, change the prime, or replace exact arithmetic with numerical arithmetic.

## Evidence and coverage

`RESULT.json` contains the measured compiler/platform, raw alternating samples,
implementation/generated-source hashes, input pins, and coverage counters.
`PRELIMINARY.json` retains the first same-input measurement separately.
Three alternating process pairs on Apple clang 21.0.0 / macOS arm64 gave
median wall times **169.198 s → 98.954 s (1.710× faster; 41.5% less time)**.
Every stdout and stderr hash agreed. These measurements finished before the
session pause; `VALIDATION.json` records the final checks after resuming.

The full predecessor receipt covers:

| Obligation | Count |
|---|---:|
| Triple pairs | 4,073,300 |
| Primary-prime successes | 4,073,290 |
| Primary-prime fallback records | 10 |
| Nonzero pivot checks | 191,444,880 |
| Ordered-zero checks | 1,409,360,440 |
| Per-first-triple product records | 1,771 |

Seven focused test groups compile the actual original and transformed C++
elimination bodies in an eight-column harness. They compare complete final
matrices and partial receipts on 48 seed-86 dense/sparse cases and each of eight
failure positions. An independent Python determinant implementation uses
natural-column elimination with row swaps and verifies successful products,
including the sign of non-natural column permutations. These tests also cover
the left-of-pivot mutation, valid reversed updates, invalid ordered zeros,
repeated pivots, source and fixture drift, ambiguous transformation sites,
disabled C++ assertions, and eight corruptions of proof-relevant receipt fields.
This is finite differential validation plus a loop-equivalence argument, not a
formal proof of the multiplication theorem.

The ten primary-prime failures remain failures in this runner's output. The
historical producer subsequently calls `data_recovery.py`, which verifies their
47 ordered pivots over the rationals. That separate recovery is unchanged and
is outside this optimization and its timing claims. No modular zero is called
a rational counterexample.

## Scope, provenance and handoff

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
`SOURCE.json` pins the two execution inputs by SHA-256 and Git blob identity.
The runner requires only this package and those two repository-relative files;
it does not access the network or depend on Git during execution.

`CLAIM.json` records OS-random seed 86, the three candidates, scope and overlap
checks. There was no pinned coordination issue, so the claim is local. The user later
authenticated GitHub and confirmed submission of one focused PR.
A final overlap sweep covered 693 open PRs through #902; no matching optimization
was found. After a user-requested pause, upstream was refreshed to
`f567884aeb8851b6e794af1184119a3bfbe1e631`; both execution input blobs are unchanged there. Existing source
packages, manifests, certificates, default targets and `upstream/` are unchanged.
Only files in this directory are added.

The selected supplier cold replay, whole-repository `make verify`, Lean, and
remote CI were not rerun for this isolated opt-in historical checker. The
all-size/compiler/common-label/hosting/residual/precision/tape/analytic
assumptions remain. Measurements concern this finite checker, not the selected
frontier or practical integer multiplication.

See `NOTICE.md` for predecessor credit and AI disclosure.
