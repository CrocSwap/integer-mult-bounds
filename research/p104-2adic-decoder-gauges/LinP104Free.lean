import Nov15.LinKbarFin
import Mathlib.Algebra.BigOperators.ModEq
/-!
LINP104FREE (lane LEANCB).  P104: C >= 56 for every Z4-linear half-integer decoder, WITHOUT the hypothesis hMu.
Z4-linear: w_k(t) = x_k . ct_t (mod 4), v_k(t) = y_k . ct_t (mod 4) for integer vectors x_k, y_k and ANY integer
lift ct of the F2 labels.  Proof: Kbar = sum_k xbar_k ybar_k^T satisfies the mod-2 law on B-orthogonal cells, so
Kbar in {0,B} (kern_B, kernel-certified); Kbar = 0 would give K = 2Z and (Gram of Z on the orthogonal dependent
quadruple 0,6,16,95) a contradiction; so Kbar = B, det (sum alpha_k p_k^T) = det B det Binv != 0 and Cauchy-Binet
(LinCB.cb_exists) yields 8 rows whose M = (alpha_j . p_k) is invertible.
-/
open Matrix Finset LinCore LinFinal

namespace P104
open P104Data

section
variable {κ : Type*}

lemma Q_one (t s : Fin 104) (h : (Bm *ᵥ lab t) ⬝ᵥ lab s = 0) : Qlab t s = 1 := by
  have h1 := Qlab_pat t s
  rw [h, add_zero] at h1
  rcases Qlab_01 t s with h0 | h0
  · rw [h0] at h1; simp at h1
  · exact h0

lemma par_eq (u : Fin 104 → ℤ) (t : Fin 104) : Doubling.par u t = (u t : F2) := by
  unfold Doubling.par
  exact_mod_cast ZMod.intCast_mod (u t) 2

lemma bil_sum_gen {R : Type*} [CommRing R] (J : Finset κ) (X Y : κ → Fin 8 → R) (u s : Fin 8 → R) :
    ∑ a : Fin 8, ∑ b : Fin 8, (∑ k ∈ J, X k a * Y k b) * (u a * s b) =
      ∑ k ∈ J, (∑ a, X k a * u a) * (∑ b, Y k b * s b) := by
  have L : ∑ a : Fin 8, ∑ b : Fin 8, (∑ k ∈ J, X k a * Y k b) * (u a * s b) =
      ∑ a : Fin 8, ∑ b : Fin 8, ∑ k ∈ J, X k a * Y k b * (u a * s b) := by
    simp only [Finset.sum_mul]
  have M : ∑ a : Fin 8, ∑ b : Fin 8, ∑ k ∈ J, X k a * Y k b * (u a * s b) =
      ∑ k ∈ J, ∑ a : Fin 8, ∑ b : Fin 8, X k a * Y k b * (u a * s b) := by
    calc _ = ∑ a : Fin 8, ∑ k ∈ J, ∑ b : Fin 8, X k a * Y k b * (u a * s b) :=
          Finset.sum_congr rfl fun a _ => Finset.sum_comm
      _ = _ := Finset.sum_comm
  have R : ∀ k ∈ J, (∑ a, X k a * u a) * (∑ b, Y k b * s b) =
      ∑ a : Fin 8, ∑ b : Fin 8, X k a * Y k b * (u a * s b) := by
    intro k _
    rw [Finset.sum_mul_sum]
    exact Finset.sum_congr rfl fun a _ => Finset.sum_congr rfl fun b _ => by ring
  rw [L, M]
  exact Finset.sum_congr rfl fun k hk => (R k hk).symm

lemma bil_sum (J : Finset κ) (X Y : κ → Fin 8 → F2) (u s : Fin 8 → F2) :
    u ⬝ᵥ ((Matrix.of fun a b => ∑ k ∈ J, X k a * Y k b) *ᵥ s) = ∑ k ∈ J, (X k ⬝ᵥ u) * (Y k ⬝ᵥ s) := by
  rw [dot_expand]
  simp only [Matrix.of_apply]
  exact bil_sum_gen J X Y u s

end

section Main
variable {κ : Type*} [DecidableEq κ]

structure Z4Lin (J : Finset κ) (w v : κ → Fin 104 → ℤ) (x y : κ → Fin 8 → ℤ)
    (ct : Fin 104 → Fin 8 → ℤ) : Prop where
  hct : ∀ t i, ((ct t i : ℤ) : F2) = lab t i
  hw : ∀ k ∈ J, ∀ t, w k t ≡ ∑ i, x k i * ct t i [ZMOD 4]
  hv : ∀ k ∈ J, ∀ t, v k t ≡ ∑ i, y k i * ct t i [ZMOD 4]

variable {J : Finset κ} {w v : κ → Fin 104 → ℤ} {x y : κ → Fin 8 → ℤ} {ct : Fin 104 → Fin 8 → ℤ}

lemma cast_lin_gen (Z : Z4Lin J w v x y ct) (u : κ → Fin 104 → ℤ) (z : κ → Fin 8 → ℤ)
    (h : ∀ k ∈ J, ∀ t, u k t ≡ ∑ i, z k i * ct t i [ZMOD 4]) (k : κ) (hk : k ∈ J) (t : Fin 104) :
    (u k t : F2) = (fun i => (z k i : F2)) ⬝ᵥ lab t := by
  have h2 : u k t ≡ ∑ i, z k i * ct t i [ZMOD 2] := Int.ModEq.of_dvd (by norm_num) (h k hk t)
  have h3 := (ZMod.intCast_eq_intCast_iff _ _ 2).2 (by exact_mod_cast h2)
  rw [h3]
  simp only [dotProduct]
  push_cast
  exact Finset.sum_congr rfl fun i _ => by rw [Z.hct]

def Kb (J : Finset κ) (x y : κ → Fin 8 → ℤ) : Matrix (Fin 8) (Fin 8) F2 :=
  Matrix.of fun a b => ∑ k ∈ J, (x k a : F2) * (y k b : F2)

lemma cellK (Z : Z4Lin J w v x y ct)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Qlab t s = if t = s then 2 else 0)
    (t s : Fin 104) (h : (Bm *ᵥ lab t) ⬝ᵥ lab s = 0) : lab t ⬝ᵥ (Kb J x y *ᵥ lab s) = 0 := by
  have hq := Q_one t s h
  have h1 := hdec t s
  rw [hq] at h1
  simp only [mul_one] at h1
  have h2 : ((∑ k ∈ J, w k t * v k s : ℤ) : F2) = 0 := by
    rw [h1]; split_ifs <;> decide
  push_cast at h2
  unfold Kb
  rw [bil_sum]
  rw [← h2]
  refine Finset.sum_congr rfl fun k hk => ?_
  rw [← cast_lin_gen Z w x Z.hw k hk t, ← cast_lin_gen Z v y Z.hv k hk s]

lemma Kb_ne_zero (Z : Z4Lin J w v x y ct)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Qlab t s = if t = s then 2 else 0) :
    Kb J x y 0 1 ≠ 0 := by
  intro h0
  have hK : ∀ a b, Kb J x y a b = 0 := by
    intro a b
    rw [kern_B _ (cellK Z hdec) a b, h0, mul_zero]
  have hev : ∀ a b : Fin 8, ∃ z : ℤ, ∑ k ∈ J, x k a * y k b = 2 * z := by
    intro a b
    have h1 := hK a b
    have h2 : (((∑ k ∈ J, x k a * y k b : ℤ)) : ZMod 2) = 0 := by
      simpa [Kb] using h1
    obtain ⟨z, hz⟩ := (ZMod.intCast_zmod_eq_zero_iff_dvd _ 2).1 h2
    exact ⟨z, by simpa using hz⟩
  choose Zz hZ using hev
  have cellG : ∀ t s : Fin 104, (Bm *ᵥ lab t) ⬝ᵥ lab s = 0 →
      lab t ⬝ᵥ ((Matrix.of fun a b => (Zz a b : F2)) *ᵥ lab s) = if t = s then 1 else 0 := by
    intro t s hts
    have hq := Q_one t s hts
    have h1 := hdec t s
    rw [hq] at h1
    simp only [mul_one] at h1
    set d : ℤ := if t = s then 1 else 0 with hd
    have h1' : ∑ k ∈ J, w k t * v k s = 2 * d := by
      rw [h1, hd]; split_ifs <;> simp
    set G : ℤ := ∑ a : Fin 8, ∑ b : Fin 8, Zz a b * ct t a * ct s b with hG
    have hE : ∑ k ∈ J, w k t * v k s ≡ 2 * G [ZMOD 4] := by
      have e1 : ∑ k ∈ J, w k t * v k s ≡
          ∑ k ∈ J, (∑ a, x k a * ct t a) * (∑ b, y k b * ct s b) [ZMOD 4] :=
        Int.ModEq.sum fun k hk => Int.ModEq.mul (Z.hw k hk t) (Z.hv k hk s)
      have e2 : ∑ k ∈ J, (∑ a, x k a * ct t a) * (∑ b, y k b * ct s b) = 2 * G := by
        rw [← bil_sum_gen J (fun k a => x k a) (fun k b => y k b) (ct t) (ct s)]
        rw [hG, Finset.mul_sum]
        refine Finset.sum_congr rfl fun a _ => ?_
        rw [Finset.mul_sum]
        refine Finset.sum_congr rfl fun b _ => ?_
        rw [hZ a b]; ring
      rw [e2] at e1
      exact e1
    have hdG : G % 2 = d % 2 := by
      rw [h1'] at hE
      unfold Int.ModEq at hE
      omega
    have hGd : (G : F2) = (d : F2) := by
      apply (ZMod.intCast_eq_intCast_iff' _ _ 2).2
      exact_mod_cast hdG
    have hGl : (G : F2) = lab t ⬝ᵥ ((Matrix.of fun a b => (Zz a b : F2)) *ᵥ lab s) := by
      rw [dot_expand, hG]
      push_cast
      refine Finset.sum_congr rfl fun a _ => Finset.sum_congr rfl fun b _ => ?_
      rw [Z.hct, Z.hct]
      simp only [Matrix.of_apply]
      ring
    rw [← hGl, hGd, hd]
    split_ifs <;> simp
  set Zb : Matrix (Fin 8) (Fin 8) F2 := Matrix.of fun a b => (Zz a b : F2) with hZb
  have e : lab 0 = lab 6 + lab 16 + lab 95 := by
    funext a
    have h := dep_sum a
    simp only [Pi.add_apply]
    generalize lab 0 a = p at *
    generalize lab 6 a = q at *
    generalize lab 16 a = r at *
    generalize lab 95 a = u at *
    revert p q r u
    decide
  have g00 : lab 0 ⬝ᵥ (Zb *ᵥ lab 0) = 1 := by
    rw [cellG 0 0 (Bm_alt 0)]; simp
  have g6 := cellG 6 0 dep_orth0
  have g16 := cellG 16 0 dep_orth1
  have g95 := cellG 95 0 dep_orth2
  have hs : lab 0 ⬝ᵥ (Zb *ᵥ lab 0) = lab 6 ⬝ᵥ (Zb *ᵥ lab 0) + lab 16 ⬝ᵥ (Zb *ᵥ lab 0) +
      lab 95 ⬝ᵥ (Zb *ᵥ lab 0) := by
    rw [← add_dotProduct, ← add_dotProduct, ← e]
  rw [g00, g6, g16, g95] at hs
  revert hs
  decide

lemma Kb_eq (Z : Z4Lin J w v x y ct)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Qlab t s = if t = s then 2 else 0) :
    ∀ i j, Kb J x y i j = Bm i j := by
  intro i j
  have h := kern_B _ (cellK Z hdec) i j
  have h1 : Kb J x y 0 1 = 1 := by
    have h0 := Kb_ne_zero Z hdec
    have key : ∀ p : F2, p ≠ 0 → p = 1 := by decide
    exact key _ h0
  rw [h, h1, mul_one]

/-- P104, every Z4-linear half-integer decoder (any number of rows): cost >= 56, no extra hypothesis. -/
theorem p104_linear_cost_ge_free (Z : Z4Lin J w v x y ct)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Qlab t s = if t = s then 2 else 0) :
    56 ≤ ∑ k ∈ J, (Doubling.Qk Qlab (w k) (v k)).rank := by
  classical
  have hBinv : Bm * Binv = 1 := mul_eq_one_comm.1 Binv_mul
  have hBinvu : IsUnit Binv.det := Matrix.isUnit_det_of_left_inverse hBinv
  let A : Matrix J (Fin 8) F2 := Matrix.of fun k a => (x k a : F2)
  let P : Matrix J (Fin 8) F2 := Matrix.of fun k a => (Binv *ᵥ (fun b => (y k b : F2))) a
  have hN : Aᵀ * P = Kb J x y * Binvᵀ := by
    ext a b
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.of_apply, Kb, A, P, mulVec, dotProduct]
    rw [Finset.sum_coe_sort J (fun k => (x k a : F2) * ∑ c, Binv b c * (y k c : F2))]
    simp only [Finset.mul_sum, Finset.sum_mul]
    rw [Finset.sum_comm]
    exact Finset.sum_congr rfl fun c _ => Finset.sum_congr rfl fun k _ => by ring
  have hKbBm : Kb J x y = Bm := Matrix.ext (Kb_eq Z hdec)
  have hdet : (Aᵀ * P).det ≠ 0 := by
    rw [hN, det_mul, det_transpose, hKbBm]
    exact mul_ne_zero Bm_unit.ne_zero hBinvu.ne_zero
  obtain ⟨f, hf, hfa, hfp⟩ := LinCB.cb_exists A P hdet
  have hM : (Matrix.of fun j k : Fin 8 => ((fun a => (x (f j) a : F2)) ⬝ᵥ
      (Binv *ᵥ (fun b => (y (f k) b : F2))))) = (A.submatrix f id) * (P.submatrix f id)ᵀ := by
    ext j k
    simp [Matrix.mul_apply, dotProduct, A, P]
  have hMu : IsUnit (Matrix.of fun j k : Fin 8 => ((fun a => (x (f j) a : F2)) ⬝ᵥ
      (Binv *ᵥ (fun b => (y (f k) b : F2))))).det := by
    rw [hM, det_mul, det_transpose]
    exact isUnit_iff_ne_zero.2 (mul_ne_zero hfa hfp)
  exact p104_linear_cost_ge J w v (fun j => (f j : κ))
    (fun j a => (x (f j) a : F2)) (fun j => Binv *ᵥ (fun b => (y (f j) b : F2))) hdec
    (fun j k h => hf (Subtype.ext h)) (fun j => (f j).2)
    (fun j t => by rw [par_eq]; exact cast_lin_gen Z w x Z.hw _ (f j).2 t)
    (fun j t => by
      rw [par_eq, cast_lin_gen Z v y Z.hv _ (f j).2 t, Matrix.mulVec_mulVec, hBinv, Matrix.one_mulVec])
    hMu

end Main
#print axioms P104.p104_linear_cost_ge_free
#print axioms P104.kern_B
#print axioms LinCB.cb_exists
end P104
