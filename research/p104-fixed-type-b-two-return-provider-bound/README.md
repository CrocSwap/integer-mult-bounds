# Fixed Type B two-return provider bound

**NO VERIFIED GAIN.** The complete comparator is independently
reproduced [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, κ
`0.00364665195644`, with exact signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.

The two original Type B odd idles at clocks 1339 and 2970
return separate rails. The literal scan and independent
emitter trace agree across all eight ports and four phases.
The signed child contributes q⁻¹ times the corresponding body
and its physical sign correction contributes q². Erasing both
selected calls leaves zero odd response on their fixed returns.

For a single canonical rank-16 or rank-18 core per port, the
required carrier volume exceeds the directed affordability
upper under the stated fibre and volume-linear price
assumptions. The same capacity inequality holds at every
canonical tensor width m ≥ 8 under those assumptions.
[Proof and scope](PROOF.md).

## Replay

Use CPython 3.12 with assertions from a clean checkout.

```sh
python3.12 -I -B research/p104-fixed-type-b-two-return-provider-bound/replay.py
```

The standard-library replay authenticates the retained
sources, regenerates the exact two-rank quote and both
incidence receipts, and rejects three altered inputs.
Use `--out fresh-directory` to retain all three receipts.
[Source provenance](PROVENANCE.json) · [Verification](VERIFICATION.md).

## Open next questions

Can a changed erased map deliver an independent q-odd response
to the original two returns at positive complete margin?
Start with one exact restored owner and explicit new input and
return incidences. Price the new interface, routing and retained
outputs before any host build.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supply the exact native and signed caller.
[#7295](https://github.com/CrocSwap/integer-mult-bounds/pull/7295)
supplies the fixed-contact inventory and rank-additive grouping
precedent. [#7394](https://github.com/CrocSwap/integer-mult-bounds/pull/7394)
supplies the exact odd-idle pair and one-projection exclusion.
[#7357](https://github.com/CrocSwap/integer-mult-bounds/pull/7357)
and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
supply the exact signed invoice and directed tariff.
[#7344](https://github.com/CrocSwap/integer-mult-bounds/pull/7344)
supplies the width-eight displacement method for an earlier
Type A provider question. This package uses its capacity
argument on the two separate Type B returns and supplies the
uniform tensor-width algebra. OpenAI Codex and subagents
materially assisted proof, implementation, independent replay
and packaging.
