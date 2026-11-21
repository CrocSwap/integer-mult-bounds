import Nov15.LinFinal
/-!
LINTOY (lane LEANLINEAR).  Non-vacuity of LinFinal.linear_cost_ge: a small symplectic toy (g = 1, n = 2).
Labels = the 3 nonzero points of F2^2, B = [[0,1],[1,0]], pattern Q = I (1 + B(c_t,c_s) = [t = s]).
A 2-row half-integer linear decoder: w = [[1,0,1],[0,1,1]], v = [[2,1,1],[1,2,1]], decoder identity
sum_k w_k(t) v_k(s) Q(t,s) = 2 [t = s].  All hypotheses (HInj included) are discharged by `decide`.
-/
open Matrix Finset LinCore LinFinal

namespace LinToy

def c : Fin 3 → Fin 2 → F2 := ![![1, 0], ![0, 1], ![1, 1]]
def Bm : Matrix (Fin 2) (Fin 2) F2 := !![0, 1; 1, 0]
def Mz : Fin 3 → Fin 3 → ℤ := fun t s => if t = s then 1 else 0
def w : Fin 2 → Fin 3 → ℤ := ![![1, 0, 1], ![0, 1, 1]]
def v : Fin 2 → Fin 3 → ℤ := ![![2, 1, 1], ![1, 2, 1]]
def α : Fin 2 → Fin 2 → F2 := ![![1, 0], ![0, 1]]
def p : Fin 2 → Fin 2 → F2 := ![![1, 0], ![0, 1]]

lemma hdec : ∀ t s : Fin 3, ∑ k ∈ (Finset.univ : Finset (Fin 2)), w k t * v k s * Mz t s =
    if t = s then 2 else 0 := by decide
lemma h01 : ∀ t s : Fin 3, Mz t s = 0 ∨ Mz t s = 1 := by decide
lemma hd : ∀ t : Fin 3, Mz t t = 1 := by decide
lemma hB : ∀ i j : Fin 2, Bm i j = Bm j i := by
  intro i j; fin_cases i <;> fin_cases j <;> first | rfl | decide | simp [Bm]
lemma hBu : IsUnit Bm.det := Matrix.isUnit_det_of_left_inverse (A := Bm) (B := Bm) (by decide)
lemma hInj : HInj c := by unfold HInj; decide +kernel
lemma hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det := by
  have : (Matrix.of fun j k => α j ⬝ᵥ p k) = 1 := by decide
  rw [this]; simp
lemma hSet : LinSetup Bm c Mz (Finset.univ : Finset (Fin 2)) w v id α p where
  pat := by decide
  einj := Function.injective_id
  eJ := fun j => Finset.mem_univ j
  parw := by decide
  parv := by decide

theorem toy_cost : 2 * Fintype.card (Eix 2) ≤
    ∑ k ∈ (Finset.univ : Finset (Fin 2)), (Doubling.Qk Mz (w k) (v k)).rank :=
  linear_cost_ge h01 hd hdec hB hBu hInj (by decide) hSet hMu

/-- the bound is genuinely instantiated: card Eix 2 = 1, so the toy cost is >= 2. -/
theorem toy_cost2 : 2 ≤ ∑ k ∈ (Finset.univ : Finset (Fin 2)), (Doubling.Qk Mz (w k) (v k)).rank := by
  have := toy_cost
  have h : Fintype.card (Eix 2) = 1 := by decide
  omega

/-- tamper control: with a repeated label the labels carry an extra quadric (x1 x2), so HInj FAILS. -/
def c' : Fin 3 → Fin 2 → F2 := ![![1, 0], ![1, 0], ![0, 1]]
lemma toy_not_hinj : ¬ HInj c' := by unfold HInj; decide +kernel

end LinToy

#print axioms LinToy.toy_cost2
#print axioms LinToy.toy_not_hinj
#print axioms LinFinal.linear_cost_ge
#print axioms LinCore.key_zero
#print axioms LinCore.dim_le
#print axioms LinCore.hall_bound
#print axioms LinCore.rho_rank_unit
#print axioms LinRado.rado
#print axioms LinOrd.exists_ordering
#print axioms LinOrd.no_alt_upper
