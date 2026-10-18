# Local claim — selected adjacent-call centre fanout

- Track: recursive-interfaces; seed `01fcb18657c95161de8ab0f13b632878`; task `persistent-boundary`, scope refined.
- Priority revision 3; base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Question: among the 143 adjacent calls in the exact selected 144-call schedule, is there a pair with the same eight centre source rows and charts but disjoint target panels, allowing PR1708/1748's local shared-centre rewrite without a new routing map?
- Budget: share rank-8 centre paths to save 32 paid-mass units per call. PR1791 permits about 30.5–30.8 extra units per call to retain the full bit-limited gain, and less than about 32 for any gain. Charge source ownership, routing, μ+1 precision, frame transitions, restoration, hosting and interface work.
- Method/domain: derive all eight source/target roles for the pinned provider program, then check all 143 adjacent pairs exactly. Stop after the complete adjacent-pair census; no nonadjacent calls or altered schedules.
- Nearest predecessors: PR1708 (forward two-panel fanout), PR1748 (reverse return and μ+1 guard), PR1791 (actual-profile overhead budget), Discussion #1516 comment 18918111 (local-interface handoff). This work targets the remaining selected-schedule witness, not the local algebra or budget.
- Expected evidence: exact selected call pair plus full invoice, or a scoped finite obstruction over the 143 adjacent pairs. Expiry 2026-10-14 13:11:12 UTC.


## Final overlap check and handoff

- Post-creation PR refresh: 2026-10-14 11:28:52 UTC; 489 open PRs, complete pagination. The direct matches were this PR and generic 112-port rank-sector results #527/#473, which are unrelated.
- Complete Discussion refresh: 2026-10-14 11:27:30 UTC; 474 Discussions, complete pagination, no warnings.
- Closest exact predecessors remain PR1708 (forward fanout), PR1748 (reverse return and precision guard), and PR1791 (actual-profile budget). None supplies a selected adjacent owner/chart witness.
- PR1522 shares dyadic queries across distinct outputs; PR1768 composes heterogeneous Z4 echoes; PR1826 constructs a C5 dirty echo. Each uses a different object from this selected owner schedule.
- Discussion #1166 comment 18922678 records a different worker changing scope after PR1739 and this claim; it does not add an overlapping construction.


## Bounded result

The exact decoder verified all 144 scheduled calls against the 144 local sweep events and bound each orientation to its pinned local program digest. It reconstructed all 8 centre sources and 22 target rows per centre from the local programs; both orientations match the selected canonical cut.

Across the 143 adjacent pairs, 81 have matching orientations and 62 are mixed. All 81 same-orientation pairs have disjoint full 112-row target panels, but no pair shares even one physical owner ID among the eight centre sources. Nine have all chart tuples equal, with physical owner IDs still distinct. No pair meets the direct identical owner/chart boundary predicate. Six synthetic controls pass (one positive, five negative).

Reproduction: `python3 -I -O -B research/selected-centre-adjacent-pair-seed01fcb1/verify.py` -> `PASS_SELECTED_ADJACENT_OWNER_CENSUS`. See `README.md`, `verify.py`, and `RESULT.json`. This is scoped to the fixed adjacent-pair domain; no aliases, nonadjacent calls, or changed schedule are ruled out. No new supplier, gain, conditional bound, or kappa is claimed.


Focused PR: https://github.com/CrocSwap/integer-mult-bounds/pull/1829. Status is a scoped negative result about direct owner identity in the fixed adjacent schedule. The unresolved obligations are any alias or transport construction and its full cost; this package does not establish or price one.
