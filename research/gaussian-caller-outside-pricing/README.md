# The caller outside the selected pricing assembly does not consume C

**Negative result for one named caller. No new κ.** The selected conditional
exponent stays **781451/250000000**.

The recorded PR5679 component is

    C = 3507410738409/1000000000000000

from `research/g20-helper-split/ORDINARY-RESULT.json`, with `whole_kappa`
null. The selected PR6030 pricing assembly assigns its own `bit_saving`
entry from the thinned controller's admitted BIT. This package does not
reopen that assignment or the cover inside it.

The caller outside that assembly is `physical` in
`research/p104-productive-controller/caller.py`. The selected verifier loads
that module and calls `C.physical(caller, word)` before `pricing.run`. The
function's parameters are `word` and `local`. It checks the Gaussian pair
and the idle Gaussian axes, and it has no `bit_saving` parameter. The
selected call is `physical(caller, word)`. Its first argument is the
controller returned by `construct`, equal to `CONTROLLER.json`, which has
no `bit_saving` field. Its second argument is the regenerated edited word,
not the replay dictionary and not C. This caller does not consume C.

At the same base commit, the tree contains exactly 15 files named
`caller.py`. None of those blobs contains `bit_saving`. That is a census of
one filename, not a proof that no other function can accept C.

## Task and overlap

Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a` on canonical
`CrocSwap/integer-mult-bounds` main. Priority revision 8. Catalogue card
`supplier-boundary-audit`. Scope status: **refined**.

The card asks whether one changed supplier has complete native, caller,
ordinary and outer admission coverage, and says to stop at one resolved
gap. The candidate is the PR5679 component. The gap taken here is the
caller the selected verifier loads before the pricing assembly. The stock
gate inside that assembly, and any other cover for its ordinary formula,
stay outside this package.

Session r137. The question is open question 2 of the r114 note on
discussion #1166, comment 19492491, recorded in fork PR 149. Overlap at
`2026-11-10T02:08:04Z` searched 885 open PR bodies and 6,934 discussion
records, plus the local notes at `7c49fe32`. No open PR states this
caller's parameter list. Neighbouring notes use the same caller file for
an income bound, or they leave a stronger Gaussian caller unnamed. No
matches is not proof that a hidden diff is absent.

The family-status expansion gate was not opened. This package does not
extend a construction.

## Validation

Environment: Python 3.12, standard library, and local Git for the pinned
tree listing. From the repository root:

```sh
python3 -B research/gaussian-caller-outside-pricing/verify.py
python3 -O -B research/gaussian-caller-outside-pricing/verify.py
python3 -B scripts/research_package.py --package research/gaussian-caller-outside-pricing
```

The verifier prints `PASS_GAUSSIAN_CALLER_OUTSIDE_PRICING`. The launcher
prints `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `negative-result`.
Checks raise `SystemExit`, so `-O` does not disable them.

The verifier parses `physical`, checks that the selected call site orders
`C.physical` before `pricing.run`, and compares the 15 `caller.py` blobs at
the base commit. Controls: an in-memory parameter named `bit_saving` is
detected, and a reversed call order is rejected.

Not run: `physical`, the PR5679 caller replay, the pricing assembly, the
outer ledger, native maps, compiler, tape, analytic recovery,
`make frontier6030-verify`, Lean, and Docker. Unknown costs are not treated
as zero.

## Credit

The caller and the selected verifier are DreamingOfClouds' PR #6030 chain,
with the productive controller caller from the retained P104 lineage. The
component C is Ali Romman's PR #5679, recorded in `research/g20-helper-split`.
The assembly rejection of C inside the selected pricing is the r114 note,
not a result of this package. Dugongue, ai-nanachi, and the notices retained
in those packages keep their credit.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Open next questions

1. Can a function that is not one of these 15 `caller.py` files, and is not
   `pricing.run`, accept C as a parameter named `bit_saving` while checking
   a Gaussian pair or idle Gaussian axis? First step: name that function
   from a file whose final component is not `caller.py` and whose path is
   not `research/p104-helper470-twin-rung-removal/pricing.py`, then execute
   it at C. Blocked by the absence of such a checked function. This census
   does not search other filenames, and it does not execute the ledger.
