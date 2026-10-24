# The narrow row keeps half its certified gap

**Claim type:** one quantified implication for the #4100 narrow reference row.
**No new κ.** The selected conditional value stays `60403/20000000 = 0.00302015`.

`vendor/FINE-PRIME.md` says that deleting diagonal aliases preserves a
polynomial gap, and that exponentially accurate band truncation and rounding
preserve half of it. `GAUSSIAN.md` concludes that the rounded reference `H`
has diagonal 1, row gap at least `1/(16p^2)` and row norm below 2. The
coverage map still lists an explicit form of that half-gap sentence as open.
This note supplies the budget the sentence does not write down.

## Statement

Fix an integer `p ≥ 1`. Write `log` for the natural logarithm, as required by
the comparison `5 exp(-2a) ≤ 5/(16p)^8` in LOG-A §1 when `a ≥ 4 log(16p)`.
Let `a ≥ 4 log(16p)` and `θ ≥ 1/(4p^2)`, and set

```text
S = exp(-2 a θ) + 5 exp(-2 a),    γ = 1 - S.
```

The parameter minimum is the worst case: both terms of `S` fall as `a` or `θ`
grows. At that minimum,

```text
γ ≥ 1/(8p^2).
```

Let a real row have nonnegative diagonal `d` and off-diagonal absolute sum
`Off`, with

```text
Off + |d - 1| ≤ S.
```

Form the reference row as follows.

1. **Alias removal.** Replace the diagonal by 1 and leave the off-diagonal
   entries unchanged.
2. **Band truncation.** Replace any set of off-diagonal entries by 0.
3. **Rounding.** Add a real perturbation whose off-diagonal absolute row sum
   is at most `τ`, then set the diagonal back to 1.

The resulting diagonal is 1 and the row gap is at least `γ - τ`. In
particular, every

```text
τ ≤ 1/(16p^2)
```

leaves row gap at least `1/(16p^2)` and absolute row sum strictly below 2.
Alias removal and truncation spend none of the certificate `γ`. Only rounding
spends it, and the published half is exactly this uniform budget.

A sufficient per-entry rule is: at most `2p` off-diagonal entries change, and
each absolute value grows by at most `2^{-5p}`. At `p = 1` the total equals
`1/(16p^2)`. For every `p ≥ 1`, `(1 + 1/p)^3 ≤ 8 ≤ 32`, so the same comparison
persists at `p + 1`. The same count with `2^{-4p}` fails at `p = 1`. This does
not identify #4100's unnamed precision constant with 5.

Any defect at most `p^M 2^{-c p}`, for integers `c ≥ 1` and `M ≥ 0`, is inside
the budget once `2^{c p} / p^{M+2}` is at least 16 and increasing. For `c = 1`
the checker records a sufficient such `p` for every `M ≤ 8`: 11, 16, 22, 29,
35, 42, 49, 57 and 64. FINE-PRIME's eventual row-norm bound
`poly(p) 2^{-(C-o(1))p}` therefore meets `τ ≤ 1/(16p^2)` for every fixed
`C > 0` and all large `p`. The implicit degree and the finite cutoff are not
extracted here.

## Proof

**Ideal certificate.** Let `x = 2 a θ`. The minimum is
`x ≥ 2 log(16p) / p^2`. The series remainder gives `exp(2) < 8`, so
`log(16p) > 2`. Thus the minimum `x` is greater than 1 at `p = 1` and at
`p = 2`.
The same series gives `exp(1) > 8/3`, hence `1 - exp(-1) > 5/8`. For these two
values of `p`,

```text
γ ≥ 5/8 - 5 (16p)^{-8} ≥ 1/(8p^2).
```

For the Taylor step, `f(x) = 1 - x + x^2/2 - exp(-x)` satisfies `f(0) = f'(0) = 0`
and `f''(x) = 1 - exp(-x) ≥ 0` for `x ≥ 0`. Thus `f` and `f'` stay nonnegative,
`exp(-x) ≤ 1 - x + x^2/2`, and

```text
1 - exp(-x) ≥ x(1 - x/2) ≥ x/2    for 0 ≤ x ≤ 1.
```

The partial sum of `exp(9/2)` through degree 5 exceeds 48, so the minimum `x`
is at most 1 at `p = 3`. The partial sum of `exp(7/2)` through degree 2 exceeds
2, and `(p+1)/p ≤ 4/3 < 2` for `p ≥ 3`, so `exp(p + 1/2) ≥ (p+1)/p`. Therefore
`16p ≤ exp(p^2/2)` persists for every integer `p ≥ 3`, and the worst-case `x`
stays at most 1. There

```text
1 - exp(-x) ≥ x/2 ≥ log(16p)/p^2 ≥ 2/p^2,
γ ≥ 2/p^2 - 5 (16p)^{-8}.
```

Clearing the positive denominator is the integer comparison
`15 · 2^{32} ≥ 40`, which is exactly `2/p^2 - 5/(16p)^8 ≥ 1/(8p^2)` at `p = 1`
and is stronger for `p > 1`.

**Three operations.** From `Off + |d - 1| ≤ S` and `d ≥ 0`:

- if `d ≥ 1`, then `Off ≤ S - (d - 1)` and `1 - Off ≥ 1 - S`;
- if `0 ≤ d < 1`, then `Off ≤ S - (1 - d)` and `1 - Off ≥ 2 - S - d ≥ 1 - S`.

Zeroing an off-diagonal entry cannot increase an absolute sum, whatever its
sign. A perturbation of off-diagonal absolute row sum `τ` increases that sum
by at most `τ`, by the triangle inequality. Resetting the diagonal to 1
discards only the diagonal part of the perturbation. The gap is therefore at
least `γ - τ`.

The budget is sharp relative to the certificate, whether or not the Gaussian
tail meets it. A row with `d = 1` and `Off = 1 - 1/(8p^2)`, and with truncation
removing nothing, is allowed by `γ ≥ 1/(8p^2)`. A defect of exactly `1/(16p^2)`
then leaves gap exactly `1/(16p^2)`, and a defect of `1/(8p^2)` leaves gap 0.
Alias mass or a deleted tail makes the final gap strictly larger, so those two
operations cannot be what forces the factor one half. The Gaussian value of
`S` may be strictly smaller than `1 - 1/(8p^2)`; that extra slack is not used.

**Row norm and principal sections.** Diagonal 1 and off-sum at most
`1 - 1/(16p^2)` give absolute row sum `2 - 1/(16p^2) < 2`. A principal
subrow keeps a subset of the off-diagonal entries, so its absolute off-sum
is no larger and its gap is no smaller.

**What the factor one half is not.** It is half of the published certificate
`1/(8p^2)`, not necessarily half of the true `γ`. The `x/2` branch is at least
`2/p^2` before the tiny tail, sixteen times `1/(8p^2)`. Extra slack is real
and unused. Charging each of `2p - 1` band entries with mass `1/(16p)`, the
old margin copied once per entry, produces a row change larger than
`1/(8p^2)` for every `p ≥ 2`. The budget has to be a total row sum.

## What this does not prove

LOG-A §3 already shows that one elimination step on a strictly row-diagonally
dominant matrix does not decrease the minimum absolute row gap. The identity
does not use the numerical size of the gap, so it applies to a matrix whose
gap is `1/(16p^2)`. This package does not re-prove that identity, and it does
not rerun the Gaussian circuit.

The column statement in `research/gaussian-gauge-column` is a different
mechanism: a relative weight error inside one cell, with the explicit warning
that a row-sum bound does not replace it. #4402 and #4437 bound ideal column
sums. #4481 keeps a Schur margin of `1/(10p^2)` once that larger gap is
already known. None of those is the alias, truncation and rounding budget for
the row.

The Neumann bound `‖H^{-1}‖_∞ ≤ 1/δ` applies after this lemma with
`δ = 1/(16p^2)`, because `H = I - E` with `‖E‖_∞ ≤ 1 - δ`. The `p^{10}` norm,
the chirp origin, across-cell columns and the unnamed setup constant remain
open. This is not an admission of #4100 and not a change to the selected
frontier.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/narrow-row-half-gap --check-only
python3 -B scripts/research_package.py --package research/narrow-row-half-gap
```

`verify.py` pins the five source sentences, checks the series comparisons, the
uniform integer certificate, the three operations for `p = 1..200`, the `C = 5`
and `C = 4` entry rules, the polynomial thresholds, and the singular control.
It does not evaluate a Gaussian matrix and does not replay #4100.

## Task and overlap

- Card `uniform-transfer-audit`, scope refined to this one precision sentence.
- Base: canonical main `fbc9ea0249746acca4f504d4fda2b84e0e36cf0d`, priority
  revision 7. #4100 remains pinned by the family record at
  `337d04939571a637aeab54a0f58f54fde811663a`.
- The coverage map's still-open column, after dropping merged closures
  including #4356, #4371, #4373, #4376 and #4377, puts this sentence at the
  ninth remaining obligation. #4217 open question 1 and #4371 open question 2
  ask for the same explicit budget.
- #4438 records that its column gauge is not a row argument. This package is
  that missing row argument.

## Open next questions

1. Does the stored narrow band have at most `2p` off-diagonal entries in every
   row, and does the note's rounding meet absolute error `2^{-5p}`? The total
   budget above is proved either way. The first step is the definition of `W`
   in `GAUSSIAN.md` together with one rounding mode for a kernel entry. It is
   blocked until that mode is pinned; the name `C` in the setup formula is not
   yet a number.
2. Which chirp origin does the interior caller use? The coverage map lists
   this beside the half-gap sentence, and #4304 shows that a centred chirp can
   push one `p = 19` entry above 1. The first step is to name the origin in
   the interior kernel and compare that one entry. This row budget does not
   choose the origin.

## Credit

The ideal bound `‖N-I‖_∞ ≤ exp(-2aθ) + 5 exp(-2a)` is LOG-A §1 from PR1673.
PR1786, and #4100's byte-identical `vendor/FINE-PRIME.md`, state the half-gap
sentence. The `1/(8p^2)` certificate for every `p ≥ 1` is the merged
`pr1786-fine-prime-transfer-audit`. #4217 asked the question. #4438
(James Reed) separated the within-cell column gauge from any row-sum charge.
#4402, #4437 and #4481 are the neighbouring column and Schur results cited
above and not reused as a row proof.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review is claimed.
