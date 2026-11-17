# Spec6: spec-break R63, survivor #6 (cells (2,1),(2,2)) kill, formalised 

File: `Nov15/Spec6.lean`. Kernel-only; axioms `propext, Classical.choice, Quot.sound`; no `sorry`, no `native_decide`. ~41 s, 2.1 GB. Standalone (Mathlib only; did not import SpecRankP/SpecLemmaU/SpecINV, which are about #0 and not needed).

Setting (n-free, order-free, char != 2): V any vector space over a field K with 2 != 0, `e : V`, `phi : Dual V`, `phi e = 1`, `R = 1 - 2 e⊗phi`; a `Job` is `g = 1 - x⊗y`, `y x = 2`. X-type = `x ∈ span{e}`, Y-type = `y ∈ span{phi}`.

| paper | Lean |
|---|---|
| G_X group, R in G_X, reflection in G_X iff X-type | `GX`, `GX_mul`, `GX_R`, `GX_job`, `job_of_GX` |
| L1 two X => third X (three rearrangements g3=g2g1R, g1=Rg3g2, g2=g1Rg3) | `L1_third/_first/_second`; Y side by transposition (`Job.dual`, `rel_dual`) |
| L2 (x/y in plane <e,x_p>, <phi,y_p> when end p is N-type) | `xplane` (x), y by `Job.dual`; packaged in `plX_first`, `plY_first` |
| L3 / F1 (<= 1 X and <= 1 Y at a plane vertex) | `L3x` (+ dual inside `plY_first`) |
| L4 (X-only end vs Y-only end impossible, both orders; Eq vertices) | `mixed` (X-only first, Y-only last), other order = `mixed` on the dual; `vertex` does the case split ends-N / XX / YY |
| vertex types exactly PLANE, XX, YY | `vertex : Vt e φ a b c` (also last-end-N via `rel_rev`), `vertex_any` (all six orders) |
| K4 incidence + case split (i)-(v) over (#XX,#YY) | `k4A` (abstract atoms; 81 cases XX/YY/plane per vertex, closed by `grind`; the 8 one-special-vertex cases (iii)/(v) split on the Y (resp. X) status of the six edges) |
| ending in PL / ALLX / ALLY | `spec6_trichotomy` |
| R58 kill of PL/ALLX/ALLY | named hypotheses `R58_PL`, `R58_ALLX`, `R58_ALLY` in `spec6_dead` (not re-proved; R58's `mu=3`/unit relations are not formalised) |

Verdict: every paper statement (L1-L4, F1, the case split) is TRUE as written; no counterexample. Wording points:
* L4 in Lean does not use the "x2 || x3 vs independent" split. Cleaner route: with end 1 X-only and end 3 Y-only, `g2g3 = g1R = 1 + w⊗e`-form with `w = 2phi - u y1`, `w e = 0`, `w != 0`; evaluate `g2g3 v` at a `v ∈ ker phi` with `w v != 0` (forces x2 || e) and at `v = e` (forces x3 || e, contradiction). So no dichotomy is needed.
* L2 independence of y2,y3 is not assumed: it is derived (claims A/B in `xplane`): if y2 vanished on ker y3 (or y3 on ker y2) then g1R - 1 would vanish on a hyperplane, forcing y1 in span phi (`vanish_contra`). This is the rank(g2g3-1)=2 step made explicit.
* "plane vertex" = an end N-type; an N-type middle edge forces an N-type end (else `vertex` lands in XX or YY, which has no N edge). The proof of (iv) uses t N-type at w_i, then `Mx`-transitivity (`tr_gen`), exactly as DERIV63 says.
* In (iii), a vertex that is XX gives no y-information and a YY vertex no x-information; the case split never needs it (every edge lies in a plane vertex). The abstract hypotheses of `k4A` encode only: L1 on both sides, and per vertex XX | YY | (plane: <=1 X, <=1 Y, all x's in the plane of any non-X edge, all y's in the plane of any non-Y edge).
* Hypotheses on the vertex relations are per-vertex orders, arbitrary (6-way disjunction), so the result is order-free.

Not formalised: the char list / reduction of #6 to cells (2,1),(2,2), BDF being a genuine char in the same basis (R57 item 3, assumed as in AUDIT63 item 7), R58's kill, minimal-counterexample frame. No non-vacuity numerics added (AUDIT63 item 8 has the 11,744 integer 2D solutions).
