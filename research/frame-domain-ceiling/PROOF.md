# Complete binary-frame exclusion for the fixed PR551 scalar word

## Claim and scope

Fix PR551 at `e7faafc4fec401d24080e5b2df12f964f1cfe123`: its scalar gate list and order, original registers, starts, central cut, target levels, endpoints, complete owner schedule, and conservative per-child bad-class charge. Allow simultaneous reassignment of **every one of its 3,657 A/B event frames** to any subspace of F₂⁹ admitted by the ordinary nested binary-frame contract. We do not freeze the prefix frames or restrict changes to the original frame catalog.

No such reassignment admits a complex saving

    b ≥ 0.001594507308884431019638.

This is the next 10⁻²⁴ grid point above PR551's admitted b. It closes frame-only search for this fixed scalar word at that grid resolution. It is not a bound on scalar rewrites, reordering, different registers or widths, altered cuts, owner repacking, alternative bad-class charges, general complex subspaces, or another outer theorem. It does not improve κ or prove a multiplication theorem.

## Complete finite domains

Make an event vertex for every gate and fixed boundary. Each register contributes directed edges between consecutive events; a multi-register gate has one common frame. The graph is acyclic in program order. At each variable vertex propagate joins forward from fixed starts and central boundaries, obtaining L. Propagate intersections backward from fixed endpoints and central boundaries, obtaining U. Any legal assignment F satisfies L ⊆ F ⊆ U by induction in the two orders.

For this word, dim(U/L) ≤ 3 everywhere. The verifier enumerates every quotient subspace and lifts it to the interval [L,U]; this is a complete enumeration, not a sampled neighborhood. Exactly 2,375 vertices have multiple choices. After fixed vertices are removed, their dependency graph splits into 71 components.

The graph permits a charged climb into a fixed center even if no original scalar event realizes that climb. This enlarges the feasible set. Every genuinely legal original program remains represented with zero such extra climb, so a lower bound for the relaxation applies to the claimed class. The fixed central descent contributes eight rank-8 children, separately from the graph's rank mass 5,948.

## Linear relaxation and exact duals

For each vertex v and possible frame F, introduce x(v,F) ≥ 0 with sum_F x(v,F)=1. For each directed edge v→w introduce y(F,G) ≥ 0 only when F ⊆ G. Its two marginal sums equal the corresponding x variables. Repeated register edges retain their multiplicities. Every literal assignment gives a feasible 0/1 point; fractional points only enlarge the set.

Let M_r(b) be the exact per-child contribution, including its share of the conservative fallback charge, to the dimension-73 recurrence moment. Use adjusted charges C_r = M_r − r M_1, with C_0=C_1=0. Along each register, differences of frame dimensions telescope; the total graph rank mass is fixed. Thus minimizing adjusted cost is equivalent to minimizing the original moment cost. Fixed-center and owner-remainder charges are constants.

The linear program is min cᵀz subject to Az=d and z≥0. A dual vector q with Aᵀq≤c proves cᵀz≥dᵀq: subtract qᵀAz and use nonnegative z. No optimization theorem beyond this identity is needed.

Each supplied dual entry is a rational linear combination of C₂,…,C₉. The verifier independently rebuilds every domain, constraint, column and objective coefficient. It checks every reduced cost using outward rational bounds from **two independent moment engines**. Identically zero linear forms are checked symbolically. The dual objective equals the literal PR551 assignment's adjusted profile as a coefficient-vector identity for every component. Therefore that assignment minimizes the relaxed cost at the excluded b, and hence also minimizes cost among all legal frame assignments there.

The solver used during discovery only nominated a basis. Basis inversion was reconstructed rationally and checked; the shipped verifier imports no optimizer, NumPy, SciPy or floating-point LP result. The exact dual inequalities themselves are the proof.

## From local optimization to a rate ceiling

There are 72 local invocations. Their helper widths and owner identities are fixed. The remaining paid profile is {2:448, 3:1923, 7:208, 39:1, 48:1660}; these counts are independently derived by subtracting 72 times the local profile from the pinned complete PR551 profile, with nonnegativity checked.

At b = 0.001594507308884431019638, both rational engines give a strictly positive lower bound for the complete moment minus one. Every allowed frame assignment has moment at least this baseline value by the dual proof. Every child has rank strictly below dimension73, so each positive child and fallback term increases with b; no larger b can restore admission.

The raw word is reconstructed from pinned PR551/548/static44 source files, including static44's scalar and omission checks. The result's byte hash is checked before dual verification. This proof does not re-run the complete physical bit/complex suppliers: those are the independently tested PR551 dependencies, and this contribution excludes other frame choices for the fixed word.

## Consequence for the retained outer assembly

The pinned outer engine has a<b, q=a(1−2η), η>0, and the strict compact-phase constraint κ<(1−η)q/(1+q). Therefore κ<b/(1+b). Combining this with the frame ceiling gives

    κ < 0.0015919689028333465200257576762271245922...
      < 0.001591968902833347.

The displayed decimal is explanatory; the verifier compares the exact fraction b*/(1+b*) with both neighboring 10⁻¹⁸ grid points. Thus frame reassignment alone cannot increase PR551's published κ by even one grid tick under this outer engine. A different outer theorem is explicitly outside the claim.

## Rejection controls

The verifier rejects a missing component, an altered dual coefficient, an omitted domain choice, and an attempt to exclude the already admitted b instead of the next grid point. The last control prevents a ceiling claim from merely trusting solver output or a supplied profile.
