# Independent joint-chart source binding before the candidate execution gate

2026-10-23. **PASS for the frozen graph, fixed pivot and incidence inventory. The actual joint candidate code gate is pending.** No candidate search, optimizer, single-move census, native circuit, numerical Tensor, compiler or Lean execution is included.

The source-design packet currently supplies PIVOT-INVENTORY.json and the frozen inputs under `outputs/joint-clifford-design-20261023/`. Its source head is `0335701859182b7bdf31706b0d969c72f5de41c7`. The literal compressed forward word has SHA256 `7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`; the contracted graph is `f5db08a5814b14b11b93b79207afb1a8d5ec2c5803c1cf6bbc3333cccf0a94af`; the pivot inventory is `9182378f7c7c3c1f50cd32b2c990c0395b596d9edf980b6b4ce4ad7bb592a76b`.

## Independent reconstruction and all original zero contacts

`verify_graph_binding.py` reads the literal source JSON/gzip as data and independently rebuilds the chronology, zero-contact contraction, Lagrangian charts, signed native warp operators and helper boundary rows. It imports none of the predecessor model, algebra, discovery or verifier implementations. It reproduces the complete encoded contracted graph byte-for-byte.

There are 19,197 original chronological nodes and 34,638 original paid/warp contact rows. Exactly31,108 original zero-paid rows connect identical source frames and are contracted. The contracted graph has1,075 groups,275 frozen groups,800 movable groups,144 exact binary symplectic warp operators and3,938 signed incidences. Those incidences comprise3,290 paid identity contacts,240 warp contacts and408 helper rewards. The eight fixed owned centre calls contribute8H8 separately.

Every original zero-paid row lies within one contracted group. Assigning a single chart to each complete group therefore leaves all31,108 omitted original zero contacts at rank zero. They are not silently dropped across different trial assignments. Frozen main, adapter and owned-contact boundaries are represented by the union of their frozen groups.

Independent binary row elimination verifies every stored chart has dimension9 and is isotropic. Every one of the144 stored operators is invertible and preserves the exact symplectic pairing. The full graph has78 selfloop incidence rows and805 additional parallel rows under the exact ordered endpoint/operator/sign key. These are genuine multiplicities and must remain separately charged where affected.

The independently reconstructed full baseline invoice is

```
paid={1:2201,2:412,3:510,4:127,5:40,8:8},
helpers={4:28,7:7,8:47,9:326}.
```

The reconstruction and output JSON are byte-identical under normal and optimized Python. This reconstruction is a small data audit and does not rerun the credited full nearest-chart census.

## Fixed zero pivot and three declared joint neighborhoods

The fixed pivot is group499, Pauli axis7. Direct independent transvection/rank calculations give its four incident row transitions:

| Row | Baseline rank | Pivot-only rank |
|---:|---:|---:|
|1193|2|3|
|1194|1|2|
|1204|2|1|
|1212|3|2|

The resulting signed rank polynomial is identically zero; this is stronger than a floating near-tie at one C. Both the old and changed chart are valid distance-one Lagrangians. Group499 and all three partners are movable.

The partner172 union is exactly rows `{130,131,1181,1187,1193,1194,1204,1212,1399,1405,1411}`. Partner497 uses `{1189,1190,1193,1194,1204,1208,1212}`. Partner504 uses `{1193,1194,1203,1204,1205,1212,1213}`. These unions contain11,7,7 distinct incidence IDs respectively, all paid identity contacts. No helper or warp row changes in these particular neighborhoods. The global generic evaluator must nevertheless handle selfloops, parallel rows, native operators and signed helper feasibility correctly; absence from the selected unions is not a general omission license.

For a9-dimensional binary Lagrangian L, every distance-one neighbor intersects L in one hyperplane H. There are2^9−1=511 such hyperplanes. The symplectic quotient H-perp/H has dimension2 and three lines; one corresponds to L/H and the other two to its two neighbors. Hence there are exactly1,022 distinct distance-one neighbors. A receipt containing1,022 unique isotropic dimension9 charts, each at distance one from the partner baseline, establishes coverage of that partner's nearest neighborhood without another exhaustive Pauli-axis sweep. The declared total is3,066 partner candidates with the one fixed pivot move.

## Required actual-code gate and downstream scope

The actual search must use the union of incidence **IDs**, counting a selfloop once and retaining distinct parallel rows. For every affected row it must substitute both endpoint trial charts, apply a native operator to the source chart before measuring distance, and record exact ranks for all four pivot/partner states. Helpers, if present in a generic control, must retain strictly positive rank in every feasible state. All four state invoices and their signed rank polynomials must be retained, rather than only a floating objective delta. A failed domain search is scoped to this one pivot and these three nearest neighborhoods.

A graph rank transition is not an emitted physical circuit. Even a strict gain still needs literal phase-correct legal new charts, paid transitions at every chronological contact, all original arbitrary-input/helper endpoints and inverse-transpose/boundary conventions, exact all-width tariffs and ordinary cost, and a completed supplier/caller/precision/stock binding before compiler or κ transfer. A nearest-domain negative result is not a universal obstruction to joint Clifford changes.

Credit Cinna Davis's independent-chart mathematics and census, the contact/chronological source model and PR4610/PR4470/native lineage, and Astra's specifically declared new joint neighborhood. Substantial OpenAI Codex assistance. This reviewer creates no separate literature feed and makes no priority or κ claim.
