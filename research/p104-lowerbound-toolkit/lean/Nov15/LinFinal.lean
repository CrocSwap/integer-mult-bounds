import Nov15.Doubling
import Nov15.LinCore
/-!
LINFINAL (lane LEANLINEAR).  LINEAR56 Theorem B, port-general, combined with the DOUBLING lemma:
for every half-integer LINEAR decoder whose row-pair matrix M = (α_j·p_k) is invertible on some n rows
(n = 2g) and whose labels carry no extra quadric (HInj),   C >= rho_A + rho_B >= 2 * C(n,2) = 2g(2g-1).
-/
open Matrix Finset

namespace LinFinal
open LinCore

variable {ι κ : Type*} [Fintype ι] [DecidableEq ι]
variable {n : ℕ}

/-- The structure of a (half-integer) linear decoder on n chosen rows e j:
  pattern Q_ts = 1 + B(c_t, c_s); parities of the row ports are linear functionals
  (a_j(t) = α_j·c_t on the w side, b_j(t) = (Bm p_j)·c_t on the v side). -/
structure LinSetup (Bm : Matrix (Fin n) (Fin n) F2) (c : ι → Fin n → F2) (Mz : ι → ι → ℤ)
    (J : Finset κ) (w v : κ → ι → ℤ) (e : Fin n → κ) (α p : Fin n → Fin n → F2) : Prop where
  pat : ∀ t s, (Mz t s : F2) = 1 + (Bm *ᵥ c t) ⬝ᵥ c s
  einj : Function.Injective e
  eJ : ∀ j, e j ∈ J
  parw : ∀ j t, Doubling.par (w (e j)) t = α j ⬝ᵥ c t
  parv : ∀ j t, Doubling.par (v (e j)) t = (Bm *ᵥ p j) ⬝ᵥ c t

variable {Bm : Matrix (Fin n) (Fin n) F2} {c : ι → Fin n → F2} {Mz : ι → ι → ℤ}
  {J : Finset κ} {w v : κ → ι → ℤ} {e : Fin n → κ} {α p : Fin n → Fin n → F2}

lemma Yhat_eq [DecidableEq κ] (S : LinSetup Bm c Mz J w v e α p) (y : ι → Fin n → F2) :
    Doubling.Tm Mz J w v (fun k t => ∑ j, if e j = k then y t j * (α j ⬝ᵥ c t) else 0)
        (fun k => Doubling.par (v k)) =
      Matrix.of fun t s : ι => (1 + (Bm *ᵥ c t) ⬝ᵥ c s) *
        ∑ j, (y t j * (α j ⬝ᵥ c t)) * ((Bm *ᵥ p j) ⬝ᵥ c s) := by
  ext t s
  simp only [Doubling.Tm, Matrix.sum_apply, Matrix.mul_diagonal, Matrix.diagonal_mul, Matrix.of_apply]
  have h1 : ∀ k ∈ J, (∑ j, if e j = k then y t j * (α j ⬝ᵥ c t) else 0) *
      Doubling.Qk Mz (w k) (v k) t s * Doubling.par (v k) s =
      ∑ j, if e j = k then (y t j * (α j ⬝ᵥ c t)) * Doubling.Qk Mz (w k) (v k) t s *
        Doubling.par (v k) s else 0 := by
    intro k _
    rw [Finset.sum_mul, Finset.sum_mul]
    refine Finset.sum_congr rfl fun j _ => ?_
    split_ifs <;> simp
  rw [Finset.sum_congr rfl h1, Finset.sum_comm]
  have h2 : ∀ j, (∑ k ∈ J, if e j = k then (y t j * (α j ⬝ᵥ c t)) * Doubling.Qk Mz (w k) (v k) t s *
        Doubling.par (v k) s else 0) =
      (y t j * (α j ⬝ᵥ c t)) * Doubling.Qk Mz (w (e j)) (v (e j)) t s * Doubling.par (v (e j)) s := by
    intro j
    rw [Finset.sum_ite_eq]; simp [S.eJ j]
  simp only [h2]
  rw [Finset.mul_sum]
  refine Finset.sum_congr rfl fun j _ => ?_
  have h3 := Doubling.par_Qk_par Mz (w (e j)) (v (e j)) t s
  rw [S.parw j t, S.parv j s, S.pat] at h3
  rw [S.parv j s]
  calc y t j * (α j ⬝ᵥ c t) * Doubling.Qk Mz (w (e j)) (v (e j)) t s * ((Bm *ᵥ p j) ⬝ᵥ c s)
      = y t j * ((α j ⬝ᵥ c t) * Doubling.Qk Mz (w (e j)) (v (e j)) t s * ((Bm *ᵥ p j) ⬝ᵥ c s)) := by ring
    _ = _ := by rw [h3]; ring

lemma sym_pat (hB : ∀ i j, Bm i j = Bm j i) (t s : ι) :
    (Bm *ᵥ c t) ⬝ᵥ c s = (Bm *ᵥ c s) ⬝ᵥ c t := by
  rw [hsd Bm hB, dotProduct_comm]

lemma Zhat_eq [DecidableEq κ] (hB : ∀ i j, Bm i j = Bm j i) (S : LinSetup Bm c Mz J w v e α p)
    (z : ι → Fin n → F2) :
    Doubling.Tm Mz J w v (fun k => Doubling.par (w k))
        (fun k s => ∑ j, if e j = k then z s j * ((Bm *ᵥ p j) ⬝ᵥ c s) else 0) =
      (Matrix.of fun s t : ι => (1 + (Bm *ᵥ c s) ⬝ᵥ c t) *
        ∑ j, (z s j * ((Bm *ᵥ p j) ⬝ᵥ c s)) * (α j ⬝ᵥ c t))ᵀ := by
  ext t s
  simp only [Doubling.Tm, Matrix.sum_apply, Matrix.mul_diagonal, Matrix.diagonal_mul, Matrix.transpose_apply,
    Matrix.of_apply]
  have h1 : ∀ k ∈ J, Doubling.par (w k) t * Doubling.Qk Mz (w k) (v k) t s *
      (∑ j, if e j = k then z s j * ((Bm *ᵥ p j) ⬝ᵥ c s) else 0) =
      ∑ j, if e j = k then Doubling.par (w k) t * Doubling.Qk Mz (w k) (v k) t s *
        (z s j * ((Bm *ᵥ p j) ⬝ᵥ c s)) else 0 := by
    intro k _
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl fun j _ => ?_
    split_ifs <;> simp
  rw [Finset.sum_congr rfl h1, Finset.sum_comm]
  have h2 : ∀ j, (∑ k ∈ J, if e j = k then Doubling.par (w k) t * Doubling.Qk Mz (w k) (v k) t s *
        (z s j * ((Bm *ᵥ p j) ⬝ᵥ c s)) else 0) =
      Doubling.par (w (e j)) t * Doubling.Qk Mz (w (e j)) (v (e j)) t s *
        (z s j * ((Bm *ᵥ p j) ⬝ᵥ c s)) := by
    intro j
    rw [Finset.sum_ite_eq]; simp [S.eJ j]
  simp only [h2]
  rw [Finset.mul_sum, ← sym_pat hB t s]
  refine Finset.sum_congr rfl fun j _ => ?_
  have h3 := Doubling.par_Qk_par Mz (w (e j)) (v (e j)) t s
  rw [S.parw j t, S.parv j s, S.pat] at h3
  rw [S.parw j t]
  calc α j ⬝ᵥ c t * Doubling.Qk Mz (w (e j)) (v (e j)) t s * (z s j * ((Bm *ᵥ p j) ⬝ᵥ c s))
      = z s j * ((α j ⬝ᵥ c t) * Doubling.Qk Mz (w (e j)) (v (e j)) t s * ((Bm *ᵥ p j) ⬝ᵥ c s)) := by ring
    _ = _ := by rw [h3]; ring

/-- THEOREM B (abstract, port-general), combined with the doubling lemma:
 C >= rho_A + rho_B >= 2 * C(n,2) for linear half-integer decoders. -/
theorem linear_cost_ge [DecidableEq κ]
    (h01 : ∀ t s, Mz t s = 0 ∨ Mz t s = 1) (hd : ∀ t, Mz t t = 1)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0)
    (hB : ∀ i j, Bm i j = Bm j i) (hBu : IsUnit Bm.det) (hInj : HInj c)
    (hcard : Fintype.card (Eix n) ≤ Fintype.card ι)
    (S : LinSetup Bm c Mz J w v e α p)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det) :
    2 * Fintype.card (Eix n) ≤ ∑ k ∈ J, (Doubling.Qk Mz (w k) (v k)).rank := by
  classical
  -- B side
  obtain ⟨y, hy⟩ := rho_rank_unit Bm α p c hB hBu hMu hInj hcard
  -- Z side: swapped roles
  set q : Fin n → Fin n → F2 := fun k => Bm⁻¹ *ᵥ α k with hq
  have hBq : ∀ k, Bm *ᵥ q k = α k := by
    intro k; simp [hq, Matrix.mulVec_mulVec, Matrix.mul_nonsing_inv _ hBu]
  have hM' : (Matrix.of fun j k => (fun j => Bm *ᵥ p j) j ⬝ᵥ q k) =
      (Matrix.of fun j k => α j ⬝ᵥ p k)ᵀ := by
    ext j k
    simp only [Matrix.of_apply, Matrix.transpose_apply]
    rw [dotProduct_comm, ← hsd Bm hB, hBq, dotProduct_comm]
  have hdet' : IsUnit (Matrix.of fun j k => (fun j => Bm *ᵥ p j) j ⬝ᵥ q k).det := by
    rw [hM', Matrix.det_transpose]; exact hMu
  obtain ⟨z, hz⟩ := rho_rank_unit Bm (fun j => Bm *ᵥ p j) q c hB hBu hdet' hInj hcard
  have hmat : (Matrix.of fun s t : ι => (1 + (Bm *ᵥ c s) ⬝ᵥ c t) *
        ∑ j, (z s j * ((Bm *ᵥ p j) ⬝ᵥ c s)) * (α j ⬝ᵥ c t)) =
      (Matrix.of fun t s : ι => (1 + (Bm *ᵥ c t) ⬝ᵥ c s) *
        ∑ k, (z t k * ((fun j => Bm *ᵥ p j) k ⬝ᵥ c t)) * ((Bm *ᵥ q k) ⬝ᵥ c s)) := by
    refine Matrix.ext fun s t => ?_
    simp only [Matrix.of_apply]
    congr 1
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [hBq]
  have hz' : Fintype.card (Eix n) ≤
      (Matrix.of fun s t : ι => (1 + (Bm *ᵥ c s) ⬝ᵥ c t) *
        ∑ j, (z s j * ((Bm *ᵥ p j) ⬝ᵥ c s)) * (α j ⬝ᵥ c t)).rank := by
    rw [hmat]; exact hz
  have hd2 := Doubling.doubling Mz J w v h01 hdec
    (fun k t => ∑ j, if e j = k then y t j * (α j ⬝ᵥ c t) else 0)
    (fun k s => ∑ j, if e j = k then z s j * ((Bm *ᵥ p j) ⬝ᵥ c s) else 0)
  rw [Yhat_eq S y, Zhat_eq hB S z, Matrix.rank_transpose] at hd2
  omega

end LinFinal
