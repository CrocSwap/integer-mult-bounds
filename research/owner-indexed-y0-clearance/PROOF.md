# An owner-indexed reading clears y0 and keeps the restored x0 block

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

No new κ is claimed. The selected frontier is unchanged.

## Object

Use the published two-edge feed in
[research/coded-active-feedback](../coded-active-feedback/PROOF.md).
After the left endpoint the replay stores four banks. Bank 2 carries the
restored coefficient

```text
A = D1 Q^{-1}
```

together with the y0 coupling `B` and a three-term x1 block. Bank 1 is the
pure y0 monomial `G`. Banks 0 and 3 are the other endpoint banks. All four
are among the 39 saved banks. This note does not rerun the declared
alternating-family lock.

An owner index assigns to every owner `o` and every final bank `b` a
D-exponent-0 element `m_{o,b}` of the predecessor's `Q, C1, C3` algebra.
The reading on that owner is the left combination of the four banks. It
does not mix owners. The published operators are owner-scalar: the
predecessor's coupling rank is `112` times a frequency factor. An arbitrary
input supported on one owner therefore forces the same operator equation
on that owner. Negative D exponents, owner-mixing maps, and a new feedback
edge are outside this statement.

## Normal forms

The pinned replay gives the D-exponent-0 quotients by the unit `A`

```text
x = X0 A^{-1} = Q^{-1} C1 Q + Q^2 C1 Q
g = G A^{-1} = C1 Q^2
b = B A^{-1} = Q^{-1} C1 Q^2 - Q^{-1} C1 Q^{-1}
```

with `X0` the x0 block of bank 0. Write `s = Q^{-1} C1 Q^2` and
`t = Q^{-1} C1 Q^{-1}`, so `b = s - t`. The four products are

```text
(Q^{-1} C1 Q) s = Q
(Q^{-1} C1 Q) t = Q^2
(Q^2 C1 Q) s = 1
(Q^2 C1 Q) t = Q
```

using `Q^4 = 1` and `C1^2 = 1`. Hence

```text
x b = (Q - Q^2) + (1 - Q) = 1 - Q^2.
```

Also `C1 g = Q^2`, so `x b - 1 = -C1 g` and `(x b - 1) g^{-1} = -C1`.
The inverse is `g^{-1} = Q^2 C1`, and

```text
s g^{-1} = Q^{-1},
t g^{-1} = Q^{-1} C1 Q C1,
b g^{-1} = Q^{-1} - Q^{-1} C1 Q C1.
```

The constant defect is therefore

```text
const = -b g^{-1} = -Q^{-1} + Q^{-1} C1 Q C1
       = Q^{-1} (C1 Q C1 - I).
```

Both words are outside the short declared family of alternating `C1`/`C3`
words, with or without a right `Q^2`. The first word is not an even-Q word.
Let `E` be the span of normal forms whose every Q run has even exponent.
Products stay in `E`: adjacent even exponents add to an even exponent, and
reduction by `Q^4` subtracts a multiple of 4. `C1` lies in `E`, while
`const` does not, so `m0` and `m1` are never both in `E`.

Bank 3's x0 and y0 columns are single monomials on D-exponent `(1, 1)`.
Left multiplication by a D-exponent-0 element preserves that line. The
target `A` has no D3 component, and a monomial has an inverse in this
algebra, so the bank-3 coefficient in any solution is 0.

## The identity

For an arbitrary D-exponent-0 element `m0`, set

```text
m3 = 0
m2 = 1 - m0 x
m1 = const - m0 C1.
```

Right-multiplying the x0 and y0 equations by `A^{-1}` reduces them to
`m0 x + m2 = 1` and `m0 + m1 g + m2 b = 0`. The second is the calculation
above. Equivalently, every solution satisfies

```text
m1 + m0 C1 = const.
```

The two coefficients in `const` are `±1`. No choice of `m0`, and no choice
of owner, changes either coefficient in this combination. Choosing
`m0 = -Q^{-1} C1` moves the pure `Q^{-1}` term from `m1` into `m0`; the
combination is still `const`. This is an identity in the predecessor's
algebra, not a search over a bounded ansatz. In a quotient that identifies
further words, the image of this identity remains true, but a collapsed
word could make the same element look cheaper. No such quotient is proved
here.

## The constant-index map

Use the same multipliers on every owner:

```text
m0 = 0,  m1 = const,  m2 = 1,  m3 = 0.
```

Write them into a fresh image

```text
S = bank 2 + const · bank 1.
```

Bank 1 has zero x0, x1, and y1, so

```text
S_x0 = A,  S_y0 = B + const · G = 0,  S_y1 = 0,
```

and `S_x1` equals bank 2's x1 block. That block is the published coefficient

```text
(Q^{-1} C1 Q C1 - Q^{-1}) D1 + Q^{-1} C3 D1 D3,
```

three monomials, none of them removed. The four stored endpoint banks are
only read. They stay equal to the replayed left endpoint.

## Charge

The algebraic charge is the pair of monomials in `const`, with coefficients
`-1` and `+1`, on every owner. The field ledger below is one circuit for
the constant-index choice. It is an upper bound for that circuit under the
predecessor's published units. It is not a minimum circuit cost, not a
tape proof, and not a new κ.

The predecessor charges one F-transpose at 896 scalar ADDs, 224 monomial
passes and 16 mode CLEARs; one 112-field addition at 112 ADDs; one capture
at 112 COPYs; and one uniform `Q^2` at 112 monomial passes. This ledger
uses those units. Each of `Q` and `Q^{-1}` is charged as one uniform
monomial pass, the same unit as `Q^2`, because each is one monomial per
field. If `Q^{-1}` must be expanded as three factors, the monomial count
rises by 224 and this table is only a lower figure for that alternative.
That expansion is not established here.

The factored circuit, overwriting scratch and keeping both sources stored,
is:

| Step | Inherited unit | Count |
| --- | --- | ---: |
| Copy bank 1 into `U` | 112 COPYs | 1 |
| `V ← C1 U` | one F-transpose | 1 |
| `V ← Q V` | 112 monomial passes | 1 |
| `V ← C1 V` | one F-transpose | 1 |
| `V ← V - U` | 112 scalar ADDs | 1 |
| `V ← Q^{-1} V` | 112 monomial passes | 1 |
| Copy bank 2 into `S` | 112 COPYs | 1 |
| `S ← S + V` | 112 scalar ADDs | 1 |

The totals are 2016 scalar ADDs, 672 monomial passes, 32 mode CLEARs,
224 COPYs, 336 extra fields, and the predecessor's 8 mode fields reused.
No Gaussian child is added. Banks 0, 1, 2, and 3 are not written.

## What is not proved

The x1 block of `S` is unpaid. Owner-mixing maps, multipliers with a
nonzero D exponent, and a feedback edge outside the published two-edge
feed are not classified. The formal algebra is the predecessor's
sufficient identity model. Native tape, precision, compiler, and outer
costs are not repriced. The selected conditional κ is not changed.
