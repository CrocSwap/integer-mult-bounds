# Exact internal grid of the selected complex word

**Positive scoped result; no new κ.** The selected chain runs the eight-relation body of
[PR #5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383) (Ali Romman), on Cao Yifan's #4610 word,
through #5392, #5398 and #5413. Public physical inputs, including dirty helpers and owned entries, are arbitrary
arrays on `2^-f Z[i]`. At payload tensor depth `lambda`, every atomic cut of this body is exact with

```text
backward program: ceil(9 lambda / 2) + 6 extra fractional bits      (11, 15, 20, 24 at lambda = 1..4)
forward program:  ceil(9 lambda / 2) + 5 extra fractional bits
stored component magnitude < H * 457 * 2^(9 lambda / 2)
```

Both guards are **attained**, so they are the exact minimum for one uniform grid. The #4610 source word gives the
same numbers. Until now the repository checked only that formal prefix norms and denominators of this word stay
below `2^192` ([eight-owned-relations/native.py](../eight-owned-relations/native.py)). For comparison, the P104
words have the sharp guard `ceil(9 lambda/2) + 2` ([p104-retimed-internal-grid](../p104-retimed-internal-grid/README.md)).
This is step 1 of target 7 in [PR #5428](https://github.com/CrocSwap/integer-mult-bounds/pull/5428).

## Model and proof

The model is the one of PR2772, PR2813 and [p104-joint-prefix-grid](../p104-joint-prefix-grid/README.md).
At an atomic cut a field standing in frame `F` holds

```text
sum_s c_s U_s^(tensor lambda) V_s(0),
```

with exact rational coefficients `c_s`, one per input `s` and native warp word. For a term without a warp word,
`U_s = Delta_F Delta_{I_s}^-1`. All charts and native maps are exact dyadic Gaussian Cliffords on nine binary
coordinates. This is inherited from the exact Clifford admission in
[kappa-round3-warp-20261022](../kappa-round3-warp-20261022/README.md). A Clifford column of Fourier rank `r` has
`2^r` nonzero entries, each a Gaussian unit times `2^(-r/2)`, so its reduced denominator is exactly
`2^ceil(r/2)` (Ross Richardson's lemma, as retained in p104-retimed-internal-grid). Under the payload lift the
rank becomes `r lambda`.

[verify.py](verify.py) replays both programs exactly over Q and records three things:

- **Dyadic coefficients.** Every scalar coefficient is dyadic; there is no odd division anywhere.
- **Fourier ranks.** For each term it computes the rank of `Delta_F Delta_{I_s}^-1` with the repository's
  Clifford compiler. As a check, that rank equals the paid rank on every one of the 3,282 to 3,290 climbs per
  program. Warp-word and owned-entry terms get the universal rank 9.
- **Pareto front.** The front of `(v2(den c_s), r)` over all terms of all cuts is `{(6, 9)}` backward and
  `{(5, 9)}` forward, so the guard is the maximum of `v2 + ceil(r lambda/2)`.

**Attainment.** Backward event 19537 adds `L321/4` into `L532`. Input `L470` occurs exactly once in the resulting
row, with coefficient `-1/64` and rank 9. Inputs are independent, so no other term cancels it: for `lambda = 1` an
input basis vector produces a component with denominator exactly `2^(6+5)`. The forward witness is event 19466,
with coefficient `-1/32` and rank 9. The largest coefficient sum `sum_s |c_s|` is 457. Since each row of a
`2^(9 lambda)`-dimensional unitary has l1 norm at most `2^(9 lambda/2)`, this gives the magnitude bound.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/selected-word-exact-grid
python3.12 -I -B research/selected-word-exact-grid/verify.py
python3.12 -I -B research/selected-word-exact-grid/test_verify.py
```

The verifier uses only the standard library and the pinned repository Clifford compiler. It takes about a minute
and prints `PASS_SELECTED_WORD_EXACT_GRID_CEIL_9L_2_PLUS_6`. The controls reject a drifted input, an odd division,
a corrupted climb rank, a smaller guard claim and a tampered RESULT.json.

## Scope

This covers the eight-relation body and its #4610 source, in both programs. It does not cover the #5413 caller
packet (normalizers, the #5402 coupled provider with `ZW = 14 I`, owned fields). Native operator correctness, the
canonical-chart convention and the tensor-lift convention stay inherited premises. It is an exact-grid statement,
not a rounded execution, a paid recursive implementation or a supplier admission. The selected record is unchanged.

## Open next questions

- **Caller packet.** What exact grid does the complete #5413 caller packet need? First replay its literal packets
  with the same census. An odd division there would rule out a fixed dyadic grid for the selected result.
- **Recursive price.** What does the attained guard cost in the recursive invoice? #5419 shows that a uniform
  paid-precision factor above about 1.0046 removes the 0.0033 margin. First compare the guard with the retained
  precision_tape packing.

## Credit

Cao Yifan (#4610) supplied the word. Ali Romman (#5377, #5383) and the eight-owned-relations package supplied the
relation body. Ross Richardson supplied the Clifford denominator lemma. The P104 grid packages (PR2674, PR2772,
PR2813) supplied the model. zxv's #5428 named precision composition as a target. Prepared by Mark (Matarener)
with substantial Claude Code assistance. New work is Apache-2.0.
