# Shorten the concrete nonunit P104 helper handoff

A unit **column** pivot and one support-cancelling shear complete #6297's
nonunit row using six source ADDs and five cut ADDs. Including both inverse
boundaries, the complete handoff needs 22 inserted events and scalar allowance
280, versus 140 and 1136 for the published Euclidean schedule. The savings are
118 scalar events and 856 allowance units.
The same rank 9 → rank 5 + rank 4 helper split, arbitrary dirty-input identity, paid
histogram and eight owned lifetimes are retained. **No new κ.**

This source-specific constructive improvement includes an independent exact
whole-word audit. The elementary shear identity is classical. A support-activation proof makes
the six-/five-ADD counts optimal among ADD + nonzero SCALE completions of these
dual pairs, even with extra roles absent from the pair. Thus 22 is optimal for
the four separately completed boundary maps. No whole-word or scalar-allowance
optimum or literature priority is claimed. The new completion may differ from
the predecessor on its unconstrained complement. It satisfies the same two
boundary equations, and complete local replay verifies the resulting handoff.

| Complete local word | Events | Real scalar allowance | Public inputs |
|---|---:|---:|---:|
| Original #5580 input |25140|217428|735|
| #6297 Euclidean handoff |25280|218564|736|
| Gate-minimum unit-column handoff |25162|217708|736|
| Lower-allowance alternative |25166|217700|736|

A second, two-half-shear completion uses **26 inserted ADDs and allowance 272**,
trading four extra events for eight fewer allowance units. Its source/cut
schedules cost 72/64 and retain the same complete endpoint and inventories.
[ALTERNATIVE-PROOF.md](ALTERNATIVE-PROOF.md) gives the exact construction and
full replay. These two schedules are a tradeoff, not a claimed complete Pareto
frontier or allowance optimum.

The source is canonical base `2485805a6d47f36ea83ddde6327d453ac82d44dc`.
`SOURCES.json` pins four live base inputs and historical catalogue/selection
provenance. `PREDECESSOR.json` binds two verbatim #6297 source snapshots to head
`2fbb316a7bd34fabebed8e47ed40017c150d71b8`. Pending Git history is not needed
for replay. The shared shallow checkout cannot establish a complete-history
preflight; original blob/byte authentication, committed files/modes and portable
export checks are recorded separately and are not called an ancestry proof.

## Reproduce

From the repository root, CPython 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/p104-unit-column-handoff
```

Expected: `PASS_P104_UNIT_COLUMN_HANDOFF`, `PASS_P104_ALLOWANCE_ALTERNATIVE`
and `PASS_REGISTERED_RESEARCH_PACKAGE`.
The registered normal and optimized commands authenticate all source inputs,
reconstruct both concrete completions, replay the original and both handoff
words, run 160 generic dyadic fixtures, 120 preconditioned fixtures and 2,500 local
support-transition cases and meaningful rejection controls, and
invoke the independent full-word checker. The alternative commands additionally
reconstruct the 26-ADD schedule, reject all 26 inserted-event omissions plus
chart/growth faults, and run 10 semantic controls through the independently
implemented replay with its fixture inventory explicitly adapted. `RESULT.json`
and `ALTERNATIVE.json` are deterministic exact receipts. Default replay is
read-only; `verify.py --write` explicitly regenerates the main receipt and
`alternative.py --write` regenerates the alternative receipt. The command
`verify.py --emit-word /absolute/external/path.json` exports the constructed
candidate for a separate checker without committing a duplicate large word.

See [PROOF.md](PROOF.md) for the general column-unit lemma, complete tariff,
actual inserted programs and dirty-handoff proof. See
[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) for the separate integer-dyadic
whole-word method. [VALIDATION.md](VALIDATION.md) distinguishes actual completed
checks from unrun supplier obligations.

## Scope and predecessor relationship

This answers the concrete schedule-shortening opportunity in #6297 under the
same dual-pair boundary specification. Unlike an exact-matrix refactor, the
complement action is allowed to change, and the entire consumer is rechecked.
The selected `p104-side-correction` card is explicitly narrowed to a scalar
boundary module; its full supplier gate is not claimed. Three candidate methods
were considered: column-pivot triangular completion, inverse-transpose use of
the row-pivot constructor, and pivot-reordered Euclidean elimination. The first
produces the concrete gain; lead review then cancels one equal/opposite support
pair with a single shear. No wider optimization search is claimed.
Track seed 32 records assignment only; all finite fixtures are deterministic.
Stop after the gate-minimum schedule and the approved same-pair allowance
alternative receive independent complete audits. No further weighted search is
part of this package.

#5611 supplies the general dyadic Euclidean compiler and #5602 the coupled
handoff specification and tariff. #6280 supplies a separate spare-role exchange;
that spare contract is not required here because the actual column pivot is a
unit. Its circuits are not imported or compared numerically. The added program
uses only the original support roles. The target histogram and paid recursive
invoice are identical to #6297, so no exponent improvement follows from this
scalar saving. Native maps, complete physical caller, stock/precision/tape,
compiler closure and outer predicates remain unrun or inherited. The five
selected framework assumptions and selected frontier are unchanged. No hosted
CI, independent human acceptance or proof-kernel verification is claimed.

## Open next questions

1. Can the same column-pivot rule reduce a different current helper handoff's
complete boundary allowance? First identify its exact dual pair and chart
availability, then compare the full emitted word; this instance's old helper
boundary must not be assumed to survive in a newer word.
2. Can the scalar allowance fall below 280 while retaining the six-/five-ADD
minimum, or below 272 when extra ADDs are permitted? First compare exact
coefficient tariffs among alternative completions
of the same dual pairs. The support lower bound counts ADDs, not their weighted
allowance. Interleaving the boundary modules is a separate, unproved possibility.
3. Can the original #6297 target split be admitted as a complete supplier with
all native, caller, compiler and outer costs? Start with its exact historical
source and full obligation ledger. This scalar saving alone does not perform
that admission or improve a selected κ.

Structured questions, bounded overlap coverage and local claim status are in
`TASK.json`. Discussion posting was unavailable, so the claim is local-only.

## Credit

Prepared for @CubeJerry with substantial OpenAI Codex assistance: worker A's
construction and primary replay, the lead's support-cancelling and two-half-shear
refinements, and
worker D's separate symbolic/chronological verification. Apache-2.0. Credit unpaidmoon and its disclosed
Cursor Grok assistance for #6297; Ali Romman for #5611/#5602 and the retained
#5599 lineage; David Arias, Cinna Davis and Gareth Davidson for the literal word
and ownership construction; Nick Petalas for the related #6280 discussion.
Source snapshots retain their original notices. Independent here means separate
implementations and derivations, not independent human or formal acceptance.
