# Census: the emitted after-cover does not make ordinary equal C

## Claim type

This is an exhaustive finite census of one source field, plus the exact rational
identity for the selected ordinary formula on that field. It is not a heuristic
search, not an unrestricted nonexistence theorem, and not an admission verdict.

## Hypotheses

The selected conditional exponent stays **781451/250000000**. Nothing here
changes `certificates/selected-result.json`.

1. **Formula.** In `research/p104-helper470-twin-rung-removal/pricing.py` the
   ordinary value is the single assignment

        ordinary = (1 - atom) * Q(bit["after_cover"]) + atom * Q(".0000384599")

   where `bit` is `ordinary_BIT` from
   `research/query-thinned-controllers/RESULT.json` and
   `atom = Q(bit["atom"])`. The same file sets `admitted = Q(bit["admitted"])`
   and passes `bit_saving = admitted`. It never reads `ordinary_saving`.

2. **Stock contract.** `research/query-thinned-controllers/PROOF.md` says to
   keep one external cover weight, with `C0 = 0.003459` before covering and
   `C1 = 0.00345` afterward. The controller verifier assigns that weight once:

        before, after, atom, old = Q(".003459"), Q(".00345"), Q(".004"), Q(".0000384599")

   and stores `after` as `after_cover`. The physical BIT word and
   `controller.py` do not carry a second cover field.

3. **Recorded component.** `C` is the top-level `admitted` value of
   `research/g20-helper-split/ORDINARY-RESULT.json`,

        C = 3507410738409/1000000000000000,

   equal to that receipt's fifth finite level. The receipt has
   `whole_kappa = null`. It is a component saving, not a selected exponent.

A source-bound after-cover, under this contract, is a value of the single
`ordinary_BIT.after_cover` field those bytes emit. A rational that does not
appear there is not a source-bound cover for this formula, even if some other
package records a different `C1`.

## Census

After the SHA256 and Git blob pins match, the receipt text contains the key
`after_cover` once, spelled `69/20000`, at `ordinary_BIT.after_cover`. The
controller verifier contains one writer of that key and one assignment of
`after`. The proof contains one `C1 = 0.00345` sentence. The physical word has
no `after_cover` key and neither cover literal. Therefore the emitted set is

    { 69/20000 }.

`Q(".00345")` equals that fraction, and `Q(".003459")` equals the separate
before-cover field `3459/1000000`. The before-cover is the claim template
named "BIT before cover". It is not the field the ordinary formula reads.

The domain is finite because it is one parsed field written by one literal.
The enumeration is complete because every pinned writer, stored key, and
physical-word key was counted, and a second key, including a duplicate JSON
key that a parser would collapse, is rejected by the text count. The controller
program was not executed. The stored field and the writer literal were
compared, and they are the same rational. A disagreement would have failed
the census.

## Arithmetic

The pins give `atom = 1/250` and `epsilon = 384599/10000000000`. The slope

    1 - atom = 249/250

is positive, so the formula is injective in the cover. The emitted value
reproduces the selected claim:

    ordinary(69/20000) = 8590884599/2500000000000.

The unique rational preimage of `C` is

    (C - atom * epsilon) / (1 - atom) = 3507256898809/996000000000000.

That preimage is not `69/20000`. The same identity gives

    C - ordinary(69/20000) = 71056898809/1000000000000000 > 0.

So the only emitted after-cover does not make the formula equal `C`, and there
is no other emitted after-cover that could. The preimage numerator does not
occur as a constant in the pinned controller, pricing, claim, or component
files. This package does not write it into the controller.

## What is outside the census

The following rationals are recorded somewhere, and each fails the formula
when substituted, but none of them is an emitted after-cover. They are
controls, not extra census elements.

- The before-cover `3459/1000000`.
- PR5679's own cover `C1 = uniform - 1/10^14 = 350741073841/100000000000000`,
  from `ordinary.py`, where the component formula is
  `(1 - rho) * C1 + rho * backend` with `rho = 1/100`. That is not the
  selected formula.
- PR5708's receipt cover and the different preimage
  `3507565220149/996000000000000` of its larger component. The odd-prime
  question asked for that other preimage is not this census.

The delayed-cover bridge's group fibers are not values of this scalar field
and are not read by the formula.

## What this does not say

`ordinary(69/20000) ≠ C` is the statement that the emitted cover is not the
preimage. It is not a new proof that `C` fails admission. The pricing still
feeds `bit_saving = admitted = 17/5000` to the ledger. This note does not
execute that ledger, does not replace `admitted` by `C` or by `ordinary`, and
does not move κ.

A cover the controller does not emit remains a changed stock contract. The
odd-prime comparison at `3507256898809/996000000000000` was not run. A
Gaussian caller outside this pricing assembly was not named or executed.
