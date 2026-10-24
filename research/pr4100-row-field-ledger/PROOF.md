# Short-field movement sits above the Strassen boundary row

Scoped substitution for one open question of
`research/pr4100-row-field-movement`. No new κ. #4100 is not accepted.
The selected record is unchanged.

## What is substituted

Lemma 3 of that package says that exposing one field of length `a ≥ 1`
and real volume `V` moves strictly fewer than

```text
8 · max(1, ceil(log2 a)) · V
```

records on the forward-plus-undo schedule. The #4100 boundary sentence
already charges

```text
O(V d W^(tau-1)/B polylog(p)),    tau = 45/16,
```

and the same paragraph's union movement is

```text
O(V d W/B polylog(p)).
```

PHASE-LAYOUT charges the layout itself as `O(log p)` times the boundary
volume, not a transpose of the long spectator field. The open question
was whether that count becomes the Strassen sentence only after the
exposed length is set equal to the carving parameters `W` and `B`.

## Pinned lengths

Two lengths are named. Neither is the equality `a = W` or `a = B`.

- FINE-PRIME.md and GAUSSIAN.md set `W = O(sqrt(p) polylog p)`. The
  boundary-row field in PHASE-LAYOUT is that polynomial-width row, so
  this reading has `a = O(p^{1/2} polylog p)`.
- If the exposed field is instead the whole carved line, CAPPED-SIGNOFF
  gives `|E_i| = O(L W/B polylog p + W polylog p)`, and GAUSSIAN.md sets
  `L = 2^{ceil(400 log2 p)}`. Then `a` is still `p^{O(1)}`.

In both readings `ceil(log2 a) = O(log p)`. Lemma 3 therefore multiplies
the volume it actually exposes by a polylogarithmic factor. It does not
change a `W` power.

The volume it exposes is the boundary volume. GAUSSIAN.md gives that set
density `O(W/B polylog(p))`, and FINE-PRIME.md §6 keeps the cost power
`epsilon - xi + (tau-1)/2` because the density is still `W/B`. UNION-SCHEDULE
records the same density as `mu = O((W/B) polylog p)`.

## Exponent comparison

FINE-PRIME.md §6–§7 uses one dictionary. A term

```text
O(V (d/B) W^alpha polylog p)
```

has cost power `epsilon - xi + alpha/2` and saving
`1 - epsilon + xi - alpha/2`, because the worst-case bandwidth in that
section satisfies `log_p W = 1/2`. That is why the printed union row
(`alpha = 1`) has saving `xi + 1/2 - epsilon`, and the printed Strassen
row (`alpha = tau - 1`) has saving `c + xi - epsilon` with
`c = (3 - tau)/2`.

Lemma 3, on the boundary volume, is the `alpha = 1` shape: the extra
`ceil(log2 a)` factor is inside the polylog already written on the union
sentence `O(V d W/B polylog(p))`. Its saving exceeds the Strassen saving by

```text
(xi + 1/2 - epsilon) - (c + xi - epsilon) = 1/2 - c = (tau - 2)/2.
```

The difference does not depend on `epsilon` or `xi`. For the stated
`tau = 45/16`, one has `c = 3/32` and

```text
1/2 - 3/32 = 13/32.
```

`W = O(sqrt(p) polylog p)` contributes `o(1)` beyond the printed `1/2`,
because `(log p)^k = p^{o(1)}`. A constant gap of `13/32` stays positive
for all large `p`. This note does not compute that finite threshold; an
explicit density constant would be needed for one. A separate movement
row would still save `13/32 - o(1)` more than the Strassen boundary row,
so it does not become the minimum. At the explicit §7 balance
(`s = 10^{-64}`, boundary saving `= epsilon q + s`), the printed-power
movement saving is that boundary saving plus `13/32`.

The same arithmetic gives the monomial comparison used by the big-O.
For every integer `W ≥ 1`,

```text
W^{29} ≥ W^{16},
```

so `W^{29/16} ≥ W`, and `W^{tau-1} ≥ W` at `tau = 45/16`. A movement of
shape `K V (d/B) W (log p)^k` is at most `K (log p)^k` times the monomial
inside `O(V d W^{tau-1}/B polylog p)`. The layout factor is absorbed by
the polylog of the boundary sentence. It is not necessary to set `a`
equal to `W` or to `B`.

For the other printed exponent `tau_eff = 2 + 10^{-64}`, the same
difference is `(tau_eff - 2)/2 = 5 · 10^{-65} > 0`, and `W^{tau_eff-1} ≥ W`
for every integer `W ≥ 1`. Absorption holds for that exponent too. Which
of the two exponents the ledger should state is a separate question.

## The density is necessary

If Lemma 3 were charged on the full tensor volume instead of the boundary
volume, the `W/B` factor would drop out and the saving would fall to
`1 - epsilon`. At the §7 parameters `epsilon = 9999999/10000000`, that
saving is strictly smaller than the headline `epsilon q`. The boundary
density is what keeps the movement off the binding row. The proof does
not rerun the carving program that produces the density; it uses the
density #4100 already writes.

## Not proved

This note does not prove the Strassen count, the seven-product circuit,
conditioning, the row gap, or the choice between `tau = 45/16` and
`tau_eff`. It does not replay the dyadic carving. It does not accept
#4100 or change the selected exponent. The `O` constants inside the
written density are not replaced by explicit integers.
