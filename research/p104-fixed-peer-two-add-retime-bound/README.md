# Fixed-peer two-ADD retiming of P104 helper paths

**NO VERIFIED GAIN.** Exact Δκ = 0 relative to the independently
reproduced conditional κ = `0.00364665195644` on
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, with exact signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.

Replace one public 1+1 paid ascent by a direct rank-two ascent.
Retain both signed ADDs in order, with a fixed public peer and
its complete paid path. Four frozen windows contain 8,248 typed
retiming cuts. Strict ascent excludes all 4,124 low-endpoint cuts.
Two opposite-direction literal walks agree on all 4,124
high-endpoint cuts. The peer never occupies the high endpoint,
including the 2,364 cuts free of crossed scalar/lifetime events.
The other 1,760 also cross an ADD. There are no survivors or
unresolved cuts. [Exact interval and blocker agreement](receipts/AGREEMENT.json).

The directed one-edit upper is about 0.08583213854035211 raw.
The optimistic four-edit upper is about 0.34332855416140845
with all ancillary work granted free. One extra raw rank-one
paid call defeats that whole envelope. [Proof and price](PROOF.md).

## Replay

From a clean checkout, use CPython 3.12 with assertions enabled:

```sh
python3.12 -I -B research/p104-fixed-peer-two-add-retime-bound/replay.py
```

The standard-library replay authenticates the exact word and
published predecessor receipts, rebuilds the price, and compares
all four intervals, chart IDs, peer MOVE records and first
blockers. It rejects modified price and word inputs. Use
`--out fresh-directory` to retain all four regenerated receipts.
The package needs no Git metadata, network or previous temporary
state. [Provenance](PROVENANCE.json) · [Path-keyed hashes](LOCAL-PINS.json).

## Open next questions

For the 32 scalar-clean cuts of the role-652 window, can an
explicit change to peer 1450's paid path create a chart-207
meeting? First freeze and price one such change, then test
signed arbitrary-input forward and adjoint action, restoration,
precision and tape only if the complete price survives. The
present exclusion retains the original peer itinerary.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
supplies the exact native word and comparator, and
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
the signed caller. [#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)
already inventories these four paid pairs under the
maximal-component virtual-owned fusion mechanism.
[#7365](https://github.com/CrocSwap/integer-mult-bounds/pull/7365)
supplies the changed-role contact and pricing inputs,
[#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362)
the complete stock receipt and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
the exact tariff. [#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003)
and [#7004](https://github.com/CrocSwap/integer-mult-bounds/pull/7004)
supply the earlier commuting-contact and changed-peer-itinerary
precedents. [#7312](https://github.com/CrocSwap/integer-mult-bounds/pull/7312),
[#7366](https://github.com/CrocSwap/integer-mult-bounds/pull/7366) and
[#7368](https://github.com/CrocSwap/integer-mult-bounds/pull/7368)
supply neighboring sole-ADD chronology tests. OpenAI Codex and
subagents materially assisted the proof, implementation, independent
verification and packaging.
