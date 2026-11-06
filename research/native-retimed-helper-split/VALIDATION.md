# Verification record

Executed on 2026-11-06 with CPython 3.12.14 and the standard library.
The upstream publication refresh still resolved to
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Complete scientific replays

| Run | Result | Elapsed seconds |
|---|---|---:|
| Corrected complete receipt regeneration | PASS_RETIMED_NATIVE_HELPER_SPLIT | 237.09 |
| Registered normal replay | PASS_RETIMED_NATIVE_HELPER_SPLIT | 245.32 |
| Registered optimized replay | PASS_RETIMED_NATIVE_HELPER_SPLIT | 128.62 |
| Standalone normal replay | PASS_RETIMED_NATIVE_HELPER_SPLIT | 236.23 |
| Final publication-source standalone optimized replay | PASS_RETIMED_NATIVE_HELPER_SPLIT | 132.53 |

The registered command was:

```sh
python3 -B scripts/research_package.py --package research/native-retimed-helper-split
```

It returned `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `completed`.
Both interpreters reproduced the exact complete receipt. All 60 package-file
hashes stayed unchanged. The standalone copies contained only those 60 files,
with read-only modes, outside a Git checkout. They ran from `/tmp` with the
environment cleared and `PATH=/nonexistent`, using the absolute Python
interpreter. The scientific code made no network request.

The final standalone optimized replay used every final executable byte. The
only executable edit after the registered runs removed an extra blank line
at the end of `split.py`; its Python AST was checked unchanged. The final
standalone copy and the publication source had identical hashes for all 60
files. This verification record is the sole additional documentation file.

## Decisive coverage

The replays regenerate the candidate and both caller retirements, check
arbitrary public inputs and owned storage, all signed native maps and phases,
1,536 explicit changed-pair columns, every caller contact and independent
field allocation. Separately written native and invoice implementations
agree. All three complete ordinary counts equal **535,415,008**, including
286,728 explicitly decomposed canonical adapters.

Both exact rational interval engines, finite strictification, the retained
compiler and all 54 strict plus four functional outer inequalities pass at
conditional kappa **165407/50000000 = 0.00330814**. Semantic controls reject
wrong phases, malformed native or ownership data, missing canonical adapters,
aliased independent fields and an insufficient BIT budget. Normal and
optimized execution both retain these checks.

The optional deterministic discovery replay also rediscovered the exact
published witness among its nine successful variants. Search-domain limits
and unsuccessful continuation experiments are in `RESEARCH-NOTES.md`; they
are not impossibility certificates.

## Publication byte checks

The package is additive and isolated. Reproduce the committed-byte and export
checks with:

```sh
python3 -B scripts/check_research_commit.py --package research/native-retimed-helper-split --check-modes
python3 -B scripts/export_research_package.py export --package research/native-retimed-helper-split --ref HEAD --output /tmp/native-retimed-helper-split.tar.gz
python3 -B scripts/export_research_package.py check --check-inputs /tmp/native-retimed-helper-split.tar.gz
```

The five inherited framework assumptions remain. Hosted CI, a materialized
full multiplier, formal proof-kernel acceptance, human peer review and
authentication of all historical pending-commit ancestry are not claimed.
