/-
CallerWordA (lane CALLERWORD, Nov 20).  SUPPORT for the type-A J record (two HOSTs):
  jA t x y u v α2 = [HOST(x,y,0,1), HOST(u,v,α2,0), IDLE x {t}, IDLE y {t}, IDLE u {t}, IDLE v {t}],
with x, y, u, v distinct (operator_ring `joint distinct fields`).  Every frame column of either HOST is supported on
E_t = {r : t ∈ mask r}.  The second HOST conjugates the first one's incidence vectors only through H2 = 1 + α2 E_uv,
which fixes e_x, e_y (columns, x, y ≠ v) and their rows (x, y ≠ u).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.CallerWordS

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerWord
open Matrix Finset CallerSign

section suppA
variable {n k : ℕ}

theorem mul_E1_apply (X : Matrix (Fin n) (Fin n) ℂ) (x y : Fin n) (c : ℂ) (r r' : Fin n) :
    (X * E1 x y c) r r' = if r' = y then X r x * c else 0 := by
  simp only [Matrix.mul_apply, E1, Matrix.of_apply]
  by_cases h : r' = y
  · simp [h]
  · simp [h]

theorem E1_mul_E1 (a b c d : Fin n) (p q : ℂ) (hbc : b ≠ c) : E1 a b p * E1 c d q = 0 := by
  ext r r'; rw [E1_mul_apply]; simp [E1, hbc]

theorem host2_base (u v : Fin n) (α : ℚ) :
    evMat (1 : ℂ) Complex.I (1 : Fin k → ℂ) (Ev.host u v α 0 : Ev n k) = 1 + E1 u v (algebraMap ℚ ℂ α) := by
  simp [evMat, E1_zero]

theorem host2_inv (u v : Fin n) (c : ℂ) (huv : u ≠ v) :
    (1 + E1 u v c : Matrix (Fin n) (Fin n) ℂ)⁻¹ = 1 + E1 u v (-c) := by
  apply Matrix.inv_eq_right_inv
  rw [Matrix.add_mul, Matrix.mul_add, Matrix.mul_add, Matrix.one_mul, Matrix.mul_one, Matrix.one_mul,
    E1_mul_E1 _ _ _ _ _ _ huv.symm]
  have : E1 u v c + E1 u v (-c) = (0 : Matrix (Fin n) (Fin n) ℂ) := by
    ext a b; simp only [E1, Matrix.add_apply, Matrix.of_apply, Matrix.zero_apply]; split_ifs <;> simp
  first
  | (rw [add_zero, add_assoc, this, add_zero])
  | (rw [add_comm (E1 u v (-c)), this, add_zero])
  | (simp only [add_zero]; rw [add_assoc, add_comm (E1 u v (-c)), this, add_zero])

variable (w : CWord n k) (t0 : Fin k)
variable (hb : replay (1 : ℂ) Complex.I 1 w.evs = 1) (hL : LegalAt (1 : DN) iD (Dt t0) w)
include hb hL

theorem jA_cols (j : ℕ) (hj5 : j + 5 < w.evs.length) (x y u v : Fin n) (α : ℚ)
    (hxy : x ≠ y) (hxu : x ≠ u) (hxv : x ≠ v) (hyu : y ≠ u) (hyv : y ≠ v) (huv : u ≠ v)
    (h0 : w.evs.get ⟨j, by omega⟩ = Ev.host x y 0 1)
    (h1 : w.evs.get ⟨j + 1, by omega⟩ = Ev.host u v α 0)
    (h2 : w.evs.get ⟨j + 2, by omega⟩ = Ev.idle x {t0} 0)
    (h3 : w.evs.get ⟨j + 3, by omega⟩ = Ev.idle y {t0} 0)
    (h4 : w.evs.get ⟨j + 4, by omega⟩ = Ev.idle u {t0} 0)
    (h5 : w.evs.get ⟨j + 5, hj5⟩ = Ev.idle v {t0} 0)
    (r : Fin n) (hr : t0 ∉ w.mask r) (p : Iota w) (hp : p.1.1.val = j ∨ p.1.1.val = j + 1) :
    Aw w Complex.I r p = 0 ∧ Bw w Complex.I r p = 0 := by
  have g2 : w.evs[j + 2]'(by omega) = Ev.idle x {t0} 0 := by simpa using h2
  have g3 : w.evs[j + 3]'(by omega) = Ev.idle y {t0} 0 := by simpa using h3
  have g4 : w.evs[j + 4]'(by omega) = Ev.idle u {t0} 0 := by simpa using h4
  have g5 : w.evs[j + 5]'hj5 = Ev.idle v {t0} 0 := by simpa using h5
  have i2 : inc t0 (w.evs.get ⟨j + 2, by omega⟩) = true := by rw [h2]; simp [inc]
  have i3 : inc t0 (w.evs.get ⟨j + 3, by omega⟩) = true := by rw [h3]; simp [inc]
  have i4 : inc t0 (w.evs.get ⟨j + 4, by omega⟩) = true := by rw [h4]; simp [inc]
  have i5 : inc t0 (w.evs.get ⟨j + 5, hj5⟩) = true := by rw [h5]; simp [inc]
  have stepI : ∀ m (hm : m < w.evs.length) (z : Fin n),
      w.evs.get ⟨m, hm⟩ = Ev.idle z {t0} 0 → P1 w Complex.I (m + 1) = P1 w Complex.I m := by
    intro m hm z hz
    unfold P1; rw [pre_succ, evAt_get w _ 1 1 m hm, hz, idle_base, Matrix.one_mul]
  have P3 := stepI (j + 2) (by omega) x h2
  have P4 := stepI (j + 3) (by omega) y h3
  have P5 := stepI (j + 4) (by omega) u h4
  have hP2 : P1 w Complex.I (j + 2) = (1 + E1 u v (algebraMap ℚ ℂ α)) * P1 w Complex.I (j + 1) := by
    unfold P1; rw [pre_succ, evAt_get w _ 1 1 (j + 1) (by omega), h1, host2_base]
  have hP2i : (P1 w Complex.I (j + 2))⁻¹ = (P1 w Complex.I (j + 1))⁻¹ * (1 + E1 u v (-algebraMap ℚ ℂ α)) := by
    rw [hP2, Matrix.mul_inv_rev, host2_inv _ _ _ huv]
  rcases hp with hp | hp
  · -- first HOST: its incidences sit at j+2 (x) and j+3 (y), behind H2
    refine host_cols w t0 hb hL ⟨j, by omega⟩ x y 0 1 h0 hxy ⟨_, i2⟩ ⟨_, i3⟩ ?_ ?_ ?_ ?_ r hr p (Fin.ext hp)
    · intro r'; simp only [incV, Matrix.of_apply]
      rw [hP2i, Matrix.mul_add, Matrix.mul_one, Matrix.add_apply, mul_E1_apply]; simp [g2, reg, hxv]
    · intro r'; simp only [incV, Matrix.of_apply]
      rw [P3, hP2i, Matrix.mul_add, Matrix.mul_one, Matrix.add_apply, mul_E1_apply]; simp [g3, reg, hyv]
    · intro r'; simp only [incW, Matrix.of_apply]
      rw [hP2, Matrix.add_mul, Matrix.one_mul, Matrix.add_apply, E1_mul_apply]; simp [g2, reg, hxu]
    · intro r'; simp only [incW, Matrix.of_apply]
      rw [P3, hP2, Matrix.add_mul, Matrix.one_mul, Matrix.add_apply, E1_mul_apply]; simp [g3, reg, hyu]
  · -- second HOST: incidences at j+4 (u), j+5 (v); prefixes equal P1(j+2)
    refine host_cols w t0 hb hL ⟨j + 1, by omega⟩ u v α 0 h1 huv ⟨_, i4⟩ ⟨_, i5⟩ ?_ ?_ ?_ ?_ r hr p (Fin.ext hp)
    · intro r'; simp [incV, g4, reg, P4, P3]
    · intro r'; simp [incV, g5, reg, P5, P4, P3]
    · intro r'; simp [incW, g4, reg, P4, P3]
    · intro r'; simp [incW, g5, reg, P5, P4, P3]

end suppA

/-- headline: every legal word's type-A J record gives frame columns supported on E_t0. -/
theorem legal_jA_support {n k : ℕ} (w : CWord n k) (hL : Legal w) (t0 : Fin k) (j : ℕ)
    (hj5 : j + 5 < w.evs.length) (x y u v : Fin n) (α : ℚ)
    (hxy : x ≠ y) (hxu : x ≠ u) (hxv : x ≠ v) (hyu : y ≠ u) (hyv : y ≠ v) (huv : u ≠ v)
    (h0 : w.evs.get ⟨j, by omega⟩ = Ev.host x y 0 1)
    (h1 : w.evs.get ⟨j + 1, by omega⟩ = Ev.host u v α 0)
    (h2 : w.evs.get ⟨j + 2, by omega⟩ = Ev.idle x {t0} 0)
    (h3 : w.evs.get ⟨j + 3, by omega⟩ = Ev.idle y {t0} 0)
    (h4 : w.evs.get ⟨j + 4, by omega⟩ = Ev.idle u {t0} 0)
    (h5 : w.evs.get ⟨j + 5, hj5⟩ = Ev.idle v {t0} 0)
    (r : Fin n) (hr : t0 ∉ w.mask r) (p : Iota w) (hp : p.1.1.val = j ∨ p.1.1.val = j + 1) :
    Aw w Complex.I r p = 0 ∧ Bw w Complex.I r p = 0 := by
  obtain ⟨hL', hb⟩ := legal_dn w hL t0
  exact jA_cols w t0 hb hL' j hj5 x y u v α hxy hxu hxv hyu hyv huv h0 h1 h2 h3 h4 h5 r hr p hp

end CallerWord

#print axioms CallerWord.jA_cols
#print axioms CallerWord.legal_jA_support
