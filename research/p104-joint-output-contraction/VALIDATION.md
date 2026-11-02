# Validation record

The author checks ran on CPython 3.12.13, macOS 26.6.1 arm64. The package
uses only the Python standard library. No subagents were used.

The complete authoring run passed:

```sh
python3.12 -I -B research/p104-joint-output-contraction/verify.py --write
```

The normal and optimized registered replays both passed:

```sh
python3.12 -B scripts/research_package.py --package research/p104-joint-output-contraction --check-only
python3.12 -B scripts/research_package.py --package research/p104-joint-output-contraction
```

Each mode reports `PASS_P104_JOINT_OUTPUT_CONTRACTION_KAPPA_00315057`.
The runner reports `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome
`completed`. Both modes check the same complete receipt and all 26 explicit
rejection controls. The retained native-phase and price controls also pass.

Coverage includes the exact joint basis and zero temporary rows, all source
and changed scalar inputs, the separate 799-column dense replay, 2,932 native
maps with absolute phases, 7,904 physical caller contacts, all paid and
productive jobs, both rational interval engines, completion, compiler and
all 54 strict plus four functional outer predicates. The old supplier with
the same caller fails at the new claim. Its crossing matches PR6350.

The signed invoice preflight is `inconclusive` for all increasing concave
tariffs: its hinges have both signs. This is consistent with the six extra
paid calls and zero rank-mass change in the signed difference. The package
uses the complete exact moment calculation at the declared saving. It does
not claim a uniform improvement for every concave tariff.

All thirteen live source files are declared in VERIFY.json and pinned at
canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Direct Discussion
reads and recent open PRs were refreshed before publication. The cached
overlap search covered 317 open PRs and 6,165 Discussion records with full
remote pagination. Its local note search covered 55 records and was sparse;
8,864 HEAD note paths were not searched. Code diffs and unpublished work
remain coverage limits. Main and priority revision 8 were unchanged at the
submission checkpoint.

The five inherited framework assumptions remain. The uniform word and
rounded multiplier are not materialized. These are author checks, not an
independent scientific review or proof-kernel acceptance. The selected
frontier is unchanged.

## Committed bytes and cold export

The tested scientific commit is
`18cf11a6c411962494c7c4328818767bc8bb3533`. Its direct parent is the stated
canonical base. The committed-byte and POSIX execute-mode preflight passed
for all 28 package and input files. The official export and declared-input
inventory check passed for all thirteen live inputs:

```sh
python3 -B scripts/check_research_commit.py --package research/p104-joint-output-contraction --check-modes
python3 -B scripts/export_research_package.py export --package research/p104-joint-output-contraction --ref 18cf11a6c411962494c7c4328818767bc8bb3533 --output /tmp/joint-output.tar
python3 -B scripts/export_research_package.py check --check-inputs /tmp/joint-output.tar
```

The complete normal and optimized Python 3.12.13 replays passed from a
separate extracted directory. All files had mode 0444; all directories had
mode 0555. An OS sandbox denied writes below that directory. A deliberate
write probe failed with PermissionError. PATH was an empty directory, with
no Git. All 29 files, including the export receipt, and all 37 path modes
stayed unchanged. The normal run took 106.022 seconds and the optimized run
took 53.131 seconds on this host. These are replay times, not multiplication
performance measurements.

The first nested-sandbox launch stopped before the verifier because the
outer sandbox denied sandbox creation. The permitted launch then applied
the read-only policy and completed both modes. No code or mathematical
guard was changed to pass that check.

Two actual mutations of copied export files also rejected. A damaged byte
in the source WORD.json.gz failed its SHA256 check before source import.
An altered KAPPA literal failed the declared price-adapter check. Both ran
with Python assertions disabled. The original bytes were restored before
the sealed replays.

The optional `--check-source-history` preflight stopped with
`source-history check requires full Git history`. This checkout is shallow;
full history was not fetched. All source pins use the canonical base, which
the raw scientific commit records as its direct parent. No side-branch pin
is required. This parent check is not reported as a full-history pass.

The validation-record commit changes this file only. A later documentation
clarification labels the follow-up screen as local-only and unbundled.
All scientific code, witness, word, source pins and result bytes are unchanged
from the sealed replay. Hosted CI remains separate from these local checks
and from independent scientific acceptance.
