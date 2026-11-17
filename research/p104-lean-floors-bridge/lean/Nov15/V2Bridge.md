# V2Bridge: JB edge cost vs FloorD0 helper D0 (lane LEAN-BRIDGE, Nov 16)

## Milestone 1: the exact statement, and whether it is true

**The bridge "helperD0(W) ≥ JB(edge set of W's relay)" is FALSE for general class-K words.** It is true exactly when every helper
is a {0}→V chain (born at dim 0, ends at dim 9). This agrees with V2FloorKernel.md (LEAN-KERNEL), and here it is sharpened to an exact
correction that holds for every accepted word.

Notation: f(n) = n ln n; dims are those of the verifier's charts (span dims, 0..9).
- cB(a,b) = f(9−a) − f(9−b) − f(b−a) (S2β), and cA(a,b) = f(b) − f(a) − f(b−a) (S2α, written in the original lattice).
- w0_θ = θ·cB + (1−θ)·cA, with no B1 terms, extended to dims 0..9.
- JB's edge price (V2FloorBound.wcut θ) is wt_θ(a,b) = w0_θ(a,b) + θ·B1·[a=1] + (1−θ)·B1·[b=8] on 1 ≤ a < b ≤ 8, and 0 otherwise.
- ρ_θ(d) = θ·B1·[d=1] − (1−θ)·B1·[d=8].
- corr_θ(d0,e) = w0_θ(d0,e) + ρ_θ(d0) − ρ_θ(e) is the endpoint credit. corr_θ(0,9) = 0.

**Identity (per helper, any θ).** D0(h) = f(e−d0) − Σ f(gaps) = Σ_moves w0_θ(tail, head) − w0_θ(d0, e), because both cB and cA telescope.
- So w0 is exact D0 per move only for {0}→V helpers.
- cB is exact for helpers that end at V, and cA is exact for helpers born at {0}.

**Per-move domination.** For 0 ≤ a < b ≤ 9 and θ ∈ [0,1]: wcut_θ(a,b) ≤ w0_θ(a,b) + ρ_θ(a) − ρ_θ(b).
- The line debt θB1 (out of a dim-1 chart) is prepaid by the move 0→1: cB(0,1) = B1.
- The hyperplane debt (1−θ)B1 (into a dim-8 chart) is paid by the move 8→9: cA(8,9) = B1.

**Bridge (true, every accepted word, any θ ∈ [0,1]).** Let E_W be the distinct images (ι tail, ι head) of all helper MOVEs, with ι the chart → subspace map.
Then Σ_{e∈E_W} wcut_θ(e) ≤ helperD0(W) + Σ_{h∈H} corr_θ(dim ini h, dim fin h).
- Deduplication uses wcut ≥ 0 (superadditivity of f).
- If every helper is {0}→V, the correction is 0, and helperD0 ≥ JB(E_W).

**Minimal counterexamples to the uncorrected bridge.**
1. A helper with one move, dim 1 → dim 2 = its final chart: D0 = 0, but JB = wt(1,2) > 0 (corr_β(1,2) = 6.15, corr_joint = 1.59).
2. A helper born at a line, L → Y → V: D0 = cB(1,b), but JB_β adds B1.

**Size on the native (#7623 helpers, hit_loan_14).** Σ corr = 1,413.6 (joint θ, 467 helpers with corr > 0) and 1,403.1 (β, 250 helpers).
helperD0 = 9,946.29. 484 of the 1,100 helpers are not {0}→V. So on native-like words the correction is close to the size of the floor itself.
The JB floor bounds helper D0 cleanly only under the {0}→V hypothesis.

**Realisation (i).** "W's relay realises every forced pair" = `Reach E_W (L p) (U p)` (V2FloorCert.Reach) for all p. It is a named data hypothesis
(r7-taint extraction, like H2). It is not a theorem of class K: class K fixes the kept stream only.

## Milestone 2: Lean, compiled (kernel-only)
Files: Nov15/V2Bridge.lean (imports FloorD0, V2FloorBound; about 7 s, 2.4 GB) and Nov15/V2BridgeFinal.lean (imports V2Bridge, V2FloorFinal; about 6 s, 2.3 GB).
Oleans are in .lake/build/lib/lean/Nov15/. No sorry, no native_decide, no axiom.
`#print axioms` = [propext, Classical.choice, Quot.sound] for all 10 printed theorems.
- `move_dom`: wcut θ a b ≤ w0 θ a b + rho θ a − rho θ b, for a < b ≤ 9 and θ ∈ [0,1].
- `chD0_bound`: for an ascending MChain a→b with dims ≤ 9, Σ wcut ≤ chD0 fL dim a b ms + corr θ (dim a) (dim b).
- `helper_bound`: the same statement per helper of an Accepted word, using regD0 and hcorr.
- `bridge`: Accepted w, ι : C → Sub strictly monotone, fdim ∘ ι = dim ⇒
  Σ_{e ∈ relayE ι H ini w} wcut θ (fdim e.1) (fdim e.2) ≤ helperD0 fL dim H ini w + Σ_{h∈H} hcorr θ dim ini w h.
  - relayE = H.biUnion (distinct (ι tail, ι head) of h's MOVEs). It includes edges out of dim 0 and into dim 9, which wcut prices at 0.
- `bridge_0V`: every helper has ini dim 0 and fin dim 9 ⇒ JB_θ(relayE) ≤ helperD0.
- `bridge_beta_V`: θ = 1 and every helper ends at dim 9 ⇒ JB_β(relayE) ≤ helperD0 + B1·#{h : dim ini h = 1}.
- `relayE_lt`: the edges of relayE strictly ascend (this is V2FloorFinal's hE).
- V2BridgeFinal composes these with V2FloorFinal.floor_joint / floor_beta, under hfeas : IntFeasible and hreal : ∀ p, Reach (relayE ι H ini w) (L p) (U p):
  - `v2floor_helperD0_joint`: 1839727178682/2^30 (1,713.38) ≤ helperD0 + Σ_h hcorr (22257/2^19).
  - `v2floor_helperD0_joint_0V`: 1,713.38 ≤ helperD0, given that every helper is {0}→V.
  - `v2floor_helperD0_beta`: 1536575200417/2^30 (1,431.05) ≤ helperD0 + Σ_h hcorr 1.
  - `v2floor_helperD0_beta_V`: 1,431.05 ≤ helperD0 + B1·#line-born, given that every helper ends at V.
- Class K: ClassK gives `.acc : Accepted`, so every theorem applies to class-K words.

## Open hypotheses (named, not proved)
- `IntFeasible` for the certificate. This is V2FloorFinal's hypothesis; LEAN-KERNEL and the native_decide lane are working on it.
- `hreal`: the word's helper relay realises every forced pair in the Reach sense. This is the r7-taint extraction, a data fact like H2.
- ι: chart ↦ span. dim = fdim ∘ ι, and chart order ↦ strict inclusion. For the verifier's charts these are facts.
- For the clean (uncorrected) floor: every helper is {0}→V (joint), or ends at V (β, which still carries the B1 per line-born helper).
  Neither is implied by class K. On #7623, 484 of 1,100 helpers violate it, and Σcorr ≈ 1,414.
- The r2 certificates (joint 1,990.45, β 1,556.06) plug in the same way once they are in Lean as floor_* theorems.

