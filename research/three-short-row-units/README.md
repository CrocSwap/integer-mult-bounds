# Three short rows realize every unit coefficient for every m ≥ 6

**Task:** independent-moment (an answer to #4600's open question 2, within the row model). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## Background

petalas's #4600 proves, in #4280's row model of balanced depth-four dirty chain words with modulus m, that a unit coefficient needs at least three short rows. Its open question 2 asks whether three short rows realize every unit for every m ≥ 6. My #4622 settles the two-short-row case completely: two short rows realize c ≠ 0 exactly when gcd(c, m) ≥ 3.

## Result

The verifier enumerates the model exactly:

- every nonincreasing ρ and β with m entries in [0, m];
- every λ with exactly three short rows L₁ ≥ L₂ ≥ L₃ summing to 0 (mod m), placed after f full rows.

It finds the following.

| m | coefficients realized with exactly three short rows |
|---|---|
| 2 to 5 | none |
| 6 | 1, 2, 4, 5 |
| 7 to 13 | every nonzero c |

- **The answer to #4600's open question 2 is yes for 6 ≤ m ≤ 13.** Every unit is realized with three short rows.
- **The threshold m ≥ 6 is sharp.** For m ≤ 5, no nonzero coefficient is realized with three short rows.
- **Two vs three rows at m = 6.** The coefficient 3 needs two rows rather than three, consistent with #4622.

## Fixed-shape evidence up to m = 30

A single shape suffices well beyond the exhaustive range:

```text
λ = (m−1, m−2, 3, 0, …),   ρ = (m, a, b, padding ≤ b, …).
```

For each target only (a, b) changes, and β is decided exactly by a dynamic programme. This shape realizes every unit for 7 ≤ m ≤ 30. At m = 6 the unit 5 needs a different shape, which the exhaustive run finds.

## Theorem: three short rows realize every unit for every m ≥ 6

This answers #4600's open question 2 within #4280's row model.

**Construction (m ≥ 14).** Take λ = (m−1, m−2, 3, 0, …) and ρ = (m, 3t, 2t, padding ≤ 2t). Here t = 1 unless c = −1. In that case t is a unit with 2 ≤ t < m/3:

- t = 2 for odd m;
- t = 3 when 3 ∤ m;
- otherwise the smallest prime not dividing m, which satisfies 3t < m for every m ≥ 14.

Then put X ≡ c·t⁻¹ (mod m). This lies in [1, m−2], because t ≠ 1 whenever c = −1. Take

```text
β = (balanced block of sum X + 2m,  balanced middle of length m−5 and sum S,  X,  0),
```

where S is the least value ≥ (m−5)X with S ≡ −2(X + 2m) (mod m). Then:

- **Partial sums.** B(3) ≡ X, B(m−2) ≡ −X and B(m−1) ≡ B(m) ≡ 0.
- **Congruences.** Σ ρL = 3tm ≡ 0, and the coefficient is −(3t·B(m−2) + 2t·B(3)) ≡ tX = c.

**Monotonicity (written).** Write X = m − k with k ≥ 2.

- **First block.** Its minimum is ⌊(X+2m)/3⌋ = m − ⌈k/3⌉, so the middle block may rise by ⌊2k/3⌋ ≥ 1 per entry.
- **Middle block.** S − (m−5)X ≡ 3X ≡ −3k (mod m), so the needed excess is (−3k mod m).
- **Case k = 2.** The excess is m − 6 ≤ m − 5.
- **Case k ≥ 3.** The excess is at most m − 1 ≤ 2(m−5), using m ≥ 9.

So the middle block fits between the first block and X. All entries lie in [0, m], and the padding sum is below m ≤ 2t(m−3).

The verifier also checks the construction for **every nonzero c and every 14 ≤ m ≤ 200**. Together with the exact enumeration for m ≤ 13:

- **every unit**, and in fact every nonzero c for m ≥ 7, has three short rows for every m ≥ 6;
- for m ≤ 5, nothing does.

The fixed-shape dynamic programme for m ≤ 30 is retained as a further cross-check.

## Verify

```text
python3 -B research/three-short-row-units/verify.py
```

The check takes about 20 s and uses the standard library only.

## Limitations

- **Inherited model.** The row model and its converse are inherited from #4280.
- **Not claimed.** Call counts and κ.

## Open next questions

- **Beyond the balanced row model.** Every balanced word uses each call exactly m times, so every coefficient realized here costs exactly #4600's 4m calls. The open direction is unbalanced or signed depth-four words, where short-row counts and call counts can separate. First step: restate #4280's congruences for a word with one call used m + 1 times.

Credit: petalas (Nick Petalas) for #4600 and #4280. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
