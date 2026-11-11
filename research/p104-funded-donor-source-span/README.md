# Fixed-boundary source obstruction for the funded donor fusion

**NO VERIFIED GAIN. Conditional κ change 0%.** On exact
[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314),
fusing role 1355's paid rank-one and rank-five MOVEs would remove
an intervening correction of `−2x863`. Neither fixed boundary
chart can supply that correction from existing cocharted rows.
The chart-739 bank is empty immediately before the split. The
chart-127 bank immediately after the split has 673 eligible rows,
all public and all with exact x863 coefficient zero.

The exact sparse replay and an independent scalar replay agree
on both cuts. The scalar replay checks the original and the literal
fused prefix. Their eligible banks are identical, while the missing
donor coefficient is −2. Arbitrary rational combinations in either
bank fail. Both cuts are resolved and the compatible paid saving
upper is zero. See [PROOF.md](PROOF.md).

[#7335](https://github.com/CrocSwap/integer-mult-bounds/pull/7335) tested compensating through other public recipients while
the chart-240 cache is live. This package instead fixes recipient
1355 and tests source rows on its two original boundary charts.
The protected roles 863, 1355 and 1568, both stationary captures,
the other fifteen corrections, and all other events stay fixed.
The complete directed price-only credit is about
0.16685897749686654 raw before this support exclusion.

## Evidence and reproduction

The comparator is exact #7314 head
`9d0119eb12fbd9fa534b48cd37b68e7099757b91`, certified κ
`0.003646221436446`, with exact
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
head `07a76c5e2738882c0cb322278e56f6cae3c9885d`.
The inherited premises are native all-columns, owned erasure,
compiler, precision/tape and analytic recovery. The package
authenticates the earlier comparator admission and reproduces
the bounded two-cut result.

From a clean checkout, use CPython 3.12 with assertions enabled.

```sh
python3.12 -I -B research/p104-funded-donor-source-span/replay.py
python3.12 -B scripts/research_package.py --package research/p104-funded-donor-source-span
```

Use `--out fresh-directory` to retain the four exact regenerated
receipts. The replay uses only committed files and the Python standard
library. It reconstructs the price before both support walks,
matches all 673 literal role IDs, and rejects changed price and
caller inputs. The first nullspace-first attempt hit its time cap
while processing the post bank. Its exact partial receipt is bundled
as a predecessor pin. The clean replay checks both banks and does
not depend on reproducing the original time cutoff.

## Open next questions

Can a changed cut or already-paid itinerary expose a source with an
x863 component? Pin and fully price one proposed change, then check
its exact signed source rows, ownership and restoration. Any literal
survivor needs the full physical, precision, tape, compiler and
caller replay. One additional paid rank-one position on the complete
caller erases the price-only gain.

## Credit

[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314)
supplies the funded correction and stationary captures.
[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
supplies the original direct MOVE.
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supplies the signed caller.
[#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298),
[#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319) and
[#7332](https://github.com/CrocSwap/integer-mult-bounds/pull/7332)
supply the directed tariff and price adapters. [#7335](https://github.com/CrocSwap/integer-mult-bounds/pull/7335) supplies
the identical fusion price and the distinct recipient-side result.
[#7308](https://github.com/CrocSwap/integer-mult-bounds/pull/7308)
supplies the exact sparse replay core and predecessor separating
dual methods. OpenAI Codex and subagents materially assisted.
