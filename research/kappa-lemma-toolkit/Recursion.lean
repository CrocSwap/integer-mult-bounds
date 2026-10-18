import Mathlib.Algebra.Order.Archimedean.Basic
import Mathlib.Algebra.Order.Archimedean.Real.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-!
# Active-depth exact-grid bounds and affine exponent bootstrap

Universal sufficient algebraic interfaces. No recursive child implementation,
rounding model, multiplication runtime, or numerical frontier is assumed here.
-/

namespace IntegerMultBounds.Recursion

/-- A proper rank gives a nonincreasing child width, including short tails. -/
theorem child_le (m r e : ℕ) (hr : r ≤ m) : r * (e / m) ≤ e := by
  calc
    r * (e / m) ≤ m * (e / m) := Nat.mul_le_mul_right _ hr
    _ ≤ e := Nat.mul_div_le e m

/-- Once a node is nonleaf, the proper-rank child is strictly smaller. -/
theorem child_lt (m r e : ℕ) (hm : 0 < m) (hr : r < m) (he : m ≤ e) :
    r * (e / m) < e := by
  have hq : 0 < e / m := Nat.div_pos he hm
  exact lt_of_lt_of_le (Nat.mul_lt_mul_of_pos_right hr hq) (Nat.mul_div_le e m)

/-- A short tail contains no complete field. -/
theorem child_eq_zero_of_lt (m r e : ℕ) (he : e < m) : r * (e / m) = 0 := by
  simp [Nat.div_eq_of_lt he]

/-- The fixed nonchild charge may be absorbed because a nonleaf has q>=1. -/
theorem quotient_budget (m r e C s E : ℕ) (hm : 0 < m) (he : m ≤ e)
    (hbudget : C * r + s + E ≤ C * m) :
    C * (r * (e / m)) + s * (e / m) + E ≤ C * e := by
  have hq : 0 < e / m := Nat.div_pos he hm
  calc
    C * (r * (e / m)) + s * (e / m) + E ≤
        C * (r * (e / m)) + s * (e / m) + E * (e / m) := by
      exact Nat.add_le_add_left (Nat.le_mul_of_pos_right E hq) _
    _ = (C * r + s + E) * (e / m) := by ring
    _ ≤ (C * m) * (e / m) := Nat.mul_le_mul_right _ hbudget
    _ = C * (m * (e / m)) := by ring
    _ ≤ C * e := Nat.mul_le_mul_left _ (Nat.mul_div_le e m)

/-- The active-depth theorem allows arbitrary tails and any larger stopping rule. -/
theorem linear_bound_of_stopped_recursion (A r : ℕ → ℕ) (m stop C s E : ℕ)
    (hm : 0 < m) (hstop : m ≤ stop) (hr : ∀ e, r e < m)
    (hleaf : ∀ e, e < stop → A e ≤ C * e)
    (hstep : ∀ e, stop ≤ e → A e ≤ A (r e * (e / m)) + s * (e / m) + E)
    (hbudget : ∀ e, C * r e + s + E ≤ C * m) :
    ∀ e, A e ≤ C * e := by
  intro e
  induction e using Nat.strong_induction_on with
  | h e ih =>
    by_cases leaf : e < stop
    · exact hleaf e leaf
    have hnonleaf : stop ≤ e := Nat.le_of_not_gt leaf
    have he : m ≤ e := hstop.trans hnonleaf
    have hchild := ih (r e * (e / m)) (child_lt m (r e) e hm (hr e) he)
    calc
      A e ≤ A (r e * (e / m)) + s * (e / m) + E := hstep e hnonleaf
      _ ≤ C * (r e * (e / m)) + s * (e / m) + E := by omega
      _ ≤ C * e := quotient_budget m (r e) e C s E hm he (hbudget e)

/-- Every proper rank fits the standard linear common-exponent budget. -/
theorem standard_rank_budget (m r s E : ℕ) (hr : r < m) :
    2 * (s + E) * r + s + E ≤ 2 * (s + E) * m := by
  have h : r + 1 ≤ m := hr
  nlinarith

/-- Leaf 8e plus the exact active-child recurrence implies a linear 2Be bound. -/
theorem exact_grid_linear_bound (A r : ℕ → ℕ) (m stop s E : ℕ)
    (hm : 0 < m) (hstop : m ≤ stop) (hr : ∀ e, r e < m) (hB : 8 ≤ s + E)
    (hleaf : ∀ e, e < stop → A e ≤ 8 * e)
    (hstep : ∀ e, stop ≤ e → A e ≤ A (r e * (e / m)) + s * (e / m) + E) :
    ∀ e, A e ≤ 2 * (s + E) * e := by
  apply linear_bound_of_stopped_recursion A r m stop (2 * (s + E)) s E hm hstop hr
  · intro e he
    exact (hleaf e he).trans (Nat.mul_le_mul_right e (by omega))
  · exact hstep
  · intro e
    exact standard_rank_budget m (r e) s E (hr e)

/-- Finite partitions add linear excess only on their actual selected axes. -/
theorem partition_linear_bound {ι : Type*} (I : Finset ι) (A size : ι → ℕ)
    (C d : ℕ) (hA : ∀ i ∈ I, A i ≤ C * size i)
    (hsize : ∑ i ∈ I, size i ≤ d) : ∑ i ∈ I, A i ≤ C * d := by
  calc
    ∑ i ∈ I, A i ≤ ∑ i ∈ I, C * size i := Finset.sum_le_sum hA
    _ = C * ∑ i ∈ I, size i := by rw [Finset.mul_sum]
    _ ≤ C * d := Nat.mul_le_mul_left C hsize

/-- Outer phases and preprocessing are charged after the finite partition. -/
theorem layer_excess_bound {ι : Type*} (I : Finset ι) (A size : ι → ℕ)
    (B d outer : ℕ) (hA : ∀ i ∈ I, A i ≤ 2 * B * size i)
    (hsize : ∑ i ∈ I, size i ≤ d) :
    (∑ i ∈ I, A i) + outer * d ≤ (2 * B + outer) * d := by
  have h := partition_linear_bound I A size (2 * B) d hA hsize
  nlinarith

/-- The traditional C0 reserve dominates the linear exact-grid coefficient. -/
theorem standard_C0_guard (m B : ℕ) (hm : 1 ≤ m) (hB : 8 ≤ B) :
    2 * B + 18 < 32 * m * B ^ 2 := by
  have hb : B ≤ B ^ 2 := by nlinarith
  have hmB := Nat.mul_le_mul_right (B ^ 2) hm
  nlinarith

/-- A strict coefficient reserve remains strict for every positive dimension. -/
theorem common_grid_sufficient (excess C C0 d : ℕ) (hexcess : excess ≤ C * d)
    (hC : C < C0) (hd : 0 < d) : excess < C0 * d := by
  exact lt_of_le_of_lt hexcess (Nat.mul_lt_mul_of_pos_right hC hd)

/-- Repeated active-child descent, kept separate from sibling work. -/
def descent (child : ℕ → ℕ) (e : ℕ) : ℕ → ℕ
  | 0 => e
  | n + 1 => child (descent child e n)

/-- Any strictly decreasing positive active width reaches zero in at most e steps. -/
theorem descent_le_sub (child : ℕ → ℕ) (hzero : child 0 = 0)
    (hdecrease : ∀ x, 0 < x → child x < x) (e n : ℕ) :
    descent child e n ≤ e - n := by
  induction n with
  | zero => simp [descent]
  | succ n ih =>
    simp only [descent]
    by_cases hz : descent child e n = 0
    · simp [hz, hzero]
    · have h := hdecrease (descent child e n) (by omega)
      omega

/-- A coarse but unconditional finite-depth certificate. -/
theorem descent_terminates (child : ℕ → ℕ) (hzero : child 0 = 0)
    (hdecrease : ∀ x, 0 < x → child x < x) (e : ℕ) :
    descent child e e = 0 := by
  have h := descent_le_sub child hzero hdecrease e e
  omega

/-- The floor-rank child shrinks geometrically without requiring divisible widths. -/
theorem descent_scaled_bound (m r e n : ℕ) :
    m ^ n * descent (fun x => r * (x / m)) e n ≤ r ^ n * e := by
  induction n with
  | zero => simp [descent]
  | succ n ih =>
    simp only [descent, pow_succ]
    have h := Nat.mul_div_le (descent (fun x => r * (x / m)) e n) m
    have h1 := Nat.mul_le_mul_left (m ^ n * r) h
    have h2 := Nat.mul_le_mul_left r ih
    nlinarith

/-- An explicit geometric inequality is sufficient to stop the recursion. -/
theorem descent_eq_zero_of_scaled_lt (m r e n : ℕ)
    (hstop : r ^ n * e < m ^ n) :
    descent (fun x => r * (x / m)) e n = 0 := by
  have h := descent_scaled_bound m r e n
  by_contra hn
  have hp : 1 ≤ descent (fun x => r * (x / m)) e n := by omega
  have hmul := Nat.mul_le_mul_left (m ^ n) hp
  nlinarith

/-- The affine improvement used by stopped exponent bootstraps. -/
def bootstrap (s a : ℝ) : ℕ → ℝ
  | 0 => a
  | n + 1 => (1 - s) * s + s * bootstrap s a n

/-- Closed form for the remaining gap, valid for every real s and initial a. -/
theorem bootstrap_gap (s a : ℝ) (n : ℕ) :
    s - bootstrap s a n = s ^ n * (s - a) := by
  induction n with
  | zero => simp [bootstrap]
  | succ n ih =>
    simp only [bootstrap, pow_succ]
    calc
      s - ((1 - s) * s + s * bootstrap s a n) = s * (s - bootstrap s a n) := by ring
      _ = s * (s ^ n * (s - a)) := by rw [ih]
      _ = s ^ n * s * (s - a) := by ring

/-- The bootstrap never crosses its fixed point. -/
theorem bootstrap_le (s a : ℝ) (hs : 0 ≤ s) (ha : a ≤ s) (n : ℕ) :
    bootstrap s a n ≤ s := by
  have h := mul_nonneg (pow_nonneg hs n) (sub_nonneg.mpr ha)
  rw [← bootstrap_gap] at h
  linarith

/-- Strictly positive contraction leaves strictly positive headroom. -/
theorem bootstrap_lt (s a : ℝ) (hs : 0 < s) (ha : a < s) (n : ℕ) :
    bootstrap s a n < s := by
  have h := mul_pos (pow_pos hs n) (sub_pos.mpr ha)
  rw [← bootstrap_gap] at h
  linarith

/-- Each positive-gap bootstrap stage makes strict progress when 0<s<1. -/
theorem bootstrap_strict_progress (s a : ℝ) (hs : 0 < s) (hs1 : s < 1)
    (ha : a < s) (n : ℕ) : bootstrap s a n < bootstrap s a (n + 1) := by
  have hgap := bootstrap_lt s a hs ha n
  have hpos := mul_pos (sub_pos.mpr hs1) (sub_pos.mpr hgap)
  simp only [bootstrap]
  nlinarith

/-- A checked power bound is a sufficient finite-stage target certificate. -/
theorem bootstrap_target_of_power_bound (s a target : ℝ) (n : ℕ)
    (hbound : s ^ n * (s - a) ≤ s - target) : target ≤ bootstrap s a n := by
  rw [← bootstrap_gap] at hbound
  linarith

/-- Every target below the fixed point is reached in finitely many stages. -/
theorem bootstrap_eventually_above (s a target : ℝ)
    (_hs : 0 ≤ s) (hs1 : s < 1) (ha : a < s) (htarget : target < s) :
    ∃ n : ℕ, target < bootstrap s a n := by
  obtain ⟨n, hn⟩ := exists_pow_lt_of_lt_one
    (div_pos (sub_pos.mpr htarget) (sub_pos.mpr ha)) hs1
  refine ⟨n, ?_⟩
  have hmul := (mul_lt_mul_of_pos_right hn (sub_pos.mpr ha))
  have hden : s - a ≠ 0 := ne_of_gt (sub_pos.mpr ha)
  rw [div_mul_cancel₀ _ hden] at hmul
  rw [← bootstrap_gap] at hmul
  linarith


/-- Nonnegative input exponents remain nonnegative under a valid bootstrap. -/
theorem bootstrap_nonnegative (s a : ℝ) (hs : 0 ≤ s) (hs1 : s ≤ 1)
    (ha : 0 ≤ a) (n : ℕ) : 0 ≤ bootstrap s a n := by
  induction n with
  | zero => exact ha
  | succ n ih =>
    exact add_nonneg (mul_nonneg (sub_nonneg.mpr hs1) hs) (mul_nonneg hs ih)

/-- Arbitrarily many extra bootstrap stages preserve all established savings. -/
theorem bootstrap_monotone (s a : ℝ) (hs : 0 ≤ s) (hs1 : s ≤ 1) (ha : a ≤ s) :
    Monotone (bootstrap s a) := by
  apply monotone_nat_of_le_succ
  intro n
  have hgap := bootstrap_le s a hs ha n
  have h := mul_nonneg (sub_nonneg.mpr hs1) (sub_nonneg.mpr hgap)
  simp only [bootstrap]
  nlinarith

/-- A finite target witness remains valid at every later stage. -/
theorem bootstrap_eventually_always_above (s a target : ℝ)
    (hs : 0 ≤ s) (hs1 : s < 1) (ha : a < s) (htarget : target < s) :
    ∃ N : ℕ, ∀ n, N ≤ n → target < bootstrap s a n := by
  obtain ⟨N, hN⟩ := bootstrap_eventually_above s a target hs hs1 ha htarget
  refine ⟨N, fun n hn => ?_⟩
  exact hN.trans_le (bootstrap_monotone s a hs hs1.le ha.le hn)

end IntegerMultBounds.Recursion
