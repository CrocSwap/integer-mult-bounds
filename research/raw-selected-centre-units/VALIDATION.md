# Publication validation

On 22 October 2026, both runs passed all eight stages from a copy outside
the research workspace. The normal run took 175.274 seconds. The
optimized run took 143.069 seconds. Each run used one process at a time.
The machine used Python 3.14.7 on macOS 26.6.1, ARM64. Linux and other
Python versions were not tested in this validation.

The commands ran from `/private/tmp`:

```sh
python3 -I -B /private/tmp/raw-selected-units-cold-package-20261022/reproduce.py --out /private/tmp/raw-selected-units-final-normal-20261022
python3 -I -B /private/tmp/raw-selected-units-cold-package-20261022/reproduce.py --optimized --out /private/tmp/raw-selected-units-final-optimized-20261022
```

Both commands returned:

```text
PASS_RAW_SELECTED_CENTRE_UNITS
```

The retained [normal report](validation/normal/REPLAY.json) and
[optimized report](validation/optimized/REPLAY.json) give the exact
subprocess commands, status values, and times. Their temporary workspace
paths record the executed runs. Those temporary workspaces were removed
after each run. The retained logs and receipts are in the same folders
as the reports.

| Check | Normal | Optimized reviewers |
| --- | --- | --- |
| Independent irregular S38 units | PASS | PASS |
| Fixed dyadic witness | PASS | PASS, assertions enabled |
| All 14 complete-minor cases | PASS | PASS |
| Odd-grid and minor factors | PASS | PASS |
| Native phase records, base and extra providers | PASS | PASS |
| Serial S8 and S40 local words | PASS | PASS |
| S38 native words and response inverse | PASS | PASS |
| Structured short normalization | PASS | PASS |

Each run verified all 187 source files before and after execution. The
old and transferred centre rows agreed exactly. Every mathematical
receipt field agreed with the retained historical result. The
regenerated complete-minor program agreed by decompressed payload.

The [mode comparison](validation/COMPARISON.json) also checks the eight
mathematical receipts against each other. It removes only the keys
`seconds`, `max_rss_bytes`, and `checker_sha256`. The three native input
manifests agree byte for byte. All other receipt fields agree.

The input manifest hash is:

```text
ab9fbd1a279135af0f4ae2d9445c97603ef4767b30a1f5aed1c7de1fbb56121f
```

The replay entrypoint hash is:

```text
0246a899091017c73361390c0822c9f25f1e4024dc021e91be5cdd6e010506fd
```

The full package manifest covers the proof, source files, replay code,
and validation receipts. It excludes only the manifest itself. The
independent publication review is retained outside this package by the
coordinating agent.

The separate [primary source check](validation/PR2588-SOURCE-VERIFICATION.json)
confirms all five PR #2588 phase-source files against GitHub bytes at
commit `8cd9dc88e24f062e2ca2fa7f4844a3d3319381fb`. It recomputes both
the Git blob hash and SHA-256. Four files used new Contents and separate
blob reads. The fifth used an earlier readback at the same exact commit.
The source notice, its two referenced notices, source README, and
same-commit license are retained. The
[readback index](validation/pr2588-readback/INDEX.json) maps the original
evidence paths to the portable copies in this package. These added
publication records do not change the 187 replay inputs or their manifest.

These checks verify the listed exact local maps and costs. They do not
repeat the fixed-pair enumeration, prove a global minimum of 38 ports,
regenerate every historical phase-compiler output, or replay the current
selected supplier. They do not establish a complete multiplication
theorem or a new complete kappa bound.
