# Packing ceiling for the changed 408-helper supplier

This certificate concerns one fixed supplier and capacity model. The widths are (4,5,6,7,8,9), their per-call inventory is (26,2,18,52,97,213), and the supplier's paid local profile is 2439H1+726H2+224H3+102H4+20H5+8H8. There are nine calls per replica and respectively (672,448,448,448) bins of capacities (8,16,32,48). Here H_r(a)=r^(1−a).

Every nonnegative integer pattern that fits one bin is enumerated: 2,551 patterns. The certificate contains a feasible rational primal basis and ten dual coefficients, each expressed as a rational linear combination of H_r. At the recorded rational upper root endpoint, the verifier proves all dual inequalities by rational log/exponential intervals. Twelve reduced costs vanish symbolically; the other 2,539 are strictly positive. The primal uses tight patterns and satisfies all ten equalities exactly, establishing the fractional minimum at that exponent.

The supplied T488 aggregate is bound by its canonical scientific-field SHA-256 (baseT, S, order, dispatch, groups, widths, inventory, local_profile, x, z, profile). The verifier independently checks its bin counts, width totals, idle cost, full paid profile, and tightness of every used pattern. Its per-replica profile equals the primal optimum:

22185H1 + 6534H2 + (8325/4)H3 + 918H4 + (777/4)H5 + 72H8 + (1531/4)H48.

The certificate also bounds the zero of this profile minus 896H73, approximately 0.0017300963635286236. Both endpoint signs are independently recomputed. After division by H73, every positive term is a positive multiple of (r/73)^(1−a), which is strictly increasing in a because r<73; therefore the bracket contains its unique zero. The dual certificate is explicitly evaluated at the upper endpoint, not asserted uniformly for arbitrary exponents.

This removes chronology, source windows, family constraints and integrality from the packing lower bound. Attainment by the aggregate is useful mathematical evidence, but literal-owner correctness and full native/outer admission are separate checks. No optimality claim concerns other suppliers, capacities, geometries, or recursive interfaces.

## Replay

With Python's standard library only:

    python -I -B verify_ceiling.py CANDIDATE.json CEILING.json --out RESULT.json
    python -I -B test_ceiling.py CANDIDATE.json

The candidate path is explicit. There are no imports from a checkout or private tooling directory, no optimizer dependencies, and no network/Git operations. JSON whitespace and non-scientific metadata do not affect the candidate binding; the complete scientific-field projection is fixed by the verifier. The private optimization pipeline is intentionally absent.

## Attribution

The width change is the staged-release construction in PR3605. The capacity model and finite-pattern primal/dual approach descend from the retained coupled-carrier-cap740 certificate. T488 combines the retained T37 chronology with the T8 and T16 chronologies and supplies a newly reconstructed aggregate. This component certifies the resulting fixed-model packing equality; it does not claim ownership of the supplier or predecessor chronologies.

At the certified upper endpoint, the dual lower bound makes every admissible profile’s normalized cost at least one. Since all positive occupied ranks are strictly below73, each such normalized cost increases with κ; no larger κ can satisfy the required cost inequality in this fixed model. This conclusion uses the dual only at that endpoint, not a uniform dual certificate across κ.
