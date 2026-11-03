# Cached contractions in the complete A2+E6 primary replay

The opt-in PR2061 adapter removes 154,233 repeated exact contractions and
1,233,864 rational multiplications. The complete primary CLI's local median
time falls by 27.86%, preserving its complete result and all original checks.
This is a scoped implementation-equivalence proof, exact operation-count
certificate and local performance result. It is not a new decoder theorem,
supplier admission or kappa. The contribution was produced by Nick Petalas.

`replay.py` authenticates nine live source files, imports the unchanged primary
verifier and replaces only `exact_identity`. The new implementation computes
the fixed 112-by-9 root-normal contraction table once per call. It retains
every ordered entry comparison, the original early rejection and the complete
`RESULT.json` comparison. The cache never survives an invocation.
[PROOF.md](PROOF.md) proves exact equality and gives the counting argument.
No frozen predecessor file or selected record changes.

## Measurements

CPython 3.12.15, macOS 27.0.1 arm64, 18 logical CPUs, standard library only.
Five alternating original/cached fresh-process pairs passed with no errors,
identical stdout and empty stderr. The timer encloses the entire CLI, including
imports, source authentication and both rational budget screens.

| Mode | Median seconds | Minimum | Maximum |
| --- | ---: | ---: | ---: |
| Original | 2.354848833 | 2.331363334 | 2.602431125 |
| Cached | 1.698670834 | 1.675971083 | 1.886004875 |

The integer nanosecond samples, in alternating pair order, are:

```text
original   cached
2332376792 1886004875
2602431125 1675971083
2354848833 1841411000
2331363334 1698670834
2503531083 1684102000
```

The one-minute load average rose from 3.00 to 4.41 during the run. Other work
could not be controlled; the sides were interleaved on the same machine.
A separate profile places about 58% of the original `run()` time in the two
identity invocations. The unchanged interval budget calculation is a remaining
limiter. Profiler runs are excluded from the timing sample. The measured gain
is below the original identity share; no isolated helper timing is substituted
for the complete CLI. This is not a whole four-command workflow speedup or a
guarantee on another machine.

## Reproduce

From the repository root with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/a2-e6-cached-contractions/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/a2-e6-cached-contractions/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/a2-e6-cached-contractions
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/a2-e6-cached-contractions --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/a2-e6-cached-contractions/benchmark.py
```

Any CPython 3.12 path may replace the local absolute path. Put `TMPDIR` and
redirected receipts in an external scratch directory if retaining outputs.
The benchmark defaults to five alternating pairs and accepts at most nine.
It checks every exit status and exact stdout; a failed run aborts the report.
Registered verification runs normal and optimized Python and writes a generated
stdout receipt bound to every package-file hash. No receipt is handwritten.
Expected markers are `PASS_A2_E6_CACHED_CONTRACTIONS`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.

The verifier retains the complete primary science, including 12,544 positive
identity comparisons and the coefficient mutation's rejection at comparison
4,817. It adds 37 rational control cases and ten real source-admission controls.
Each of the nine live dependencies is independently corrupted and rejected;
one missing input is rejected. The package exports with all declared inputs
and can replay without Git or network access. No source receipt is rewritten.

## Scope and implementation constraints

The first successful contraction change ended optimization. `independent.py`
and `test_verify.py` from PR2061 are unchanged, unoptimized and outside the timed
primary CLI. Their mathematical results are not this contribution. No selected
cold replay, Lean, Docker, native supplier or complete multiplication theorem
was run or proved. The selected conditional kappa 0.003125804 and its five
framework assumptions remain unchanged. Independent human and formal
proof-kernel review are unclaimed.

The adapter has at most 120 indices, nine normals and eight coordinates from
the authenticated source. Its cache has at most 1,080 rational entries, 1,008
on the actual fixture. New functions fit within 60 lines, use no recursion and
enforce bounded domains. Source-control copies are temporary and removed on
every exit. Each subprocess has a 60-second timeout; the benchmark has at most
18 subprocesses. CPython allocation and fixed-target dynamic module imports are
documented Power of Ten deviations. The legacy imported `run()` exceeds the
function-size target; it remains frozen to preserve the exact workload.
Warning-strict normal and optimized runs provide recurring diagnostics.

## Open next questions

Should this adapter be adopted by PR2061's registered workflow? Start with an
explicit successor source binding and the complete four-command Linux replay.
Default adoption and a whole-workflow measurement are still missing. They
cannot be inferred from the primary CLI measurement. [TASK.json](TASK.json)
records the same first step and blocker. No further optimization is reserved.

## Credit and overlap

Adam Gall's [PR2061](https://github.com/CrocSwap/integer-mult-bounds/pull/2061),
head `eed23989eddf7ec0b2c24d9e3794d0fca53f11ab`, supplies the complete scientific
workload, COPY69 result and rejection controls. Credit joaqcoo / PR1224 for the
normal family and geometry implementation; Philipp / mightyOil / PR1248,
commdata2338 / PR1304 and Hanson Sun / bbMisk / PR1612 for the deficiency method;
DreamingOfClouds, GamingPuzzled, themilkman216, woklerx, Sagar Thakrar and Douglas
Colkitt for the decoder, coverage and ceiling lineage retained in PR2061.
Their files and notices are unchanged. The new contribution is the contraction
adapter, equality proof, operation reduction and complete-CLI measurements.
Exact source pins are in [SOURCES.json](SOURCES.json). New work is Apache-2.0.

Base canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371337).
Live open PRs, recent account PRs, handoffs and all-main README searches were
checked for this particular replay. The overlap helper had complete remote
pagination and incomplete sparse local-note coverage, supplemented by Git main
searches. These searches are bounded evidence, not proof of global novelty.
No related open PR studying this exact A2+E6 primary replay was found.
