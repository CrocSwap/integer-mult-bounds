# Approximate dyadic channels cross odd-torsion cuts and restore dirt exactly

For every dyadic cut matrix K and 0 < epsilon < 1, the largest number of
channels satisfying `||X K Y - I||_infinity <= epsilon` is exactly its
rational rank. Odd Smith factors obstruct exact normalization but do not
obstruct this deterministic approximate response contract. A constructive
rounding bound supplies finite dyadic constants.

The response can cancel arbitrary incoming helper dirt exactly:

```text
h += Y x
y += A h
h -= Y x
y -= A h
# endpoint: x unchanged; h restored; y += A Y x
```

For source norm at most B and `||AY-I||_infinity <= epsilon`, the final
increment error is at most epsilon B, independent of the dirty helper.
Four block shears are necessary and sufficient in the stated two-kind
alphabet for a nonzero response independent of initial dirt. Every scalar
coefficient has an explicit lowering to signed unit ADDs and SCALE 2 or
SCALE half; [PROOF.md](PROOF.md) gives its exact event count and guards.

For the fixed scalar reader A=[3], the best coefficient with at most b
fractional bits has error exactly 2^-b at every b>=0. Thus the odd-factor
escape has a sharp precision cost in this model.

Claim type: scoped constructive proof with finite exact corroboration.
This contribution was produced by Nick Petalas. No new kappa is claimed.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/approximate-dyadic-dirty-channels/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/approximate-dyadic-dirty-channels/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/approximate-dyadic-dirty-channels
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/approximate-dyadic-dirty-channels --check-source-history
```

Any CPython 3.12 installation may replace this local interpreter path.
The direct marker is `PASS_APPROXIMATE_DYADIC_DIRTY_CHANNELS`; registered
replay also prints `PASS_REGISTERED_RESEARCH_PACKAGE`. Both registered
commands execute the same complete fixed domain, with warnings as errors
and a 60-second timeout. The checker writes no files. Its generated JSON
receipt binds all package files by SHA256 and records the actual interpreter.

The exact checker covers all 625 two-by-two integer matrices with entries
in [-2,2]: 496 full-rank constructions and 129 rank-deficient rejections.
Six additional dyadic, rectangular and larger cuts extend through four
channels. Literal execution of the elementary gates checks 4,022 complete
basis/dirty vectors, plus 2,510 dirty states including magnitudes 10^60,
against a separate matrix-product endpoint calculation. It enumerates
123,060 integer candidates for 195 odd-scalar precision cases, checks
the factor-three formula at depths zero through 64, and executes 5,425
two-role inputs for 217 coefficient presentations. Nine exact-reason
boundary rejections and four semantic controls remain active under `-O`.
The arbitrary-size claims rely on the written proof, not this finite census.

## Scope and predecessor credit

The exact-capacity background is Ali Romman's
[PR5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615), including
PR5602/5611/5599, Nick Petalas's PR5115 and the retained helper/native/
controller/compiler lineage. Its theorem is cited, not replayed.
[PR1135](https://github.com/CrocSwap/integer-mult-bounds/pull/1135), also by
Ali Romman, already distinguishes exact same-grid additivity from rational
approximation and names grid refinement as an escape, retaining Gareth
Davidson's PR1057 and the PR985/1054 lineage. This construction explicitly
requires exact dyadic execution on a sufficiently refined grid.

Dyadic density, rational inversion, commutator shears and binary coefficient
synthesis are classical. The new step is this approximate-capacity contract
with quantitative normalization, exact dirty restoration and the matching
block-count and scalar-precision bounds. No literature-wide priority for
those classical methods is claimed. No predecessor source is copied or run.

[SOURCES.json](SOURCES.json) pins the cited statements and assignment
provenance at canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8, selected PR6030. The selected source-binding baseline
passed; it is orientation, not a scientific supplier replay. The
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19377705)
records the changed boundary before substantial work.

The `coverage-law-change` card is explicitly changed to this local
approximate-response question. It does not satisfy that card's complete
productive-credit and paid-invoice acceptance gate. Current exact cuts,
tensor pooling and frozen-snapshot capacities are different questions;
none is rechecked or extended here. Live PR/Discussion searches, account
history, batch locks and main-tree README searches supplied bounded overlap
coverage. Sparse local notes and unpublished work remain coverage limits.

The two observations and two deliveries must be legal, correctly charted
and fully charged in a real caller. No actual P104 cut, native implementation,
independent productive targets, paid/target saving, physical speedup,
supplier admission or complete multiplication theorem is supplied.
Rounded gate execution, storage for bounded incoming dirt, stock, tape
movement, compiler closure and complete recovery remain obligations.
The selected frontier and five framework assumptions retain their status.
Selected cold replay, Lean, Docker and physical hosting were not run.

## Implementation limits

The executable constructor accepts full-row-rank dyadic matrices with one
through four rows and at most four columns. Canonical coefficient numerators
and denominators are at most 4096 in absolute value; tolerance is an exact
rational between 2^-32 and 1/2. It searches at most six square minors and
65 candidate precision depths. The chosen depth is at most 47 in this
domain. Cofactor and determinant bounds give inverse magnitude below
2^87, so rounded numerators fit within the compiler's 160-bit limit.
These executable bounds do not restrict the written arbitrary-size theorem.

All loops have finite domains, no code is recursive, and functions stay
under 60 physical lines. Power of Ten rule 3 has a managed-runtime deviation:
Python allocates Fraction objects and lists dynamically. At most a four-by-
eight elimination table, twelve state values and 30,592 elementary events
are live per constructed word; the finite census streams its cases. Rule 9
uses only fixed standard-library operations and direct local calls.
Warning-strict normal and optimized replays supply the available diagnostics;
no repository-wide analyzer configuration is changed.

## Open next questions

The structured questions are in [TASK.json](TASK.json).

1. Can one physical helper cut fund both observations and both deliveries?
   First specify a cut, source norm, chronological accesses, compatible
   charts and every added native/ordinary charge. A favorable complete bill
   and independent productive-target contract are missing.
2. Can an actual fixed-grid backend retain the dirty-independent error bound?
   First fix incoming widths and sufficient fractional bits for the lowered
   gates, then propagate remaining error through the complete consumer.
   The grid, dirty-width contract and recovery budget are missing. Independent
   rounding of cancelling gates is not covered by the exact-dyadic proof.
