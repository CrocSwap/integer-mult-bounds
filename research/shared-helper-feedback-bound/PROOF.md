# Post-call helper feedback stays inside the separated B/C bill

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

This is a scoped negative screen. It does not change κ, admit a caller, or
replay a native word. The selected record stays
`781451/250000000`.

## What is already proved

Ali Romman's capacity gate prices every whole B or C call whose helpers stay
out of the main computation. In that separated model the complete
target-minus-paid moment is strictly negative for every `0<t<1`. The proof
states the boundary it does not cross: shared or productive helper feedback
into the main computation needs a new bill. This note supplies that bill for
ordinary post-call feedback, and the bill does not improve.

The inherited data, copied here only as the objects being rechecked, are the
audited profiles and the capacity polynomial

```text
K(t) = 28 + 140*7^t + 84*8^t.
```

| Call | Paid rank counts | Independent helper rank counts |
| --- | --- | --- |
| B | 1:1956, 2:450, 3:403, 4:127, 5:28, 8:8 | 3:2, 4:26, 6:7, 7:47, 8:326 |
| C | 1:2011, 2:445, 3:427, 4:112, 5:12, 7:8 | 3:26, 4:2, 6:6, 7:48, 8:326 |

The four sign-cut charges of one call's main block are `0, 112, 224, 168`.

## Post-call model

After a call returns, its main rows and helper rows may be mixed by any
ordinary complex-linear operation. Those operations are invisible to the sign
characters, as in the capacity gate. A helper row is a coordinate Gaussian of
its audited rank, on its own field. Under a sign set `S` that row differs by
rank exactly 1 when `|S ∩ support|` is odd, and by rank 0 otherwise.

No helper is given a second life as an uncharged address permutation, a
conjugation, or an input that rewrites the native paid profile. Those
remain outside this screen. The paid profile stays the audited one.

## Rank budget

Write `D_main(S)` for the main-block rank distance and `D_H(S)` for the
helper-block rank distance. Any linear image of the combined output, including
an image that mixes main and helper rows, has rank distance at most
`D_main(S) + D_H(S)`.

On distinct fields, `D_H(S)` equals the number of helpers whose support meets
`S` oddly. Averaging independent axis flips of probability `p` therefore gives

```text
E[D_H] = sum_j h_p(r_j),
h_p(r) = (1 - (1-2p)^r) / 2.
```

The same average of `D_main` is `K`'s character form
`140 h_p(7) + 28 h_p(1) + 84 h_p(8)` per B or C call. A coordinate-Gaussian
target of rank `s` flips with probability `h_p(s)`, and the rank of the
output difference is at least the number of such targets that flip. Therefore

```text
sum_i h_p(s_i) <= E[D_main] + E[D_H].
```

The integral transform in the capacity gate is linear and sends `h_p(s)` to
`s^t`. Every family of coordinate-Gaussian jobs extracted from the combined
output satisfies

```text
sum_i s_i^t <= (L_B + L_C) K(t) + H(t) + sum_queries r^t
```

for `0<t<1`. Here `H(t)` is the moment of the audited helper ranks, whether or
not those rows are still labelled helpers. Consuming a helper into another
job spends its character budget; it does not create a second copy. Queries
cancel against their own charge exactly as before.

Subtracting the audited paid profiles leaves the same ceiling as the separated
theorem:

```text
F(t) <= -L_B Delta_B(t) - L_C Delta_C(t).
```

Both deltas are strictly positive for `0<t<1`, by the published mass split.
For B, paid minus helpers minus `K` has positive rank mass `4575` and negative
rank mass `4567`. Removing eight rank-1 units leaves equal masses `4567`, with
every positive rank at most 5 and every negative rank at least 6. For C the
two masses are already `4576`. For `g(r)=r^t`,

```text
g(5)/5 - g(6)/6 > 0
```

because `6 * 5^t > 5 * 6^t` rearranges to `(6/5)^{1-t} > 1`. Thus one or more
B or C calls still force `F(t) < 0`.

Keeping the helpers as independent jobs and also asking for one more flipping
target exceeds the joint row budget. On the central-axis character the main
cut is 112 and all 408 B helper rows flip, so the budget is 520. Retaining
those 408 jobs and filling the 112 main-cut rows already uses 520.

## What remains open

This does not price a native rewrite that deletes a paid Gaussian by reading
a helper inside the call. It does not price odd input gauges or address maps
outside the coordinate algebra. Unknown compiler, precision and outer costs
are not set to zero in order to continue; the post-call moment is already
negative with those costs omitted.
