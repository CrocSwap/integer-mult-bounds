# Annex validation

Both fresh relocated runs passed on 22 October 2026. The normal run took
0.362 seconds. The optimized run took 0.350 seconds. Each used one process
at a time, Python 3.14.7, and macOS 26.6.1 ARM64. Other systems and Python
versions were not tested in this validation.

The commands ran from `/private/tmp`:

```sh
python3 -I -B /private/tmp/fixed-baseline-spectral-cold-20261022/replay.py --out /private/tmp/fixed-baseline-spectral-normal-20261022
python3 -I -O -B /private/tmp/fixed-baseline-spectral-cold-20261022/replay.py --optimized --out /private/tmp/fixed-baseline-spectral-optimized-20261022
```

Both commands printed:

```text
PASS_UNPAIRED_SPECTRAL_EXCLUSIONS
PASS_INDEPENDENT_UNPAIRED_SPECTRAL_BOUND
PASS_FIXED_BASELINE_SPECTRAL_GAP
```

The [normal report](validation/normal/REPLAY.json) and
[optimized report](validation/optimized/REPLAY.json) retain the exact
commands, source hashes, stage statuses, and times. The producer ran
with assertions enabled in both runs. The independent checker used
explicit failures, including in the optimized run.

Both producer receipts and both independent receipts match the
historical receipt bytes exactly. The
[mode comparison](validation/MODE-COMPARISON.json) records their hashes.
No fields were removed for this comparison. The replay verified all
21 source files before and after execution. It checked both compressed
member hashes and both decoded payload hashes.

The source manifest SHA256 is:

```text
9a891d1ea4656b9dc60321646af4e6ef3cdb4213fffef55ebeb63624545a1904
```

The replay entrypoint SHA256 is:

```text
4d6c64b3bdd95d9d7369eb63bfd6cdce0b94edec19954f3dfc878eadede66fdc
```

The [preservation check](validation/MAIN-PRESERVATION.json) verified
all 256 accepted main files and the unchanged main package manifest.
Only this annex was added. The earlier main replay was not repeated.
The independent publication review of this annex is stored separately
by the coordinating agent.

This validation repeats the bounded source reconstruction, root cases,
and rational spectral inequalities. The selected-baseline necessity
and factor-11 arguments are retained proof steps. No selected-set
enumeration, new search, native word, ownership schedule, routed caller,
recursive pricing, current supplier, or complete kappa calculation ran.
