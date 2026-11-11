# Sharp Gaussian half-shift inverse lower envelope

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. No new kappa.

For every integer N>=1, define the normalized Gaussian section

```text
T_N^epsilon(q)[i,j] = q^((j-i)^2-epsilon(j-i)),
0<q<1, epsilon in {-1,1}, 0<=i,j<N.
```

Its exact scale-uniform inverse-norm infimum is

```text
inf_(0<q<1) ||T_N^epsilon(q)^(-1)||_2
    = 1/(2 sin(pi/(4N+2))).
```

For N>=2 every admissible q gives a strictly larger norm, and q tending
to zero approaches the infimum. At N=1 the norm is exactly one. The
envelope divided by N tends to 2/pi. This gives a sharp universal lower
allowance at each size. It does not give the actual norm at a fixed q.

[PROOF.md](PROOF.md) uses the q-LDU identities cited from Jose Manuel /
jmbarrancoml's [#4193](https://github.com/CrocSwap/integer-mult-bounds/pull/4193).
The new step compares the entire positive checkerboard inverse with the
upper triangular all-ones matrix, whose classical singular value is
explicit. The small-q limit proves sharpness. This takes the finite-cap
sharpness question of #4193; it does not audit its factors or scientific
verifier. Earlier related lower estimates in Nick Petalas's #5150 and
the upper-bound improvement in #6459 retain their credit. No claim that
all linear-growth consequences are new is made.

## Reproduce

From the repository root with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-half-shift-envelope/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/gaussian-half-shift-envelope/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-half-shift-envelope
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-half-shift-envelope --check-source-history
```

Another CPython 3.12 path may be substituted. The direct checker prints
`PASS_GAUSSIAN_HALF_SHIFT_ENVELOPE` in a generated JSON receipt bound to
all six package files by SHA256. It writes nothing. Expected wrapper
statuses are `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. No receipt is handwritten or committed.

The exact check enumerates 80 rational endpoint matrices at five scales
and sizes one through eight. Gauss-Jordan inversion checks both inverse
products, then all 2,040 entries against the new triangular comparison.
All 70 nontrivial-size cases have a strict diagonal witness. It also
checks 32 complete Laurent-polynomial spectral identities, eight pairs
of triangular inverse identities, 28 small-scale matrices and 21 strict
decreases in their squared Frobenius errors. Ten invalid inputs reject.
Five semantic controls distinguish the triangular comparator, checkerboard
signs, endpoint transpose, inverse corruption and the interior-shift domain.
Every check remains active with Python optimization enabled.

## Scope and credit

The universal quantifiers and infimum rely on the written proof and its
cited q-LDU premise. Finite checks are corroboration. No predecessor code
or external mathematical runtime input is imported. [SOURCES.json](SOURCES.json)
pins exact predecessor statements as historical provenance at canonical
main e54523517d0f03e58352e647c403a5af3e525a57. Frozen sources are unchanged.

Credit Jose Manuel / jmbarrancoml #4193 for the explicit question and
finite-cap framework; Vlado Vojdanovski #1673 for the retained Gaussian
q-LDU identities; Jeremy Kothe and the #1758 contributors for the shifted
Gaussian lineage; Cinna Davis for the later broad caller; and Nick
Petalas #5150/#6459 for related lower and upper results. Triangular
singular values, positivity, Perron's theorem and continuity of inversion
are classical. The contribution here is their sharp scale-uniform
half-shift consequence. No general literature-priority claim is made.

This changes the `uniform-transfer-audit` card to an analytic side result,
as recorded in [TASK.json](TASK.json). The card's selected-binding first
control passed. The live selected #7000 result and kappa 0.00363005817
remain unchanged. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19538492)
records the target and overlap checks. Those checks cannot exclude
unpublished work or every historical diff.

No interior-shift lower envelope, fixed-q sharp coefficient, production
normalization/gauges, rounded inverse, physical execution, native/compiler/
stock/tape invoice, supplier admission or complete multiplication theorem
is supplied. No selected framework assumption is discharged. Lean, Docker,
predecessor scientific suites and the selected full cold replay are unrun.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Determine the sharp leading coefficient at a fixed positive q as N
  grows. First bound the positive inverse's difference from a constant
  multiple of the triangular matrix. Boundary and near-diagonal terms
  are the missing estimate.
- Determine the finite-size crossover for shifts approaching a half.
  First retain the geometrically decaying triangle under diagonal
  conjugation. A sharp two-parameter estimate and justified limit regime
  remain open. Interior shifts can have a bounded inverse norm as N grows.

Structured relevance, first steps and blockers are in TASK.json.

## Verifier constraints

The verifier has no recursion, dynamic code, subprocess, network, solver
or third-party dependency. Matrices are at most 8 by 16 including
augmentation; polynomial degrees are at most 32 and Laurent supports
have at most 65 entries. Input fractions have at most 20 bits per part;
the fixed fixture list bounds all exact arithmetic. Each function has
fewer than 60 physical lines. Explicit exceptions preserve invariants
under optimization. Package hash reads cover six files of at most 256 KiB.

Power of Ten rule 3 deviation: CPython allocates managed integers,
fractions and containers during these finite checks. Only one matrix
case is live at a time, with the fixed dimensions and fraction inputs
above. This is a bounded certificate checker, not a fixed-allocation
numerical runtime. A runtime integration would require a separate
storage design. Warning-strict normal/optimized runs and source
compilation supply the available diagnostics; separate type/lint
analysis and repository-wide analyzer changes are unrun.
