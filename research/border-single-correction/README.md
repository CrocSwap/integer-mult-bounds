# Two repair cuts are necessary for the fixed five-call border

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped algebraic proof with exact finite evidence.**
Ali Romman's [PR6398 five-call border](https://github.com/aliromman/integer-mult-bounds/blob/dee2663ba0918be86993fd9d63c8d64b020f4c83/research/mixed-projector-root-headroom/BOUNDARY-MODULES.md)
cannot reach its exact diagonal target through a central-only linear repair
confined to any single cut. This excludes an arbitrary-rank operation or an
arbitrarily long block of such operations at that cut. The minimum number
of distinct repair locations is **two**, attained by the predecessor's
two rank-one corrections.

For each of the six cuts, invertibility uniquely determines the inserted
repair matrix. The required matrices differ between the two middle stages
`B=1` and `B=-1`, already at `A=C=1` and central character `S=-1`.
The repair cannot be independent of the stages. An exact diagonal similarity
extends the argument to every nonzero border parameter, over any field of
characteristic other than two. [PROOF.md](PROOF.md) gives the six required
matrices and the complete argument.

This answers a part of PR6398's different-recovery question. Increasing the
rank or scalar complexity of a repair at one location cannot remove its
need for stage information. A future recovery must cross a stage boundary,
use stage-dependent operations, change the word or change another stated
hypothesis. The predecessor's native construction, two-correction word
and reported losing invoice retain their credit; they are premises rather
than audit deliverables.

## Reproduce

From the repository root, using only CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/border-single-correction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/border-single-correction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/border-single-correction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/border-single-correction --check-source-history
```

Other hosts may substitute a CPython 3.12 interpreter. The verifier prints
`PASS_BORDER_SINGLE_CORRECTION` in a generated JSON receipt, including all
36 cut/parameter witnesses, 36 normalized table checks, 48 two-correction
positive fixtures and five domain/singularity controls. Every frozen
one-cut correction is explicitly rejected on the other middle stage.
All checks remain active under `-O`. The receipt binds package files by
SHA256 and is printed to stdout; redirect it outside the checkout to save it.

The package imports no predecessor solver and does not rerun a predecessor
scientific suite. The source is cited at the exact public head above.
Its definition is transcribed explicitly into the proof and standalone
verifier. It is an external scholarly reference, not an unresolvable Git
input pin. The declared Git provenance binds the base card and selected record.

## Scope and limitations

The theorem concerns a formal identity in three independent invertible
commuting stage variables and a central involution. The negative-character
specialization is essential; a concrete central operator equal to identity
is outside the obstruction. There are exactly four arbitrary input fields,
the original five factors stay fixed, and the repair location is fixed
independently of the stage values. Repairs may depend arbitrarily on the
central operator and nonzero border parameter, but not on the stages.

Retuned original factors, adaptive cut selection, additional workspace,
stage-sensitive recovery, approximate endpoints and physical implementations
are excluded. This does not lower or rederive the predecessor's invoice,
fund recursive precision, admit a supplier, change selected kappa or prove
a complete multiplication theorem. No Lean, Docker, selected cold replay,
native replay or predecessor root search was run. Independent human and
formal proof-kernel review are unclaimed.

Canonical main was checked at `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8. The selected source-binding positive control passed;
it is metadata orientation, not supplier validation. The original
coverage-law-change card is narrowed to an exact recovery-location obstruction
for a changed caller boundary. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360652)
records that scope before the proof was packaged.

Credit Ali Romman for PR6398's border and recovery question, its two-correction
upper bound and source-specific pricing. Credit Cinna Davis for the caller
interfaces, Jacob Alan Sussman for productive recursion, and the retained
native, helper, compiler, BIT and analytic lineage identified in PR6398.
The new uniqueness table and single-cut obstruction are the contribution here.
All predecessor notices and credit remain unchanged by citation.

Power-of-ten inspection: the verifier uses no recursion, matrices have four
rows, words have at most seven factors, and every scientific loop ranges
over a fixed finite set. Functions stay below 60 lines. Exact fractions and
collections allocate dynamically, a managed-runtime deviation bounded by
these fixed domains. Five rejection-control callbacks have explicit local
targets. Matrix dimensions are internal invariants; zero parameters, invalid
cuts and singular inversion fail explicitly. Warning-strict normal and
optimized commands are registered. No output files or processes are created.

## Open next questions

- Can a changed two-cut recovery cost less than the existing two rank-one
  queries? Start with explicit central operations on both sides of the
  middle stage and a full signed invoice. The present result supplies a
  location lower bound, not a complete tariff optimum.
- Can a stage-sensitive operation or changed original factor yield a
  favorable exact caller? Start from the required correction table and price
  the missing middle-stage dependence, including inverse access and cleanup.
  Physical stage delivery and complete recursive costs remain the blockers.
