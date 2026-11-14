# Prove a uniform rounding margin for all 24 orders of two selected source factors

## Result

A11 proves exact rank at selected source phases, but exact nonvanishing alone gives no Cp-bit margin. This package closes a quantified two-axis case using the deterministic extremal phase `s beta_i=-(s-1)/2`. Arbitrary A11-good phases remain open.

For the retained fine-prime parameters with `p>=4096`, `s_l>=p^4` and integer `alpha=ceil(sqrt((4/pi)ln(16p)))`, the selected pair is exactly `[[1,U_l],[V_l,1]]`, with phase/chirp retained. Write `a=pi alpha^2`, `w=exp(-2a)`. In all 24 orders of the two-axis tensor, ordinary Stein determinant magnitude is at least `w^2/16`; smallest singular values are at least `2^-10 w^2` forward and `2^-19 w^2` for the inverse.

Per-factor absolute entry error at most `2^-34 w^2` preserves full displacement rank for the perturbed tensor and its inverse. Thus `b>=ceil(34+36 log2(16p))` bits suffice; `p` bits suffice for every `p>=4096`. The exact matched periodization `Pi(G)` contributes at most `4exp(-a t^2/8)` per selected factor entry and fits an additional two-bit allowance. This covers the selected tensor of periodic principal sections and its own inverse under a stated entry-error contract.

## Proof, costs and boundaries

The orders split into explicit lex/Gray determinant classes and eight opposite-first orders with reference determinants ±1. Uniform inequalities cover a continuous parameter box. Determinant/norm bounds, a Schur-complement determinant identity and a charged Neumann estimate give forward/inverse stability. No transcendence argument is needed.

A modular inverse selects each nonwrapping source index in polynomial bit work in log s, with logarithmic scratch and paid outputs. Coefficients, inverses, generator pages, transport and setup remain separate. A symbolic three-axis family in the same box has duplicate displacement columns for one order: unchanged tensorization fails. That boundary family is not an actual distinct-prime source counterexample.

No production routine is declared admitted. The named #6099 guards `u d<=p, 4d theta>1` contradict `theta<=p^-2` for `p>=4,u>=1`; this excludes that particular admission theorem, not every possible producer. Matrix identification, setup precision and coefficient construction remain open. Inverse sections of larger matrices are not interchangeable with these selected inverses.

No new kappa is claimed. All five assumptions and selected #7000 remain unchanged. The ordinary-generator consequence is a specified representation statement, not a general algorithmic lower bound.

## Evidence and reproduction

Canonical base `e54523517d0f03e58352e647c403a5af3e525a57`; package-only addition with exact pins.

```sh
python3 -I -W error -B research/extremal-phase-two-axis-margin/verify.py
python3 -I -O -W error -B research/extremal-phase-two-axis-margin/verify.py
python3 -B scripts/research_package.py --package research/extremal-phase-two-axis-margin
```

The direct normal/optimized commands print `PASS_EXTREMAL_PHASE_TWO_AXIS_MARGIN` with identical receipts. Checks cover all 24 symbolic/reference orders, 72 rational ordered fixtures and 288 exact Gram certificates including perturbed inverses, two declared p=4096 source tuples with exact primality certificates, 32 literal alias exponent checks, and 11 controls. Independent root review supplies a stronger continuous Bernstein certificate without importing author math code. Finite fixtures corroborate the written proof. No supplier cold replay, native caller, human/formal-kernel acceptance or hosted CI is claimed.

## Predecessors and credit

Immediate predecessor: [A11 selected source-pair theorem](https://github.com/CubeJerry/integer-mult-bounds/commit/0a6315b71a47b37a4faa2a4f555c5bc4e9e87811). Credit [A10 core specialization](https://github.com/CubeJerry/integer-mult-bounds/commit/da06a3d10e06870a0279e33dd5056ded8d7e7a38) and the [normalized lexicographic margin](https://github.com/CubeJerry/integer-mult-bounds/commit/575491d5fc353eac26010e45e9ced60fc9870017). Their scopes are not silently extended.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. The worker proposed and derived the extremal-phase proof; the lead independently reviewed it, supplied the alias/g3 observations and constructed a separate continuous certificate. Credit Chafik Boukhalfa / #1786, Vlado Vojdanovski / #1673, IdeaOuter's shift work credited in #1758, Jeremy Kothe and the bilateral source lineage, JoyboyBrian / #6099, Jose Manuel/jmbarrancoml / #3851, and the framework contributors. Classical determinant, norm, Schur, Neumann and Bernstein facts are credited. Original notices and Apache-2.0 terms remain unchanged.

## Executed independent verification

`review/ROOT-REVIEW.md` proves the Bernstein conversion behind a separate exact checker: all19992 coefficients for all24 orders are positive on the continuous box. It also checks the exact three-axis nonextension. Run `python3 -I -W error -B research/extremal-phase-two-axis-margin/review/check_bernstein.py`, also with `-O`; both commands are in VERIFY.json. A separate agent's source/proof review in `review/CROSS-REVIEW.md` authenticates the normalization, source parameters, alias and inverse/error interfaces without duplicating that polynomial implementation.
