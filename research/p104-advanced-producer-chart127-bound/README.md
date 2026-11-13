# Advanced producer at the chart-127 repair

**NO VERIFIED GAIN.** On exact #7481, fuse public role 1351's MOVEs 38867 and 48154, omit its intervening incoming ADD38868, and advance role 1369's ADD52128 and already-paid MOVE52129. Test the full edited chart-127 bank immediately before ADD48155, granting both the advanced producer and the edited role 1351.

One exact 90-coordinate rational probe annihilates all 669 edited rows. Old role 1351 is 1 on the probe, and the old outward ADD makes role 408 equal 1. The unrepaired edited output is zero. A separate literal normalized forward replay confirms the result and the earlier access to the same owner version. This exhausts the one fixed route and cut with no unresolved case.

The paid fusion has hypothetical gross in the interval [0.15453192223429987, 0.15453192223429988] raw across all 17 signed calls, before repairs. No saving was realized. See [proof and price](PROOF.md), [path pins](PINS.json) and [verification](VERIFICATION.md).

## Replay

Use CPython 3.12 and its standard library on POSIX. From a clean checkout:

```sh
python3.12 -I -B research/p104-advanced-producer-chart127-bound/replay.py
```

Expect `PASS_ADVANCED_PRODUCER_CHART127_BOUND`. The exact continuation and independent forward engine each have a 30-second cap. The initial capped receipt is authenticated as provenance. Direct replay requires no Git metadata, network or prior temporary state.

## Open next questions

Can a different paid producer supply a distinguishing direction at this deadline? Name its exact sender, receiver and affected reads, and show that its action distinguishes the separator input from zero before repricing a build. Different paid paths, earlier repairs and a changed downstream interface remain open.

## Credit

[#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) supplies the exact native word and invoice, with [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) and [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) in its lineage. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the signed caller, [#7482](https://github.com/CrocSwap/integer-mult-bounds/pull/7482) exact cut covectors, [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) directed tariffs and [#7508](https://github.com/CrocSwap/integer-mult-bounds/pull/7508) prior public copies. [#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003) and [#7494](https://github.com/CrocSwap/integer-mult-bounds/pull/7494) supply timing and fixed-peer retiming precedents. [#7500](https://github.com/CrocSwap/integer-mult-bounds/pull/7500) supplies the different deferred chart-127 separator and ownership-aware replay precedent. OpenAI Codex and subagents materially assisted proof, implementation, independent replay and packaging.
