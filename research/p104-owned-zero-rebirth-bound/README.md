# Owned zero-rebirth suffix bounds

**NO VERIFIED GAIN.** Conditional κ remains `0.00364665195644`
on the independently reproduced complete comparator
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace` with exact signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`. Exact Δκ is zero.

At each paid owned MOVE, grant a same-clock CLEAR at the old chart
and fresh zero INIT at the destination chart. Keep every other
event, sign and coefficient fixed. All 47 single-site edits change
a final public row. Of 1,081 unordered pairs, 1,073 have independent
original moved rows. The other eight have independently checked
distinct final-public response supports. Every pair is excluded
even when granting arbitrary cross-transport between both sites.
[Proof](PROOF.md) · [Pair witnesses](receipts/PAIR-WITNESSES.json).

## Replay

From a clean checkout, use POSIX CPython 3.12 with assertions.

```sh
python3.12 -I -B research/p104-owned-zero-rebirth-bound/replay.py
```

The standard-library command authenticates the exact word, signed
invoice and predecessor source, regenerates nine deterministic
receipts, and rejects two altered dependencies. Use
`--out fresh-directory` to retain the receipts. No Git metadata,
network, external source root or prior temporary state is required.
[Provenance](PROVENANCE.json) · [Pins](LOCAL-PINS.json) ·
[Verification](VERIFICATION.md).

## Open next questions

Could one ordinary correction at a specified legal coframe restore
every affected public row and clean-write guard within the
incumbent ordinary-work envelope? Start with a receiver whose full
guarded suffix response is known. Larger zeroing subsets, changed
times or coefficients, replacement donor writes, and changes to
the caller remain open.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supply the exact native word and signed caller.
[#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)
retains the independent comparator admission.
[#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362)
supplies the exact signed stock and
[#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
supplies the directed tariff.
[#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355)
and [#7384](https://github.com/CrocSwap/integer-mult-bounds/pull/7384)
supply the exact row and span engines used to rebuild the R137
predecessor rows.

[#7307](https://github.com/CrocSwap/integer-mult-bounds/pull/7307)
checks direct dead owned MOVEs on #7277.
[#7308](https://github.com/CrocSwap/integer-mult-bounds/pull/7308)
checks immediate owned-row replacement on that older word.
[#5557](https://github.com/CrocSwap/integer-mult-bounds/pull/5557)
establishes earlier residual-preserving checks that motivate
the clean-write observables.
[#7378](https://github.com/CrocSwap/integer-mult-bounds/pull/7378)
checks a two-write aggregate while retaining the original dirty owner.
The present replay tests complete suffix observability for fresh zero
replacement on exact #7334.
OpenAI Codex and subagents materially assisted proof, implementation,
independent verification and packaging.
