# Provenance of the files in this directory

These receipts come from a **development run** of `reproduce.py` by PMPack with a prepared retained-native cache (`--prepared-retained`, jobs 3). They are NOT from the no-cache release runs.

Stage times of that development run: derive-source 2.8 s, derive-preload-move 2.8 s, fresh-shared-native 88.8 s, complete-admission 473 s.

Separately, the complete no-cache `verify_release.py` (fresh retained bootstrap, fresh shared natives, complete admission and outer release) passed on:

| OS | Result | Wall time |
|---|---|---|
| Windows (Python 3.12, jobs 3) | PASS_RELEASE | 957 s |
| WSL Ubuntu-24.04 (Python 3.12, jobs 3) | PASS_RELEASE | 646 s |

Both reproduce the exact kappa in `CLAIM.json`. The receipts of those two runs are not stored here; `evidence/pr2863/` is the inherited predecessor record.
