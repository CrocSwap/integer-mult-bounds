# Constant on the longer reservoir layout

**Scoped comparison. No new κ.** The selected conditional exponent stays
60403/20000000. This does not accept PR #4100.

## Result

PR #4646 proves, when `L ≤ p` and `r ≤ floor(L/(100G))`,

```text
r (2/B + β) < r (2 + 2^{1−62G}) 2^{−G} ≤ p 2^{−G} / 6400.
```

PR #4913's admitted layout `p = 2`, `ell = 2`, and 65,536 widths of 1 has
`L = 65536 > p`, `G = 256`, and `r_max = 2`. At `r = r_max` the factor
`1/6400` does not survive. The exact sharp ratio is

```text
C_* = 2 + 2^{-15871} - 2^{-16126}.
```

It is the number `C` in `r (2/B + β) = C p 2^{-G}`. It lies strictly
between 2 and 3, so `C = 2` fails and `C = 3` holds. Thus 3 is the
smallest integer constant that replaces `1/6400` for this one inequality.

The published window term has exact ratio `2 + 2^{-15869}`. It has the
same integer threshold: `1/6400` and `2` fail, and `3` holds.

The production plan `L = 1540096`, `p = 9240576`, `r_max = 5` still
satisfies `5 · 3 · 6400 ≤ p`. This package does not replace `1/6400`
there. The `< 3` majorant is the one PR #4646 uses to reach `1/6400`.

## Scope

Card `formal-interface-lemma`, scope **refined**. This is the open
question of the production address-length comparison. The check is one
layout at `r = r_max`. It does not give a constant for every layout with
`L > p`, and it does not rerun the 104,864-plan census. No repair
tariff, `E` multiplication, or multiplication theorem is claimed.

Canonical main fetched 2026-10-22T23:47:42Z at
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/crt-reservoir-length-constant/verify.py
python3.12 -B scripts/research_package.py --package research/crt-reservoir-length-constant
```

The direct command prints `PASS_CRT_RESERVOIR_LENGTH_CONSTANT`.

## Open next questions

1. For every layout the #4174 constructor accepts, is
   `C = 3 r_max / p` sufficient for
   `r (2/B + β) ≤ C p 2^{-G}` at `r = r_max`? The constant 3 is proved
   here only for `p = 2` and `ell = 2`. First step: show that every
   accepted layout has `G ≥ 256`, so `2 + 2^{1−62G} < 3`. Blocker: this
   package checks only the one longer layout.

## Credit

Hiroki KUMAZAKI, PR #4174, for the constructor that admits this layout.
PR #4646 for the `1/6400` absorption. PR #4328 for the `L ≤ p` hypothesis
that absorption uses. Cinna Davis, PR #4100, for the CRT parameters.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance.
Apache-2.0. No independent human review and no formal-kernel acceptance
are claimed.
