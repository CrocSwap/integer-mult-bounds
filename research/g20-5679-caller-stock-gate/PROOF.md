# Proof: the selected pricing rejects the PR5679 BIT component as admitted BIT

## Setting

The selected conditional result is PR6030, κ = 781451/250000000.
`research/p104-helper470-twin-rung-removal/pricing.py` is the pricing
assembly admitted with that result. It fixes

    κ = 0.003125804,    TESTED = 0.0031258090,

and reads `ordinary_BIT` from
`research/query-thinned-controllers/RESULT.json`. With atom = 1/250,
after_cover = 69/20000 and ε = 0.0000384599, it sets

    ordinary = (1 − atom) · after_cover + atom · ε,
    admitted = 17/5000,

and requires the strict stock gate

    atom > ordinary > admitted > TESTED

before calling `ledger` in
`research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py`
with `bit_saving = admitted`. The gap used by that call is

    gap = (TESTED − κ) / 7 = 1/1400000000,

and the complex uniform input is U = κ + 6·gap. The effective BIT threshold
inside the ledger is a = κ + 4·gap.

PR5679's ordinary receipt
(`research/g20-helper-split/ORDINARY-RESULT.json`) records component saving

    C = 3507410738409 / 1000000000000000

and `whole_kappa = null`. That file is the component's five-level ordinary
admission, not a whole-multiplication claim.

PR5708's later receipt records the strictly larger component

    C₂ = 3507719059749 / 1000000000000000.

`research/g20-component-stock-gate` already shows that the selected gate
rejects C₂. That comparison does not decide C: a smaller component could
have fallen to or below the selected ordinary stock. This note checks C
directly.

## Arithmetic

Direct expansion gives

    ordinary = 8590884599 / 2500000000000,

which is the selected claim's `ordinary_BIT_saving`. The same claim records
`admitted_BIT_saving = 17/5000` and complex uniform saving

    U = 10940329 / 3500000000 = κ + 6·gap.

The seven quantities then satisfy

    U < 17/5000 < ordinary < C < C₂ < 1/250 < 1/32.

In particular

    C − ordinary = 71056898809 / 1000000000000000 > 0,
    C₂ − C = 15416067 / 50000000000000 > 0,

so `ordinary > C` is false even though C < C₂. The stock gate with
`admitted` replaced by C fails. The same numbers satisfy

    1/250 > C > 17/5000 > TESTED,

so C lies strictly between the stock atom and the BIT value the pricing
actually passes to the ledger.

## The ledger is not the rejecting gate

In the pinned `endpoint.py`, the only check expression that reads
`bit_saving` is

    actual_bit_above_effective = bit_saving − a.

Every other strict check, and every functional check, is independent of
`bit_saving`. The selected parameters already have 17/5000 − a > 0, and
C − a > 17/5000 − a > 0. Therefore every ledger check that passes at
`bit_saving = 17/5000` still passes at `bit_saving = C`. The pricing's own
control `bit_saving = 0.0027` still fails some strict check, and
`bit_saving = a` makes `actual_bit_above_effective` zero, so the strictness
is still enforced.

The fourth functional check added by pricing, `β(1 − atom)` with
β = 1 − 3·gap, does not read `bit_saving` and stays positive.

## What this does not raise

Under the selected family shape the complex uniform input U is strictly
below both 17/5000 and C. Raising `bit_saving` from 17/5000 to C loosens
only `bit_saving − a`. It does not increase U, and the selected κ remains
strictly below U by 6·gap. Accepting C as a ledger input would not raise
the selected exponent.

Solving the ordinary formula for the cover that would produce C gives

    after_cover = (C − atom · ε) / (1 − atom)
                 = 3507256898809 / 996000000000000,

which is not the pinned 69/20000 and is not the cover implied by C₂.
The selected controller does not supply that cover. This package does not
construct one.

## Scope

This is a stock-gate and ledger-arithmetic certificate for one substitution
into the selected pricing. It does not replay the PR5679 caller, native
maps, compiler, tape, or analytic recovery, and it does not change κ.
The five selected framework assumptions remain in force.
