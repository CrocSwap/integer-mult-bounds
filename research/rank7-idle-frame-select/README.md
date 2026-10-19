# Hosted frame selection on PR3939: complex root 0.0017411726, κ reaches the pooled bit cap, conditional κ = 0.001734900431583947157341 − 10⁻⁴⁶ − 10⁻⁷⁰ (+0.00203%)

**Author-checked conditional candidate; not maintainer-reviewed.** The selected record on
`main` is still #1094. This package stacks on the open PR3939 (pooled R438 bit), which stacks on
PR3934 → PR3251 → PR3200 → PR3198 → PR3190 → PR3184 → PR3148 → PR3133. PR3133's words and PR3148's
fill rows, order and dispatch are unchanged.

| | complex root lower | bit endpoint | binds | κ headline |
|---|---|---|---|---|
| PR3939 | 0.0017348651784727109982331 | pooled R438 0.001734900431583947157341 | complex | 0.001734865178472710998233 − … |
| **this** | **0.0017411725885452521674224** | pooled R438 0.001734900431583947157341 | **bit** | **0.001734900431583947157341 − …** |

The gain is **+0.00203% over PR3939**. This is the whole remaining window up to the pooled bit
endpoint. The complex root itself rises by **+0.36%**, so κ is now capped by the bit supplier with
about 6.3e-6 of complex headroom.

## Idea

Since PR3190, a bin hosting `used` helper cells was modelled with those cells on the recipe
**prefix** `[0, used)`. Its idle remainder was the recipe **suffix** `[used, cap)`. After PR3934,
the complex side was saturated under that convention:

- 147,220 rank-1 hosted remainders were left.
- 94,656 of them keep only an axis that fails PR1252's translation rule, so they can never move.
- Every one of the 134,320 unmodified rank-1 hosted bins has a **live** axis somewhere in its full
  recipe frame. A live axis is one that commutes with every stage entry/exit X/Y translation, the
  terminal Y translation and the bin's own terminal translation.

**New hypothesis:** the hosted cells may be mapped to **any** `used`-subset of the bin's recipe
frame. The recipe order is not binding. The idle remainder is then whichever `(cap − used)`-subset
the cells leave free.

The builder reorders each hosted bin's frame so that the remainder holds the axes most able to move:

1. live under the translation rule;
2. then legal toward the most children of the group.

It then runs PR3934's pipeline unchanged:

- phase 1: the exact per-group search;
- phase 2: the star optimum;
- phase 3: the greedy single-axis phase;
- phase 5: hosted receivers.

Every move still obeys PR1252's commuting rule, role exclusivity (no child both donates and
receives) and the rank-51 cap. A hosted receiver never donates, so it keeps its whole frame. Its
legality is therefore checked against the full frame and does not depend on the selection.

The result is 521,798 axis moves, against 437,978 for PR3934. The idle bill becomes:

`{1:79440, 2:14080, 3:2617, 4:1800, 5:10355, 6:1594, 42:29023, 44:8040, 45:12620, 46:28120, 47:20, 48:20794, 49:23020, 51:160932}`

Rank-1 remainders fall from 147,220 to 79,440, and rank-51 children rise from 129,006 to 160,932.
Rank mass is unchanged at `65088·740`.

## Reproduce

```sh
# PR3148 materialize.py (research/coupled-carrier-cap740) -> /tmp/t740
python3 -B research/rank7-idle-frame-select/build.py  --t740 /tmp/t740   # ~2 min, deterministic
python3 -B research/rank7-idle-frame-select/verify.py --t740 /tmp/t740   # ~2 min
```

`verify.py` is PR3934's independent verifier, changed for frame selection. It does not import
`build.py`. It re-derives:

- every moved axis is in the donor's own recipe frame, and each hosted donor gives at most
  `cap − used` axes, its idle budget;
- a hosted receiver is orthogonal to its whole recipe frame;
- role exclusivity, unit length, orthogonality at receipt, the commuting rule and the rank-51 cap;
- the profile and rank mass;
- the exact complex root bracket;
- the pooled R438 endpoint, by rerunning `rank7-pooled-r438-bit/verify.py`'s role audit and endpoint
  check;
- `κ = min(floor₂₄(complex), bit) − 10⁻⁴⁶ − 10⁻⁷⁰` with the bit side binding;
- the gates over PR3148 through PR3939.

Nine mutation controls are rejected:

- an over-budget donation;
- a hosted-frame conflict;
- an axis that does not commute;
- a foreign axis;
- an axis moved twice;
- a receiver that also donates;
- a dropped move;
- the next root grid point;
- κ above the bit cap.

With `--t740`, BINS is rebound to PR3148's materialized fill.

## Scope

**New hypothesis: the hosted cell-to-axis map is free.** This is stronger than PR3190's
prefix/suffix convention, which was itself never admitted natively. It also inherits:

- PR3934's hosted-receiver hypothesis;
- PR3190's hosted-donor hypothesis;
- PR3939's cross-replica bit owner map.

**Not rerun:**

- the native admission;
- the overlay-aware T74 controller audit;
- the outer release, whose ledger pins PR589.

The result is conditional on R438, whose source PR1043 is open, and on the whole stack. All
inherited obligations remain.

## Open next questions

- **Is the hosted cell-to-axis map free?** First step: make the T74 hosted overlay/controller audit
  read an explicit per-bin cell-to-axis map, and rerun its controls on PR3148's release with this
  selection. Blocked by: the T74 chain has no overlay reader, and the native hosted emission fixes
  the prefix.
- **Can the bit side rise?** The complex root (0.0017411726) is now about 6.3e-6 above the pooled
  bit endpoint, so any bit gain up to that is realizable. First step: price width-7 conversions or
  deletion-ladder bit words under the pooled slot model. Blocked by: a bit word with an admitted slot
  model beyond R438.

## Credit

- PR1252 (Gonzalo-Mier): the move, the rule and the pricing.
- Guéorgui Maissouradze: the star class.
- PR3148 (Jeremy Diviney): the fill.
- PR3133 and PR3042 (dcharb78): the words.
- PR2979 (Marius-Paul Dumitrean).
- Ali Romman (PR1043) and Sagar Thakrar (PR2423): R438.
- mightyOil (PR1281): the pooled32 optimum.
- The `r438-native-rehost` authors.
- DreamingOfClouds and eumemic.
- OpenCode (Space bunny free): the remainder-donor and exact-search ideas in the stacked
  predecessors.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
