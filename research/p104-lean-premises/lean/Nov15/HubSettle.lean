/-
Joint-hub derivation (internal notes). See HubSettle.md.

Build: imports the olean of RankLaw (which imports TokenCancel):
  lake env lean -o .lake/build/lib/lean/Nov15/TokenCancel.olean Nov15/TokenCancel.lean
  lake env lean -o .lake/build/lib/lean/Nov15/RankLaw.olean Nov15/RankLaw.lean
  lake env lean Nov15/HubSettle.lean
-/
import Nov15.RankLaw
import Mathlib.Data.Matrix.ColumnRowPartitioned

set_option linter.unusedSectionVars false
namespace HubSettle
open Submodule Module Matrix RankLaw

section Gauge
variable {K N G0 G1 NV ιU : Type*} [Field K]
  [Fintype N] [Fintype G0] [Fintype G1] [Fintype NV] [Fintype ιU]
  [DecidableEq N] [DecidableEq G0] [DecidableEq G1] [DecidableEq NV] [DecidableEq ιU]

/-- G0-parts of the V-ender combinations with zero non-G0 part: `{y·B : y·A = 0}`. -/
def kerPart (A : Matrix G1 N K) (B : Matrix G1 G0 K) : Submodule K (G0 → K) :=
  (LinearMap.ker A.vecMulLinear).map B.vecMulLinear

variable (Xn : Matrix G1 N K) (X0 : Matrix G1 G0 K) (Rn : Matrix G1 N K) (R0 : Matrix G1 G0 K)
  (Rn0 Fn0 : Matrix NV G0 K) (U0 V0 : Matrix ιU G0 K)

/-- A {0}-prefix `M` (mixing the G0 initial rows) is valid if the non-V rows land on their targets
(`R_n0 · M = F_n0`) and the V mix then exists for the V-enders' end rows `[X_n | X_0·M]`. -/
def Valid (M : Matrix G0 G0 K) : Prop :=
  Rn0 * M = Fn0 ∧ VMixM (fromCols Xn (X0 * M)) (fromCols Rn R0)

/-- Row span of the V-enders after prefix `M`, as a range. -/
abbrev P (M : Matrix G0 G0 K) : Submodule K (N ⊕ G0 → K) :=
  LinearMap.range (fromCols Xn (X0 * M)).vecMulLinear

abbrev Q : Submodule K (N ⊕ G0 → K) := LinearMap.range (fromCols Rn R0).vecMulLinear

theorem P_apply (M : Matrix G0 G0 K) (y : G1 → K) :
    (fromCols Xn (X0 * M)).vecMulLinear y = Sum.elim (y ᵥ* Xn) ((y ᵥ* X0) ᵥ* M) := by
  simp [vecMul_fromCols, vecMul_vecMul]

theorem valid_iff (M : Matrix G0 G0 K) :
    Valid Xn X0 Rn R0 Rn0 Fn0 M ↔ Rn0 * M = Fn0 ∧ P Xn X0 M = Q Rn R0 := by
  unfold Valid; rw [vmixM_iff_span, ← range_vecMulLinear, ← range_vecMulLinear]

/-- Kernel part of `P M`: `(0, v) ∈ P M` iff `v ∈ kerPart Xn X0 · M`. -/
theorem zero_mem_P (M : Matrix G0 G0 K) (v : G0 → K) :
    Sum.elim (0 : N → K) v ∈ P Xn X0 M ↔ v ∈ (kerPart Xn X0).map M.vecMulLinear := by
  constructor
  · rintro ⟨y, hy⟩
    rw [P_apply] at hy
    have h1 : y ᵥ* Xn = 0 := by funext n; have := congrFun hy (Sum.inl n); simpa using this
    have h2 : (y ᵥ* X0) ᵥ* M = v := by funext g; have := congrFun hy (Sum.inr g); simpa using this
    exact ⟨y ᵥ* X0, ⟨y, h1, rfl⟩, h2⟩
  · rintro ⟨_, ⟨y, hy, rfl⟩, rfl⟩
    refine ⟨y, ?_⟩
    rw [P_apply]
    have : y ᵥ* Xn = 0 := hy
    simp [this]

theorem zero_mem_Q (v : G0 → K) : Sum.elim (0 : N → K) v ∈ Q Rn R0 ↔ v ∈ kerPart Rn R0 := by
  have := zero_mem_P Rn R0 (1 : Matrix G0 G0 K) v
  simp only [P, Matrix.mul_one] at this
  rw [Q, this]
  constructor
  · rintro ⟨w, hw, rfl⟩; simpa using hw
  · intro hv; exact ⟨v, hv, by simp⟩

theorem span_rows_mul (A : Matrix ιU G0 K) (M : Matrix G0 G0 K) :
    span K (Set.range (A * M).row) = (span K (Set.range A.row)).map M.vecMulLinear := by
  rw [Submodule.map_span, ← Set.range_comp]; rfl

/-- **Joint-hub gauge (ALT r2).** Suppose some prefix `M⋆` is valid (the native's), the rows of
`R_n0` and `U0` together span the G0 space (`[R_n0; U0]` has full column rank; square
invertible on #7623), `U0` spans the zero-non-G0 part of the V-enders' end rows and `V0` that of
their targets. Then for EVERY invertible `G`, any `M` with `R_n0·M = F_n0` and `U0·M = G·V0` is a
valid prefix. -/
theorem prefix_valid (Mstar M : Matrix G0 G0 K) (GG : Matrix ιU ιU K)
    (hstar : Valid Xn X0 Rn R0 Rn0 Fn0 Mstar)
    (hspan : span K (Set.range Rn0.row) ⊔ span K (Set.range U0.row) = ⊤)
    (hU0 : span K (Set.range U0.row) = kerPart Xn X0)
    (hV0 : span K (Set.range V0.row) = kerPart Rn R0)
    (hG : IsUnit GG.det) (hR : Rn0 * M = Fn0) (hUM : U0 * M = GG * V0) :
    Valid Xn X0 Rn R0 Rn0 Fn0 M := by
  rw [valid_iff] at hstar ⊢
  obtain ⟨hRs, hPQ⟩ := hstar
  refine ⟨hR, ?_⟩
  -- the kernel part of P M is span V0
  have hGV : span K (Set.range (GG * V0).row) = span K (Set.range V0.row) :=
    ((vmixM_iff_span V0 (GG * V0)).1 ⟨GG, hG, rfl⟩).symm
  have hkerM : (kerPart Xn X0).map M.vecMulLinear = kerPart Rn R0 := by
    rw [← hU0, ← span_rows_mul, hUM, hGV, hV0]
  have hkerS : (kerPart Xn X0).map Mstar.vecMulLinear = kerPart Rn R0 := by
    ext v; rw [← zero_mem_P, hPQ, zero_mem_Q]
  -- D = M - M⋆ sends every vector into kerPart Rn R0
  have hD : ∀ w : G0 → K, w ᵥ* M - w ᵥ* Mstar ∈ kerPart Rn R0 := by
    intro w
    have hw : w ∈ span K (Set.range Rn0.row) ⊔ span K (Set.range U0.row) := hspan ▸ mem_top
    obtain ⟨a, ha, u, hu, rfl⟩ := mem_sup.1 hw
    have haD : a ᵥ* M - a ᵥ* Mstar = 0 := by
      rw [← range_vecMulLinear] at ha
      obtain ⟨t, rfl⟩ := ha
      simp only [vecMulLinear_apply, vecMul_vecMul, hR, hRs, sub_self]
    have huM : u ᵥ* M ∈ kerPart Rn R0 := by
      rw [← hkerM]; rw [hU0] at hu; exact ⟨u, hu, rfl⟩
    have huS : u ᵥ* Mstar ∈ kerPart Rn R0 := by
      rw [← hkerS]; rw [hU0] at hu; exact ⟨u, hu, rfl⟩
    have : (a + u) ᵥ* M - (a + u) ᵥ* Mstar = (a ᵥ* M - a ᵥ* Mstar) + (u ᵥ* M - u ᵥ* Mstar) := by
      simp only [add_vecMul]; abel
    rw [this, haD, zero_add]; exact sub_mem huM huS
  -- compare P M with P M⋆ = Q
  have hdiff : ∀ y : G1 → K, (fromCols Xn (X0 * M)).vecMulLinear y -
      (fromCols Xn (X0 * Mstar)).vecMulLinear y = Sum.elim (0 : N → K) ((y ᵥ* X0) ᵥ* M - (y ᵥ* X0) ᵥ* Mstar) := by
    intro y; rw [P_apply, P_apply]; funext x; cases x <;> simp
  apply le_antisymm
  · rintro _ ⟨y, rfl⟩
    have h1 : (fromCols Xn (X0 * Mstar)).vecMulLinear y ∈ Q Rn R0 := hPQ ▸ ⟨y, rfl⟩
    have h2 := (zero_mem_Q Rn R0 _).2 (hD (y ᵥ* X0))
    rw [← hdiff] at h2
    simpa using add_mem h1 h2
  · rw [← hPQ]
    rintro _ ⟨y, rfl⟩
    have h1 : (fromCols Xn (X0 * M)).vecMulLinear y ∈ P Xn X0 M := ⟨y, rfl⟩
    have h2 : Sum.elim (0 : N → K) ((y ᵥ* X0) ᵥ* M - (y ᵥ* X0) ᵥ* Mstar) ∈ P Xn X0 M := by
      rw [zero_mem_P, hkerM]; exact hD _
    rw [← hdiff] at h2
    simpa using sub_mem h1 h2

/-- **Converse: the gauge is all of it.** Every valid prefix has `U0·M = G·V0` for some `G`;
if `U0`, `V0` have independent rows and `M` is invertible, `G` is invertible. -/
theorem prefix_gauge (M : Matrix G0 G0 K) (hM : Valid Xn X0 Rn R0 Rn0 Fn0 M)
    (hU0 : span K (Set.range U0.row) = kerPart Xn X0)
    (hV0 : span K (Set.range V0.row) = kerPart Rn R0) :
    ∃ GG : Matrix ιU ιU K, U0 * M = GG * V0 ∧
      (LinearIndependent K U0.row → LinearIndependent K V0.row → IsUnit M.det → IsUnit GG.det) := by
  rw [valid_iff] at hM
  have hkerM : (kerPart Xn X0).map M.vecMulLinear = kerPart Rn R0 := by
    ext v; rw [← zero_mem_P, hM.2, zero_mem_Q]
  have hrow : ∀ i, U0 i ᵥ* M ∈ LinearMap.range V0.vecMulLinear := by
    intro i
    rw [range_vecMulLinear, hV0, ← hkerM, ← hU0]
    exact ⟨U0 i, subset_span ⟨i, rfl⟩, rfl⟩
  choose GG hGG using hrow
  have hmul : U0 * M = Matrix.of GG * V0 := by
    ext i j
    have := congrFun (hGG i) j
    simp only [vecMulLinear_apply] at this
    change (U0 i ᵥ* M) j = (GG i ᵥ* V0) j
    rw [this]
  refine ⟨Matrix.of GG, hmul, fun hUi hVi hMu => ?_⟩
  rw [← Matrix.vecMul_injective_iff] at hUi hVi
  rw [← Matrix.isUnit_iff_isUnit_det, ← Matrix.vecMul_injective_iff_isUnit]
  have hMi : Function.Injective (fun v : G0 → K => v ᵥ* M) :=
    Matrix.vecMul_injective_iff_isUnit.2 ((Matrix.isUnit_iff_isUnit_det _).2 hMu)
  intro t t' h
  apply hUi; apply hMi
  simp only [vecMul_vecMul, hmul]
  rw [← vecMul_vecMul, ← vecMul_vecMul]
  exact congrArg (fun w => w ᵥ* V0) h

/-- **The V mix is unique once the prefix is fixed** — provided the V-enders' end rows
`[X_n | X_0·M]` are independent (rank X[G1] = |G1|, checked [C] on #7623: 1052). -/
theorem vmix_unique (M : Matrix G0 G0 K)
    (hind : LinearIndependent K (fromCols Xn (X0 * M)).row) (C C' : Matrix G1 G1 K)
    (h : C * fromCols Xn (X0 * M) = fromCols Rn R0) (h' : C' * fromCols Xn (X0 * M) = fromCols Rn R0) :
    C = C' :=
  vmixM_unique _ _ hind C C' h h'

/-- **Finding (scope of "unique").** Without independent end rows the V mix is not unique:
one V-ender with end row 0 and target 0 admits every nonzero scalar. -/
theorem vmix_not_unique_example :
    Matrix.diagonal (fun _ : Unit => (2 : ℚ)) * 0 = (0 : Matrix Unit Unit ℚ) ∧
      (1 : Matrix Unit Unit ℚ) * 0 = 0 ∧ Matrix.diagonal (fun _ : Unit => (2 : ℚ)) ≠ 1 := by
  refine ⟨by simp, by simp, fun h => ?_⟩
  have := congrFun (congrFun h ()) (); simp [Matrix.diagonal] at this

/-- **The prefix formula.** If the stack `[R_n0; U0]` is square (via `e`) and invertible, then
`M = [R_n0; U0]⁻¹ [F_n0; G·V0]` solves both block equations, and the spanning hypothesis of
`prefix_valid` holds. -/
theorem prefix_formula (e : G0 ≃ NV ⊕ ιU) (GG : Matrix ιU ιU K)
    (hA : IsUnit ((fromRows Rn0 U0).submatrix e id).det) :
    let M := ((fromRows Rn0 U0).submatrix e id)⁻¹ * (fromRows Fn0 (GG * V0)).submatrix e id
    Rn0 * M = Fn0 ∧ U0 * M = GG * V0 ∧
      span K (Set.range Rn0.row) ⊔ span K (Set.range U0.row) = ⊤ := by
  intro M
  set A := (fromRows Rn0 U0).submatrix e id
  have hAM : A * M = (fromRows Fn0 (GG * V0)).submatrix e id := by
    rw [show M = A⁻¹ * (fromRows Fn0 (GG * V0)).submatrix e id from rfl, ← Matrix.mul_assoc,
      Matrix.mul_nonsing_inv _ hA, Matrix.one_mul]
  have hstack : fromRows Rn0 U0 * M = fromRows Fn0 (GG * V0) := by
    ext r j
    have := congrFun (congrFun hAM (e.symm r)) j
    simp only [A, Matrix.mul_apply, Matrix.submatrix_apply, id, Equiv.apply_symm_apply] at this
    rw [Matrix.mul_apply]; exact this
  rw [fromRows_mul] at hstack
  obtain ⟨h1, h2⟩ := fromRows_inj hstack
  refine ⟨h1, h2, eq_top_iff.2 (fun w _ => ?_)⟩
  have hw : w = (w ᵥ* A⁻¹) ᵥ* A := by
    rw [vecMul_vecMul, Matrix.nonsing_inv_mul _ hA, vecMul_one]
  rw [hw]
  have hrows : ∀ g, A g ∈ span K (Set.range Rn0.row) ⊔ span K (Set.range U0.row) := by
    intro g
    obtain ⟨x, hx⟩ : ∃ x, e g = x := ⟨_, rfl⟩
    have : A g = fromRows Rn0 U0 x := by rw [← hx]; rfl
    rw [this]
    rcases x with r | u
    · exact mem_sup_left (subset_span ⟨r, by funext j; simp [Matrix.row]⟩)
    · exact mem_sup_right (subset_span ⟨u, by funext j; simp [Matrix.row]⟩)
  have : (w ᵥ* A⁻¹) ᵥ* A ∈ span K (Set.range A.row) := by
    rw [← range_vecMulLinear]; exact ⟨_, rfl⟩
  exact (span_le.2 (by rintro _ ⟨g, rfl⟩; exact hrows g)) this

/-- **Gauge changes the determinant.** `det M_G = det G · det M_I`: the prefix for gauge `G`
differs from the `G = 1` prefix by exactly `det G`. -/
theorem det_prefix_gauge (e : G0 ≃ NV ⊕ ιU) (GG : Matrix ιU ιU K) :
    (((fromRows Rn0 U0).submatrix e id)⁻¹ * (fromRows Fn0 (GG * V0)).submatrix e id).det =
      GG.det * (((fromRows Rn0 U0).submatrix e id)⁻¹ * (fromRows Fn0 V0).submatrix e id).det := by
  have hB : (fromRows Fn0 (GG * V0)).submatrix e id =
      (fromBlocks 1 0 0 GG).submatrix e e * (fromRows Fn0 V0).submatrix e id := by
    ext g j
    simp only [Matrix.mul_apply, Matrix.submatrix_apply, id]
    rw [← Equiv.sum_comp e.symm]
    simp only [Equiv.apply_symm_apply, Fintype.sum_sum_type]
    rcases e g with r | u
    · simp [fromBlocks, Matrix.one_apply]
    · simp [fromBlocks, Matrix.mul_apply]
  rw [hB, Matrix.det_mul, Matrix.det_mul, Matrix.det_mul, Matrix.det_submatrix_equiv_self,
    det_fromBlocks_zero₂₁, Matrix.det_one, one_mul]
  ring

end Gauge
section Prefix
open TokenCancel
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- Apply a linear map to every row (a change of initial-row coordinates). -/
def mapRows (L : (Reg → K) →ₗ[K] (Reg → K)) (s : St K Reg C) : St K Reg C :=
  ⟨fun r => L (s.row r), s.loc⟩

/-- Ops commute with any coordinate change that fixes the birth tokens. -/
theorem step_mapRows (L : (Reg → K) →ₗ[K] (Reg → K)) (s : St K Reg C) (e : Ev K Reg C)
    (hb : ∀ i c, e = .born i c → L (Pi.single i 1) = Pi.single i 1) :
    step (mapRows L s) e = mapRows L (step s e) := by
  cases e with
  | born i c =>
    simp only [step, mapRows, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr; simp [hb r c rfl]
    · simp [Function.update_of_ne hr]
  | init i c =>
    simp only [step, mapRows, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr; simp
    · simp [Function.update_of_ne hr]
  | move i c => rfl
  | add i j a c =>
    simp only [step, mapRows, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr; simp
    · simp [Function.update_of_ne hr]
  | scale i u c =>
    simp only [step, mapRows, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr; simp
    · simp [Function.update_of_ne hr]
  | clear i c =>
    simp only [step, mapRows, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr; simp
    · simp [Function.update_of_ne hr]
  | copy i j c =>
    simp only [step, mapRows, St.mk.injEq, and_true]
    funext r; by_cases hr : r = i
    · subst hr; simp
    · simp [Function.update_of_ne hr]

/-- **The {0}-prefix is a right multiplication on the G0 columns.** Mixing the initial rows of
the {0}-born registers by `L` (any linear map fixing the tokens of the registers born later) and
then running the mid program gives `L` applied to the end rows of the unmixed run. With
`L v = v ᵥ* M` on the G0 columns this is `[X_n | X_0·M]`. -/
theorem run_mapRows (L : (Reg → K) →ₗ[K] (Reg → K)) (s : St K Reg C) (evs : List (Ev K Reg C))
    (hb : ∀ i c, Ev.born i c ∈ evs → L (Pi.single i 1) = Pi.single i 1) :
    run (mapRows L s) evs = mapRows L (run s evs) := by
  induction evs generalizing s with
  | nil => rfl
  | cons e es ih =>
    simp only [run]
    rw [step_mapRows L s e (fun i c he => hb i c (he ▸ List.mem_cons_self))]
    exact ih _ (fun i c h => hb i c (List.mem_cons_of_mem _ h))

end Prefix

section Local
/-! ## Localisation `A = ℤ[1/m] ⊆ ℚ` (any domain `A` with an injective map into a field `F`). -/
variable {A F n : Type*} [CommRing A] [Field F] [Fintype n] [DecidableEq n] (φ : A →+* F)

/-- `M` lies in `GL_n(A)`: it is the image of an `A`-matrix with unit determinant. -/
def InGL (M : Matrix n n F) : Prop := ∃ M' : Matrix n n A, IsUnit M'.det ∧ M'.map φ = M

theorem det_map' (X : Matrix n n A) : (X.map φ).det = φ X.det := by
  rw [RingHom.map_det]; rfl

/-- **Sufficiency.** If `A1`, `B` are `A`-matrices with unit determinants, the solution of
`A1·M = B` over `F` lies in `GL_n(A)`: no non-unit denominators can appear. -/
theorem solve_inGL (A1 B : Matrix n n A) (h1 : IsUnit A1.det) (h2 : IsUnit B.det)
    (M : Matrix n n F) (hM : A1.map φ * M = B.map φ) : InGL φ M := by
  refine ⟨A1⁻¹ * B, ?_, ?_⟩
  · rw [Matrix.det_mul, Matrix.det_nonsing_inv, Ring.inverse_of_isUnit h1]
    exact (h1.unit⁻¹).isUnit.mul h2
  · have hA1 : IsUnit (A1.map φ).det := by
      rw [det_map']; exact h1.map φ
    have hsol : A1.map φ * (A1⁻¹ * B).map φ = B.map φ := by
      rw [← Matrix.map_mul, ← Matrix.mul_assoc, Matrix.mul_nonsing_inv _ h1, Matrix.one_mul]
    have := congrArg (fun X => (A1.map φ)⁻¹ * X) (hsol.trans hM.symm)
    simpa [← Matrix.mul_assoc, Matrix.nonsing_inv_mul _ hA1] using this

/-- **Necessity is only for the ratio.** If `M ∈ GL_n(A)` solves `A1·M = B`, then
`φ(det B) = φ(u)·φ(det A1)` for a unit `u` of `A`; the individual determinants need not be units. -/
theorem inGL_det_ratio (A1 B : Matrix n n A) (M : Matrix n n F) (hM : A1.map φ * M = B.map φ)
    (hG : InGL φ M) : ∃ u : Aˣ, φ B.det = φ u * φ A1.det := by
  obtain ⟨M', hu, rfl⟩ := hG
  refine ⟨hu.unit, ?_⟩
  have := congrArg Matrix.det hM
  rw [Matrix.det_mul, det_map', det_map', det_map'] at this
  rw [← this, IsUnit.unit_spec, mul_comm]

/-- **Finding: the literal "iff" is false.** Over `A = ℤ ⊆ ℚ`: `A1 = B = (2)` gives `M = 1 ∈ GL(ℤ)`
although `det A1 = 2` is not a unit of `ℤ`. -/
theorem iff_false_example :
    let A1 : Matrix Unit Unit ℤ := Matrix.diagonal fun _ => 2
    A1.map (Int.castRingHom ℚ) * 1 = A1.map (Int.castRingHom ℚ) ∧
      InGL (Int.castRingHom ℚ) (1 : Matrix Unit Unit ℚ) ∧ ¬ IsUnit A1.det := by
  intro A1
  refine ⟨Matrix.mul_one _, ⟨1, by simp, by simp⟩, ?_⟩
  simp only [A1, Matrix.det_diagonal, Finset.univ_unique, Finset.prod_singleton]
  decide

end Local

#print axioms HubSettle.prefix_valid
#print axioms HubSettle.prefix_gauge
#print axioms HubSettle.prefix_formula
#print axioms HubSettle.vmix_unique
#print axioms HubSettle.vmix_not_unique_example
#print axioms HubSettle.det_prefix_gauge
#print axioms HubSettle.solve_inGL
#print axioms HubSettle.inGL_det_ratio
#print axioms HubSettle.iff_false_example
#print axioms HubSettle.run_mapRows
end HubSettle
