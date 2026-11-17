# FloorD0.lean: H1 closed. Helper D0 ≥ 2 ln 2 · #paid stays on every accepted word; floor_D0_classK. No sorry, ~6 s, 2.6 GB
Lane LEAN-NEXT18, Nov 16. Imports Nov15.FloorEndToEnd, Nov15.FloorCert, Nov15.JunkLB2 (h, two_point, fL), Nov15.DescentPrice.
Build: `lake env lean -o .lake/build/lib/lean/Nov15/FloorD0.olean Nov15/FloorD0.lean` (needs the DescentPrice olean, built this lane).
Axioms: the 13 printed theorems use exactly [propext, Classical.choice, Quot.sound]. No `sorry`, no `native_decide`, no `axiom`.

## Cost model (read from PRICEKIT pricekit.py, wrapped by REBUILDKIT/harness/common.py `price`)
- One native word = one call. `invoice()` adds the word's T and P histograms once per J event (L = 17 on #7623).
- Native word: helper r (public, not a main) gives T[dim final(r) − dim initial(r)]; every MOVE a → b gives P[|dim b − dim a|].
- D0 = Σ_r (T_r − P_r)·f(r), f(r) = r ln r (`Dsum`; it sums r > 1 only, which is the same since f(0) = f(1) = 0).
- **÷17.** `histD0_invoice`: D0(invoice) = D0(caller) + L·D0(native), exactly. So "D0/call" of the helper layer is the word's own helper D0:
  `helperD0 = Σ_{h∈H} [f(dim fin h − dim ini h) − Σ_{MOVEs of h} f(|Δ dim|)]` (`regD0`, `helperD0`). This is GAPMAP's "helpers 9,946.29 D0/call" quantity, and FloorCert's 1,081.31 is in the same unit.
- Model data beyond FloorEndToEnd: `dim : C → ℕ` with a < b ⇒ dim a < dim b. For the verifier's chart order (a < b iff span a ⊊ span b, frames = bases) this is a fact, not data.
- PRICEKIT's T uses W['final']; `regD0` uses the run's final location. They agree whenever the exit-frame check passes (replay `exit-frames`).
- The official repo has no D0. Its figure of merit is the κ crossing, and PRICEKIT reproduces those crossings bit-exactly (PRICEKIT/RESULT §1). D0 is the lab's first-order unit.

## Results
- **Abstract f** (convex on [0,∞), f 0 = 0), κ_f := f(2) − 2 f(1):
  - `stay_ge`: h_e(a,b) = f(e−a) − f(b−a) − f(e−b) ≥ κ_f whenever b − a ≥ 1 and e − b ≥ 1. This generalises JunkLB2.kappa_le.
  - `kap_nonneg`; `attr_final`: h_e(a,e) = 0.
  - `chD0_attr`: GAPMAP §1's attribution identity (D0 = Σ_moves h_e(tail, head), e = final dim) on any ascending MOVE chain.
  - `chain_D0_ge`: a chain of k moves has D0 ≥ κ_f (k − 1). Each non-final move is the arrival into a chart the register later leaves (a paid stay), and it is charged ≥ κ_f.
  - `kap_fL`: κ_{r ln r} = 2 ln 2.
- **Word**:
  - `chain_run`: a public register's MOVE records form a chain from ini to its final chart.
  - `dep_move`: a departure of r from c in the projection is a MOVE of r out of c. A public register is never CLEARed.
  - `fibre_le`: #stays(h) ≤ #moves(h) − 1.
  - `helper_D0_ge`: per helper.
  - `helperD0_ge`: **κ_f · #stays ≤ helperD0 on EVERY accepted word** (class K is not needed).
  - `helperD0_ge_fL`: the same with 2 ln 2.
- **`floor_D0_classK`**: ClassK + H2 ⇒ helperD0 ≥ 780·2 ln 2 and ≥ 1,081.309 D0/call (via Real.log_two_gt_d9).
  - H2 (`def H2`): ∃ x ≥ 0 on the 18,868 support columns satisfying the 892 exported rows, with cᵀx ≤ #stays. This is FloorEndToEnd.md items 2–4: the exported rows are family instances for D₀, so x(w) restricted is feasible, and objective_le applies.
  - H2 is the only remaining hypothesis.
- `chD0_id`: with rank weight f = id (S instead of D0), the per-register invoice is DescentPrice's: credit − paid = −2·(descent ranks), via DescentPrice.helper_identity. The same invoice model, reused.

## Where the attribution holds or fails (per stay type)
- **Helper stays: holds for every type.** It needs only b − a ≥ 1 (l.51: a public MOVE strictly climbs) and e − b ≥ 1 (a paid stay is later left, and the next move climbs).
  - Stays at V: none. Nothing is above V, so a helper at V never departs. Arrivals into V are final moves and are charged 0.
  - Births: departures from the birth chart are not stays. The first move is charged to the stay it arrives at.
- **Owned registers: the attribution fails, but no paid stay is owned.** An owned MOVE may descend (l.51 allows b < a). Then the signed-gap h_e telescoping (GAPMAP §1) no longer equals PRICEKIT's |Δ| charge, and h_e can be negative.
  - Owned D0 is not in helperD0, and FloorEndToEnd's stays are helper-only, so the floor is unaffected.
  - Minimal fix, if owned stays are ever counted: charge an owned register by DescentPrice's paid ≥ descents (`owned_ge`), not by h_e.
- **Mains/hosted:** not in H, so no stays and no D0 are counted. The floor is a helper-layer floor only.

## Statements found false / imprecise
- The brief's suggested per-stay form "f(e) − f(e−1) ≥ f(1) − f(0) = κ" is vacuous for PRICEKIT's f: r ln r gives f(1) − f(0) = 0. The correct per-stay charge is GAPMAP's h_e(a,b), and its minimum over b − a ≥ 1, e − b ≥ 1 is f(2) − 2f(1) = 2 ln 2.
- GAPMAP §1's identity "D0(r) = f(e−d0) − Σf(gaps)" uses signed gaps. It equals PRICEKIT's charge only on ascending registers. That covers all public registers by l.51, which is the scope GAPMAP states it for, so it is not false. It would be false for owned descents.
- Nothing else found false. FloorEndToEnd.md's H1 is now discharged in aggregate form (κ·#stays ≤ helper D0), which is what FloorCert's floor uses.
