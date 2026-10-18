# Five-copy vacancy completion of the shared-kernel allocation

This construction uses Yiyang/Lyy-iiis’s actual PR #2857 shared-kernel words and T37 allocation at head `0b2e2537b368a0cade07ce3f71452ea018ebe394`. It preserves the native providers and constructs a literal T185 allocation. The finite owner witness and directed rational moment pass; complete native and outer admission are separate root-owned checks. All inherited sufficient hypotheses remain in force.

## Exact construction

The original T37 allocation has exactly one capacity-16 bin with unused rank 9: owner 35, child 16, port 37. Its existing role has width 7. Moving a width-9 role from a full [7,9] bin into this vacancy leaves the donor with the same unused rank 9, so it changes no paid cost. The actual relay moves helper 208 at call 320 from bin (28,16,76) to (35,16,37).

The new vacancy’s source window admits every role of the actual capacity-48 donor bin (32,13,94). This donor holds five width-9 roles at calls 292, 293, 311, 316, and 317, and has unused rank 3. The role identifiers are 17, 151, 107, 54, and 26 respectively. These are literal received rows, not hypothetical equal-width replacements.

Make five disjoint copies of the complete T37 call schedule. Interleave them in lockstep: original call t in copy b becomes call 5t+b, and every owner index is increased by 37b. Replicate the one-step vacancy relay in all five copies. Then move the five roles of one actual donor bin into the five resulting rank-9 vacancies, one role per vacancy. Their width-7 occupants remain in place. The five capacity-16 bins become full, and the capacity-48 donor becomes empty.

The exported journal has exactly ten whole-role moves. Every helper identifier and call time remains unchanged after the initial copied schedule is formed. The full recount checks the expanded bridge and source events, strict source windows, distinct physical families at each call, complete coverage of all 408 helpers per call, integral coordinates, disjoint masks, capacity bounds, used prefixes, and exact rank mass. It checks 679,320 roles in 1,665 calls, with live stock 165,760. Four invalid controls are rejected for their intended reasons. The copied source-event projection is exactly the original 30-event projection for each of the 185 replicas; it is checked explicitly rather than inferred from the lockstep construction.

## Sufficient paid-cost proof

Relative to five complete incoming PR #2857 profiles, the exact paid difference is

    H_48 − H_3 − 5 H_9.

The rank mass is unchanged because 48 = 3 + 5·9. For every 0 < p < 1 and positive a,b, strict subadditivity gives (a+b)^p < a^p+b^p. One proof writes b=ta and differentiates g(t)=1+t^p−(1+t)^p: g(0)=0 and g′(t)=p(t^(p−1)−(1+t)^(p−1))>0. Repeated application proves 48^p < 3^p+5·9^p. Thus the complete paid power cost decreases strictly, with no discarded idle charge.

The outgoing profile is

    {1:4029300, 2:1068930, 3:458874, 4:213120,
     5:65490, 8:13320, 48:66896}.

It is exactly 185 times the fractional packing support. The separate exact primal/dual checker subsequently verified all 1,163 capacity-feasible patterns, including 11 symbolically tight patterns, and certified equality of the actual profile with the fixed-inventory fractional optimum throughout the root interval. Thus this construction attains that packing bound for the fixed capacities and native inventory. This does not bound changed native words, alternate controllers, or all suppliers.

The directed rational root bracket is [0.00172010080541688592794400, 0.00172010080541688592794401]. The conservative 24-digit target is 0.001720100805416885927944 − 10^−46 − 10^−70. The exact comparator is the full incoming PR #2857 rational, whose claim file has SHA-256 `c2a04b639c86f462caef654a29817545c57b8e5ba809e37d4d476d3577f5cd6f`. The gain is approximately 4.17673205333 × 10^−9. The finer bracket is an independent interval result; the final outer receipt determines the completed release precision.

## Reproduction and limits

`reproduce_t185.py` takes `--baseline`, `--relay-plan`, and `--out`. It authenticates the six PR #2857 source inputs and the actual source template and plan before writing a fresh destination. The candidate is generated without a solver. Its output fill, order, dispatch, providers, and profile must match the frozen candidate hashes. The source fixture directory can be flat or retain the upstream `sources/` subdirectory. The immutable relay plan is RELAY-PLAN-5.json. Root-owned independent audits and complete admission supplement this constructor’s own checks.

The T37 same-call greedy, neutral-exchange, and two-exchange screens found no paid improvement. The actual two-copy merge was checked and improved the prior claim, but the five-copy construction gives the stronger selected result. Direct three-copy donor transfer failed the original late source windows; a two-step relay plan was found, but no complete three-copy literal export was checked because the stronger five-copy witness was already available. No global maximum over changed native words is claimed.

## Attribution

Credit Yiyang/Lyy-iiis for PR #2857’s staged shared kernels, cheaper local profile, actual T37 fill, and PR #2848’s residue concentration. Credit Marius-Paul Dumitrean/mdumitrean’s PR #2856 for the related paid-profile-preserving vacancy-path method, and PR #2843’s allocation transport. Philippe Van Velzen’s PR #2853 treats the same four A-phase helpers through a different schedule. Jeremy Kothe’s PR #2833 supplies the preceding dirty-entry words. Dugongue’s PR #2855 and the retained Tekalign/Dugongue checker lineage supply prior atlas applications and independent-checking work. Preserve all upstream notices and licenses. No exclusive helper-selection or global novelty claim is made.
