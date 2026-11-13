# Bound fixed-route outward ADD retiming

**NO VERIFIED GAIN.** On exact #7481, no public two-MOVE chain with exactly one middle-chart contact can remove that stop by relocating its outward ADD to an endpoint when the peer's chart itinerary and noncommuting source chronology are fixed. Two implementations agree on all 958 routes, with zero earlier or later placements. This applies to the stated relocation class on the exact literal word. [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481)

From a clean POSIX checkout with CPython 3.12 and assertions enabled:

```sh
python3.12 -I -B research/p104-outward-add-retiming-bound/replay.py
```

[Scope and proof](PROOF.md) · [Verification](VERIFICATION.md) · [Source pins and credit](PROVENANCE.json)

## Open next questions

A peer with a movable paid chart arrival can change the coframe interval. Before searching more sites, name a concrete route, pin its two new arrival windows, and check both operand source versions and all outward results. A literal candidate must retain the exact signed action and pass a fully charged price. Joint peer retiming, multiple middle contacts, changed scalar dependencies and newly encoded donor histories are outside this screen.
