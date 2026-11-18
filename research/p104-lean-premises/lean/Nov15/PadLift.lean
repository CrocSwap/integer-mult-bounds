/-
SPECBREAK R64 PAD-LIFT .
Source: internal notes, AUDIT64, R66/RESULT66.md.  See PadLift.md.
-/
import Nov15.SpecRankP
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.Diagonal
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Tactic.Ring
import Mathlib.FieldTheory.Finite.Basic

open Matrix Module

attribute [local instance] Nat.fact_prime_two

set_option linter.unusedSectionVars false

namespace PadLift

variable {K : Type*} [Field K] {α β : Type*} [Fintype α] [DecidableEq α] [Fintype β] [DecidableEq β]

/-- `g = diag(g', -I_pad)`. -/
def padG (g' : Matrix α α K) : Matrix (α ⊕ β) (α ⊕ β) K := fromBlocks g' 0 0 (-1)

/-- rank of a block-diagonal matrix. -/
theorem rank_blockdiag (A : Matrix α α K) (D : Matrix β β K) :
    (fromBlocks A 0 0 D).rank = A.rank + D.rank := by
  classical
  let e := LinearEquiv.sumArrowLequivProdArrow α β K K
  have hf : Matrix.toLin' (fromBlocks A 0 0 D) =
      e.symm.toLinearMap ∘ₗ ((LinearMap.prodMap (Matrix.toLin' A) (Matrix.toLin' D)) ∘ₗ e.toLinearMap) := by
    refine LinearMap.ext fun x => ?_
    obtain ⟨x1, x2, rfl⟩ : ∃ x1 x2, x = Sum.elim x1 x2 := ⟨_, _, (Sum.elim_comp_inl_inr x).symm⟩
    have h1 : e (Sum.elim x1 x2) = (x1, x2) := rfl
    simp only [Matrix.toLin'_apply, Matrix.fromBlocks_mulVec, LinearMap.comp_apply,
      LinearEquiv.coe_coe, h1, LinearMap.prodMap_apply, zero_mulVec, add_zero, zero_add]
    apply e.injective
    rw [LinearEquiv.apply_symm_apply]
    rfl
  have hrange : LinearMap.range (Matrix.toLin' (fromBlocks A 0 0 D)) =
      Submodule.map e.symm.toLinearMap
        (LinearMap.range (LinearMap.prodMap (Matrix.toLin' A) (Matrix.toLin' D))) := by
    rw [hf, LinearMap.range_comp,
      LinearMap.range_comp_of_range_eq_top _ (LinearEquiv.range e)]
  have hprod : ∀ (p : Submodule K (α → K)) (q : Submodule K (β → K)),
      finrank K (p.prod q) = finrank K p + finrank K q := fun p q => by
    have hinj : Function.Injective (LinearMap.prodMap p.subtype q.subtype) :=
      Function.Injective.prodMap p.injective_subtype q.injective_subtype
    have : LinearMap.range (p.subtype.prodMap q.subtype) = p.prod q := by
      rw [LinearMap.range_prodMap, Submodule.range_subtype, Submodule.range_subtype]
    rw [← this, LinearMap.finrank_range_of_inj hinj, Module.finrank_prod]
  change finrank K (LinearMap.range (Matrix.toLin' (fromBlocks A 0 0 D))) =
    finrank K (LinearMap.range (Matrix.toLin' A)) + finrank K (LinearMap.range (Matrix.toLin' D))
  rw [hrange, LinearEquiv.finrank_map_eq, LinearMap.range_prodMap, hprod]

/-- **(1) PAD-LIFT, rank.**  char ≠ 2: `rank(I - diag(g', -I_pad)) = rank(I - g') + |pad|`. -/
theorem pad_rank (h2 : (2 : K) ≠ 0) (g' : Matrix α α K) :
    (1 - padG (β := β) g').rank = (1 - g').rank + Fintype.card β := by
  classical
  have h : (1 : Matrix (α ⊕ β) (α ⊕ β) K) - padG g' =
      fromBlocks (1 - g') 0 0 (Matrix.diagonal fun _ : β => (2 : K)) := by
    ext i j
    rcases i with i | i <;> rcases j with j | j <;>
      simp [padG, Matrix.one_apply, Matrix.diagonal_apply] <;> (try split_ifs) <;> (try ring)
  rw [h, rank_blockdiag, Matrix.rank_diagonal]
  congr 1
  simp [h2]

/-- **(2) PAD-LIFT, involution** (any characteristic):
`diag(g', -I_pad)² = I ⇔ g'² = I`. -/
theorem pad_sq (g' : Matrix α α K) : padG (β := β) g' * padG g' = 1 ↔ g' * g' = 1 := by
  have h : padG (β := β) g' * padG g' = fromBlocks (g' * g') 0 0 1 := by
    simp [padG, Matrix.fromBlocks_multiply]
  rw [h, ← Matrix.fromBlocks_one, Matrix.fromBlocks_inj]
  simp

/-- **(3) PAD-LIFT, lifting of a kill.**  A kill of the form
"`rank(I - g') ≥ r`, with equality ⇒ `g'² = I`" lifts to
"`rank(I - g) ≥ r + |pad|`, with equality ⇒ `g² = I`".  (char ≠ 2.) -/
theorem lift_kill (h2 : (2 : K) ≠ 0) (g' : Matrix α α K) (r : ℕ)
    (hge : r ≤ (1 - g').rank) (heq : (1 - g').rank = r → g' * g' = 1) :
    r + Fintype.card β ≤ (1 - padG (β := β) g').rank ∧
      ((1 - padG (β := β) g').rank = r + Fintype.card β → padG (β := β) g' * padG g' = 1) := by
  rw [pad_rank h2]
  refine ⟨by omega, fun h => (pad_sq g').2 (heq (by omega))⟩

/-- Budget form: a rank budget `U` (rank(I - g) ≤ U) for the padded system. -/
theorem lift_budget (h2 : (2 : K) ≠ 0) (g' : Matrix α α K) (r : ℕ)
    (hge : r ≤ (1 - g').rank) (heq : (1 - g').rank = r → g' * g' = 1) (U : ℕ)
    (hU : (1 - padG (β := β) g').rank ≤ U) :
    r + Fintype.card β ≤ U ∧
      (U = r + Fintype.card β → padG (β := β) g' * padG g' = 1) := by
  obtain ⟨h1, h3⟩ := lift_kill (β := β) h2 g' r hge heq
  refine ⟨le_trans h1 hU, fun hUe => h3 (le_antisymm (hUe ▸ hU) h1)⟩

/-! ### The realisation level: dark pads give block-diagonal `J`, `D`, `g = D J⁻¹`. -/

/-- `J = diag(J', I_pad)`. -/
def lift1 (M : Matrix α α K) : Matrix (α ⊕ β) (α ⊕ β) K := fromBlocks M 0 0 1

theorem lift1_mul (M N : Matrix α α K) : lift1 (β := β) (M * N) = lift1 M * lift1 N := by
  simp [lift1, Matrix.fromBlocks_multiply]

theorem lift1_one : lift1 (β := β) (1 : Matrix α α K) = 1 := by
  simp [lift1]

/-- A job `1 - x yᵀ` with `x, y` vanishing on the pad registers is `diag(1 - x' y'ᵀ, I_pad)`. -/
theorem job_dark (x y : α → K) :
    (1 : Matrix (α ⊕ β) (α ⊕ β) K) - Matrix.vecMulVec (Sum.elim x 0) (Sum.elim y 0) =
      lift1 (1 - Matrix.vecMulVec x y) := by
  ext i j
  rcases i with i | i <;> rcases j with j | j <;>
    simp [lift1, Matrix.one_apply, Matrix.vecMulVec_apply]

/-- A product of dark jobs is `diag(J', I_pad)`. -/
theorem jobs_dark (L : List ((α → K) × (α → K))) :
    (L.map fun p => (1 : Matrix (α ⊕ β) (α ⊕ β) K) -
        Matrix.vecMulVec (Sum.elim p.1 0) (Sum.elim p.2 0)).prod =
      lift1 (L.map fun p => (1 : Matrix α α K) - Matrix.vecMulVec p.1 p.2).prod := by
  induction L with
  | nil => simp [lift1_one]
  | cons p L ih =>
    rw [List.map_cons, List.prod_cons, List.map_cons, List.prod_cons, job_dark, ih, lift1_mul]

/-- `g = D J⁻¹` with `D = diag(D', -I)`, `J = diag(J', I)`: `g = diag(D' J'⁻¹, -I)`. -/
theorem g_blockdiag (D' J' : Matrix α α K) (hJ : IsUnit J'.det) :
    fromBlocks D' 0 0 (-1 : Matrix β β K) * (lift1 (β := β) J')⁻¹ = padG (D' * J'⁻¹) := by
  have hinv : (lift1 (β := β) J')⁻¹ = lift1 J'⁻¹ := by
    apply Matrix.inv_eq_right_inv
    rw [← lift1_mul, Matrix.mul_nonsing_inv _ hJ, lift1_one]
  rw [hinv]
  simp [lift1, padG, Matrix.fromBlocks_multiply]

/-- Char 2 counterexample: `+2k` in (1) needs `char ≠ 2` (here `-I = I`, so the pad is invisible). -/
theorem pad_rank_char2_fails :
    ∃ g' : Matrix Unit Unit (ZMod 2),
      (1 - padG (β := Unit) g').rank ≠ (1 - g').rank + Fintype.card Unit := by
  refine ⟨1, ?_⟩
  have hneg : (-1 : Matrix Unit Unit (ZMod 2)) = 1 := by
    ext i j; simp
  have h : (1 : Matrix (Unit ⊕ Unit) (Unit ⊕ Unit) (ZMod 2)) - padG (β := Unit) 1 = 0 := by
    rw [padG, hneg, Matrix.fromBlocks_one, sub_self]
  rw [h]; simp

/-! ### Corollary: `rank_ge` is dimension-free in `S`
(RB4 item 1 with `S` of arbitrary dimension `m`; the padded case is `m = 2k + 2`.) -/
section Free
open SpecRankP

/-- `Δ = +1` on `e₁` and ancillas, `-1` on `m` S-coordinates. -/
def DlM (K : Type*) [Field K] (m : ℕ) (ι : Type*) [DecidableEq ι] :
    Matrix (Unit ⊕ Fin m ⊕ ι) (Unit ⊕ Fin m ⊕ ι) K :=
  Matrix.diagonal (Sum.elim (fun _ => 1) (Sum.elim (fun _ => -1) (fun _ => 1)))

theorem rank_ge_dim {ι : Type*} [Fintype ι] [DecidableEq ι] (m : ℕ)
    (h2 : (2 : K) ≠ 0) (P : Matrix (Unit ⊕ Fin m ⊕ ι) (Unit ⊕ Fin m ⊕ ι) K)
    (V : Submodule K (Unit ⊕ Fin m ⊕ ι → K)) (hV : finrank K V ≤ 2)
    (he1 : (Pi.single (Sum.inl ()) 1 : Unit ⊕ Fin m ⊕ ι → K) ∈ V)
    (hP : ∀ w, P *ᵥ w - w ∈ V) (hdet : P.det = 1) :
    m ≤ (DlM K m ι - P).rank := by
  let S : Submodule K (Unit ⊕ Fin m ⊕ ι → K) :=
    Submodule.span K (Set.range fun i : Fin m => (Pi.single (Sum.inr (Sum.inl i)) 1 : Unit ⊕ Fin m ⊕ ι → K))
  have hli : LinearIndependent K (fun i : Fin m => (Pi.single (Sum.inr (Sum.inl i)) 1 : Unit ⊕ Fin m ⊕ ι → K)) := by
    have := (Pi.basisFun K (Unit ⊕ Fin m ⊕ ι)).linearIndependent
    have h := this.comp (fun i : Fin m => (Sum.inr (Sum.inl i) : Unit ⊕ Fin m ⊕ ι))
      (fun a b h => by simpa using h)
    convert h using 1
    funext i
    simp [Pi.basisFun_apply]
  have hS : finrank K S = m := by
    simpa using finrank_span_eq_card hli
  have hΔS : ∀ s ∈ S, Matrix.toLin' (DlM K m ι) s = -s := by
    intro s hs
    refine Submodule.span_induction ?_ ?_ ?_ ?_ hs
    · rintro _ ⟨i, rfl⟩
      ext j
      simp [DlM, Matrix.toLin'_apply, Matrix.mulVec_diagonal, Pi.single_apply]
      aesop
    · simp
    · intro x y _ _ hx hy; rw [map_add, hx, hy]; abel
    · intro a x _ hx; rw [map_smul, hx]; simp
  have hΔe : Matrix.toLin' (DlM K m ι) (Pi.single (Sum.inl ()) 1) = Pi.single (Sum.inl ()) 1 := by
    ext j
    simp only [DlM, Matrix.toLin'_apply, Matrix.mulVec_diagonal, Pi.single_apply]
    split_ifs with h <;> simp [h]
  have heS : (Pi.single (Sum.inl ()) 1 : Unit ⊕ Fin m ⊕ ι → K) ∉ S := by
    intro hm
    have hmem : ∀ x ∈ S, x (Sum.inl ()) = 0 := by
      intro x hx
      refine Submodule.span_induction ?_ ?_ ?_ ?_ hx
      · rintro _ ⟨i, rfl⟩; simp [Pi.single_apply]
      · simp
      · intro x y _ _ hx hy; simp [hx, hy]
      · intro a x _ hx; simp [hx]
    have := hmem _ hm
    simp at this
  have := rank_ge h2 S V (Matrix.toLin' (DlM K m ι)) (Matrix.toLin' P) hΔS _ hΔe heS hV he1
    (fun w => by simpa [Matrix.toLin'_apply] using hP w) (by rw [LinearMap.det_toLin']; exact hdet)
  rw [hS] at this
  have e : (DlM K m ι - P).rank = finrank K (LinearMap.range (Matrix.toLin' (DlM K m ι) - Matrix.toLin' P)) := by
    rw [← map_sub]; rfl
  rw [e]; exact this

/-- The padded case: `dim S = 2k + 2` gives `rank(Δ - P) ≥ 2k + 2`; at `k = 1` this is the `4` of
`SpecRankP.rank_ge_four` (`m = 4`), at `k = 0`, `m = 2`. -/
theorem rank_ge_pad {ι : Type*} [Fintype ι] [DecidableEq ι] (k : ℕ)
    (h2 : (2 : K) ≠ 0) (P : Matrix (Unit ⊕ Fin (2 * k + 2) ⊕ ι) (Unit ⊕ Fin (2 * k + 2) ⊕ ι) K)
    (V : Submodule K (Unit ⊕ Fin (2 * k + 2) ⊕ ι → K)) (hV : finrank K V ≤ 2)
    (he1 : (Pi.single (Sum.inl ()) 1 : Unit ⊕ Fin (2 * k + 2) ⊕ ι → K) ∈ V)
    (hP : ∀ w, P *ᵥ w - w ∈ V) (hdet : P.det = 1) :
    2 * k + 2 ≤ (DlM K (2 * k + 2) ι - P).rank :=
  rank_ge_dim _ h2 P V hV he1 hP hdet

end Free

end PadLift

#print axioms PadLift.rank_blockdiag
#print axioms PadLift.pad_rank
#print axioms PadLift.pad_sq
#print axioms PadLift.lift_kill
#print axioms PadLift.lift_budget
#print axioms PadLift.jobs_dark
#print axioms PadLift.g_blockdiag
#print axioms PadLift.pad_rank_char2_fails
#print axioms PadLift.rank_ge_dim
#print axioms PadLift.rank_ge_pad
