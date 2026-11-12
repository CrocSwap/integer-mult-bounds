# Exclude fixed-clock Type A QUERY cache pairs

**NO VERIFIED GAIN. Exact conditional κ change 0%.** The exact signed #7113 caller has four Type A QUERYs at clocks 1516, 1580, 1659 and 1721. They share the literal source role 1, destination role 0 and central exponent −1. Their exact arbitrary-input source rows are pairwise nonproportional. Two independent rational replays exclude all six ordered-in-time reuse pairs. No case remains unresolved.

The strongest independently reproduced comparable witness is [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, κ = 0.00364665195644, with exact caller [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. Its peer gain of 0.000000430519994 over #7314 is separate from this contribution. The selected result remains unchanged.

## Exact scope and price

The tested reuse keeps one already paid query result in an owned cache and reads a fixed scalar multiple at one later original QUERY. The first consumer, the 17 literal J blocks, all other caller operators, clocks and public endpoints stay fixed. The four logical QUERYs act across 96 Type A ports. Removing one paid event would give exact raw credit 96, paid positions 110,423, productive positions 22,461 and surplus 1,520. The price-only full-stock upper is exactly 288, granting one producer and three reused events before setup, storage, routes, ownership, restoration, precision and tape. The actual scope builds at most one reuse. Ancillary costs were left as obligations because no source identity survives. After the support exclusion, the compatible credit in this scope is zero.

The lead exact replay excludes every pair at q=−1 and all bodies one. The independent exact replay excludes every pair at q=+1 and all bodies one. Its full predecessor endpoint controls also check both signs and two nonunit body assignments. See [the proof and determinants](PROOF.md).

## Replay

Use CPython 3.12 with assertions.

```sh
python3.12 -B scripts/research_package.py --package research/p104-type-a-query-cache-pair-bound
python3.12 -B scripts/check_research_commit.py --package research/p104-type-a-query-cache-pair-bound --check-modes --check-source-history
```

A Git-free checkout or export reproduces the exact four receipts into a new directory.

```sh
python3.12 -I -B research/p104-type-a-query-cache-pair-bound/replay.py --out fresh-receipts
```

The replay authenticates the exact source bytes and rebuilds the complete price before either support engine reads the caller. It compares the price, both result receipts and controls to the recorded SHA-256 values, then recomputes every determinant from its exact serialized rows. A changed caller is rejected before decoding. [Verification receipts](VERIFICATION.md)

## Credit

[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the exact signed caller and physical QUERY lowering. [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) supplies the independently reproduced complete comparator. [#7198](https://github.com/CrocSwap/integer-mult-bounds/pull/7198) and [#5803](https://github.com/CrocSwap/integer-mult-bounds/pull/5803) supply chronological common-query cache compression and the request-row rank perspective. [#6975](https://github.com/CrocSwap/integer-mult-bounds/pull/6975) supplies an older owned inverse-Q lifecycle, and [#3965](https://github.com/CrocSwap/integer-mult-bounds/pull/3965) binds older private query outputs to delivered consumers. [#7309](https://github.com/CrocSwap/integer-mult-bounds/pull/7309) supplies the exact four-query census and fixed-port q-even demotion proof, and [#7310](https://github.com/CrocSwap/integer-mult-bounds/pull/7310) gives the single altered-J obstruction. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplies directed arithmetic. OpenAI Codex and subagents materially assisted the proof, implementation, independent checking and packaging.

## Open next questions

Can an encoded or updated cache, or a span of multiple already paid sources, supply a later query on the same paid invoice? Start by pinning one such cache contract and computing its full charged price and exact request rank. A successful normalized identity would still require signed all-width phase, a lawful owned lifetime, restoration, precision, tape and complete caller verification. The six pairwise exclusions leave these larger mechanisms open.
