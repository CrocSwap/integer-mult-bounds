# Local verification record

The scientific commit is 24f03629fc2a939ea0c6c015017bf1cdc07e06cd.
The environment is CPython 3.12.13 on macOS arm64. The scientific package
needs only the standard library. Its archive has 38 authenticated source
files. The selected record remains unchanged.

## Executed checks

The direct replay constructed `RESULT.json` with the final bound and
changed-source ceiling. Both registered commands then passed:

```sh
/tmp/kappa-1101-venv/bin/python -B scripts/research_package.py \
  --package research/mixed-root-source-composition
```

The runner executed normal and optimized Python. Both reported
`PASS_MIXED_ROOT_SOURCE_COMPOSITION_KAPPA_00328551`, followed by
`PASS_REGISTERED_RESEARCH_PACKAGE`. The result includes every native input
and phase, the caller, complete price, compiler, 58 outer predicates,
53 rejection controls and the ceiling for all binary child sizes.

Three separate process controls changed the source archive, claim literal
and ceiling literal on temporary package copies. Each failed its declared
hash or exact-adapter gate under optimized Python.

Metadata and source pins pass. `git diff --cached --check` passed before
the scientific commit. The byte preflight verified all 14 committed package
files. The official export passed its exact inventory and hash check:

```sh
python3 -B scripts/check_research_commit.py \
  --package research/mixed-root-source-composition
python3 -B scripts/export_research_package.py export \
  --package research/mixed-root-source-composition \
  --ref 24f03629fc2a939ea0c6c015017bf1cdc07e06cd \
  --output /tmp/mixed-root-source-composition-20261102.tar
python3 -B scripts/export_research_package.py check \
  /tmp/mixed-root-source-composition-20261102.tar
```

The export SHA256 is
`19e4c2d34c2893049fa8dbf8c26a0f3c0bb2add8693000e4e5435583616df90a`.

## Isolated replay

The complete committed export passed an optimized replay with empty PATH.
An OS profile denied network access, reads from the live checkout and
writes to the export. Separate probes produced PermissionError for each
denied action. A further probe confirmed that Git was absent from PATH.
All 15 exported files, including the export receipt, retained their hashes
and modes. The replay took about 53.25 seconds.

The committed ceiling adapter removes two inherited trailing blank lines
through a declared exact edit. This whitespace change followed registered
replay. The isolated replay checked the committed bytes and the complete
unchanged scientific receipt. No source assertion, interval condition or
compiler predicate was weakened.

`VALIDATION.json` retains the isolated-run and process-control receipts.
The later validation-file commit changes documentation only.

## Limits

These are author checks. Hosted CI and independent scientific review have
not run for this local package. The five framework assumptions remain.
The uniform word, rounded multiplier and practical running time were not
tested. No full source-history ancestry check is claimed for the shallow
checkout; separate-branch executable inputs are retained in the archive.

The final canonical-main refresh still gave
7c49fe32c55de02c2c873655c804b16e4c3fef0a. PR6353 remains open at the retained
db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3 head. No push, PR, merge, closure
or selected-frontier change was made. The larger requested gain remains
unmet; this package supplies only the stated composition increment.
