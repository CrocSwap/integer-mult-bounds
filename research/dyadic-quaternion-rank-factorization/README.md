# Exact dyadic quaternion channel factors

Every finite rectangular matrix over the dyadic Hamilton quaternion ring
factors through exactly its rational quaternion rank. The exact algorithm
uses Hurwitz Euclidean row reduction and tracks its inverse operations.
If `2^s A` has integral coordinates, its attaining factors `A=C B` satisfy
`C in O` and `2^s B in O`, entrywise, where `O` is the Hurwitz order.
Thus left coordinates need at most one half; right denominators divide
`2^(s+1)`. No odd denominator appears in either emitted factor.

This answers the general-response question in PR7745 and the coefficient
part of the atlas's RQ10. The Euclidean method is classical. Read
[PROOF.md](PROOF.md), [factor.py](factor.py), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json) and [CREDITS.md](CREDITS.md).
There is no new kappa or physical query implementation.

## Reproduce

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/dyadic-quaternion-rank-factorization
```

Both registered commands print:

```text
PASS_DYADIC_QUATERNION_RANK_FACTORIZATION exact rank and denominator certificates
```

The checker verifies 669 matrices, 947 Euclidean reductions, 4,096 rounding
points, complete inverse/factor identities, denominator bounds and a separate
rational block rank. It replays the original channel-gap evidence unchanged.
Eight domain rejections, three altered certificates and two order/stagnation
controls test the stated boundaries. See [VALIDATION.md](VALIDATION.md).

## Scope

The theorem concerns the full dyadic Hamilton coefficient ring. A smaller
ordinary dictionary can have a larger inner rank. Exact rational arithmetic
may use odd denominators while choosing a rounded quotient; the emitted
quotients and factors have the promised Hurwitz/dyadic coefficients.
Coefficient magnitudes and compiler bit complexity are not bounded here.
Actual reached-grid halving, source preservation, queries, movement, storage
and cleanup still need a complete caller. All five framework assumptions
and the selected frontier remain unchanged.

## Open next questions

1. Can an attaining factorization have a useful coefficient-height bound?
   Start with Euclidean row operations on a fixed rank-one rectangular family.
   The denominator theorem alone does not control numerators or conditioning.
2. Can a reached caller use these factors with a charged ordinary dictionary?
   Start with PR7745's two-by-two response and its changed half placement.
   The exact input grid, coefficient words, query boundary, preservation and
   scratch restoration must be supplied together.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas, Dugongue and the classical Hurwitz arithmetic sources retain
credit. No independent human or formal-kernel acceptance is claimed.

[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19719542).
