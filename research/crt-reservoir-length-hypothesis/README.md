# Production address length against p

**Scoped comparison. No new κ.** The selected conditional exponent stays
60403/20000000. This does not accept PR #4100.

## Result

PR #4328 absorbs the sparse repair under the hypothesis `L ≤ p`. PR #4646
reuses it: with `r ≤ floor(L/(100G))` and `L ≤ p`, the batch bound becomes
`r ≤ p/19200`, and the sharp-window union bound is at most
`p 2^{-G}/6400`.

The production census in PR #4174 builds one layout and then its plans.
The caller is `Layout(6 * L, ell, widths)` with `d = 65536`, `ell = 24`,
and widths alternating `24, 23`. The first plan, at level 1, partition 0,
batch 0, has active axes `(1, 3, 5, 7, 9)`. Its address length is the
layout length:

```text
L = 1540096,    p = 9240576,    p = 6L.
```

So `L ≤ p` is true for this plan, and `r_max = 5` satisfies
`r_max ≤ p/19200`. These are the constants recorded in that package's
`RESULT.json`. PR #4329 already prints the same production row, including
`p = 6L`, while deciding the guard-coloring premise. The 104,864-plan
census is not replayed.

The same constructor does not require the inequality. It accepts

```text
p = 2,    ell = 2,    d = 65536,    every width 1,
```

where `L = 65536 > p` and `r_max = 2 > p/19200`. On that layout the step
from `L ≤ p` to `r ≤ p/19200` fails. `L ≤ p` is a property of the
production choice `p = 6L`, and it remains a hypothesis for an arbitrary
#4174 layout.

## Scope

Card `formal-interface-lemma`, scope **refined**. This is the open
question left by the sharp-window two-target check. The density comparison
is PR #4646, and the placement audit is PR #4174.

No descriptor census, repair-tariff replay, `H`-bit exchange, or
multiplication theorem is claimed. The constant `1/6400` is not retuned.

Canonical main fetched 2026-10-22T23:43:14Z at
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/crt-reservoir-length-hypothesis/verify.py
python3.12 -B scripts/research_package.py --package research/crt-reservoir-length-hypothesis
```

The direct command prints `PASS_CRT_RESERVOIR_LENGTH_HYPOTHESIS`.

## Open next questions

1. On the admitted layout `p = 2`, `ell = 2`, `L = 65536`, what constant
   replaces `1/6400` in `r (2/B + β) ≤ C p 2^{-G}`? There `r_max = 2`
   exceeds `p/19200`, so the production factor does not transfer. First
   step: evaluate that one inequality at `r = r_max`. Blocker: the
   104,864-plan census is not an input here.

## Credit

Hiroki KUMAZAKI, PR #4174, for the reservoir constructor and the recorded
production constants. PR #4329 for the same production row in the
guard-coloring audit. PR #4328 for the `L ≤ p` absorption hypothesis.
PR #4646 for the constant `1/6400`. Cinna Davis, PR #4100, for the CRT
parameters those packages read.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance.
Apache-2.0. No independent human review and no formal-kernel acceptance
are claimed.
