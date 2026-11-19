# No mixed-cycle input at q+3 rows

There is no (q+3)-by-(q+2) partial Butson matrix over roots of order
3q^b when q>=5 is prime and b>=1. In particular, the eight-row,
fifteenth-root input requested in PR7744 does not exist.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[verify.py](verify.py), [SOURCE-PINS.json](SOURCE-PINS.json) and
[CREDITS.md](CREDITS.md). The proof first forces an original-alphabet
completion, then excludes it by a Hermitian trace contradiction.
It does not infer nonexistence from a search limit.

Run from the repository root with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/mixed-cycle-column-obstruction
```

Both registered modes print `PASS_MIXED_CYCLE_COLUMN_OBSTRUCTION`.
The retained source replay is unchanged. Exact finite checks support the
written proof; they are not a formal proof-kernel acceptance.

No physical supplier, new kappa or selected-frontier change follows.
All five framework assumptions remain. The selected cold replay, Lean
and Docker were not run.

## Open next questions

- Resolve mixed-cycle counts that admit more than one cycle decomposition.
  Start with the projected Gram constraints; the triangle argument above
  depends on the precise ratio q/(q+3).
- Determine which parts survive an alphabet of order 3^a q^b with a>1.
  The projected phases then have more than three possible values, so a
  nontrivial triangle phase need not give a negative minor.
- Connect a valid recovery interface to a complete physical caller cost.
  This package supplies an obstruction and no physical recovery routine.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
