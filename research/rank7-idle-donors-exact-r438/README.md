# Exact per-group idle-donor search on PR3200: conditional κ = 0.001734815770385098563484 − 10⁻⁴⁶ − 10⁻⁷⁰

**Author-checked conditional candidate; not maintainer-reviewed.** This package stacks on the open PR3200, which stacks on PR3198, PR3190, PR3184, PR3148 and PR3133. PR3133's words and PR3148's fill rows, order and dispatch are unchanged. Only the idle-axis donor moves change.

**Idea credit: OpenCode (Space bunny free).** The idea is to replace PR3200's greedy phase-1 selection with an exact search inside each (replica, port) group.

| | complex root lower | bit endpoint | binds | κ headline |
|---|---|---|---|---|
| PR3200 | 0.0017348070217261275520343 | R438 0.001734846264120199151475 | complex | 0.001734807021726127552033 − … |
| **this** | **0.0017348157703850985634843** | R438 0.001734846264120199151475 | complex | **0.001734815770385098563484 − …** |

The gain over PR3200 is **+8.7487e-9**, exactly `174973179420229/2·10²²`. About 3.05e-8 of headroom to the R438 bit endpoint remains.

## What changes

PR3200's three phases run per (replica, port) group:

1. drain hosted remainders greedily;
2. stars: PR3184's exact optimum on fully idle 48s;
3. greedy single-axis moves between unhosted children.

Phase 1 is replaced by a **memoised exact search**:

- **Choices.** Every hosted-remainder axis either stays put or moves to any unhosted receiver where it is legal.
- **Legality.** This is PR1252's commuting rule:
  - the axis commutes with the receiver's axes held at that moment;
  - it commutes with all stage entry/exit X/Y translations and the terminal Y translation;
  - it commutes with both children's terminal translations.
- **Cap.** Receivers stay at rank ≤ 51.
- **State.** Item index, the set of axes received per receiver, and the number of axes moved per donor.
- **Scoring.** Each terminal state is scored by the **final** group cost Σ Hf(rank). That cost is computed after running phase 2 (optional: both with and without stars) and PR3200's unchanged phase 3 on that state. So phase 1 is chosen for the group's end cost, not its own.

Two findings shaped the patch:

- **Phase 1 alone was already optimal.** An exact phase 1 that minimises only its own cost reproduces PR3200's moves exactly (430,164 moves, same κ).
- **The gain is from the joint scoring.** Scoring with phases 2 and 3 included, and letting a group skip stars when that is cheaper, gives the improvement.

The result is 435,604 axis moves. The idle bill becomes:

`{1:149514, 2:15880, 3:14951, 5:13855, 42:32303, 43:1160, 44:8240, 45:32140, 46:6300, 47:20, 48:35294, 49:27626, 50:10480, 51:129006}`

Rank mass is unchanged at `65088·740`. The maximum child rank is 51, and the halving check gives [5329, 5202].

## Reproduce

```sh
# PR3148 materialize.py (research/coupled-carrier-cap740) -> /tmp/t740
python3 -B research/rank7-idle-donors-exact-r438/build.py  --t740 /tmp/t740   # ~1 min, deterministic
python3 -B research/rank7-idle-donors-exact-r438/verify.py --t740 /tmp/t740   # ~70 s
```

`verify.py` is PR3200's independent verifier, which does not import `build.py`. Only the status string is renamed and a PR3200 gate is added. Every legality, profile, rank-mass, root-bracket and bit check is unchanged.

The run outputs `PASS_IDLE_DONOR_EXACT_R438_AUDIT moves=435604 controls=8 kappa=0.0017348157703850986 binding=complex`, with all 8 mutation controls rejected. As a cross-check, PR3200's **unmodified** `verify.py` also passes on these BINS, MOVES and RESULT files.

`build.py` is byte-deterministic: two runs give identical BINS, MOVES and RESULT files.

## Open next questions

- **Do hosted donors and multi-donor receivers satisfy the T74 controller contract?** First step:
  generalize the T74 `audit_mixed.py` to read the idle-axis overlay and rerun PR3148's release.
  Blocked by: the T74 chain has no overlay reader.
- **Can the remaining 3.05e-8 to the R438 bit endpoint be closed?** The exact search is optimal
  over legal single-axis donor moves; the residual is blocked by PR1252's commuting rule. First
  step: prototype chained/relay donor swaps or port axes re-anchored outside the translation span,
  with the commuting rule strictly enforced. Blocked by: no such move class is specified yet.
- **Can the bit endpoint rise past R438?** First step: test helper removals outside PR1043's
  pure-relay class. Blocked by: PR1043's lifetime test only certifies 2-occurrence relays, and
  R438 depends on the open PR1043.

## Scope

This is conditional on PR3200's stack and on R438, whose source PR1043 is open. It inherits PR3200's scope:

- the hosted-remainder donor hypothesis and multi-donor receivers rely on PR1252's per-axis rule;
- only unhosted pairs have an admitted controller audit;
- native admission, the overlay-aware controller audit and the outer release were not rerun.

All inherited obligations remain. The remaining 3.05e-8 to the bit endpoint is blocked by axis legality, not by search: about 99% of blocked moves fail the commuting rule. Recovering it needs a new move class, such as chained or relay donor swaps.

Credits: the idea is from OpenCode (Space bunny free). The base is PR3200, PR3198 and PR3190 (rohanarun). Also: PR1252 Gonzalo-Mier; star class Gueorgui Maissouradze; PR3148 Jeremy Diviney; PR3133 dcharb78; PR1043 Ali Romman; PR2423 Sagar Thakrar. Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
