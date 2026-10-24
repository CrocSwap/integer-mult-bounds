# Local validation

Checked on 2026-10-23 on Darwin arm64 with CPython 3.12.14, standard library
only. The bundled interpreter was
`/Users/temp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.
No new dependency installation was required.

## Commands and outcomes

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-cache-reuse --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-cache-reuse
python3 -B scripts/research_selected_baseline.py
```

The metadata/source-pin check passed. The registered replay passed both
`-I -W error -B verify.py` and `-I -O -W error -B verify.py`, each in its
launcher-supplied private bytecode-cache namespace. They reproduced all saved
mathematical fields read-only and ended with
`PASS_REGISTERED_RESEARCH_PACKAGE research/gaussian-cache-reuse outcome=partial`.
Explicit guards and all-column comparisons remain active under optimization.
Result comparison uses the JSON representation, including string rank keys.

Coverage: 256 exact canonical frame pairs including 140 non-nested pairs;
40 independent input columns in each main orientation and in the supplied
observation module; eight correlated observation fixtures; wrong phase,
wrong raw-dual orientation and stale-snapshot controls; restored/proportional
row controls; all 15 two-qubit Lagrangians and 6,750 paths/trees; all 16
selected center block-orientations with 22 targets each; complete local paid
profile reconstruction; outward rational moment signs at four exponents
and a losing half-exponent control.

The selected-baseline command passed source/metadata orientation only. It is
not the full selected replay. No new selected supplier was installed, so
native, Lean, Docker, full compiler/precision/tape and multiplication-theorem
replays were not run. The all-width identities and lower bound are written
proofs, not kernel-checked theorems or an independently reviewed admission.

## Frozen evidence

The plan was frozen at `2026-10-23T13:12:01.622494+00:00` before exact Clifford
realization and the all-column checker. The frozen geometry file already
contains the word skeleton. Its prediction is a module moment saving, not
a blind design forecast or a new kappa. The observation variant and final
proof are subsequent derivations.

| File | SHA256 |
| --- | --- |
| `PLAN.json` | `9d914483465b5da9952a8c2ad3c1017ad231ffa6b1c2681eb846d4b98b6fd649` |
| `geometry.py` | `20c217d44893d2cc3b517af826936fc8a4c58f498f5bf76b833e5599a25d9084` |
| `RESULT.json` | `127aaacd8c24043129f224f56f14f436826c218091c82bde647ef9f46fe9c3c5` |

## Upstream checkpoint and scope

The investigation started at canonical main
`ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c` and refreshed to
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. Selection, catalogue,
family guidance and every pre-existing declared source pin were unchanged.
Upstream was merged without modifying frozen evidence, and the package was
replayed with its updated Git-reader cleanup. The newly archived
active-feedback README is a separately pinned provenance source.

The overlap search and relevant live claims are recorded in TASK.json.
At the initial validation checkpoint no external post or PR had been made.
zxv subsequently authorized this focused contribution PR. No selected-frontier
update or maintainer queue action is included.

## Committed bytes and Git free replay

The byte preflight passed for all 24 package/input files at
`40eeaa2a363ec8f9bc420b3bb6e337234949b308`:

```sh
python3 -B scripts/check_research_commit.py --package research/gaussian-cache-reuse
python3 -B scripts/export_research_package.py export --package research/gaussian-cache-reuse --ref 40eeaa2a363ec8f9bc420b3bb6e337234949b308 --output /tmp/gaussian-cache-reuse-40eeaa2a36.tar
python3 -B scripts/export_research_package.py check /tmp/gaussian-cache-reuse-40eeaa2a36.tar
```

The 580 KiB export passed its exact inventory/hash check. It was extracted
into a fresh temporary directory with no Git checkout and replayed normally
and with `-O`, using the same Python 3.12 interpreter, `PATH=/nonexistent`,
`-I -W error -B` and fresh `-X pycache_prefix` directories. Both mathematical
replays passed and the temporary extracted files were removed. Subsequent
documentation refinements leave the verifier, plan and result bytes unchanged.
This is evidence for the declared mathematical replay inputs, not hosted CI.

The additional `--check-source-history` preflight did not pass: this checkout
is shallow and the tool requires full Git history. It reported
`source-history check requires full Git history`. No full-history download
or weaker replacement check was used. The successful byte/export checks do
not substitute for that separate optional publication-history preflight.

## Focused publication replay

The publication branch starts at canonical main
`ff3cc58e370d0f678e529246f8c73e8094e18fcf` and contains only this package.
Earlier exploratory packages stay on the development branch. Frozen PLAN,
geometry and RESULT bytes are unchanged. PLAN's `base_commit` records that
local development checkpoint; it is not a replay dependency. The consumed
source pins are the canonical commits declared in SOURCES.json.

The registered normal and optimized commands above passed again from the
focused branch. A fresh committed export at its reachable commit
`5a40115affefff6a6811996e7c175a4e4ab10a40` passed inventory/hash checks and
both Git-free mathematical replays, using the same isolated Python flags,
fresh bytecode directories and `PATH=/nonexistent` described above.

For publication, this reachable snapshot replaces the development-only
`40eeaa2a36` reference in the historical export example:

```sh
python3 -B scripts/export_research_package.py export --package research/gaussian-cache-reuse --ref 5a40115affefff6a6811996e7c175a4e4ab10a40 --output /tmp/gaussian-cache-reuse-publication-5a40115aff.tar
python3 -B scripts/export_research_package.py check /tmp/gaussian-cache-reuse-publication-5a40115aff.tar
```

Publication status and credit refinements after that snapshot change no
scientific input, verifier, frozen plan or result. Metadata and committed-byte
checks cover the final publication commit separately.
