# Local task card (autoresearch.md section 3)

Task ID / proposed scope key: `selected-packing` (catalogue scope key
`ab5d8f0f0d19bbab8625`, chooser seed `5faf82d91e84b5186f43a7c029914c43`,
track `incumbent-optimization`, priority revision 3); refined scope key
`ab5d8f0f0d19bbab8625:PR1094:two-role-swap:fixed-windows:concavity`.

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; exact predecessors and
dependency heads: selected PR1094 audited head `0fc329d0bec93ca7cd288eaea1295172e8789810`,
PR1087 `589d1cedf5ef5f231182f4ec86408616311a8af0` (via
`research/community-frontier1094-audit/SELECTED-SOURCE.json` and
`certificates/selected-result.json`).

Concrete object and question: on the **selected PR1094 owner map** (the exact
map of `research/complex-t16-rare-pattern-exchanges/`), fix all 144 call times,
helper widths, source-event windows and the local paid word. Consider the move
class of **unordered two-role whole-helper swaps**: two roles in distinct owner
bins exchange bins (prefix compaction allowed in both slices). Is there a legal
swap that strictly lowers the idle moment for every real `0 < a < 1`? If not,
give the exact obstruction as a complete census of this move class.

Scope status: **refined** within the card's allowed variation "one bounded
residual packing instance or exact relaxation". Reason: the nearest complete
census (`research/frontier1094-single-relocation`) covers one-role relocations
and explicitly lists "swaps" among its non-exclusions; heuristic whole-helper
exchanges (`research/complex-t16-*`) are search bests, not an exact census.

Existing restriction being changed (or exact claim being audited): the
selected map's single-move local optimality is known only for one-role
relocations; this audits the next named move class on the same inputs.

Method; explicit parameter ranges/candidate alphabet: exact integer class
counting over the 69,120 hosted roles by (own-bin remainder, width), widths
{4,5,7,8,9}, bin remainders {0,1,3,7,48}, 16 owner replicas, 144 calls. A swap
moves net rank `d = w1 - w2` between bins with remainders `x1, x2`; with
`p = 1 - a` the moment sign is uniform on `0 < a < 1` and decided by comparing
the new maximum remainder with the old one (strict concavity, exact integer
comparison). Every capacity-feasible strictly improving pair is materialized
and checked against the strict source-event windows, the active-pair
restriction and per-call family uniqueness.

Nearest overlapping PRs and why this adds something: PR1240
(https://github.com/CrocSwap/integer-mult-bounds/pull/1240) computes a
fractional packing ceiling, not a move census; PR1091
(https://github.com/CrocSwap/integer-mult-bounds/pull/1091) audits the owner
geometry (reused, credited); `research/frontier1094-single-relocation`
(single-role class) and `research/selected1094-idle-reassignment` (idle-axis
relaxation) cover different classes. Refreshed `find_overlap.py` runs over
"whole-helper swap", "two-role swap", "swap census", "pair exchange idle
remainder", "selected owner map swap", "improving swap" returned 0 matches at
2026-10-14T09:31Z (complete pagination); no match is not a novelty certificate.

Optimistic full cost budget; required observable improvement: any swap changes
only the idle histogram of the fixed word, so its gain is bounded by the
packing ceiling (`research/complex-local-word-ceiling`, cap
kappa < 0.001687202646, +0.87% over the selected kappa). The required
observable is either one legal strictly improving swap (exact new map, idle
histogram recounted, priced against that cap) or an exact obstruction of the
whole class. The linear `a < D/E` supplier diagnostic does not apply to a
fixed-word repacking; the packing ceiling is the applicable budget.

Success evidence; falsification test; time/compute cap: a reproducible
certificate with the complete class table, every materialized improving pair
and its rejection reason, plus a positive fixture (a legal worsening swap whose
improving inverse the census detects) and inherited owner mutation controls.
One bounded census pass; no heuristic search; no rerun with new seeds.

Predecessor authors; intended artifact and reproduction command: selected
construction Rohan Arun (PR1094) and its retained lineage; owner geometry and
baseline checker Josie Elliston (PR1091, `research/t16-owner-audit-seed67`);
one-role census `research/frontier1094-single-relocation` (prepared for
@Arham-Tahir64). Artifact: `research/frontier1094-swap-census/` (README,
CERTIFICATE.json, SOURCES.json, TASK.json, verify.py, test_verify.py).
Reproduce: `python3 -I -O -B research/frontier1094-swap-census/verify.py` and
`python3 -B scripts/research_package.py --package research/frontier1094-swap-census`.
