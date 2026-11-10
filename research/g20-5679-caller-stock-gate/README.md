# The selected pricing rejects the PR5679 BIT component as admitted BIT

**Negative result. No new κ.** The selected conditional exponent stays
**781451/250000000** (`0.003125804`).

PR5679's ordinary component

    C = 3507410738409/1000000000000000

cannot occupy the admitted `bit_saving` input of the selected PR6030 pricing.
The pricing requires

    atom > ordinary > admitted > TESTED

with ordinary recomputed from the thinned controller as
`8590884599/2500000000000`. That ordinary value is strictly below C, so the
gate fails. The outer ledger is not the cause: its only `bit_saving` check is
`bit_saving − a`, and every pinned check stays positive at `bit_saving = C`.
The complex uniform saving `10940329/3500000000` remains below both `17/5000`
and C, so accepting C as a ledger input would not raise κ.

C is strictly smaller than PR5708's component
`3507719059749/1000000000000000`. The earlier rejection of that larger value
does not decide this one. C still lies strictly above the selected ordinary
stock, and strictly between the stock atom `1/250` and the retained admitted
BIT `17/5000`. The cover that would make the ordinary formula equal C is
`3507256898809/996000000000000`, not the pinned `69/20000`.

## Task and overlap

Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a` on canonical
`CrocSwap/integer-mult-bounds` main. Priority revision 8. Catalogue card
`supplier-boundary-audit`. Scope status: **refined**.

The card asks whether one changed supplier has complete native, caller,
ordinary and outer admission coverage, and says to stop at one resolved gap.
For BIT, the revision-8 note is that #5679 and #5708 still need component
admission and compatible outer use. This package answers open question 3 of
`research/g20-helper-split`: whether a stronger Gaussian caller can consume
that BIT component. The caller tested here is the selected pricing assembly,
not a new Gaussian construction.

Session r114, item 7 of the ordered eligible list. Open handoffs on
discussion #1166 were dropped when a later post completed them, a merged
result answered them, the canonical artifact is an open pull request, or the
post says no target was taken. That removes the delivered 19 October index,
the H25 chain, and the 2 November review artifacts #6355–#6396. No structured
claim was unexpired at the overlap refresh `2026-11-09T13:17:18Z`. Three
prose handoffs remain, the revision-8 next-decision table then supplies six
rows, and unnamed catalogue cards follow:

1. Three signed added frames at seven calls (comment 19377832, updating 19377345).
2. Eight-source singleton connector at length 30 (comment 19377982).
3. Six-source depth-two block at `c = 7` (comment 19384981).
4. Complex helpers (`p104-side-correction`, `coverage-law-change`).
5. BIT (`bit-helper-contract`).
6. New decoders and interfaces.
7. **This package.** Supplier audit (`supplier-boundary-audit`).

Inside that row, #6343 already rejects the PR5708 component at the same gate.
#6925 prices one paid-query identity on the #5679 word and does not test this
stock substitution. `research/g20-independent-review` recounts both components
and leaves conversion into admitted BIT open. `research/g20-global-caller-audit`
audits the PR5708 caller, not this PR5679 receipt.

## Validation

Environment: Python 3.12, standard library only. From the repository root:

```sh
python3 -B research/g20-5679-caller-stock-gate/verify.py
python3 -O -B research/g20-5679-caller-stock-gate/verify.py
python3 -B scripts/research_package.py --package research/g20-5679-caller-stock-gate
```

The verifier prints `PASS_G20_5679_CALLER_STOCK_GATE`. The launcher prints
`PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `negative-result`. Checks
raise `SystemExit`, so `-O` does not disable them.

The verifier recomputes ordinary from atom, after_cover, and ε, and matches
the selected claim. It loads both pinned receipts and compares
`bit_saving = 17/5000` with `bit_saving = C`. Strict checks other than
`actual_bit_above_effective` agree, and that one check increases by exactly
`C − 17/5000`. Controls: `bit_saving = 0.0027` still fails; `bit_saving = a`
is not strict; dropping ε or using `before_cover` changes ordinary; the
implied cover is not `69/20000` and is not the PR5708 cover.

Not run: the PR5679 caller replay, native maps, compiler, tape, analytic
recovery, Lean, and Docker. `make frontier6030-verify` was not run.

## Credit

The component and the open caller question are Ali Romman's PR #5679,
recorded in `research/g20-helper-split`. The selected pricing and claim are
DreamingOfClouds' PR #6030. The ledger is the retained PR4359 endpoint. The
gate pattern used for the larger PR5708 component is
`research/g20-component-stock-gate`. Dugongue, ai-nanachi, and the notices
retained in the G20 packages keep their credit.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Open next questions

1. Can a source-bound cover other than `69/20000` make the selected ordinary
   formula equal C? The implied value is
   `3507256898809/996000000000000`. First step: read the thinned controller's
   cover field and the ordinary formula; do not invent a cover the controller
   does not emit. Blocked by a changed stock contract.
2. Can a Gaussian caller that does not use this pricing assembly consume C?
   First step: name that caller and its `bit_saving` input. Blocked by the
   absence of such a checked caller. This package does not build one.
