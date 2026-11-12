# Pair and triple reuse of signed Type A phase legs

**NO VERIFIED GAIN.** The exact comparator is [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace` with signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, κ = 0.00364665195644.

At unit bodies the old Type A relative endpoint between the two legal central signs is −I. Its chronological factorization has 38 rank-one updates, two per native J call and four original QUERYs. Can two or three selected updates be moved through the intervening fixed factors and replaced by one fewer rank-one update? All 703 pairs and 8,436 triples fail. The 152 proper maximal windows cover 699 pairs and 8,296 triples by exact displacement rank. The four remaining pairs and 140 remaining triples span J1 and J17. Independent exact endpoint replays find rank two and rank three, respectively, for every transported product minus identity. There are zero unresolved keys in the declared family.

Run from a clean checkout with POSIX CPython 3.12 and assertions.

```sh
python3.12 -I -B research/p104-signed-phase-leg-reuse-bound/replay.py
```

The offline command authenticates the exact word and source receipts, verifies the legal signed phases, reproduces the proper-window gate and both methods for each endpoint family, and rejects a changed caller. See [proof and pricing](PROOF.md) and [verification](VERIFICATION.md).

[#7419](https://github.com/CrocSwap/integer-mult-bounds/pull/7419) at `a590edb3c5f7efd7404b1203e727c8cc3218493e` supplies the proper-window rank certificate and price stock. #7334 and #7113 supply the exact native and caller. #7410 supplies exact signed-phase replay and literal-prefix tools, #7362 the rank stock, and #7298 the directed tariff. OpenAI Codex and subagents materially assisted. Apache-2.0.

## Open next questions

A simultaneous rewrite of four or more selected factors, a changed retained factor, or a different provider remains open. Price one exact new family, then bound the displacement rank of its transported product before any all-body or native build.
