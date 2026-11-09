# Wave 2: exact production nonempty-interior admission

Status: **verified local package, ready for lead publication review**.
Canonical main was rechecked and remains
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Branch: `research/core-production-nonempty-20261109`.
Worker: analytic_join. Package: `research/core-production-nonempty`.

## Established and independently reviewed

The exact target-coordinate inverse image and longest phase-pure selected run
M give `I nonempty iff M>6W` for the unchanged production capped carve. The
uniform guard `S>=e(6W+1), L>=12W+2` admits every ordinary original start,
including short endpoint half-cells. Both one-unit adverse families retain
`N-L>=W`; sharpness is not asserted for dyadic aligned windows.

The lead independently reviewed the inverse cuts, middle-cell maximum,
cap criterion, all-window proof and fixed-tape setup cost. The lead independently
checked the source-ratio adverse family; the worker separately checked both
families against the original source bodies. Common per-axis descriptors
permit O(g d^2) setup; heterogeneous or local tests retain up to O(K g d^2).
No payload pass, numerical recovery theorem or kappa gain is claimed.

## Reproduction and executed checks

`python3 -B scripts/research_package.py --package research/core-production-nonempty --check-only`
returned `PASS_PACKAGE_METADATA_AND_PINS`.

`python3 -B scripts/research_package.py --package research/core-production-nonempty`
returned `PASS_REGISTERED_RESEARCH_PACKAGE` after both ordinary and optimized
runs passed the full frozen receipt. Coverage: 772,850 exact literal-coordinate
windows; 77,793 authenticated source partitions; 855 uniform-guard admissions;
17 negative controls; both sharp families W=1 through 16. No numerical or
native replay is represented by these geometry checks.

The complete-Core source family is a cited conditional application. All three
executable dependencies are exact canonical-main files listed in SOURCES.json
and VERIFY.json. The phase-cell facts of #6259 and the capped density lineage
are prior work, explicitly credited.

## Outstanding obligations and next action

Source row gap, numerical accuracy/norms, uniform preparation, native lifecycle
and whole recovery remain. Empty short sections outside the uniform guard
still need a complete numerical/native solver. Next action: commit the checked
package, run the committed-byte/mode gate and give the exact head to the lead.
The worker has created no remote branch, external post or upstream PR.

Wave 1 is preserved separately at public bridge commit
`73d5adaba2b7dc662e86eb901e81369a3f73be9f`; this package has no executable
dependency on that branch or another unmerged package.
