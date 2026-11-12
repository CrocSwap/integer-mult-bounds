# Four-role P104 endpoint exchange bound

**NO VERIFIED GAIN.** The exact [#7334 native word](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace` and [#7113 signed caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d` retain conditional κ = 0.00364665195644. The four-role edit would trade productive ranks 5 and 9 for 6 and 8 at fixed paid rank. All 15 prefix banks are excluded. The realized saving is zero.

The [#7391 two-role scope](https://github.com/CrocSwap/integer-mult-bounds/pull/7391) contains 20,455 raw cut incidences. Extending the [#7395 three-role bank](https://github.com/CrocSwap/integer-mult-bounds/pull/7395) with public role 1251 leaves 16,494 four-role coframed cuts and 3,961 cuts without the required coframe. The original eight exact prefix exclusions and seven resumed exclusions cover all 15 legal segments. An independent forward replay checks all 16,494 eligible incidences directly. The exact proof and price are in [PROOF.md](PROOF.md). The matched workflow trial is inconclusive and leaves the existing per-case solver as default. Its receipts and effort estimates are in [VERIFICATION.md](VERIFICATION.md).

## Replay

From the checkout root on a POSIX system, use CPython 3.12 with assertions enabled.

```sh
python3.12 -I -B research/p104-four-role-endpoint-exchange-bound/replay.py
```

The package carries one pinned gzip of the public native word. It needs neither Git metadata, network access, prior temporary files, nor a nonstandard dependency. Expected final line is `PASS_P104_FOUR_ROLE_ENDPOINT_EXCHANGE_BOUND`. Exact inputs and predecessor contributions are recorded in [PROVENANCE.json](PROVENANCE.json) and [NOTICE](NOTICE). OpenAI Codex and subagents materially assisted.

## Open next questions

Can a different provider-side edit reduce a paid rank while retaining the caller? Fix one exact slot, charge the entire invoice change including scalar, routing, ownership, restoration and tape, then test signed arbitrary-input action only if the directed saving remains positive. A different endpoint pair or bank role also needs its own coframe census and full price. The present proof closes the inherited four-role family and leaves those distinct scopes open.
