# Successor frame climbs of the A1858 contraction

**Negative result. No new κ.** The selected record is not edited.

On all four frozen words, the A1858 contraction leaves every positive-dimension climb of registers 456, 457 and 475 unchanged, and it leaves the recursive frame histogram unchanged.

## Scope and evidence

Chooser seed `05f92898273de33149bc662a2b87104d` drew `incumbent-optimization` on canonical main `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`. Suggestion 1, `selected-packing`, is not taken: [PR #4170](https://github.com/CrocSwap/integer-mult-bounds/pull/4170) already transferred the pooled ceiling onto the retained PR #4088 head. This package is suggestion 2, `scalar-to-moment`, scope **refined**. The stop rule of that card is to compare complete histograms and report a scalar-only change honestly.

[PR #4152](https://github.com/CrocSwap/integer-mult-bounds/pull/4152) certifies the cleanup edit of the consecutive A1858 contraction from [PR #3998](https://github.com/CrocSwap/integer-mult-bounds/pull/3998) and leaves the successor climbs of registers 456, 457 and 475 uncomputed. The four gzip words checked here are that package's frozen inputs, authenticated by the SHA256 values in `verify.py`. No predecessor Python is imported.

The published block at zero-based `A[1858:1861]`, all on frame `span(82,42)`,

```
457 <- 457 - 475
456 <- 456 + 457
456 <- 456 + 475
```

is replaced by

```
456 <- 456 + 457
457 <- 457 - 475
```

and cleanup is rederived from the forward word. Both sides induce the same map on `(x456, x457, x475)`. A rank-d child is charged only when a register's frame dimension increases. Recomputing that bill:

| Words | Histogram before and after |
|---|---|
| both PR3734 words | `{1:2440,2:725,3:224,4:102,5:20,8:8}` |
| both PR3945 words | `{1:2482,2:712,3:218,4:109,5:20,8:8}` |

Register 457's full climb sequence is identical, including indices. The only sequence edits are zero-dimension touches inside the block: register 456 replaces A indices 1859 and 1860 by 1858, and register 475 replaces A indices 1858 and 1860 by 1859. Every positive-dimension climb of the three registers keeps its section and index. Widening the block frame to `span(82,42,1)` fails containment. Deleting the block without the two-ADD image changes the histogram. A flipped central sign fails the three-register map.

PR #3998 already stated the PR3734 profile. This note does not replay that package. It answers the climb question PR #4152 left open, on all four words that package froze, with an independent bill.

## What this does not establish

No paid transition is removed. The two deleted ADD events are zero-dimension touches, so the scalar saving is not a frame-itinerary improvement. Native operators, owners, precision, stock, tape and the PR3945 producer bill are not priced. The selected record stays the pinned `certificates/selected-result.json` (κ = `60403/20000000`); `make frontier4470-verify` was not run.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/a1858-successor-frame-climbs/verify.py
python3.12 -B scripts/research_package.py --package research/a1858-successor-frame-climbs
```

Expected first line: `PASS_A1858_SUCCESSOR_FRAME_CLIMBS words=4 pr3734={1:2440,2:725,3:224,4:102,5:20,8:8} pr3945={1:2482,2:712,3:218,4:109,5:20,8:8} paid_climbs=unchanged`.

Catalogue and selected-record provenance, and the four input pins, are in [SOURCES.json](SOURCES.json). Base commit `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`.

## Open next questions

Can the two-ADD image be carried into the PR3945 producer with native, owner and precision costs still paid? An unchanged frame histogram does not decide whether the two removed ADDs survive those obligations. Price one contracted PR3945 word's native and owner bill before claiming the scalar saving. Those obligations are outside the frozen scalar words checked here.

## Credit

Dataisfire's PR3734 words and Dugongue's PR3945 words are the frozen inputs. Chris R / Clear1nsight, PR #3998, wrote the contraction and stated the PR3734 profile. unpaidmoon, PR #4152, certified the cleanup edit and asked for this climb. The frame contract follows the BORROW-WORD reading used by Arham Tahir's coupled-carrier audit and restated, without being imported, by the PR #3998 vendor. Riquelme Soares (@hevlyo), with substantial AI assistance. Apache-2.0. No independent human or formal-kernel review is claimed.
