# The declared decoder keeps one active-feedback coupling monomial

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

No new κ is claimed. The selected frontier is unchanged.

## Object

Use the published two-edge feed in
[research/coded-active-feedback](../coded-active-feedback/PROOF.md):
save the first FULL output `h`, add it to the second query, and add
`C1 Q^2` times that response to the final query. In the predecessor's
group algebra the post-query4 bank, and its final image, has x0
coefficient

```text
A = D1 Q^{-1}
```

and y0 coefficient

```text
B = Q^{-1} C1 Q (I - Q) D1.
```

The same algebra gives `B = K A` with
`K = Q^{-1} C1 Q^2 (I - Q)`. Both `K` and `B` are nonzero. This identity
is the predecessor's left-associate relation; the new statement is about
the decoder that is allowed to act on every saved bank.

The declared decoder is the infinite family already named by the
predecessor search: every reduced alternating `C1`/`C3` word, and the
same words multiplied on the right by `Q^2`. Rational sums of those
monomials are included. Odd powers of `Q`, port-dependent maps and a
different feedback edge are not.

## Witness

Write α for the basis key `Q^{-1}` on the `D1` line, word `(-1,)` with
D-exponent `(1, 0)`. Write β for the basis key word `(-1, 2, 1)` with the
same D-exponent. The restored coefficient `A` is exactly the α term, and
the coupling `B` contains the β term with coefficient `+1`.

For a monomial control `W` of D-exponent 0, left multiplication acts on
these keys by the inverse monomial. Therefore a rational decoder output
has equal α coefficient in its x0 block and β coefficient in its y0
block whenever every saved bank does, after pullback by every declared
`W`.

## Finite support

Replay of the published feed produces 39 saved banks. On input columns
x0 and y0, the only words that occur on the `D1` line are

```text
(), (-1,), (-1, 2), (2, 1), (-1, 2, 1), (1, 1, 2), (-1, 2, 1, 1).
```

The longest has length 4.

For the identity control, the α and β coefficients are equal on every
bank: both are `1` on `response4`, `query4:3` and final bank `left:2`,
and both are `0` elsewhere. Those three banks are the published restored
row and its final image, together with the paid response that creates it.

For a nonempty alternating code word `w` of C-length `n`, the inverse
does not shorten `w`, and multiplication by α appends `Q^{-1}` at a
code letter, which does not cancel. The α preimage therefore has length
`n + 1`. For `n ≥ 4` that length is at least 5, so the preimage misses
the support. The β preimage is longer. Both pulled-back coefficients
are 0.

For the right-`Q^2` extension of a nonempty `w`, the same junction count
gives α-preimage length `n + 3`. For `n ≥ 2` the length is at least 5,
again outside the support. The empty word's right-`Q^2` extension pulls
α back to word `(1,)` and β back to `(1, 2, 1)`, neither of which is in
the support.

The remaining controls are the nonempty alternating words of C-length
1, 2 and 3, with and without right `Q^2`. There are finitely many. Each
preimage misses the seven-word support, so both coefficients are 0.
The verifier enumerates them.

## Conclusion

Every declared decoder output, of any code-word length and any rational
coefficients, has equal α coefficient on x0 and β coefficient on y0.
The autonomous target that keeps `A` and deletes the y0 block has those
coefficients `1` and `0`. It is not attained.

In particular the published coupling cannot be removed by this decoder
while the restored coefficient is kept: the β term of `B` would have to
stay equal to 1. This uses every saved bank, including the final four,
not only the pre-response4 observations in the predecessor's 8,281-policy
search.

The obstruction is grammatical. Final bank 1 is a pure y0 monomial.
Left multiplication by the two-term element `B` times that monomial's
inverse clears y0 on the restored bank and leaves x0 equal to `A`. Both
words of that correction contain an odd power of `Q`, so the correction
is not a declared code word and is not priced as a free Pauli. No claim
is made that an odd-`Q` or port-dependent map has a favorable bill.

## What is not proved

The x1 block of the restored bank is untouched. No new feedback edge is
tested. The formal algebra is the predecessor's sufficient identity
model, not a claim that every extra physical relation is absent. Native
tape, precision, compiler and outer costs are not repriced. The selected
conditional κ is not changed.
