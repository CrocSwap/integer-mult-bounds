# Bound the chart-549 paid bypass for role 235

**NO VERIFIED GAIN.** The exact [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) native tape uses role 235 at chart 549 between paid ranks four and two. A rank-six direct move would save strictly between 0.2355 and 0.2356 raw across the complete signed caller. At the old ADD, the retained bank annihilates the public unit input in role 7, while the original source has value one. The old ADD is impossible to reconstruct from that bank.

One role and one fixed cut were exhausted. From a clean POSIX checkout with CPython 3.12 and assertions enabled, run:

```sh
python3.12 -I -B research/p104-role235-paid-bypass-bound/replay.py
```

[Proof and exact scope](PROOF.md) · [Verification](VERIFICATION.md) · [Source pins and credit](PROVENANCE.json)

## Open next questions

Different capture clocks or transport of an additional independent row can change the span. Their complete price must be checked before construction. A new paid rank-one position alone costs 17 raw under the retained caller and exceeds this case's gross gain. This bound leaves changed bank itineraries and paid exchanges outside its scope.
