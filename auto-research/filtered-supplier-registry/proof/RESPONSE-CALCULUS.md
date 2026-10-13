# Support-saturated response calculus

This is a sufficient construction theorem for the existing frame compiler, not an optimality assertion. Its application is the 504-helper supplier derived from PR531, head c609855ff92acc8cae3aa0808a4ecb624165f548. All claims below are mathematical arguments plus independently replayed finite witnesses; no Lean certification is claimed.

## 1. Response relations lift to every common admissible entrance

Work over a field in which the stated rational coefficients exist. Let the scalar body have source/background coordinates X, observed target coordinates Y, and full map (X,Y) -> (F X, G X + L Y), with F and L invertible. Background instructions must read only X. A separate inverse background cleanup restores X. Let C_h denote the target-response column of helper h, before background cleanup. Choose disjoint pivot and donor sets P,D with exact relations

    C_p = sum_d q[d,p] C_d.

Let S be P together with donors having at least one nonzero q[d,p]. Every register h in S has an actual first-touch frame F_h. Let E be any admissible frame contained in their common intersection. Require all gauge registers to be outside S and keep their existing target/center frame chains admissible. Prepend, at frame E, the elementary updates d <- d - q[d,p] p and start each pivot at E.

Proof. All prefix shears commute: their destinations are donors and their sources are disjoint pivots, so every source value is unchanged by the prefix. They form an invertible triangular matrix U. The response column at p of G U is C_p - sum_d q[d,p] C_d = 0. Other helper response columns are unchanged. Each touched register follows an allowed entrance-to-E-to-F_h chain. Thus the unchanged gauge construction and its zero-frame dirty compensation remain applicable; every warm pivot has identically zero compensated dirty response. The background inverse of the modified body is regenerated, restoring every background coordinate, including arbitrary initial helper dirt. The target map is the original target map. Existing phase-correct residual wrappers implement the changed warm-helper entrance and must be charged separately. The theorem does not assert those wrappers are free.

If multiple components have pairwise disjoint active supports and avoid gauges, their prefix matrices commute and the proof applies simultaneously. This is the support-closure composition law. It is stronger than counting nullity: a proposed relation must supply all actual nonzero donors and a legal common entrance.

The maximal common admissible entrance is the meet of the first frames of its active support. It is computed geometrically, not inferred from only the pivot frame or a chosen donor's frame. Any smaller contained entrance is also sufficient. In the delivered witness, each of the 24 components uses its maximal meet: eight have rank four and sixteen have rank one.

## 2. Exact resource signature

Write f_h = dim F_h and e = dim E. Compare against the same gauge-only word, before any subsequent frame coalescing. For a pivot, replace its initial child rank f_h by f_h-e, and replace its final residual width h by h-e. For an active donor, replace its initial rank f_h by the two ranks e and f_h-e. Rank-zero children are omitted. Inactive declared donors have no instruction and contribute nothing. All later events are unchanged. Therefore these signed histograms add exactly over disjoint support components. This is proved by listing the affected chain edges; it makes no approximation and does not infer a price from total warm rank.

FILTERED-RELATIONS.json recomputes each relation over Q, checks active-support disjointness, gauge exclusion, every frame inclusion, and equality between this predicted histogram and the actual compiler histogram. The aggregate pre-coalescing change from the same gauge-only base is

    rank 1: +104; rank 2: +80; rank 3: -80;
    rank 4: +32; rank 5: -64.

The frozen PR531 frame-promotion mechanism is then replayed separately with 248 explicit legal promotions. It changes the final local histogram to

    {1:2048, 2:732, 3:176, 4:360, 5:56, 6:56, 7:8}.

There are still 504 physical helper roles: 32 residuals of width 5, 112 of width 8, and 360 of width 9. No helper is discarded or silently erased.

## 3. Endpoint principle for a fixed resource regime

Fix a support component, a nested flag of admissible entrances, and an explicit physical owner layout. Assume that throughout an interval of warm ranks e, all relevant child ranks and owner remainder ranks are affine functions a_i+b_i e, remain nonnegative, and no controller, toll, or atom bound changes. For a fixed exponent 0<alpha<1, the complete rank moment

    Phi(e) = sum_i multiplicity_i * (a_i+b_i e)^alpha

is concave: x -> x^alpha is concave on nonnegative x; affine precomposition and nonnegative sums preserve concavity. For e between endpoints l,r, concavity gives Phi(e) >= min(Phi(l),Phi(r)). Hence at least one endpoint is no worse than any intermediate entrance in this fixed regime. The conclusion is a sufficient finite comparison rule, not a claim that arbitrary packing, coalescing, or gauge changes share one concave regime. Discrete allowed ranks are covered by the same interval inequality. Changed resource regimes must each be billed explicitly.

The source analogue inspected is Mathlib.Analysis.Convex.SpecificFunctions.Pow, Real.concaveOn_rpow (and Real.strictConcaveOn_rpow). We reuse the mathematical fact, not a compiled import. The actual construction tests maximal support meets; global improvement additionally depends on the separate exact whole-owner admission witness. No fixed-layout endpoint lemma proves that new allocation by itself.

## 4. Concrete evidence and bounded alternatives

The native search examined 27,195 admissible subspaces and found 458 positive-nullity classes: 78 of rank one, 252 of rank two, 120 of rank three, and eight of rank four. Discovery used modular elimination only as a nomination tool. The chosen 72-pivot construction was rebuilt over Q, with dyadic addition denominators and signed power-of-two scaling gates checked. Both 728-column scalar orientations and 72 omitted-correction negative controls passed with the original compensation held fixed.

Two subsequent 256-mask hybrid screens reserved subsets of the eight rank-four supports and recomputed rank-one kernels on remaining helpers, first in the six public line classes and then in all 78 positive line classes. These are recorded candidate families, not a completeness or optimality result. The original support-saturated, re-coalesced 72-pivot construction remains the frozen nominee. The first restricted owner allocation lost; a later exact rank-32 allocation packs (5,9,9,9) and gives a positive complete supplier moment. Final kappa and phase/physical certification belong to the package's final assembly receipts, not this discovery note.

## 5. Reconstruction and scope

code/build_filtered.py reconstructs PR531's raw 504-helper factory from attributed inputs, recomputes the frozen exact response relations, replays the frozen frame promotions, checks the complete scalar-program semantic hashes, and checks the dyadic gate contract. No candidate optimizer is needed. The fresh local pipeline transports every scalar column and frame, lowers new phase edges including global phases, decodes every residual wrapper independently, emits both local orientations, and independently replays the emitted instructions. The observational retargeting variant is a separate proved rewrite of the resulting word with the same resource signature; heterogeneous gluing and whole-owner admission are separate composition theorems.

The inherited all-size realization and analytic-transfer interfaces remain conditional exactly as in the public project. This note establishes sufficient local rewrites and their finite resource signatures; it does not remove those project-level conditions.
