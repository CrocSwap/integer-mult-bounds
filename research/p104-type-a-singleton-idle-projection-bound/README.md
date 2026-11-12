# Single projections for Type A singleton idles

**NO VERIFIED GAIN.** The independently reproduced comparator is
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, κ
`0.00364665195644`, with exact signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.

The two Type A singleton idles at clocks 1466 and 1487 share
body B8 and act on distinct roles 7 and 25. Direct dual
arithmetic and independent inverse projector transport agree
on a rank-two derivative difference when erasing the calls.
The exact difference is affine in B8 with q and all other
bodies fixed to 1. At physical B8 = −1 its separating minor
has determinant 4. One local projected return has difference
rank at most one under the fixed surrounding word, so the
tested replacement is excluded. [Proof and price](PROOF.md).

## Replay

From a clean checkout with CPython 3.12 and assertions:

```sh
python3.12 -I -B research/p104-type-a-singleton-idle-projection-bound/replay.py
```

The standard-library replay authenticates the signed caller
and complete price, regenerates three exact receipts and
rejects three changed dependencies. Use `--out fresh-directory`
to retain the receipts. Only this pair and its 20 strict
interior events receive a support test.
[Source provenance](PROVENANCE.json) · [Verification](VERIFICATION.md).

## Open next questions

Can a separately priced provider preserve both original
projected returns? Start with one explicit pair of input and
return owners and a charged body and phase contract. A second
singleton pair at clocks 1742 and 1766 is present in the
price stock. Its support is outside this proof.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supply the exact benchmark word and signed caller.
[#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362)
and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
supply the complete base invoice and directed tariff.
[#7360](https://github.com/CrocSwap/integer-mult-bounds/pull/7360)
tests same-mask Type B pairs with a different fixed-role
projector contract. [#7295](https://github.com/CrocSwap/integer-mult-bounds/pull/7295)
supplies prior fixed-contact grouping and
[#7144](https://github.com/CrocSwap/integer-mult-bounds/pull/7144)
supplies related diagonal Laurent body gauges.
OpenAI Codex and subagents materially assisted proof,
implementation, independent verification and packaging.
