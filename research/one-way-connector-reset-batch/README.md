# One reset makes the five-source connector batch exactly 63 queries

**Scoped exact result with a finite certificate and a written lower bound; no
new kappa.** Produced by Nick Petalas.

The universal five-source dirty connector costs exactly **74 complete queries**
for the batch of all 31 nonzero masks (Ross Richardson's #934 contract as
recorded in `research/universal-connector-boundary/`). This package adds one
operation and changes one boundary premise:

    Z:  z := 0        one complete query, and the connector is consumed
                      (its exit value is unconstrained).

Under that alphabet the exact optimum drops to **63 = 2^6 - 1**:

    1 reset  +  31 source calls  +  31 readouts.

The 31 source calls are a reflected-Gray walk of the 5-cube; each readout sits
at the vertex whose mask is its own output row, so every row is read exactly
once. The matching lower bound is `2^(n+1) - 1` for **every** `n >= 1`, so the
closed form is not a five-source accident. `verify.py` replays the schedule for
`n = 1..8`, and recomputes the complete optimum for `n = 2, 3` from every
visited vertex set.

```sh
python3.12 -B research/one-way-connector-reset-batch/verify.py
```

Expected:
`PASS_ONE_WAY_CONNECTOR_RESET exact_n1..8=3,7,15,31,63,127,255,511 optimum5=63 restored5=74 saving5=11 reset_free5_floor=71 nine_point_coverage=28 paths=70846 controls=6`

## What the number says

The saving is **11**, not the 31 that a "one readout per mask" comparison
suggests. The readout term `2(2^n - 1)` is the same under both contracts; what
changes is the source word. Restoration can afford a 12-call paired walk,
single readouts need a 31-vertex walk, and the difference is exactly
`T(n) - 1`:

| sources | restored (cited) | one-way (here) | saving |
|---|---:|---:|---:|
| 4 | 38 | 31 | 7 |
| 5 | 74 | 63 | 11 |

So connector restoration is worth exactly `T(n) - 1` queries at these arities,
and at least `2n - 1` in general. The dominant term in both contracts is the
`2^n - 1` readouts, which no boundary change in this alphabet removes.

The reset is not decoration. Keeping the connector one-way but forbidding the
reset still leaves every readout dirty, so every row needs an even read count
and the cheapest design costs at least `9 + 62 = 71`: `verify.py` exhausts all
70,846 simple eight-step paths from `0` in the 5-cube and finds pairwise
coverage at most 28 of 32, which rules out a nine-vertex difference basis and
forces a ninth source call. The reset, not the missing restoration, is what
buys the last eight queries.

## Interface and price ledger

Unchanged from the predecessor: sources `x_j`, connector `z`, outputs `y_i`,
arbitrary `F2`-linear possibly noncommuting maps `B_j`, `A_i`, read-only
sources, arbitrary dirty `z` and `y_i`, complete fixed-port calls, unit query
prices, all rows restored except the requested output sums. The single change
is the exit contract for `z` plus the one reset call. A caller that needs the
old connector value must save and restore it; that is a separate obligation and
is not priced here, so this is not a claim that every caller can discard a
shared connector for free.

## Claim type and evidence

Scoped written proof with an exact finite certificate:

* `PROOF.md` proves `2^(n+1) - 1` in two cases (`r >= 1` and `r = 0`), with the
  counting lemma that every extra prefix value is paid for by a source call.
* `verify.py` replays the literal schedule in a free noncommutative symbol
  model, checks the three counts, recomputes the complete optimum for `n = 2,3`,
  runs the complete eight-step path census for the reset-free floor, and applies
  six rejection controls.

It is not a kappa improvement, not a supplier admission, and not a complete
multiplication theorem. The 74 and 38 values and the restored source-call
counts `T(5) = 12`, `T(4) = 8` are cited from the predecessor; this package does
not replay or audit its 945-word census.

## Related open work

* `research/universal-connector-boundary/` (PR #934 lineage, five-source
  boundary): supplies the contract, the 945-pairing census, the restored exact
  74 and the four-source 38. Cited, not replayed.
* PR #3909 (open): a five-source arity-four source event priced as one dispatch
  plus four additions, whose schedules cost at least 149 units. That extension
  enlarges the source alphabet; this one enlarges the connector contract. The
  two results are complementary and neither implies the other.
* PR #2249 (open): a high-arity six-source toggle floor with `f(6) = 16`. It
  studies larger arities and larger alphabets; this package stays at unit
  weight source calls and changes only the exit contract.
* `research/two-connector-transfer-boundary/`: two connectors with a paid
  transfer, explicitly excluding connector resets. This package analyzes the
  excluded operation, at one connector.

## Open next questions

* **Does a save-and-restore wrapper keep the gain?** A caller that must return
  the old connector value needs one admitted clean row plus copy and restore
  calls. Price that wrapper exactly; the favourable region is narrow (below
  74 - 63 = 11 units at five sources), and no such row is assumed here.
* **Can a nonuniform tariff change the ranking?** The 63 count uses unit
  prices. With `c_Z`, `c_B` and `c_A` arbitrary positive prices, does the Gray
  schedule still dominate the paired design whenever `c_Z` is small, and what
  is the exact crossover?
* **What is the reset-free floor at general `n`?** At five sources the floor is
  71 by a complete eight-step path census. The analogous minimum difference
  basis size for `n >= 6` is open here, and the predecessor's six-source floor
  is a different quantity.
* **Does a bounded number of resets help a partial mask set?** For a sparse
  set of requested masks, resetting between blocks may beat one long walk; the
  exact tradeoff is not computed here.
