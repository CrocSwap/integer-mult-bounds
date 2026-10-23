# Validation

Environment: CPython 3.12 with numpy, macOS.

| Command | Result |
|---|---|
| `python3 -I -B research/coded-reverse-physical-fix/verify.py` | PASS; exact local pair, independent NumPy pair, coded roots, guards, outer ledger |
| `python3 -I -O -B research/coded-reverse-physical-fix/verify.py` | PASS; `need()` raises explicitly, so optimization does not remove checks |
| `python3 -B scripts/research_package.py --package research/coded-reverse-physical-fix` | PASS_REGISTERED_RESEARCH_PACKAGE, outcome=partial; both registered commands pass |
| `python3 -B scripts/check_research_commit.py --package research/coded-reverse-physical-fix --check-source-history` | PASS_RESEARCH_COMMIT_BYTES; 15 package/source files, source history f259dabc |

The verifier reads only the pinned PR4933 data and the outer ledger. It does not
run the full p19 controller, the fixed-tape field-map tariff, the denominator
13/52 implementation, the compiler, hosted CI or the formal kernel.
