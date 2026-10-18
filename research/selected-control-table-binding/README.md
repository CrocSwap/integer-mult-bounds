# Actual selected BIT matrices bind to the compiled control tables

This package joins PR2234's actual full-ring producer to PR2310's iterative
control evaluator. The adapter checks the selected request, exact frozen
field specification and actual low-class child before constructing a table.
It retains original global slots after unit resets and the fallback child's
physical atom reversal. Neither predecessor implementation is changed.

[PROOF.md](PROOF.md) proves the structural binding for every admitted finite
chain under the stated producer normal-form hypotheses. It also shows why
numerical high fields before the last reset need not be prepared. This takes
the preparation/evaluator handoff; the claim is in
[Discussion #2304](https://github.com/CrocSwap/integer-mult-bounds/discussions/2304#discussioncomment-18941098).
It does not establish the complete payload dispatcher or a new exponent.

The final overlap check found Jose Manuel's concurrent
[Discussion #2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319)
claim for joined preparation and completed-child dispatch in a generic
two-dimensional caller. This package supplies a separate, scoped coefficient
binding audit on actual selected 64-dimensional requests. It does not claim
priority for the broader joined-execution handoff or duplicate that payload work.

## Evidence and reproduction

The source-bound replay covers 12 actual selected request representatives,
all paid ranks 1–7 and 42, and MOVE/COPY/IDLE requests. It passes 87 fixtures,
801 generated-weight comparisons and 12,642 independent local equalities.
The matrix oracle constructs the raw-label projector independently of the
producer's split basis and uses normalized elimination. Catalogue decoding
and incoming parent descriptors are explicitly reused and credited.

Thirteen semantic controls include concrete counterexamples to low-only
coefficients (2 instead of 8), discarded row permutation (1 instead of 8)
and omitted atom reversal (8 instead of 2), all modulo 9. Other controls cover
source identity, legal child selection, reset slots and inaccessible stock.
The fixtures include mixed paths over Z/9, Z/25 and Z/27 and a width-one root.
They do not enumerate all matrices or execute large payloads.

With Python 3.12 and the standard library, from the repository root:

```sh
python3 scripts/research_package.py --package research/selected-control-table-binding
```

The hook runs normal and optimized replays plus artifact-integrity tests.
The direct command `python3 -I -B research/selected-control-table-binding/verify.py`
prints `PASS_SELECTED_CONTROL_TABLE_BINDING fixtures=87 coordinate_equalities=801 independent_equalities=12642 controls=13`.
`--emit` prints the full deterministic [receipt](RESULT.json) without writing
files. Exact base, dependency heads, source hashes and scope are in
[SOURCES.json](SOURCES.json) and [TASK.json](TASK.json).

## Open next questions

Coordinate with the active #2319 dispatch investigation to connect this bound evaluator to one complete stream coefficient-preparation
site, including high-header spectators, inverse cleanup and local work
lifetime. This would join semantic values to the pending physical-charge
argument; the complete payload dispatcher remains the blocker. A separate
formalization can prove the reset/extent induction on the explicit grammar.
[TASK.json](TASK.json) gives concrete first steps for both.

## Credit and limits

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Jose Manuel (@jmbarrancoml) supplied both pending principal predecessors;
the retained notices credit source527, Ross Richardson, this account's
PR2160/2188, and the selected supplier lineage. See [NOTICE.md](NOTICE.md).
This is an author-checked scoped proof and finite certificate. No independent
human review, Lean proof, complete physical supplier, cold replay or kappa
change is claimed.
