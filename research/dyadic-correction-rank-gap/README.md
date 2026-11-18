# Dyadic completion can require more correction rank

The exact field minimum in [PR #7654](https://github.com/CrocSwap/integer-mult-bounds/pull/7654)
need not be attainable with a dyadic inverse. This package classifies
rank(P-I) for every normalized two-role dyadic row/column contract.
For m prescribed pairs, the contract P*e_i=4e_i+f_i and
f_i^T*P=e_i^T has minimum **m over Q and 2m over Z[1/2]**.
The lower bound permits arbitrary coupling with any extra coordinates.
At m=1 the field-minimum matrix has integer entries but determinant 3.
A three-ADD word per pair attains the dyadic minimum with determinant one.

This is a scoped proof with exact finite corroboration. Read
[PROOF.md](PROOF.md), [verify.py](verify.py) and [RESULT.json](RESULT.json).
The complete two-role test depends on whether the single required
determinant is a dyadic unit; no bounded exponent search is used.
No new kappa, physical supplier or selected-assumption discharge is claimed.

## Evidence and reproduction

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -I -W error -B research/dyadic-correction-rank-gap/verify.py
python3.12 -I -W error -B -O research/dyadic-correction-rank-gap/verify.py
python3.12 -B scripts/research_package.py --package research/dyadic-correction-rank-gap
python3.12 -B scripts/check_research_commit.py --package research/dyadic-correction-rank-gap --check-source-history --check-modes
```

Expected markers are PASS_DYADIC_CORRECTION_RANK_GAP,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES.
The checks cover 6561 literal grid matrices, including 2480 dyadic
invertible matrices, all 308 normalized integer pairs in [-5,5]^4,
and 928 distinct contracts. The constructed completions attain every
classified minimum. There are 336 strict-gap contracts in this finite
union. The word and inverse pass exact matrix checks on 16 (pair-count,
extra-coordinate) shapes. All 11330 admissible matrices in four small
modular domains satisfy the rank floor, including coupled free blocks.
Six controls reject invalid completions or contracts.

The written proof is uniform in the allowed dyadic coefficients, and
the separating family permits any number of pairs and extra coordinates. No
predecessor scientific replay, selected cold replay, Lean or Docker
run is required or claimed. Independent human and formal-kernel review
remain open. There are no external run-time inputs.

## Current task and prior coverage

Canonical main is `e54523517d0f03e58352e647c403a5af3e525a57`, with priority
revision 8 and selected PR #7000 unchanged. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19702329)
takes the released PR #7654 dyadic-attainment handoff. The current
baseline metadata check passed. The PR/Discussion overlap cache includes
both open and closed bodies; sparse local notes and unpublished work
remain coverage limits.

[PR #6016](https://github.com/CrocSwap/integer-mult-bounds/pull/6016)
already gives the completion parameterization and optimizes conditioning.
The present result optimizes correction rank. PR #5904 concerns eligible
observation acquisition, and PR #6027 concerns common invariant lattices.
The new arithmetic obstruction does not replace any of those results.
[SOURCES.json](SOURCES.json) pins the task and selected record. The exact
context sources below are citations, not external executable dependencies.

## Open next questions

Which higher-dimensional paired contracts attain the field minimum over
Z[1/2]? Start with the sums of the prescribed and fixed modules; the
example shows that individually saturated modules can have a sum with
odd index. This question matters before an optimizer treats field rank
as a legal dyadic completion budget. A full criterion and an actual
source cut remain missing. The [task record](TASK.json) gives the first
step and blockers. Physical implementation, range/precision bounds and
the complete caller invoice remain separate obligations.

## Credit and exact sources

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Nick Petalas supplied the field formula and dyadic question in
[PR #7654's proof](https://github.com/petalas/integer-mult-bounds/blob/0438595fadc4902fa20cb88aecc305b526193a99/research/primal-dual-completion-rank/PROOF.md)
and the known two-role parameterization in
[PR #6016's proof](https://github.com/petalas/integer-mult-bounds/blob/d2df1a6e3caf20c47fff89e6064f3747016fb954/research/dyadic-basis-conditioning/PROOF.md).
Ali Romman's [PR #5611 proof](https://github.com/aliromman/integer-mult-bounds/blob/c132f93acaee6dd8d5ee5006da0670dfef3e9362/research/dyadic-helper-basis-completion/PROOF.md)
supplies the dyadic helper interface. Dugongue posed GQ08 in
[PR #5803](https://github.com/CrocSwap/integer-mult-bounds/pull/5803).
No predecessor code was copied. New work is Apache-2.0.
