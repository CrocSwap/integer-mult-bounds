# Interleaved helper-basis residual audit

This package reproduces the three requested PR7726 restriction/split
comparisons with 54 explicit rational certificates. A separate checker tests
formal coefficient identities and every response equation. It confirms the
three chosen contracts and the three published alternate-equation failures.
The complete invoice and rational price signs also match. No new kappa is
claimed.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[CERTIFICATE.json.gz](CERTIFICATE.json.gz), [SOURCE-PINS.json](SOURCE-PINS.json)
and [CREDITS.md](CREDITS.md). The exact source constructor is retained; its
witness evaluator and pricing engine are not used by the new checker.
This is source-aware checking with a shared constructor, not blind or
independent human acceptance.

Run with CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/interleaved-basis-residual-audit
```

Both registered commands end with:

```text
PASS_INTERLEAVED_BASIS_RESIDUAL_AUDIT {'dual_identities': 30, 'primal_solutions': 24, 'primal_equations': 176320, 'nonzero_multipliers': 10484} 96512 paid 17296 productive
```

The optional generate.py script proposes the deposited certificate. It is
separate from acceptance and is not run by the registered checker.

## Open next questions

Can a separate constructor reproduce all journal edits and the full physical
application? First compare its graph with the exact published digest, then
check a changed edit that must fail. Can the 2^30 scalar allowance or path
grid be reduced for this graph? That requires an explicit physical audit;
the older graph's scale does not transfer. Neither task is claimed here.
