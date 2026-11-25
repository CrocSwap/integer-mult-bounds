# Lead 1: one join swap and a T360 whole-helper allocation

The finite construction preserves Ross Richardson's staged-width suppliers from #3605 and hexapode's T37/T8 source orders retained in #3624. In the concatenated45-replica clock, exchange adjacent calls `(stage8,replica36)` and `(stage0,replica37)`, at grouped times332/333. Per-replica progression is unchanged. Recompute source windows from the actual event template, then use eight copies of this45-replica clock.

## Source-derived opportunity

Exactly three aggregate source-window groups change. For capacities16/32/48 and lower endpoints317/284/232 respectively, the upper endpoint moves332→333; each group contains224 physical bins. The initial global lower boundary remains−1. No window is inferred just by shifting a claimed group. The new exact certificate uses this extra time: at grouped time333, the capacity16 group hosts416 width7 and192 width8 roles; the capacity32 group hosts208 width4,16 width5,144 width6 and584 width8 roles (counts across all eight copies). Thus reverting this certificate's clock without changing the allocation violates source windows. We make no claim that this swap is necessary for every allocation or that either clock is optimally packed.

The source suppliers remain the arbitrary-dirty, both-orientation staged644/660 words of #3605. Their private buffers and full terminal frames remain. The exact ordinary helper inventory is `{4:26,5:2,6:18,7:52,8:97,9:213}`; per-call paid local profile is `{1:2439,2:726,3:224,4:102,5:20,8:8}`. No earlier width or T8 gains are added a second time.

## Exact integer construction

CHRONOLOGY-CANDIDATE.json contains complete integer pattern counts and source-window flows at S=8. `chronology_check.py` independently recomputes the45-replica groups from authenticated source geometry, checks per-width supply at every call, one role per physical group/bin per call, pattern capacity and total slot count≤S. It checks disjoint windows for children sharing a physical family. The floating LP was only discovery; its numerical optimality and reduced costs are not claimed or required for replay. All positive entries reconstruct with denominator4; S=8 accommodates the maximum five-slot bin. This is a feasible exact primal, not an optimum or minimal-copy theorem.

`literal_build.py` applies the retained integral lower-bound network decomposition. With R copied calls remaining, assigning each remaining role fraction1/R meets all width quotas, per-bin unit capacity and future group degree bounds. Integral flow chooses the next copy. Sorting bins by their latest required copy at the upper endpoint chooses a physical owner copy that remains available. Eight copies are eight successive actual calls at each grouped time; multiple roles may share a grouped time if their actual calls differ.

The literal reconstruction has3240 calls and1,321,920 individually assigned helpers. The retained scalar owner audit checks every role against actual windows, capacity, compact prefix masks and physical family uniqueness. Its historical `physical=live+490` field is not the new stock invoice; the actual private stock is509, verified separately below. The separate `independent_literal.py` imports neither the producer nor its source-window function. It reconstructs source windows directly from the event JSON and derives every helper's width from the freshly checked native canonical frame tables. Its full-family/compact-prefix/invoice check and five semantic controls pass on all roles.

## Paid profile and exact comparison

The completed profile is

`{1:7986600,2:2352240,3:749250,4:330480,5:69930,8:25920,48:137790}`.

Rank mass is exactly`65088*360=23431680`. For the retained width73 and live stock`896*360`, price

`F(k)=sum_r n_r*(r/73)^(1-k)/(896*360)`.

All occupied ranks are positive and below73, so F is strictly increasing; F(0)<1. Exact rational log/exp enclosures from the attributed retained price engine certify the crossing in

`[0.001730096363528623534230,0.001730096363528623534231]`.

The finite intended outer endpoint is the lower endpoint minus`10^-46+10^-70`; the complete original source-bound release passed at that exact endpoint.

Normalized comparison against #3624 (T450) gives nonzero signed coefficients

`450*new_profile −360*old_profile = −118800 H1−5940 H3−29700 H5+5940 H48`,

where Hr=r^(1−k). Rank mass cancels. The exact upper bound on this difference is negative at the old root's upper endpoint. This yields about`4.88114352794e-8` more κ than #3624.

The later live #3626 (T530, head659fd5e7064d9466b668d7188cbb013b333a415a) reports the stronger predecessor endpoint`0.001730071864705779882540−10^-46−10^-70`. Its exact EXPECTED/CLAIM/CREDITS bytes are retained under comparators/. `price_check.py` also certifies a strict normalized paid-cost decrease against that profile and a root improvement of at least`2.4498822843651689e-8`. These predecessor claims are author-checked conditional candidates, not newly selected results or independently replayed suppliers here. Challenged #3184/#3190/#3251 endpoints are not comparators.

## Complete boundary and cost ledger

| Obligation | Construction / evidence |
|---|---|
| Source word / native operations | Unchanged staged644/660 words; exact648-file source manifest318ede57… retained through PR3624 source builder |
| Source acquisition / chronology | Actual9-stage event windows recomputed; three upper endpoints extended as above |
| Logical helper inventory |408 roles per call, both ordered provider-width arrays authenticated |
| Whole-helper physical owners | Fresh1,321,920-row literal fill; strict/closed windows, capacity, family uniqueness and prefix masks checked |
| Dirty maps / both orientations | Fresh five-stage native base+extra chains; exact all-column warp/control proofs, arbitrary incoming logical helper maps; no relaxed restore210 endpoint |
| Private/physical stock |`896*360+408+8+91+2=323069`; all91 buffers retained |
| Local recursive work | Complete local profile above, included3240 times |
| Remaining idle children |`{1:84240,3:23490,5:5130,48:137790}`, fully charged |
| Physical norm / precision | Original stock checker; stock exponent1323 and conservative reserve`128+37+18+1323+1+4=1511<2048`; actual prefix must pass full release |
| Scalar/Horner work / restoration | Unchanged source driver; full arbitrary-column, helper-data-zero, centre-clear, buffer-zero obligations remain in admission |
| Both supplier caps / outer | New complex crossing is below the retained bit cap; exact outer ledger and final release must pass |
| Full conditional theorem | Inherited all-size/compiler, common-label/mutable-source, uniform cost, hosting, bootstrap-time, precision/recovery/tape, analytic and bit assumptions remain |

## Reproduction and provenance

Retained dependency: #3624 head515a7c4490aa32ac3ca5014feb6f7da0d6952863, complete package bytes in PR3624-SOURCE.tar.gz; its per-file SHA256/Git blob IDs and archive hash are in PR3624-SOURCE.json. The new source loader extracts only authenticated regular members into a fresh temporary directory. No unmerged Git object or network fetch is needed for its code/data at replay time. Main-tree inputs and T8 materialization closure are in SOURCES.json. All predecessor notices and credits remain in the retained archive. #3626 contributes comparison data only.

Finite checks: `python3 -B research/three-kappa-leads/chronology_check.py`, `price_check.py`, and `aggregate_controls.py` in the same directory. Literal generation: `python3 -B research/three-kappa-leads/literal_build.py --out /fresh/owners --owner-check`.

Complete cold command (Python3.12 with numpy1.26.4, scipy1.15.3, sympy1.14.0, mpmath1.3.0 installed in that interpreter's site-packages so isolated subprocesses can import them):

`python -B research/three-kappa-leads/full_replay.py --work /fresh/release`

The completed coverage, exact commands, original failed environment attempt and whether the complete cold CLI was itself run end-to-end are reported in VALIDATION.json, separately from stored receipts. Authenticated same-session fresh-native reuse is supported explicitly, with exact original materializer file checks and derived-driver pins; full admission authenticates source/cache/receipt bindings again.

## Open next questions

Do other bounded join changes or complete allocations improve this new profile? First recompute exact source windows and an optimistic full bill; require an integer primal before literal expansion. No optimality claim here justifies a census. The unrelated unresolved theorem-level premises remain independent research obligations and are not discharged by a new finite allocation.

Credit Ross Richardson/#3605 and the retained integral-network/source lineage; hexapode/#3494 and #3624 for T8, combination and admission machinery; #3626 for the stronger live comparison; all original authors retained in their source notices. New join experiment, integer certificate, adapted checks and package by OpenAI Codex with substantial AI assistance. Independent Astra review is a separate scoped AI check, not human or formal acceptance.

## Final freshness correction and fixed-model stopping result

At11:42:53UTC the live refresh found concurrent #3633, head72c268f113368ea0387d188225e3f81ba6d6ef73, with exactly this endpoint and normalized profile at T488. No claim to exceed that candidate or own the first attainment is made. Its1,791,936 roles and437,757 physical families exceed ours by470,016 and114,688 respectively. The complete source/native/physical/precision/outer release of our T360 construction passed. This supports a smaller matching-frontier contribution.

PR3630 independently supplied an all-T fixed-inventory packing ceiling; #3633 supplied a primal/dual attainment certificate. We retain the latter's exact dual data and attribution under comparators/. Our independently written ceiling_check.py uses the earlier PR3624 rational moment engine, not the new published ceiling interpreter, and recomputes all2,551 patterns at OUR exact upper24-place grid point0.001730096363528623534231. It verifies12 symbolic zero reduced costs,2,539 strictly positive rational lower bounds, all primal equalities, and equality with our exact per-replica profile. The independently certified positive moment at that upper grid point bounds every relaxed profile in this fixed model.

The capacity/width constraints scale linearly with any positive integer T. Removing chronology, physical families and integrality only improves the relaxation, so this dual also bounds all such legal fixed-model constructions. Every positive rank is below73 and its normalized cost increases with the exponent. Thus no admissible fixed-model root reaches the next24-place grid point. Since our released C is the preceding grid point, no further packing/chronology search within these capacities, widths, local bill, nine-call/live896T normalization and SAME24-place transfer recipe can increase the released endpoint. This is a scoped stopping result; different precision/outer choices or changed suppliers/interfaces are not excluded. Any possible remaining real-root slack below the next grid point is less than10^-24, not a new useful chronology opportunity.

Lead1 therefore yields LOCAL_PROGRESS (full smaller frontier match) and a scoped negative for a strict new24-grid κ increase in this fixed supplier model. It does not satisfy SUCCESS_KAPPA against the refreshed concurrent candidate. The scope revision is due to new public evidence, not elapsed time or an unsuccessful search. A focused submission-ready PR should advertise the smaller construction and preserved credit.
