# Validation at the frozen base

Run on 2026-10-13, CPython 3.14, Windows, base ba82555c64e1879e4b7decce28186f208fcb8262.

| Command | Result |
|---|---|
| `python -I -B research/leaver-monotone-optimality-seed21/verify.py` | PASS, eight cores, minimum 21, projected minimum 5, eleven controls |
| `python -I -O -B research/leaver-monotone-optimality-seed21/verify.py` | Same PASS and complete saved receipt match |
| `python -I -B scripts/verify_selected_result.py` | PASS selected record, exact kappa, original source inventory and proof supplement; 1672188119205421/10^18 |
| `git diff --check` | PASS before staging; staged check also required before commit |
| `make verify` | Not run: `make` is unavailable (`not recognized as an internal or external command`) |

All 24 projected searches exhaust 16,384 states each, with no cap or timeout. The relaxed type control attains four. Other controls reject an x receiving y dirt, an extra target dependency, a missing projection coefficient, inconsistent scaled coefficient, one omitted ADD, Boolean unit coefficient, deletion of a required source pin, duplicate JSON keys, nonfinite JSON and floating seed 21.0. Default replay does not regenerate the certificate.

The first development run exposed a stale-source assumption: the retained package evidence/local full word is R492, so a literal k8 cell search there correctly found no matching cell. That word was removed from the proof's consumed sources rather than presented as a selected-word replay. Final binding is to the named eight core files, the exact named entries of CODED-CELLS-k8, the construction source and immutable assembly. This is an explicit limit, not an admission failure of the selected construction.

No native, full hosted, precision, owner-map or all-size replay is claimed. The selected-result script is a provenance guard, not an independent proof of those interfaces. The new theorem concerns scalar gate counts in the stated class only.
