# Fixed-boundary coframe bound for two chart-32 signed triads

**NO VERIFIED GAIN.** Exact Δκ = 0 relative to conditional κ = `0.00364665195644` on #7334 `aaeec8c0acf01e99a5f331ef363a698d9c084ace` with signed #7113 `07a76c5e2738882c0cb322278e56f6cae3c9885d`. [Comparator #7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) · [Signed caller #7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)

Both exact signed ADD/SCALE/ADD blocks on role pairs (319,35) and (1081,807) have the same fixed outer charts. On each block, the only binary subspace for a common coframe with public nested transport is chart 32's span. Moving the block to chart 3 fails the peer's entrance. Moving it to chart 355 fails the peer's exit. Every common coframe under these boundaries preserves the three rank-one paid legs. Both exact engines agree on the signed matrices, paid and scalar contacts and all four failed placements. [Proof](PROOF.md) · [Agreement](receipts/AGREEMENT.json)

The complete preflight relaxed two-site saving was at most 0.558921518138573 raw. With the actual nearest peer boundaries, chart 3 has no admissible price and chart 355's rejected placement is worth at most 0.08583213854035211 per site. The verified saving is zero. [Complete price and scope](PROOF.md)

## Replay

Use CPython 3.12 from a clean checkout.

```sh
python3.12 -I -B research/p104-chart32-triad-coframe-bound/replay.py
```

This standard-library replay authenticates the exact predecessor manifests and #7334 word, reconstructs the directed price, runs both chart and incident walks and compares the four dispositions. Add `--out fresh-directory` to keep all four receipts. Altered geometry, price and word controls reject. [Verification](VERIFICATION.md) · [Provenance](PROVENANCE.json) · [Path-keyed pins](LOCAL-PINS.json)

## Open next questions

Could a separately priced edit change one peer boundary or implement the ordered block with a different source contract? Start by pinning the exact changed exterior contact and all new paid legs. Check its whole-stock upper against the current complete witness before any literal build. Multi-coframe or changed-contact constructions are outside the theorem.

## Credit

#7365 supplies the inherited contact inventories, #7362 the complete paid/target stock, #7298 the directed arithmetic and #7338 the exact admission and overlapping maximal-component evidence. #7338 includes the role-1081 window under its separate low/high-stock gate and excludes protected mover 319 from its stock. [#7365](https://github.com/CrocSwap/integer-mult-bounds/pull/7365) · [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) · [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) · [#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)

#7003 supplies the commuting slide method, #7004 and #2725 earlier paid peer/coframe changes for single ADDs, and #6529 an older owned-carrier method on SCALE-containing intervals. [#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003) · [#7004](https://github.com/CrocSwap/integer-mult-bounds/pull/7004) · [#2725](https://github.com/CrocSwap/integer-mult-bounds/pull/2725) · [#6529](https://github.com/CrocSwap/integer-mult-bounds/pull/6529)

OpenAI Codex and subagents materially assisted the proof, implementation, independent verification and packaging.
