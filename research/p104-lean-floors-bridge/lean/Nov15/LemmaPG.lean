/-
SPECBREAK R25 Lemma PG (pinned general lemma), lane LEAN-NEXT7, Nov 16.
Source: cards/WILD/SPECBREAK/R25/THEORY.md §2, RESULT25.md item 3. See LemmaPG.md.

V = V_Q ⊕ V_− ⊕ V_0 is modelled as the product `E × F × W` with finrank E = finrank F = 2 and
W (the ancillas) any finite-dimensional space. T w = (−I_Q) ⊕ w ⊕ I_0, so T₊ = T w and
T₋ = T (−w). Lemma PG: if det w = 1 and X lies within rank 2 of I, of T₊ and of T₋, then X² = I.

Proved over ANY field with 2 ≠ 0 (no characteristic-0 hypothesis, no dimension-4 reduction, no
Gröbner step). `char_two_counterexample` shows 2 ≠ 0 cannot be dropped.
-/
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Determinant
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Module
import Mathlib.Tactic.FinCases

open Module Submodule

set_option linter.unusedSectionVars false

namespace LemmaPG

variable {K : Type*} [Field K]
variable {E F W : Type*} [AddCommGroup E] [Module K E] [AddCommGroup F] [Module K F]
  [AddCommGroup W] [Module K W]

/-- `T w = (−I on E) ⊕ w ⊕ (I on W)`. T₊ = `T w`, T₋ = `T (-w)`. Block diagonal = the pin. -/
def T (w : Module.End K F) : Module.End K (E × F × W) :=
  LinearMap.prodMap (-LinearMap.id) (LinearMap.prodMap w LinearMap.id)

@[simp] lemma T_apply (w : Module.End K F) (v : E × F × W) :
    (T w : Module.End K (E × F × W)) v = (-v.1, w v.2.1, v.2.2) := rfl

/-- projection onto V_Q ⊕ V_−; its kernel is V_0. -/
def pr : (E × F × W) →ₗ[K] E × F := LinearMap.prodMap LinearMap.id (LinearMap.fst K F W)

lemma mem_ker_pr (v : E × F × W) : v ∈ LinearMap.ker (pr (K := K)) ↔ v.1 = 0 ∧ v.2.1 = 0 := by
  simp [pr]

lemma finrank_ker_pr [FiniteDimensional K E] [FiniteDimensional K F] [FiniteDimensional K W]
    (hE : finrank K E = 2) (hF : finrank K F = 2) :
    finrank K (LinearMap.ker (pr (K := K) (E := E) (F := F) (W := W))) + 4
      = finrank K (E × F × W) := by
  have h := LinearMap.finrank_range_add_finrank_ker (pr (K := K) (E := E) (F := F) (W := W))
  have htop : LinearMap.range (pr (K := K) (E := E) (F := F) (W := W)) = ⊤ :=
    LinearMap.range_eq_top.2 (fun x => ⟨(x.1, x.2, 0), rfl⟩)
  rw [htop, finrank_top, Module.finrank_prod, hE, hF] at h
  omega

/-- Cayley–Hamilton in dimension 2 with det = 1: w² = t·w − 1 (t = trace). -/
lemma ch2 [FiniteDimensional K F] (hF : finrank K F = 2) (w : Module.End K F)
    (hdet : LinearMap.det w = 1) : ∃ t : K, w * w = t • w - 1 := by
  let b := Module.finBasisOfFinrankEq K F hF
  set M := LinearMap.toMatrix b b w with hM
  have hd : M.det = 1 := by rw [hM, LinearMap.det_toMatrix]; exact hdet
  refine ⟨M.trace, ?_⟩
  apply (LinearMap.toMatrix b b).injective
  rw [LinearMap.toMatrix_mul, map_sub, map_smul, LinearMap.toMatrix_one, ← hM]
  rw [Matrix.det_fin_two] at hd
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_two, Matrix.trace_fin_two] <;>
    first | ring1 | linear_combination -hd

/-- Two subspaces of codimension ≤ 2 meeting inside a subspace of codimension 4 are
complementary modulo it: they span V and meet exactly in it. -/
lemma sup_inf_of_count {V : Type*} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
    (K1 K2 L : Submodule K V) (h1 : finrank K V ≤ finrank K K1 + 2)
    (h2 : finrank K V ≤ finrank K K2 + 2) (hL : finrank K L + 4 = finrank K V)
    (hle : K1 ⊓ K2 ≤ L) : K1 ⊔ K2 = ⊤ ∧ K1 ⊓ K2 = L := by
  have hs := Submodule.finrank_sup_add_finrank_inf_eq K1 K2
  have hi := Submodule.finrank_mono hle
  have hsup := Submodule.finrank_le (K1 ⊔ K2)
  constructor
  · apply Submodule.eq_top_of_finrank_eq; omega
  · apply Submodule.eq_of_le_of_finrank_le hle; omega

lemma ker_big {V : Type*} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
    (f : Module.End K V) (h : finrank K (LinearMap.range f) ≤ 2) :
    finrank K V ≤ finrank K (LinearMap.ker f) + 2 := by
  have := LinearMap.finrank_range_add_finrank_ker f; omega

lemma mem_ker_sub {V : Type*} [AddCommGroup V] [Module K V] (X A : Module.End K V) (v : V) :
    v ∈ LinearMap.ker (X - A) ↔ X v = A v := by
  simp [sub_eq_zero]

lemma two_smul_eq_zero {M : Type*} [AddCommGroup M] [Module K M] (h2 : (2 : K) ≠ 0) {x : M}
    (h : x = -x) : x = 0 := by
  have : (2 : K) • x = 0 := by rw [two_smul]; nth_rewrite 2 [h]; exact add_neg_cancel x
  exact (smul_eq_zero.1 this).resolve_left h2

variable [FiniteDimensional K E] [FiniteDimensional K F] [FiniteDimensional K W]

/-- Lemma PG in the case where −1 is not an eigenvalue of w (so I − T₋ is invertible on
V_Q ⊕ V_−). Only w² = t·w − 1 is used (Cayley–Hamilton with det 1). -/
theorem core (h2 : (2 : K) ≠ 0) (hE : finrank K E = 2) (hF : finrank K F = 2)
    (w : Module.End K F) (t : K) (hCH : w * w = t • w - 1) (hinj : ∀ v, w v = -v → v = 0)
    (X : Module.End K (E × F × W))
    (h0 : finrank K (LinearMap.range (X - 1)) ≤ 2)
    (hp : finrank K (LinearMap.range (X - T w)) ≤ 2)
    (hm : finrank K (LinearMap.range (X - T (-w))) ≤ 2) : X * X = 1 := by
  have hCHv : ∀ x, w (w x) = t • w x - x := fun x => by
    have := congrArg (fun f => f x) hCH; simpa using this
  set K0 := LinearMap.ker (X - 1) with hK0
  set Kp := LinearMap.ker (X - T w) with hKp
  set Km := LinearMap.ker (X - T (-w)) with hKm
  set L := LinearMap.ker (pr (K := K) (E := E) (F := F) (W := W)) with hLdef
  have mem0 : ∀ v, v ∈ K0 ↔ X v = v := fun v => by
    rw [hK0, mem_ker_sub]; rfl
  have memp : ∀ v, v ∈ Kp ↔ X v = T w v := fun v => mem_ker_sub _ _ v
  have memm : ∀ v, v ∈ Km ↔ X v = T (-w) v := fun v => mem_ker_sub _ _ v
  have memL : ∀ v, v ∈ L ↔ v.1 = 0 ∧ v.2.1 = 0 := mem_ker_pr
  have hL4 := finrank_ker_pr (K := K) (E := E) (F := F) (W := W) hE hF
  -- Step 1: K0 ∩ K₋ ⊆ V_0, hence K0 + K₋ = V and V_0 ⊆ K0.
  have hle : K0 ⊓ Km ≤ L := by
    intro v hv
    rw [Submodule.mem_inf, mem0, memm] at hv
    obtain ⟨ha, hb⟩ := hv
    rw [ha, T_apply] at hb
    have e1 : v.1 = -v.1 := congrArg Prod.fst hb
    have e2 : w v.2.1 = -v.2.1 := by
      have := congrArg (fun p => p.2.1) hb
      simp only [LinearMap.neg_apply] at this
      exact neg_eq_iff_eq_neg.mp this.symm
    exact (memL v).2 ⟨two_smul_eq_zero h2 e1, hinj _ e2⟩
  obtain ⟨hsup, hinf⟩ := sup_inf_of_count K0 Km L (ker_big _ h0) (ker_big _ hm) hL4 hle
  have hL0 : L ≤ K0 := hinf ▸ inf_le_left
  have hW0 : ∀ z : W, ((0 : E), (0 : F), z) ∈ K0 := fun z => hL0 ((memL _).2 ⟨rfl, rfl⟩)
  -- the V_− part of an element of K0 with zero V_Q part is in K0
  have hpart : ∀ a ∈ K0, a.1 = 0 → ((0 : E), a.2.1, (0 : W)) ∈ K0 := by
    intro a ha ha1
    have : ((0 : E), a.2.1, (0 : W)) = a - ((0 : E), (0 : F), a.2.2) := by
      ext <;> simp [ha1]
    rw [this]; exact K0.sub_mem ha (hW0 _)
  have hwinj : ∀ x, w x = 0 → x = 0 := by
    intro x hx
    have := hCHv x
    rw [hx, map_zero, smul_zero, zero_sub] at this
    exact neg_eq_zero.1 this.symm
  have hwinj' : ∀ x y, w x = w y → x = y := fun x y h =>
    sub_eq_zero.1 (hwinj _ (by rw [map_sub, h, sub_self]))
  -- Step 2 (key): for k ∈ K₋, (0, (1 − w) k_−, 0) ∈ K0.
  have key : ∀ k ∈ Km, ((0 : E), k.2.1 - w k.2.1, (0 : W)) ∈ K0 := by
    intro k hk
    rw [memm] at hk
    by_cases hA : K0 ⊓ Kp ≤ L
    · -- Case A: K0 + K₊ = V.
      obtain ⟨hsup', -⟩ := sup_inf_of_count K0 Kp L (ker_big _ h0) (ker_big _ hp) hL4 hA
      have hkmem : k ∈ K0 ⊔ Kp := hsup' ▸ Submodule.mem_top
      obtain ⟨a, ha, b, hb, hab⟩ := Submodule.mem_sup.1 hkmem
      have hXa := (mem0 a).1 ha
      have hXb := (memp b).1 hb
      have hbk : b = k - a := by rw [← hab]; abel
      rw [hbk, map_sub, map_sub, hk, hXa] at hXb
      have ea1 : a.1 = -a.1 := by
        have := congrArg Prod.fst hXb
        simp only [Prod.fst_sub, T_apply] at this
        linear_combination (norm := module) -this
      have ha1 : a.1 = 0 := two_smul_eq_zero h2 ea1
      have eA : w a.2.1 - a.2.1 = (2 : K) • w k.2.1 := by
        have := congrArg (fun p => p.2.1) hXb
        simp only [Prod.snd_sub, Prod.fst_sub, T_apply, LinearMap.neg_apply] at this
        linear_combination (norm := module) this
      have e1 := congrArg w eA
      rw [map_sub, map_smul, hCHv, hCHv] at e1
      have hy : k.2.1 - w k.2.1 = ((2 - t) / 2) • a.2.1 := by
        have h2' : (2 : K) • (k.2.1 - w k.2.1) = (2 - t) • a.2.1 := by
          apply hwinj'
          rw [map_smul, map_smul, map_sub, hCHv]
          linear_combination (norm := module) e1 - eA
        have := congrArg (fun x => (2 : K)⁻¹ • x) h2'
        simp only [smul_smul, inv_mul_cancel₀ h2, one_smul] at this
        rw [this, div_eq_inv_mul]
      have : ((0 : E), k.2.1 - w k.2.1, (0 : W)) = ((2 - t) / 2) • ((0 : E), a.2.1, (0 : W)) := by
        ext <;> simp [hy]
      rw [this]; exact K0.smul_mem _ (hpart a ha ha1)
    · -- Case B: some u ∈ K0 ∩ K₊ outside V_0; then w fixes u_− ≠ 0, t = 2 and (1 − w)² = 0.
      obtain ⟨u, hu, huL⟩ := SetLike.not_le_iff_exists.1 hA
      rw [Submodule.mem_inf, mem0, memp] at hu
      obtain ⟨hu0, hup⟩ := hu
      rw [hu0, T_apply] at hup
      have eu1 : u.1 = -u.1 := congrArg Prod.fst hup
      have u1 : u.1 = 0 := two_smul_eq_zero h2 eu1
      have eu2 : w u.2.1 = u.2.1 := (congrArg (fun p => p.2.1) hup).symm
      have u2 : u.2.1 ≠ 0 := fun h => huL ((memL u).2 ⟨u1, h⟩)
      have ht : t = 2 := by
        have := hCHv u.2.1
        rw [eu2, eu2] at this
        have h' : (t - 2) • u.2.1 = 0 := by
          linear_combination (norm := module) -this
        exact (sub_eq_zero.1 ((smul_eq_zero.1 h').resolve_right u2))
      set N : Module.End K F := 1 - w with hN
      have hNN : ∀ x, N (N x) = 0 := by
        intro x
        simp only [hN, LinearMap.sub_apply, Module.End.one_apply, map_sub, hCHv, ht]
        module
      have hNu : u.2.1 ∈ LinearMap.ker N := by
        simp [hN, eu2]
      have hy : k.2.1 - w k.2.1 ∈ K ∙ u.2.1 := by
        have hyN : k.2.1 - w k.2.1 = N k.2.1 := by simp [hN]
        by_cases hker : LinearMap.ker N = ⊤
        · have : N k.2.1 = 0 := by
            have : k.2.1 ∈ LinearMap.ker N := hker ▸ Submodule.mem_top
            exact this
          rw [hyN, this]; exact Submodule.zero_mem _
        · have hlt := Submodule.finrank_lt hker
          rw [hF] at hlt
          have hspan : (K ∙ u.2.1) = LinearMap.ker N := by
            apply Submodule.eq_of_le_of_finrank_le
            · exact (Submodule.span_singleton_le_iff_mem _ _).2 hNu
            · rw [finrank_span_singleton u2]; omega
          rw [hspan, hyN]
          exact hNN k.2.1
      obtain ⟨c, hc⟩ := Submodule.mem_span_singleton.1 hy
      have hu' : ((0 : E), u.2.1, (0 : W)) ∈ K0 := hpart u ((mem0 u).2 hu0) u1
      have : ((0 : E), k.2.1 - w k.2.1, (0 : W)) = c • ((0 : E), u.2.1, (0 : W)) := by
        ext <;> simp [hc]
      rw [this]; exact K0.smul_mem _ hu'
  -- Step 3: X² = I.
  refine LinearMap.ext fun v => ?_
  show X (X v) = v
  have hv : v ∈ K0 ⊔ Km := hsup ▸ Submodule.mem_top
  obtain ⟨a, ha, b, hb, rfl⟩ := Submodule.mem_sup.1 hv
  have hXa := (mem0 a).1 ha
  have hXb := (memm b).1 hb
  have hc := key b hb
  have e : b + T (-w) b = ((0 : E), b.2.1 - w b.2.1, (0 : W)) + (2 : K) • ((0 : E), (0 : F), b.2.2) := by
    ext <;> simp [two_smul, sub_eq_add_neg]
  have hfix : X (b + T (-w) b) = b + T (-w) b := by
    rw [e, map_add, map_smul, (mem0 _).1 hc, (mem0 _).1 (hW0 _)]
  rw [map_add, hXb] at hfix
  have hXT : X (T (-w) b) = b := by
    rw [add_comm b (T (-w) b)] at hfix
    exact add_left_cancel hfix
  rw [map_add, map_add, hXa, hXa, hXb, hXT]

/-- **Lemma PG (R25).** Over any field with 2 ≠ 0: w ∈ SL(V_−), T± = (−I_Q) ⊕ (±w) ⊕ I_0.
If rank(X − I), rank(X − T₊), rank(X − T₋) ≤ 2, then X² = I. Any finite-dimensional V_0. -/
theorem lemmaPG (h2 : (2 : K) ≠ 0) (hE : finrank K E = 2) (hF : finrank K F = 2)
    (w : Module.End K F) (hdet : LinearMap.det w = 1)
    (X : Module.End K (E × F × W))
    (h0 : finrank K (LinearMap.range (X - 1)) ≤ 2)
    (hp : finrank K (LinearMap.range (X - T w)) ≤ 2)
    (hm : finrank K (LinearMap.range (X - T (-w))) ≤ 2) : X * X = 1 := by
  obtain ⟨t, hCH⟩ := ch2 hF w hdet
  have hCHv : ∀ x, w (w x) = t • w x - x := fun x => by
    have := congrArg (fun f => f x) hCH; simpa using this
  by_cases hinj : ∀ v, w v = -v → v = 0
  · exact core h2 hE hF w t hCH hinj X h0 hp hm
  · push Not at hinj
    obtain ⟨v, hv, hv0⟩ := hinj
    have hinj' : ∀ u, (-w) u = -u → u = 0 := by
      intro u hu
      rw [LinearMap.neg_apply, neg_inj] at hu
      by_contra hu0
      have a := hCHv v
      rw [hv, map_neg, hv, neg_neg] at a
      have ta : (t + 2) • v = 0 := by linear_combination (norm := module) a
      have ht1 : t + 2 = 0 := (smul_eq_zero.1 ta).resolve_right hv0
      have b := hCHv u
      rw [hu, hu] at b
      have tb : (t - 2) • u = 0 := by linear_combination (norm := module) -b
      have ht2 : t - 2 = 0 := (smul_eq_zero.1 tb).resolve_right hu0
      have h4 : (2 : K) * 2 = 0 := by linear_combination ht1 - ht2
      exact h2 (mul_self_eq_zero.1 h4)
    have hCH' : (-w) * (-w) = (-t) • (-w) - 1 := by rw [neg_mul_neg, hCH, neg_smul_neg]
    have hm' : finrank K (LinearMap.range (X - T (-(-w)))) ≤ 2 := by rwa [neg_neg]
    exact core h2 hE hF (-w) (-t) hCH' hinj' X h0 hm hm'

lemma neg_eq_self_of_two {M : Type*} [AddCommGroup M] [Module K M] (h2 : (2 : K) = 0) (x : M) :
    -x = x := by
  have : (2 : K) • x = 0 := by rw [h2, zero_smul]
  rw [two_smul] at this
  exact neg_eq_of_add_eq_zero_left this

/-- 2 ≠ 0 is necessary: in characteristic 2, with w = 1 and V_0 = K, T₊ = T₋ = I and
X = I − (projection onto V_0) satisfies all three rank bounds (rank 1) but X² = X ≠ I. -/
theorem char_two_counterexample (h2 : (2 : K) = 0) :
    let X : Module.End K (E × F × K) :=
      LinearMap.prodMap LinearMap.id (LinearMap.prodMap LinearMap.id 0)
    finrank K (LinearMap.range (X - 1)) ≤ 1 ∧
    (T (1 : Module.End K F) : Module.End K (E × F × K)) = 1 ∧
    (T (-1 : Module.End K F) : Module.End K (E × F × K)) = 1 ∧ X * X ≠ 1 := by
  intro X
  refine ⟨?_, ?_, ?_, ?_⟩
  · -- X − 1 factors through the last coordinate K
    let g : K →ₗ[K] E × F × K := LinearMap.inr K E (F × K) ∘ₗ LinearMap.inr K F K
    let h : (E × F × K) →ₗ[K] K := LinearMap.snd K F K ∘ₗ LinearMap.snd K E (F × K)
    have hfac : X - 1 = -(g ∘ₗ h) := by
      ext v <;> simp [X, g, h]
    rw [hfac, LinearMap.range_neg]
    calc finrank K (LinearMap.range (g ∘ₗ h)) ≤ finrank K (LinearMap.range g) :=
          Submodule.finrank_mono (LinearMap.range_comp_le_range h g)
      _ ≤ finrank K K := LinearMap.finrank_range_le g
      _ = 1 := Module.finrank_self K
  · ext v <;> simp [neg_eq_self_of_two h2]
  · ext v <;> simp [neg_eq_self_of_two h2]
  · intro hX
    have := congrArg (fun f => f ((0 : E), (0 : F), (1 : K))) hX
    simp [X] at this

end LemmaPG

#print axioms LemmaPG.lemmaPG
#print axioms LemmaPG.core
#print axioms LemmaPG.char_two_counterexample
