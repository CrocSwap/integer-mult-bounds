import Nov15.TokenCancel
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.LinearAlgebra.Determinant
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.LinearAlgebra.Matrix.Transvection
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.LinearAlgebra.Projection
import Mathlib.LinearAlgebra.Isomorphisms
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

set_option linter.unusedSectionVars false
namespace RankLaw
open Submodule Module

section Equiv
variable {K V W : Type*} [Field K] [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]
  [FiniteDimensional K V]

/-- Two linear maps out of a finite-dimensional space with the same range differ by an
automorphism of the source. -/
theorem exists_equiv_comp (f g : V →ₗ[K] W) (h : LinearMap.range f = LinearMap.range g) :
    ∃ φ : V ≃ₗ[K] V, f ∘ₗ φ.toLinearMap = g := by
  obtain ⟨Qg, hQg⟩ := Submodule.exists_isCompl (LinearMap.ker g)
  obtain ⟨Qf, hQf⟩ := Submodule.exists_isCompl (LinearMap.ker f)
  have hk : finrank K (LinearMap.ker g) = finrank K (LinearMap.ker f) := by
    have h1 := LinearMap.finrank_range_add_finrank_ker f
    have h2 := LinearMap.finrank_range_add_finrank_ker g
    rw [h] at h1; omega
  let e1 : LinearMap.ker g ≃ₗ[K] LinearMap.ker f := LinearEquiv.ofFinrankEq _ _ hk
  let e2 : Qg ≃ₗ[K] Qf :=
    (Submodule.quotientEquivOfIsCompl _ _ hQg).symm ≪≫ₗ g.quotKerEquivRange ≪≫ₗ
      (LinearEquiv.ofEq _ _ h.symm) ≪≫ₗ f.quotKerEquivRange.symm ≪≫ₗ
      Submodule.quotientEquivOfIsCompl _ _ hQf
  let φ : V ≃ₗ[K] V := (Submodule.prodEquivOfIsCompl _ _ hQg).symm ≪≫ₗ (e1.prodCongr e2) ≪≫ₗ
      Submodule.prodEquivOfIsCompl _ _ hQf
  refine ⟨φ, ?_⟩
  -- key: f (e2 q) = g q
  have key : ∀ q : Qg, f (e2 q : V) = g q := by
    intro q
    set y : Qf := e2 q
    have hy : (Submodule.Quotient.mk (y : V) : V ⧸ LinearMap.ker f) =
        f.quotKerEquivRange.symm (LinearEquiv.ofEq _ _ h.symm
          (g.quotKerEquivRange (Submodule.Quotient.mk (q : V)))) := by
      have := Submodule.mk_quotientEquivOfIsCompl_apply hQf
        (f.quotKerEquivRange.symm (LinearEquiv.ofEq _ _ h.symm
          (g.quotKerEquivRange (Submodule.Quotient.mk (q : V)))))
      convert this using 2
      simp [y, e2, Submodule.quotientEquivOfIsCompl_symm_apply]
    have := congrArg (fun t => (f.quotKerEquivRange t : W)) hy
    simpa using this
  apply LinearMap.ext; intro v
  obtain ⟨⟨k, q⟩, rfl⟩ := (Submodule.prodEquivOfIsCompl _ _ hQg).surjective v
  have hφ : φ ((Submodule.prodEquivOfIsCompl _ _ hQg) (k, q)) = (e1 k : V) + (e2 q : V) := by
    simp only [φ, LinearEquiv.trans_apply, LinearEquiv.symm_apply_apply]
    rfl
  rw [LinearMap.comp_apply, LinearEquiv.coe_coe, hφ, coe_prodEquivOfIsCompl', map_add, map_add]
  have hk0 : f (e1 k : V) = 0 := (e1 k).2
  have hg0 : g (k : V) = 0 := k.2
  rw [hk0, hg0, key]
end Equiv


section Mix
variable {K G ι : Type*} [Field K] [Fintype G] [DecidableEq G]

/-- **The V-mix target, as a linear system.** Given the end rows `X` of the registers that end at V
(indexed by `G`) and their target rows `R`, a V mix is an invertible `C` with `C * X = R`. -/
def VMixM (X R : Matrix G ι K) : Prop := ∃ C : Matrix G G K, IsUnit C.det ∧ C * X = R

/-- The V-mix system is solvable iff the end rows and the target rows span the same space. -/
theorem vmixM_iff_span (X R : Matrix G ι K) :
    VMixM X R ↔ span K (Set.range X.row) = span K (Set.range R.row) := by
  constructor
  · rintro ⟨C, hC, hCX⟩
    have hR : ∀ g, R.row g ∈ span K (Set.range X.row) := by
      intro g; rw [← hCX]
      have : (C * X).row g = Matrix.vecMul (C g) X := rfl
      rw [this, ← range_vecMulLinear X]; exact ⟨C g, rfl⟩
    have hX : X = C⁻¹ * R := by rw [← hCX, ← Matrix.mul_assoc, Matrix.nonsing_inv_mul _ hC, Matrix.one_mul]
    have hXR : ∀ g, X.row g ∈ span K (Set.range R.row) := by
      intro g; rw [hX]
      have : (C⁻¹ * R).row g = Matrix.vecMul (C⁻¹ g) R := rfl
      rw [this, ← range_vecMulLinear R]; exact ⟨C⁻¹ g, rfl⟩
    apply le_antisymm
    · exact span_le.2 (by rintro _ ⟨g, rfl⟩; exact hXR g)
    · exact span_le.2 (by rintro _ ⟨g, rfl⟩; exact hR g)
  · intro h
    have h' : LinearMap.range X.vecMulLinear = LinearMap.range R.vecMulLinear := by
      rw [range_vecMulLinear, range_vecMulLinear]; exact h
    obtain ⟨φ, hφ⟩ := exists_equiv_comp X.vecMulLinear R.vecMulLinear h'
    refine ⟨(LinearMap.toMatrix' φ.toLinearMap).transpose, ?_, ?_⟩
    · rw [Matrix.det_transpose, LinearMap.det_toMatrix']
      exact LinearEquiv.isUnit_det' φ
    · ext g j
      have e := congrArg (fun F : (G → K) →ₗ[K] (ι → K) => F (Pi.single g 1) j) hφ
      simp only [LinearMap.comp_apply, Matrix.vecMulLinear_apply, LinearEquiv.coe_coe] at e
      rw [Matrix.single_one_vecMul] at e
      have hrow : (fun k => (LinearMap.toMatrix' φ.toLinearMap).transpose g k) = φ (Pi.single g 1) := by
        funext k; simp [Matrix.transpose_apply, LinearMap.toMatrix'_apply]
      change Matrix.vecMul _ X j = R.row g j
      rw [hrow, e]
/-- If the targets are independent, a V mix makes the end rows independent too ("G1 rows are
|G1| independent vectors inside span(G1 targets)"). -/
theorem vmixM_indep (X R : Matrix G ι K) (h : VMixM X R) (hR : LinearIndependent K R.row) :
    LinearIndependent K X.row := by
  obtain ⟨C, hC, hCX⟩ := h
  have hX : X = C⁻¹ * R := by
    rw [← hCX, ← Matrix.mul_assoc, Matrix.nonsing_inv_mul _ hC, Matrix.one_mul]
  rw [← Matrix.vecMul_injective_iff] at hR ⊢
  have hCi : Function.Injective (fun v : G → K => Matrix.vecMul v C⁻¹) :=
    Matrix.vecMul_injective_iff_isUnit.2 ((Matrix.isUnit_iff_isUnit_det _).2 ((Matrix.isUnit_nonsing_inv_det_iff).2 hC))
  intro v w hvw
  apply hCi; apply hR
  simpa [hX, Matrix.vecMul_vecMul] using hvw

/-- **Uniqueness.** With independent end rows, the V mix is unique. -/
theorem vmixM_unique (X R : Matrix G ι K) (hX : LinearIndependent K X.row)
    (C C' : Matrix G G K) (h : C * X = R) (h' : C' * X = R) : C = C' := by
  rw [← Matrix.vecMul_injective_iff] at hX
  ext g h0
  have : Matrix.vecMul (C g) X = Matrix.vecMul (C' g) X := by
    have e1 : (C * X).row g = Matrix.vecMul (C g) X := rfl
    have e2 : (C' * X).row g = Matrix.vecMul (C' g) X := rfl
    rw [← e1, ← e2, h, h']
  exact congrFun (hX this) h0

/-- **Token order affects only fill.** `vmixM_iff_span` (and `rank_law`) carry no order hypothesis:
existence of the V mix does not depend on any carrier/token order. An order only shapes `C`:
if the end rows are a block-triangular (w.r.t. the order `b`) invertible recombination of the
targets, the V mix is block-triangular, so it has no fill outside the triangle. -/
theorem vmixM_fill {α : Type*} [LinearOrder α] (b : G → α) (X R : Matrix G ι K)
    (Tg : Matrix G G K) (hT : Tg.BlockTriangular b) (hdet : IsUnit Tg.det) (hX : X = Tg * R) :
    ∃ C : Matrix G G K, IsUnit C.det ∧ C * X = R ∧ C.BlockTriangular b := by
  letI := Matrix.invertibleOfIsUnitDet Tg hdet
  refine ⟨Tg⁻¹, (Matrix.isUnit_nonsing_inv_det_iff).2 hdet, ?_,
    Matrix.blockTriangular_inv_of_blockTriangular hT⟩
  rw [hX, ← Matrix.mul_assoc, Matrix.nonsing_inv_mul _ hdet, Matrix.one_mul]

/-- **Realisability by V-hub ops.** Every V mix factors into transvections (ADD i += c·j between
two V-enders), a diagonal with nonzero entries (SCALEs), and transvections. -/
theorem vmix_ops (Cm : Matrix G G K) (hC : IsUnit Cm.det) :
    ∃ (L L' : List (Matrix.TransvectionStruct G K)) (D : G → K), (∀ g, D g ≠ 0) ∧
      Cm = (L.map Matrix.TransvectionStruct.toMatrix).prod * Matrix.diagonal D *
        (L'.map Matrix.TransvectionStruct.toMatrix).prod := by
  obtain ⟨L, L', D, hM⟩ := Matrix.Pivot.exists_list_transvec_mul_diagonal_mul_list_transvec Cm
  refine ⟨L, L', D, fun g hg => ?_, hM⟩
  have hdet : Cm.det = ∏ g, D g := by
    rw [hM, Matrix.det_mul, Matrix.det_mul, Matrix.TransvectionStruct.det_toMatrix_prod,
      Matrix.TransvectionStruct.det_toMatrix_prod, Matrix.det_diagonal]; simp
  rw [hdet] at hC
  exact hC.ne_zero (Finset.prod_eq_zero (Finset.mem_univ g) hg)

end Mix

section Run
open TokenCancel
variable {K Reg C : Type*} [Field K] [Fintype Reg] [DecidableEq Reg] [DecidableEq C]

/-- Span of the rows of a state. -/
abbrev Sp (s : St K Reg C) : Submodule K (Reg → K) := span K (Set.range s.row)

/-- Rows of the other registers. -/
abbrev Oth (s : St K Reg C) (i : Reg) : Submodule K (Reg → K) := span K (s.row '' {r | r ≠ i})

theorem span_range_update (f : Reg → Reg → K) (i : Reg) (v : Reg → K) :
    span K (Set.range (Function.update f i v)) = span K (f '' {r | r ≠ i}) ⊔ K ∙ v := by
  have : Set.range (Function.update f i v) = f '' {r | r ≠ i} ∪ {v} := by
    ext x; constructor
    · rintro ⟨r, rfl⟩
      by_cases hr : r = i
      · subst hr; simp
      · left; exact ⟨r, hr, by simp [Function.update_of_ne hr]⟩
    · rintro (⟨r, hr, rfl⟩ | hx)
      · exact ⟨r, by simp [Function.update_of_ne (show r ≠ i from hr)]⟩
      · rw [Set.mem_singleton_iff] at hx; exact ⟨i, by simp [hx]⟩
  rw [this, span_union]

theorem span_range_eq (f : Reg → Reg → K) (i : Reg) :
    span K (Set.range f) = span K (f '' {r | r ≠ i}) ⊔ K ∙ f i := by
  conv_lhs => rw [show f = Function.update f i (f i) by simp]
  exact span_range_update f i (f i)

theorem sup_singleton_add (S : Submodule K (Reg → K)) (x w : Reg → K) (hw : w ∈ S) :
    S ⊔ K ∙ (x + w) = S ⊔ K ∙ x := by
  apply le_antisymm
  · refine sup_le le_sup_left ((span_singleton_le_iff_mem _ _).2 ?_)
    exact add_mem (mem_sup_right (mem_span_singleton_self x)) (mem_sup_left hw)
  · refine sup_le le_sup_left ((span_singleton_le_iff_mem _ _).2 ?_)
    have h := sub_mem (mem_sup_right (mem_span_singleton_self (x + w)) : x + w ∈ S ⊔ K ∙ (x + w))
      (mem_sup_left hw : w ∈ S ⊔ K ∙ (x + w))
    simpa using h

/-- A loss of rank: CLEAR or COPY (onto a different source) of a row that is not in the span of
the other rows at that instant. -/
def Lossy (s : St K Reg C) : Ev K Reg C → Prop
  | .clear i _ => s.row i ∉ Oth s i
  | .copy i j _ => i ≠ j ∧ s.row i ∉ Oth s i
  | _ => False

/-- A loss somewhere along the run. -/
def Loss : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => False
  | s, e :: es => Lossy s e ∨ Loss (step s e) es

/-- Every SCALE factor is nonzero (a SCALE by 0 is a CLEAR). -/
def NZ : Ev K Reg C → Prop
  | .scale _ u _ => u ≠ 0
  | _ => True

/-- Tokens: registers present at the start plus registers born so far. -/
def tokStep (T : Finset Reg) : Ev K Reg C → Finset Reg
  | .born i _ => insert i T
  | _ => T

def tokRun (T : Finset Reg) : List (Ev K Reg C) → Finset Reg
  | [] => T
  | e :: es => tokRun (tokStep T e) es

/-- Token span. -/
abbrev TS (T : Finset Reg) : Submodule K (Reg → K) :=
  span K ((fun r => (Pi.single r (1 : K) : Reg → K)) '' (T : Set Reg))

theorem finrank_TS (T : Finset Reg) : finrank K (TS (K := K) T) = T.card := by
  let b : T → Reg → K := fun r => Pi.single (r : Reg) (1 : K)
  have hb : LinearIndependent K b := by
    have := (Pi.basisFun K Reg).linearIndependent.comp (Subtype.val : T → Reg) Subtype.val_injective
    convert this using 1; funext r; simp [b, Pi.basisFun_apply]
  have hr : Set.range b = (fun r => (Pi.single r (1 : K) : Reg → K)) '' (T : Set Reg) := by
    ext x; simp [b]
  have := finrank_span_eq_card hb
  rw [hr] at this
  rw [this, Fintype.card_coe]

variable (z V : C)

/-- Bookkeeping invariant: absent registers have row 0; tokens are present registers. -/
def Good (s : St K Reg C) (T : Finset Reg) : Prop :=
  (∀ r, s.loc r = none → s.row r = 0) ∧ (∀ r ∈ T, s.loc r ≠ none)

theorem good_step (s : St K Reg C) (T : Finset Reg) (e : Ev K Reg C)
    (hL : LegalEv z V s e) (hG : Good s T) : Good (step s e) (tokStep T e) := by
  obtain ⟨h1, h2⟩ := hG
  cases e with
  | born i c =>
    refine ⟨fun r hr => ?_, fun r hr => ?_⟩
    · by_cases hri : r = i
      · subst hri; simp [step] at hr
      · simp only [step, Function.update_of_ne hri] at hr ⊢; exact h1 r hr
    · by_cases hri : r = i
      · subst hri; simp [step]
      · simp only [tokStep, Finset.mem_insert, hri, false_or] at hr
        simp only [step, Function.update_of_ne hri]; exact h2 r hr
  | init i c =>
    refine ⟨fun r hr => ?_, fun r hr => ?_⟩
    · by_cases hri : r = i
      · subst hri; simp [step]
      · simp only [step, Function.update_of_ne hri] at hr ⊢; exact h1 r hr
    · by_cases hri : r = i
      · subst hri; simp [step]
      · simp only [step, Function.update_of_ne hri]; exact h2 r hr
  | move i c =>
    refine ⟨fun r hr => ?_, fun r hr => ?_⟩
    · by_cases hri : r = i
      · subst hri; simp [step] at hr
      · simp only [step, Function.update_of_ne hri] at hr ⊢; exact h1 r hr
    · by_cases hri : r = i
      · subst hri; simp [step]
      · simp only [step, Function.update_of_ne hri]; exact h2 r hr
  | add i j a c =>
    obtain ⟨-, hi, -⟩ := hL
    refine ⟨fun r hr => ?_, h2⟩
    by_cases hri : r = i
    · subst hri; simp [step, hi] at hr
    · simp only [step, Function.update_of_ne hri] at hr ⊢; exact h1 r hr
  | scale i u c =>
    have hi : s.loc i = some c := hL
    refine ⟨fun r hr => ?_, h2⟩
    by_cases hri : r = i
    · subst hri; simp only [step] at hr; rw [hi] at hr; exact absurd hr (by simp)
    · simp only [step, Function.update_of_ne hri] at hr ⊢; exact h1 r hr
  | clear i c =>
    refine ⟨fun r hr => ?_, h2⟩
    by_cases hri : r = i
    · subst hri; simp [step]
    · simp only [step, Function.update_of_ne hri] at hr ⊢; exact h1 r hr
  | copy i j c =>
    obtain ⟨hi, -⟩ := hL
    refine ⟨fun r hr => ?_, h2⟩
    by_cases hri : r = i
    · subst hri; simp [step, hi] at hr
    · simp only [step, Function.update_of_ne hri] at hr ⊢; exact h1 r hr

theorem Sp_eq_oth (s : St K Reg C) (i : Reg) : Sp s = Oth s i ⊔ K ∙ s.row i :=
  span_range_eq s.row i

theorem Sp_update (s : St K Reg C) (i : Reg) (v : Reg → K) (l : Reg → Option C) :
    Sp (⟨Function.update s.row i v, l⟩ : St K Reg C) = Oth s i ⊔ K ∙ v :=
  span_range_update s.row i v

theorem mem_oth (s : St K Reg C) {i j : Reg} (h : j ≠ i) : s.row j ∈ Oth s i :=
  subset_span ⟨j, h, rfl⟩

/-- **Only CLEAR (and COPY) can lose rank.** Every non-birth op keeps the row span inside the
old one. -/
theorem Sp_step_le (s : St K Reg C) (T : Finset Reg) (e : Ev K Reg C) (hb : ∀ i c, e ≠ .born i c)
    (hL : LegalEv z V s e) (hG : Good s T) : Sp (step s e) ≤ Sp s := by
  cases e with
  | born i c => exact absurd rfl (hb i c)
  | init i c =>
    have h0 : s.row i = 0 := hG.1 i hL
    simp only [step]; rw [Sp_update, Sp_eq_oth s i, h0]
  | move i c => exact le_rfl
  | add i j a c =>
    simp only [step]; rw [Sp_update, Sp_eq_oth s i,
      sup_singleton_add _ _ _ (smul_mem _ _ (mem_oth s (Ne.symm hL.1)))]
  | scale i u c =>
    simp only [step]; rw [Sp_update, Sp_eq_oth s i]
    exact sup_le_sup_left ((span_singleton_le_iff_mem _ _).2
      (smul_mem _ _ (mem_span_singleton_self _))) _
  | clear i c =>
    simp only [step]; rw [Sp_update, Sp_eq_oth s i, span_singleton_eq_bot.2 rfl, sup_bot_eq]
    exact le_sup_left
  | copy i j c =>
    simp only [step]; rw [Sp_update, Sp_eq_oth s i]
    by_cases hij : j = i
    · subst hij; exact le_rfl
    · exact sup_le le_sup_left (le_trans ((span_singleton_le_iff_mem _ _).2 (mem_oth s hij))
        le_sup_left)

theorem TS_insert (T : Finset Reg) (i : Reg) :
    TS (K := K) (insert i T) = TS (K := K) T ⊔ K ∙ (Pi.single i (1 : K) : Reg → K) := by
  simp only [TS, Finset.coe_insert, Set.image_insert_eq, span_insert]; exact sup_comm _ _

/-- A non-lossy step keeps the row span equal to the token span (SCALE factors nonzero). -/
theorem Sp_step_noloss (s : St K Reg C) (T : Finset Reg) (e : Ev K Reg C)
    (hL : LegalEv z V s e) (hN : NZ e) (hG : Good s T) (hS : Sp s = TS T) (hl : ¬ Lossy s e) :
    Sp (step s e) = TS (tokStep T e) := by
  cases e with
  | born i c =>
    have h0 : s.row i = 0 := hG.1 i hL
    have : Sp s = Oth s i := by rw [Sp_eq_oth s i, h0, span_singleton_eq_bot.2 rfl, sup_bot_eq]
    simp only [step, tokStep]; rw [Sp_update, TS_insert, ← hS, this]
  | init i c =>
    have h0 : s.row i = 0 := hG.1 i hL
    simp only [step, tokStep]; rw [Sp_update, ← hS, Sp_eq_oth s i, h0]
  | move i c => exact hS
  | add i j a c =>
    simp only [step, tokStep]; rw [Sp_update, ← hS, Sp_eq_oth s i,
      sup_singleton_add _ _ _ (smul_mem _ _ (mem_oth s (Ne.symm hL.1)))]
  | scale i u c =>
    simp only [step, tokStep]; rw [Sp_update, ← hS, Sp_eq_oth s i,
      span_singleton_smul_eq (IsUnit.mk0 _ hN)]
  | clear i c =>
    have hm : s.row i ∈ Oth s i := not_not.1 hl
    simp only [step, tokStep]; rw [Sp_update, ← hS, Sp_eq_oth s i, span_singleton_eq_bot.2 rfl,
      sup_bot_eq, sup_eq_left.2 ((span_singleton_le_iff_mem _ _).2 hm)]
  | copy i j c =>
    simp only [step, tokStep]
    by_cases hij : j = i
    · subst hij; simpa using hS
    · have hm : s.row i ∈ Oth s i := by
        by_contra h; exact hl ⟨Ne.symm hij, h⟩
      rw [Sp_update, ← hS, Sp_eq_oth s i, sup_eq_left.2 ((span_singleton_le_iff_mem _ _).2 hm),
        sup_eq_left.2 ((span_singleton_le_iff_mem _ _).2 (mem_oth s hij))]

open Classical in
/-- Rank bookkeeping for one step: rank + tokens never gains, and a lossy step loses one. -/
theorem rank_step (s : St K Reg C) (T : Finset Reg) (e : Ev K Reg C)
    (hL : LegalEv z V s e) (hG : Good s T) :
    finrank K (Sp (step s e)) + T.card + (if Lossy s e then 1 else 0) ≤
      finrank K (Sp s) + (tokStep T e).card := by
  classical
  by_cases hb : ∃ i c, e = .born i c
  · obtain ⟨i, c, rfl⟩ := hb
    have hloc : s.loc i = none := hL
    have h0 : s.row i = 0 := hG.1 i hloc
    have hiT : i ∉ T := fun h => hG.2 i h hloc
    have hl : ¬ Lossy s (.born i c : Ev K Reg C) := id
    simp only [hl, if_false, add_zero, tokStep, Finset.card_insert_of_notMem hiT]
    have hS : Sp s = Oth s i := by rw [Sp_eq_oth s i, h0, span_singleton_eq_bot.2 rfl, sup_bot_eq]
    have hE : Sp (step s (.born i c)) = Oth s i ⊔ K ∙ (Pi.single i (1:K) : Reg → K) := by
      simp only [step]; rw [Sp_update]
    have e1 := congrArg (fun S : Submodule K (Reg → K) => finrank K S) hE
    have e2 := congrArg (fun S : Submodule K (Reg → K) => finrank K S) hS
    have := Submodule.finrank_add_le_finrank_add_finrank (Oth s i) (K ∙ (Pi.single i (1:K) : Reg → K))
    have hv : (Pi.single i (1:K) : Reg → K) ≠ 0 := fun h => by simpa using congrFun h i
    have h1 := finrank_span_singleton (K := K) hv
    omega
  · push Not at hb
    have hle := Sp_step_le z V s T e hb hL hG
    have hT : tokStep T e = T := by cases e <;> simp_all [tokStep]
    rw [hT]
    by_cases hl : Lossy s e
    · simp only [hl, if_true]
      have hlt : Sp (step s e) < Sp s := by
        refine lt_of_le_of_ne hle (fun heq => ?_)
        cases e with
        | clear i c =>
          apply hl
          have : s.row i ∈ Sp s := subset_span ⟨i, rfl⟩
          rw [← heq] at this; simp only [step] at this
          rw [Sp_update, span_singleton_eq_bot.2 rfl, sup_bot_eq] at this; exact this
        | copy i j c =>
          apply hl.2
          have : s.row i ∈ Sp s := subset_span ⟨i, rfl⟩
          rw [← heq] at this; simp only [step] at this
          rwa [Sp_update, sup_eq_left.2 ((span_singleton_le_iff_mem _ _).2 (mem_oth s hl.1.symm))]
            at this
        | _ => exact hl.elim
      have := Submodule.finrank_lt_finrank_of_lt hlt
      omega
    · simp only [hl, if_false]
      have := Submodule.finrank_mono hle
      omega

/-- No loss along a legal run (SCALE factors nonzero): the final row span is the token span. -/
theorem span_run (s : St K Reg C) (T : Finset Reg) (evs : List (Ev K Reg C))
    (hL : Legal z V s evs) (hN : ∀ e ∈ evs, NZ e) (hG : Good s T) (hS : Sp s = TS T)
    (hl : ¬ Loss s evs) : Sp (run s evs) = TS (tokRun T evs) := by
  induction evs generalizing s T with
  | nil => exact hS
  | cons e es ih =>
    simp only [Loss, not_or] at hl
    exact ih (step s e) (tokStep T e) hL.2 (fun e' he' => hN e' (List.mem_cons_of_mem _ he'))
      (good_step z V s T e hL.1 hG)
      (Sp_step_noloss z V s T e hL.1 (hN e List.mem_cons_self) hG hS hl.1) hl.2

/-- Rank bookkeeping along a legal run: any slack m is kept, and a loss adds one more unit. -/
theorem rank_run (s : St K Reg C) (T : Finset Reg) (evs : List (Ev K Reg C))
    (hL : Legal z V s evs) (hG : Good s T) (m : ℕ) (hm : finrank K (Sp s) + m ≤ T.card) :
    finrank K (Sp (run s evs)) + m ≤ (tokRun T evs).card ∧
      (Loss s evs → finrank K (Sp (run s evs)) + m + 1 ≤ (tokRun T evs).card) := by
  induction evs generalizing s T m with
  | nil => exact ⟨hm, fun h => h.elim⟩
  | cons e es ih =>
    simp only [run, tokRun]
    have hst := rank_step z V s T e hL.1 hG
    have hG' := good_step z V s T e hL.1 hG
    by_cases hl : Lossy s e
    · simp only [hl, if_true] at hst
      have := (ih (step s e) (tokStep T e) hL.2 hG' (m + 1) (by omega)).1
      exact ⟨le_trans (Nat.le_succ _) this, fun _ => this⟩
    · simp only [hl, if_false, add_zero] at hst
      have := ih (step s e) (tokStep T e) hL.2 hG' m (by omega)
      refine ⟨this.1, fun hlo => ?_⟩
      simp only [Loss, hl, false_or] at hlo
      exact this.2 hlo

/-- **Rank is lost exactly at lossy CLEAR/COPY.** For a legal run from a state whose rows span its
tokens (all SCALE factors nonzero), the final row span equals the final token span iff the run
contains no lossy event. -/
theorem full_rank_iff_noloss (s : St K Reg C) (T : Finset Reg) (evs : List (Ev K Reg C))
    (hL : Legal z V s evs) (hN : ∀ e ∈ evs, NZ e) (hG : Good s T) (hS : Sp s = TS T) :
    Sp (run s evs) = TS (tokRun T evs) ↔ ¬ Loss s evs := by
  refine ⟨fun h hl => ?_, span_run z V s T evs hL hN hG hS⟩
  have h0 : finrank K (Sp s) + 0 ≤ T.card := by
    rw [hS, finrank_TS]; simp
  have := (rank_run z V s T evs hL hG 0 h0).2 hl
  have e := congrArg (fun S : Submodule K (Reg → K) => finrank K S) h
  rw [e, finrank_TS] at this
  omega

/-- Cancellation: two subspaces of `U` with the same sum against a complement-to-`U` piece agree. -/
theorem eq_of_sup_eq {M : Type*} [AddCommGroup M] [Module K M] (A B N U : Submodule K M)
    (hA : A ≤ U) (hB : B ≤ U) (hUN : U ⊓ N = ⊥) (h : A ⊔ N = B ⊔ N) : A = B := by
  have key : ∀ A B : Submodule K M, A ≤ U → B ≤ U → A ⊔ N = B ⊔ N → A ≤ B := by
    intro A B hA hB h x hx
    have : x ∈ B ⊔ N := h ▸ mem_sup_left hx
    obtain ⟨b, hb, n, hn, rfl⟩ := mem_sup.1 this
    have hnU : n ∈ U := by
      have := sub_mem (hA hx) (hB hb); simpa using this
    have : n ∈ U ⊓ N := ⟨hnU, hn⟩
    rw [hUN, mem_bot] at this; subst this; simpa using hb
  exact le_antisymm (key A B hA hB h) (key B A hB hA h.symm)

theorem span_range_split (f : Reg → Reg → K) (G1 : Finset Reg) :
    span K (Set.range f) = span K (f '' (G1 : Set Reg)) ⊔ span K (f '' (G1 : Set Reg)ᶜ) := by
  rw [← span_union, ← Set.image_union, Set.union_compl_self, Set.image_univ]

theorem range_restrict (f : Reg → Reg → K) (G1 : Finset Reg) :
    Set.range (Matrix.of fun g : G1 => f g).row = f '' (G1 : Set Reg) := by
  ext x; constructor
  · rintro ⟨g, rfl⟩; exact ⟨g, g.2, rfl⟩
  · rintro ⟨g, hg, rfl⟩; exact ⟨⟨g, hg⟩, rfl⟩

/-- The V mix of a run: an invertible `C` over the registers `G1` that end at V with
`C · X[G1] = Rf[G1]`, where `X` are the end rows of the run (all V-hub ops deleted). -/
def VMix (X Rf : Reg → Reg → K) (G1 : Finset Reg) : Prop :=
  VMixM (Matrix.of fun g : G1 => X g) (Matrix.of fun g : G1 => Rf g)

/-- **RANK law (REBUILD-CORE, RESULT §7).** Run a legal word (V-hub ops deleted, SCALE factors
nonzero) from a state whose rows span its tokens. Let `G1` end at V; assume every other register
already ends at its target (`hNon`), and the target end state has full token rank (`hTgt`).
Let `U` be the "zero-W0" subspace (T_X + tokens): it contains the V targets (`hRU`) and meets the
span of the non-V targets only in 0 (`hUN`). Then a V mix exists iff
(i) no CLEAR/COPY loses rank and (ii) every V-ender row lies in `U`. -/
theorem rank_law (s : St K Reg C) (T : Finset Reg) (evs : List (Ev K Reg C))
    (hL : Legal z V s evs) (hN : ∀ e ∈ evs, NZ e) (hG : Good s T) (hS : Sp s = TS T)
    (Rf : Reg → Reg → K) (G1 : Finset Reg) (U : Submodule K (Reg → K))
    (hNon : ∀ r ∉ G1, (run s evs).row r = Rf r)
    (hTgt : span K (Set.range Rf) = TS (tokRun T evs))
    (hRU : ∀ g ∈ G1, Rf g ∈ U)
    (hUN : U ⊓ span K (Rf '' (G1 : Set Reg)ᶜ) = ⊥) :
    VMix (run s evs).row Rf G1 ↔ ¬ Loss s evs ∧ ∀ g ∈ G1, (run s evs).row g ∈ U := by
  set X := (run s evs).row with hXdef
  have hNim : X '' (G1 : Set Reg)ᶜ = Rf '' (G1 : Set Reg)ᶜ :=
    Set.image_congr (fun r hr => hNon r (by simpa using hr))
  have hBU : span K (Rf '' (G1 : Set Reg)) ≤ U :=
    span_le.2 (by rintro _ ⟨g, hg, rfl⟩; exact hRU g hg)
  unfold VMix
  rw [vmixM_iff_span, range_restrict, range_restrict]
  constructor
  · intro hAB
    have hfull : Sp (run s evs) = TS (tokRun T evs) := by
      rw [← hTgt, Sp, ← hXdef, span_range_split X G1, span_range_split Rf G1, hAB, hNim]
    refine ⟨(full_rank_iff_noloss z V s T evs hL hN hG hS).1 hfull, fun g hg => ?_⟩
    exact hBU (hAB ▸ subset_span ⟨g, hg, rfl⟩)
  · rintro ⟨hl, hU⟩
    have hfull := span_run z V s T evs hL hN hG hS hl
    have hsum : span K (X '' (G1 : Set Reg)) ⊔ span K (Rf '' (G1 : Set Reg)ᶜ) =
        span K (Rf '' (G1 : Set Reg)) ⊔ span K (Rf '' (G1 : Set Reg)ᶜ) := by
      rw [← hNim, ← span_range_split X G1, hNim, ← span_range_split Rf G1, hTgt]; exact hfull
    exact eq_of_sup_eq _ _ _ U (span_le.2 (by rintro _ ⟨g, hg, rfl⟩; exact hU g hg)) hBU hUN hsum

/-- ADD and SCALE (nonzero) are invertible ops: an inverse op restores the state exactly. -/
theorem add_inverse (s : St K Reg C) (i j : Reg) (a : K) (c : C) (hij : i ≠ j) :
    step (step s (.add i j a c)) (.add i j (-a) c) = s := by
  obtain ⟨row, loc⟩ := s
  simp only [step, St.mk.injEq, and_true]
  funext r; by_cases hr : r = i
  · subst hr; simp [Function.update_of_ne (Ne.symm hij)]
  · simp [Function.update_of_ne hr]

theorem scale_inverse (s : St K Reg C) (i : Reg) (u : K) (c : C) (hu : u ≠ 0) :
    step (step s (.scale i u c)) (.scale i u⁻¹ c) = s := by
  obtain ⟨row, loc⟩ := s
  simp only [step, St.mk.injEq, and_true]
  funext r; by_cases hr : r = i
  · subst hr; simp [smul_smul, inv_mul_cancel₀ hu]
  · simp [Function.update_of_ne hr]

/-- The canonical start: present registers carry their own coordinate, absent ones 0. -/
def start (l : Reg → Option C) : St K Reg C :=
  ⟨fun r => if l r = none then 0 else Pi.single r 1, l⟩

def startTok (l : Reg → Option C) : Finset Reg := Finset.univ.filter fun r => l r ≠ none

theorem start_good (l : Reg → Option C) : Good (start (K := K) l) (startTok l) :=
  ⟨fun r hr => by simp only [start] at hr ⊢; simp [hr], fun r hr => by simpa [start, startTok] using hr⟩

theorem start_span (l : Reg → Option C) : Sp (start (K := K) l) = TS (startTok l) := by
  apply le_antisymm
  · refine span_le.2 ?_
    rintro _ ⟨r, rfl⟩
    by_cases hr : l r = none
    · simp [start, hr]
    · simp only [start, hr, if_false]
      exact subset_span ⟨r, by simpa [startTok] using hr, rfl⟩
  · refine span_le.2 ?_
    rintro _ ⟨r, hr, rfl⟩
    have hr' : l r ≠ none := by simpa [startTok] using hr
    exact subset_span ⟨r, by simp [start, hr']⟩

/-- **Finding: COPY is not invertible either.** The prose lists CLEAR as the only rank-losing op;
in the op model with COPY (i := j's row), COPY onto a row outside the others' span loses rank. -/
theorem copy_lossy_example :
    Lossy (start (K := ℚ) (C := Unit) (fun _ : Fin 2 => some ())) (.copy 0 1 ()) := by
  refine ⟨by decide, fun h => ?_⟩
  have himg : (start (K := ℚ) (C := Unit) (fun _ : Fin 2 => some ())).row '' {r | r ≠ 0} =
      {Pi.single 1 1} := by
    ext x; simp only [Set.mem_image, Set.mem_ofPred_eq, Set.mem_singleton_iff, start]
    constructor
    · rintro ⟨r, hr, rfl⟩
      have : r = 1 := by fin_cases r <;> simp_all
      subst this; simp
    · rintro rfl; exact ⟨1, by decide, by simp⟩
  rw [Oth, himg, mem_span_singleton] at h
  obtain ⟨a, ha⟩ := h
  have := congrFun ha 0
  simp [start] at this

end Run

end RankLaw

#print axioms RankLaw.rank_law
#print axioms RankLaw.full_rank_iff_noloss
#print axioms RankLaw.vmixM_iff_span
#print axioms RankLaw.vmixM_fill
#print axioms RankLaw.vmix_ops
#print axioms RankLaw.vmixM_unique
#print axioms RankLaw.vmixM_indep
#print axioms RankLaw.copy_lossy_example
#print axioms RankLaw.add_inverse
#print axioms RankLaw.scale_inverse
#print axioms RankLaw.start_span
