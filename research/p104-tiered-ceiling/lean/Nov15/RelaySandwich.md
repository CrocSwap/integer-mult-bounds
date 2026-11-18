# RelaySandwich.lean: NEWNATIVE R4 LAW RELAY-SANDWICH + stop-cost identity
Imports Nov15.FrameSep, Nov15.JunkLB2. Kernel-only, 5 s / 2.3 GB, no sorry/native_decide; 9 `#print axioms` all within [propext, Classical.choice, Quot.sound] (the lattice theorems use none).
Build: FrameSep olean was missing; built with `runlean.sh Nov15/FrameSep.lean .lake/build/lib/lean/Nov15/FrameSep.olean`.

## Results
- `Pinned p n c`: p i ≤ c ≤ n i, c = ⨆ p, c = ⨅ n (any complete lattice, any index type).
- `admissible_unique` / `admissible_iff`: a chart c' keeping every resident ascending (p i ≤ c' ≤ n i) equals c. So no stop can be moved or collapsed to another chart while all residents still meet there.
- `no_neighbour_collapse`: if no p i or n i equals c, no neighbour chart (p j or n j) is admissible.
- `pinned_nontrivial`: under p i ≠ c a pinned relay has at least 2 residents.
- `restop_valid_iff`, `route_collapse`: frame form on FrameSep.Route (submodules). Replacing the frame at t+1 by c' keeps all public steps ascending iff f t ≤ c' ≤ f (t+2); for residents pinned by those frames, c' = c.
- `stopCost_fL`: helper 0 -> e with k stops (k+1 equal moves), D0 = f(e) - Σ f(gap) = e ln(k+1) for f = r ln r; `stopCost_nine`: 9 ln(k+1). `stopCost_strictMono`: strictly increasing in k. k = 2 gives 9 ln 3 (integer gap 3).

## Scope / statements checked
- R4's law is TRUE as written, with one reading made explicit: "collapse" means a chart change that keeps ALL residents at one common chart (they must meet to relay). If a single resident drops its stop it stops meeting the others; that is partner-changing re-routing, which R4 puts out of scope (its test (c)).
- The non-equality hypothesis is needed only to make neighbour charts distinct from c; uniqueness of an admissible chart holds without it (example in the file: degenerate p = n = c).
- Cost identity: "evenly spaced" gives integer dims only for (k+1) | 9 (k = 0, 2, 8). For other k the identity is the real-gap version (PRICEKIT charges |Δ dim| with integer dims, so it needs integer gaps). Per-stay form: this is FloorD0's chD0 = f(e - d0) - Σ f(|Δ|) specialised to equal gaps; I proved the closed form directly, not via the MChain machinery.
- Not formalised: that the 238/254 families in R4 (c) really satisfy Pinned (computational [C] fact).
