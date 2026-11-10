# The omitted relation D1^4 = I does not kill the residual x1 word

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

No new κ is claimed. The selected frontier stays
`781451/250000000`.

Evidence class: **proof** that one named central relation does not send
one explicit monomial to zero. The quotient is the predecessor group
algebra modulo the principal ideal `(D1^4 - 1)`. The check reduces that
one word. It is not an enumeration of words, not a search, and not a
theorem about every physical quotient at once.

## The named relation

The predecessor algebra is the one installed by
`research/coded-active-feedback/search.py`: the rational group algebra
of the free product `C4(Q) * C2(C1) * C2(C3)`, with formal integer D
exponents, and with `D_i` conjugating only `C_i` by `Q^{-1}`. That is
`Q^4 = C1^2 = C3^2 = I` together with the inherited D conjugation rule
from `research/coded-native-caller/gauge.py`. In that algebra `D1^4` is
the normal form with empty word and degree `(4, 0)`, which is not `I`.

The relation imposed here is the single extra equation

```text
D1^4 = I.
```

`research/coded-active-feedback/PROOF.md` names this law as omitted:
the formal search adds `C1^2 = C3^2 = I` and `Q^4 = I`, keeps fresh D
exponents as integers, and records that `D^4 = I` is a physical source
relation not imposed there. `D1` is the stage-1 fresh eight-axis
Gaussian in that note. The same note's opening conventions identify
those stage operators with the fresh Gaussians.

The displayed one-axis factor of that Gaussian law is the normalized
matrix in `research/moving-stage-restoration-tariff/PROOF.md`,

```text
A = [[a, b], [b, a]],  a = (1+i)/2,  b = (1-i)/2.
```

Clearing the denominator, `2A = [[1+i, 1-i], [1-i, 1+i]]`. Exact
arithmetic in `Z[i]` gives `(2A)^2 = 4 X` and `(2A)^4 = 16 I`, where
`X = [[0, 1], [1, 0]]`. Therefore `A^2 = X` and `A^4 = I`, which is the
sentence `D^2 = X` and `D^4 = I` in that note. The tariff applies the
same normalized block Gaussian at width 8 to the eight-axis blocks.
`research/coded-native-caller/PHYSICAL.md` writes each stage factor as
a coordinate C gate and the fresh stage Gaussian as the product of the
eight noncentral gates. This package does not replay that native
product. The equation imposed on the residual is the one formal
equation `D1^4 = I`. `D3^4 = I` is not imposed.

## Reduction of the residual word

Rightmost factors apply first in the engine, and the product is written
left to right. The residual word of open question 2 in PR #7033 is

```text
Q^{-1} C1 Q^2 C1 C3 D1 D3.
```

The Q letters in the middle are adjacent and already form the normal
syllable `Q^2`. The leading `Q^{-1}` is separated from them by `C1`, so
the free-product reducer does not combine those runs. The two `C1`
letters are separated by `Q^2`, so they do not cancel. `C3` remains at
the right of the coefficient. The two D factors contribute degree
`(1, 1)` and an empty word. The engine product is the single basis
element

```text
word (-1, 2, 1, 1, 2, 3), degree (1, 1), coefficient 1.
```

`D1^4` commutes with each generator `Q, C1, C3, D1, D3`. It therefore
commutes with their inverses and with every word. On this monomial the
commutation is a pure shift: left or right multiplication by `D1^4`
replaces the basis element by the same word at degree `(5, 1)`. The
action of degree `(4, 0)` inserts `Q^{-4}` and `Q^4` around each `C1`,
and those runs are empty because `Q^4 = I`. No coefficient is cancelled.

The quotient by the central element `D1^4` identifies a normal form
`(w, (e1, e3))` with `(w, (e1 + 4k, e3))` and with nothing else. Coset
sums of coefficients are the quotient coordinates. The residual has one
term, already at D1 exponent `1`, so its coset sum is `1` at

```text
((-1, 2, 1, 1, 2, 3), (1, 1)).
```

That coordinate is not zero. The same quotient sends `D1^4 - I` to zero,
and it sends `D1^5` and `D1^{-3}` to the class of `D1`, which is not
the class of `I`.

## Q^{-1} C1 stays nonzero and distinct

The comparison element is the single basis element

```text
Q^{-1} C1 = word (-1, 2), degree (0, 0), coefficient 1.
```

Its D1 exponent is `0`, so the coset of `D1^4` does not mix it with any
other degree-`(0, 0)` word. The quotient coordinate is `1` at
`((-1, 2), (0, 0))`. That is not the residual class. The Q-letter parity
character, the sign of the number of letters of absolute value `1`,
still sends this representative to `-1`.

Thus `D1^4 = I` does not send the residual word to zero and does not
collapse `Q^{-1} C1`.

## Separating representation

Let the basis of `C^8` be indexed by `q + 2 d1 + 4 d3` with each bit in
`{0, 1}`. Define

```text
Q  = diag(i^q),   D1 = diag(i^{d1}),   D3 = diag(i^{d3}),
C1 = swap of bits q and d1,            C3 = swap of bits q and d3.
```

These matrices are monomial, hence invertible. They satisfy `Q^4 = I`,
`C1^2 = C3^2 = I`, commutation of each `D` with `Q` and with each other,
commutation of `D1` with `C3` and of `D3` with `C1`, the two conjugation
identities `D_s C_s = Q^{-1} C_s Q D_s`, and `D1^4 = I`. They also
satisfy the further equations `D3^4 = I` and `(C1 C3)^3 = I`. Those
further equations are relations of this representation only. They are
not imposed on the formal quotient above.

The representation is therefore a ring homomorphism out of the quotient
by `D1^4 - I` into 8 by 8 matrices over the Gaussian integers. The image
of the residual is an invertible monomial matrix, and the image of
`Q^{-1} C1` is a different invertible monomial matrix. A homomorphism
that sends an element to a nonzero matrix witnesses that the element
was nonzero, and unequal images witness that the two elements were not
equal.

`C1` does not commute with `Q` in this representation, so the witness
does not force the predecessor noncommutation `[C1, Q] = 0`.

## What this does not claim

The quotient does not produce an autonomous row. No owner-indexed
multiplier is exhibited, and the four published banks are not reread.
A later quotient that did kill the residual would still need its own
multiplier before anyone could call the result an autonomous caller.

`D3^4 = I` is a different equation and is not part of the quotient.
Nonzero D exponents, owner mixing, and any feedback edge other than the
published pair stay outside. The result is not a change of the selected
conditional κ.
