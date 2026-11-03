# Faster complete chirp-residue replay

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: a bounded implementation improvement with a scoped equivalence
proof and measured complete-command evidence. No new kappa is claimed.

Inlining the one-axis predicate calls reduces the complete PR3806 primary
replay's median wall time by **19.30%**, from 2.4564 s to 1.9822 s, in five
alternating fresh-process pairs. All ten outputs match and there are zero
errors. Baseline times range from 2.4403 to 2.4750 s; fast times range from
1.9595 to 2.0033 s. [BENCHMARK.json](BENCHMARK.json) retains the generated
samples, source hashes, interpreter and host information. The shared macOS
host had 18 logical cores. These are local timings; a physical-consumer
speedup and cross-platform performance are unclaimed.

The source profile spends 5.093 of 5.151 profiled primary-command seconds in
the one-axis loop. Profiling is separate from the reported timings. The new
loop eliminates exactly 41,955,312 successful condition-call boundaries while
still evaluating their predicates. It retains every 13,981,010 one-axis state,
6,141 rollout, 21,840 two-axis state, 4,096 square check and 3,905 visit tuple.
The whole source driver and its receipt checks run with only the one-axis
function substituted. Frozen sources are unchanged.

[PROOF.md](PROOF.md) gives the state induction, loop bound, first-failure
equivalence and counted work. The mathematical chirp result is James Reed's
credited prior work. This package contributes the faster implementation.

## Reproduction

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/chirp-residue-loop/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/chirp-residue-loop/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/chirp-residue-loop
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/chirp-residue-loop --check-source-history
```

Any CPython 3.12 path may replace the local interpreter. The direct verifier
prints `PASS_CHIRP_RESIDUE_LOOP` in a generated receipt bound to every package
file's SHA256. It compares complete stdout and every ordered rollout tuple,
checks all 1,533 corrupted initial states, rejects fifteen malformed domain
or control states and a changed source program, and runs the unchanged
independent source test. All checks remain active under optimization.
Both registered commands have 120-second limits. Timing is not a CI gate.

The fast primary command alone is:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/chirp-residue-loop/replay.py
```

To repeat the ten timings, choose a fresh output path outside the checkout:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/chirp-residue-loop/benchmark.py --output /absolute/scratch/benchmark.json
```

Both modes use the same wrapper, authentication, interpreter flags and fixture;
baseline runs the unchanged original main. Measurement includes startup and the
complete primary command. It excludes the separate independent test script and
conformance harness. The host was shared; the sample ranges remain separated.

## Sources and scope

James Reed / jwr404's [PR3806](https://github.com/CrocSwap/integer-mult-bounds/pull/3806)
supplies the residue replay and its mathematical claims. Credit Jose Manuel's
PR3763 for the producer, Chafik Boukhalfa for the residue schedule and Ross
Richardson for the symbolic-transition lineage. Their files and credit are
unchanged. No predecessor theorem or count is claimed as a new result.

[SOURCES.json](SOURCES.json) authenticates four live files at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The replay-runtime card is refined
to this full command. [TASK.json](TASK.json) records scope and coordination. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372291)
precedes implementation. Cached overlap covered 541 open PRs and 6,563
Discussion records; main and merged searches also checked distinctive
object/count terms. Sparse notes, arbitrary diffs and unpublished work remain
coverage limits. The selected metadata orientation passed.

The loop accepts only the predecessor driver's admitted domain and explicitly
rejects other arguments. An unrestricted API replacement is unclaimed. Native
realization, physical time, precision, storage, ownership, compiler and outer
recovery obligations remain separate. All five selected framework assumptions
remain. No selected cold replay, Lean, Docker, independent human or proof-kernel
acceptance is claimed. The selected frontier is unchanged.

## Implementation constraints

The new loop has at most 4,096 iterations. The complete driver calls it 6,141
times. The conformance census stores 6,141 four-integer rows per side; the
fault census has three groups of 512 states. Ordinary arithmetic operands
have fewer than forty bits. Test-only initial components are capped at 64 bits.
New functions are below sixty physical lines.

Power of Ten deviations are confined to this offline checker. Rule 1:
the immutable source's visit enumeration recurses to depth five and is retained
to preserve coverage. Rule 3: CPython allocates integers and bounded collections
dynamically; a static allocation guarantee is unclaimed. Rules 8 and 9:
the adapter loads one authenticated module and replaces one fixed function
binding; the optional census uses one bounded callback. The controlled import
path names only the package directory. The independent source test is one
child with a ten-second timeout; benchmark children have 120-second timeouts
and there are exactly ten. Temporary source-drift copies are removed by their
context manager. Warning-strict normal and optimized replay provide available
diagnostics. No separate type checker or linter is installed. A broader runtime
or input domain would require revisiting these bounds and allocation/import
deviations.

## Open next questions

1. Can remaining closed-form arithmetic be reduced while retaining a separate
   predicate at every state? Start with the final fast profile and one exact
   change, then prove preserved coverage and measure the whole command. No
   further optimization is supplied here.
2. Does an actual physical chirp-consumer replay use this loop and benefit?
   First identify a caller and measure its complete execution. This residue
   checker does not price a multiplication consumer.
