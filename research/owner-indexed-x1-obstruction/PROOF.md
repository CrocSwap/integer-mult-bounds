# No D-exponent-0 owner index clears the three-term x1 block

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

No new κ is claimed. The selected frontier is unchanged.

Evidence class: **proof** in the predecessor's formal algebra, under the
hypotheses below. The multiplier space is infinite. This is not an
enumeration of words, not a bounded search, and not a theorem about every
quotient or every physical caller.

## Object

Use the published two-edge feed in
[research/coded-active-feedback](../coded-active-feedback/PROOF.md),
replayed by `search.replay(one, C1 Q^2)`. After the left endpoint the
replay stores four banks. Bank 2 carries

```text
A = D1 Q^{-1}
```

together with the y0 coupling and the three-term x1 block. The reading on
one owner is a left combination of these four banks by D-exponent-0
elements `m0, m1, m2, m3` of the predecessor's `Q, C1, C3` algebra. It
does not mix owners. The four stored banks are only read. A fresh image is
this combination and nothing else.

Negative D exponents, owner-mixing maps, and a feedback edge outside the
published two-edge feed are outside this statement. The declared
alternating-family lock and the one-edge `C1 Q` row are not re-proved.

The algebra is the one installed by `search.algebra()`: words in the free
product `C4(Q) * C2(C1) * C2(C3)`, with formal D exponents, and with `D_i`
conjugating only `C_i` by `Q^{-1}`. A D-exponent-0 left factor therefore
concatenates words and preserves the D degree of the right factor.

## The banks

The replay equals the following columns. Here `D(1,0)` is `D1` and
`D(1,1)` is `D1 D3`.

```text
bank 0:  x0 = (Q^{-1} C1 + Q^2 C1) D1
         y0 = Q^{-1} D1
         x1 = -Q^2 C1 D1
         y1 = 0
bank 1:  y0 = C1 Q D1
         x0 = x1 = y1 = 0
bank 2:  x0 = A = Q^{-1} D1
         y0 = (Q^{-1} C1 Q - Q^{-1} C1 Q^2) D1
         x1 = (Q^{-1} C1 Q C1 - Q^{-1}) D1 + Q^{-1} C3 D1 D3
         y1 = 0
bank 3:  x0 = C3 Q^{-1} C1 D1 D3
         y0 = C3 D1 D3
         x1 = (-I - C3 Q^{-1} C1 + C3 C1) D1 D3
         y1 = C3 Q D1 D3
```

`verify.py` compares these polynomials with the replay. Bank 3's x0 column
is the only x0 column on the `D1 D3` line, and it is a monomial. Its
two-sided inverse in the algebra sends `m3` times that column to `m3`.
The target `A` has no `D3` component, so every solution of `S_x0 = A` has
`m3 = 0`.

## The forced shape

Write `x` for bank 0's x0 column times `A^{-1}`, and write

```text
const = Q^{-1}(C1 Q C1 - I) = -Q^{-1} + Q^{-1} C1 Q C1.
```

Direct multiplication gives

```text
x = (Q^{-1} + Q^2) C1 Q = Q^2 (I + Q) C1 Q,
Q^{-1} + Q^2 = Q^2 (I + Q),
bank0_x0 = x A,
bank2_x1 = const D1 + Q^{-1} C3 D1 D3.
```

The second formula for `x` uses `Q^2 Q = Q^3 = Q^{-1}`. Thus every
D-exponent-0 solution of `S_x0 = A` has

```text
m2 = 1 - m0 x.
```

Bank 1 has zero x1, and `m3 = 0`, so

```text
S_x1 = bank2_x1 + m0 (bank0_x1 - x bank2_x1)
     = (const - m0 C1) D1 + (1 - m0 x) Q^{-1} C3 D1 D3.
```

The same two element identities

```text
bank2_y0 + const · bank1_y0 = 0,
bank0_y0 - C1 · bank1_y0 - x bank2_y0 = 0
```

give, for `m1 = const - m0 C1`, the y0 column `S_y0 = 0`. Banks 0, 1, and
2 have zero y1, so `S_y1 = 0` as well. Imposing y0 zero fixes `m1` and
does not appear in `S_x1`.

## The D1 D3 summand never vanishes

Right multiplication by the group element `Q^{-1} C3` is bijective on the
D-exponent-0 algebra: its two-sided inverse is `C3 Q`, and

```text
(Q^{-1} C3)(C3 Q) = I = (C3 Q)(Q^{-1} C3).
```

A D-exponent-0 left factor does not change D degree, so

```text
(1 - m0 x) Q^{-1} C3 D1 D3 = 0
```

if and only if `1 - m0 x = 0`.

Suppose `m0 x = 1`. Substitute the factorization of `x` and cancel the
unit `C1 Q` on the right:

```text
m0 Q^2 (I + Q) = Q^{-1} C1.
```

Let `φ` be the linear map on the D-exponent-0 algebra that sends a word
to `(-1)` raised to the number of letters of absolute value 1, and a
linear combination to the corresponding combination of those signs. Then
`φ(I + Q) = 1 + (-1) = 0` and `φ(Q^{-1} C1) = -1`.

This `φ` is an algebra homomorphism. Multiplication concatenates words
and then runs the installed reducer. Each reducer step preserves the
parity of the Q-letter count:

- cancelling an adjacent pair `C_i C_i` removes two letters that are not
  Q letters;
- a Q run of `n` letters `±1` has exponent sum `s ≡ n (mod 2)`, and the
  normal form of the exponent modulo 4 has letter count `0, 1, 2, 1` in
  the four residue classes, hence letter count congruent to `s` modulo 2.

Concatenation adds the counts, so `φ` multiplies on words and therefore
on the whole algebra. Apply it to the displayed equation:

```text
φ(m0 Q^2) φ(I + Q) = 0 ≠ -1 = φ(Q^{-1} C1).
```

No such `m0` exists. Therefore `1 - m0 x` is never zero, and neither is
the `D1 D3` summand of `S_x1`.

In particular, no fresh image of this form has `S_x1 = 0` while
`S_x0 = A`. Clearing the block means that zero column: together with
`S_y0 = S_y1 = 0` it would be the autonomous row `[A, 0, 0, 0]`. The
subfamily that also keeps `S_y0 = 0` is included. A later
D-exponent-0 left multiple `u` of such an image still has x0 block `u A`.
Since `A` is a monomial, `u A = A` forces `u = I`, so that later multiple
does not clear the summand either.

## The unique index that clears the D1 line

Right multiplication by `C1` is bijective because `C1^2 = I`. The `D1`
summand vanishes if and only if

```text
m0 = const C1 = Q^{-1} C1 Q - Q^{-1} C1,
```

and the y0 equation then forces `m1 = 0`. For this single index the four
products in `m0 x` are

```text
(-Q^{-1} C1)(Q^{-1} C1 Q) = -Q^{-1} C1 Q^{-1} C1 Q,
(-Q^{-1} C1)(Q^2 C1 Q)    = -Q^{-1} C1 Q^2 C1 Q,
(Q^{-1} C1 Q)(Q^{-1} C1 Q) = I,
(Q^{-1} C1 Q)(Q^2 C1 Q)    = Q^{-1} C1 Q^{-1} C1 Q.
```

The first and fourth cancel, so

```text
m0 x = I - Q^{-1} C1 Q^2 C1 Q,
m2 = Q^{-1} C1 Q^2 C1 Q.
```

Right multiplication by `Q^{-1} C3` cancels `Q Q^{-1}` and leaves the
fresh image

```text
S = m0 · bank 0 + m2 · bank 2,
S_x0 = A,  S_y0 = 0,  S_y1 = 0,
S_x1 = Q^{-1} C1 Q^2 C1 C3 D1 D3.
```

That x1 column is one monomial, not zero, and it is not the published
three-term block. The three multiplier monomials are the algebraic charge
of this near-miss. They do not clear the block. No scalar-field minimum
and no tape cost are claimed for them.

The constant index `m0 = 0`, `m1 = const`, `m2 = 1` is the predecessor's
image. Its x1 column is the original three monomials. Both indexes obey
the same nonvanishing statement.

## What is not proved

A multiplier with a nonzero D exponent can mix the `D1` and `D1 D3`
lines; this note does not classify it. Owner-mixing maps and any feedback
operator other than the published pair `(I, C1 Q^2)` are not classified.
The formal algebra does not impose `D^4 = I` or any further physical
relation. In a quotient that sends `Q^{-1} C1 Q^2 C1 C3` to zero while
keeping the displayed character argument's target nonzero, the image of
the identity `m0 x - 1 = m2` remains true, but this particular monomial
could vanish. No such quotient is proved here.

The result is not an autonomous decoder, not a new caller bill, and not
a change of the selected conditional κ.
