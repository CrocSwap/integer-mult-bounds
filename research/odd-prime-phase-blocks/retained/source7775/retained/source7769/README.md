# Exact fifteenth-root column capacity

Eight rows over fifteenth roots support exactly four orthogonal
columns. The proof gives an attaining matrix and excludes five by a
complete normalized extension graph. Its 95 vertices form two
six-cycles and 83 isolated vertices, so no triangle exists.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[verify.py](verify.py), [SOURCE-PINS.json](SOURCE-PINS.json) and
[CREDITS.md](CREDITS.md). The general source bound permitted five
columns; this finite result determines the exact count.

Run with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/fifteenth-root-column-capacity
```

Both registered modes print `PASS_FIFTEENTH_ROOT_COLUMN_CAPACITY`.
The source verifier runs unchanged. No new kappa or physical supplier
follows. All five assumptions and the selected frontier remain.

## Open next questions

- Determine whether four is also the sharp count over roots of order
  3*5^b for b>1. First control the extra prime-power cosets; the present
  normalization does not remove them.
- Resolve an exact column capacity at another row count and alphabet.
  State a new finite domain or supply a general proof.
- Connect a valid matrix to a physical preparation and caller cost.
  Exact orthogonality alone does not supply that implementation.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
