import Nov15.CongestionI3DualAlg
import Nov15.NumCertK
import Nov15.CongestionI3DualConst

/-!
CONGESTION-I3-DUAL, sigma certificates.  `sigma(t)` = the largest c2 of one mixed register (dims 1 <= a <= b <= 8) is CERTIFIED here
on each t-piece by `NumCertK.Fup` (kernel interval arithmetic): for every pair (a,b), min(Fup h9, Fup k0) < sigma on the whole s-interval.  So sigma needs
no monotonicity hypothesis: each piece carries its own certified bound.
-/
namespace CongestionI3Dual
open NumCertK

def h9CF (a b : ℕ) : CF := [(b - a, 1), (9 - b, 1), (9 - a, -1)]
def k0CF (a b : ℕ) : CF := [(b - a, 1), (a, 1), (b, -1)]

theorem gs_nat (s : ℝ) (k : ℕ) (hk : 1 ≤ k) : gs s (k : ℝ) = (k : ℝ) ^ s := by
  have : (0 : ℝ) < k := by exact_mod_cast hk
  simp [gs, this]

theorem h9_Fc (s : ℝ) (a b : ℕ) (ha : 1 ≤ a) (hab : a < b) (hb : b ≤ 8) :
    h9 (gs s) (a : ℝ) (b : ℝ) = Fc (h9CF a b) s := by
  have e1 : (b : ℝ) - a = ((b - a : ℕ) : ℝ) := by rw [Nat.cast_sub hab.le]
  have e2 : (9 : ℝ) - b = ((9 - b : ℕ) : ℝ) := by rw [Nat.cast_sub (by omega)]; norm_num
  have e3 : (9 : ℝ) - a = ((9 - a : ℕ) : ℝ) := by rw [Nat.cast_sub (by omega)]; norm_num
  unfold h9; rw [e1, e2, e3, gs_nat s _ (by omega), gs_nat s _ (by omega), gs_nat s _ (by omega)]
  simp [Fc, h9CF]; ring

theorem k0_Fc (s : ℝ) (a b : ℕ) (ha : 1 ≤ a) (hab : a < b) (hb : b ≤ 8) :
    k0 (gs s) (a : ℝ) (b : ℝ) = Fc (k0CF a b) s := by
  have e1 : (b : ℝ) - a = ((b - a : ℕ) : ℝ) := by rw [Nat.cast_sub hab.le]
  unfold k0; rw [e1, gs_nat s _ (by omega), gs_nat s _ ha, gs_nat s _ (by omega)]
  simp [Fc, k0CF]; ring

def pairs : List (ℕ × ℕ) := [(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(2,3),(2,4),(2,5),(2,6),(2,7),(2,8),(3,4),(3,5),(3,6),(3,7),(3,8),
  (4,5),(4,6),(4,7),(4,8),(5,6),(5,7),(5,8),(6,7),(6,8),(7,8)]
theorem mem_pairs (a : ℕ) (ha : a < 9) (b : ℕ) (hb : b < 9) (h : 1 ≤ a ∧ a < b ∧ b ≤ 8) : (a, b) ∈ pairs := by
  obtain ⟨h1, h2, h3⟩ := h
  interval_cases a <;> interval_cases b <;> simp [pairs] at h2 h3 ⊢

def sigOK (lo hi σ : ℚ) : Bool :=
  pairs.all fun p => decide (Fup (h9CF p.1 p.2) lo hi < σ) || decide (Fup (k0CF p.1 p.2) lo hi < σ)

theorem okR_h9CF (a b : ℕ) (ha : 1 ≤ a) (hab : a < b) (hb : b ≤ 8) : okR (h9CF a b) := by
  intro p hp; simp [h9CF] at hp
  rcases hp with h | h | h <;> subst h <;> simp <;> omega
theorem okR_k0CF (a b : ℕ) (ha : 1 ≤ a) (hab : a < b) (hb : b ≤ 8) : okR (k0CF a b) := by
  intro p hp; simp [k0CF] at hp
  rcases hp with h | h | h <;> subst h <;> simp <;> omega

/-- **sigma certificate**: if `sigOK lo hi σ`, then for every s in [lo, hi], every 1 <= a <= b <= 8: c2 (gs s) a b <= σ (σ >= 0). -/
theorem sig_of_ok (lo hi σ : ℚ) (hok : sigOK lo hi σ = true) (hlo : 0 ≤ lo) (hhi : hi ≤ 1) (hσ : 0 ≤ σ) (s : ℝ)
    (h1 : (lo : ℝ) ≤ s) (h2 : s ≤ (hi : ℝ)) (a b : ℕ) (ha : 1 ≤ a) (hab : a ≤ b) (hb : b ≤ 8) :
    c2 (gs s) (a : ℝ) (b : ℝ) ≤ (σ : ℝ) := by
  rcases Nat.lt_or_ge a b with h | h
  · have hm : (a, b) ∈ pairs := mem_pairs a (by omega) b (by omega) ⟨ha, h, hb⟩
    have := List.all_eq_true.mp hok (a, b) hm
    simp only [Bool.or_eq_true, decide_eq_true_eq] at this
    unfold c2
    rcases this with hh | hh
    · have := Fc_le (h9CF a b) (okR_h9CF a b ha h hb) lo hi hlo hhi s h1 h2
      have h' : ((Fup (h9CF a b) lo hi : ℚ) : ℝ) < σ := by exact_mod_cast hh
      rw [← h9_Fc s a b ha h hb] at this
      exact le_trans (min_le_left _ _) (by linarith)
    · have := Fc_le (k0CF a b) (okR_k0CF a b ha h hb) lo hi hlo hhi s h1 h2
      have h' : ((Fup (k0CF a b) lo hi : ℚ) : ℝ) < σ := by exact_mod_cast hh
      rw [← k0_Fc s a b ha h hb] at this
      exact le_trans (min_le_right _ _) (by linarith)
  · have hba : a = b := le_antisymm hab h
    subst hba
    have h0 : h9 (gs s) (a : ℝ) (a : ℝ) = 0 := by unfold h9; simp [gs_zero]
    have : c2 (gs s) (a : ℝ) (a : ℝ) ≤ 0 := by unfold c2; rw [h0]; exact min_le_left _ _
    have hσ' : (0 : ℝ) ≤ σ := by exact_mod_cast hσ
    linarith

/-! ### the pieces (t in [t_j, t_{j+1}], s in [1 - t_{j+1}, 1 - t_j]) -/
end CongestionI3Dual

#print axioms CongestionI3Dual.sig_of_ok
