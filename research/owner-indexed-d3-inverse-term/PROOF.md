# A D-exponent (0,-1) correction leaves the sharp x1 residual

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

No new κ is claimed. The selected frontier is unchanged.

Evidence class: **proof** in the predecessor's formal algebra, under the
hypotheses below. The coefficient `u0` ranges over an infinite-dimensional
space. This is not an enumeration of words, not a bounded search, and not
a theorem about every quotient or every nonzero D exponent.

## Object

Use the published two-edge feed in
[research/coded-active-feedback](../coded-active-feedback/PROOF.md),
replayed by `search.replay(one, C1 Q^2)`. The four final banks and the
sharp index are the ones recorded by open PR #7033 in
`research/owner-indexed-x1-obstruction`: the D-exponent-0 multipliers

```text
m0 = const C1 = -Q^{-1} C1 + Q^{-1} C1 Q,
m1 = 0,
m2 = Q^{-1} C1 Q^2 C1 Q,
m3 = 0,
```

with `const = -Q^{-1} + Q^{-1} C1 Q C1` and

```text
x = Q^2 (I + Q) C1 Q.
```

Their fresh image has `x0 = A = Q^{-1} D1`, `y0 = 0`, `y1 = 0`, and

```text
x1 = R = Q^{-1} C1 Q^2 C1 C3 D1 D3.
```

`verify.py` recomputes this image from the replay. It does not import the
unmerged package. The D-exponent-0 nonvanishing argument of #7033 is not
repeated.

An owner index reads the four stored banks. It does not mix owners and
does not write the banks. A D-exponent `(0,-1)` correction of the sharp
index is a fresh image

```text
S = sum_b (sharp_b + u_b D3^{-1}) · bank b,
```

where each `u_b` is an arbitrary element of D exponent `(0,0)`. One bank
means the other three coefficients are zero. Letters are `1 = Q`,
`-1 = Q^{-1}`, `2 = C1`, and `3 = C3`. The algebra is `search.algebra()`:
the free product `C4(Q) * C2(C1) * C2(C3)`, formal D exponents, and `D_i`
conjugating only `C_i` by `Q^{-1}`. Distinct D exponents are basis labels
in this algebra. No relation `D^4 = I` is imposed.

## The four transported columns

Left multiplication by `D3^{-1}` adds `(0,-1)` to every degree and
replaces each `C3` by `Q C3 Q^{-1}`. Letters `Q` and `C1` are fixed.
`verify.py` compares the resulting sixteen columns with the replay.
They are

```text
bank 0, degree (1,-1):
  x0 = Q^{-1} C1 + Q^2 C1
  y0 = Q^{-1}
  x1 = -Q^2 C1
  y1 = 0
bank 1, degree (1,-1):
  y0 = C1 Q
  x0 = x1 = y1 = 0
bank 2:
  x0 = Q^{-1}                         degree (1,-1)
  y0 = Q^{-1} C1 Q - Q^{-1} C1 Q^2    degree (1,-1)
  x1 = -Q^{-1} + Q^{-1} C1 Q C1       degree (1,-1)
       + C3 Q^{-1}                    degree (1,0)
  y1 = 0
bank 3, degree (1,0):
  x0 = Q C3 Q^2 C1
  y0 = Q C3 Q^{-1}
  x1 = -I + Q C3 Q^{-1} C1 - Q C3 Q^2 C1
  y1 = Q C3
```

Bank 3's `x0` word is the one place a `C3` is rewritten. The raw
conjugate of `C3 Q^{-1} C1` is `Q C3 Q^{-1} Q^{-1} C1`, and the Q-run
`Q^{-2}` normalizes to `Q^2`, giving `Q C3 Q^2 C1`.

Every x1 transport misses D degree `(1,1)`. A D-exponent-0 left factor
adds degree `(0,0)`, so it preserves those degrees. The sharp x1 column
is exactly `R`, at degree `(1,1)`. Therefore, for every coefficient
tuple `(u0,u1,u2,u3)`,

```text
S_x1 = R + (terms of D degree other than (1,1)).
```

The coefficient of `Q^{-1} C1 Q^2 C1 C3 D1 D3` stays `1`. In particular
`S_x1` is not zero. This is the whole four-bank family, not a sample of
`u_b`.

## Right multiplication by a monomial is injective

The reducer is the left-to-right stack in `search.reduce_word`. Its stack
after reading a word is the reduced word. A reduced word is alternating
canonical syllables: a Q syllable is empty, `Q`, `Q^2`, or `Q^{-1}`, and a
C syllable is a single `C1` or `C3` different from the previous letter.
Reading that word again pushes the same syllables, so reduction is
idempotent, and

```text
reduce(reduce(A) + B) = reduce(A + B)
```

for every word pair. The four-syllable normal forms are a control for this
fold, not the proof.

On normal words, right multiplication by `Q^r` adds `r` to the final
Q exponent modulo 4 and leaves the preceding prefix fixed. Addition
modulo 4 is bijective, so every Q power, including `Q^{-1}` and `Q^2`,
is bijective. Right multiplication by `C_i` is the involution that
deletes a final `C_i` or appends one; a normal word does not end with
two copies of `C_i`, so the second application restores the word.

Right multiplication by a normal word is the composition of its syllable
maps, hence bijective. For a one-term element `g` of nonzero coefficient,
a D-exponent-0 element `u` satisfies `u g = 0` only when `u = 0`: degree
0 does not conjugate the word of `g`, the product has one output term per
term of `u`, and those words are distinct.

The same fold gives the association used below. For D-exponent-0 elements
`u,z` and a monomial `g`,

```text
(u z) g = u (z g),
```

because both sides are bilinear and, on monomials, both word maps reduce
the concatenated letters.

## The boundary family

Write `T_b` for the column transports above. Direct expansion gives

```text
x T_{2,x0} = (Q^{-1} + Q^2) C1 Q · Q^{-1}
           = (Q^{-1} + Q^2) C1
           = T_{0,x0}
```

at degree `(1,-1)`. For the y0 columns, write

```text
A = Q^{-1} C1 Q,  B = Q^2 C1 Q,  S = Q^{-1} C1 Q^2,
```

so `x = A + B` and `T_{2,y0} = A - S`. Then `A^2 = I`, `B A = Q^{-1}`,
`A S = Q`, and `B S = I`, hence

```text
x T_{2,y0} = (I + Q^{-1}) - (I + Q) = Q^{-1} - Q.
```

Also `C1 T_{1,y0} = C1 (C1 Q) = Q`, so

```text
C1 T_{1,y0} + x T_{2,y0} = Q^{-1} = T_{0,y0}.
```

Both `x` and `C1` use only `Q` and `C1`, so each commutes with
`D3^{-1}`. The sharp image already has `x0 = A` and `y0 = 0`, and the
transports of banks 0, 1, and 2 lie in degree `(1,-1)` on those two
columns. Bank 3's x0 and y0 transports lie in degree `(1,0)` and are the
monomial units `Q C3 Q^2 C1` and `Q C3 Q^{-1}`. The degree-`(1,0)` part
of `S_y0` is therefore `u3` times a unit, and the degree-`(1,0)` part of
`S_x0` is `A` plus `u3` times a unit. Either forces

```text
u3 = 0.
```

The degree-`(1,-1)` equations are then

```text
(u0 x + u2) T_{2,x0} = 0,
(u0 C1 + u1) T_{1,y0} = 0.
```

`T_{2,x0} = Q^{-1}` and `T_{1,y0} = C1 Q` are monomial units, so

```text
u2 = -u0 x,  u1 = -u0 C1.
```

Conversely, every `u0` with these coefficients keeps `x0 = A`, `y0 = 0`,
and `y1 = 0`: banks 0, 1, and 2 have zero y1 transport, and `u3 = 0`.
The x1 column of this family is `S_x1 = R + u0 Δ` with
`Δ = T_{0,x1} - x T_{2,x1}`. For the witness `u0 = I`, so `u2 = -x`,
the products are:

```text
(-x)(-Q^{-1}) = Q^{-1} C1 + Q^2 C1,
(-x)(Q^{-1} C1 Q C1) = -C1 - Q^{-1} C1,
T_{0,x1} = -Q^2 C1.
```

The degree-`(1,-1)` sum is `-C1`. The only degree-`(1,0)` source in
`T_{2,x1}` is `C3 Q^{-1}`, and

```text
(-x)(C3 Q^{-1}) = -Q^{-1} C1 Q C3 Q^{-1} - Q^2 C1 Q C3 Q^{-1}.
```

Thus

```text
Δ = -C1 D1 D3^{-1}
    - Q^{-1} C1 Q C3 Q^{-1} D1
    - Q^2 C1 Q C3 Q^{-1} D1.
```

`Δ` has no degree-`(1,1)` term, so `R` remains with coefficient 1 for
every `u0`. One bank is the special case in which two of `u0,u1,u2`
vanish. Since `x` and `C1` are nonzero, that forces `u0 = 0`.

## The witness and its charge

Take `u0 = I`. Then `u1 = -C1` and

```text
u2 = -x = -Q^{-1} C1 Q - Q^2 C1 Q.
```

The new multiplier monomials, beyond the three sharp monomials, are

```text
D3^{-1}                         on bank 0,
-C1 D3^{-1}                     on bank 1,
-Q^{-1} C1 Q D3^{-1}            on bank 2,
-Q^2 C1 Q D3^{-1}               on bank 2.
```

The fresh x1 column is `R + Δ`: the residual monomial, unchanged, plus
the three monomials of `Δ`. The algebraic charge of this near-miss is
the four new multiplier monomials together with those three image
monomials. None of them removes `R`. No scalar-field minimum and no tape
cost are claimed. The four stored banks are only read.

For a general `u0`, the same charge is the support of `u0`, of `-u0 C1`,
and of `-u0 x`, together with the support of `u0 Δ` in the image. Every
such support leaves the residual monomial in place.

## One homogeneous term on one bank

The single-bank case above is degree `(0,-1)`. The same gate applies to
every other single degree. Each bank has a monomial column among x0 and
y0: bank 0 and bank 1 use y0, and bank 2 and bank 3 use x0. For any D
exponent `d`, `D^d` times that monomial is one monomial, because the
product of two one-term elements is one term. Right multiplication by
that monomial is injective on D-exponent-0 elements by the syllable
argument. Adding only `u D^d` on that bank therefore keeps `x0 = A` and
`y0 = 0` exactly when `u = 0`, and the zero coefficient leaves `R`.

This does not classify two banks at a degree other than `(0,-1)`.

## What is not proved

A D exponent other than `(0,-1)`, spread across two or more banks, can
meet degree `(1,1)`. The same closed form `u1 = -u0 C1`, `u2 = -u0 x`,
`u3 = 0` keeps the boundary when `D3^{-1}` is replaced by `D3`, because
`x` and `C1` commute with every power of `D3`. For `u0 = I` that positive
power changes the degree-`(1,1)` line: `verify.py` checks that the line
properly contains `R` and that x1 is still not zero. No coefficient is
solved there.

Owner-mixing maps, a feedback edge other than `(I, C1 Q^2)`, and a
physical relation that identifies distinct D exponents are outside this
statement. In a quotient that moves degree `(1,1)` onto a shifted degree,
the formal coefficient 1 need not remain visible. No such quotient is
proved here. The result is not an autonomous decoder, not a new caller
bill, and not a change of the selected conditional κ.
