# One frame-indicator row as a length-4 label word

No new κ. The selected record stays `781451/250000000`. This note hosts one
frame-indicator row and charges the monomials of that word. It does not host
the other twelve rows and it does not compare a histogram with the selected
profile.

## 1. Hypotheses

Ports and the odd graph are those of PR #6933. Two distinct ports are adjacent
when their `F_2` dot product is 1. Frame 0 of the #7014 witness is the ordered
8-tuple

```text
11, 21, 38, 56, 140, 146, 161, 191.
```

A **letter** is a root-line functional `λ_i(j) = (<r_i, r_j> + 1) mod 2` on the
120 root lines. A **word** is a product of letters. The product is evaluated in
`F_2`, so the value is 1 only when every factor is 1. The word **hosts** the
frame-indicator row when, on all 120 lines, the product equals 1 on these eight
lines and equals 0 on the other 112. Restriction to the 104 P104 lines is then
the indicator of this frame.

Labels use the inherited simple-root chart. If `B` is the doubled simple-root
basis of `e8model.py`, the label of a root `r` is

```text
u(r) = (coordinates of r in B, reduced mod 2) with a ninth coordinate 1.
```

The symmetric form `S9` is the Cartan matrix of `B` on the first eight
coordinates and 1 on the ninth diagonal entry. The chart is accepted only
because `S9(u_i, u_j) = (<r_i, r_j> + 1) mod 2` holds for every pair of the 120
lines. That identity is checked exhaustively; it is the pairing (1) of the
PR968 model.

Square-free monomials are written in `x0, ..., x7`, the first eight label
coordinates. The relation `x_i^2 = x_i` is used throughout, so a function
`F_2^8 → F_2` has one algebraic normal form.

## 2. The word

**Theorem.** Under the hypotheses above, no product of fewer than four letters
hosts the row. Every product of four letters that does host it expands to the
same 48 monomials

```text
(1 + x0)(1 + x1 + x2 + x4)(1 + x5)(1 + x6 + x7).
```

Eight of those monomials have degree at most 1: the constant `1` and
`x0, x1, x2, x4, x5, x6, x7`. The other **40** have degree 2, 3, or 4
(17, 17, and 6). Those 40 are the new monomials charged for this row.

One such word, the lexicographically first length-4 subset in the frame order
above, is the product of the letters of ports `11, 21, 38, 140`:

```text
λ_11 = 1 + x1 + x2 + x4 + x5,
λ_21 = 1 + x0 + x1 + x2 + x4 + x5,
λ_38 = 1 + x0 + x1 + x2 + x4,
λ_140 = 1 + x0 + x5 + x6 + x7.
```

The support of this function on the chart `x8 = 1` is the 16-point flat

```text
x0 = 0,  x5 = 0,  x1 + x2 + x4 = 0,  x6 + x7 = 0
```

(`x3` is free). Exactly eight of those points are root-line labels, and those
eight are the frame. On every root line the function is therefore the
frame indicator. It is not the indicator of those eight points inside all of
`F_2^8`.

## 3. Proof

**Factor restriction.** Suppose a product of letters equals 1 at a line. Each
factor is 0 or 1, so each factor equals 1 at that line. The indicator equals 1
on the eight frame lines, so every factor of a hosting word equals 1 on all
eight. Checking the 120 letters, the only ones with that property are the
eight frame letters. Every hosting word is therefore a product of a subset of
these eight letters, repetitions included. A repeated letter does not change
an `F_2` value, so the 255 nonempty subsets exhaust the words.

**Census.** Each of those 255 products was evaluated on all 120 lines. The
products equal to the indicator are 56 of length 4, 56 of length 5, 28 of
length 6, 8 of length 7, and 1 of length 8. None is shorter than 4. This is an
exhaustive census of a finite domain of size 255, after the factor restriction.
It is not a sample.

**Reduction.** Write `p = 1 + x1 + x2 + x4`, `q = x0`, `r = x5`, and
`s = x6 + x7`. The four letters are the functions

```text
λ_38 = p + q,  λ_11 = p + r,  λ_21 = p + q + r,  λ_140 = 1 + q + r + s.
```

On `F_2`, every function satisfies `f^2 = f`. Hence

```text
(p + q)(p + q + r) = (p + q)(1 + r),
(1 + r)(p + r) = p(1 + r),
(p + q)(p + r)(p + q + r) = p(1 + q)(1 + r).
```

The last step uses `p(p + q) = p(1 + q)`. Multiplying by `λ_140` gives
`p(1 + q)(1 + r)(1 + q + r + s)`. The target form is
`p(1 + q)(1 + r)(1 + s)`. Their difference is killed because

```text
(1 + q)(q + r) = r(1 + q),  so  p(1 + q)(1 + r)(q + r) = p(1 + q) · r(1 + r) = 0.
```

Thus the four-letter product equals `(1 + x0)(1 + x1 + x2 + x4)(1 + x5)(1 + x6 + x7)`
as a function on `F_2^8`. The four factors use disjoint variables, so the
square-free expansion has `2 · 4 · 2 · 3 = 48` monomials and no cancellation.
The eight monomials in which at most one factor contributes a variable are
`1, x0, x1, x2, x4, x5, x6, x7`. The remaining 40 are new relative to that
degree-at-most-1 alphabet.

**Same expansion for every shortest word.** The same evaluation shows that all
56 length-4 hosting products determine one polynomial: each agrees with this
expansion on all 256 points of the chart. Longer hosting products agree with
the indicator on the 120 lines. Their chart polynomials are not charged here.

**Pairing rank, not added.** On the eight frame lines the pairing matrix is
the all-ones matrix, which has `F_2`-rank 1. That is the inherited copy-cost
of the support of `χ χ^T`. It is a different unit from the 40 monomials and is
not added to them.

## 4. What the census does not decide

The factor restriction uses products of root-line letters. A sum of such
products, a coordinate change, or a circuit that is not a product can be a
different hosting, and this note gives no lower bound for those larger
alphabets. The 40 monomials are the expansion of this word in the fixed
simple-root chart. They are not a count of Clifford monomial routes, Gaussian
children, or selected-invoice primitives. No conversion into the selected paid
histogram is claimed, so this bill does not beat the selected profile and does
not change κ.

The other twelve frames of the witness are not expanded. A monomial shared
with one of them would make a joint bill smaller than the sum of the separate
bills. That comparison is not made.
