# Entry-shadow replay for owned descents

**NO VERIFIED GAIN.** The comparable witness remains [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, with signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d), κ = 0.00364665195644.

Can an owned descent be replaced by one rank-one lift of a saved chart-3 entry shadow? Allow a second entry contribution from all public inputs already in the exact destination chart. The native tape contains eight owned descents where this edit has a positive paid price and the destination rank is one. Independent forward and reverse methods reproduce every exact pre-descent row. Every row has 52 nonzero coefficients outside the two allowed entry banks. All eight cases fail, with zero unresolved within scope.

The largest candidate is old MOVE 39811 on role 1503, chart 520→595, rank five. Its row has 236 nonzero coefficients, including 184 from chart 3 and 52 exterior entries. Input x₀ starts in chart 0 and has required coefficient +1/4. It is a direct counterexample to reconstruction from the allowed charts. The narrower snapshot of role 146 at pre-38967 also fails exact proportionality.

Run from a clean checkout with POSIX CPython 3.12 and assertions.

```sh
python3.12 -I -B research/p104-entry-shadow-owned-descent-bound/replay.py
```

The Git-free replay authenticates the exact word, regenerates six deterministic receipts, compares every full row and verifies all exterior witnesses. Use `--out fresh-directory` to retain the regenerated receipts. See [proof and pricing](PROOF.md) and [verification](VERIFICATION.md).

#7334 and #7113 supply the exact native and caller, [#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355) the reverse row reducer, [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) the retained stock, and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) the directed price. [#7392](https://github.com/CrocSwap/integer-mult-bounds/pull/7392) and [#7409](https://github.com/CrocSwap/integer-mult-bounds/pull/7409) concern existing paid carrier and donor schedules. [#7330](https://github.com/CrocSwap/integer-mult-bounds/pull/7330) supplies related entrance retiming on an earlier word. OpenAI Codex and subagents materially assisted. Apache-2.0.

## Open next questions

A different saved source chart, an ordinary equivalence between distinct entry charts, or a charged replay from multiple chart groups remains open. Pin one exact additional source route and price all required conversions before testing the full row or constructing a shadow.
