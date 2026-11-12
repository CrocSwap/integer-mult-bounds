# Closed public multi-ADD recharts with fixed MOVE clocks

**NO VERIFIED GAIN. Exact conditional κ change 0%.** Both exact walks matched all 13 price-positive inherited components on exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334). Eleven proposed upward shifts require rank five in a rank-four high intersection. The two downward shifts require ranks three and four while their low unions have ranks four and five. Zero survivors and zero unresolved or unvisited keys.

The comparator is #7334 at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, κ 0.00364665195644, with the exact [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) signed 17-copy caller. The edit changes one common interior chart for a closed public component containing multiple ADDs. Every role, coefficient, contact clock, paid MOVE and outer chart stays fixed. The exact geometry covers only the 13 frozen inherited #7277 ADD-only variants. Newly created current-word components and changed outer routes lie outside scope. [Proof](PROOF.md)

## Complete price

The frozen #7312 public contact inventory gives 1,311 components with at least two ADDs, of which 818 are closed. Among 424 closed unprotected helper components, 352 contain only ADD contacts. Twenty-eight components allow a nonzero rank offset with positive paid ranks. The quote tests 38 offsets and finds 13 strictly positive at the complete incumbent probe. All 13 are ADD-only.

Paid count stays 110,519, productive count 22,461, signed rank surplus 1,424 and empty-root credit zero. The highest one-edit gross upper is about 0.10630539120918452 raw. The maximum disjoint-clock stock upper is about 0.8868787213783863 raw, granting all ancillary costs free. At fixed κ 0.0040075385047236 the exact whole-stock complete margin stays below −138.7929181743437. Both geometry checks reduce compatible saving to zero.

## Reproduce

Use CPython 3.12 with assertions and the standard library. From a clean repository checkout:

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-public-multi-add-rechart-bound
~~~

From the package directory or a Git-free copy:

~~~sh
python3.12 -I -B replay.py --out fresh-receipts
~~~

The standalone replay verifies the exact ancestor and current word bytes, regenerates the complete price before native decoding, compares both signed contact walks and reconciles the exact chart bounds. It matches four receipts byte for byte and rejects mutations of the price and current word. [Verification and exact source pins](VERIFICATION.md)

## Open next questions

A different outer route may enlarge a common chart interval. Pin one exact changed route, charge every added or changed paid call and route, then recompute its span and signed caller compatibility. The current optimistic stock is smaller than one additional raw paid rank-one position.

## Attribution

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) supplies the current word and comparison, [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) the exact caller, and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) directed pricing. [#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) and [#7312](https://github.com/CrocSwap/integer-mult-bounds/pull/7312) supply the predecessor word and contact inventory. [#7358](https://github.com/CrocSwap/integer-mult-bounds/pull/7358) supplies the fixed-clock single-ADD precedent and the forward chart-contact helper. [#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319) and [#7339](https://github.com/CrocSwap/integer-mult-bounds/pull/7339) supply the productive cohort and changed-role protection. [#7337](https://github.com/CrocSwap/integer-mult-bounds/pull/7337) and [#7297](https://github.com/CrocSwap/integer-mult-bounds/pull/7297) cover related mixed and owned cases. OpenAI Codex and subagents materially assisted.
