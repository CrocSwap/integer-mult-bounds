# Validation and source coverage

Environment: CPython 3.12.14, Linux x86_64/glibc 2.41; standard library only. Canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected PR6030. The activated environment's installed NumPy/SymPy/SciPy are not used by this package. Upstream was refreshed before packaging and remained identical.

## Scientific verification

```sh
python3 -B scripts/research_package.py --package research/pr6551-retirement-audit
python3 -I -O -B research/pr6551-retirement-audit/verify.py
```

Both exit 0. The registered command runs both normal and optimized scientific replays with metadata/source-pin validation; observed total 1.600426 seconds. The additional optimized direct run took 0.684600 seconds. The recorded child high-water RSS is 63,820 KiB (the measuring process reports the maximum across its completed children). Full commands, environment and results are in [evidence/local-runs.json](evidence/local-runs.json), [registered.log](evidence/registered.log) and [optimized-direct.log](evidence/optimized-direct.log).

The deterministic [RESULT.json](RESULT.json) has SHA256 `f872cfe53b831e904cae956abb81138efb1ce735ace664fcfdca53592da98364`. It contains both complete 1,225-coefficient caller checks, the separate four-fiber cut certificate, event/tree accounting, native archive identity and all 22 semantic negative controls. Neither source constructors nor predecessor scientific verifiers are imported or executed. Accounting reads the retained native word only for source identity, 104 ports, 562 public helpers, 3,456 paid jobs per native invocation, and cancellation of the same 18 calls.

Three external optimized corruption runs also exit nonzero as required: changed caller source, changed native archive byte, and changed expected receipt. Their exact rejection reasons are in [evidence/external-corruptions.json](evidence/external-corruptions.json). Source corruption fails authentication; changing only the expected receipt fails the independent recomputation comparison.

Early package validation rejected a nonstandard outcome label and the capitalization/heading of the open-questions section. Both metadata issues were corrected before the successful registered run; no scientific result changed. The internal review also corrected a next-step source link to the exact public candidate pricing file. [REVIEW.md](REVIEW.md) records the mathematical review and shared assumptions; the final integration review is retained alongside it.

## Scope not run

No full native replay, all-width physical proof, source numerical-root/tail/outer replay, selected `make frontier6030-verify`, historical `make verify`, Lean, Docker or hosted-CI inference is claimed. These would test different obligations and were unnecessary for the scoped audit. The complete physical ordinary-work rate remains inherited evidence. The favorable Gaussian difference is not a fresh κ certificate or supplier admission.

## Export and committed-byte checks

At commit `28929ae5b3bb575c0bb423d26d98d6f878ab8dd3`, these commands passed:

```sh
python3 -B scripts/check_research_commit.py --package research/pr6551-retirement-audit --check-source-history
python3 -B scripts/export_research_package.py export --package research/pr6551-retirement-audit --ref 28929ae5b3bb575c0bb423d26d98d6f878ab8dd3 --output /tmp/retirement-audit.tar
python3 -B scripts/export_research_package.py check /tmp/retirement-audit.tar
```

The preflight compared all 47 committed files and confirmed the declared base-history dependency. The export contains those files plus its integrity metadata. Normal and optimized direct replays then passed from the read-only export with no Git metadata and an empty PATH, in 0.533343 and 0.646604 seconds. Both returned the exact committed scientific receipt; all 48 file hashes and modes were unchanged. [evidence/cold-runs.json](evidence/cold-runs.json) records exact actual paths/commands and [cold-normal.log](evidence/cold-normal.log) / [cold-optimized.log](evidence/cold-optimized.log) retain complete outputs. The commands above substitute a portable temporary output path for that record's local path.

The final evidence commit adds only validation/overlap records and logs. The checkers, frozen inputs and RESULT retain the hashes reviewed in FINAL-REVIEW.md. Publication repeats the byte/history preflight and export replay on that actual final commit. Remote CI is reported separately in the contribution PR; local success does not imply hosted success or maintainer acceptance.
