# Faster complete E8 root-swap replay

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

The new exact eight-coordinate dot product reduces the complete retained
[PR3166](https://github.com/CrocSwap/integer-mult-bounds/pull/3166) replay's
local median wall time by **13.95%**, from **6.131 s to 5.275 s**. Five
alternating fresh-process pairs execute the full scientific command on both
sides. All ten runs succeed with identical stdout and no stderr. Every
candidate run is faster than every baseline run in this sample.

Claim type: scoped implementation-equivalence proof, exact finite conformance,
and local performance evidence. The decoder mathematics and its certificates
remain conorholds's contribution. No new kappa or scientific audit is claimed.

`replay.py` authenticates ten scientific files, compiles the four original
modules from their authenticated bytes, replaces only the primary and
extension dot products, and calls the original main. The separate Cartan
implementation, Gaussian algebra, geometry, rejection controls, source hashes
and complete RESULT.json comparison remain active. Frozen files are unchanged.
[PROOF.md](PROOF.md) gives the substitution argument and scope.

## Measured complete consumer

CPython 3.12.15, macOS 27.0.1 arm64, 18 logical CPUs. Initial shared-host load
averages were 2.27, 2.58, 1.99. No other replay from this contribution ran during
timing; other contributors could use the machine. Both commands use
`-I -W error -B`, including startup, imports, every check and output capture.

| Pair | Original, seconds | Specialized, seconds |
|---|---:|---:|
| 1 | 6.333281 | 5.110564 |
| 2 | 6.083976 | 5.607583 |
| 3 | 6.376638 | 5.199241 |
| 4 | 6.130820 | 5.275435 |
| 5 | 6.124533 | 5.409365 |
| Median | 6.130820 | 5.275435 |
| Range | 6.083976 to 6.376638 | 5.110564 to 5.607583 |

The percentage uses nanosecond medians 6,130,819,750 and 5,275,434,583.
A separate baseline profile attributes 3.718 s of its 17.878 s instrumented
run to the two replaced dot functions. The measured saving is below that
20.8% share. Generator/sum overhead is the changed cost; the other checks
limit the saving. Profile seconds are not estimates of uninstrumented time.
This local result implies no runtime bound on another host or input.

`benchmark.py` generates stdout evidence containing every command, elapsed
nanosecond count, return code, stdout digest and failure count. The table
transcribes that report. No timing receipt is hand-written. CI runs
conformance, not a performance threshold.

## Reproduce

From the repository root with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/e8-root-swap-fast-inner/replay.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/e8-root-swap-fast-inner/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/e8-root-swap-fast-inner/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/e8-root-swap-fast-inner/benchmark.py --pairs 5
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/e8-root-swap-fast-inner
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/e8-root-swap-fast-inner --check-source-history
```

Another CPython 3.12 executable may replace the absolute path. Set `TMPDIR`
to a private external directory for temporary custody controls. The fast
command prints the unchanged source success line. The new verifier emits a
generated JSON receipt with `PASS_E8_ROOT_SWAP_FAST_INNER`, 5,096,623 exact
old/new dot comparisons, 576 scalar fixtures, nineteen controls and hashes of
all eight package files. Source mathematical check counts are inherited
coverage. Each registered normal/optimized command has a 120-second limit.
Benchmarking is optional and excluded from CI.

## Sources and limits

Canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priorities revision 8.
The selected record resolves to PR6030, kappa .003125804. The card's first
binding control passed with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; this is
orientation only. TASK.json refines replay-runtime to this complete command.
SOURCES.json pins ten live scientific inputs and historical provenance.

Credit conorholds / PR3166 for the original replay, proofs, checks and
certificates, and DreamingOfClouds / PR2816, PR2826, PR2862 and PR3154 with
their retained E8 lineage. Their files and notices are unchanged. Fixed-product
unrolling is standard. This contribution supplies its source-bound adaptation,
preservation argument and measured complete consumer. Nick Petalas / PR6164
optimized publication-byte preflight using this package as a fixture; it did
not accelerate this scientific command.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370259)
states this scope. Main, merged and live PRs, recent account work, handoffs and
local reservations were checked. The overlap cache covered 506 open PRs and
6,501 Discussion records; sparse local-note coverage was incomplete. Arbitrary
historical diffs, unpublished work and literature priority remain outside coverage.

Equivalence covers the pinned default command and exact integer/rational
eight-coordinate arguments. Arbitrary overloaded scalar types, receipt-emission
CLI options, arbitrary module-cache states and future source changes are
excluded. Lean source bytes are authenticated; Lean is not run. No native or
physical caller, precision, tape, stock, compiler, outer or selected cold replay,
new supplier or complete multiplication theorem is supplied. All five selected
framework assumptions and the selected frontier remain unchanged.

New functions stay below sixty lines and have bounded fixture/module/input
loops and no recursion. Managed allocation is a Power of Ten rule 3 deviation
for this fixed workload and ten inputs capped at 1 MiB each. Authenticated
compilation of four unchanged modules is a rule 8 deviation; it generates no
new source. The two substitutions, comparison closure and source main are
fixed rule 9 dispatch targets. Frozen predecessor loop/function constraints
are retained. Warning-strict normal/optimized replay supplies the available
diagnostics; no separate static analyzer or real-time guarantee is claimed.

## Open next questions

1. Integrate into one maintained replay entry while retaining the checkers'
   intended arithmetic independence. First identify the active consumer and
   measure its full command. This adapter targets a historical fixture.
2. Profile that consumer's remaining bottleneck before another optimization.
   The first verified improvement ends this contribution; no follow-up is reserved.
