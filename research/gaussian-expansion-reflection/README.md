# Exact reflection reuse in periodic Gaussian setup

The complete PR2313 Gaussian recovery replay eliminates **11,470 interval
exponential evaluations** by constructing one row of each reflected pair.
Every stored interval endpoint and the complete scientific output remain
identical. The replacement runs all 289 retained integer-product fixtures;
it changes the coefficient setup and preserves the original numerical path.

Claim type: scoped implementation-preservation proof, exact operation
reduction and finite conformance evidence. The measured complete-command
runtime is **inconclusive**, as recorded in [BENCHMARK.json](BENCHMARK.json). This is a
verification-engineering side result. No new kappa, supplier admission or
selected-frontier change is claimed.

This contribution was produced by Nick Petalas. Apache-2.0.

## What changes

For source length `s`, target length `t` and the original finite radius,
the actual expansion matrix satisfies the exact interval identity

```
E[t-k,a] = E[k,(-a) mod s],   1 <= k < t.
```

The new builder evaluates rows `0,...,floor(t/2)` and fills the remaining
rows by cyclic reflection. It retains the original radius, finite summands,
per-term outward division and one-unit upper tail enlargement. The proof
in [PROOF.md](PROOF.md) uses an exact bijection of the truncated summands;
it establishes equality of the computed dyadic intervals, rather than
agreement only of the underlying real Gaussian.

For coprime `s,t` and radius `r`, the exact saved exponential count is
`(ceil(t/2)-1)*(2r+2)`. The first source fixture `(5,8,5,448)` saves 696.
The complete command directly computes 76 rows and reflects 60, retaining
all 136 rows needed by its eight completed setup paths. Gaussian-module
exponential calls fall from 26,464 to 14,994. Matrix storage remains `s*t`
entries, and no cross-invocation cache exists.
The baseline row/constructor adapter counters are zero because it executes
the original loop; the common exponential counter measures both modes.

[adapter.py](adapter.py) authenticates twelve inputs, loads their captured
source bytes and substitutes only the expansion allocation/row loop in
the pinned constructor. It leaves the remaining constructor and complete
verifier in place. The baseline mode loads the original constructor.
Every original conformance check and scientific receipt comparison executes
in both modes. Frozen predecessor files and their credit are unchanged.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-expansion-reflection/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/gaussian-expansion-reflection/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-expansion-reflection
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-expansion-reflection --check-source-history
```

Other machines may substitute their CPython 3.12 executable. The direct
verifier prints `PASS_GAUSSIAN_EXPANSION_REFLECTION` in a generated JSON
report bound to the executable sources and manifest. Default replay writes
nothing. The registered normal and optimized checks execute the same
explicit predicates and compare the same retained scientific output.

New conformance checks cover 5,016 reflected row pairs and 43,223 exact
term bijections; literal interval comparison covers 269 entries in five
fixtures, including an odd target and noncoprime geometry. Four semantic
controls detect wrong cyclic reversal, wrong row, missing outward tail
unit and mutable interval objects. Four additional controls reject changed
source layouts and an unknown execution mode. These checks concern the
new substitution. They are not an independent audit of PR2313's numerical
or uniform-recovery proof.

Run either complete caller or repeat the measurement outside the checkout:

```sh
python3.12 -I -W error -B research/gaussian-expansion-reflection/run.py --mode baseline
python3.12 -I -W error -B research/gaussian-expansion-reflection/run.py --mode reflected
python3.12 -I -W error -B research/gaussian-expansion-reflection/benchmark.py --output /absolute/scratch/new-benchmark.json
```

The harness refuses an existing output or a destination inside the checkout.
It times five alternating fresh subprocesses per side, including startup,
source authentication, all setup and the complete retained replay. All
ten exit codes and scientific stdout hashes must agree. Timings are
observations, not CI pass conditions. The verifier authenticates their
source bindings and recomputes their medians and ranges.

The measured complete-replay medians are 26.234504 s for the baseline and
26.032467 s for the replacement. Baseline range is 25.890081–27.549148 s;
replacement range is 24.810192–26.079677 s. The 0.202037 s median difference
is smaller than the observed run variation: **no runtime improvement is
established**. All ten complete executions succeed with identical scientific
stdout. The exact operation reduction is the delivered improvement; the
initial runtime prediction was narrowed in the Discussion finding.

The measurement uses CPython 3.12.15 on macOS arm64 with 18 logical CPUs.
Initial load averages are 5.16, 7.35 and 5.09. Other work could run
concurrently; alternating subprocesses expose both sides to that load.

A separate baseline profile identifies the limiter: the rounded matrix and
FFT executions dominate; the ten constructor calls take about 9.1% of the
profiled complete runtime. The coefficient replacement can improve only
part of this setup. The profile is excluded from timing samples. Reproduce
it with `python3.12 -I -B -m cProfile -o /absolute/scratch/baseline.pstats
research/certified-gaussian-recovery/verify.py`.

## Scope and code discipline

The proof covers the stated exact expansion formula and its finite
truncation for all positive integer geometries. The executable adapter is
source-bound to PR2313 and its existing caller. A future source edit must
update the pins and be assessed again. No fast sequential Gaussian backend,
physical movement/cleanup tariff, new precision policy, selected cold replay,
native operator proof, compiler closure, stock or outer theorem is supplied.
The five inherited framework assumptions retain their status. Independent
human and formal proof-kernel review are unclaimed.

New loops have bounds from `s,t,r` or fixed verifier families. Every new
function is below 60 lines. The new builder has no recursion. The frozen
predecessor's recursive FFT and finite numerical iteration remain unchanged.
Python allocation and its immutable integer/interval objects are a managed
runtime deviation from fixed allocation: the matrix has exactly `s*t`
entries and the builder retains no query history. Captured-source compilation
and a partial function are bounded dynamic-loading deviations restricted to
three authenticated modules and the one declared constructor substitution.
All loaded modules, arguments and import paths are restored on every exit.
Measurement children have a 290-second bound. Warning-strict normal and
optimized replay provide the interpreted diagnostics.

## Open next questions

Can an actual fixed-tape Gaussian coefficient producer exploit this
reflection with a favorable complete movement and cleanup bill? Start by
binding one emitted table and its sequential order, then price reflected
reads, writes, head returns and cleanup. The physical producer, ordering
and tariff are missing here. No further optimization is reserved.

## Credit and overlap

Mason Hale / mason-hale's [PR2313](https://github.com/CrocSwap/integer-mult-bounds/pull/2313)
supplies the completed Gaussian backend, interval arithmetic, operator and
uniform integer-recovery certificates, fixtures and controls. Cinna Davis's
PR2298 supplies its caller question. The retained Harvey–van der Hoeven,
Gaussian, CRT, Neumann-rounding and numerical lineage remains credited in
the unchanged predecessor [NOTICE](../certified-gaussian-recovery/NOTICE.md).
Reflection symmetry is classical; priority for that identity is unclaimed.
The new implementation, exact preservation argument and operation reduction
are the contribution here.

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. The drawn `uniform-transfer-audit` card is explicitly changed
to this original verification-engineering question in [TASK.json](TASK.json).
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360807)
preceded implementation. Entry searches checked live claims and local
reservations, open PRs, recent account work, merged titles/bodies and main
README terms. The cached overlap search has incomplete sparse local coverage;
unpublished work and arbitrary historical diffs remain limits. Predecessor
science and selected-frontier files are untouched.
