# Fixed endpoint span bound for one owned two-write aggregate

**NO VERIFIED GAIN.** Exact Δκ = 0 relative to independently reproduced conditional κ = `0.00364665195644` on #7334 `aaeec8c0acf01e99a5f331ef363a698d9c084ace` with signed #7113 `07a76c5e2738882c0cb322278e56f6cae3c9885d`. [Comparator #7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) · [Signed caller #7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)

Owner 1531 receives exactly two unobserved signed writes between its paid moves at 41996 and 44242. Moving their sum to either old endpoint would allow a direct rank-five route if that endpoint supplied the same arbitrary-input row. Both exact engines exclude both banks even after granting every other live cocharted row, including owned donors, and the old dirty destination diagonal. Coordinate 244 is zero on all granted rows and −1/2 on the aggregate. [Proof](PROOF.md) · [Exact agreement](receipts/AGREEMENT.json)

The two placements share one paid debit. The directed saving upper is 0.154513811062998 raw for one compatible edit across 17 caller copies. The realized saving is zero. Two fixed banks exhausted, with no unresolved key in this scope. [Complete price](PROOF.md)

## Replay

Use CPython 3.12 with assertions from a clean checkout.

```sh
python3.12 -I -B research/p104-owned-two-write-aggregate-bound/replay.py
```

The standard-library replay authenticates the exact #7354 inventory, #7362 rank-stock manifest, #7334 word and both #7355 proof engines. It regenerates the price, both signed bank receipts and their agreement. Add `--out fresh-directory` to retain the four receipts. Altered inventory, price and word controls reject. [Verification](VERIFICATION.md) · [Provenance](PROVENANCE.json) · [Path-keyed pins](LOCAL-PINS.json)

## Open next questions

Could a changed donor path or an explicitly different producer supply coordinate 244 while preserving the remaining lifetime? Start by pinning the changed source and pricing every added paid leg against the one-edit upper. This result fixes both old endpoint cuts, the original owner, the donor paths and the original post-window state. A later-response cancellation or changed-contract construction requires a separate proof and complete invoice.

## Credit

#7354 at `f92b4c999204e0437dc89359f87fc7be3ecdd12e` supplies the exact owned-lifetime stock. #7355 at `403e0d388c35e83b15eab5bba67be563b33d5a8a` supplies both span engines and covers a separate later sole-ADD pair on the same owner. #7307 supplies the earlier owned terminal chronology method. [#7354](https://github.com/CrocSwap/integer-mult-bounds/pull/7354) · [#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355) · [#7307](https://github.com/CrocSwap/integer-mult-bounds/pull/7307)

The released role-1531 result includes these paid anchors inside a longer changed-producer route with terminal recovery. The fixed two-endpoint aggregate is a separate target. Campaign Round 112 supplies the analogous two-write check on a public role. #7362 supplies the full paid and productive stock, #7338 the admitted witness receipt and #7298 the directed tariff. [Exact released role-1531 finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19554307) · [Campaign discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111) · [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) · [#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338) · [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)

OpenAI Codex and subagents materially assisted proof, implementation, independent verification and packaging.
