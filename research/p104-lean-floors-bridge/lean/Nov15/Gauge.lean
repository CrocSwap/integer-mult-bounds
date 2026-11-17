/-
Coefficient gauge, lane LEAN-NEXT11, Nov 16. See Gauge.md.
Source: REBUILD-ALT r3 (cards/WILD/REBUILDKIT/ROUNDLOG.md "ALT: r3 (1)", alt/r3/gen5.py Gauge/apply_gauge).

Op model: TokenCancel's. A gauge is a time-indexed unit per register, g t r. Gauging an event list
rescales ADD coefficients (a ↦ a·g(i)/g(j)) and SCALE factors (u ↦ u·g'(i)/g(i)); every other event,
partner and chart is unchanged.
(1) `run_gauge`: if the gauge changes only where the event allows it (`Adm`: only at a SCALE, INIT or
    CLEAR of that register; a born register gets gauge 1; COPY i j hands j's gauge to i), the gauged run
    from the gauged start is the gauged run. So every register whose final gauge is 1 ends with the same
    row (`row_preserved`), and every register's final row is (final gauge) • (old row).
(2) `valid_gauge`, `valid_gauge_A`: the joint hub settle re-absorbs the gauge (HubSettle.Valid):
    prefix D0·M, V mix C·Dv⁻¹; with A-unit gauges the A-integrality (InGL) is kept too.
(3) `lam`, `lam_norm`: a spanning forest over the free segments (each with a parent edge whose
    coefficient is a unit) fixes the gauge so every forest edge has coefficient 1; non-free segments get 1;
    the gauge lies in any subgroup containing the forest coefficients (A-units).
(4) `seg_adm`, `forest_gauge`: segments → gauge; the composed theorem.

Build (imports the HubSettle olean):
  lake env lean -o .lake/build/lib/lean/Nov15/TokenCancel.olean Nov15/TokenCancel.lean
  lake env lean -o .lake/build/lib/lean/Nov15/RankLaw.olean Nov15/RankLaw.lean
  lake env lean -o .lake/build/lib/lean/Nov15/HubSettle.olean Nov15/HubSettle.lean
  lake env lean Nov15/Gauge.lean
-/
import Nov15.HubSettle

set_option linter.unusedSectionVars false

namespace Gauge
open TokenCancel RankLaw HubSettle Matrix

section Run
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- Gauged state: row r multiplied by g r. -/
def gs (g : Reg → K) (s : St K Reg C) : St K Reg C := ⟨fun r => g r • s.row r, s.loc⟩

/-- Gauged event (before-gauge g, after-gauge g'). -/
def gEv (g g' : Reg → K) : Ev K Reg C → Ev K Reg C
  | .add i j a c => .add i j (a * g i / g j) c
  | .scale i u c => .scale i (u * g' i / g i) c
  | e => e

/-- Where the gauge may change. -/
def Adm (g g' : Reg → K) : Ev K Reg C → Prop
  | .born i _ => g' i = 1 ∧ ∀ r, r ≠ i → g' r = g r
  | .init i _ | .clear i _ | .scale i _ _ => ∀ r, r ≠ i → g' r = g r
  | .copy i j _ => g' i = g j ∧ ∀ r, r ≠ i → g' r = g r
  | .move _ _ | .add _ _ _ _ => g' = g

theorem step_gauge (g g' : Reg → K) (hg : ∀ r, g r ≠ 0) (s : St K Reg C) (e : Ev K Reg C)
    (h : Adm g g' e) : step (gs g s) (gEv g g' e) = gs g' (step s e) := by
  cases e with
  | born i c =>
    obtain ⟨h1, h2⟩ := h
    simp only [step, gs, gEv, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr; simp [h1]
    · simp [Function.update_of_ne hr, h2 r hr]
  | init i c =>
    simp only [step, gs, gEv, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr; simp
    · simp [Function.update_of_ne hr, h r hr]
  | clear i c =>
    simp only [step, gs, gEv, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr; simp
    · simp [Function.update_of_ne hr, h r hr]
  | move i c =>
    have h' : g' = g := h
    subst h'; rfl
  | add i j a c =>
    have h' : g' = g := h
    subst h'
    simp only [step, gs, gEv, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr
      simp only [Function.update_self]
      funext k
      simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul]
      have := hg j
      field_simp
    · simp [Function.update_of_ne hr]
  | scale i u c =>
    simp only [step, gs, gEv, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr
      simp only [Function.update_self]
      funext k
      simp only [Pi.smul_apply, smul_eq_mul]
      have := hg r
      field_simp
    · simp [Function.update_of_ne hr, h r hr]
  | copy i j c =>
    obtain ⟨h1, h2⟩ := h
    simp only [step, gs, gEv, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr; simp [h1]
    · simp [Function.update_of_ne hr, h2 r hr]

/-- Gauge a list with the time-indexed gauge `g` (g 0 before the first event). -/
def gList (g : ℕ → Reg → K) : List (Ev K Reg C) → List (Ev K Reg C)
  | [] => []
  | e :: es => gEv (g 0) (g 1) e :: gList (fun t => g (t + 1)) es

def AdmList (g : ℕ → Reg → K) : List (Ev K Reg C) → Prop
  | [] => True
  | e :: es => Adm (g 0) (g 1) e ∧ AdmList (fun t => g (t + 1)) es

/-- **Gauge covariance.** -/
theorem run_gauge : ∀ (evs : List (Ev K Reg C)) (g : ℕ → Reg → K) (s : St K Reg C),
    (∀ t r, g t r ≠ 0) → AdmList g evs →
      run (gs (g 0) s) (gList g evs) = gs (g evs.length) (run s evs)
  | [], _, _, _, _ => rfl
  | e :: es, g, s, hg, ⟨h1, h2⟩ => by
    simp only [gList, run, List.length_cons]
    rw [step_gauge (g 0) (g 1) (hg 0) s e h1]
    exact run_gauge es (fun t => g (t + 1)) (step s e) (fun t r => hg (t + 1) r) h2

/-- **Non-hub rows are preserved**: every register whose final gauge is 1 ends with the same row;
locations are untouched. -/
theorem row_preserved (evs : List (Ev K Reg C)) (g : ℕ → Reg → K) (s : St K Reg C)
    (hg : ∀ t r, g t r ≠ 0) (hA : AdmList g evs) (r : Reg) (hr : g evs.length r = 1) :
    (run (gs (g 0) s) (gList g evs)).row r = (run s evs).row r ∧
      (run (gs (g 0) s) (gList g evs)).loc = (run s evs).loc := by
  rw [run_gauge evs g s hg hA]; simp [gs, hr]

end Run

/-! ## (2) The joint hub settle re-absorbs the gauge -/

section Hub
variable {K N G0 G1 : Type*} [Field K] [Fintype N] [Fintype G0] [Fintype G1]
  [DecidableEq N] [DecidableEq G0] [DecidableEq G1]

/-- Gauging the interior with start gauge `D0` on the {0}-born rows and end gauge `Dv` on the V-enders
(non-V-enders end with gauge 1) turns the hub data into `Dv·X`, `X0·D0⁻¹`, `Rn0·D0⁻¹`; the prefix
`D0·M` and the V mix `C·Dv⁻¹` settle it. -/
theorem valid_gauge (Xn : Matrix G1 N K) (X0 : Matrix G1 G0 K) (Rn : Matrix G1 N K)
    (R0 : Matrix G1 G0 K) {NV : Type*} [Fintype NV] (Rn0 Fn0 : Matrix NV G0 K)
    (M D0 : Matrix G0 G0 K) (Dv : Matrix G1 G1 K) (hD0 : IsUnit D0.det) (hDv : IsUnit Dv.det)
    (h : Valid Xn X0 Rn R0 Rn0 Fn0 M) :
    Valid (Dv * Xn) (Dv * X0 * D0⁻¹) Rn R0 (Rn0 * D0⁻¹) Fn0 (D0 * M) := by
  obtain ⟨h1, C, hC, h2⟩ := h
  have hcancel : D0⁻¹ * (D0 * M) = M := by
    rw [← Matrix.mul_assoc, Matrix.nonsing_inv_mul _ hD0, Matrix.one_mul]
  refine ⟨by rw [Matrix.mul_assoc, hcancel, h1], C * Dv⁻¹, ?_, ?_⟩
  · rw [Matrix.det_mul, Matrix.det_nonsing_inv, Ring.inverse_of_isUnit hDv]
    exact hC.mul (hDv.unit⁻¹).isUnit
  · rw [Matrix.mul_assoc (Dv * X0), hcancel, Matrix.mul_assoc Dv, ← Matrix.mul_fromCols,
      Matrix.mul_assoc, ← Matrix.mul_assoc Dv⁻¹, Matrix.nonsing_inv_mul _ hDv, Matrix.one_mul, h2]

variable {A : Type*} [CommRing A] (φ : A →+* K)

theorem inGL_mul {n : Type*} [Fintype n] [DecidableEq n] (P Q : Matrix n n K)
    (hP : InGL φ P) (hQ : InGL φ Q) : InGL φ (P * Q) := by
  obtain ⟨P', hP', rfl⟩ := hP
  obtain ⟨Q', hQ', rfl⟩ := hQ
  exact ⟨P' * Q', by rw [Matrix.det_mul]; exact hP'.mul hQ', by rw [Matrix.map_mul]⟩

theorem inGL_diag {n : Type*} [Fintype n] [DecidableEq n] (d : n → Aˣ) :
    InGL φ (diagonal fun x => φ (d x)) := by
  refine ⟨diagonal fun x => (d x : A), ?_, by ext i j; by_cases h : i = j <;> simp [diagonal, h]⟩
  rw [det_diagonal, ← Units.coe_prod]
  exact Units.isUnit _

theorem diag_inv_mul {n : Type*} [Fintype n] [DecidableEq n] (d : n → Aˣ) :
    (diagonal fun x => φ (↑(d x)⁻¹ : A)) * diagonal (fun x => φ (d x)) = 1 := by
  rw [diagonal_mul_diagonal, ← diagonal_one]
  congr 1; funext x; rw [← map_mul, Units.inv_mul, map_one]

/-- **A-integrality is kept.** With gauges that are units of `A` (gen5 only normalises A-unit
coefficients), an `A`-integral prefix `M` and V mix `C` stay `A`-integral after re-absorption. -/
theorem valid_gauge_A (M : Matrix G0 G0 K) (C : Matrix G1 G1 K) (d0 : G0 → Aˣ) (dv : G1 → Aˣ)
    (hM : InGL φ M) (hC : InGL φ C) :
    InGL φ ((diagonal fun x => φ (d0 x)) * M) ∧
      InGL φ (C * diagonal fun x => φ (↑(dv x)⁻¹ : A)) ∧
      (diagonal fun x => φ (↑(dv x)⁻¹ : A)) = (diagonal fun x => φ (dv x))⁻¹ := by
  refine ⟨inGL_mul φ _ _ (inGL_diag φ d0) hM,
    inGL_mul φ _ _ hC (inGL_diag φ fun x => (dv x)⁻¹), ?_⟩
  exact (Matrix.inv_eq_left_inv (diag_inv_mul φ dv)).symm

end Hub

/-! ## (3) Spanning-forest normalisation -/

section Forest
variable {K S : Type*} [Field K]

/-- The forest gauge: a non-free segment has gauge 1; a free segment's gauge is fixed from its parent's
so that its parent edge (coefficient `a s`) becomes 1. Orientation `o s = true`: the edge coefficient
transforms as a·λ(s)/λ(par s) (s is the ADD target / the SCALE's after-segment); `false`: a·λ(par s)/λ(s). -/
def lam (free : S → Prop) [DecidablePred free] (par : S → S) (depth : S → ℕ)
    (hdep : ∀ s, free s → depth (par s) < depth s) (a : S → Kˣ) (o : S → Bool) (s : S) : Kˣ :=
  if _h : free s then
    (if o s then lam free par depth hdep a o (par s) * (a s)⁻¹
     else a s * lam free par depth hdep a o (par s)) else 1
termination_by depth s
decreasing_by all_goals exact hdep s ‹_›

variable (free : S → Prop) [DecidablePred free] (par : S → S)
  (depth : S → ℕ) (hdep : ∀ s, free s → depth (par s) < depth s) (a : S → Kˣ) (o : S → Bool)

/-- Gauged coefficient of the parent edge of `s`. -/
def ncoef (s : S) : Kˣ :=
  if o s then a s * lam free par depth hdep a o s / lam free par depth hdep a o (par s)
  else a s * lam free par depth hdep a o (par s) / lam free par depth hdep a o s

theorem lam_fixed (s : S) (hs : ¬ free s) : lam free par depth hdep a o s = 1 := by
  rw [lam]; simp [hs]

theorem lam_of_free (s : S) (hs : free s) : lam free par depth hdep a o s =
    if o s then lam free par depth hdep a o (par s) * (a s)⁻¹
    else a s * lam free par depth hdep a o (par s) := by
  rw [lam]; simp [hs]

/-- **Every forest edge is normalised to 1.** -/
theorem lam_norm (s : S) (hs : free s) : ncoef free par depth hdep a o s = 1 := by
  unfold ncoef
  rw [lam_of_free free par depth hdep a o s hs]
  cases ho : o s
  · rw [if_neg (by simp), if_neg (by simp)]; exact div_self' _
  · rw [if_pos rfl, if_pos rfl]
    apply Units.ext
    have h1 := (lam free par depth hdep a o (par s)).ne_zero
    have h2 := (a s).ne_zero
    simp only [Units.val_div_eq_div_val, Units.val_mul, Units.val_inv_eq_inv_val, Units.val_one]
    field_simp

/-- The gauge lies in any subgroup containing the forest coefficients (e.g. the units of A = ℤ[1/30]). -/
theorem lam_mem (H : Subgroup Kˣ) (hH : ∀ s, free s → a s ∈ H) :
    ∀ s, lam free par depth hdep a o s ∈ H := by
  intro s
  induction h : depth s using Nat.strong_induction_on generalizing s with
  | _ n ih =>
    rw [lam]
    by_cases hs : free s
    · have hp := ih (depth (par s)) (h ▸ hdep s hs) (par s) rfl
      simp only [hs, dif_pos]
      split
      · exact H.mul_mem hp (H.inv_mem (hH s hs))
      · exact H.mul_mem (hH s hs) hp
    · simp [hs, H.one_mem]

end Forest

/-! ## (4) Segments to gauge -/

section Seg
variable {K Reg C S : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] (free : S → Prop)

/-- Segment bookkeeping per event: a register keeps its segment unless the event is a SCALE, INIT or
CLEAR of it; a born register starts a non-free segment; COPY i j puts i in j's segment. -/
def SegAdm (σ σ' : Reg → S) : Ev K Reg C → Prop
  | .born i _ => ¬ free (σ' i) ∧ ∀ r, r ≠ i → σ' r = σ r
  | .init i _ | .clear i _ | .scale i _ _ => ∀ r, r ≠ i → σ' r = σ r
  | .copy i j _ => σ' i = σ j ∧ ∀ r, r ≠ i → σ' r = σ r
  | .move _ _ | .add _ _ _ _ => σ' = σ

def SegAdmList (seg : ℕ → Reg → S) : List (Ev K Reg C) → Prop
  | [] => True
  | e :: es => SegAdm free (seg 0) (seg 1) e ∧ SegAdmList (fun t => seg (t + 1)) es

theorem seg_adm (lv : S → Kˣ) (hfix : ∀ x, ¬ free x → lv x = 1) :
    ∀ (evs : List (Ev K Reg C)) (seg : ℕ → Reg → S), SegAdmList free seg evs →
      AdmList (fun t r => (lv (seg t r) : K)) evs
  | [], _, _ => trivial
  | e :: es, seg, ⟨h1, h2⟩ => by
    refine ⟨?_, seg_adm lv hfix es (fun t => seg (t + 1)) h2⟩
    cases e with
    | born i c => exact ⟨by simp [hfix _ h1.1], fun r hr => by simp [h1.2 r hr]⟩
    | init i c => exact fun r hr => by simp [h1 r hr]
    | clear i c => exact fun r hr => by simp [h1 r hr]
    | scale i u c => exact fun r hr => by simp [h1 r hr]
    | copy i j c => exact ⟨by simp [h1.1], fun r hr => by simp [h1.2 r hr]⟩
    | move i c => show (fun r => _) = (fun r => _); rw [show seg 1 = seg 0 from h1]
    | add i j a c => show (fun r => _) = (fun r => _); rw [show seg 1 = seg 0 from h1]

/-- **ALT r3 gauge, composed.** Segments with forest gauge `lam`: the gauged program (forest edges now
coefficient 1, `lam_norm`) ends with every register whose final segment is not free on its old row;
every register ends on (its final segment's unit) • (old row), which the hubs re-absorb (`valid_gauge`). -/
theorem forest_gauge (par : S → S) (depth : S → ℕ) (hdep : ∀ s, free s → depth (par s) < depth s)
    (a : S → Kˣ) (o : S → Bool) [DecidablePred free]
    (evs : List (Ev K Reg C)) (seg : ℕ → Reg → S) (hS : SegAdmList free seg evs) (s : St K Reg C) :
    let g := fun t r => (lam free par depth hdep a o (seg t r) : K)
    run (gs (g 0) s) (gList g evs) = gs (g evs.length) (run s evs) ∧
      ∀ r, ¬ free (seg evs.length r) →
        (run (gs (g 0) s) (gList g evs)).row r = (run s evs).row r := by
  intro g
  have hfix : ∀ x, ¬ free x → lam free par depth hdep a o x = 1 := lam_fixed free par depth hdep a o
  have hA := seg_adm free _ hfix evs seg hS
  have hg : ∀ t r, g t r ≠ 0 := fun t r => Units.ne_zero _
  refine ⟨run_gauge evs g s hg hA, fun r hr => (row_preserved evs g s hg hA r ?_).1⟩
  simp [g, hfix _ hr]

end Seg

end Gauge

#print axioms Gauge.run_gauge
#print axioms Gauge.row_preserved
#print axioms Gauge.valid_gauge
#print axioms Gauge.valid_gauge_A
#print axioms Gauge.lam_norm
#print axioms Gauge.lam_mem
#print axioms Gauge.forest_gauge
