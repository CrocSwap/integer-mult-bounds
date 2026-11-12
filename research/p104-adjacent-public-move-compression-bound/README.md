# Adjacent same-chart public MOVE compression

**NO VERIFIED GAIN.** The comparator is [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, with [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The independently reproduced comparable κ is 0.00364665195644.

Could two adjacent paid public MOVEs with the same exact source and destination charts use one transport if their normalized input rows are proportional? The literal word has 29 such pairs and 58 distinct paid clocks. Their ranks are {1:7, 3:4, 4:1, 5:17}. Independent exact forward and backward calculations reproduce all 58 rows on the full 1,501-dimensional arbitrary input and give a nonzero 2×2 minor for every pair. All 29 cases are excluded. Zero remain unresolved within this scope.

The chosen highest-rank, earliest pair is at clocks 32944 and 32945 on roles 625 and 624, chart 3→117. Role 624 has only its original coordinate x₆₂₄. Role 625 has 26 nonzero coordinates and no x₆₂₄ term. With columns 246 and 624, the two rows give the diagonal block (−1,1), with determinant −1. The input x₆₂₄=−1 and all others zero is a direct separating witness.

Use CPython 3.12 on POSIX with assertions. From a clean checkout, run

```sh
python3.12 -I -B research/p104-adjacent-public-move-compression-bound/replay.py
```

The Git-free command authenticates the exact word and source receipts, regenerates all five receipts, compares the full rows, re-evaluates both minor proofs on each pair, and rejects an altered predecessor receipt. Use `--out fresh-directory` to retain the regenerated outputs. See [proof and price](PROOF.md) and [verification](VERIFICATION.md).

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supply the exact native word and signed caller. [#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355) supplies the backwards row reducer, [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) the signed stock, and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) the directed tariff. [#7365](https://github.com/CrocSwap/integer-mult-bounds/pull/7365), [#7366](https://github.com/CrocSwap/integer-mult-bounds/pull/7366), [#7384](https://github.com/CrocSwap/integer-mult-bounds/pull/7384), [#7389](https://github.com/CrocSwap/integer-mult-bounds/pull/7389), and [#7409](https://github.com/CrocSwap/integer-mult-bounds/pull/7409) give adjacent serial, retimed, aggregate and owned transport results. OpenAI Codex and subagents materially assisted. Apache-2.0.

## Open next questions

A larger simultaneous group, a pair separated by other events, or a new physical transport provider remains open. Before testing one, pin its exact pair or group and all changed contacts. Reprice the complete compatible family, then compare its reachable rank to the number of paid positions before any native construction. This package closes adjacent two-field scalar compression via exact zero.
