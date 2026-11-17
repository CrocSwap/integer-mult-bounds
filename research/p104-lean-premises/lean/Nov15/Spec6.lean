/-
SPECBREAK R63 survivor #6 kill .  See Spec6.md.
Kernel-only.  Setting: V a vector space over a field K with 2 ≠ 0, vectors e, functional φ with φ e = 1,
R = 1 - 2 e⊗φ, jobs g = 1 - x⊗y with y x = 2.  n-free (V arbitrary), order-free, char ≠ 2.
-/
import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.Tactic.Module
import Mathlib.Tactic.Abel
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Tauto

open Module

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace Spec6

/-! ## §0 jobs, R, types -/
section Basic
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

structure Job (K V : Type*) [Field K] [AddCommGroup V] [Module K V] where
  x : V
  y : Dual K V
  hxy : y x = 2

def Job.g (j : Job K V) : Module.End K V := 1 - LinearMap.smulRight j.y j.x

theorem Job.g_apply (j : Job K V) (v : V) : j.g v = v - j.y v • j.x := by
  simp [Job.g, LinearMap.smulRight_apply]

theorem Job.g_sq (j : Job K V) : j.g * j.g = 1 := by
  ext v
  simp only [Module.End.mul_apply, Job.g_apply, map_sub, map_smul, j.hxy, smul_eq_mul, Module.End.one_apply]
  module

/-- R = 1 - 2 e⊗φ -/
def Rm (e : V) (φ : Dual K V) : Module.End K V := 1 - (2 : K) • LinearMap.smulRight φ e

theorem Rm_apply (e : V) (φ : Dual K V) (v : V) : Rm e φ v = v - (2 * φ v) • e := by
  simp [Rm, LinearMap.smulRight_apply, mul_smul]

theorem Rm_sq (e : V) (φ : Dual K V) (he : φ e = 1) : Rm e φ * Rm e φ = 1 := by
  ext v
  simp only [Module.End.mul_apply, Rm_apply, map_sub, map_smul, he, smul_eq_mul, Module.End.one_apply]
  module

def xT (e : V) (j : Job K V) : Prop := j.x ∈ Submodule.span K {e}
def yT (φ : Dual K V) (j : Job K V) : Prop := j.y ∈ Submodule.span K {φ}

end Basic

/-! ## §1 linear-algebra keys -/
section Keys
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

theorem exists_ker (χ ψ : Dual K V) (hχ : ∃ v0, χ v0 ≠ 0) (h : ∀ v, χ v = 0 → ψ v = 0) :
    ∃ c : K, ψ = c • χ := by
  obtain ⟨v0, hv0⟩ := hχ
  refine ⟨ψ v0 / χ v0, ?_⟩
  ext v
  have h1 : χ (v - (χ v / χ v0) • v0) = 0 := by
    simp only [map_sub, map_smul, smul_eq_mul]
    field_simp
    ring
  have h3 := h _ h1
  simp only [map_sub, map_smul, smul_eq_mul] at h3
  simp only [LinearMap.smul_apply, smul_eq_mul]
  have : ψ v = χ v / χ v0 * ψ v0 := by linear_combination h3
  rw [this]; field_simp

theorem coef_zero {e x : V} (hx : x ∉ Submodule.span K {e}) {a b : K}
    (h : a • e + b • x = 0) : b = 0 ∧ a • e = 0 := by
  by_cases hb : b = 0
  · subst hb
    rw [zero_smul, add_zero] at h
    exact ⟨rfl, h⟩
  · exfalso
    apply hx
    rw [Submodule.mem_span_singleton]
    refine ⟨-(a / b), ?_⟩
    have h' : b • x = -(a • e) := eq_neg_of_add_eq_zero_right h
    have : x = b⁻¹ • (b • x) := by rw [smul_smul, inv_mul_cancel₀ hb, one_smul]
    rw [this, h']
    module

theorem e_ne {e : V} {φ : Dual K V} (he : φ e = 1) : e ≠ 0 := by
  rintro rfl; simp at he

theorem vanish_contra {e : V} {φ : Dual K V} (he : φ e = 1) (h2 : (2 : K) ≠ 0) (j : Job K V)
    (hx : ¬ xT e j) (hy : ¬ yT φ j) (ψ : Dual K V) (hψ : ∃ v, ψ v ≠ 0)
    (hv : ∀ v, ψ v = 0 → (j.g * Rm e φ) v = v) : False := by
  have hφ : ∀ v, ψ v = 0 → φ v = 0 ∧ j.y v = 0 := by
    intro v hv0
    have h0 := hv v hv0
    simp only [Module.End.mul_apply, Rm_apply, Job.g_apply, map_sub, map_smul, smul_eq_mul] at h0
    have h3 : (-(2 * φ v)) • e + (-(j.y v - 2 * φ v * j.y e)) • j.x = 0 := by
      calc _ = (v - j.y v • j.x - (2 * φ v) • (e - j.y e • j.x)) - v := by module
        _ = 0 := by rw [h0, sub_self]
    obtain ⟨hb, ha⟩ := coef_zero hx h3
    have hφv : φ v = 0 := by
      rcases smul_eq_zero.mp ha with h | h
      · have : 2 * φ v = 0 := by linear_combination -h
        rcases mul_eq_zero.mp this with h | h
        · exact absurd h h2
        · exact h
      · exact absurd h (e_ne he)
    refine ⟨hφv, ?_⟩
    rw [hφv] at hb
    linear_combination -hb
  obtain ⟨c, hc⟩ := exists_ker ψ φ hψ (fun v hv0 => (hφ v hv0).1)
  obtain ⟨c', hc'⟩ := exists_ker ψ j.y hψ (fun v hv0 => (hφ v hv0).2)
  have hc0 : c ≠ 0 := by
    rintro rfl
    have := congrArg (fun f => f e) hc
    simp [he] at this
  apply hy
  show j.y ∈ Submodule.span K {φ}
  rw [Submodule.mem_span_singleton]
  refine ⟨c' / c, ?_⟩
  rw [hc', hc]
  ext v
  simp only [LinearMap.smul_apply, smul_eq_mul]
  field_simp

end Keys

/-! ## §2 one vertex: L1, L3, L2 (x-plane), L4 (mixed ends) -/
section Vertex
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {e : V} {φ : Dual K V}

/-- the group G_X (as a predicate): Im(g - 1) ⊆ ⟨e⟩ -/
def GX (e : V) (g : Module.End K V) : Prop := ∃ w : Dual K V, ∀ v, g v = v + w v • e

theorem GX_mul {g h : Module.End K V} (hg : GX e g) (hh : GX e h) : GX e (g * h) := by
  obtain ⟨wg, hwg⟩ := hg
  obtain ⟨wh, hwh⟩ := hh
  refine ⟨wg + wh + (wg e) • wh, fun v => ?_⟩
  rw [Module.End.mul_apply, hwg, hwh]
  simp only [map_add, map_smul, LinearMap.add_apply, LinearMap.smul_apply, smul_eq_mul]
  module

theorem GX_R : GX e (Rm e φ) :=
  ⟨-(2 : K) • φ, fun v => by rw [Rm_apply]; simp only [LinearMap.smul_apply, smul_eq_mul]; module⟩

theorem GX_job {j : Job K V} (hj : xT e j) : GX e j.g := by
  obtain ⟨c, hc⟩ := Submodule.mem_span_singleton.mp hj
  refine ⟨-c • j.y, fun v => ?_⟩
  rw [Job.g_apply, ← hc]
  simp only [LinearMap.smul_apply, smul_eq_mul]
  module

theorem job_of_GX (h2 : (2 : K) ≠ 0) {j : Job K V} (hj : GX e j.g) : xT e j := by
  obtain ⟨w, hw⟩ := hj
  have h1 := hw j.x
  rw [Job.g_apply, j.hxy] at h1
  have h3 : (2 : K) • j.x = (-(w j.x)) • e := by
    have : j.x - (2 : K) • j.x = j.x + w j.x • e := h1
    have h4 : (2 : K) • j.x = -(w j.x • e) := by
      have : (2 : K) • j.x = j.x - (j.x + w j.x • e) := by rw [← this]; module
      rw [this]; module
    rw [h4]; module
  show j.x ∈ Submodule.span K {e}
  rw [Submodule.mem_span_singleton]
  refine ⟨-(w j.x) / 2, ?_⟩
  calc (-(w j.x) / 2) • e = (2 : K)⁻¹ • ((-(w j.x)) • e) := by
        rw [smul_smul]; congr 1; field_simp
    _ = (2 : K)⁻¹ • ((2 : K) • j.x) := by rw [h3]
    _ = j.x := by rw [smul_smul, inv_mul_cancel₀ h2, one_smul]

/-- the vertex relation: ordered word of three jobs is R -/
def Rel (e : V) (φ : Dual K V) (a b c : Job K V) : Prop := a.g * b.g * c.g = Rm e φ

theorem rel_third {a b c : Job K V} (h : Rel e φ a b c) : c.g = b.g * a.g * Rm e φ := by
  have : b.g * a.g * (a.g * b.g * c.g) = c.g := by
    calc _ = b.g * (a.g * a.g) * (b.g * c.g) := by simp only [mul_assoc]
      _ = c.g := by rw [a.g_sq, mul_one, ← mul_assoc, b.g_sq, one_mul]
  rw [← this]; unfold Rel at h; rw [h]

theorem rel_first {a b c : Job K V} (h : Rel e φ a b c) : a.g = Rm e φ * c.g * b.g := by
  have : a.g * b.g * c.g * c.g * b.g = a.g := by
    calc _ = a.g * b.g * (c.g * c.g) * b.g := by simp only [mul_assoc]
      _ = a.g := by rw [c.g_sq, mul_one, mul_assoc, b.g_sq, mul_one]
  unfold Rel at h
  rw [← h]; exact this.symm

theorem rel_second {a b c : Job K V} (h : Rel e φ a b c) : b.g = a.g * Rm e φ * c.g := by
  have : a.g * (a.g * b.g * c.g) * c.g = b.g := by
    calc _ = (a.g * a.g) * b.g * (c.g * c.g) := by simp only [mul_assoc]
      _ = b.g := by rw [a.g_sq, c.g_sq, one_mul, mul_one]
  unfold Rel at h
  rw [← h]; exact this.symm

theorem rel_bc {a b c : Job K V} (h : Rel e φ a b c) : b.g * c.g = a.g * Rm e φ := by
  unfold Rel at h
  have : a.g * (a.g * b.g * c.g) = b.g * c.g := by
    calc _ = (a.g * a.g) * (b.g * c.g) := by simp only [mul_assoc]
      _ = b.g * c.g := by rw [a.g_sq, one_mul]
  rw [← this, h]

theorem rel_rev (he : φ e = 1) {a b c : Job K V} (h : Rel e φ a b c) : Rel e φ c b a := by
  have h1 : c.g * b.g * a.g * Rm e φ = 1 := by
    unfold Rel at h
    rw [← h]
    calc _ = c.g * b.g * (a.g * a.g) * (b.g * c.g) := by simp only [mul_assoc]
      _ = c.g * (b.g * b.g) * c.g := by rw [a.g_sq, mul_one]; simp only [mul_assoc]
      _ = 1 := by rw [b.g_sq, mul_one, c.g_sq]
  unfold Rel
  calc c.g * b.g * a.g = c.g * b.g * a.g * (Rm e φ * Rm e φ) := by rw [Rm_sq e φ he, mul_one]
    _ = (c.g * b.g * a.g * Rm e φ) * Rm e φ := by simp only [mul_assoc]
    _ = Rm e φ := by rw [h1, one_mul]

/-- L1: two X-type edges at a vertex force the third. -/
theorem L1_third (h2 : (2 : K) ≠ 0) {a b c : Job K V} (h : Rel e φ a b c)
    (ha : xT e a) (hb : xT e b) : xT e c := by
  apply job_of_GX h2; rw [rel_third h]
  exact GX_mul (GX_mul (GX_job hb) (GX_job ha)) GX_R

theorem L1_first (h2 : (2 : K) ≠ 0) {a b c : Job K V} (h : Rel e φ a b c)
    (hb : xT e b) (hc : xT e c) : xT e a := by
  apply job_of_GX h2; rw [rel_first h]
  exact GX_mul (GX_mul GX_R (GX_job hc)) (GX_job hb)

theorem L1_second (h2 : (2 : K) ≠ 0) {a b c : Job K V} (h : Rel e φ a b c)
    (ha : xT e a) (hc : xT e c) : xT e b := by
  apply job_of_GX h2; rw [rel_second h]
  exact GX_mul (GX_mul (GX_job ha) GX_R) (GX_job hc)

/-- a functional not in span φ is nonzero somewhere on ker φ -/
theorem exists_kerφ (he : φ e = 1) (y : Dual K V) (hy : ¬ y ∈ Submodule.span K {φ}) :
    ∃ v, φ v = 0 ∧ y v ≠ 0 := by
  by_contra hcon
  push Not at hcon
  obtain ⟨c, hc⟩ := exists_ker φ y ⟨e, by rw [he]; exact one_ne_zero⟩ hcon
  exact hy (Submodule.mem_span_singleton.mpr ⟨c, hc.symm⟩)

/-- L3 (x side): the N-type end a of a vertex forbids b, c both X-type. -/
theorem L3x (he : φ e = 1) (h2 : (2 : K) ≠ 0) {a b c : Job K V} (h : Rel e φ a b c)
    (hn : ¬ xT e a) (hn' : ¬ yT φ a) (hb : xT e b) (hc : xT e c) : False := by
  have hG : GX e (a.g * Rm e φ) := by rw [← rel_bc h]; exact GX_mul (GX_job hb) (GX_job hc)
  obtain ⟨w, hw⟩ := hG
  obtain ⟨v, hv1, hv2⟩ := exists_kerφ he a.y hn'
  have h1 := hw v
  rw [Module.End.mul_apply, Rm_apply, hv1, mul_zero, zero_smul, sub_zero, Job.g_apply] at h1
  apply hn
  show a.x ∈ Submodule.span K {e}
  rw [Submodule.mem_span_singleton]
  refine ⟨-(w v) / a.y v, ?_⟩
  have h3 : a.y v • a.x = -(w v • e) := by
    have : v - a.y v • a.x = v + w v • e := h1
    have h4 : a.y v • a.x = v - (v + w v • e) := by rw [← this]; module
    rw [h4]; module
  calc (-(w v) / a.y v) • e = (a.y v)⁻¹ • (-(w v • e)) := by
        rw [smul_neg, smul_smul, ← neg_smul]; congr 1; field_simp
    _ = (a.y v)⁻¹ • (a.y v • a.x) := by rw [h3]
    _ = a.x := by rw [smul_smul, inv_mul_cancel₀ hv2, one_smul]

end Vertex

section Vertex2
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {e : V} {φ : Dual K V}

theorem mem_of_smul_mem {S : Submodule K V} {s : K} {x : V} (hs : s ≠ 0) (h : s • x ∈ S) : x ∈ S := by
  have := S.smul_mem s⁻¹ h
  rwa [smul_smul, inv_mul_cancel₀ hs, one_smul] at this

theorem gR_mem (a : Job K V) (v : V) :
    a.g (Rm e φ v) - v ∈ Submodule.span K {e, a.x} := by
  rw [Submodule.mem_span_pair]
  refine ⟨-(2 * φ v), -(a.y v - 2 * φ v * a.y e), ?_⟩
  simp only [Rm_apply, Job.g_apply, map_sub, map_smul, smul_eq_mul]
  module

theorem hbc_apply {a b c : Job K V} (h : Rel e φ a b c) (v : V) :
    b.g (c.g v) = a.g (Rm e φ v) := by
  have := congrArg (fun f => f v) (rel_bc h)
  simpa using this

/-- L2 (x side): at a vertex whose first job a is N-type, the other two x's lie in ⟨e, x_a⟩. -/
theorem xplane (he : φ e = 1) (h2 : (2 : K) ≠ 0) {a b c : Job K V} (h : Rel e φ a b c)
    (hn : ¬ xT e a) (hn' : ¬ yT φ a) :
    b.x ∈ Submodule.span K {e, a.x} ∧ c.x ∈ Submodule.span K {e, a.x} := by
  have hA : ∃ v, c.y v = 0 ∧ b.y v ≠ 0 := by
    by_contra hcon
    push Not at hcon
    refine vanish_contra he h2 a hn hn' c.y ⟨c.x, by rw [c.hxy]; exact h2⟩ (fun v hv => ?_)
    rw [Module.End.mul_apply, ← hbc_apply h, Job.g_apply c v, hv, zero_smul, sub_zero,
      Job.g_apply, hcon v hv, zero_smul, sub_zero]
  have hbx : b.x ∈ Submodule.span K {e, a.x} := by
    obtain ⟨v, hv1, hv2⟩ := hA
    have := gR_mem (e := e) (φ := φ) a v
    rw [← hbc_apply h, Job.g_apply c v, hv1, zero_smul, sub_zero, Job.g_apply] at this
    have h3 : b.y v • b.x ∈ Submodule.span K {e, a.x} := by
      have h4 : b.y v • b.x = -(v - b.y v • b.x - v) := by abel
      rw [h4]; exact Submodule.neg_mem _ this
    exact mem_of_smul_mem hv2 h3
  refine ⟨hbx, ?_⟩
  have hB : ∃ v, b.y v = 0 ∧ c.y v ≠ 0 := by
    by_contra hcon
    push Not at hcon
    refine vanish_contra he h2 a hn hn' b.y ⟨b.x, by rw [b.hxy]; exact h2⟩ (fun v hv => ?_)
    rw [Module.End.mul_apply, ← hbc_apply h, Job.g_apply c v, hcon v hv, zero_smul, sub_zero,
      Job.g_apply, hv, zero_smul, sub_zero]
  obtain ⟨v, hv1, hv2⟩ := hB
  have := gR_mem (e := e) (φ := φ) a v
  rw [← hbc_apply h] at this
  simp only [Job.g_apply, map_sub, map_smul, smul_eq_mul, hv1] at this
  have hmem := Submodule.sub_mem _ (Submodule.smul_mem _ (c.y v * b.y c.x) hbx) this
  apply mem_of_smul_mem hv2
  convert hmem using 1
  module

/-- L4 core: X-only first end, Y-only last end is impossible. -/
theorem mixed (he : φ e = 1) (h2 : (2 : K) ≠ 0) {a b c : Job K V} (h : Rel e φ a b c)
    (ha : xT e a) (ha' : ¬ yT φ a) (hc : yT φ c) (hc' : ¬ xT e c) : False := by
  obtain ⟨u, hu⟩ := Submodule.mem_span_singleton.mp ha
  obtain ⟨d, hd⟩ := Submodule.mem_span_singleton.mp hc
  have hae : a.y e * u = 2 := by
    have := a.hxy
    rw [← hu] at this
    simpa [mul_comm] using this
  have hcy : ∀ v, c.y v = d * φ v := fun v => by rw [← hd]; rfl
  have hd0 : d ≠ 0 := by
    intro h0
    have := c.hxy
    rw [hcy, h0, zero_mul] at this
    exact h2 this.symm
  have hu0 : u ≠ 0 := by
    intro h0
    rw [h0, mul_zero] at hae
    exact h2 hae.symm
  let w : Dual K V := (2 : K) • φ - u • a.y
  have hw : ∀ v, a.g (Rm e φ v) = v + w v • e := by
    intro v
    simp only [Rm_apply, Job.g_apply, map_sub, map_smul, smul_eq_mul, w, LinearMap.sub_apply,
      LinearMap.smul_apply, ← hu]
    match_scalars
    · ring
    · linear_combination (2 * φ v) * hae
  have hwe : w e = 0 := by
    simp only [w, LinearMap.sub_apply, LinearMap.smul_apply, smul_eq_mul, he]
    linear_combination -hae
  have hw0 : ∃ v, φ v = 0 ∧ w v ≠ 0 := by
    by_contra hcon
    push Not at hcon
    obtain ⟨k, hk⟩ := exists_ker φ w ⟨e, by rw [he]; exact one_ne_zero⟩ hcon
    have hk0 : k = 0 := by
      have := congrArg (fun f => f e) hk
      simp only [LinearMap.smul_apply, smul_eq_mul, he, mul_one] at this
      rw [hwe] at this; exact this.symm
    rw [hk0, zero_smul] at hk
    apply ha'
    show a.y ∈ Submodule.span K {φ}
    rw [Submodule.mem_span_singleton]
    refine ⟨2 / u, ?_⟩
    ext v
    have := congrArg (fun f => f v) hk
    simp only [w, LinearMap.sub_apply, LinearMap.smul_apply, smul_eq_mul, LinearMap.zero_apply] at this
    simp only [LinearMap.smul_apply, smul_eq_mul]
    field_simp
    linear_combination this
  obtain ⟨v0, hv0, hwv0⟩ := hw0
  have E1 := hbc_apply h v0
  rw [hw v0, Job.g_apply c v0, hcy, hv0, mul_zero, zero_smul, sub_zero, Job.g_apply] at E1
  have hb1 : b.y v0 • b.x = -(w v0 • e) := by
    have h4 : b.y v0 • b.x = v0 - (v0 + w v0 • e) := by rw [← E1]; module
    rw [h4]; module
  have hby : b.y v0 ≠ 0 := by
    intro h0
    rw [h0, zero_smul] at hb1
    have : w v0 • e = 0 := by
      have := neg_eq_zero.mp hb1.symm
      exact this
    rcases smul_eq_zero.mp this with h | h
    · exact hwv0 h
    · exact e_ne he h
  have hbx : b.x = (-(w v0) / b.y v0) • e := by
    calc b.x = (b.y v0)⁻¹ • (b.y v0 • b.x) := by rw [smul_smul, inv_mul_cancel₀ hby, one_smul]
      _ = (-(w v0) / b.y v0) • e := by
        rw [hb1, smul_neg, smul_smul, ← neg_smul]; congr 1; field_simp
  have E2 := hbc_apply h e
  rw [hw e, hwe, zero_smul, add_zero] at E2
  have hce : c.y e = d := by rw [hcy, he, mul_one]
  rw [Job.g_apply c e, hce, Job.g_apply] at E2
  simp only [map_sub, map_smul, smul_eq_mul] at E2
  set q : K := b.y e - d * b.y c.x with hq
  have E3 : d • c.x = (-(q * (-(w v0) / b.y v0))) • e := by
    have h5 : d • c.x = -(q • b.x) := by
      have : d • c.x = e - (e - d • c.x - q • b.x) - q • b.x := by module
      rw [this, E2]; module
    rw [h5, hbx, smul_smul]
    module
  apply hc'
  show c.x ∈ Submodule.span K {e}
  rw [Submodule.mem_span_singleton]
  refine ⟨d⁻¹ * (-(q * (-(w v0) / b.y v0))), ?_⟩
  calc (d⁻¹ * (-(q * (-(w v0) / b.y v0)))) • e = d⁻¹ • ((-(q * (-(w v0) / b.y v0))) • e) := by
        rw [smul_smul]
    _ = d⁻¹ • (d • c.x) := by rw [E3]
    _ = c.x := by rw [smul_smul, inv_mul_cancel₀ hd0, one_smul]

end Vertex2

/-! ## §3 duality: transpose the whole vertex system (V ↦ Dual V, e ↦ φ, φ ↦ eval e) -/
section Dualize
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {e : V} {φ : Dual K V}

def Job.dual (j : Job K V) : Job K (Dual K V) :=
  ⟨j.y, Dual.eval K V j.x, by simpa using j.hxy⟩

theorem dual_g (j : Job K V) : j.dual.g = j.g.dualMap := by
  refine LinearMap.ext fun ψ => LinearMap.ext fun v => ?_
  simp [Job.g_apply, Job.dual, LinearMap.dualMap_apply']
  ring

theorem dual_R : Rm φ (Dual.eval K V e) = (Rm e φ).dualMap := by
  refine LinearMap.ext fun ψ => LinearMap.ext fun v => ?_
  simp [Rm_apply, LinearMap.dualMap_apply']
  ring

theorem dualMap_mul (f g : Module.End K V) : (f * g).dualMap = g.dualMap * f.dualMap := by
  refine LinearMap.ext fun ψ => LinearMap.ext fun v => ?_
  simp [LinearMap.dualMap_apply']

theorem rel_dual (he : φ e = 1) {a b c : Job K V} (h : Rel e φ a b c) :
    Rel φ (Dual.eval K V e) a.dual b.dual c.dual := by
  have h1 := rel_rev he h
  unfold Rel at h1 ⊢
  rw [dual_g, dual_g, dual_g, dual_R, ← h1, dualMap_mul, dualMap_mul, mul_assoc]

theorem yT_dual_iff {e : V} (j : Job K V) : yT (Dual.eval K V e) j.dual ↔ xT e j := by
  unfold yT xT
  show Dual.eval K V j.x ∈ Submodule.span K {Dual.eval K V e} ↔ _
  constructor
  · intro h
    obtain ⟨c, hc⟩ := Submodule.mem_span_singleton.mp h
    rw [Submodule.mem_span_singleton]
    refine ⟨c, ?_⟩
    apply Module.eval_apply_injective K
    simpa using hc
  · intro h
    obtain ⟨c, hc⟩ := Submodule.mem_span_singleton.mp h
    rw [Submodule.mem_span_singleton]
    exact ⟨c, by rw [← hc]; simp⟩

end Dualize

/-! ## §3 the K4 incidence: abstract case split (i)-(v), by `grind` after splitting each vertex into XX / YY / plane -/
section K4
variable {α : Type*} (X Y : α → Prop) (M N : α → α → Prop)

def PlA (X : α → Prop) (M : α → α → Prop) (a b c : α) : Prop :=
  ¬(X a ∧ X b) ∧ ¬(X a ∧ X c) ∧ ¬(X b ∧ X c) ∧
  (¬X a → M a b ∧ M a c) ∧ (¬X b → M b a ∧ M b c) ∧ (¬X c → M c a ∧ M c b)

def L1A (X : α → Prop) (a b c : α) : Prop :=
  (X a → X b → X c) ∧ (X a → X c → X b) ∧ (X b → X c → X a)

def VtA (X Y : α → Prop) (M N : α → α → Prop) (a b c : α) : Prop :=
  L1A X a b c ∧ L1A Y a b c ∧
  ((X a ∧ X b ∧ X c) ∨ (Y a ∧ Y b ∧ Y c) ∨ (PlA X M a b c ∧ PlA Y N a b c))

theorem L1A_swap12 {a b c : α} (h : L1A X a b c) : L1A X b a c := by
  unfold L1A at *; tauto
theorem L1A_swap23 {a b c : α} (h : L1A X a b c) : L1A X a c b := by
  unfold L1A at *; tauto
theorem PlA_swap12 {a b c : α} (h : PlA X M a b c) : PlA X M b a c := by
  unfold PlA at *; tauto
theorem PlA_swap23 {a b c : α} (h : PlA X M a b c) : PlA X M a c b := by
  unfold PlA at *; tauto

theorem VtA_swap12 {a b c : α} (h : VtA X Y M N a b c) : VtA X Y M N b a c := by
  obtain ⟨l1, l2, t⟩ := h
  refine ⟨L1A_swap12 _ l1, L1A_swap12 _ l2, ?_⟩
  rcases t with ⟨h1, h2, h3⟩ | ⟨h1, h2, h3⟩ | ⟨hp, hq⟩
  · exact Or.inl ⟨h2, h1, h3⟩
  · exact Or.inr (Or.inl ⟨h2, h1, h3⟩)
  · exact Or.inr (Or.inr ⟨PlA_swap12 _ _ hp, PlA_swap12 _ _ hq⟩)
theorem VtA_swap23 {a b c : α} (h : VtA X Y M N a b c) : VtA X Y M N a c b := by
  obtain ⟨l1, l2, t⟩ := h
  refine ⟨L1A_swap23 _ l1, L1A_swap23 _ l2, ?_⟩
  rcases t with ⟨h1, h2, h3⟩ | ⟨h1, h2, h3⟩ | ⟨hp, hq⟩
  · exact Or.inl ⟨h1, h3, h2⟩
  · exact Or.inr (Or.inl ⟨h1, h3, h2⟩)
  · exact Or.inr (Or.inr ⟨PlA_swap23 _ _ hp, PlA_swap23 _ _ hq⟩)

end K4

/-! ## §4 vertex theorem: every vertex is XX, YY or plane (with L1 on both sides) -/
section VertexThm
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {e : V} {φ : Dual K V}

/-- x of edge q lies in the plane ⟨e, x_t⟩ -/
def Mx (e : V) (t q : Job K V) : Prop := q.x ∈ Submodule.span K {e, t.x}
def My (φ : Dual K V) (t q : Job K V) : Prop := q.y ∈ Submodule.span K {φ, t.y}
def Vt (e : V) (φ : Dual K V) (a b c : Job K V) : Prop := VtA (xT e) (yT φ) (Mx e) (My φ) a b c

theorem mem_swap {M : Type*} [AddCommGroup M] [Module K M] {e a b : M}
    (hb : b ∈ Submodule.span K {e, a}) (hnb : b ∉ Submodule.span K {e}) :
    a ∈ Submodule.span K {e, b} := by
  obtain ⟨p, q, hpq⟩ := Submodule.mem_span_pair.mp hb
  have hq : q ≠ 0 := by
    rintro rfl
    apply hnb
    rw [Submodule.mem_span_singleton]
    exact ⟨p, by simpa using hpq⟩
  rw [Submodule.mem_span_pair]
  refine ⟨-(p / q), q⁻¹, ?_⟩
  rw [← hpq]
  match_scalars <;> field_simp <;> ring

theorem span_pair_le {M : Type*} [AddCommGroup M] [Module K M] {e a b : M}
    (h : a ∈ Submodule.span K {e, b}) : Submodule.span K {e, a} ≤ Submodule.span K {e, b} := by
  rw [Submodule.span_le]
  intro z hz
  rcases hz with rfl | rfl
  · exact Submodule.subset_span (by simp)
  · exact h

theorem tr_gen {M : Type*} [AddCommGroup M] [Module K M] {e a b i : M}
    (hb : b ∈ Submodule.span K {e, a}) (hnb : b ∉ Submodule.span K {e})
    (hi : i ∈ Submodule.span K {e, a}) : i ∈ Submodule.span K {e, b} :=
  span_pair_le (mem_swap hb hnb) hi

theorem plX_first (he : φ e = 1) (h2 : (2 : K) ≠ 0) {a b c : Job K V} (h : Rel e φ a b c)
    (hn : ¬ xT e a) (hn' : ¬ yT φ a) : PlA (xT e) (Mx e) a b c := by
  obtain ⟨hb, hc⟩ := xplane he h2 h hn hn'
  have hnn : ¬ (xT e b ∧ xT e c) := fun ⟨h1, h3⟩ => L3x he h2 h hn hn' h1 h3
  refine ⟨fun ⟨h1, _⟩ => hn h1, fun ⟨h1, _⟩ => hn h1, hnn, fun _ => ⟨hb, hc⟩,
    fun hnb => ?_, fun hnc => ?_⟩
  · exact ⟨mem_swap hb hnb, span_pair_le (mem_swap hb hnb) hc⟩
  · exact ⟨mem_swap hc hnc, span_pair_le (mem_swap hc hnc) hb⟩

theorem he_dual (he : φ e = 1) : (Dual.eval K V e) φ = 1 := by simpa using he

theorem plY_first (he : φ e = 1) (h2 : (2 : K) ≠ 0) {a b c : Job K V} (h : Rel e φ a b c)
    (hn : ¬ xT e a) (hn' : ¬ yT φ a) : PlA (yT φ) (My φ) a b c :=
  plX_first (e := φ) (φ := Dual.eval K V e) (he_dual he) h2 (rel_dual he h) hn'
    (fun hh => hn ((yT_dual_iff a).1 hh))

theorem vertex (he : φ e = 1) (h2 : (2 : K) ≠ 0) {a b c : Job K V} (h : Rel e φ a b c) :
    Vt e φ a b c := by
  have L1x : L1A (xT e) a b c :=
    ⟨fun ha hb => L1_third h2 h ha hb, fun ha hc => L1_second h2 h ha hc,
      fun hb hc => L1_first h2 h hb hc⟩
  have L1y : L1A (yT φ) a b c :=
    (⟨fun ha hb => L1_third h2 (rel_dual he h) ha hb, fun ha hc => L1_second h2 (rel_dual he h) ha hc,
      fun hb hc => L1_first h2 (rel_dual he h) hb hc⟩ : L1A (xT φ) a.dual b.dual c.dual)
  refine ⟨L1x, L1y, ?_⟩
  by_cases N1 : ¬ xT e a ∧ ¬ yT φ a
  · exact Or.inr (Or.inr ⟨plX_first he h2 h N1.1 N1.2, plY_first he h2 h N1.1 N1.2⟩)
  by_cases N3 : ¬ xT e c ∧ ¬ yT φ c
  · have hr := rel_rev he h
    have p1 := plX_first he h2 hr N3.1 N3.2
    have p2 := plY_first he h2 hr N3.1 N3.2
    exact Or.inr (Or.inr ⟨PlA_swap12 _ _ (PlA_swap23 _ _ (PlA_swap12 _ _ p1)),
      PlA_swap12 _ _ (PlA_swap23 _ _ (PlA_swap12 _ _ p2))⟩)
  by_cases xa : xT e a
  · by_cases xc : xT e c
    · exact Or.inl ⟨xa, L1x.2.1 xa xc, xc⟩
    · have yc : yT φ c := by
        by_contra yc; exact N3 ⟨xc, yc⟩
      by_cases ya : yT φ a
      · exact Or.inr (Or.inl ⟨ya, L1y.2.1 ya yc, yc⟩)
      · exact (mixed he h2 h xa ya yc xc).elim
  · have ya : yT φ a := by
      by_contra ya; exact N1 ⟨xa, ya⟩
    by_cases yc : yT φ c
    · exact Or.inr (Or.inl ⟨ya, L1y.2.1 ya yc, yc⟩)
    · have xc : xT e c := by
        by_contra xc; exact N3 ⟨xc, yc⟩
      exact (mixed (e := φ) (φ := Dual.eval K V e) (he_dual he) h2 (rel_dual he h) ya
        (fun hh => xa ((yT_dual_iff a).1 hh)) ((yT_dual_iff c).2 xc) yc).elim

/-- any of the six orders of the three jobs of a vertex gives the same symmetric statement -/
theorem vertex_any (he : φ e = 1) (h2 : (2 : K) ≠ 0) {a b c : Job K V}
    (h : Rel e φ a b c ∨ Rel e φ a c b ∨ Rel e φ b a c ∨ Rel e φ b c a ∨ Rel e φ c a b ∨
      Rel e φ c b a) : Vt e φ a b c := by
  rcases h with h | h | h | h | h | h
  · exact vertex he h2 h
  · exact VtA_swap23 _ _ _ _ (vertex he h2 h)
  · exact VtA_swap12 _ _ _ _ (vertex he h2 h)
  · exact VtA_swap12 _ _ _ _ (VtA_swap23 _ _ _ _ (vertex he h2 h))
  · exact VtA_swap23 _ _ _ _ (VtA_swap12 _ _ _ _ (vertex he h2 h))
  · exact VtA_swap23 _ _ _ _ (VtA_swap12 _ _ _ _ (VtA_swap23 _ _ _ _ (vertex he h2 h)))

end VertexThm

/-! ## §5 the K4 case split, abstract (cases (i)-(v) of DERIV63) -/
section K4b
variable {α : Type*} (X Y : α → Prop) (M N : α → α → Prop)
set_option maxHeartbeats 8000000 in
theorem k4A (hfx : ∀ t q, X q → M t q) (hfy : ∀ t q, Y q → N t q)
    (hrefl : ∀ t, M t t) (hreflY : ∀ t, N t t)
    (htr : ∀ t t' i, M t t' → ¬X t' → M t i → M t' i)
    (htrY : ∀ t t' i, N t t' → ¬Y t' → N t i → N t' i)
    (p1 p2 p3 p4 p5 p6 : α)
    (hv1 : VtA X Y M N p2 p4 p6) (hv2 : VtA X Y M N p1 p3 p6)
    (hv3 : VtA X Y M N p1 p4 p5) (hv4 : VtA X Y M N p2 p3 p5) :
    (X p1 ∧ X p2 ∧ X p3 ∧ X p4 ∧ X p5 ∧ X p6) ∨ (Y p1 ∧ Y p2 ∧ Y p3 ∧ Y p4 ∧ Y p5 ∧ Y p6) ∨
    (((M p1 p1 ∧ M p1 p2 ∧ M p1 p3 ∧ M p1 p4 ∧ M p1 p5 ∧ M p1 p6) ∨
      (M p2 p1 ∧ M p2 p2 ∧ M p2 p3 ∧ M p2 p4 ∧ M p2 p5 ∧ M p2 p6) ∨
      (M p3 p1 ∧ M p3 p2 ∧ M p3 p3 ∧ M p3 p4 ∧ M p3 p5 ∧ M p3 p6) ∨
      (M p4 p1 ∧ M p4 p2 ∧ M p4 p3 ∧ M p4 p4 ∧ M p4 p5 ∧ M p4 p6) ∨
      (M p5 p1 ∧ M p5 p2 ∧ M p5 p3 ∧ M p5 p4 ∧ M p5 p5 ∧ M p5 p6) ∨
      (M p6 p1 ∧ M p6 p2 ∧ M p6 p3 ∧ M p6 p4 ∧ M p6 p5 ∧ M p6 p6)) ∧
     ((N p1 p1 ∧ N p1 p2 ∧ N p1 p3 ∧ N p1 p4 ∧ N p1 p5 ∧ N p1 p6) ∨
      (N p2 p1 ∧ N p2 p2 ∧ N p2 p3 ∧ N p2 p4 ∧ N p2 p5 ∧ N p2 p6) ∨
      (N p3 p1 ∧ N p3 p2 ∧ N p3 p3 ∧ N p3 p4 ∧ N p3 p5 ∧ N p3 p6) ∨
      (N p4 p1 ∧ N p4 p2 ∧ N p4 p3 ∧ N p4 p4 ∧ N p4 p5 ∧ N p4 p6) ∨
      (N p5 p1 ∧ N p5 p2 ∧ N p5 p3 ∧ N p5 p4 ∧ N p5 p5 ∧ N p5 p6) ∨
      (N p6 p1 ∧ N p6 p2 ∧ N p6 p3 ∧ N p6 p4 ∧ N p6 p5 ∧ N p6 p6))) := by
  obtain ⟨l1, l1', t1⟩ := hv1
  obtain ⟨l2, l2', t2⟩ := hv2
  obtain ⟨l3, l3', t3⟩ := hv3
  obtain ⟨l4, l4', t4⟩ := hv4
  unfold PlA L1A at *
  rcases t1 with t1 | t1 | t1 <;> rcases t2 with t2 | t2 | t2 <;> rcases t3 with t3 | t3 | t3 <;>
    rcases t4 with t4 | t4 | t4 <;>
    first
    | grind
    | (by_cases hY1 : Y p1 <;> by_cases hY2 : Y p2 <;> by_cases hY3 : Y p3 <;>
        by_cases hY4 : Y p4 <;> by_cases hY5 : Y p5 <;> by_cases hY6 : Y p6 <;> grind)
    | (by_cases hX1 : X p1 <;> by_cases hX2 : X p2 <;> by_cases hX3 : X p3 <;>
        by_cases hX4 : X p4 <;> by_cases hX5 : X p5 <;> by_cases hX6 : X p6 <;> grind)
end K4b

/-! ## §6 composition: spec6_dead -/
section Compose
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {e : V} {φ : Dual K V}

def ALLX (e : V) (jA jB jC jD jE jF : Job K V) : Prop :=
  xT e jA ∧ xT e jB ∧ xT e jC ∧ xT e jD ∧ xT e jE ∧ xT e jF
def ALLY (φ : Dual K V) (jA jB jC jD jE jF : Job K V) : Prop :=
  yT φ jA ∧ yT φ jB ∧ yT φ jC ∧ yT φ jD ∧ yT φ jE ∧ yT φ jF
/-- PL: all six x in one plane ⟨e, p⟩ and all six y in one plane ⟨φ, q⟩ -/
def PLdef (e : V) (φ : Dual K V) (jA jB jC jD jE jF : Job K V) : Prop :=
  (∃ p : V, jA.x ∈ Submodule.span K {e, p} ∧ jB.x ∈ Submodule.span K {e, p} ∧
      jC.x ∈ Submodule.span K {e, p} ∧ jD.x ∈ Submodule.span K {e, p} ∧
      jE.x ∈ Submodule.span K {e, p} ∧ jF.x ∈ Submodule.span K {e, p}) ∧
  (∃ q : Dual K V, jA.y ∈ Submodule.span K {φ, q} ∧ jB.y ∈ Submodule.span K {φ, q} ∧
      jC.y ∈ Submodule.span K {φ, q} ∧ jD.y ∈ Submodule.span K {φ, q} ∧
      jE.y ∈ Submodule.span K {φ, q} ∧ jF.y ∈ Submodule.span K {φ, q})

/-- Structure theorem: four vertex relations (K4: BDF, ACF, ADE, BCE) ⇒ PL ∨ ALLX ∨ ALLY. -/
theorem spec6_trichotomy (he : φ e = 1) (h2 : (2 : K) ≠ 0) (jA jB jC jD jE jF : Job K V)
    (hBDF : Rel e φ jB jD jF ∨ Rel e φ jB jF jD ∨ Rel e φ jD jB jF ∨ Rel e φ jD jF jB ∨
      Rel e φ jF jB jD ∨ Rel e φ jF jD jB)
    (hACF : Rel e φ jA jC jF ∨ Rel e φ jA jF jC ∨ Rel e φ jC jA jF ∨ Rel e φ jC jF jA ∨
      Rel e φ jF jA jC ∨ Rel e φ jF jC jA)
    (hADE : Rel e φ jA jD jE ∨ Rel e φ jA jE jD ∨ Rel e φ jD jA jE ∨ Rel e φ jD jE jA ∨
      Rel e φ jE jA jD ∨ Rel e φ jE jD jA)
    (hBCE : Rel e φ jB jC jE ∨ Rel e φ jB jE jC ∨ Rel e φ jC jB jE ∨ Rel e φ jC jE jB ∨
      Rel e φ jE jB jC ∨ Rel e φ jE jC jB) :
    PLdef e φ jA jB jC jD jE jF ∨ ALLX e jA jB jC jD jE jF ∨ ALLY φ jA jB jC jD jE jF := by
  have hfx : ∀ t q : Job K V, xT e q → Mx e t q := fun t q hq =>
    Submodule.span_mono (by simp) hq
  have hfy : ∀ t q : Job K V, yT φ q → My φ t q := fun t q hq =>
    Submodule.span_mono (by simp) hq
  have hrefl : ∀ t : Job K V, Mx e t t := fun t => Submodule.subset_span (by simp)
  have hreflY : ∀ t : Job K V, My φ t t := fun t => Submodule.subset_span (by simp)
  have htr : ∀ t t' i : Job K V, Mx e t t' → ¬ xT e t' → Mx e t i → Mx e t' i :=
    fun t t' i h1 h2' h3 => tr_gen h1 h2' h3
  have htrY : ∀ t t' i : Job K V, My φ t t' → ¬ yT φ t' → My φ t i → My φ t' i :=
    fun t t' i h1 h2' h3 => tr_gen h1 h2' h3
  have key := k4A (xT e) (yT φ) (Mx e) (My φ) hfx hfy hrefl hreflY htr htrY jA jB jC jD jE jF
    (vertex_any he h2 hBDF) (vertex_any he h2 hACF) (vertex_any he h2 hADE) (vertex_any he h2 hBCE)
  rcases key with h | h | ⟨hx, hy⟩
  · exact Or.inr (Or.inl h)
  · exact Or.inr (Or.inr h)
  · left
    refine ⟨?_, ?_⟩
    · rcases hx with h | h | h | h | h | h
      · exact ⟨jA.x, h⟩
      · exact ⟨jB.x, h⟩
      · exact ⟨jC.x, h⟩
      · exact ⟨jD.x, h⟩
      · exact ⟨jE.x, h⟩
      · exact ⟨jF.x, h⟩
    · rcases hy with h | h | h | h | h | h
      · exact ⟨jA.y, h⟩
      · exact ⟨jB.y, h⟩
      · exact ⟨jC.y, h⟩
      · exact ⟨jD.y, h⟩
      · exact ⟨jE.y, h⟩
      · exact ⟨jF.y, h⟩

/-- Survivor #6 is dead, modulo R58's kill of PL / ALLX / ALLY, kept as named hypotheses. -/
theorem spec6_dead (he : φ e = 1) (h2 : (2 : K) ≠ 0) (jA jB jC jD jE jF : Job K V)
    (hBDF : Rel e φ jB jD jF ∨ Rel e φ jB jF jD ∨ Rel e φ jD jB jF ∨ Rel e φ jD jF jB ∨
      Rel e φ jF jB jD ∨ Rel e φ jF jD jB)
    (hACF : Rel e φ jA jC jF ∨ Rel e φ jA jF jC ∨ Rel e φ jC jA jF ∨ Rel e φ jC jF jA ∨
      Rel e φ jF jA jC ∨ Rel e φ jF jC jA)
    (hADE : Rel e φ jA jD jE ∨ Rel e φ jA jE jD ∨ Rel e φ jD jA jE ∨ Rel e φ jD jE jA ∨
      Rel e φ jE jA jD ∨ Rel e φ jE jD jA)
    (hBCE : Rel e φ jB jC jE ∨ Rel e φ jB jE jC ∨ Rel e φ jC jB jE ∨ Rel e φ jC jE jB ∨
      Rel e φ jE jB jC ∨ Rel e φ jE jC jB)
    (R58_PL : ¬ PLdef e φ jA jB jC jD jE jF)
    (R58_ALLX : ¬ ALLX e jA jB jC jD jE jF)
    (R58_ALLY : ¬ ALLY φ jA jB jC jD jE jF) : False := by
  rcases spec6_trichotomy he h2 jA jB jC jD jE jF hBDF hACF hADE hBCE with h | h | h
  · exact R58_PL h
  · exact R58_ALLX h
  · exact R58_ALLY h

end Compose

/-! ## axiom audit -/
#print axioms Spec6.L1_third
#print axioms Spec6.L3x
#print axioms Spec6.xplane
#print axioms Spec6.mixed
#print axioms Spec6.vertex
#print axioms Spec6.k4A
#print axioms Spec6.spec6_trichotomy
#print axioms Spec6.spec6_dead

end Spec6
