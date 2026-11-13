# Public role 720 chart-265 terminal contraction

**NO VERIFIED GAIN.** On exact #7481, test deleting public720's terminal rank-one MOVE45363 and moving the correction from ADD45364 to chart 265 immediately before MOVE41307. The proposed productive endpoint contracts from rank four to rank three. All earlier outward reads and the original owned role 1511 history remain fixed.

The input `x0=2, x7=−1, x720=−1/4` with all other coordinates zero annihilates all six offered chart-265 rows, including old720. Role 92 is zero on this probe when it leaves chart 265, but the historical version captured by owned1511 at ADD33129 is 1. The independent normalized forward replay verifies the six-row bank, the owner read and clear, and the final old and unrepaired role720 responses of −1/4 and zero. This exhausts one fixed cut with zero unresolved in scope.

Hypothetical gross is in [0.13900113391906015, 0.13900113391906017] raw across all 17 signed calls before corrections or ancillary costs. No saving was realized. See [proof and price](PROOF.md), [path pins](PINS.json) and [verification](VERIFICATION.md).

## Replay

Use CPython 3.12 and its standard library on POSIX. From a clean checkout:

```sh
python3.12 -I -B research/p104-public720-terminal-contraction-bound/replay.py
```

Expect `PASS_PUBLIC720_TERMINAL_CONTRACTION_BOUND`. Both scientific processes have a 30-second cap. Direct replay needs no Git metadata, network or prior temporary state.

## Open next questions

Can a different already-paid carrier or a different legal cut recover the later version of role92? Name its source, chart and first affected read, and check that its row distinguishes the separator before pricing the full edit. Other cuts, changed source histories and altered banks remain open.

## Credit

[#7494](https://github.com/CrocSwap/integer-mult-bounds/pull/7494) supplies the adjacent same-word public720 retiming result at MOVEs40828/45363 and ADD40829. [#7124](https://github.com/CrocSwap/integer-mult-bounds/pull/7124) supplies the global output rechart precedent, and [#7453](https://github.com/CrocSwap/integer-mult-bounds/pull/7453) the fixed-endpoint multi-ADD component census. [#7491](https://github.com/CrocSwap/integer-mult-bounds/pull/7491) supplies a related timed receiver-bank method. [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) supplies the exact word and invoice, with [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) and [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) in its lineage. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the signed caller, [#7482](https://github.com/CrocSwap/integer-mult-bounds/pull/7482) exact cut covectors, [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) directed tariffs, and [#7508](https://github.com/CrocSwap/integer-mult-bounds/pull/7508) prior public copies of pinned bytes. OpenAI Codex and subagents materially assisted proof, implementation, independent replay and packaging.
