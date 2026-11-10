# One feedback edge outside the 8,281-policy family

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

No new κ is claimed. The selected frontier is unchanged.

## Named edge

The published feed in
[research/coded-active-feedback](../coded-active-feedback/PROOF.md) has two
feedback operators. The first is the identity on the saved first-FULL Y
output. The second is `C1 Q^2` on that query's response. The 8,281 policies
are the pairs of choices in which each operator is absent or a scalar in
`{-2,-1,-1/2,1/2,1,2}` times a reduced alternating `C1`/`C3` word of length
at most 7, and the second word is always followed by `Q^2`.

The named edge is the second operator `C1 Q`. The first operator stays the
published identity. No FULL, query, or other call is added. `C1 Q` is not
one of the 91 second-edge choices: those nonzero choices end in `Q^2`.

## The row being tested

After query 4, and before the last scalar operations, the second pair's Y
bank is the four-input row. Write `A = D1 Q^{-1}` and write `X1` for the
no-feedback value `Q^{-1} C3 D1 D3` of its third coefficient. The row is
autonomous when its four coefficients are exactly

```text
[A, 0, X1, 0].
```

That is the restored first-input job, no second-input coupling, the original
third-input job, and a zero fourth coefficient. It is one bank. It is not
the four diagonal target banks of the uncoded caller, and it is not a claim
that a later decoder separates those jobs.

## Direct test

Replay with the named edge gives the row

```text
x0 = Q^{-1} C1 Q^{-1} C1 D1
y0 = Q^{-1} C1 D1 - Q^{-1} C1 Q D1
x1 = Q^{-1} D1 - Q^{-1} C1 Q^{-1} C1 D1 + X1
y1 = 0.
```

The first coefficient is not `A`, and the second coefficient is not zero.
The row is not autonomous. The verifier recomputes this polynomial from
`search.replay`.

## Schedule identity

Let `S` be the saved response of query 2, and let `F2` be the second
feedback operator. In the suffix that `search.replay` runs after that
response, the part of the four-input row that depends on `S` is

```text
D3 S + Q^{-1} C3 D3 (-Q) C3 S + Q^{-1} F2 S.
```

The inherited relation `D3 C3 = Q^{-1} C3 Q D3`, together with `C3^2 = I`
and the fact that `D3` commutes with `Q`, reduces the first two summands:

```text
Q^{-1} C3 D3 (-Q) C3 = -Q^{-1} C3 Q D3 C3
                     = -Q^{-1} C3 Q Q^{-1} C3 Q D3
                     = -D3.
```

Their sum is zero. For every algebra element `F2` and every response `S`,

```text
query4:3 = B + Q^{-1} F2 S,
```

where `B` is the row obtained by dropping `S`. That row is
`[0, 0, X1, 0]`. The first feedback affects the row only through `S`.

`S = Q^{-1}(C1 X + F1 L)`, where `X` is the pair-0 X bank at query 2 and
`L` is the saved first-FULL Y bank. Both are fixed before either feedback.
The replayed trace has

```text
L = [Q^{-1} C1 D1, D1, -Q^{-1} C1 D1, 0].
```

In particular `L2 = -L0` and `L3 = 0`.

## No second-edge replacement works

Hold the first operator at the published identity. Then
`S = Q^{-1} Z` with `Z = C1 X + L`, and the reachable rows are
`B + P Z` as `P = Q^{-1} F2 Q^{-1}` runs through the algebra. The trace gives

```text
Z0 = Q^{-1} C1 D1,    Z1 = (I - Q) D1,    Z3 = 0.
```

`Z0` is one monomial of D-degree `(1, 0)`. Degrees add under multiplication,
so a component of `P` whose D-degree is not zero lands outside D-degree
`(1, 0)` and cannot cancel into `A`. On the D-free slice, `Q^{-1} C1` has
the two-sided inverse `C1 Q`. The equation `P Z0 = A` therefore has the one
solution

```text
P = Q^{-1} C1 Q,    F2 = Q P Q = C1 Q^2.
```

That operator is the published second edge. It lies in the 8,281-policy
family, and `P Z1 = P(I-Q)D1` is not zero. Every other second-edge element
fails to restore `A`. None makes the row autonomous.

This is an identity in the predecessor's algebra. It is not a census of the
91 second-edge choices, and it does not forbid an operator on a different
source.

## No first-edge replacement works

Hold the second operator at the published `C1 Q^2`. Then
`P = Q^{-1} C1 Q` is fixed, and the first operator contributes
`P F1 L`. Because `L2 = -L0`,

```text
(P F1 L)2 = -(P F1 L)0
```

for every algebra element `F1`. With `F1 = 0`, the row's third coefficient
is `X1 + Q^{-1} C1 Q C1 D1` and its first coefficient is zero. Reaching
`[A, 0, X1, 0]` would require the first-edge correction to add `A` on the
first coefficient and `-Q^{-1} C1 Q C1 D1` on the third. Those two required
values are not negatives of each other. No first-edge element works.

## What the two published edges can do together

The same identities give one pair that does clear the row: `F1 = Q` and
`F2 = C1 Q`. Both are outside the 8,281-policy family, so this changes two
edges. The replay equals `[A, 0, X1, 0]`, and the final image of that bank
agrees. The other three final banks are not the four uncoded target banks.
This pair is a boundary witness. It shows that the one-edge obstruction
depends on holding one published operator fixed. It is not a one-edge
result, not a complete caller, and not a new κ.

## What is not proved

No statement is made about a third source, a port-dependent map, an added
call, or a relation that is absent from this algebra. The two-edge witness
is one pair, not a classification of every pair. Native tape, precision,
compiler, and outer costs are not priced. The selected conditional κ is not
changed.
