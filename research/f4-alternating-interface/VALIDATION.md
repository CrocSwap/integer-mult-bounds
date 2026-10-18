# Executed validation (2026-10-13)

CPython 3.11 on Windows; standard library only.

- Normal `python -B verify.py` completed: 452 phase cases, 114,752 entries.
- Optimized `python -O -B verify.py` completed with identical JSON.
- All four internal rejection controls passed in both modes.
- Embedded ambient hyperbolic block passed separately.
- Independent enumeration of Hermitian nullspaces matches trace-form ranks.
- Copied verifier alone to a transient directory within math: identical receipt.
- Existing `--output RESULT.json` rejected; retained receipt unchanged.
- All four consulted-source SHA-256 pins recomputed and matched.
- `git diff --check` passed. Selected certificate and production files unchanged.

No full make verify, selected cold replay, formal proof assistant or remote
CI is claimed. Repository-wide validation would not strengthen this isolated
finite interface result. Source-code and mathematical review remain welcome.
