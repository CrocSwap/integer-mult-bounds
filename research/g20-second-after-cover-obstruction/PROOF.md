# No second after-cover keeps the one-weight proof and hits C

## Claim type

This is a scoped proof. It is not an exhaustive census of every file that
contains the string `after_cover`, not a heuristic search, and not an
admission verdict. The selected conditional exponent stays
**781451/250000000**. Nothing here changes `certificates/selected-result.json`.

## What was authenticated before arithmetic

Two source assignments were named and hash-bound before any `Fraction`
evaluation.

1. **The controller's only writer.** `research/query-thinned-controllers/verify.py`
   contains one assignment

        before, after, atom, old = Q('.003459'), Q('.00345'), Q('.004'), Q('.0000384599')

   and stores `after` once under the key `after_cover`. The receipt spells
   that field `69/20000`. `controller.py` contains neither the key nor the
   literal. `PROOF.md` contains one sentence, "Keep one external cover weight
   throughout the entire finite BIT compilation," and one C1 sentence,
   "Use C0=0.003459 before covering and C1=0.00345".

2. **The retained bridge's other after-cover weight.** The controller package
   pins `research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md` and
   `research/kappa-rebuild/bit/BIT-ALLSIZE-PARAMETERS.json` as inputs. It does
   not pin the writer script. That script assigns

        before, after = Q(69, 25000), Q(11, 4000)

   and stores the second name as `C1_after_cover`, spelled `11/4000`. The
   bridge prose states `C1=11/4000=0.00275` once. None of those three files
   contains the key `after_cover`. The controller proof does not contain
   `11/4000`.

The selected formula, in `research/p104-helper470-twin-rung-removal/pricing.py`,
is the single assignment

    ordinary = (1 - atom) * Q(bit['after_cover']) + atom * Q('.0000384599')

where `bit` is `ordinary_BIT` from the thinned-controller receipt. The same
file passes `bit_saving = admitted`. It does not read `C1_after_cover`.

The component is the top-level `admitted` value of
`research/g20-helper-split/ORDINARY-RESULT.json`,

    C = 3507410738409/1000000000000000,

with `whole_kappa = null`.

## Hypotheses kept

A changed thinned-controller contract keeps the one-weight delayed-cover proof
only when all four of the following remain true of that contract.

- **(H-one)** There is one external cover weight, the sentence quoted above.
- **(H-writer)** `after_cover` is written once, from the single assignment of
  `after`.
- **(H-C1)** That assignment is the single sentence `C1=0.00345`.
- **(H-gap)** The verifier's gate `before > after` remains, and the proof's
  comparison `256/(C0-C1)` remains a comparison across a positive denominator.
  The recorded coefficient check is `2**26 > 256/(before-after)`.

(H-one) and (H-writer) forbid a second stored `after_cover`. (H-C1) fixes the
one stored value at `69/20000`. (H-gap) is the reason the algebraic preimage
cannot be substituted for that value either.

## Argument

The pinned spellings give `atom = 1/250` and `epsilon = 384599/10000000000`.
The slope `1 - atom = 249/250` is positive, so the formula is strictly
increasing and injective in the cover. Its only solution of `ordinary = C` is

    (C - atom * epsilon) / (249/250) = 3507256898809/996000000000000.

The controller's before-cover is `C0 = 3459/1000000`. The same identity gives

    preimage - C0 = 62092898809/996000000000000 > 0,

so the preimage fails `before > after`. At that preimage the denominator
`C0 - C1` is negative, and the proof's positive-gap comparison does not apply.
No odd prime was tested there. The failure is the sign of the gap, not an
incomplete search.

The image of the kept gap is strictly below the component, not merely at the
emitted point. Because the slope is positive,

    ordinary(x) < ordinary(C0) for every rational x < C0,

and

    ordinary(C0) = 8613294599/2500000000000,
    C - ordinary(C0) = 62092898809/1000000000000000 > 0.

Thus every cover that keeps (H-gap) misses `C`. This is a proof about an
infinite rational ray. It does not list the ray.

The two named assignments both lie on that ray and both miss `C`:

    ordinary(69/20000) = 8590884599/2500000000000,
    ordinary(11/4000) = 6847884599/2500000000000.

The first is the selected claim. The second is what the formula would return
if it were pointed at the bridge weight. The pricing does not do that, and
storing the bridge weight under `after_cover` would be a second external
weight, dropping (H-one) or (H-writer). The bridge's own atom is `3/1000` and
its own before-cover is `69/25000`; that other formula is not the selected
formula.

Therefore no second source assignment to `after_cover` makes the selected
formula equal `C` while (H-one), (H-writer), (H-C1) and (H-gap) are kept.
Under (H-writer) and (H-C1) there is no second assignment at all. Under the
weaker requirement that a changed single weight still obey (H-gap), the
formula still misses `C`, and the bridge weight is one authenticated example.

## The odd-prime rule

The controller records `odd q > 2^26*N^5`, avoiding fixed denominators and
rank witnesses, and says that such a prime exceeds `256/(C0-C1)*N^5`. The
coefficient comparison `2**26 > 256/(C0-C1)` holds at the kept gap
`9/1000000`. That is rational arithmetic on the pinned literals. It is not a
search for a prime, and the avoidance clause was not executed. At the
preimage the same comparison has a negative denominator, so the rule's
positive-gap hypothesis is false before any prime is chosen. The avoidance
clause remains unrun. It is not the blocker of this negative result.

## What this does not say

`ordinary(69/20000) ≠ C` was already the census in
`research/g20-source-bound-cover-census`. The new statement is that the whole
positive-gap ray misses `C`, and that the retained bridge weight is not a
second `after_cover` which repairs that miss.

This note does not census other filenames, does not replay `verify.py` or the
bridge script, does not execute the outer ledger, and does not replace
`admitted` by `C` or by `ordinary`. The pricing still feeds
`bit_saving = admitted = 17/5000` to the ledger. A contract that drops
`before > after`, or that changes the formula, is outside the hypotheses.
Equality of `ordinary` with `C` would still leave this assembly's
`bit_saving` equal to `17/5000`.
