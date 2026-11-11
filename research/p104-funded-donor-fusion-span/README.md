# Fixed-chart span obstruction for the funded donor fusion

**NO VERIFIED GAIN. Conditional κ change 0%.** On exact
[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314), fusing
donor 1355's paid rank-one and rank-five MOVEs would require replacing
one intervening ADD. Every eligible replacement into an existing public
chart-240 role has zero coefficient at output coordinate 1109. The
omitted ADD contributes −8 there. Thus even arbitrary rational
combinations of the eligible responses cannot support the fusion.

The full rational replay exhausts 1,003 cut-role visits, including
39 distinct nonzero columns of rank 25. The independent scalar adjoint
replay covers 82 boundary cuts and 59 conservative recipient classes.
Both check the same exact coordinate separator. No cases remain
unresolved. See [PROOF.md](PROOF.md).

The candidate would replace emitted clocks 48182–48184 by the original
direct paid rank-six MOVE 739→127, retain the other fifteen corrections,
and leave both stationary caches and every other event fixed. Only
additive injections into existing unprotected public chart-240 roles
while the second cache is live are covered. The complete directed
optimistic one-edit credit is about 0.16685897749686654 raw.
The compatible upper after support is zero.

## Evidence and reproduction

The comparator is exact #7314 head
`9d0119eb12fbd9fa534b48cd37b68e7099757b91`, certified κ
`0.003646221436446), under the exact
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
signed 17-copy caller at `07a76c5e2738882c0cb322278e56f6cae3c9885d`.
The inherited premises are native all-columns, owned erasure, compiler,
precision/tape and analytic recovery. The package authenticates the
comparator admission and reproduces the scoped price and support result.

From a clean checkout use CPython 3.12 with assertions enabled.

```sh
python3.12 -I -B research/p104-funded-donor-fusion-span/replay.py
python3.12 -B scripts/research_package.py --package research/p104-funded-donor-fusion-span
```

Use `--out fresh-directory` for the three regenerated plaintext receipts.
The command uses committed files and the Python standard library.
It reconstructs and saves the complete price before either support replay,
checks both exact target responses and their shared separator, and rejects
a modified price and a modified caller.

## Open next questions

Could a changed cache chart or different paid itinerary supply the missing
coordinate at positive complete margin? Pin and preprice one changed
route, then test its exact signed response and adjoint, ownership and
restoration. New routing, setup, precision and tape charges all affect
the available margin. One additional rank-one paid position on the whole
signed caller already eliminates this price-only gain.

## Credit

[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314) supplies
the funded donor split and the two captures.
[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) supplies
the original direct transport.
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies
the signed caller. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298),
[#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319) and
[#7332](https://github.com/CrocSwap/integer-mult-bounds/pull/7332) supply
the directed tariff and price adapters.
[#7326](https://github.com/CrocSwap/integer-mult-bounds/pull/7326)
supplies a related abstract fusion tariff result.
[#7312](https://github.com/CrocSwap/integer-mult-bounds/pull/7312) and
[#7259](https://github.com/CrocSwap/integer-mult-bounds/pull/7259) study
older fixed-endpoint MOVE windows, and
[#7308](https://github.com/CrocSwap/integer-mult-bounds/pull/7308) studies
same-chart span at individual owned MOVE clocks. OpenAI Codex and
subagents materially assisted.
