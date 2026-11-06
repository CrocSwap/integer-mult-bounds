# Sharp dimension growth for the column-capped Euclidean resolvent

For integer m>=2 and fixed 0<rho<1, consider every complex n by n E
with absolute row sums at most rho and column sums at most m rho.
The worst Euclidean norm of (I-E)^-1 has these sharp growth orders:

- rho sqrt(m)<1: it tends to exactly 1/(1-rho sqrt(m)).
- rho sqrt(m)=1: Theta(log n).
- rho sqrt(m)>1: Theta(n^(log_m(rho sqrt(m)))).

[PROOF.md](PROOF.md) gives the all-dimension upper bound and nilpotent,
zero-diagonal tree witnesses. At the critical point coherent radial input
proves logarithmic growth; a single inverse column gives only a square root
of that logarithm. This distinction matters when inferring Euclidean
precision bounds from column budgets.

This is a scoped proof with exact finite corroboration. It changes the
uniform-transfer-audit card to an abstract conditioning side result. The
original actual-caller gate is unmet. No selected assumption, supplier,
kappa or selected-frontier change is claimed.

## Evidence and reproduction

From the repository root, Python 3.12 with the standard library:

```sh
python3 -B scripts/research_package.py --package research/column-cap-spectral-growth
```

The registered normal and optimized checks pass with identical generated
counts under CPython 3.12.9 and use exact rational arithmetic.
They check 15 dense tree fixtures, 960 capped real matrices, 12 complex-phase
realifications, 63 virtual radial cases through height 64 and six controls.
They compare full dense inverses with independent path formulas, check
radial matrix actions and critical coherent-input ratios, and certify the
upper bound through exact positive-semidefiniteness tests. Finite tests are
not proof-kernel or independent human verification. The verifier imports
no predecessor scientific engine. Source authentication is performed by
the package runner; sources remain unchanged.

## Scope and related work

Base is canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a,
priority revision 8. The selected baseline binding check passed.
The live handoff-first scan and complete cached overlap covered 762 open
PRs, 6,884 Discussion records and all 8,917 local note records. This is
body/note coverage, not every diff or unpublished result.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19448717).

Nick Petalas's PR6788, head c1d915303450bec823784befd3ada5a261796a5c,
and ToikY's PR6806, head c9f16c03d67638bf02e3a7cff785480474790718,
optimize the induced 1-norm under integer and fractional column capacities.
This result concerns Euclidean norm growth, with a different critical
boundary. Their PR bodies were read; their scientific suites were not run.
Ali Romman's PR5255 gives the row-only support envelope and sharp banded
gap exponent. Its proof is credited, not re-established here.

## Open next questions

- Bind row/column caps or a stronger weighted condition to one actual
  emitted Gaussian matrix. First extract its exact support and rounded
  coefficients; those source and preparation obligations are missing.
- Determine the exact finite-dimensional Euclidean optimum. Begin with
  small rational cap polytopes; the tree lower bound and triangle upper
  bound here need not coincide at finite n.

Fractional branching, exact finite optima and physical integration are
unclaimed. Native operators, owned erasure, uniform compiler, precision/tape
and analytic recovery remain separate. No selected cold replay, native
suite, Lean or Docker run was performed.

## Credit and assistance

Prepared for zhaobenny. Credit Nick Petalas PR6788, ToikY PR6806,
Ali Romman PR5255/PR5306, Cinna Davis PR4100 and James Reed PR4282,
with their retained conditioning and Gaussian lineage. Classical norm
interpolation, geometric sums and regular-tree radial methods retain
credit; general literature priority is unclaimed. Apache-2.0.

Produced with OpenAI GPT-6.1 Sol at high reasoning effort through Codex.
No subagents were used. The proof and verifier were written by the same
assistant after source exposure; independent review is unclaimed.
