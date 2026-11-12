# Fixed-clock distinct-mask Type B odd-idle unions

**NO VERIFIED GAIN.** Exact Δκ = 0 relative to conditional κ = 0.00364665195644 on independently replayed [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334), head `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, with signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113), head `07a76c5e2738882c0cb322278e56f6cae3c9885d`.

Pair one stage-8 odd idle at clock 1339 or 1340 with one stage-9 odd idle at clock 2970 or 2971. Keep a one-role union at either original clock and delete the other idle. The four pairs give eight single schedules and eight simultaneous disjoint-pair schedules. Exact transported projectors and a separate contact-based stage-set proof exclude all 16. Every original projected role is distinct, so simultaneous stage derivatives cannot cancel. The necessary test specializes q and all body variables to one. All other caller events stay fixed. [Proof](PROOF.md)

The complete paid invoice removes 16 rank-nine positions and adds eight rank-18 positions per edit, across eight Type B ports with all 17 native copies unchanged. The one-edit optimistic upper is 0.360623245857322 raw and the two-edit upper is 0.721246491714643. Granting an unproved rank-16 provider, the corresponding whole upper is 32.2769060131216 raw. Both miss the fixed moonshot target. The verified saving is zero. [Verification and exact replay](VERIFICATION.md)

## Replay

Use CPython 3.12 with assertions enabled. From a clean checkout:

```sh
python3.12 -I -B research/p104-type-b-odd-odd-idle-bound/replay.py
```

This authenticates the exact caller, regenerates the complete directed price and both exact support results, compares every signed witness and rejects four altered inputs. Use `--out fresh-directory` to retain the three deterministic receipts. [Source provenance](PROVENANCE.json)

## Credit

[#7295](https://github.com/CrocSwap/integer-mult-bounds/pull/7295) supplies the exact backward logical contact trace and earlier rank-additive price bound, which already covers the four odd/odd pairs as lane groups. [#7357](https://github.com/CrocSwap/integer-mult-bounds/pull/7357) supplies the literal idle census, complete current price input and exact impulse routines. [#7315](https://github.com/CrocSwap/integer-mult-bounds/pull/7315) supplies the derivative method. [#7356](https://github.com/CrocSwap/integer-mult-bounds/pull/7356), [#7360](https://github.com/CrocSwap/integer-mult-bounds/pull/7360) and [#7380](https://github.com/CrocSwap/integer-mult-bounds/pull/7380) cover phase transfers, same-mask squares and odd/even unions. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplies directed arithmetic. OpenAI Codex and subagents materially assisted.

## Open next questions

Can an exact two-role provider retain both original projected actions while lowering the total paid cost? Start by fixing one provider’s logical return contract and fully pricing its two outputs, parity, volume, ownership, routing and restoration. A common one-role projection already fails the frozen schedules.
