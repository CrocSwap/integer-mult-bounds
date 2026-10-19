# Hosted remainders as receivers on PR3251: the complex side passes R438 again, conditional κ = 0.001734846264120199151475 − 10⁻⁴⁶ − 10⁻⁷⁰ (+0.00176%)

**Author-checked conditional candidate; not maintainer-reviewed.** The selected record on
`main` is still #1094. This package stacks on the open PR3251, an exact per-group idle-donor search
that itself stacks on PR3200 → PR3198 → PR3190 → PR3184 → PR3148 → PR3133. PR3133's words and
PR3148's fill rows, order and dispatch are unchanged.

| | complex root lower | bit endpoint | binds | κ headline |
|---|---|---|---|---|
| PR3251 | 0.0017348157703850985634843 | R438 0.001734846264120199151475 | complex | 0.001734815770385098563484 − … |
| **this** | **0.0017348651784727109982331** | R438 0.001734846264120199151475 | **bit** | **0.001734846264120199151475 − …** |

The gain is **+0.00176% over PR3251**, which is the whole remaining window to the R438 bit endpoint.
The complex root now sits 1.9e-8 above R438, so κ is capped by the bit supplier again.

## Why a new receiver class

After PR3251, 149,514 rank-1 idle remainders remain. This package audits each of them in the final
state:

- **107,356** have an axis that fails PR1252's translation rule. They are dead under any receiver.
- **39,558** conflict with every unhosted child of their group, and all other children in the group
  are hosted.
- **2,600** conflict with every unhosted child.

Relaying through an unhosted child was also tested: move one of its own axes onward so that the
blocked axis fits. It found no legal relay on this fill.

**Change:** after PR3251's three phases, a fifth greedy phase lets an idle-remainder axis move into
the remainder of **another partially hosted bin** of the same replica and port, under the same
cost-lowering rule. The move must:

- commute with that bin's **full** recipe frame, both the hosted prefix and the current remainder;
- commute with every stage entry/exit X and Y translation and the terminal Y translation;
- commute with both children's terminal translations.

As before, no child both donates and receives, and the rank cap is 51.

This adds 2,374 moves, 437,978 in total, and mostly merges pairs of rank-1 remainders into rank-2
children. The idle bill becomes:

`{1:147220, 2:16800, 3:13337, 4:1214, 5:13415, 6:440, 42:32303, 43:1160, 44:8240, 45:32140, 46:6300, 47:20, 48:35294, 49:27626, 50:10480, 51:129006}`

Rank mass is unchanged at `65088·740`.

## Reproduce

```sh
# PR3148 materialize.py (research/coupled-carrier-cap740) -> /tmp/t740
python3 -B research/rank7-idle-hosted-receivers-r438/build.py  --t740 /tmp/t740   # ~75 s, deterministic
python3 -B research/rank7-idle-hosted-receivers-r438/verify.py --t740 /tmp/t740   # ~80 s
```

`verify.py` is PR3251's independent verifier, extended for hosted receivers, and does not import
`build.py`. It re-derives:

- donor-remainder membership for every moved axis;
- that each receiver is either unhosted, or hosted with the moved axis orthogonal to the receiver's
  hosted prefix;
- roles, unit length, orthogonality at receipt, the commuting rule and the rank cap;
- the profile and rank mass;
- the exact complex root bracket;
- the R438 endpoint, accepted at c and rejected at c + 10⁻²⁴ with the fallback envelope;
- `κ = min(floor₂₄(complex), bit) − 10⁻⁴⁶ − 10⁻⁷⁰`, with the bit side binding;
- the gates over PR3148, PR3184, PR3198, PR3200 and PR3251.

Nine mutation controls are rejected:

- an axis moved into a hosted receiver whose prefix anticommutes with it;
- an axis that does not commute;
- an axis taken from the used prefix;
- a foreign axis;
- an axis moved twice;
- a receiver that also donates;
- a dropped move;
- the next root grid point;
- κ above the bit cap.

## Scope

**New hypothesis:** a hosted bin's idle remainder may *receive* axes. This extends PR3190's
hosted-donor hypothesis. Orthogonality to the full hosted frame and the PR1252 commuting rule are
checked, but no hosted-controller argument is given. Only PR1252's unhosted pairs have an admitted
controller audit.

**Not rerun:**

- the native admission;
- the overlay-aware controller audit;
- the outer release, whose ledger pins PR589 and asserts `complex < bit`.

The result is conditional on R438, whose source PR1043 is open, and on the whole stack. All
inherited obligations remain.

## Open next questions

- **Are hosted remainders legal receivers (and donors) under the T74 controller contract?** First
  step: generalize the T74 `audit_mixed.py` to read this overlay and rerun PR3148's release.
  Blocked by: the T74 chain has no overlay reader.
- **Can R438 rise, now that the bit side binds?** The complex side leaves 1.9e-8 of headroom above
  it. First step: idle-remainder exchanges on R438's own `{34:32, 42:320}` remainders (cap 45 at
  m = 64). Blocked by: R438's per-child idle axis data.

## Credit

- PR1252 (Gonzalo-Mier): the move, the rule and the pricing.
- Guéorgui Maissouradze: the star class.
- PR3148 (Jeremy Diviney): the fill.
- PR3133 and PR3042 (dcharb78): the words.
- PR2979 (Marius-Paul Dumitrean).
- Ali Romman (PR1043) and Sagar Thakrar (PR2423): R438.
- The `r438-native-rehost` authors.
- DreamingOfClouds and eumemic.
- OpenCode (Space bunny free): the remainder-donor and exact-search ideas in the stacked
  predecessors.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
