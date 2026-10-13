import FloorDepth
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-! The exact floor recurrence has a uniform power bound without any
monotonicity hypothesis on its cost function. The physical recurrence remains
an explicit contract. Constants below are constructed from a finite base sum.
-/
namespace FloorRecurrence
open scoped BigOperators

theorem floor_child_le_ratio (m t e : ℕ) (hm : 0 < m) :
    (FloorDepth.child m t e : ℝ) ≤ ((t : ℝ) / m) * e := by
  have hf : ((e / m : ℕ) : ℝ) * m ≤ e := by exact_mod_cast Nat.div_mul_le_self e m
  have hmR : (0 : ℝ) < m := by exact_mod_cast hm
  have hdiv : ((e / m : ℕ) : ℝ) ≤ (e : ℝ) / m := (le_div_iff₀ hmR).mpr hf
  have h := mul_le_mul_of_nonneg_left hdiv (Nat.cast_nonneg t : (0 : ℝ) ≤ t)
  simpa only [FloorDepth.child, Nat.cast_mul, div_mul_eq_mul_div, mul_div_assoc] using h

theorem floor_child_power (m t e : ℕ) (p : ℝ) (hm : 0 < m) (hp : 0 ≤ p) :
    (FloorDepth.child m t e : ℝ) ^ p ≤ ((t : ℝ) / m) ^ p * (e : ℝ) ^ p := by
  have h := Real.rpow_le_rpow (Nat.cast_nonneg _) (floor_child_le_ratio m t e hm) hp
  simpa only [Real.mul_rpow (div_nonneg (Nat.cast_nonneg t) (Nat.cast_nonneg m))
    (Nat.cast_nonneg e)] using h

theorem one_le_width_power (e : ℕ) (p : ℝ) (he : 0 < e) (hp : 0 ≤ p) :
    1 ≤ (e : ℝ) ^ p := by
  have heR : (1 : ℝ) ≤ e := by exact_mod_cast he
  simpa using Real.rpow_le_rpow (by norm_num : (0 : ℝ) ≤ 1) heR hp

/-- Strict finite moment contraction pays constant node overhead at every
integer width. Children are literally t*(e/m), not ceil(t*e/m). -/
theorem all_width_bound {ι : Type} (rows : List ι) (c : ι → ℝ) (t : ι → ℕ)
    (m : ℕ) (f : ℕ → ℝ) (p A C γ : ℝ)
    (hm : 0 < m) (hp : 0 ≤ p) (hA : 0 ≤ A)
    (hc : ∀ i ∈ rows, 0 ≤ c i) (ht : ∀ i ∈ rows, 0 < t i)
    (htm : ∀ i ∈ rows, t i < m)
    (hγ : γ = (rows.map (fun i => c i * ((t i : ℝ) / m) ^ p)).sum)
    (hγ1 : γ < 1) (overhead : C ≤ A * (1 - γ))
    (base : ∀ e, 0 < e → e < m → f e ≤ A * (e : ℝ) ^ p)
    (physical_recurrence : ∀ e, m ≤ e →
      f e ≤ C + (rows.map (fun i => c i * f (t i * (e / m)))).sum) :
    ∀ e, 0 < e → f e ≤ A * (e : ℝ) ^ p := by
  intro e
  induction e using Nat.strong_induction_on with
  | h e ih =>
    intro he
    by_cases hbase : e < m
    · exact base e he hbase
    · have hem : m ≤ e := Nat.le_of_not_gt hbase
      have hrow : ∀ i ∈ rows, c i * f (t i * (e / m)) ≤
          c i * (A * (((t i : ℝ) / m) ^ p * (e : ℝ) ^ p)) := by
        intro i hi
        have hchild := ih (FloorDepth.child m (t i) e)
          (FloorDepth.child_lt m (t i) e (htm i hi) hem)
          (FloorDepth.child_pos m (t i) e hm (ht i hi) hem)
        exact mul_le_mul_of_nonneg_left
          (hchild.trans (mul_le_mul_of_nonneg_left (floor_child_power m (t i) e p hm hp) hA))
          (hc i hi)
      have hsum : (rows.map (fun i => c i * (A * (((t i : ℝ) / m) ^ p * (e : ℝ) ^ p)))).sum =
          A * γ * (e : ℝ) ^ p := by
        calc
          _ = (rows.map (fun i => (c i * ((t i : ℝ) / m) ^ p) * (A * (e : ℝ) ^ p))).sum := by
            congr 1
            apply List.map_congr_left
            intro i hi
            ring
          _ = γ * (A * (e : ℝ) ^ p) := by rw [List.sum_map_mul_right, ← hγ]
          _ = _ := by ring
      have hgap : 0 ≤ A * (1 - γ) := mul_nonneg hA (by linarith)
      have hpaid : C ≤ A * (1 - γ) * (e : ℝ) ^ p :=
        overhead.trans (by simpa using mul_le_mul_of_nonneg_left (one_le_width_power e p he hp) hgap)
      calc
        f e ≤ C + (rows.map (fun i => c i * f (t i * (e / m)))).sum := physical_recurrence e hem
        _ ≤ C + (rows.map (fun i => c i * (A * (((t i : ℝ) / m) ^ p * (e : ℝ) ^ p)))).sum :=
          add_le_add_left (List.sum_le_sum hrow) C
        _ = C + A * γ * (e : ℝ) ^ p := by rw [hsum]
        _ ≤ A * (e : ℝ) ^ p := by nlinarith [hpaid]

/-- A concrete uniform constant using only the finitely many base values. -/
noncomputable def boundConstant (m : ℕ) (f : ℕ → ℝ) (C γ : ℝ) : ℝ :=
  (∑ e ∈ Finset.range m, |f e|) + |C| / (1 - γ)

theorem boundConstant_nonneg (m : ℕ) (f : ℕ → ℝ) (C γ : ℝ) (hγ : γ < 1) :
    0 ≤ boundConstant m f C γ := by
  unfold boundConstant
  exact add_nonneg (Finset.sum_nonneg (fun _ _ => abs_nonneg _))
    (div_nonneg (abs_nonneg _) (by linarith))

theorem boundConstant_overhead (m : ℕ) (f : ℕ → ℝ) (C γ : ℝ) (hγ : γ < 1) :
    C ≤ boundConstant m f C γ * (1 - γ) := by
  have hgap : 0 < 1 - γ := by linarith
  have hsum : 0 ≤ ∑ e ∈ Finset.range m, |f e| :=
    Finset.sum_nonneg (fun _ _ => abs_nonneg _)
  have hle : |C| / (1 - γ) ≤ boundConstant m f C γ := by unfold boundConstant; linarith
  have h := mul_le_mul_of_nonneg_right hle hgap.le
  rw [div_mul_cancel₀ _ hgap.ne'] at h
  exact (le_abs_self C).trans h

theorem boundConstant_base (m : ℕ) (f : ℕ → ℝ) (C γ p : ℝ)
    (hγ : γ < 1) (hp : 0 ≤ p) (e : ℕ) (he : 0 < e) (hem : e < m) :
    f e ≤ boundConstant m f C γ * (e : ℝ) ^ p := by
  have hsum : |f e| ≤ ∑ k ∈ Finset.range m, |f k| :=
    Finset.single_le_sum (fun k (_ : k ∈ Finset.range m) => abs_nonneg (f k))
      (Finset.mem_range.mpr hem)
  have hquot : 0 ≤ |C| / (1 - γ) := div_nonneg (abs_nonneg _) (by linarith)
  have hbase : f e ≤ boundConstant m f C γ := by
    unfold boundConstant
    linarith [le_abs_self (f e)]
  exact hbase.trans (by
    simpa using mul_le_mul_of_nonneg_left
      (one_le_width_power e p he hp) (boundConstant_nonneg m f C γ hγ))

/-- No base-growth hypothesis is needed: a fixed finite base is absorbed by
the explicit boundConstant. The sole cost premise is the physical recurrence. -/
theorem finite_base_all_width {ι : Type} (rows : List ι) (c : ι → ℝ) (t : ι → ℕ)
    (m : ℕ) (f : ℕ → ℝ) (p C γ : ℝ)
    (hm : 0 < m) (hp : 0 ≤ p)
    (hc : ∀ i ∈ rows, 0 ≤ c i) (ht : ∀ i ∈ rows, 0 < t i)
    (htm : ∀ i ∈ rows, t i < m)
    (hγ : γ = (rows.map (fun i => c i * ((t i : ℝ) / m) ^ p)).sum) (hγ1 : γ < 1)
    (physical_recurrence : ∀ e, m ≤ e →
      f e ≤ C + (rows.map (fun i => c i * f (t i * (e / m)))).sum) :
    ∀ e, 0 < e → f e ≤ boundConstant m f C γ * (e : ℝ) ^ p :=
  all_width_bound rows c t m f p (boundConstant m f C γ) C γ hm hp
    (boundConstant_nonneg m f C γ hγ1) hc ht htm hγ hγ1
    (boundConstant_overhead m f C γ hγ1)
    (boundConstant_base m f C γ p hγ1 hp) physical_recurrence

/-- The executable floor-depth has an explicit logarithmic upper bound.
This bound concerns recursion depth, not tape-machine cost. -/
theorem depth_log_bound (m t : ℕ) (ht : t < m) (ht0 : 0 < t) :
    ∀ e, 0 < e → (FloorDepth.depth m t ht e : ℝ) ≤
      1 + Real.log (e : ℝ) / Real.log ((m : ℝ) / t) := by
  have hm : 0 < m := Nat.zero_lt_of_lt ht
  have htR : (0 : ℝ) < t := by exact_mod_cast ht0
  have hmR : (0 : ℝ) < m := by exact_mod_cast hm
  have hratio : 1 < (m : ℝ) / t := (one_lt_div htR).mpr (by exact_mod_cast ht)
  have hlog : 0 < Real.log ((m : ℝ) / t) := Real.log_pos hratio
  intro e
  induction e using Nat.strong_induction_on with
  | h e ih =>
    intro he
    have heR : (0 : ℝ) < e := by exact_mod_cast he
    by_cases hb : e < m
    · rw [FloorDepth.depth_base m t ht e hb]
      have hlogE : 0 ≤ Real.log (e : ℝ) := Real.log_nonneg (by exact_mod_cast he)
      have hnonneg := div_nonneg hlogE hlog.le
      norm_num only [Nat.cast_zero]
      linarith
    · have hem : m ≤ e := Nat.le_of_not_gt hb
      have hc0 := FloorDepth.child_pos m t e hm ht0 hem
      have hcR : (0 : ℝ) < FloorDepth.child m t e := by exact_mod_cast hc0
      have ihc := ih (FloorDepth.child m t e) (FloorDepth.child_lt m t e ht hem) hc0
      have hl : Real.log (FloorDepth.child m t e : ℝ) ≤
          Real.log (e : ℝ) - Real.log ((m : ℝ) / t) := by
        have hmono := Real.log_le_log hcR (floor_child_le_ratio m t e hm)
        rw [Real.log_mul (div_pos htR hmR).ne' heR.ne',
          Real.log_div htR.ne' hmR.ne'] at hmono
        rw [Real.log_div hmR.ne' htR.ne']
        linarith
      have hd := (div_le_div_iff_of_pos_right hlog).mpr hl
      rw [sub_div, div_self hlog.ne'] at hd
      rw [FloorDepth.depth_step m t ht e hem, Nat.cast_add, Nat.cast_one]
      linarith

end FloorRecurrence

#print axioms FloorRecurrence.floor_child_le_ratio
#print axioms FloorRecurrence.floor_child_power
#print axioms FloorRecurrence.one_le_width_power
#print axioms FloorRecurrence.all_width_bound
#print axioms FloorRecurrence.boundConstant_nonneg
#print axioms FloorRecurrence.boundConstant_overhead
#print axioms FloorRecurrence.boundConstant_base
#print axioms FloorRecurrence.finite_base_all_width
#print axioms FloorRecurrence.depth_log_bound
