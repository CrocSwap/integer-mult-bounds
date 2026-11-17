/-
BEAUTY-NOV17B pinning fact [P] and multiplicity statement, lane LEAN-NEXT31, Nov 17.  See PrefixPin.md.
Self-contained (Mathlib only); relates to HubSettle.Valid in the .md.
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Dimension.Finite
import Mathlib.Data.Matrix.ColumnRowPartitioned

namespace PrefixPin
open Matrix Submodule Module

variable {K : Type*} [Field K]

section Pin
variable {R N G0 I : Type*} [Fintype R] [Fintype N] [Fintype G0] [Fintype I]
  [DecidableEq R] [DecidableEq N] [DecidableEq G0] [DecidableEq I]

/-- A fixed interior+V program is affine on the exit rows: `Final = A·Exit + B·Inj`
(`A` = effect on the exit rows, `Inj` = rows born later, fixed by the program).  Columns are `N ⊕ G0`. -/
def Final (A : Matrix R R K) (B : Matrix R I K) (Inj : Matrix I (N ⊕ G0) K)
    (Exit : Matrix R (N ⊕ G0) K) : Matrix R (N ⊕ G0) K := A * Exit + B * Inj

/-- **Pinning [P].** If `A_rest` is invertible, the exit rows (hence the W0 block `R0`) are determined
by the final rows: `Exit = A⁻¹ (Final - B Inj)`, so two exits with equal finals are equal. -/
theorem exit_unique (A : Matrix R R K) (hA : IsUnit A.det) (B : Matrix R I K)
    (Inj : Matrix I (N ⊕ G0) K) (E E' : Matrix R (N ⊕ G0) K)
    (h : Final A B Inj E = Final A B Inj E') : E = E' := by
  unfold Final at h
  have h2 : A * E = A * E' := add_right_cancel h
  have := congrArg (fun M => A⁻¹ * M) h2
  simpa [← Matrix.mul_assoc, Matrix.nonsing_inv_mul _ hA] using this

/-- Explicit formula `E = A⁻¹ (F - B Inj)`. -/
theorem exit_formula (A : Matrix R R K) (hA : IsUnit A.det) (B : Matrix R I K)
    (Inj : Matrix I (N ⊕ G0) K) (E : Matrix R (N ⊕ G0) K) :
    E = A⁻¹ * (Final A B Inj E - B * Inj) := by
  simp [Final, ← Matrix.mul_assoc, Matrix.nonsing_inv_mul _ hA]

/-- W0 block only: if the N-columns of the exits agree, equal finals force equal W0 blocks; indeed
the W0 block alone is pinned even when the N-block is allowed to differ, provided `A` is invertible
*and the programs' injected rows are fixed* — this is the statement in `exit_unique` restricted. -/
theorem w0_block_unique (A : Matrix R R K) (hA : IsUnit A.det) (B : Matrix R I K)
    (Inj : Matrix I (N ⊕ G0) K) (E E' : Matrix R (N ⊕ G0) K)
    (h : Final A B Inj E = Final A B Inj E') :
    E.submatrix id Sum.inr = E'.submatrix id Sum.inr := by
  rw [exit_unique A hA B Inj E E' h]

/-- The prefix `M` acts as `Exit0 = X0 * M` (rows of the G0 initial block mixed). If `X0` has a left
inverse (the loaded rows span G0), the prefix itself is pinned. -/
theorem prefix_unique (X0 : Matrix R G0 K) (L : Matrix G0 R K) (hL : L * X0 = 1)
    (M M' : Matrix G0 G0 K) (A : Matrix R R K) (hA : IsUnit A.det) (B : Matrix R I K)
    (Inj : Matrix I (N ⊕ G0) K) (Xn : Matrix R N K)
    (h : Final A B Inj (Matrix.fromCols Xn (X0 * M)) = Final A B Inj (Matrix.fromCols Xn (X0 * M'))) :
    M = M' := by
  have h1 := exit_unique A hA B Inj _ _ h
  have h2 : X0 * M = X0 * M' := by
    funext i j; have := congrFun (congrFun h1 i) (Sum.inr j); simpa using this
  have := congrArg (fun T => L * T) h2
  simpa [← Matrix.mul_assoc, hL] using this

/-- Contrast: with the V mix left free (`∃ T`, as in `HubSettle.prefix_gauge`) the exit is NOT unique:
scalar instance, final `f = 1`, exits `1` and `2` both reach it. -/
theorem free_mix_not_unique :
    ∃ r r' : ℚ, r ≠ r' ∧ (∃ T : ℚ, T * r = 1) ∧ (∃ T : ℚ, T * r' = 1) :=
  ⟨1, 2, by norm_num, ⟨1, by norm_num⟩, ⟨1/2, by norm_num⟩⟩

end Pin

section Mult
variable {R G0 : Type*} [Fintype R] [Fintype G0] [DecidableEq R] [DecidableEq G0]

open Classical in
/-- number of loaded (row, token) pairs = nonzero entries. -/
noncomputable def nnz (M : Matrix R G0 K) : ℕ :=
  (Finset.univ.filter (fun p : R × G0 => M p.1 p.2 ≠ 0)).card

/-- rank ≤ number of nonzero entries. -/
theorem rank_le_nnz (M : Matrix R G0 K) : M.rank ≤ nnz M := by
  classical
  rw [Matrix.rank_eq_finrank_span_row]
  set S : Finset R := Finset.univ.filter (fun i => M.row i ≠ 0) with hS
  have hsub : span K (Set.range M.row) ≤ span K (↑(S.image M.row) : Set (G0 → K)) := by
    apply span_le.2
    rintro _ ⟨i, rfl⟩
    by_cases hi : M.row i = 0
    · rw [hi]; exact zero_mem _
    · exact subset_span (by simp only [Finset.coe_image, Set.mem_image, Finset.mem_coe, hS, Finset.mem_filter, Finset.mem_univ, true_and]; exact ⟨i, hi, rfl⟩)
  refine (Submodule.finrank_mono hsub).trans ((finrank_span_finset_le_card _).trans
    ((Finset.card_image_le).trans ?_))
  unfold nnz
  refine (Finset.card_le_card (t := (Finset.univ.filter (fun p : R × G0 => M p.1 p.2 ≠ 0)).image Prod.fst)
    ?_).trans Finset.card_image_le
  intro i hi
  have : M.row i ≠ 0 := by simpa [hS] using hi
  have : ∃ j, M i j ≠ 0 := by
    by_contra hc; push_neg at hc; exact this (funext hc)
  obtain ⟨j, hj⟩ := this
  simp only [Finset.mem_image, Finset.mem_filter, Finset.mem_univ, true_and]
  exact ⟨(i, j), hj, rfl⟩

/-- **Multiplicity.** If the W0 block of the final rows has rank ≥ p (the terminal labels force p
independent W0 directions; p = 104 in the instance), and the exit rows are the pinned
`A⁻¹`-image, then the number of loaded (row, token) pairs is ≥ p. -/
theorem loaded_pairs_ge_ports (A : Matrix R R K) (F0 R0 : Matrix R G0 K) (hF : F0 = A * R0) (p : ℕ)
    (hp : p ≤ F0.rank) : p ≤ nnz R0 :=
  hp.trans ((hF ▸ Matrix.rank_mul_le_right A R0).trans (rank_le_nnz R0))

/-- ... and the count can exceed the rank (so exceed the number of ports): the all-ones `n × n`
matrix over ℚ has rank ≤ 1 but `n²` loaded pairs. -/
theorem nnz_can_exceed (n : ℕ) (hn : 2 ≤ n) :
    (Matrix.of fun (_ _ : Fin n) => (1 : ℚ)).rank ≤ 1 ∧
    nnz (Matrix.of fun (_ _ : Fin n) => (1 : ℚ)) = n * n ∧ 1 < n * n := by
  refine ⟨?_, ?_, by nlinarith⟩
  · have : (Matrix.of fun (_ _ : Fin n) => (1 : ℚ)) = Matrix.vecMulVec (fun _ => 1) (fun _ => 1) := by
      ext i j; simp [Matrix.vecMulVec]
    rw [this]; exact Matrix.rank_vecMulVec_le _ _
  · unfold nnz; simp

end Mult
#print axioms exit_unique
#print axioms prefix_unique
#print axioms loaded_pairs_ge_ports
#print axioms nnz_can_exceed
end PrefixPin
