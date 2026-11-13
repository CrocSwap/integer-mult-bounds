# Four donors for the owned role 1548 repair

**NO VERIFIED GAIN.** On exact #7481, remove the rank-one owned1548 MOVE39785 and omit its two old additions to public1298 and public1429. The proposed repair advances the already-paid public913 and public1298 MOVEs to chart 127 immediately before ADD46664. It allows four named donor rows, 913, 1197, 587 and 1494, and requires restoring both old receiver values.

The exact original input `x164=4`, with all other coordinates zero, annihilates all four donors. The historical owned value is −2, so each receiver needs a correction of +1. Independent normalized forward replay verifies the old and edited prefixes and observes a difference of −1 at both first outward reads. An oracle correction restores both reads, and its sign reversal fails both. One fixed case exhausted with no unresolved case in that scope.

Removing one rank-one child per native call gives exactly 17 raw gross across the signed caller before repairs. An added rank-one child per call consumes it. No saving was realized. See [proof and price](PROOF.md), [path pins](PINS.json) and [verification](VERIFICATION.md).

## Replay

Use CPython 3.12 and its standard library on POSIX. From a clean checkout:

```sh
python3.12 -I -B research/p104-owned1548-two-recipient-bound/replay.py
```

Expect `PASS_OWNED1548_TWO_RECIPIENT_BOUND`. Both scientific processes have a 30-second cap. Direct replay needs no Git metadata, network or prior temporary state.

## Open next questions

Can another already-paid path supply the historical owned value at the first outward deadline? Name its precise source version, sender and receiver, then evaluate it on the exact separator before verifying both recipient actions and the full price. A wider chart-127 bank, joint writable-recipient repair, earlier deadlines and altered retirement remain open.

## Credit

[#7491](https://github.com/CrocSwap/integer-mult-bounds/pull/7491) supplies the original single-recipient terminal-bank method, [#7500](https://github.com/CrocSwap/integer-mult-bounds/pull/7500) a distinct deferred multi-recipient chart-127 precedent, and [#7529](https://github.com/CrocSwap/integer-mult-bounds/pull/7529) a separate fixed historical-donor telescope. [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) supplies the exact word and invoice, with [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) and [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) in its lineage. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the signed caller, [#7482](https://github.com/CrocSwap/integer-mult-bounds/pull/7482) the exact cut covectors, [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) the rank tariff, and [#7508](https://github.com/CrocSwap/integer-mult-bounds/pull/7508) prior public copies of pinned bytes. OpenAI Codex and subagents materially assisted proof, implementation, independent replay and packaging.
