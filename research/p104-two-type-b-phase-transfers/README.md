# Two simultaneous Type B phase transfers at fixed clocks

**NO VERIFIED GAIN. Conditional κ change 0%.** On the exact signed #7113 caller, all 1,950 ways to move two negative central phases from original singleton Type B idles to two larger even idles change the endpoint at `q = −1` with unit body values. The exact rational and modular replays agree on every key. Zero cases survived or remained unresolved.

Choose two of four original `IDLE_ODD` clocks and two of 26 `IDLE_ONE` clocks with body-mask sizes 2–8. Demote both former signs and promote both latter signs. Keep every role, clock, mask, all 17 J blocks and every other event fixed. Each 2+2 choice specifies one word. Overlapping masks are included and the two ways to pair donors with receivers give the same four edits. The result is a necessary endpoint exclusion under this exact scope. [Proof](PROOF.md)

## Complete price before support

The comparison uses independently reproduced [#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314) at `9d0119eb12fbd9fa534b48cd37b68e7099757b91`, κ = `0.003646221436446`, with the literal [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The old complete invoice has 110,536 paid and 22,461 productive positions across 17 native copies, signed rank surplus 1,424 and zero empty-root credit. The signed rank redistribution preserves both position counts, both rank masses and the productive histogram. The directed price is evaluated at the upper endpoint `0.0036462214364462343366888845568981` of the certified raw complex crossing.

The upper bound over all eligible two-transfer keys, with extra work free, is about **0.11648618439752845 raw units**. Its exact upper is `72803865248455278947107190998539661213280058633 / 625000000000000000000000000000000000000000000000`. The two size-eight receivers at clocks 2324 and 2337 attain the highest priced signature. Every price-only interval has positive margin, but charging one extra rank-one paid position makes every margin negative. The endpoint obstruction makes the compatible saving upper **zero**.

## Replay

From a clean checkout, use CPython 3.12 with assertions and the standard library.

```sh
python3.12 -I -B research/p104-two-type-b-phase-transfers/replay.py
```

The standalone replay runs without Git, network, or prior temporary state. It authenticates inputs by package-relative path and the exact comparator admission closure. It saves the complete price in fresh scratch before decoding the caller, then verifies all modular and independent exact keys. It regenerates four frozen plaintext SHA-256 receipts. Add `--out fresh-receipts` to retain `PRICE.json`, `BODY1.json`, `EXACT.json` and `COMPARE.json`. The exact receipt records the first mismatching input column, output row and nonzero rational difference for each key. Cancellation controls cover two failing pairs whose joint edit cancels, different orthogonal bases and a corrupted reflection. Stale price and mutated caller inputs are rejected. [Source pins](PROVENANCE.json) · [Receipt hashes](receipts/SHA256.json)

The primary run is capped at 25 seconds and the independent run at 30 seconds. Both exhausted their scope. No nonunit-body, changed native, ownership, precision or tape replay was needed for this exclusion. The inherited five framework assumptions and the selected result remain separate from the finite gate. [Comparator admission](admission/ADMITTED.json)

## Credit

#7113 supplied the literal signed caller and #7314 supplied the complete comparable invoice. #7298 supplied directed arithmetic. #7317 excluded single transfers and supplied the predecessor price and stock; #7315 supplied the signed gate decoder. #7309 treated pure demotions and #7296 treated one merged child. #3204 supplied an older four-site rigidity precedent under a different schedule and independent-axis contract; #1324 supplied an older constructive simultaneous axis reassignment. OpenAI Codex and subagents materially assisted. [Notices](NOTICE)

## Open next questions

Can three or four simultaneous transfers preserve the endpoint, or can a changed surrounding interval support a funded transfer? Start with a complete directed invoice and check the full signed arbitrary-input endpoint of one changed scope. A survivor needs uniform signed multi-stage child binding, dirty-data ownership and restoration, and all setup, routing, precision and tape costs charged.
