# Response-kernel entries on the gen4 word (per-entry cuts, rank-e entrances)

This package is #276's `research/five-stage-gen4-banks` with #279's concave-descent retiming stage (rohanarun,
`descent_transform.py` + `descent-selection.json`, 880 source-pair mix gates, unchanged) followed by one added
transcript stage, `kernel_transform.py`, between the descent and the five-stage lowering. The kernel selection is
bound to the descent word (input hashes); its pairs' cuts are bound by content. The descent gates act on source
registers only, the kernel pairs on 848 dirty helpers, so the two levers commute on disjoint registers. It applies PR254/#268's response-kernel helper pairs to
the gen4 bit word, which had none of the source527 lineage's entrance levers.

## Construction

Let a and b be two plain dirty helpers (initial frame ZERO, not gauges, not reuse-pair members) whose complete
F2 responses into the targets are identical (twins), and let F_a, F_b be their first frames, the frames of their
first use other than an initial compensation read. Choose a line E = <u> with u in F_a and F_b and
9|u|^2 - (sum u)^2 != 0 (nondegenerate for G = 9I - J). On gen4 every plain helper's initial reads precede its first
other use, so each pair has its own cut c(a,b): the later of the two helpers' last initial reads (reads at frame
ZERO; the helpers are also read late, at their current frames, and those reads are untouched). The rewrite:

* removes every initial read of the pivot a (its response is now supplied through the donor);
* enters a at E (initial frame E instead of ZERO);
* pays b += a at E right after the cut (`kernel_setup`) and b -= a at the full frame at the end (`kernel_restore`).

Over F2 the suffix after the cut is unchanged and the donor's accumulated correction cancels the missing pivot
reads, as in #268's KERNEL-PROOF; no estimate is used: `kernel_transform.replay` runs every formal column (19,930
source, target and dirty columns) forward and inverse on the emitted word, and rejects the omission of either new
gate category. The required frame path of every stream is rebuilt from scalar/COPY events independently of the
emitted MOVEs, both reflected (annihilator) ledgers are checked, every used frame is nondegenerate, data input/output
and dirty output frames and the 24 copied-centre lifetimes are unchanged. Per pair the paid rank mass falls by one
(the pivot enters at rank 1), two scalar ADDs are paid and the pivot's initial reads (on average 22) disappear.

## Selection and tiling

`kernel-selection.json` freezes 424 pairs (848 helpers), found by `discovery/census.py` and ordered by the concave
gain phi(r) = r ln(120/r) of the first-move ranks; all 424 have negative gain (first-frame dims (2,2), (3,3), (3,5))
and the ledger model of `discovery/pick_k.py` is maximal at K = 424. Every pair is bound by content: the helpers,
the cut read [target, helper, coefficient], the entrance line and the input hashes of the descent-retimed word (the descent selection itself binds to the parity-fused word, hash 60830cb2...).

The 424 pivots have residual rank 23. `bank_template.py` tiles their 60*424 slots with 6,360 banks (23^4, 4^7)
per stage, whose 44,520 rank-4 blocks come out of the (4^30) banks (4,400 -> 2,916); the (24^5) banks drop to
162,240. Every bank is exactly 120 wide and fully filled: 171,915 banks per stage (was 172,127), literal stock
1,281,975 (was 1,283,035), 4,923,000 assignments enumerated as before. Rank-23 charts are built by the unchanged
chart code (512 charts, at most 576 elementary factors; normalizer bound 815; selector calls 963,707,984,400 < 2^40).

## Pinned values

Every #276 literal that this rewrite changes is re-pinned in `expected/kernel-pins.json` and asserted through
`pins.pin` (a missing or different value fails): `kernel_pairs`, `kernel_local_delta`, `kernel_helper_rank_mass`,
`entrance_rank_histogram` {1:424, 20:2200, 21:266}, `entrance_count` 2890, `five_stage_calls`,
`five_stage_rank_mass`, `gauge_dimension_histogram`, `charts`, `max_chart_factors`, `removed_completion_histogram`,
`priced_five_stage_calls`, `priced_five_stage_rank_mass`, `normalizer_factor_bound`,
`conservative_extra_selector_calls`, `intentional_family_collisions` (family-only coincidences of a rank-23 and a
rank-4 slot in one mixed bank; all (family, route) addresses are distinct), `scalar_events`,
`scalar_coefficient_counts`, `scalar_event_sha256`, `forward_max_row_l1`, `inverse_max_row_l1`,
`literal_unit_additions`, `bundled_unique_bases`, `literal_stock`, `banks_total`, `kappa`. The gauge-entrance
subtraction in bank_check/math_check/finite_check uses #268's form (subtract, delete when zero) because rank-1
entrances share the five-stage bucket 5 with ordinary rank-5 children. No check is dropped.

## Result

kappa = 724733001963261/10^18 = 7.247330019632610e-4 with the 695 entries of this package (the first version, 424 e=1 pairs only, gave 7.239437286151320e-4 composed with #279's 7.23571590007464e-4 and 7.232412442944060e-4 without it), bit side binding.
Same retained interfaces as #276; no Lean, no benchmark.


## Rank-e entrances and multi-donor families (this package)

`kernel_transform.py` now admits entries {pivot p, donors D, entrance E of rank e >= 1}: twin pairs (|D| = 1) and
collective families (|D| = 2, 3; pivot response = XOR of the donors' responses, checked on the literal prefix). The
entry cut is the later of the members' last frame-ZERO reads, bound by content; the pivot enters at E (residual rank
24 - e), every donor pays d += p at E after the cut and d -= p at the full frame; a donor may serve several entries
along a nested entrance chain (the emitted MOVEs are checked nested). Correctness is still the F2 replay of all 19,930
columns forward and inverse with both omission controls. Bank tiling (`bank_template.build_patterns`, #283's rule):
for each residual width r with k_r pivots, 15 k_r banks (r^4, 4^(30-r)) of width 120, whose rank-4 blocks come out
of the (4^30) banks; the pivot residual census is pinned (`pivot_residual_census`, `bank_families`, `literal_stock`).
`code/geometry527.py` checks one actual entrance basis of every new rank (projector, 5-window completion, residual
decomposition) exactly as for the rank-20/21 entrances. Every new entrance basis gets a prime witness
(`prime_check`); all selected bases factor completely over the primes <= 31.

This package: 416 e=1 + 24 e=16 twin pairs and 255 multi-donor families (208 quads, 47 tris; 59 donors shared along nested chains) of the gen4coll selA census: 695 entries, total entrance rank 2028, residual widths 6..23. kappa = 724733001963261/1000000000000000000 = 7.247330019632610e-4.
