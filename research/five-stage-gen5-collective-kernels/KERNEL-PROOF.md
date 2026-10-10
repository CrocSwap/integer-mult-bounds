# Response-kernel entries on the gen5 word (per-entry cuts, rank-e entrances, multi-donor families)

This package is #287 (rohanarun: #285's gen5 five-stage banks + 904-gate descent retiming + 220 target-prefix squares)
with one added transcript stage, `kernel_transform.py`, after the target squares and before the five-stage lowering.

## Construction
Entries {pivot p, donors D (1 = twin pair, 2-3 = collective family), entrance E of rank e >= 1}: the pivot's complete
F2 target response is the XOR of the donors' (checked on the literal prefix); E is nondegenerate for 9I-J and lies in
every member's first frame. The entry cut is the later of the members' last frame-ZERO compensation reads (bound by
content: cut_read = [target, helper, coefficient]); no member is touched before it. The pivot starts at E (residual
rank 24-e) and loses its initial reads; each donor pays d += p at E after the cut and d -= p at the full frame; a donor
may serve several entries along a nested entrance chain (emitted MOVEs checked nested). Correctness: F2 replay of all
19,406 formal columns forward and inverse, both omission controls rejected; every required frame path rebuilt from
scalar/COPY events independently of the emitted MOVEs; both reflected ledgers; all used frames nondegenerate.
The selected helpers are plain dirty helpers; #287's target squares act on targets reading rank-20 gauges and its
retimed gates on source-pair mixes and internal gates, so the stages compose (the selection is bound to the
post-target word's hashes and the census was run on that word).

## Selection (discovery/)
Twin census (twin-census.log) and collective census (coll/: families.py, fameval.py, pack.py adapted from the gen4
collective census): 450 entries = 260 twin pairs (244 e=1, 16 e=3) + 190 families (151 quads, 39 tris), total
entrance rank 1022, ranks 1..18. Greedy phi packing (phi(r) = r ln(120/r)), best prefix on the package's own ledger.

## Banks
`bank_template.build_patterns` keeps gen5's base patterns (7^12,4^9)x10, (3^40)x531, (6^20)x48 and, for each pivot
residual width r with k_r pivots, adds 15 k_r banks (r^4, 4^(30-r)) (#283's rule) whose rank-4 blocks come out of
the (4^30) banks; the (24^5) banks hold the remaining full-residual helpers. Pivot widths 6 and 7 coexist with the
base rank-18/17 gauges of the same widths. Every bank is 120 wide and fully filled; all assignments are enumerated.

## Pinned values
Every #287 literal changed by the rewrite is re-pinned in expected/kernel-pins.json and asserted via pins.pin
(recorded by discovery/generate_pins.py; verify.py refuses recording mode): kernel_pairs, kernel_entries,
kernel_entrance_rank, kernel_local_delta, kernel_helper_rank_mass, entrance_rank_histogram, entrance_count,
five_stage_calls, five_stage_rank_mass, gauge_dimension_histogram, bank_families, pivot_residual_census,
literal_stock, banks_total, charts, bundled_unique_bases, max_chart_factors, removed_completion_histogram,
priced_five_stage_calls, priced_five_stage_rank_mass, normalizer_factor_bound, conservative_extra_selector_calls,
intentional_family_collisions, scalar_events, scalar_coefficient_counts, scalar_event_sha256, forward/inverse
max row l1, literal_unit_additions, kappa. Gauge-entrance subtraction uses the subtract-and-delete form because
rank-e pivot entrances share five-stage buckets with ordinary children. No check is dropped.

## Result
kappa = 186178624839407/250000000000000000 = 7.447144993576280e-4 (+0.080% over #287's 7.44120696397042e-4),
bit side binding (bit coarse below the complex supplier's 7.47454944651775e-4).
