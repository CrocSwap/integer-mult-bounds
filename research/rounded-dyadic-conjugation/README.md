# A sharp rounding carry at the dyadic connector boundary

**Scoped proof with exact finite corroboration. No new kappa.** This answers
one bounded part of the approximate-child question in Hanson Sun / bbMisk's
[PR1526](https://github.com/CrocSwap/integer-mult-bounds/pull/1526).

For the deterministic nearest-grid additive child
`Q_h(t)=h floor(t/h+1/2)`, one additional fractional bit makes `H B D` compute
`z+s Q_h(2Bx)`. Its sharp coordinate error is h/2, versus h for two ordinary
rounded queries. `D A H` also has sharp error h/2 and restores its root.
Both intervals have exact literal inverses when the sign is applied after
rounding. The extra root bit and both scale passes remain paid obligations.

The local accuracy improvement creates an exact dirty-root obstruction in
PR1526's displayed B0 repair:

```
z_final - z_initial = rho_h(B0 x0),
rho_h(v) = Q_h(2v) - 2 Q_h(v) in {-h, 0, h}.
```

Every value occurs. With h=1, B0=1/8 and x0=3, the word leaves root error 1
even with zero output maps. Keeping coarse rounding in the special B query
restores cancellation, with the original error h. A final correction by
`-rho_h(B0 x0)` also restores the root, but needs its own implementation and
invoice. One extra fractional bit alone does not admit the refined word.

[PROOF.md](PROOF.md) proves the local optimum, the exact three-interval carry
classification, the necessary and sufficient root-restoration condition, and
the two stated root repairs. This is a new rounded extension of the exact
predecessor circuit. It does not identify an error in that exact circuit or
re-establish its optimum.

## Reproduce

From the repository root, CPython 3.12 and the standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rounded-dyadic-conjugation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rounded-dyadic-conjugation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rounded-dyadic-conjugation/verify.py
```

The direct verifier emits a generated JSON receipt bound to all six package
file hashes, followed by `PASS_ROUNDED_DYADIC_CONJUGATION`. It writes no files.
Both registered commands use warning-strict isolated normal and optimized
execution. The checks enumerate 3,402 source intervals, 1,050 output intervals,
102 complete rounded-word fixtures and eight controls. The full-word fixtures
use two-coordinate noncommuting matrices, immutable sources, dirty outputs
and dirty roots, and replay literal inverses. Coarse/refined root endpoints
and the correction agree with the proved formulas.

The controls compute failures of coarse whole-target rounding, rounding the
negative as an inverse, omitted doubling, missing/wrong carry correction and
the false coarse h/2 error bound. They also check the root representation
requirement and reject a zero grid. No predecessor executable is imported or
replayed. The card's 945-pairing positive control and selected binding-only
orientation were run separately as required orientation, not as contributions.

## Scope and provenance

Canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. [SOURCES.json](SOURCES.json) pins the predecessor README as
the sole live input. [TASK.json](TASK.json) retains the original
`connector-alphabet-change` card and records the changed scope to its open
rounded-interface question. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370233)
targets this local precision and admissibility decision.

Live open PRs, recent account work, handoff claims and local reservations were
checked before claiming. Canonical-main README searches and merged searches
used PR1526, dyadic connector, rounded conjugation, root carry and related
terms. The overlap helper searched 506 open PRs and 6,502 discussion records
with complete remote pagination; its sparse local scan covered 118 of 8,917
HEAD note records. Separate Git searches covered committed READMEs for the
target terms. These searches omit arbitrary diffs and unpublished work and
do not prove novelty. PR1556 concerns exact unit-phase query tariffs;
PR1770 concerns a different five-source binary connector. Neither supplies
this rounded carry formula.

The claim requires exact dyadic scales and source-only deterministic rounded
increments with the specified tie and inverse rules. It does not cover
target-dependent defects or inexact H/D. The full connector output-error
budget, actual recursive/native child, physical correction tariff, compiler,
stock, tape and outer recovery remain unproved. All five selected framework
assumptions remain. No selected cold replay, Lean, Docker, independent human
review or proof-kernel acceptance is claimed.

## Engineering constraints

The verifier has no recursion or subprocesses. Its arithmetic loops have fixed
finite bounds, its word has 15 events and its state has seven two-coordinate
rows. Every function is below 60 lines. Contracts use explicit exceptions and
remain enabled under optimized execution. Python allocates managed arithmetic
objects during execution; fixed fixtures and fixed-size live state bound their
number. This is the managed-runtime deviation from static allocation.
Warning-strict normal and optimized executions supply the relevant diagnostics.

## Open next questions

1. Can an actual recursive B child supply the carry repair for less than the
   removed child price after paying both scans? Begin with one literal native
   source, its exact coefficient precision and a paid source-only correction.
   Physical evaluation, routing and restoration costs are the blockers.
2. What is the complete output-error budget of the repaired rounded word?
   Propagate its actual rounded errors through every A read, keeping the carry
   until its final correction. The local radius and restored root do not bound
   those outputs. This needs a specified native norm and caller allowance.

## Credit

This contribution was produced by Nick Petalas. Credit Hanson Sun / bbMisk
for PR1526's exact word and open precision question, Ross Richardson for
PR944, martinxxx9 for PR1088, and the retained signed-connector lineage.
Nearest-grid rounding is classical. Independent human and formal proof-kernel
review are unclaimed. Apache-2.0.
