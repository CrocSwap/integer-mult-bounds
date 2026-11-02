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
