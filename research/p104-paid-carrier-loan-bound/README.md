# Paid carrier loans for owned lifts

**NO VERIFIED GAIN.** Conditional κ remains `0.00364665195644`
against independently reproduced
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace` and exact signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.

Two tests exhaust all 47 paid owned MOVE anchors. The sole
same-endpoint carrier with restoration deferred to the owner's
old MOVE has an intervening read. The strict nested-carrier test
allows immediate restoration and has one geometric survivor.
Its required carrier row has coefficient −1/2 on input 4.
The only two live cocharted donor rows both have coefficient zero.
Arbitrary rational combinations of those donors fail.

The same-endpoint route also fails with immediate restoration.
Its chart-1091 bank has 17 live donor rows, including three owned
rows. The exact covector x397 − x382 − 3(x2+x230)/2 annihilates all
17 and evaluates to −2 on the required f988 row.
[Proof and price](PROOF.md) · [Exact agreement](receipts/AGREEMENT.json).

## Replay

From a clean checkout use POSIX CPython 3.12 with assertions.

```sh
python3.12 -I -B research/p104-paid-carrier-loan-bound/replay.py
```

The command authenticates the pinned word, earlier census,
signed price and tariff sources. It regenerates eleven original
receipts and checks an exact agreement receipt. Three altered
dependencies are rejected. Use `--out fresh-directory` to retain
all twelve receipts. The standard-library replay works without
Git metadata, network, an external source root or prior temporary
state. [Source provenance](PROVENANCE.json) · [Verification](VERIFICATION.md).

## Open next questions

Can one compensated donor trajectory supply the missing input
response in the chart-1091 bank before clock 36648? Start with a
separately priced donor edit and check the four-coordinate dual
while preserving every original read and restoration. This
changes the frozen unchanged-donor contract.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supply the word and signed caller.
[#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)
supplies independent comparator admission and a distinct
compensated fusion precedent.
[#7387](https://github.com/CrocSwap/integer-mult-bounds/pull/7387)
supplies the exact owned MOVE census and first-contact inventory.
[#7389](https://github.com/CrocSwap/integer-mult-bounds/pull/7389)
supplies the signed deletion-price stock.
[#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362)
supplies the exact base invoice and a distinct paid-midpoint
productive split. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
supplies the directed tariff.
[#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355)
and [#7384](https://github.com/CrocSwap/integer-mult-bounds/pull/7384)
supply forward exact row and donor-span engines.
[#7165](https://github.com/CrocSwap/integer-mult-bounds/pull/7165)
and [#7308](https://github.com/CrocSwap/integer-mult-bounds/pull/7308)
supply earlier unchanged-donor recovery precedents.
[#7244](https://github.com/CrocSwap/integer-mult-bounds/pull/7244)
uses roles 988 and 991 on an earlier word and funded cut.
The current tests use exact #7334 banks and clocks.
OpenAI Codex and subagents materially assisted proof, implementation,
independent replay and packaging.
