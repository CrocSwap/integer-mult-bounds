# Greedy idle-axis phase on PR3198: conditional κ = 0.001734807021726127552033 − 10⁻⁴⁶ − 10⁻⁷⁰

**Author-checked conditional candidate; not maintainer-reviewed.** The selected record on
`main` is still #1094. This package stacks on the open PR3198, which composes PR3190's
idle-remainder donors with the R438 bit supplier. PR3133's words and PR3148's fill rows, order and
dispatch are unchanged.

| | complex root lower | bit endpoint | binds | κ headline |
|---|---|---|---|---|
| PR3198 | 0.0017347705571115131604951 | R438 0.001734846264120199151475 | complex | 0.001734770557111513160495 − … |
| **this** | **0.0017348070217261275520343** | R438 0.001734846264120199151475 | complex | **0.001734807021726127552033 − …** |

The gain is **+3.646e-8 over PR3198**. That closes about half of PR3198's window
to the R438 bit endpoint.

## What changes

The construction keeps PR3190's two phases and adds a third:

1. **Drain hosted remainders** smallest first into the largest legal unhosted receiver.
2. **Stars:** PR3184's exact optimum on the untouched fully idle 48s.
3. **New greedy phase:** repeat the single best one-axis move from a smaller unhosted child to an
   equal-or-larger unhosted receiver, as long as it lowers the moment cost.

Every move obeys PR1252's commuting rule:

- it commutes with the receiver's axes at that moment;
- it commutes with every stage entry/exit X and Y translation and the terminal Y translation;
- it commutes with both children's terminal translations.

Receivers stay at or below rank 51. No child both donates and receives.

The result is 430,164 axis moves. The idle bill becomes:

`{1:149514, 2:15880, 3:14951, 5:13855, 42:32303, 44:5120, 45:36420, 46:6300, 47:20, 48:35294, 49:28786, 50:13600, 51:124726}`

Rank mass is unchanged at `65088·740`.

### Variants tested

| Variant | Complex root |
|---|---|
| Phases 1 + 2 (PR3190) | 0.0017347706 |
| Phases 1 + 2 + 3 (this package) | **0.0017348070** |
| Phase 1 + greedy only, no stars | 0.0017347935 |

Fully idle cap-32/16/8 children do not exist in this fill. Rank-1 remainders, the last
coordinate of a 48-bin, conflict with every other 48 child's axes, so they stay blocked.

## Reproduce

```sh
# PR3148 materialize.py -> /tmp/t740
python3 -B research/rank7-idle-donors-greedy-r438/build.py  --t740 /tmp/t740   # ~20 s
python3 -B research/rank7-idle-donors-greedy-r438/verify.py --t740 /tmp/t740   # ~70 s
```

`verify.py` does not import `build.py`. It re-derives:

- every move's donor-remainder membership, receiver hosting status, roles and the commuting rule;
- the rank cap;
- the profile and rank mass;
- the exact complex root bracket;
- the R438 bit endpoint, from its certificate's own bit profile with the fallback envelope
  (accepted at c, rejected at c + 10⁻²⁴);
- `κ = min(floor₂₄(complex), bit) − 10⁻⁴⁶ − 10⁻⁷⁰`, checking that the complex side binds;
- the gates over PR3148, PR3184 and PR3198.

Eight mutation controls are rejected. The run checks against the committed `AUDIT.json` without
writing to it.

## Scope

This is conditional on PR3198's stack: PR3190, PR3184, PR3148 and PR3133. It is also conditional
on R438, whose source PR1043 is open.

The hosted-remainder donor hypothesis and the greedy single-axis chains (a child receiving from
several donors) rely on PR1252's per-axis rule. Only unhosted pairs have an admitted controller
audit. The native admission, the overlay-aware controller audit and the outer release were not
rerun. All inherited obligations remain.

## Open next questions

- **Do hosted donors and multi-donor receivers satisfy the T74 controller contract?** First step:
  generalize the T74 `audit_mixed.py` to read the idle-axis overlay. Blocked by: the T74 chain has
  no overlay reader.
- **Can the remaining 3.9e-8 to R438 be closed, and can R438 itself rise?** First step: exact
  per-group optimisation instead of greedy, and idle exchanges on R438's own
  `{34:32, 42:320}` remainders. Blocked by: the cost of the per-group search, and R438's per-child
  axis data.

## Credit

- PR1252 (Gonzalo-Mier): the move, the rule and the pricing.
- Guéorgui Maissouradze: the star class.
- PR3148 (Jeremy Diviney): the fill.
- PR3133 and PR3042 (dcharb78): the words.
- PR2979 (Marius-Paul Dumitrean).
- Ali Romman (PR1043) and Sagar Thakrar (PR2423): R438.
- The `r438-native-rehost` authors.
- DreamingOfClouds and eumemic.

Prepared by Rohan Arun. Done with help from **OpenCode (Space bunny free)**, with Anthropic
Claude assistance. Apache-2.0.
