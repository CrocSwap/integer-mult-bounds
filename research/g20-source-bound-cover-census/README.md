# The emitted after-cover does not make ordinary equal C

**Exhaustive finite census. No new κ.** The selected conditional exponent stays
**781451/250000000** (`0.003125804`).

The selected ordinary formula reads one thinned-controller field,
`ordinary_BIT.after_cover`. Under the controller's one-weight stock contract
that field is only

    69/20000.

The formula is strictly increasing in the cover. The unique cover that would
make it equal the recorded PR5679 component

    C = 3507410738409/1000000000000000

is

    3507256898809/996000000000000.

That rational is not emitted. The ordinary value at the emitted cover remains
the selected claim `8590884599/2500000000000`, and

    C - ordinary(69/20000) = 71056898809/1000000000000000 > 0.

This identifies the preimage. It does not admit `C` as BIT and it does not
change κ. The pricing passes `bit_saving = admitted = 17/5000`, not `ordinary`.

## Scope

Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a` on canonical
`CrocSwap/integer-mult-bounds` main. Priority revision 8. The live selected
record, not the older κ quoted in `current-priorities.md`, supplies the
exponent above. Catalogue card `supplier-boundary-audit`. Scope status:
**refined**.

The card asks for one resolved gap on a latest supplier candidate. The gap
taken here is the cover field left open by the PR5679 stock-gate reading:
read the thinned controller's cover before constructing one, then ask whether
any emitted cover other than `69/20000` makes the selected formula equal `C`.
The argument is in [PROOF.md](PROOF.md).

Overlap recheck on 2026-11-10, after fetching canonical main at the base
commit: 885 open upstream PR bodies and the discussion cache. The preimage
numerator occurs in discussion
[#1166 comment 19492491](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19492491)
as an open question, and in no open upstream PR body. That comment's fork
draft, PR 149, stops at the stock gate and does not census the cover field.
`research/g20-component-stock-gate` asks the odd-prime question for the
different PR5708 preimage `3507565220149/996000000000000`. No match is a
novelty certificate. This package does not take the caller question and does
not answer the odd-prime question.

## Validation

Environment: Python 3.12, standard library only. From the repository root:

```sh
python3 -B research/g20-source-bound-cover-census/verify.py
python3 -O -B research/g20-source-bound-cover-census/verify.py
python3 -B scripts/research_package.py --package research/g20-source-bound-cover-census
```

The verifier prints `PASS_G20_SOURCE_BOUND_COVER_CENSUS`. The launcher prints
`PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `negative-result`. Checks
raise `SystemExit`, so `-O` does not disable them.

Source hashes and Git blobs are checked before any scientific `Fraction`
evaluation. The census counts the raw `after_cover` key, including a duplicate
key a JSON parser would collapse. Controls reject an unbound call, a second
nested key, and that duplicate key. The before-cover, PR5679's own `C1`, and
PR5708's cover and preimage are substituted only as values outside the emitted
set; none equals `C` under this formula, and none is added to the census.

Not run: `scripts/research_selected_baseline.py`, the thinned-controller replay
itself, the outer ledger, either component caller, native maps, the odd-prime
rule at the missing preimage, Lean, Docker, and `make frontier6030-verify`.
The cover is the source literal `Q('.00345')`, checked against the pinned
receipt; it is not a value discovered by replaying the physical word.

## Credit

The component is Ali Romman's PR #5679, recorded in `research/g20-helper-split`.
The selected pricing and claim are DreamingOfClouds' PR #6030. The one-weight
cover contract is Cinna Davis's `research/query-thinned-controllers`. The
PR5708 preimage question remains with `research/g20-component-stock-gate`.
The stock-gate reading that left this cover field open is the predecessor
package behind discussion comment 19492491.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Open next questions

1. Can a changed thinned-controller contract that emits a second after-cover
   make this formula equal `C` while keeping the one-weight delayed-cover
   proof? The missing value is `3507256898809/996000000000000`. First step:
   name a second source assignment to `after_cover` and authenticate it before
   any arithmetic. Blocked by the single `C1` sentence and the single writer.
   The odd-prime rule at that missing value was not run.
2. Can a Gaussian caller that does not use this pricing assembly consume `C`?
   First step: name that caller and the field it reads as `bit_saving`.
   Blocked here because no such caller is identified. This package does not
   take that question. Equality of `ordinary` with `C` would still leave this
   assembly's `bit_saving` equal to `17/5000`.
