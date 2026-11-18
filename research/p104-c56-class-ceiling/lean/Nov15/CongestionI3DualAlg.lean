import Nov15.WordDuality
import Mathlib.Analysis.MeanInequalitiesPow
import Mathlib.Analysis.SpecialFunctions.Pow.NNReal

/-!
CONGESTION-I3-DUAL, algebra half.  Source: internal notes (audited SOUND, i3dual/audit/AUD.md).
Two-sided I3: the excess of one public register is telescoped from the END (h9 charge, needs e = 9) or from the BIRTH (k0 charge, needs d0 = 0);
every move of a non-mixed register carries a charge >= c2 = min (h9, k0), and a mixed register (d0 >= 1, e <= 8) loses at most c2 (d0, e).
Kernel only; no sorry, no native_decide.  `g` is an arbitrary price function with g 0 = 0 (instance: `gs s x = x^s`, s = 1 - t).
Nothing numeric here.  See CongestionI3Dual.md.
-/
namespace CongestionI3Dual
open Finset WordDuality

/-! ### 1. move prices -/

/-- end-anchored move price (target V = dim 9): g(b-a) + g(9-b) - g(9-a) -/
def h9 (g : ℝ → ℝ) (a b : ℝ) : ℝ := g (b - a) + g (9 - b) - g (9 - a)
/-- start-anchored move price (birth {0}): g(b-a) + g(a) - g(b) -/
def k0 (g : ℝ → ℝ) (a b : ℝ) : ℝ := g (b - a) + g a - g b
/-- the uniform charge of ID1 sec. 1 -/
def c2 (g : ℝ → ℝ) (a b : ℝ) : ℝ := min (h9 g a b) (k0 g a b)

/-- the price function of the F currency: x^s on x > 0, and 0 at 0 -/
noncomputable def gs (s : ℝ) (x : ℝ) : ℝ := if 0 < x then x ^ s else 0
theorem gs_zero (s : ℝ) : gs s 0 = 0 := by simp [gs]

/-- x^s is subadditive on [0, inf) for 0 <= s <= 1 -/
theorem gs_subadd (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (x y : ℝ) (hx : 0 ≤ x) (hy : 0 ≤ y) :
    gs s (x + y) ≤ gs s x + gs s y := by
  have key : (x + y) ^ s ≤ x ^ s + y ^ s := by
    have := NNReal.rpow_add_le_add_rpow x.toNNReal y.toNNReal hs0 hs1
    have h3 : ((x.toNNReal + y.toNNReal) ^ s : NNReal) ≤ (x.toNNReal ^ s + y.toNNReal ^ s : NNReal) := this
    have h4 := (NNReal.coe_le_coe.mpr h3)
    simpa [NNReal.coe_rpow, Real.coe_toNNReal _ hx, Real.coe_toNNReal _ hy] using h4
  unfold gs
  by_cases hx0 : 0 < x
  · by_cases hy0 : 0 < y
    · rw [if_pos hx0, if_pos hy0, if_pos (by linarith)]; exact key
    · have : y = 0 := le_antisymm (not_lt.mp hy0) hy
      subst this; simp
  · have : x = 0 := le_antisymm (not_lt.mp hx0) hx
    subst this; simp

/-- the two prices are >= 0 for a subadditive g with g 0 = 0 on 0 <= a <= b <= 9 -/
theorem h9_nonneg (g : ℝ → ℝ) (hg : ∀ x y, 0 ≤ x → 0 ≤ y → g (x + y) ≤ g x + g y) (a b : ℝ) (hab : a ≤ b) (hb : b ≤ 9) :
    0 ≤ h9 g a b := by
  have := hg (b - a) (9 - b) (by linarith) (by linarith)
  have e : b - a + (9 - b) = 9 - a := by ring
  rw [e] at this; unfold h9; linarith
theorem k0_nonneg (g : ℝ → ℝ) (hg : ∀ x y, 0 ≤ x → 0 ≤ y → g (x + y) ≤ g x + g y) (a b : ℝ) (ha : 0 ≤ a) (hab : a ≤ b) :
    0 ≤ k0 g a b := by
  have := hg (b - a) a (by linarith) ha
  have e : b - a + a = b := by ring
  rw [e] at this; unfold k0; linarith

/-- duality at the level of move prices (DU1): the start-anchored price of (a,b) is the end-anchored price of the swapped move
`swapN 9 (a,b) = (9-b, 9-a)` of WordDuality. -/
theorem k0_eq_h9_swapN (g : ℝ → ℝ) (a b : ℕ) (hb : b ≤ 9) (hab : a ≤ b) :
    k0 g a b = h9 g (swapN 9 (a, b)).1 (swapN 9 (a, b)).2 := by
  simp only [swapN, k0, h9]
  have h1 : (((9 - b : ℕ) : ℕ) : ℝ) = 9 - b := by rw [Nat.cast_sub hb]; norm_num
  have h2 : (((9 - a : ℕ) : ℕ) : ℝ) = 9 - a := by rw [Nat.cast_sub (le_trans hab hb)]; norm_num
  rw [h1, h2]
  have e1 : (9 - (a : ℝ)) - (9 - b) = b - a := by ring
  have e2 : (9 : ℝ) - (9 - a) = a := by ring
  have e3 : (9 : ℝ) - (9 - b) = b := by ring
  rw [e1, e2, e3]

/-- the dual helper (WordDuality `dualH 9`) has the same move prices: its end-anchored charge list is the start-anchored charge list of the
original (reversed order, equal sum). -/
theorem dualH_charge (g : ℝ → ℝ) (h : FibreK.Helper) (hs : ∀ s ∈ h.steps, s.2 ≤ 9 ∧ s.1 ≤ s.2) :
    (((dualH 9 h).steps).map fun s : ℕ × ℕ => h9 g s.1 s.2).sum = (h.steps.map fun s : ℕ × ℕ => k0 g s.1 s.2).sum := by
  simp only [dualH, List.map_reverse, List.sum_reverse, List.map_map]
  congr 1
  apply List.map_congr_left
  intro s hs'
  obtain ⟨h1, h2⟩ := hs s hs'
  simp only [Function.comp]
  exact (k0_eq_h9_swapN g s.1 s.2 h1 h2).symm

/-! ### 2. one register: telescoping -/

/-- a register path: levels `d 0, ..., d n` (born at `d 0`, ending at `d n`); its excess over R3's floor is
`ex = sum g(gaps) - g(e - d0)` (ID1 sec. 1). -/
def gsum (g : ℝ → ℝ) (d : ℕ → ℝ) (n : ℕ) : ℝ := ∑ i ∈ range n, g (d (i + 1) - d i)
def ex (g : ℝ → ℝ) (d : ℕ → ℝ) (n : ℕ) : ℝ := gsum g d n - g (d n - d 0)

/-- end-anchored telescoping: for e = 9 the h9 charges sum to the excess -/
theorem sum_h9_eq (g : ℝ → ℝ) (hg0 : g 0 = 0) (d : ℕ → ℝ) (n : ℕ) (he : d n = 9) :
    ∑ i ∈ range n, h9 g (d i) (d (i + 1)) = ex g d n := by
  have t : ∑ i ∈ range n, (g (9 - d (i + 1)) - g (9 - d i)) = g (9 - d n) - g (9 - d 0) :=
    Finset.sum_range_sub (fun i => g (9 - d i)) n
  have h : ∑ i ∈ range n, h9 g (d i) (d (i + 1)) = gsum g d n + ∑ i ∈ range n, (g (9 - d (i + 1)) - g (9 - d i)) := by
    unfold h9 gsum; rw [← Finset.sum_add_distrib]; apply Finset.sum_congr rfl; intro i _; ring
  rw [h, t, he]; unfold ex
  have e : (9 : ℝ) - 9 = 0 := by ring
  rw [e, hg0, he]; ring

/-- start-anchored telescoping: for d0 = 0 the k0 charges sum to the excess -/
theorem sum_k0_eq (g : ℝ → ℝ) (hg0 : g 0 = 0) (d : ℕ → ℝ) (n : ℕ) (hd : d 0 = 0) :
    ∑ i ∈ range n, k0 g (d i) (d (i + 1)) = ex g d n := by
  have t : ∑ i ∈ range n, (g (d i) - g (d (i + 1))) = g (d 0) - g (d n) := by
    have := Finset.sum_range_sub (fun i => g (d i)) n
    have h2 : ∑ i ∈ range n, (g (d i) - g (d (i + 1))) = -∑ i ∈ range n, (g (d (i + 1)) - g (d i)) := by
      rw [← Finset.sum_neg_distrib]; apply Finset.sum_congr rfl; intro i _; ring
    rw [h2, this]; ring
  have h : ∑ i ∈ range n, k0 g (d i) (d (i + 1)) = gsum g d n + ∑ i ∈ range n, (g (d i) - g (d (i + 1))) := by
    unfold k0 gsum; rw [← Finset.sum_add_distrib]; apply Finset.sum_congr rfl; intro i _; ring
  rw [h, t, hd]; unfold ex
  rw [hd, hg0]; ring_nf

/-- **non-mixed register: every move is charged >= c2 and the charges sum to the excess** (ID1 sec. 1, `charge_V`/`charge_Z`). -/
theorem nonmixed_charge (g : ℝ → ℝ) (hg0 : g 0 = 0) (d : ℕ → ℝ) (n : ℕ) (h : d n = 9 ∨ d 0 = 0) :
    ∃ w : ℕ → ℝ, (∀ i ∈ range n, c2 g (d i) (d (i + 1)) ≤ w i) ∧ ∑ i ∈ range n, w i = ex g d n := by
  rcases h with h | h
  · exact ⟨fun i => h9 g (d i) (d (i + 1)), fun i _ => min_le_left _ _, sum_h9_eq g hg0 d n h⟩
  · exact ⟨fun i => k0 g (d i) (d (i + 1)), fun i _ => min_le_right _ _, sum_k0_eq g hg0 d n h⟩

/-- **the slack of any register** (covers mixed registers, ID1 sec. 2): the c2-charges sum to at most the excess plus c2 of the whole register.
No hypothesis on g or on the levels: pointwise `c2 <= g(gap) - max (g(9-a)-g(9-b), g(b)-g(a))`, and both maxima telescope. -/
theorem sum_c2_le (g : ℝ → ℝ) (d : ℕ → ℝ) (n : ℕ) :
    ∑ i ∈ range n, c2 g (d i) (d (i + 1)) ≤ ex g d n + c2 g (d 0) (d n) := by
  have t1 : ∑ i ∈ range n, (g (9 - d (i + 1)) - g (9 - d i)) = g (9 - d n) - g (9 - d 0) :=
    Finset.sum_range_sub (fun i => g (9 - d i)) n
  have t2 : ∑ i ∈ range n, (g (d i) - g (d (i + 1))) = g (d 0) - g (d n) := by
    have := Finset.sum_range_sub (fun i => g (d i)) n
    have h2 : ∑ i ∈ range n, (g (d i) - g (d (i + 1))) = -∑ i ∈ range n, (g (d (i + 1)) - g (d i)) := by
      rw [← Finset.sum_neg_distrib]; apply Finset.sum_congr rfl; intro i _; ring
    rw [h2, this]; ring
  have A : ∑ i ∈ range n, c2 g (d i) (d (i + 1)) ≤ ex g d n + h9 g (d 0) (d n) := by
    have : ∑ i ∈ range n, c2 g (d i) (d (i + 1)) ≤ ∑ i ∈ range n, (g (d (i + 1) - d i) + (g (9 - d (i + 1)) - g (9 - d i)))  := by
      apply Finset.sum_le_sum; intro i _
      have : c2 g (d i) (d (i + 1)) ≤ h9 g (d i) (d (i + 1)) := min_le_left _ _
      unfold h9 at this; linarith
    rw [Finset.sum_add_distrib, t1] at this
    unfold ex gsum h9 at *; linarith
  have B : ∑ i ∈ range n, c2 g (d i) (d (i + 1)) ≤ ex g d n + k0 g (d 0) (d n) := by
    have : ∑ i ∈ range n, c2 g (d i) (d (i + 1)) ≤ ∑ i ∈ range n, (g (d (i + 1) - d i) + (g (d i) - g (d (i + 1)))) := by
      apply Finset.sum_le_sum; intro i _
      have : c2 g (d i) (d (i + 1)) ≤ k0 g (d i) (d (i + 1)) := min_le_right _ _
      unfold k0 at this; linarith
    rw [Finset.sum_add_distrib, t2] at this
    unfold ex gsum k0 at *; linarith
  unfold c2
  rcases le_total (h9 g (d 0) (d n)) (k0 g (d 0) (d n)) with h | h
  · rw [min_eq_left h]; exact A
  · rw [min_eq_right h]; exact B

/-- non-mixed (born at 0 or ending at 9): c2 of the whole register vanishes -/
theorem c2_total_nonmixed (g : ℝ → ℝ) (hg0 : g 0 = 0) (a e : ℝ) (h : e = 9 ∨ a = 0) : c2 g a e ≤ 0 := by
  unfold c2
  rcases h with h | h
  · subst h; have : h9 g a 9 = g 0 := by unfold h9; simp
    rw [hg0] at this; exact le_trans (min_le_left _ _) this.le
  · subst h; have : k0 g 0 e = g 0 := by unfold k0; simp
    rw [hg0] at this; exact le_trans (min_le_right _ _) this.le

/-! ### 3. many registers: <= m mixed -/

section Many
variable {ι : Type*} [DecidableEq ι]

/-- a register is MIXED if it is born above {0} and ends below V (levels are dims) -/
def Mixed (d : ι → ℕ → ℕ) (n : ι → ℕ) (r : ι) : Prop := 1 ≤ d r 0 ∧ d r (n r) ≤ 8
instance (d : ι → ℕ → ℕ) (n : ι → ℕ) (r : ι) : Decidable (Mixed d n r) := by unfold Mixed; infer_instance

/-- the dim sequence of register `r` as reals -/
def lev (d : ι → ℕ → ℕ) (r : ι) : ℕ → ℝ := fun i => (d r i : ℝ)

/-- **summing over registers**: c2-charges of all moves <= total excess + (number of mixed registers) * sigma, where `sigma` bounds c2 of one
mixed register (dims 1 <= a <= b <= 8). -/
theorem sum_all_c2_le (g : ℝ → ℝ) (hg0 : g 0 = 0) (R : Finset ι) (n : ι → ℕ) (d : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < n r, d r i ≤ d r (i + 1)) (hd9 : ∀ r ∈ R, d r (n r) ≤ 9)
    (m : ℕ) (hm : (R.filter fun r => Mixed d n r).card ≤ m) (σ : ℝ) (hσ0 : 0 ≤ σ)
    (hσ : ∀ a b : ℕ, 1 ≤ a → a ≤ b → b ≤ 8 → c2 g (a : ℝ) (b : ℝ) ≤ σ) :
    ∑ r ∈ R, ∑ i ∈ range (n r), c2 g (lev d r i) (lev d r (i + 1)) ≤ ∑ r ∈ R, ex g (lev d r) (n r) + m * σ := by
  have step : ∀ r ∈ R, ∑ i ∈ range (n r), c2 g (lev d r i) (lev d r (i + 1)) ≤
      ex g (lev d r) (n r) + (if Mixed d n r then σ else 0) := by
    intro r hr
    have h1 := sum_c2_le g (lev d r) (n r)
    have hle : ∀ k ≤ n r, d r 0 ≤ d r k := by
      intro k
      induction k with
      | zero => intro _; exact le_refl _
      | succ k ih => intro hk; exact le_trans (ih (by omega)) (hmono r hr k (by omega))
    have h0e := hle (n r) (le_refl _)
    by_cases hmx : Mixed d n r
    · rw [if_pos hmx]
      have := hσ (d r 0) (d r (n r)) hmx.1 h0e hmx.2
      simp only [lev] at h1 ⊢
      linarith
    · rw [if_neg hmx]
      have hne : d r (n r) = 9 ∨ d r 0 = 0 := by
        unfold Mixed at hmx
        have := hd9 r hr
        omega
      have h2 := c2_total_nonmixed g hg0 (lev d r 0) (lev d r (n r))
        (by
          rcases hne with h | h
          · left; simp [lev, h]
          · right; simp [lev, h])
      simp only [lev] at h1 h2 ⊢
      linarith
  calc ∑ r ∈ R, ∑ i ∈ range (n r), c2 g (lev d r i) (lev d r (i + 1))
      ≤ ∑ r ∈ R, (ex g (lev d r) (n r) + (if Mixed d n r then σ else 0)) := Finset.sum_le_sum step
    _ = ∑ r ∈ R, ex g (lev d r) (n r) + ∑ r ∈ R, (if Mixed d n r then σ else 0) := Finset.sum_add_distrib
    _ ≤ ∑ r ∈ R, ex g (lev d r) (n r) + m * σ := by
        have : ∑ r ∈ R, (if Mixed d n r then σ else 0) = ((R.filter fun r => Mixed d n r).card : ℝ) * σ := by
          rw [← Finset.sum_filter]; simp
        rw [this]
        have hm' : ((R.filter fun r => Mixed d n r).card : ℝ) ≤ m := by exact_mod_cast hm
        nlinarith

end Many

end CongestionI3Dual

#print axioms CongestionI3Dual.gs_subadd
#print axioms CongestionI3Dual.k0_eq_h9_swapN
#print axioms CongestionI3Dual.dualH_charge
#print axioms CongestionI3Dual.nonmixed_charge
#print axioms CongestionI3Dual.sum_c2_le
#print axioms CongestionI3Dual.sum_all_c2_le
