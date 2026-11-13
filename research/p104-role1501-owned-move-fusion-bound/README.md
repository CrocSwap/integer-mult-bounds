# Bound the role 1501 owned move fusion

**NO VERIFIED GAIN.** On exact [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481), owned role 1501 moves through charts 549, 115 and 593. Fusing its rank-two and rank-four moves saves strictly between 0.2355 and 0.2356 raw across the complete signed caller before correction. The intervening contribution from owned 1525 is outside the combined span of the two endpoint banks, including the old carrier value. Exact forward replay finds a public input with both endpoint banks zero and the old outward ADD increment −1/2.

One role, one route and one fixed intermediate ADD were exhausted. From a clean POSIX checkout with CPython 3.12 and assertions enabled, run:

```sh
python3.12 -I -B research/p104-role1501-owned-move-fusion-bound/replay.py
```

[Proof and exact scope](PROOF.md) · [Verification](VERIFICATION.md) · [Source pins and credit](PROVENANCE.json)

## Open next questions

The missing direction could be carried by an earlier paid arrival only if that route preserves its own independent return and all required old reads. The first next test is to identify one existing pre-cut path that is nonzero on the separator and to price it before construction. A newly added rank-one native charge alone exceeds the gross saving under the retained caller.
