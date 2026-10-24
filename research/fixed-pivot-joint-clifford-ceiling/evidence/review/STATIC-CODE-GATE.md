# Independent static gate for the bounded joint-chart checker

2026-10-23. **PASS to root's decision on one bounded60s execution.** This reviewer has not executed the joint checker, a single-neighbor census, native circuit, Tensor, compiler, solver or Lean. Source graph reconstruction and fixed-pivot data checks are documented separately.

Reviewed `outputs/joint-clifford-design-20261023/check_joint.py` SHA256 `575136ee932e697c97b8a15d2edc1f5ab159de482c66c01a6f211a9dfd301630` and CONTRACT.md SHA256 `8f29241120f28f6df2541e7fec74fa3a8ad3b03eb79a8b79dd91b6875d7d5a52`. The author AUTH-MANIFEST pins the source graph, actual literal word, source model/algebra and interval implementation. The frozen graph was independently reproduced byte-for-byte without importing those source routines; all31,108 original omitted zero-paid contacts remain internal to groups.

## Rank tables and complete incidence accounting

The checker fixes pivot499 axis7 and derives the complete movable adjacent set `{172,497,504}`. It enumerates1,022 distinct nearest charts for each partner relative to that partner's baseline, totaling3,066 candidate pairs. It checks distance one and uniqueness. The source nearest-neighbor grammar is justified by511 hyperplanes and two other lines in each2-dimensional symplectic quotient; this does not require rerunning the credited exhaustive single census.

The union is built by enumerating incidence IDs once. Parallel rows remain distinct. A selfloop is one row and both of its endpoints receive the trial chart. Native warp action is applied to the source endpoint before rank computation. Four states are recorded explicitly in the order00,10,01,11. The signed delta calculation correctly subtracts each baseline cost/reward and adds the new one. Helper rank zero invalidates the affected state; each feasible joint profile still contains408 independent helpers.

The profile updater begins with the complete baseline, including all8H8 owned centres, then changes exactly the affected incidence rows. Zero ranks cost H0=0 and do not become a productive helper. In the declared three neighborhoods every union row happens to be a paid identity incidence; the generic code still handles warps, helpers and selfloops. The fixed pivot's E10 polynomial is checked to be identically zero, rather than numerically close to zero.

The checker performs a complete global invoice for the first occurrence of each joint-delta polynomial, each certified favorable candidate and the last neighbor of each partner. This is a useful internal cross-check, **not independent verification of all candidates**. The independent reviewer must recompute every recorded four-state table and complete profile after execution before accepting either a favorable witness or a complete scoped negative result.

## Outward bounds and classification

The imported source interval engine has128-bit integer endpoints. Its logarithm uses a48-term positive atanh series after reducing the integer rank to a power of2 times a factor in[1,2), with a valid geometric tail. exp(C log r) is bounded by positive terms with floor/ceiling at every operation and twice the first omitted upper term. On0≤C≤1/200 and1≤r≤9, the exponent is below1/2, so that remainder bound is valid. Reciprocating positive exp bounds reverses endpoints and gives outward bounds on H_r(C)=r^(1-C). No floating decision is made.

For an interval[a,b], H_r decreases, so the lower term uses H_r(b) and upper uses H_r(a). Negative coefficients correctly exchange endpoints. Derivative bounds multiply by nonnegative outward log intervals, then negate delta coefficients. A zero rank-mass polynomial has E(0)=0, so nonnegative derivative across every subinterval proves nonnegativity. A positive-mass polynomial is certified only by direct nonnegative intervals or discrete concave dominance; no derivative extrapolation from a positive initial value is used.

The concave-dominance condition `sum delta[r] min(r,k)≥0` for each integer k=1..9 is sufficient: any increasing concave function with f(0)=0 on these ranks is a nonnegative linear combination of the min(r,k) functions. It therefore applies throughout the declared power domain. Point success requires a strictly negative outward upper endpoint at the exact rational C*. Nonpositive or uncertain intervals are not promoted. Full-domain unresolved certificates stay unresolved.

Coverage-complete, certificate-processing-complete and full-domain-complete fields are distinct. A deadline during certification can retain all3,066 candidate rows while honestly reporting incomplete processing. No solver, wider pivot domain, random walk or automatic120s retry appears.

## Two nonblocking reporting/budget qualifications

1. `complete_global_invoice_checks=len(full_checked)` counts distinct joint-delta polynomial keys that received a global check. It is not the number of literal check invocations and does not count all independently reverified candidate profiles. Interpret it as checked polynomial-key coverage or rename it in a future separately frozen revision.
2. `--max-seconds` is a cooperative deadline checked between candidates and certification subdivisions. Source binding, one in-progress calculation and final JSON serialization are outside a strict interrupt guarantee. If60s is an absolute process limit, root should enforce it externally; a killed process may not produce the cooperative partial receipt. No automatic budget extension is implied.

Neither qualification invalidates the mathematical gate. No author source file was changed by this review. Root controls the execution and any retry.

A negative geometric energy is only an improved rank invoice. Literal phase-correct chart lifts, chronological paid transitions, legal native maps, complete arbitrary-input/helper restoration and raw-dual/frozen boundary conventions, all-column costs, actual caller/precision/stock and compiler/outer transfer remain separate. No new κ is inferred.
