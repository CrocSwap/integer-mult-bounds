## Result and why it matters

Prove the sharp forward outward radial slack `sqrt(19)-sqrt(13)` for every
Gaussian integer pair map that preserves the complex sum, has Euclidean
pair error at most one from `C_+`, and squares exactly to wire swap. An
explicit global bijection attains the bound and also preserves global
Gaussian-unit covariance. Phase covariance and periodicity are not premises
of the lower bound.

This establishes the precise radial cost of retaining the native square
identity in this one-pair class. It is an arithmetic sub-lemma for a possible
alternative rounding interface, not selected-supplier admission.

## Universal proof and construction

On the fixed sum-one fiber, the square identity forces a bijective unit
matching on the half-grid that commutes with quarter-turn. A 36-vertex square
cannot be internally matched because matching edge orbits use eight
vertices. A forced crossing has radial cost at least the stated constant.
Pairing adjacent square rings gives the matching upper bound.

The exact four-cycle `(3,-2) -> (3i,1-3i) -> (-2,3) -> (1-3i,3i)`
alternates squared norms 13 and 19. Since `F^2=swap`, forward outward,
inverse outward and bilateral radial suprema agree in this class. No
unrestricted forward-only lower bound is asserted without the square identity.

## Verification and review boundaries

The package preserves the frozen all-input proof and bounded ring checker,
a separate constructive review and direct integer implementation, and a
separate root implementation and review of the critical arbitrary-map
reduction. The constructive role explicitly does not certify that reduction.
The root/proof role checked both half-grid color domains before applying
the matching-orbit argument.

Exact independent checks cover 66,804 half-grid points, 129 ring-pair
partitions, 50,625 Gaussian pairs and 320 large inputs through 4,096 bits.
Separate proof and root checks cover the boundary edges, attaining cycle
and smaller input sets. Seven constructive negative controls and additional
interface controls remain active under optimized Python. The publication
verifier compares all three implementations and both unbounded direct
models. These finite tests corroborate the written universal proof.

## Base and reproduction

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Python 3.12 standard library; package-local runtime evidence only.

```sh
python3 -B scripts/research_package.py --package research/sharp-order-four-gaussian-rounding --check-only
python3 -B scripts/research_package.py --package research/sharp-order-four-gaussian-rounding
```

Expected markers include `PASS_SHARP_ORDER_FOUR_CROSS_IMPLEMENTATIONS`,
`PASS_ANNULAR_GAUSSIAN_ORDER_OPTIMUM` and `PASS_REGISTERED_RESEARCH_PACKAGE`.
All eight registered normal/optimized commands are bounded and read-only.

## Novelty and predecessors

Credit Ali Romman's #6509 conserved nearest rounding and Nick Petalas's
#6619 norm question, with ywz65's #2589 lineage. #6776 already supplies an
exact-square construction for a four-axis block; this result is the sharp
one-pair radial classification. #6534, #6536 and #6574 address distinct
larger-block interfaces. Exact proof and inspected-metadata pins are retained.

The earlier [global-half theorem](https://github.com/CubeJerry/integer-mult-bounds/commit/26226aa52337e6e94bc0cdf3cf6b89d16bb42f5f) and
[exact-sum conjugation-inverse theorem](https://github.com/CubeJerry/integer-mult-bounds/commit/7cb82481cf473cdea14dbeb88ab35d336248d226)
use different contracts and smaller radial constants. This is not a numerical
improvement over either class.

## Limitations and open obligations

Exact sum and `F^2=swap` cannot coexist with inverse-by-componentwise-
conjugation: input `(1,0)` would force conjugate Gaussian outputs summing
to one. The actual inverse is `swap o F`. The constructed map also meets
#6778's hypotheses, so the known theorem excludes commutation of the same
stateless map across row and column applications. This result does not
establish tensor flatness, linearity or a selected rounded caller.

A fully charged fixed-width/tape implementation, actual caller admission,
complete precision/error recurrence and larger-block tradeoffs remain open.
**No new kappa.** The selected `363005817/100000000000` and all five
framework assumptions remain unchanged.

## Credit and assistance

Prepared for **@CubeJerry** with substantial OpenAI ChatGPT/Codex assistance.
The root supplied the annular candidate; distinct AI proof and constructive
roles developed and checked complementary claims; root independently
reviewed the critical reduction and exact implementation agreement. Shared
formulas and reference exposure are disclosed. No blind, human or formal-
kernel review is claimed. Retained predecessor notices apply. Apache-2.0.
