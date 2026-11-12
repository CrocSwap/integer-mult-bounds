# Exact historical-bank MOVE fusion continuation

**NO VERIFIED GAIN.** The comparison uses exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace` and signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, κ = 0.00364665195644.

Continue the [#7434](https://github.com/CrocSwap/integer-mult-bounds/pull/7434) fixed destination-ADD chronology. The proposed edit contracts two paid MOVEs of one role and defers its sole intermediate ADD until immediately after the second old MOVE. That edit needs the old source row in the span of the unchanged live destination-chart bank at that cut.

The earlier exact coordinate screen and six rank checks left 237 keys. Both exact methods exclude all 62 of those keys with bank size at most 19. The larger-bank search hit its 60-second cap after producing 50 exact separators. A separate literal replay verifies every one against its full historical bank and old source. This adds 112 exact exclusions. The [remaining 125 keys](receipts/UNRESOLVED.json) have a combined optimistic raw upper below 14.380 and remain unresolved.

Use POSIX CPython 3.12 with assertions from a clean checkout.

```sh
python3.12 -I -B research/p104-historical-bank-span-continuation/replay.py
```

The offline command authenticates the original word and predecessor receipts, regenerates both 62-case exact replays, verifies the 50 frozen large-bank separators, and reproduces the unresolved keys and directed prices. Use `--out fresh-directory` to retain regenerated receipts. See [proof and price](PROOF.md) and [verification](VERIFICATION.md).

[#7434](https://github.com/CrocSwap/integer-mult-bounds/pull/7434) at `5f45414d0cc5d0ce6931167bc3e54b026fd4ca09` supplies the 967-case chronology, exact support receipts and earlier six rank checks. #7334 and #7113 supply the exact word and signed caller. [#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355) supplies the reverse exact row reducer, #7362 the signed stock, and #7298 the directed tariff. OpenAI Codex and subagents materially assisted. Apache-2.0.

## Open next questions

Can any of the 125 unvisited banks supply the omitted source with a legal exact combination? Start from the committed key list. Freeze one price-eligible batch and test the existing rational separating inputs on it before another per-bank elimination. A rank survivor still needs the literal direct MOVE, legal signed coefficients and complete physical and application replay.
