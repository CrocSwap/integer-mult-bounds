import S008.LabelSharp
import S008.NativeFacets

namespace S008.Piecewise.LabelSchedule

open S008.NumericalCutoff S008.Piecewise S008.Piecewise.Facets
open S008.Recount.TrueLabel (corners den)
open S008.Piecewise.LabelSimple (upper)

private def heights : ℕ → ℕ → ℕ → List (ℕ×ℕ) → List (ℕ×ℕ)
  | _,_,_,[] => []
  | p,s,h,(v,t)::es =>
    let h' := h + (v-p)*s
    (v,h')::heights v t h' es

private def lineFromData (row : (ℕ × ℕ) × (ℕ × ℕ)) : ℕ × Line :=
  let edge := row.1.1
  let weight := row.1.2
  let height := row.2.2
  (edge, ⟨((height:ℚ)-(edge:ℚ)*weight)/(den:ℚ), (weight:ℚ)/den⟩)

private def measured : List (ℕ × Line) → Profile
  | [] => .last ⟨0,0⟩
  | [(_, l)] => .last l
  | (_, l)::(e,m)::rows => .step l e (measured ((e,m)::rows))

/-- The exact 29 published height/weight rows, extended by the last slope. -/
def measured29 : Profile := measured ((corners.zip (heights 0 0 0 corners)).map lineFromData)

theorem measured29_valid : valid measured29 = true := by decide +kernel

private def coefficients : Profile → List (ℚ × ℚ)
  | .last l => [(l.intercept, l.slope)]
  | .step l _ rest => (l.intercept,l.slope)::coefficients rest

private theorem lower_at_coefficient (p : Profile) (c s : ℚ)
    (h : (c,s) ∈ coefficients p) (x : ℝ) : lower p x ≤ (c:ℝ)+(s:ℝ)*x := by
  induction p with
  | last l =>
    have he : (c,s)=(l.intercept,l.slope) := by simpa [coefficients] using h
    have hc := congrArg Prod.fst he
    have hs := congrArg Prod.snd he
    change c=l.intercept at hc
    change s=l.slope at hs
    rw [hc,hs]
    exact le_refl _
  | step l e rest ih =>
    simp only [coefficients,List.mem_cons] at h
    rcases h with he | hr
    · have hc := congrArg Prod.fst he
      have hs := congrArg Prod.snd he
      change c=l.intercept at hc
      change s=l.slope at hs
      rw [hc,hs]
      exact min_le_left _ _
    · exact (min_le_right _ _).trans (ih hr)

/-- All six supporting affine continuations are present among the 29
    actual label rows, as are their intersections and numerical weights. -/
theorem measured29_upper (x : ℝ) : scheduled measured29 x ≤ upper x := by
  rw [← exact_schedule measured29 measured29_valid]
  have h0 := lower_at_coefficient measured29 (3719981558627835295593/20231066240) (269/167936) (by decide +kernel) x
  have h1 := lower_at_coefficient measured29 (8376764989540855006311/40462132480) (515/335872) (by decide +kernel) x
  have h2 := lower_at_coefficient measured29 (13991522341751541275193/20231066240) (39/45056) (by decide +kernel) x
  have h3 := lower_at_coefficient measured29 (3986646779673101455767/5057766560) (9/11264) (by decide +kernel) x
  have h4 := lower_at_coefficient measured29 (35803303791265894152411/40462132480) (69/90112) (by decide +kernel) x
  have h5 := lower_at_coefficient measured29 (2814186109995531152000271/950860113280) (83/192512) (by decide +kernel) x
  norm_num at h0 h1 h2 h3 h4 h5
  exact le_min h0 (le_min h1 (le_min h2 (le_min h3 (le_min h4 h5))))

private theorem history_input {H J : ℕ → ℝ} (hle : ∀ j, H j ≤ J j) (x : ℕ) :
    history H x ≤ history J x := by
  induction x with
  | zero => exact max_le_max (le_refl _) (sub_le_sub_right (hle 0) _)
  | succ x ih => exact max_le_max ih (sub_le_sub_right (hle (x+1)) _)

/-- The concrete 29 source rows directly feed the kernel-checked integer
    endpoint including the rounded global address width. -/
theorem schedule_natural_clock (n cost : ℝ) (a : ℕ)
    (hn : (2:ℝ)^((2:ℝ)^(7519517465920988:ℝ)) ≤ n) (ha : (activeLog a:ℝ) ≤ logTwo (logTwo n)+2)
    (hcost : cost ≤ n*Real.sqrt (logTwo n)*(2:ℝ)^(182+4*logTwo (logTwo (logTwo n)+2)+
        envelope (fun j => scheduled measured29 (j:ℝ)) (activeLog a))) :
    cost ≤ n*(Real.log n)^(501/1000:ℝ) := by
  have hn0 : 0 ≤ n := le_trans (Real.rpow_nonneg (by norm_num) _) hn
  have hh := history_input (H:=fun j => scheduled measured29 (j:ℝ)) (J:=fun j => upper (j:ℝ))
    (fun j => measured29_upper (j:ℝ)) (activeLog a)
  have he : envelope (fun j => scheduled measured29 (j:ℝ)) (activeLog a) ≤
      envelope (fun j => upper (j:ℝ)) (activeLog a) := add_le_add (le_refl _) hh
  apply S008.Piecewise.LabelSharp.natural_clock n cost a hn ha
  exact hcost.trans (mul_le_mul_of_nonneg_left (Real.rpow_le_rpow_of_exponent_le (by norm_num)
    (add_le_add (le_refl _) he)) (mul_nonneg hn0 (Real.sqrt_nonneg _)))

end S008.Piecewise.LabelSchedule
