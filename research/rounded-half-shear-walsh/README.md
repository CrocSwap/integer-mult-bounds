# Sharp 9h/8 error for a rounded half-shear between Walsh axes

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with an exact finite certificate. For each
of the twelve directed pairs of four coordinates, the literal program

```text
x in h Z^4
y = R_h(Ax)
z = R_h((I + E_ts/2)y)
F(x) = R_h(Bz)
T = B (I + E_ts/2) A
```

has sharp error `max_x ||F(x)-Tx||_infinity = 9h/8`. Here A and B are the
two distinct normalized real Walsh axes defined in [PROOF.md](PROOF.md),
and every R_h rounds to nearest with ties to even. This determines an exact
value for a program outside the integer-shear law of
[CubeJerry #6146](https://github.com/CrocSwap/integer-mult-bounds/pull/6146).
The half-shear is rounded internally, so it adds a rounding site.

The direct triangle bound is 11h/8. The parity proof improves it to 9h/8,
and twelve explicit integer inputs attain that value. A nonzero rounding
error at the middle shear forces its stored target to be even and its source
to be odd. Those parities remove earlier error terms at a final half-tie.
The complete error vector has input period 16h in each coordinate. An exact
counterexample shows that the integer-shear period 8h is insufficient here.

This answers a nonintegral part of the intervening-shear question in
[Josie Elliston #6140](https://github.com/CrocSwap/integer-mult-bounds/pull/6140).
The previous integer result and pure-stage results are cited context, not
replay targets. No new kappa or selected-frontier change is claimed.

## Evidence and reproduction

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rounded-half-shear-walsh/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/rounded-half-shear-walsh/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/rounded-half-shear-walsh/independent.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rounded-half-shear-walsh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rounded-half-shear-walsh --check-source-history
```

Another CPython 3.12 path may replace the absolute interpreter. The direct
commands print `PASS_ROUNDED_HALF_SHEAR_WALSH` or
`PASS_INDEPENDENT_HALF_SHEAR_WALSH` inside generated JSON stdout evidence.
The primary receipt is bound to all eight package files and the one context
input. No receipt is hand-written or consumed as an acceptance premise.

Each interpreter enumerates all 786,432 directed-pair/input cases and hashes
the complete stream of 3,145,728 signed eighth-unit errors. The primary uses
literal butterfly arithmetic. The independent implementation uses dense
integer matrices and another rounding algorithm, with 3,072 complete-vector
Fraction comparisons. Seven named semantic controls cover the insufficient
period, sharp endpoint, tie rule, omitted middle rounding, omitted shear,
reversed word and signed ties. Eight invalid primary inputs are rejected.
The primary also checks 515 signed half-rounds and 576 signed/large period
translations. The mathematical theorem rests on the written parity proof
and explicit attaining inputs, not an extrapolation of finite experiments.

## Scope and provenance

Base `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. The
selected #7000 record gives conditional kappa `363005817/100000000000`.
The source-binding positive control passed; it was not a scientific replay.
[TASK.json](TASK.json) records the changed `uniform-transfer-audit` scope.
[SOURCES.json](SOURCES.json) pins the catalogue, selected record and the
unchanged integer-shear context. The package imports no predecessor code.

The theorem assumes exact pre-round arithmetic and sufficient range. It
does not cover another coefficient, complex mixing, extra stages or a
production caller. There is no finite-width implementation, reversible
history, physical coefficient service, storage/tape bill, compiler admission,
native supplier or complete multiplication theorem. All five selected
framework assumptions remain. Independent human and formal proof-kernel
review are unclaimed. Lean, Docker and the selected scientific cold replay
are unrun. Executable bounds and the allocation deviation are recorded in
[CODE-BOUNDS.md](CODE-BOUNDS.md).

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19572871)
preceded the new calculation. Live open/account PRs, recent handoffs, local
reservations, complete cached open/closed source-reference checks, all-main
README searches and merged keyword searches were checked. Those searches
do not cover unpublished work or arbitrary historical diffs.

## Open next questions

- Which other rational coefficients have a sharp error law when the shear
  is rounded internally? Fix one coefficient and first derive its valid
  even-translation period. The general parity and attainment arguments are
  absent. No further coefficient is claimed here.
- Does an actual selected `precision_tape` caller contain this exact tile?
  Extract one complete trace and match its grids, rounding sites and
  comparator. Range, coefficient service, reversal, storage and the full
  caller bill remain blockers to any precision change.

## Credit

Josie Elliston / JosieElliston #6140 supplies the interleaved-gate question.
Jerry Chen / CubeJerry #6146 supplies the integer-shear model, parity context
and its explicitly excluded coefficient domain. Nick Petalas #6129 supplies
the pure-stage background; its theorem is not used as the new proof step.
The deferred-row context belongs to Vlado Vojdanovski #1673, and the distinct
shear-equivariance context to Sricharan Vagvala #1631, retaining the native,
BIT and analytic lineage credited by those sources. Douglas Colkitt's package
scaffold and the repository publication checks are reused without edits.
The new half-shear theorem, attaining inputs and checkers were produced by
Nick Petalas. Predecessor files and credit lines are unchanged.
