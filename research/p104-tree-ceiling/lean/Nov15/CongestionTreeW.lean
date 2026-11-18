import Nov15.CongestionI3DualSig
import Nov15.CongestionTreeCore

/-!
CONGESTION-TREE-W: kernel certificate that the integer weight table `W a b` (units 1/10^14, rounded DOWN) is a lower bound of
`c2 (gs s) a b = min (h9, k0)` for every `s` in a window `[lo, hi]`.  Method: `h9`, `k0` are exponential polynomials (`h9CF`, `k0CF`);
`dLo (negCF cf) lo hi > 0` proves them nonincreasing in `s` on the window (so nondecreasing in `t = 1 - s`), and a point enclosure
`Fup (negCF cf) hi hi <= -W/10^14` bounds them below at `s = hi`.  No monotonicity hypothesis remains.
-/
namespace CTree
open NumCertK CongestionI3Dual

def negCF (cf : CF) : CF := cf.map fun p => (p.1, -p.2)

theorem Fc_negCF (cf : CF) (s : ℝ) : Fc (negCF cf) s = - Fc cf s := by
  induction cf with
  | nil => simp [Fc, negCF]
  | cons p l ih =>
    simp only [Fc, negCF, List.map_cons, List.sum_cons] at ih ⊢
    push_cast
    linarith

theorem okR_negCF (cf : CF) (h : okR cf) : okR (negCF cf) := by
  intro p hp
  simp only [negCF, List.mem_map] at hp
  obtain ⟨q, hq, rfl⟩ := hp
  exact h q hq

def Wt (W : List (List ℕ)) (a b : ℕ) : ℕ := (W.getD a []).getD b 0

def wtPair (W : List (List ℕ)) (lo hi : ℚ) (p : ℕ × ℕ) : Bool :=
  decide (0 < dLo (negCF (h9CF p.1 p.2)) lo hi) && decide (0 < dLo (negCF (k0CF p.1 p.2)) lo hi) &&
    decide (Fup (negCF (h9CF p.1 p.2)) hi hi ≤ -((Wt W p.1 p.2 : ℚ) / 10 ^ 14)) &&
    decide (Fup (negCF (k0CF p.1 p.2)) hi hi ≤ -((Wt W p.1 p.2 : ℚ) / 10 ^ 14))

def wtOK (W : List (List ℕ)) (lo hi : ℚ) : Bool := pairs.all (wtPair W lo hi)

theorem cf_lower (cf : CF) (hok : okR cf) (lo hi : ℚ) (hlo : 0 ≤ lo) (hhi : hi ≤ 1) (hd : 0 < dLo (negCF cf) lo hi) (q : ℚ)
    (hq : Fup (negCF cf) hi hi ≤ -q) (s : ℝ) (h1 : (lo : ℝ) ≤ s) (h2 : s ≤ (hi : ℝ)) : (q : ℝ) ≤ Fc cf s := by
  have hok' := okR_negCF cf hok
  have m1 := Fc_mono (negCF cf) hok' lo hi hlo hhi hd s h1 h2
  have hhi0 : 0 ≤ hi := by
    have : (0 : ℝ) ≤ hi := le_trans (by exact_mod_cast hlo) (le_trans h1 h2)
    exact_mod_cast this
  have m2 := Fc_le (negCF cf) hok' hi hi hhi0 hhi (hi : ℝ) (le_refl _) (le_refl _)
  have m3 : ((Fup (negCF cf) hi hi : ℚ) : ℝ) ≤ ((-q : ℚ) : ℝ) := by exact_mod_cast hq
  simp only [Fc_negCF] at m1 m2
  push_cast at m3
  linarith

theorem W_lower (W : List (List ℕ)) (lo hi : ℚ) (hok : wtOK W lo hi = true) (hlo : 0 ≤ lo) (hhi : hi ≤ 1) (s : ℝ)
    (h1 : (lo : ℝ) ≤ s) (h2 : s ≤ (hi : ℝ)) (a b : ℕ) (ha : 1 ≤ a) (hab : a < b) (hb : b ≤ 8) :
    ((Wt W a b : ℕ) : ℝ) / SCr ≤ c2 (gs s) (a : ℝ) (b : ℝ) := by
  have hm : (a, b) ∈ pairs := mem_pairs a (by omega) b (by omega) ⟨ha, hab, hb⟩
  have := List.all_eq_true.mp hok (a, b) hm
  simp only [wtPair, Bool.and_eq_true, decide_eq_true_eq] at this
  obtain ⟨⟨⟨d1, d2⟩, f1⟩, f2⟩ := this
  have e1 := cf_lower (h9CF a b) (okR_h9CF a b ha hab hb) lo hi hlo hhi d1 ((Wt W a b : ℚ) / 10 ^ 14) f1 s h1 h2
  have e2 := cf_lower (k0CF a b) (okR_k0CF a b ha hab hb) lo hi hlo hhi d2 ((Wt W a b : ℚ) / 10 ^ 14) f2 s h1 h2
  rw [← h9_Fc s a b ha hab hb] at e1
  rw [← k0_Fc s a b ha hab hb] at e2
  have hS : SCr = ((10 ^ 14 : ℚ) : ℝ) := by unfold SCr; push_cast; ring
  have : (((Wt W a b : ℚ) / 10 ^ 14 : ℚ) : ℝ) = ((Wt W a b : ℕ) : ℝ) / SCr := by
    rw [hS]; push_cast; ring
  rw [this] at e1 e2
  unfold c2
  exact le_min e1 e2

end CTree

#print axioms CTree.W_lower
