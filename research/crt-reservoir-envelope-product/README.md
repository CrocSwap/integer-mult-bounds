# Envelope product on the equality-case layout

**Scoped comparison. No new κ.** The selected conditional exponent stays
60403/20000000. This does not accept PR #4100.

## Result

PR #4646 uses the printed envelope

```text
E(p, ell) ≤ C_E 2^{4 ell} (p+2)^{16}
```

and the room line

```text
2^{-G} 2^{4 ell} (p+2)^{16} ≤ 2^{-60 ell} (p+2)^{-48}.
```

On the equality-case layout `p = 1`, `ell = 2`, `G = 256`, `r_max = 2`,
the scalar prefactor from PR #4923 is `3 r_max = 6`. The product asked
for is

```text
6 · 2^{-256} · 2^{8} · 3^{16} = 3^{17} / 2^{247}.
```

The room line at these parameters is `1 / (2^{120} · 3^{48})`. Their
ratio is

```text
3^{65} / 2^{127}.
```

Since `2^{103} ≤ 3^{65} < 2^{104}`, this ratio lies in
`[2^{-24}, 2^{-23})`. It is strictly less than 1, so the product is
strictly below the room line. It is also strictly less than `1/6400`:
`6400 · 3^{65} < 2^{127}`, and `2^{127} / (6400 · 3^{65})` has integer
quotient 2580. Because `p = 1`, that is the same comparison as the older
allowance `(C_E p / 6400)` times the room. The scalar step with
`C = 1/6400` still fails on this layout. The slack in the envelope,
`(3/4)^{64}`, is what brings the product back under that allowance.
`C_E` multiplies both sides and is not evaluated.

The same ratio on the admitted layout `p = 2`, `ell = 2`, `r_max = 2`
is exactly 6, because `p+2 = 4` is a power of two and the envelope has
no slack. There the product exceeds the room line. The equality-case
bound does not extend to every accepted layout.

## Scope

Card `formal-interface-lemma`, scope **refined**. This is the open
question of the uniform constant. The check is two layouts and exact
integer arithmetic. It does not evaluate the production plan, form the
real `E` polynomial, or rerun the 104,864-plan census. No multiplication
theorem is claimed.

Canonical main fetched 2026-10-23T00:00:26Z at
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/crt-reservoir-envelope-product/verify.py
python3.12 -B scripts/research_package.py --package research/crt-reservoir-envelope-product
```

The direct command prints `PASS_CRT_RESERVOIR_ENVELOPE_PRODUCT`.

## Open next questions

1. On the production plan `p = 9240576`, `ell = 24`, `r_max = 5`, is
   `3 r_max ((p+2) / 2^{ceil(log2(p+2))})^{64}` at most `1/6400`? The
   equality case is below that allowance, and the layout `p = 2` is
   above the room itself. First step: compute `ceil(log2(9240578))` and
   compare `15 (p+2)^{64}` with `2^{64 ceil(log2(p+2))} / 6400`.
   Blocker: the production plan is not evaluated here.

## Credit

Hiroki KUMAZAKI, PR #4174, for the constructor that admits both layouts.
PR #4646 for the printed envelope and room line. PR #4923 for the
prefactor `3 r_max`. Cinna Davis, PR #4100, for the CRT parameters.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance.
Apache-2.0. No independent human review and no formal-kernel acceptance
are claimed.
