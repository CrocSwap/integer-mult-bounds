import TrialFunding
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

namespace CarrierTrial
open DyadicRoot

noncomputable def realPower (c : Claim) : ℝ := (c.rank:ℝ)^((c.num:ℝ)/c.den)

theorem real_enclosing (c : Claim) (h : c ∈ claims) :
    (c.lo:ℝ)/grid ≤ realPower c ∧ realPower c ≤ (c.hi:ℝ)/grid := by
  obtain ⟨hd,hlo,hhi⟩ := enclosing c h
  have hdn : (c.den:ℝ) ≠ 0 := by exact_mod_cast hd.ne'
  have hg : (0:ℝ)<grid := by norm_num [grid]
  have hr : 0≤realPower c := Real.rpow_nonneg (Nat.cast_nonneg _) _
  have heq : (realPower c)^c.den = (c.rank:ℝ)^c.num := by
    rw [realPower,←Real.rpow_natCast _ c.den,← Real.rpow_mul (Nat.cast_nonneg _),
      div_mul_cancel₀ _ hdn,Real.rpow_natCast]
  have hp : (2:ℕ)^(160*c.den) = grid^c.den := Nat.pow_mul _ _ _
  rw [hp] at hlo hhi
  constructor
  · apply (pow_le_pow_iff_left₀ (div_nonneg (Nat.cast_nonneg _) hg.le) hr hd.ne').mp
    rw [div_pow,heq,div_le_iff₀ (pow_pos hg _)]
    exact_mod_cast hlo
  · apply (pow_le_pow_iff_left₀ hr (div_nonneg (Nat.cast_nonneg _) hg.le) hd.ne').mp
    rw [heq,div_pow,le_div_iff₀ (pow_pos hg _)]
    exact_mod_cast hhi

def low (xs : List Row) (w : Row → ℕ) := (xs.map fun r ↦ w r*r.power.lo).sum
def high (xs : List Row) (w : Row → ℕ) := (xs.map fun r ↦ w r*r.power.hi).sum

noncomputable def actual (xs : List Row) (w : Row → ℕ) : ℝ :=
  (xs.map fun r ↦ (w r:ℝ)*realPower r.power).sum

theorem census_enclosure (xs : List Row) (w : Row→ℕ) (source : ∀ r ∈ xs, r.power∈claims) :
    (low xs w:ℝ)/grid ≤ actual xs w ∧ actual xs w ≤ (high xs w:ℝ)/grid := by
  induction xs with
  | nil => simp [low,high,actual]
  | cons r rs ih =>
    obtain ⟨hl,hu⟩ := real_enclosing r.power (source r (by simp))
    obtain ⟨ht,hs⟩ := ih (fun s h ↦ source s (by simp [h]))
    have hlo := mul_le_mul_of_nonneg_left hl (Nat.cast_nonneg (w r))
    have hhi := mul_le_mul_of_nonneg_left hu (Nat.cast_nonneg (w r))
    simp only [low,high,actual,List.map_cons,List.sum_cons,Nat.cast_add,Nat.cast_mul,add_div,mul_div_assoc] at *
    exact ⟨add_le_add hlo ht,add_le_add hhi hs⟩

theorem lift_actual : actual lift Row.paid < actual lift Row.target := by
  have h (r) (hr : r∈lift) : r.power ∈ claims := by
    simp [claims]
    exact Or.inr (Or.inr (Or.inr (Or.inl ⟨r,hr,rfl⟩)))
  have u := (census_enclosure lift Row.paid h).2
  have l := (census_enclosure lift Row.target h).1
  apply u.trans_lt (LT.lt.trans_le _ l)
  apply (div_lt_div_iff_of_pos_right (show (0:ℝ)<grid by norm_num [grid])).mpr
  exact_mod_cast static_prices.2.2.2

theorem integer_ratios :
    10^10*upP main < (10^10-88)*lowT main ∧
    1000*(upP split*grid) < 947*(lowT main*splitScale.lo) ∧
    1000*(upT prune*floorScale.hi) < 949*(lowT main*grid) ∧ 0<lowT main ∧ 0<splitScale.lo :=
  by decide +kernel

theorem actual_margins :
    actual main Row.paid < (1-88/(10^10:ℝ))*actual main Row.target ∧
    actual split Row.paid < (947/1000:ℝ)*realPower splitScale*actual main Row.target ∧
    actual prune Row.target*realPower floorScale < (949/1000:ℝ)*actual main Row.target ∧
    0<actual main Row.target ∧ 0<realPower splitScale := by
  let showIn (r : Row) (h : r ∈ main++split++prune++lift) : r.power∈claims :=
    List.mem_append_left _ (List.mem_map.mpr ⟨r,h,rfl⟩)
  have hm (r) (h : r∈main) := showIn r (by simp [h])
  have hs (r) (h : r∈split) := showIn r (by simp [h])
  have hp (r) (h : r∈prune) := showIn r (by simp [h])
  have hg : (0:ℝ)<grid := by norm_num [grid]
  have ht : (lowT main:ℝ)/grid ≤ actual main Row.target := (census_enclosure main Row.target hm).1
  have hb₀ : actual main Row.paid ≤ (upP main:ℝ)/grid := (census_enclosure main Row.paid hm).2
  have hb₁ : actual split Row.paid ≤ (upP split:ℝ)/grid := (census_enclosure split Row.paid hs).2
  have hb₂ : actual prune Row.target ≤ (upT prune:ℝ)/grid := (census_enclosure prune Row.target hp).2
  have hss := (real_enclosing splitScale (by simp [claims])).1
  have hff := (real_enclosing floorScale (by simp [claims])).2
  have f₀ : 0≤realPower floorScale := Real.rpow_nonneg (Nat.cast_nonneg _) _
  obtain ⟨q₀,q₁,q₂,q₃,q₄⟩ := integer_ratios
  have g₀ : actual main Row.paid < (1-88/(10^10:ℝ))*((lowT main:ℝ)/grid) := by
    apply hb₀.trans_lt
    have qa : 10000000000*upP main < 9999999912*lowT main := q₀
    have q₀' : (10000000000:ℝ)*(upP main:ℝ) < 9999999912*(lowT main:ℝ) := by exact_mod_cast qa
    field_simp
    linarith
  have g₁ : actual split Row.paid < (947/1000:ℝ)*((splitScale.lo:ℝ)/grid)*((lowT main:ℝ)/grid) := by
    apply hb₁.trans_lt
    have q₁' : (1000:ℝ)*((upP split:ℝ)*grid) < 947*((lowT main:ℝ)*splitScale.lo) := by exact_mod_cast q₁
    field_simp
    nlinarith
  have g₂ : (upT prune:ℝ)/grid*((floorScale.hi:ℝ)/grid) < (949/1000:ℝ)*((lowT main:ℝ)/grid) := by
    have q₂' : (1000:ℝ)*((upT prune:ℝ)*floorScale.hi) < 949*((lowT main:ℝ)*grid) := by exact_mod_cast q₂
    field_simp
    nlinarith
  have hpos : 0<(lowT main:ℝ)/grid := div_pos (by exact_mod_cast q₃) hg
  have hpos' : 0<(splitScale.lo:ℝ)/grid := div_pos (by exact_mod_cast q₄) hg
  refine ⟨g₀.trans_le (mul_le_mul_of_nonneg_left ht (by norm_num)),?_,?_,hpos.trans_le ht,hpos'.trans_le hss⟩
  · apply g₁.trans_le
    exact mul_le_mul (mul_le_mul_of_nonneg_left hss (by norm_num)) ht hpos.le
      (mul_nonneg (by norm_num) ((hpos'.trans_le hss).le))
  · exact ((mul_le_mul hb₂ hff f₀ (by positivity)).trans_lt g₂).trans_le
      (mul_le_mul_of_nonneg_left ht (by norm_num))

#print axioms actual_margins
#print axioms real_enclosing
#print axioms census_enclosure
#print axioms lift_actual
end CarrierTrial
