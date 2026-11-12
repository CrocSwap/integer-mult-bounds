# Owned MOVE chronology on the signed P104 word

**NO VERIFIED GAIN. Exact conditional κ change 0%.** These two finite exclusions cover consecutive paid MOVEs of one owned lifetime on exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, conditional κ 0.00364665195644 with the exact [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) signed 17-copy caller. The selected record is unchanged.

- **Opposite-direction unary turns.** The independent walks agree on all nine same-lifetime neighboring pairs in the 76,466-event word. All nine pairs move in the same direction and have an intervening binary ADD. There are 47 paid owned MOVEs, 73 owned lifetimes, and zero opposite-turn or contact-free geometric keys.
- **One ADD on a monotone pair.** Five of the nine pairs have exactly one intervening ADD. Across both outer-chart placements, all 51 pre-event cuts have the wrong counterpart chart. Four cuts also lack the original counterpart lifetime and ten cross a blocked incident event. No cut passes, and both scopes exhaust with zero unresolved cases.

Each feasible monotone fusion would replace ranks p and q by p+q at unchanged productive stock. The price grants the five disjoint edits and free ancillary costs. Their directed gross upper is 0.740981735345844 raw at the incumbent crossing. The complete margin at fixed κ 0.0040075385047236 stays below −138.9529217164908 raw. The verified compatible saving for each tested family is zero. [Proof and exact scopes](PROOF.md)

## Reproduce

Use CPython 3.12 with assertions and the standard library. From the clean repository checkout:

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-owned-move-chronology-bound
~~~

From the package directory or a Git-free copy:

~~~sh
python3.12 -I -B replay.py --out fresh-receipts
~~~

The replay authenticates the exact compressed word and its canonical payload, both price and geometry inputs, and the inherited stock and tariff. It regenerates both full prices and both independent geometry walks per scope, matches eight receipts byte for byte, and rejects a corrupted word before producing any receipt. It needs no earlier run or downloaded dependency. The stored #7334 admission and price readback bind the complete comparator; this package replays the two new exclusions, rather than the comparator's full admission. [Verification details](VERIFICATION.md)

## Open next questions

Four same-lifetime pairs have multiple intervening ADDs. Test one of their exact ordered contact windows by extracting its exterior source and destination response and pricing the minimum counterpart route needed to preserve it. A changed counterpart itinerary or compensation falls outside the two tested families and requires an exact arbitrary-input and signed all-width proof.

## Attribution

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) provides the exact native word and comparison, [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) the signed caller, [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) the directed tariff, and [#7307](https://github.com/CrocSwap/integer-mult-bounds/pull/7307) the prior owned rank/contact stock on #7277. [#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003) supplies an earlier constructive contact-relocation precedent. [#7259](https://github.com/CrocSwap/integer-mult-bounds/pull/7259), [#7312](https://github.com/CrocSwap/integer-mult-bounds/pull/7312), [#7171](https://github.com/CrocSwap/integer-mult-bounds/pull/7171) and [#7337](https://github.com/CrocSwap/integer-mult-bounds/pull/7337) cover related contact-free, public-lift, fixed-clock and mixed rechart scopes. OpenAI Codex and subagents materially assisted.
