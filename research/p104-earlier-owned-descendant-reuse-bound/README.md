# Earlier owned descent reuse bound

**NO VERIFIED GAIN.** On exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) `aaeec8c0acf01e99a5f331ef363a698d9c084ace` with [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) `07a76c5e2738882c0cb322278e56f6cae3c9885d`, test reuse of earlier paid owned descents to prepare each later target. Each of the eight old descents ends on a rank-one chart and has paid rank above one. The chart-3 base is granted freely and the remaining original-input row is its exterior.

All 247 earlier-descendant subsets are priced. The 64 strictly profitable subsets have exact independent separating inputs and no exterior-span survivor. The eight exterior rows have rank eight. The determinant on input columns 0,1,2,4,5,6,9,12 is 1/32768. The scoped result leaves κ at 0.00364665195644. [Proof and price](PROOF.md).

From a clean POSIX checkout with CPython 3.12 and assertions:

```sh
python3.12 -I -B research/p104-earlier-owned-descendant-reuse-bound/replay.py
```

The replay checks the two exact predecessor row receipts against the literal native word, regenerates all prices and separating certificates, verifies the full-rank minor by a separate exact determinant calculation, and rejects an altered predecessor row. One exact word gzip and all needed sources are included. [Verification](VERIFICATION.md).

## Open next questions

Can a different paid producer supply a missing exterior direction? Pin its exact original-input row and target chart, price the whole route including ownership and restoration, then test whether it defeats an existing separator. Snapshot access alone cannot change the span of these eight fixed rows.
