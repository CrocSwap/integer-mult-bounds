# Pooled R438 slack across bit replicas: conditional κ = 0.001734865178472710998233 − 10⁻⁴⁶ − 10⁻⁷⁰ (+0.00109%)

**Author-checked conditional candidate; not maintainer-reviewed.** The selected record on
`main` is still #1094. This package stacks on the open PR3934, which is bit-bound at the R438
endpoint.

| | complex endpoint | bit endpoint | binds | κ headline |
|---|---|---|---|---|
| PR3934 | 0.0017348651784727109982331 | R438 0.001734846264120199151475 | bit | 0.001734846264120199151475 − … |
| **this** | 0.0017348651784727109982331 | **pooled R438 0.001734900431583947157341** | **complex** | **0.001734865178472710998233 − …** |

The gain is **+0.00109% over PR3934**. The complex side binds again, now 3.5e-8 below the pooled bit
endpoint.

## Idea

R438 has 54 width-8 slack units per replica: Ali Romman's PR1043 word, re-hosted by Sagar
Thakrar's PR2423 under the PR1023 slot model. Its proven replica-local optimum is 10 empty
capacity-42 copies plus one capacity-42 copy holding one residual, which leaves an idle 34.

Pooled over the 32 replicas, `32·54 = 345·5 + 3`. The pooled32 slot-model optimum is then 345 empty
42-copies plus one empty capacity-28 copy. mightyOil's `bit-partial-width7-optimum` already proves
this; its k = 1 row gives 0.001734900431583947. That package and seed72's window audit both leave
open whether a **cross-replica owner map** can realize it. The complex T16 supplier already uses
such maps (`owner_replica ≠ replica`).

This package builds the map explicitly from R438's own placement, with 35 moves:

- the 32 single residuals, one per replica, all in child 6;
- the three residuals of one full capacity-28 copy of replica 0, in child 7 (stages 5–8, inside
  child 6's window 3–8).

They go into seven previously empty child-6 copies of replicas 0–6, five per copy. The idle bill
changes by `{2:+7, 4:−1, 28:+1, 34:−32, 42:+25}`. Rank mass, the 904,320-child count and maxchild 42
(`2·42² < 64²`) are unchanged.

## Verification

```sh
python3 -B research/rank7-pooled-r438-bit/build.py    # writes POOL-MOVES.json
python3 -B research/rank7-pooled-r438-bit/verify.py   # ~7 s, independent of build.py
```

- **Inputs.** `ALLOC-R438.json.gz` is R438's per-replica placement. Its SHA-256 equals
  `slot_list_sha256` in `research/bit-r438-transport-rehost/verify_rehost.receipt.json` on main.
- **Role audit.** `verify.py` rebuilds all 126,144 hosted roles (32 replicas × 9 stages × 438
  helpers) and applies the moves. It checks every role against R438's slot rules:
  - the host child's window contains the stage;
  - the host pair is inactive at that stage;
  - the width is 8 and fits the capacity;
  - cells are disjoint and prefixes are compact;
  - every (stage, replica, helper) is hosted exactly once.
- **Baseline.** The rebuilt baseline equals the R438 certificate's bit profile, and its endpoint
  is accepted at c and rejected at c + 10⁻²⁴.
- **Pooled endpoint.** The pooled endpoint is accepted at 0.001734900431583947157341 and rejected at
  the next 10⁻²⁴ point, with the 10⁻¹⁶·32m² fallback envelope.
- **Composition.** PR3934's complex root bracket is rechecked, and
  `κ = min(floor₂₄(complex), floor₂₄(bit)) − 10⁻⁴⁶ − 10⁻⁷⁰`.
- **Controls.** Six mutation controls are rejected: a move outside the window, a cell collision, a
  wrong source, a dropped move, the next grid point of the pooled endpoint, and κ off the grid.

## Scope

**New hypothesis:** the bit supplier may use a cross-replica owner map. The slot rules are audited,
but PR1043's native hosted emission (C++17/Boost) was not run, and the bit hosted audit has so far
checked only replica-local owners. The result is conditional on R438 (PR1043 is open) and on the
whole PR3934 stack, including its hosted-donor and hosted-receiver hypotheses. All inherited
obligations remain.

## Open next questions

- **Does R438's native hosted emission accept this cross-replica owner map?** First step: run
  PR1043's native lane with this owner list. Blocked by: C++17/Boost and cross-replica support in
  the bit emitter.
- **Further bit pooling.** The complex side now binds 3.5e-8 below the pooled bit endpoint. Further
  bit pooling, such as width-7 conversions or the deletion-ladder words, only matters once the
  complex side rises.

## Credit

- Ali Romman (PR1043): R438.
- Sagar Thakrar (PR2423): transport and re-hosting.
- mightyOil (PR1281): the pooled32 optimum.
- seed72 and seed14: windows and placement.
- PR1023: the slot model.
- The `r438-native-rehost` authors.
- The PR3934 stack and its credits, including OpenCode (Space bunny free) for ideas in the stacked
  predecessors.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
