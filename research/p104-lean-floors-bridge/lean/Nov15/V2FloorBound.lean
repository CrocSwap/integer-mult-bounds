/-
V2FloorBound: V2-FLOOR on the real lattice of subspaces of F₂⁹ (lane LEAN-NEXT20, Nov 16). See V2FloorCert.md.

Pairs are given as data, exactly as pairs.txt: L_p = span of basis vectors (bit masks), U_p = common kernel of parity checks
(bit masks); the certificate y = num/2^30 is given per pair and level. `floor_F2` is the bound

    Σ_{p,k} num p k / 2^30 ≤ Σ_{e ∈ E} w_θ(dim e.1, dim e.2)

for every plan E (edges X < Y between subspaces of dims 1..8) realising every pair, ASSUMING the integer edge
inequality `IntFeasible` (what check.c verifies, in its unrelaxed form) and the level-range condition. The cost side
(T(a,b) ≤ 2^30·w(a,b), logs exact) is proved in V2FloorCost; weak duality in V2FloorCert.
-/
import Nov15.V2FloorCert
import Nov15.V2FloorCost
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Field.ZMod
import Mathlib.Algebra.BigOperators.Field

namespace V2Floor
open Finset Module

attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 1000000

abbrev Vec := Fin 9 → ZMod 2
abbrev Sub := Submodule (ZMod 2) Vec

/-- bit mask → vector of F₂⁹. -/
def vec (v : ℕ) : Vec := fun i => if v.testBit i then 1 else 0

/-- span of basis masks. -/
noncomputable def Lsub (B : List ℕ) : Sub := Submodule.span (ZMod 2) {x | x ∈ B.map vec}

/-- common kernel of parity-check masks. -/
noncomputable def Usub (H : List ℕ) : Sub :=
  LinearMap.ker (Matrix.of fun (i : Fin H.length) j => vec (H.get i) j).mulVecLin

noncomputable def fdim (X : Sub) : ℕ := finrank (ZMod 2) X

theorem fdim_mono : Monotone fdim := fun _ _ h => Submodule.finrank_mono h

theorem fdim_L_le (B : List ℕ) : fdim (Lsub B) ≤ B.length := by
  unfold fdim Lsub
  have h1 : {x | x ∈ B.map vec} = ((B.map vec).toFinset : Set Vec) := by ext; simp
  rw [h1]
  calc finrank (ZMod 2) (Submodule.span (ZMod 2) ((B.map vec).toFinset : Set Vec))
      ≤ (B.map vec).toFinset.card := finrank_span_finset_le_card _
    _ ≤ (B.map vec).length := List.toFinset_card_le _
    _ = B.length := List.length_map _

theorem fdim_U_ge (H : List ℕ) : 9 - H.length ≤ fdim (Usub H) := by
  unfold fdim Usub
  set f := (Matrix.of fun (i : Fin H.length) j => vec (H.get i) j).mulVecLin
  have h := LinearMap.finrank_range_add_finrank_ker (K := ZMod 2) (V := Vec) f
  have hr : finrank (ZMod 2) (LinearMap.range f) ≤ H.length := by
    have := Submodule.finrank_le (LinearMap.range f); simpa using this
  simp only [finrank_fin_fun] at h
  omega

/-- y = num / 2^30. -/
noncomputable def yv {P : Type*} (num : P → ℕ → ℕ) (p : P) (k : ℕ) : ℝ := (num p k : ℝ) / 2 ^ 30

/-- what check.c verifies (unrelaxed form): for every edge X < Y with dims in 1..8, the served integer weights are ≤ T. -/
def IntFeasible {P : Type*} [Fintype P] (L U : P → Sub) (num : P → ℕ → ℕ) (T : ℕ → ℕ → ℕ) : Prop :=
  ∀ X Y : Sub, X < Y → 1 ≤ fdim X → fdim Y ≤ 8 →
    ∑ p ∈ univ.filter (fun p => L p ≤ X ∧ Y ≤ U p), ∑ k ∈ Ico (fdim X) (fdim Y), num p k ≤ T (fdim X) (fdim Y)

/-- edge price used for plans: w_θ on dims 1..8 (the model's range), 0 elsewhere (no such edges in a plan). -/
noncomputable def wcut (θ : ℝ) (a b : ℕ) : ℝ := if 1 ≤ a ∧ b ≤ 8 then wt θ a b else 0

theorem floor_F2 {P : Type*} [Fintype P] (LB UH : P → List ℕ) (num : P → ℕ → ℕ) (θ : ℝ) (T : ℕ → ℕ → ℕ)
    (hT : ∀ a b, 1 ≤ a → a < b → b ≤ 8 → (T a b : ℝ) ≤ 2 ^ 30 * wt θ a b)
    (hLne : ∀ p, Lsub (LB p) ≠ ⊥) (hUne : ∀ p, Usub (UH p) ≠ ⊤)
    (hk : ∀ p k, num p k ≠ 0 → (LB p).length ≤ k ∧ k < 9 - (UH p).length)
    (hk9 : ∀ p k, 9 ≤ k → num p k = 0)
    (hfeas : IntFeasible (fun p => Lsub (LB p)) (fun p => Usub (UH p)) num T)
    (E : Finset (Sub × Sub)) (hE : ∀ e ∈ E, e.1 < e.2)
    (hreal : ∀ p, Reach E (Lsub (LB p)) (Usub (UH p))) :
    (∑ p, ∑ k ∈ range 9, (num p k : ℝ)) / 2 ^ 30 ≤ ∑ e ∈ E, wcut θ (fdim e.1) (fdim e.2) := by
  have hy : ∀ p k, 0 ≤ yv num p k := fun p k => by unfold yv; positivity
  -- real feasibility on every strict containment
  have hfeasR : ∀ X Y : Sub, X < Y →
      ∑ p ∈ univ.filter (fun p => Lsub (LB p) ≤ X ∧ Y ≤ Usub (UH p)), gain fdim (yv num) p X Y ≤
        wcut θ (fdim X) (fdim Y) := by
    intro X Y hXY
    by_cases hr : 1 ≤ fdim X ∧ fdim Y ≤ 8
    · have hi := hfeas X Y hXY hr.1 hr.2
      have hab : fdim X < fdim Y := Submodule.finrank_lt_finrank_of_lt hXY
      unfold wcut; rw [if_pos hr]
      have hcast : ∑ p ∈ univ.filter (fun p => Lsub (LB p) ≤ X ∧ Y ≤ Usub (UH p)), gain fdim (yv num) p X Y =
          ((∑ p ∈ univ.filter (fun p => Lsub (LB p) ≤ X ∧ Y ≤ Usub (UH p)),
            ∑ k ∈ Ico (fdim X) (fdim Y), num p k : ℕ) : ℝ) / 2 ^ 30 := by
        simp only [gain, yv, Nat.cast_sum, Finset.sum_div]
      rw [hcast, div_le_iff₀ (by positivity)]
      have := hT _ _ hr.1 hab hr.2
      have hi' : ((∑ p ∈ univ.filter (fun p => Lsub (LB p) ≤ X ∧ Y ≤ Usub (UH p)),
            ∑ k ∈ Ico (fdim X) (fdim Y), num p k : ℕ) : ℝ) ≤ (T (fdim X) (fdim Y) : ℝ) := by exact_mod_cast hi
      linarith
    · -- no pair is served: dim X = 0 forces X = ⊥, dim Y = 9 forces Y = ⊤
      have hempty : univ.filter (fun p => Lsub (LB p) ≤ X ∧ Y ≤ Usub (UH p)) = ∅ := by
        apply Finset.filter_false_of_mem
        intro p _ ⟨h1, h2⟩
        rcases not_and_or.mp hr with h | h
        · have h0 : fdim X = 0 := by omega
          have hX : X = ⊥ := Submodule.finrank_eq_zero.mp h0
          exact hLne p (le_bot_iff.mp (hX ▸ h1))
        · have h9 : fdim Y = 9 := by
            have := Submodule.finrank_le Y; simp only [finrank_fin_fun] at this; unfold fdim at h ⊢; omega
          have hY : Y = ⊤ := by
            apply Submodule.eq_top_of_finrank_eq; simpa [fdim] using h9
          exact hUne p (top_le_iff.mp (hY ▸ h2))
      rw [hempty, sum_empty]
      unfold wcut; rw [if_neg hr]
  have hwd := weak_duality fdim (yv num) (fun p => Lsub (LB p)) (fun p => Usub (UH p)) (wcut θ) fdim_mono hy
    hfeasR E hE hreal
  have hstep : ∀ p, ∑ k ∈ range 9, (num p k : ℝ) / 2 ^ 30 ≤ gain fdim (yv num) p (Lsub (LB p)) (Usub (UH p)) := by
    intro p
    have hsub : (range 9).filter (fun k => num p k ≠ 0) ⊆ Ico (fdim (Lsub (LB p))) (fdim (Usub (UH p))) := by
      intro k hk'
      simp only [mem_filter] at hk'
      obtain ⟨h1, h2⟩ := hk p k hk'.2
      have := fdim_L_le (LB p); have := fdim_U_ge (UH p)
      simp only [mem_Ico]; omega
    calc ∑ k ∈ range 9, (num p k : ℝ) / 2 ^ 30
        = ∑ k ∈ (range 9).filter (fun k => num p k ≠ 0), yv num p k := by
          rw [sum_filter]; refine sum_congr rfl fun k _ => ?_
          unfold yv; split_ifs with h
          · rfl
          · push_neg at h; simp [h]
      _ ≤ ∑ k ∈ Ico (fdim (Lsub (LB p))) (fdim (Usub (UH p))), yv num p k :=
          sum_le_sum_of_subset_of_nonneg hsub fun k _ _ => hy p k
      _ = gain fdim (yv num) p (Lsub (LB p)) (Usub (UH p)) := rfl
  calc (∑ p, ∑ k ∈ range 9, (num p k : ℝ)) / 2 ^ 30 = ∑ p, ∑ k ∈ range 9, (num p k : ℝ) / 2 ^ 30 := by
        rw [Finset.sum_div]; simp only [Finset.sum_div]
    _ ≤ ∑ p, gain fdim (yv num) p (Lsub (LB p)) (Usub (UH p)) := sum_le_sum fun p _ => hstep p
    _ ≤ _ := hwd

end V2Floor
