# Common-hyperplane public helper recharts

**NO VERIFIED GAIN.** On exact #7334 and signed #7113, intersect any simultaneous subset of the pure public helper charts with one common binary hyperplane. Both exact flows certify upper zero on all 511 normals × 18 price vertices, covering 553 eligible components and 2,573 paid and 193 productive edges. Helper endpoints are eligible and productive ranks stay positive. Main and owned components and the scalar word stay fixed.

The independently reproduced complete comparator remains #7334 at κ = 0.00364665195644. This is the dual demotion analogue of #7456's common-vector growth model. See [PROOF.md](PROOF.md) for the annihilator reduction and exact shared-price envelope.

## Reproduction

Use POSIX CPython 3.12 with assertions enabled from a clean checkout.

```sh
python3.12 -I -B research/p104-common-hyperplane-rechart-bound/replay.py
python3.12 -B scripts/research_package.py --package research/p104-common-hyperplane-rechart-bound
```

Both exact word hashes and solver pins are authenticated. The independent solver checks duality and reversed gap controls, and both cut implementations test positive and blocked cases. A tariff-pin mutation is rejected. The original lead took 24.69 seconds and the independent replay 31.18 seconds. Each had a 60-second cap. No cap hit.

## Open next questions

Can distinct hyperplane normals cooperate across components, or can compatible growth and demotion change the full signed price? Freeze one such scope and charge every affected paid and productive edge before changing the physical word. See `TASK.json`.

## Credit

[#7456](https://github.com/CrocSwap/integer-mult-bounds/pull/7456) supplies coupled endpoint growth, the shared-price enclosure and direct-flow reuse. [#7454](https://github.com/CrocSwap/integer-mult-bounds/pull/7454) gives fixed-endpoint interior growth. [#7122](https://github.com/CrocSwap/integer-mult-bounds/pull/7122) and [#7124](https://github.com/CrocSwap/integer-mult-bounds/pull/7124) supply historical input and output rechart precedents. [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) supplies directed arithmetic, [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) the word and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) the signed caller. OpenAI Codex and subagents materially assisted proof, implementation, independent replay and packaging.
