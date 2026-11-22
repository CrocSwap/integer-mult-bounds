import TritMarginals

namespace TritMarginals

def axis {n : ℕ} (i j : Fin n) : F := if j = i then 1 else 0

/-- Normalize a nonzero pivot and clear all other entries with one invertible linear map. -/
def toAxis {n : ℕ} (i : Fin n) (a : V n) (h : a i ≠ 0) : V n ≃ₗ[F] V n where
  toFun x j := x j + (axis i j - a j)*(x i / a i)
  invFun x j := x j + (a j - axis i j)*x i
  left_inv x := by
    funext j
    change x j + (axis i j - a j)*(x i/a i) +
      (a j-axis i j)*(x i+(axis i i-a i)*(x i/a i)) = x j
    rw [show axis i i = 1 by simp [axis]]
    field_simp
    ring
  right_inv x := by
    funext j
    change x j + (a j - axis i j)*x i +
      (axis i j-a j)*((x i + (a i-axis i i)*x i)/a i) = x j
    rw [show axis i i = 1 by simp [axis]]
    field_simp
    ring
  map_add' x y := by
    funext j
    change (x j + y j) + (axis i j - a j) * ((x i + y i) / a i) =
      (x j + (axis i j - a j)*(x i/a i)) + (y j+(axis i j-a j)*(y i/a i))
    ring
  map_smul' c x := by
    funext j
    change c*x j+(axis i j-a j)*((c*x i)/a i) = c*(x j+(axis i j-a j)*(x i/a i))
    ring

theorem toAxis_self {n : ℕ} (i : Fin n) (a : V n) (h : a i ≠ 0) :
    toAxis i a h a = axis i := by
  funext j
  change a j + (axis i j-a j)*(a i / a i) = axis i j
  rw [div_self h]
  ring

/-- Reorder coordinates without changing the vector-space contract. -/
def permute {n : ℕ} (s : Equiv.Perm (Fin n)) : V n ≃ₗ[F] V n where
  toFun x j := x (s j)
  invFun x j := x (s.symm j)
  left_inv x := by funext j; exact congrArg x (s.apply_symm_apply j)
  right_inv x := by funext j; exact congrArg x (s.symm_apply_apply j)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem normalize {n : ℕ} (x : V (n+1)) (hx : x ≠ 0) :
    ∃ T : V (n+1) ≃ₗ[F] V (n+1), T x = axis 0 := by
  have existsPivot : ∃ i, x i ≠ 0 := by
    by_contra! none
    exact hx (funext none)
  obtain ⟨i, hi⟩ := existsPivot
  let S := permute (Equiv.swap 0 i)
  have hfirst : S x 0 ≠ 0 := by
    change x (Equiv.swap 0 i 0) ≠ 0
    simpa using hi
  exact ⟨S.trans (toAxis 0 (S x) hfirst), toAxis_self 0 (S x) hfirst⟩

/-- The group of invertible linear maps is transitive on the nonzero trit vectors. -/
theorem transitiveNonzero {n : ℕ} (x y : V (n+1)) (hx : x ≠ 0) (hy : y ≠ 0) :
    ∃ T : V (n+1) ≃ₗ[F] V (n+1), T x = y := by
  obtain ⟨A,hA⟩ := normalize x hx
  obtain ⟨B,hB⟩ := normalize y hy
  refine ⟨A.trans B.symm, ?_⟩
  change B.symm (A x) = y
  rw [hA, ← hB, B.symm_apply_apply]

#print axioms transitiveNonzero

end TritMarginals
