/-
HPCalc (lane LEANHP, Nov 20).  Real-analysis facts for the KASYM chord dual (cards/WILD/NOVEL/kasym/KA.md, section 2):
  g0 x = (8x+1)^s,  c a constant,  F_c(x) = (g0 x - c)/x.
  (anti)  F_c antitone on [x0,oo) as soon as M_c(x0) <= 0, M_c(x) = x g0'(x) - g0 x + c.
  (conv)  F_c convex on [2,oo) as soon as N_c(2) >= 0, N_c(x) = x^2 g0''(x) - 2 x g0'(x) + 2 (g0 x - c)   [N_c' = x^2 g0''' >= 0].
  (F1)    t -> (t+1)^s - t^s antitone on [0,oo).
Kernel only; no numerics here (they are in CallerHP.lean).
-/
import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Analysis.Convex.Deriv
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

namespace CallerHP
open Set

theorem anti_of_deriv {f f' : ℝ → ℝ} {a : ℝ} (hc : ContinuousOn f (Ici a))
    (hd : ∀ x, a < x → HasDerivAt f (f' x) x) (hn : ∀ x, a < x → f' x ≤ 0) :
    AntitoneOn f (Ici a) := by
  apply antitoneOn_of_deriv_nonpos (convex_Ici a) hc
  · intro x hx
    rw [interior_Ici] at hx
    exact (hd x hx).differentiableAt.differentiableWithinAt
  · intro x hx
    rw [interior_Ici] at hx
    rw [(hd x hx).deriv]
    exact hn x hx

theorem mono_of_deriv {f f' : ℝ → ℝ} {a : ℝ} (hc : ContinuousOn f (Ici a))
    (hd : ∀ x, a < x → HasDerivAt f (f' x) x) (hn : ∀ x, a < x → 0 ≤ f' x) :
    MonotoneOn f (Ici a) := by
  apply monotoneOn_of_deriv_nonneg (convex_Ici a) hc
  · intro x hx
    rw [interior_Ici] at hx
    exact (hd x hx).differentiableAt.differentiableWithinAt
  · intro x hx
    rw [interior_Ici] at hx
    rw [(hd x hx).deriv]
    exact hn x hx

theorem convex_of_deriv {f f' : ℝ → ℝ} {a : ℝ} (hc : ContinuousOn f (Ici a))
    (hd : ∀ x, a < x → HasDerivAt f (f' x) x) (hm : MonotoneOn f' (Ici a)) :
    ConvexOn ℝ (Ici a) f := by
  apply MonotoneOn.convexOn_of_deriv (convex_Ici a) hc
  · intro x hx
    rw [interior_Ici] at hx
    exact (hd x hx).differentiableAt.differentiableWithinAt
  · intro x hx y hy hxy
    rw [interior_Ici] at hx hy
    rw [(hd x hx).deriv, (hd y hy).deriv]
    exact hm (mem_Ici.mpr hx.le) (mem_Ici.mpr hy.le) hxy

theorem cont_of_deriv {f f' : ℝ → ℝ} {a : ℝ} (hd : ∀ x, a ≤ x → HasDerivAt f (f' x) x) :
    ContinuousOn f (Ici a) := fun x hx => (hd x hx).continuousAt.continuousWithinAt

section g
variable (σ : ℝ)

noncomputable def g0 (x : ℝ) : ℝ := (8 * x + 1) ^ σ
noncomputable def g1 (x : ℝ) : ℝ := 8 * σ * (8 * x + 1) ^ (σ - 1)
noncomputable def g2 (x : ℝ) : ℝ := 8 * σ * (8 * (σ - 1) * (8 * x + 1) ^ (σ - 1 - 1))
noncomputable def g3 (x : ℝ) : ℝ :=
  8 * σ * (8 * (σ - 1) * (8 * (σ - 1 - 1) * (8 * x + 1) ^ (σ - 1 - 1 - 1)))

theorem aff_deriv (x : ℝ) : HasDerivAt (fun y : ℝ => 8 * y + 1) 8 x := by
  simpa using ((hasDerivAt_id x).const_mul 8).add_const 1

theorem hd_g0 (x : ℝ) (hx : 0 ≤ x) : HasDerivAt (g0 σ) (g1 σ x) x := by
  have h := (aff_deriv x).rpow_const (p := σ) (Or.inl (by positivity))
  exact h.congr_deriv (by simp only [g1] <;> ring)

theorem hd_g1 (x : ℝ) (hx : 0 ≤ x) : HasDerivAt (g1 σ) (g2 σ x) x := by
  have h := ((aff_deriv x).rpow_const (p := σ - 1) (Or.inl (by positivity))).const_mul (8 * σ)
  exact h.congr_deriv (by simp only [g2] <;> ring)

theorem hd_g2 (x : ℝ) (hx : 0 ≤ x) : HasDerivAt (g2 σ) (g3 σ x) x := by
  have h := (((aff_deriv x).rpow_const (p := σ - 1 - 1) (Or.inl (by positivity))).const_mul
    (8 * (σ - 1))).const_mul (8 * σ)
  exact h.congr_deriv (by simp only [g3] <;> ring)

variable {σ}

theorem g2_nonpos (h0 : 0 < σ) (h1 : σ < 1) (x : ℝ) (hx : 0 ≤ x) : g2 σ x ≤ 0 := by
  unfold g2
  have hp : 0 < (8 * x + 1) ^ (σ - 1 - 1) := Real.rpow_pos_of_pos (by positivity) _
  have : 8 * (σ - 1) * (8 * x + 1) ^ (σ - 1 - 1) ≤ 0 := by nlinarith
  nlinarith

theorem g3_nonneg (h0 : 0 < σ) (h1 : σ < 1) (x : ℝ) (hx : 0 ≤ x) : 0 ≤ g3 σ x := by
  unfold g3
  have hp : 0 < (8 * x + 1) ^ (σ - 1 - 1 - 1) := Real.rpow_pos_of_pos (by positivity) _
  have h2 : 8 * (σ - 1 - 1) * (8 * x + 1) ^ (σ - 1 - 1 - 1) ≤ 0 := by nlinarith
  have h3 : 0 ≤ 8 * (σ - 1) * (8 * (σ - 1 - 1) * (8 * x + 1) ^ (σ - 1 - 1 - 1)) := by nlinarith
  nlinarith

variable (σ)

noncomputable def Mf (c x : ℝ) : ℝ := x * g1 σ x - g0 σ x + c
noncomputable def Nf (c x : ℝ) : ℝ := x ^ 2 * g2 σ x - 2 * x * g1 σ x + 2 * g0 σ x - 2 * c
noncomputable def Ff (c x : ℝ) : ℝ := (g0 σ x - c) / x
noncomputable def Rf (c x : ℝ) : ℝ := Mf σ c x / x ^ 2

theorem hd_M (c x : ℝ) (hx : 0 ≤ x) : HasDerivAt (Mf σ c) (x * g2 σ x) x := by
  have h := (((hasDerivAt_id x).mul (hd_g1 σ x hx)).sub (hd_g0 σ x hx)).add_const c
  exact h.congr_deriv (by simp only [id]; ring)

theorem hd_N (c x : ℝ) (hx : 0 ≤ x) : HasDerivAt (Nf σ c) (x ^ 2 * g3 σ x) x := by
  have h1 := ((hasDerivAt_pow 2 x).mul (hd_g2 σ x hx))
  have h2 := (((hasDerivAt_id x).const_mul 2).mul (hd_g1 σ x hx))
  have h3 := (hd_g0 σ x hx).const_mul 2
  have h := (((h1.sub h2).add h3).sub_const (2 * c))
  exact h.congr_deriv (by simp only [id]; ring)

theorem hd_F (c x : ℝ) (hx : 0 < x) : HasDerivAt (Ff σ c) (Rf σ c x) x := by
  have h := ((hd_g0 σ x hx.le).sub_const c).div (hasDerivAt_id x) hx.ne'
  exact h.congr_deriv (by simp only [Rf, Mf, id_eq]; field_simp; ring)

theorem hd_R (c x : ℝ) (hx : 0 < x) : HasDerivAt (Rf σ c) (Nf σ c x / x ^ 3) x := by
  have h := (hd_M σ c x hx.le).div (hasDerivAt_pow 2 x) (by positivity)
  exact h.congr_deriv (by simp only [Nf, Rf, Mf]; field_simp; ring)

variable {σ}

/-- antitone ratio: `F_c` is antitone on `[x0, oo)` once `M_c(x0) <= 0`. -/
theorem F_anti (h0 : 0 < σ) (h1 : σ < 1) (c x0 : ℝ) (hx0 : 0 < x0) (hM : Mf σ c x0 ≤ 0) :
    AntitoneOn (Ff σ c) (Ici x0) := by
  have hMa : AntitoneOn (Mf σ c) (Ici x0) :=
    anti_of_deriv (cont_of_deriv fun x hx => hd_M σ c x (by linarith))
      (fun x hx => hd_M σ c x (by linarith))
      (fun x hx => mul_nonpos_of_nonneg_of_nonpos (by linarith) (g2_nonpos h0 h1 x (by linarith)))
  refine anti_of_deriv (cont_of_deriv fun x hx => hd_F σ c x (by linarith))
    (fun x hx => hd_F σ c x (by linarith)) ?_
  intro x hx
  have hxm : Mf σ c x ≤ 0 := le_trans (hMa (mem_Ici.mpr le_rfl) (mem_Ici.mpr hx.le) hx.le) hM
  unfold Rf
  exact div_nonpos_of_nonpos_of_nonneg hxm (by positivity)

theorem N_nonneg (h0 : 0 < σ) (h1 : σ < 1) (c : ℝ) (hN : 0 ≤ Nf σ c 2) :
    ∀ x : ℝ, 2 ≤ x → 0 ≤ Nf σ c x := by
  have hm : MonotoneOn (Nf σ c) (Ici 2) :=
    mono_of_deriv (cont_of_deriv fun x hx => hd_N σ c x (by linarith))
      (fun x hx => hd_N σ c x (by linarith))
      (fun x hx => mul_nonneg (by positivity) (g3_nonneg h0 h1 x (by linarith)))
  intro x hx
  exact le_trans hN (hm (mem_Ici.mpr le_rfl) (mem_Ici.mpr hx) hx)

/-- convex ratio: `F_c` is convex on `[2, oo)` once `N_c(2) >= 0`. -/
theorem F_convex (h0 : 0 < σ) (h1 : σ < 1) (c : ℝ) (hN : 0 ≤ Nf σ c 2) :
    ConvexOn ℝ (Ici 2) (Ff σ c) := by
  have hR : MonotoneOn (Rf σ c) (Ici 2) :=
    mono_of_deriv (f' := fun x => Nf σ c x / x ^ 3)
      (cont_of_deriv fun x hx => hd_R σ c x (by linarith))
      (fun x hx => hd_R σ c x (by linarith))
      (fun x hx => div_nonneg (N_nonneg h0 h1 c hN x hx.le) (by positivity))
  exact convex_of_deriv (cont_of_deriv fun x hx => hd_F σ c x (by linarith))
    (fun x hx => hd_F σ c x (by linarith)) hR

/-- (F1) `t -> (t+1)^s - t^s` is antitone on `[0, oo)` (concavity of `t^s`). -/
theorem diff_anti (h0 : 0 < σ) (h1 : σ < 1) :
    AntitoneOn (fun t : ℝ => (t + 1) ^ σ - t ^ σ) (Ici 0) := by
  have hc : ContinuousOn (fun t : ℝ => (t + 1) ^ σ - t ^ σ) (Ici 0) := by
    apply Continuous.continuousOn
    exact ((continuous_id.add continuous_const).rpow_const (fun _ => Or.inr h0.le)).sub
      (continuous_id.rpow_const (fun _ => Or.inr h0.le))
  refine anti_of_deriv (f' := fun t => σ * (t + 1) ^ (σ - 1) - σ * t ^ (σ - 1)) hc ?_ ?_
  · intro t ht
    have hA := ((hasDerivAt_id t).add_const 1).rpow_const (p := σ) (Or.inl (by simp; linarith))
    have hB := (hasDerivAt_id t).rpow_const (p := σ) (Or.inl (by simp; linarith))
    exact (hA.sub hB).congr_deriv (by simp)
  · intro t ht
    have : (t + 1) ^ (σ - 1) ≤ t ^ (σ - 1) :=
      Real.rpow_le_rpow_of_nonpos ht (by linarith) (by linarith)
    nlinarith


end g

end CallerHP
