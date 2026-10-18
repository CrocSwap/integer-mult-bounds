# Validation record

Recorded on 2026-10-13, native Windows, CPython **3.11.15**. Exact base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.

| Check | Result |
| --- | --- |
| `python -B research/complex-jp8-cleanup-fusion/verify.py` | PASS: 999 blocks, 19,688 saved real primitives, 716 input columns in each orientation, ten rejected arithmetic mutations |
| `python -B research/complex-jp8-cleanup-fusion/test_verify.py` | PASS: seven tests, including all 999 blocks in a separate flat-vector column interpreter, separate grouping/cost enumeration, noncommuting dual-order witness, emitted-frame and ended-helper mutations, omitted paid child |
| `python -I -S -O -B research/complex-jp8-cleanup-fusion/verify.py` | Same complete receipt; checks do not depend on Python assertions or site packages |
| `python -B scripts/verify_selected_result.py` | PASS: selected record, exact kappa, original source inventory, and proof supplements |
| Minimal copied checkout in a path containing spaces | PASS with only this package and its six pinned input files, from an unrelated working directory, using isolated optimized Python |
| Recompress both gzip inputs with level 1 and mtime 17 | Identical mathematical receipt in the minimal checkout |
| Change the first canonical cleanup coefficient | Rejected by source pin before replay |
| Inflate committed saved-primitive count by two | Rejected after fresh receipt recomputation |
| Write a receipt to an existing sentinel file | Refused; sentinel bytes preserved |
| Local Markdown links | All 23 links checked at validation time resolved |

The separate scoped AI reviewer independently recounted all groups and prices,
and corroborated both strengthened prefix controls. The reviewer found no
remaining material mismatch between the code, certificate, and stated scope.
This is disclosed AI review, not independent human review or formal proof.

The complete selected supplier cold replay, repository-wide `make verify`,
global invoice/admission regeneration, Lean, and remote Linux CI were **not
run**. The change only adds this standalone research package; no existing
supplier, generator, checker, selected certificate, or `upstream/` file changes.
The production emitter's per-macro private-work contract remains an explicit
integration obligation. All inherited asymptotic assumptions remain open.
