# Temporal outer donor banks for an owned write aggregate

**NO VERIFIED GAIN.** The independently reproduced comparator
remains [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, conditional
κ = `0.00364665195644`, with signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.

[#7378](https://github.com/CrocSwap/integer-mult-bounds/pull/7378)
excludes the two original fixed outer banks for the owner-1531
two-write aggregate. This test allows the aggregate to be
assembled at multiple clocks from the unchanged live donor banks
in either old-clock switch schedule. The input-244 impulse is
zero on every donor at all 4,494 chart/cut pairs and on the
initial owner diagonal. The required signed aggregate has
response −1/2. Both switch schedules are excluded.
[Proof and price](PROOF.md) · [Exact alias inventory](receipts/ALIASES.json).

## Replay

Use POSIX CPython 3.12 with assertions from a clean checkout.

```sh
python3.12 -I -B research/p104-owned-outer-temporal-aggregate-bound/replay.py
```

The standard-library command authenticates the exact native word,
the #7378 directed quote and aggregate receipt, and the frozen
two-switch scope. Forward and reverse engines reproduce three
receipts and reject three altered dependencies. Use
`--out fresh-directory` to retain the receipts. Git metadata,
network access, external source roots and prior temporary state
are unnecessary. [Source provenance](PROVENANCE.json) ·
[Verification](VERIFICATION.md).

## Open next questions

Can a separately priced changed donor path carry input coordinate
244 into an eligible outer coframe while preserving all original
observations? First pin one concrete trajectory and charge any
new paid call, ownership, restoration and source access. This
changes the fixed donor contract tested here.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supply the exact word and signed caller.
[#7378](https://github.com/CrocSwap/integer-mult-bounds/pull/7378)
at `fb5e20890e74159f7c432f4d78cc1ebcfea9a420` supplies the two
fixed-bank exclusions, signed aggregate and exact quote.
[#7354](https://github.com/CrocSwap/integer-mult-bounds/pull/7354)
and [#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355)
supply prior owned chronology and adjacent sole-write evidence.
[#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362)
and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
supply the inherited signed stock and directed tariff.
The earlier [released producer and recovery scope](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19554307)
includes the same paid pair with a different contract.
OpenAI Codex and subagents materially assisted proof, implementation,
independent replay and packaging.
