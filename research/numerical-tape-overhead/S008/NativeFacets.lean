import S008.PiecewiseHistory

/-! A finite numerical validator for the native R=240 switches. -/
namespace S008.Piecewise.Facets

structure Line where
  intercept : ℚ
  slope : ℚ

def value (l : Line) (x : ℝ) : ℝ := l.intercept + l.slope*x

inductive Profile
  | last (l : Line)
  | step (l : Line) (edge : ℕ) (tail : Profile)

def first : Profile → Line
  | .last l | .step l _ _ => l

def before (e : ℕ) : Profile → Bool
  | .last _ => true
  | .step _ k _ => decide (e ≤ k)

def valid : Profile → Bool
  | .last _ => true
  | .step l e tail => decide ((first tail).slope ≤ l.slope) &&
      decide (l.intercept+l.slope*e = (first tail).intercept+(first tail).slope*e) &&
      before e tail && valid tail

noncomputable def lower : Profile → ℝ → ℝ
  | .last l, x => value l x
  | .step l _ tail, x => min (value l x) (lower tail x)

noncomputable def scheduled : Profile → ℝ → ℝ
  | .last l, x => value l x
  | .step l e tail, x => if x ≤ (e:ℝ) then value l x else scheduled tail x

private theorem first_le (p : Profile) (x : ℝ) : lower p x ≤ value (first p) x := by
  cases p with
  | last _ => exact le_rfl
  | step _ _ _ => exact min_le_left _ _

private theorem early_eq (p : Profile) {x : ℝ} {e : ℕ}
    (h : before e p = true) (hx : x ≤ (e:ℝ)) : scheduled p x = value (first p) x := by
  cases p with
  | last _ => rfl
  | step l k tail =>
    have hk : e ≤ k := of_decide_eq_true h
    exact ite_eq_left (hx.trans (show (e:ℝ) ≤ (k:ℝ) by exact_mod_cast hk))

private theorem cross (u v : Line) (e : ℕ) (hs : v.slope ≤ u.slope)
    (hj : u.intercept+u.slope*e = v.intercept+v.slope*e) (x : ℝ) :
    (x ≤ (e:ℝ) → value u x ≤ value v x) ∧ ((e:ℝ) ≤ x → value v x ≤ value u x) := by
  have hsr : (v.slope:ℝ) ≤ (u.slope:ℝ) := by exact_mod_cast hs
  have hjr : (u.intercept:ℝ)+u.slope*(e:ℝ) = (v.intercept:ℝ)+v.slope*(e:ℝ) := by
    exact_mod_cast hj
  unfold value
  constructor <;> intro hx
  · nlinarith only [hjr,mul_nonneg (sub_nonneg.mpr hsr) (sub_nonneg.mpr hx)]
  · nlinarith only [hjr,mul_nonneg (sub_nonneg.mpr hsr) (sub_nonneg.mpr hx)]

/-- Adjacent intersections and sorted slopes suffice to identify the minimum
    of all facets with the executed piecewise selection throughout the line. -/
theorem exact_schedule (p : Profile) (h : valid p = true) (x : ℝ) :
    lower p x = scheduled p x := by
  induction p with
  | last _ => rfl
  | step l e tail ih =>
    simp only [valid,Bool.and_eq_true,decide_eq_true_eq] at h
    obtain ⟨⟨⟨hs,hj⟩,hb⟩,ht⟩ := h
    have hcross := cross l (first tail) e hs hj x
    unfold lower scheduled
    by_cases hx : x ≤ (e:ℝ)
    · rw [ite_eq_left hx,ih ht,early_eq tail hb hx,min_eq_left (hcross.1 hx)]
    · rw [ite_eq_right hx,min_eq_right ((first_le tail x).trans (hcross.2 (le_of_not_ge hx))),ih ht]


end S008.Piecewise.Facets
