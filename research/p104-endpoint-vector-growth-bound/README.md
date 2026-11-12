# Common-vector public helper recharts with endpoint credits

**NO VERIFIED GAIN.** On exact #7334 and signed #7113, even jointly changing pure public helper input and output charts by one common binary vector gives exact directed upper zero. Both engines cover 553 eligible components, 2,573 paid edges, 193 productive edges and 511 × 18 direction/price cases. The independently reproduced complete comparator remains #7334 at κ = 0.00364665195644.

The fixed interior model in #7454 has no endpoint credits. Here all pure helper components may grow, and productive nesting and positive target ranks are enforced. Independent per-edge rounding leaves a small positive relaxation. A shared nine-increment L1 envelope closes it exactly. See [PROOF.md](PROOF.md).

## Reproduction

Use POSIX CPython 3.12 with assertions enabled.

```sh
python3.12 -I -B research/p104-endpoint-vector-growth-bound/replay.py
python3.12 -B scripts/research_package.py --package research/p104-endpoint-vector-growth-bound
```

The direct runner checks both immutable word hashes and solver pins, reconstructs the two inventories and cut models, and compares all exact results. It retains the original 60-second independent partial receipt and the 10-second continuation that checked exactly its 227 uncovered vertices. The fresh independent replay uses exact terminal-capacity cancellation and matches the merged evidence. It rejects an altered tariff pin and checks positive and blocked graph controls.

## Open next questions

Can differing added vectors or shrinking one public chart improve a coupled endpoint assignment? Freeze one such changed model and charge each affected productive and paid edge before attempting a physical rewrite. The present result closes the common-vector restriction only. See `TASK.json`.

## Credit

[#7122](https://github.com/CrocSwap/integer-mult-bounds/pull/7122) and [#7124](https://github.com/CrocSwap/integer-mult-bounds/pull/7124) supply global input and output rechart precedents on earlier words. [#7454](https://github.com/CrocSwap/integer-mult-bounds/pull/7454) supplies the fixed-endpoint common-vector family and the independent reverse-inventory and edge-flow engines. [#7453](https://github.com/CrocSwap/integer-mult-bounds/pull/7453) covers one common interior component, and [#7386](https://github.com/CrocSwap/integer-mult-bounds/pull/7386) covers terminal chart-207 retargeting. [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) supplies directed arithmetic, [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) the word and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) the caller. OpenAI Codex and subagents materially assisted proof, implementation, independent verification and packaging.
