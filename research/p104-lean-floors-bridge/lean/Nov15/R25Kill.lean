/-
SPECBREAK R25 kill of the outer words, lane LEAN-NEXT8, Nov 16. See R25Kill.md.
Source: cards/WILD/SPECBREAK/R25/THEORY.md §1 (R1–R3), §3; RESULT25.md items 2 and 4. Built on LemmaPG.

Factors are Mathlib's `LinearMap.transvection f v` (x ↦ x + f(x)·v), i.e. ρ = I − x yᵀ with f = −y, v = x:
jobs (reflections) have f v = −2, units (transvections) have f v = 0. Products are taken in a group
(units of End V); a word is a list of letters tagged `inl` (stays in place) or `inr` (moved right).

(§1) `ev_eq`: any word = (product of the inl letters) · (product of the inr letters, each conjugated by the
     inl letters to its right). `P3_iff` (R2): for ANY interleaving shape, the inr letters can be chosen
     in a conjugation-closed set R with product D iff A⁻¹D is a product of two elements of R.
(§2) `near_sigmaA`, `near_Asigma` (R3): X = D1·A_q is within rank rk(A − I) of T₊ = D1σ and rk(A − D3)
     of T₋ = D2σ, with σ = I ⊕ s ⊕ I pinned.
(§3) `tv_list_invol`: a product of ≤ 2 transvections that is an involution is I (char ≠ 2). This replaces
     "det 1 ⇒ rank ∈ {0, 2}" plus the R15 Lemma 3 equality case in one step.
     `kill_mu1`: q outer among a, a′ at μ1, U ≤ 2 ⇒ False. `kill_mu2`, `kill_outer`: the e1 ↔ e2 mirror.
-/
import Nov15.LemmaPG
import Mathlib.LinearAlgebra.Transvection.Basic
import Mathlib.Tactic.NoncommRing

open Module Submodule

set_option linter.unusedSectionVars false

namespace R25Kill

/-! ## §1a. Words: moving letters to the right -/
section Words
variable {G : Type*} [Group G]

/-- product of a word (all letters, in multiplication order) -/
def ev : List (G ⊕ G) → G
  | [] => 1
  | .inl a :: w => a * ev w
  | .inr b :: w => b * ev w

/-- the letters that stay -/
def keeps : List (G ⊕ G) → List G
  | [] => []
  | .inl a :: w => a :: keeps w
  | .inr _ :: w => keeps w

/-- the letters that are moved right -/
def movs : List (G ⊕ G) → List G
  | [] => []
  | .inl _ :: w => movs w
  | .inr b :: w => b :: movs w

/-- each moved letter conjugated past the staying letters to its right -/
def conjs : List (G ⊕ G) → List G
  | [] => []
  | .inl _ :: w => conjs w
  | .inr b :: w => ((keeps w).prod⁻¹ * b * (keeps w).prod) :: conjs w

/-- the interleaving pattern with the staying letters filled in -/
def shape : List (G ⊕ G) → List (Option G)
  | [] => []
  | .inl a :: w => some a :: shape w
  | .inr _ :: w => none :: shape w

theorem ev_eq : ∀ w : List (G ⊕ G), ev w = (keeps w).prod * (conjs w).prod
  | [] => by simp [ev, keeps, conjs]
  | .inl a :: w => by simp [ev, keeps, conjs, ev_eq w, mul_assoc]
  | .inr b :: w => by simp only [ev, keeps, conjs, List.prod_cons, ev_eq w]; group

theorem length_conjs : ∀ w : List (G ⊕ G), (conjs w).length = (movs w).length
  | [] => rfl
  | .inl _ :: w => by simp [conjs, movs, length_conjs w]
  | .inr _ :: w => by simp [conjs, movs, length_conjs w]

/-- R is closed under conjugation. -/
def ConjClosed (R : Set G) : Prop := ∀ g r, r ∈ R → g⁻¹ * r * g ∈ R

theorem conjs_mem {R : Set G} (hR : ConjClosed R) :
    ∀ w : List (G ⊕ G), (∀ b ∈ movs w, b ∈ R) → ∀ c ∈ conjs w, c ∈ R
  | [] => by simp [conjs]
  | .inl _ :: w => by simpa [conjs, movs] using conjs_mem hR w
  | .inr b :: w => by
    intro hb c hc
    simp only [movs, List.mem_cons, forall_eq_or_imp] at hb
    simp only [conjs, List.mem_cons] at hc
    rcases hc with rfl | hc
    · exact hR _ _ hb.1
    · exact conjs_mem hR w hb.2 c hc

theorem keeps_movs_of_shape : ∀ w w' : List (G ⊕ G), shape w' = shape w →
    keeps w' = keeps w ∧ (movs w').length = (movs w).length
  | [], [], _ => ⟨rfl, rfl⟩
  | [], _ :: _, h => by cases ‹G ⊕ G› <;> simp [shape] at h
  | _ :: _, [], h => by cases ‹G ⊕ G› <;> simp [shape] at h
  | x :: w, y :: w', h => by
    cases x <;> cases y <;> simp only [shape, List.cons.injEq, reduceCtorEq, false_and,
      Option.some.injEq] at h
    · obtain ⟨rfl, h⟩ := h
      obtain ⟨h1, h2⟩ := keeps_movs_of_shape w w' h
      simp [keeps, movs, h1, h2]
    · obtain ⟨-, h⟩ := h
      obtain ⟨h1, h2⟩ := keeps_movs_of_shape w w' h
      simp [keeps, movs, h1, h2]

/-- Converse direction: any target list of conjugates is realised by moved letters in R,
keeping the shape. -/
theorem realize {R : Set G} (hR : ConjClosed R) :
    ∀ (w : List (G ⊕ G)) (cs : List G), cs.length = (movs w).length → (∀ c ∈ cs, c ∈ R) →
      ∃ w', shape w' = shape w ∧ conjs w' = cs ∧ ∀ b ∈ movs w', b ∈ R
  | [], cs, hl, _ => by
    simp only [movs, List.length_nil, List.length_eq_zero_iff] at hl
    exact ⟨[], rfl, by simp [conjs, hl], by simp [movs]⟩
  | .inl a :: w, cs, hl, hc => by
    obtain ⟨w', h1, h2, h3⟩ := realize hR w cs (by simpa [movs] using hl) hc
    exact ⟨.inl a :: w', by simp [shape, h1], by simp [conjs, h2], by simpa [movs] using h3⟩
  | .inr b :: w, [], hl, _ => by simp [movs] at hl
  | .inr b :: w, c :: cs, hl, hc => by
    simp only [List.mem_cons, forall_eq_or_imp] at hc
    obtain ⟨w', h1, h2, h3⟩ := realize hR w cs (by simpa [movs] using hl) hc.2
    have hk := (keeps_movs_of_shape w w' h1).1
    refine ⟨.inr ((keeps w').prod * c * (keeps w').prod⁻¹) :: w', by simp [shape, h1], ?_, ?_⟩
    · simp only [conjs, h2, List.cons.injEq, and_true]; group
    · simp only [movs, List.mem_cons, forall_eq_or_imp]
      refine ⟨?_, h3⟩
      have := hR ((keeps w').prod⁻¹) c hc.1
      simpa using this

/-- **R2 (P3 ⇔ A⁻¹D3 ∈ Refl²), any interleaving.** Fix the shape of the word (positions of the
staying letters a, a′ and of the two moved slots). Moved letters b, b′ in R with product D exist iff
A⁻¹D is a product of two elements of R, A = product of the staying letters. -/
theorem P3_iff {R : Set G} (hR : ConjClosed R) (w : List (G ⊕ G)) (h2 : (movs w).length = 2)
    (D : G) :
    (∃ w', shape w' = shape w ∧ (∀ b ∈ movs w', b ∈ R) ∧ ev w' = D) ↔
      ∃ r1 ∈ R, ∃ r2 ∈ R, (keeps w).prod⁻¹ * D = r1 * r2 := by
  constructor
  · rintro ⟨w', hs, hb, he⟩
    obtain ⟨hk, hl⟩ := keeps_movs_of_shape w w' hs
    have hl' : (conjs w').length = 2 := by rw [length_conjs, hl, h2]
    obtain ⟨r1, r2, hc⟩ := List.length_eq_two.1 hl'
    have hm := conjs_mem hR w' hb
    rw [hc] at hm
    refine ⟨r1, hm r1 (by simp), r2, hm r2 (by simp), ?_⟩
    rw [← he, ev_eq, hk, hc]; simp
  · rintro ⟨r1, h1, r2, h2', he⟩
    obtain ⟨w', hs, hc, hb⟩ := realize hR w [r1, r2] (by simp [h2]) (by simp [h1, h2'])
    refine ⟨w', hs, hb, ?_⟩
    rw [ev_eq, (keeps_movs_of_shape w w' hs).1, hc]
    have : (keeps w).prod * ((keeps w).prod⁻¹ * D) = D := by group
    rw [← this, he]; simp

lemma ev_swap : ∀ w : List (G ⊕ G), ev (w.map Sum.swap) = ev w
  | [] => rfl
  | .inl a :: w => by simp [ev, ev_swap w]
  | .inr b :: w => by simp [ev, ev_swap w]

lemma keeps_swap : ∀ w : List (G ⊕ G), keeps (w.map Sum.swap) = movs w
  | [] => rfl
  | .inl a :: w => by simp [keeps, movs, keeps_swap w]
  | .inr b :: w => by simp [keeps, movs, keeps_swap w]

lemma movs_swap : ∀ w : List (G ⊕ G), movs (w.map Sum.swap) = keeps w
  | [] => rfl
  | .inl a :: w => by simp [keeps, movs, movs_swap w]
  | .inr b :: w => by simp [keeps, movs, movs_swap w]

end Words

/-! ## §1b. Reflections, transvections, ranks -/
section Lin
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- a job: ρ = I − x yᵀ with y x = 2, written as `transvection f v` with f v = −2 -/
def IsRefl (g : Module.End K V) : Prop :=
  ∃ (f : Dual K V) (v : V), f v = -2 ∧ g = LinearMap.transvection f v

/-- a unit: ρ = I − x yᵀ with y x = 0 (degenerate x = 0 or y = 0 allowed) -/
def IsTv (g : Module.End K V) : Prop :=
  ∃ (f : Dual K V) (v : V), f v = 0 ∧ g = LinearMap.transvection f v

lemma transvection_conj (P : (Module.End K V)ˣ) (f : Dual K V) (v : V) :
    (↑P⁻¹ : Module.End K V) * LinearMap.transvection f v * ↑P
      = LinearMap.transvection (f ∘ₗ (P : Module.End K V)) ((↑P⁻¹ : Module.End K V) v) := by
  ext x
  have hx : (↑P⁻¹ : Module.End K V) ((P : Module.End K V) x) = x := by
    rw [← Module.End.mul_apply, Units.inv_mul, Module.End.one_apply]
  simp [LinearMap.transvection.apply, hx]

lemma conj_pair (P : (Module.End K V)ˣ) (f : Dual K V) (v : V) :
    (f ∘ₗ (P : Module.End K V)) ((↑P⁻¹ : Module.End K V) v) = f v := by
  simp only [LinearMap.coe_comp, Function.comp_apply]
  rw [← Module.End.mul_apply, Units.mul_inv, Module.End.one_apply]

lemma refl_closed : ConjClosed {u : (Module.End K V)ˣ | IsRefl (u : Module.End K V)} := by
  rintro P r ⟨f, v, hfv, hr⟩
  refine ⟨_, _, (conj_pair P f v).trans hfv, ?_⟩
  simp only [Units.val_mul, hr, transvection_conj]

lemma tv_closed : ConjClosed {u : (Module.End K V)ˣ | IsTv (u : Module.End K V)} := by
  rintro P r ⟨f, v, hfv, hr⟩
  refine ⟨_, _, (conj_pair P f v).trans hfv, ?_⟩
  simp only [Units.val_mul, hr, transvection_conj]

lemma refl_sq {g : Module.End K V} (hg : IsRefl g) : g * g = 1 := by
  obtain ⟨f, v, hfv, rfl⟩ := hg
  ext x
  simp only [Module.End.mul_apply, LinearMap.transvection.apply, map_add, map_smul, hfv,
    smul_eq_mul, Module.End.one_apply]
  module

lemma det_refl [FiniteDimensional K V] {g : Module.End K V} (hg : IsRefl g) :
    LinearMap.det g = -1 := by
  obtain ⟨f, v, hfv, rfl⟩ := hg
  rw [LinearMap.transvection.det, hfv]; norm_num

variable [FiniteDimensional K V]

/-- rank of an endomorphism -/
noncomputable def rk (f : Module.End K V) : ℕ := finrank K (LinearMap.range f)

lemma rk_mul_le_left (f g : Module.End K V) : rk (f * g) ≤ rk f :=
  Submodule.finrank_mono (LinearMap.range_comp_le_range g f)

lemma rk_mul_le_right (f g : Module.End K V) : rk (f * g) ≤ rk g := by
  unfold rk
  rw [Module.End.mul_eq_comp, LinearMap.range_comp]
  exact Submodule.finrank_map_le _ _

lemma rk_add_le (f g : Module.End K V) : rk (f + g) ≤ rk f + rk g :=
  (Submodule.finrank_mono (LinearMap.range_add_le f g)).trans
    (Submodule.finrank_add_le_finrank_add_finrank _ _)

lemma rk_neg (f : Module.End K V) : rk (-f) = rk f := by
  unfold rk; rw [LinearMap.range_neg]

lemma rk_mul_sub_one (g h : Module.End K V) : rk (g * h - 1) ≤ rk (g - 1) + rk (h - 1) := by
  have : g * h - 1 = (g - 1) * h + (h - 1) := by noncomm_ring
  rw [this]
  exact (rk_add_le _ _).trans (Nat.add_le_add_right (rk_mul_le_left _ _) _)

lemma rk_transvection (f : Dual K V) (v : V) : rk (LinearMap.transvection f v - 1) ≤ 1 := by
  have hle : LinearMap.range (LinearMap.transvection f v - 1) ≤ K ∙ v := by
    rintro _ ⟨x, rfl⟩
    simp only [LinearMap.sub_apply, LinearMap.transvection.apply, Module.End.one_apply,
      add_sub_cancel_left]
    exact Submodule.smul_mem _ _ (Submodule.mem_span_singleton_self v)
  refine (Submodule.finrank_mono hle).trans ?_
  have := finrank_span_le_card (R := K) ({v} : Set V)
  simpa using this

lemma rk_prod_sub_one (L : List (Module.End K V)) (h : ∀ g ∈ L, rk (g - 1) ≤ 1) :
    rk (L.prod - 1) ≤ L.length := by
  induction L with
  | nil =>
    show rk ((1 : Module.End K V) - 1) ≤ 0
    rw [sub_self]; simp [rk]
  | cons g L ih =>
    simp only [List.mem_cons, forall_eq_or_imp] at h
    simp only [List.prod_cons, List.length_cons]
    have := rk_mul_sub_one g L.prod
    have := ih h.2
    have := h.1
    omega

lemma rk_refl {g : Module.End K V} (hg : IsRefl g) : rk (g - 1) ≤ 1 := by
  obtain ⟨f, v, -, rfl⟩ := hg; exact rk_transvection f v

lemma rk_tv {g : Module.End K V} (hg : IsTv g) : rk (g - 1) ≤ 1 := by
  obtain ⟨f, v, -, rfl⟩ := hg; exact rk_transvection f v

/-- unit-valued list product commutes with the coercion -/
lemma val_prod (L : List (Module.End K V)ˣ) :
    ((L.prod : (Module.End K V)ˣ) : Module.End K V) = (L.map Units.val).prod := by
  induction L with
  | nil => simp
  | cons u L ih => simp [ih]

/-- **Two transvections.** Over 2 ≠ 0, if t₁t₂ is an involution then t₁t₂ = I. -/
theorem tv_pair_invol (h2 : (2 : K) ≠ 0) (f1 f2 : Dual K V) (v1 v2 : V) (h1 : f1 v1 = 0)
    (h2' : f2 v2 = 0)
    (hg : (LinearMap.transvection f1 v1 * LinearMap.transvection f2 v2) *
      (LinearMap.transvection f1 v1 * LinearMap.transvection f2 v2) = 1) :
    LinearMap.transvection f1 v1 * LinearMap.transvection f2 v2 = 1 := by
  set g := LinearMap.transvection f1 v1 * LinearMap.transvection f2 v2 with hgdef
  set c := f1 v2
  set d := f2 v1
  have hgx : ∀ x, g x = x + (f1 x + c * f2 x) • v1 + f2 x • v2 := by
    intro x
    simp only [hgdef, Module.End.mul_apply, LinearMap.transvection.apply, map_add, map_smul,
      smul_eq_mul]
    module
  have hgg : ∀ x, g (g x) = x := by
    intro x; rw [← Module.End.mul_apply, hg, Module.End.one_apply]
  -- scalar equations from f2 ∘ g ∘ g = f2 at v2 and v1
  have e2 := congrArg f2 (hgg v2)
  have e1 := congrArg f2 (hgg v1)
  simp only [hgx, map_add, map_smul, smul_eq_mul, h1, h2'] at e1 e2
  have ht : c * d = 0 := by
    have hsq : (c * d) * (c * d) = 0 := by linear_combination (exp := 1) c * e1 - (c * d) * e2
    exact mul_self_eq_zero.1 hsq
  -- N := g − 1 satisfies N² = −2N and, since cd = 0, N³ = 0
  let N : Module.End K V := g - 1
  have hNx : ∀ x, N x = (f1 x + c * f2 x) • v1 + f2 x • v2 := by
    intro x; simp only [N, LinearMap.sub_apply, Module.End.one_apply, hgx]; abel
  have hN2 : ∀ x, N (N x) = (-2 : K) • N x := by
    intro x
    simp only [N, LinearMap.sub_apply, Module.End.one_apply, map_sub, hgg]
    module
  have hv1 : N v1 = d • v2 := by
    rw [hNx, h1, ht]; simp only [zero_add, zero_smul]; rfl
  have hv2 : N v2 = c • v1 := by
    rw [hNx, h2']; simp only [mul_zero, add_zero, zero_smul]; rfl
  have hN3 : ∀ x, N (N (N x)) = 0 := by
    intro x
    rw [hNx x]
    simp only [map_add, map_smul, hv1, hv2, smul_smul]
    rw [mul_assoc, mul_assoc, show d * c = 0 by rw [mul_comm]; exact ht, ht]
    simp
  have h4 : ∀ x, N x = 0 := by
    intro x
    have := hN3 x
    rw [hN2, hN2, smul_smul] at this
    have h4' : (-2 : K) * -2 ≠ 0 := mul_ne_zero (neg_ne_zero.2 h2) (neg_ne_zero.2 h2)
    exact (smul_eq_zero.1 this).resolve_left h4'
  ext x
  have := h4 x
  simp only [N, LinearMap.sub_apply, Module.End.one_apply, sub_eq_zero] at this
  simpa using this

omit [FiniteDimensional K V] in
lemma transvection_zero : LinearMap.transvection (0 : Dual K V) (0 : V) = 1 := by
  ext x; simp [LinearMap.transvection.apply]

/-- **Kill of the involution (replaces det + R15 Lemma 3 equality case).** A product of at most two
transvections that is an involution is I, over any field with 2 ≠ 0. -/
theorem tv_list_invol (h2 : (2 : K) ≠ 0) (L : List (Module.End K V)) (hL : ∀ g ∈ L, IsTv g)
    (hlen : L.length ≤ 2) (h : L.prod * L.prod = 1) : L.prod = 1 := by
  rcases L with _ | ⟨g1, _ | ⟨g2, _ | ⟨g3, L⟩⟩⟩
  · rfl
  · obtain ⟨f, v, hfv, rfl⟩ := hL g1 (by simp)
    simp only [List.prod_cons, List.prod_nil, mul_one] at h ⊢
    have := tv_pair_invol h2 f 0 v 0 hfv (by simp) (by rw [transvection_zero, mul_one]; exact h)
    rwa [transvection_zero, mul_one] at this
  · obtain ⟨f1, v1, hf1, rfl⟩ := hL g1 (by simp)
    obtain ⟨f2, v2, hf2, rfl⟩ := hL g2 (by simp)
    have := tv_pair_invol h2 f1 f2 v1 v2 hf1 hf2 (by simpa using h)
    simpa using this
  · simp at hlen

end Lin

/-! ## §2. Blocks on V = V_Q × V_− × V_0, and R3 -/
section Blocks
variable {K : Type*} [Field K]
variable {E F W : Type*} [AddCommGroup E] [Module K E] [AddCommGroup F] [Module K F]
  [AddCommGroup W] [Module K W]

open LemmaPG (T T_apply)

/-- σ = I ⊕ s ⊕ I: the pin (x_q ∈ V_−, y_q vanishing on V_Q ⊕ V_0) -/
def S (s : Module.End K F) : Module.End K (E × F × W) :=
  LinearMap.prodMap LinearMap.id (LinearMap.prodMap s LinearMap.id)

@[simp] lemma S_apply (s : Module.End K F) (v : E × F × W) :
    (S s : Module.End K (E × F × W)) v = (v.1, s v.2.1, v.2.2) := rfl

/-- D3 = I ⊕ (−I) ⊕ I (μ = e1* + e2*). D1 = `T δ`, D2 = `T (-δ)` with δ = D1|V_−. -/
def D3 : Module.End K (E × F × W) := S (-1)

lemma T_mul_S (u s : Module.End K F) :
    (T u : Module.End K (E × F × W)) * S s = T (u * s) :=
  LinearMap.ext fun v => by simp [T_apply]

lemma S_mul_T (s u : Module.End K F) :
    (S s : Module.End K (E × F × W)) * T u = T (s * u) :=
  LinearMap.ext fun v => by simp [T_apply]

lemma T_mul_T (u u' : Module.End K F) :
    (T u : Module.End K (E × F × W)) * T u' = S (u * u') :=
  LinearMap.ext fun v => by simp [T_apply]

lemma S_mul_S (s s' : Module.End K F) :
    (S s : Module.End K (E × F × W)) * S s' = S (s * s') :=
  LinearMap.ext fun v => by simp

lemma S_one : (S 1 : Module.End K (E × F × W)) = 1 :=
  LinearMap.ext fun v => by simp

/-- D1·σ·D3 = D2·σ (uses σD3 = D3σ: the pin) -/
lemma T_neg_eq₁ (δ s : Module.End K F) :
    (T (-(δ * s)) : Module.End K (E × F × W)) = T δ * S s * D3 :=
  LinearMap.ext fun v => by simp [T_apply, D3]

lemma T_neg_eq₂ (δ s : Module.End K F) :
    (T (-(δ * s)) : Module.End K (E × F × W)) = T δ * D3 * S s :=
  LinearMap.ext fun v => by simp [T_apply, D3]

variable [FiniteDimensional K E] [FiniteDimensional K F] [FiniteDimensional K W]

/-- **R3, q applied last** (A_q = σA): X = D1σA is within rk(A − I) of T₊ = D1σ and within
rk(A − D3) of T₋ = D2σ. -/
theorem near_sigmaA (δ s : Module.End K F) (A : Module.End K (E × F × W)) :
    rk (T δ * (S s * A) - T (δ * s)) ≤ rk (A - 1) ∧
      rk (T δ * (S s * A) - T (-(δ * s))) ≤ rk (A - D3) := by
  constructor
  · have : T δ * (S s * A) - T (δ * s) = (T δ * S s) * (A - 1) := by
      rw [← T_mul_S]; simp only [mul_sub, sub_mul, mul_one, one_mul, mul_assoc]
    rw [this]; exact rk_mul_le_right _ _
  · have : T δ * (S s * A) - T (-(δ * s)) = (T δ * S s) * (A - D3) := by
      rw [T_neg_eq₁]; simp only [mul_sub, sub_mul, mul_one, one_mul, mul_assoc]
    rw [this]; exact rk_mul_le_right _ _

/-- **R3, q applied first** (A_q = Aσ). -/
theorem near_Asigma (δ s : Module.End K F) (A : Module.End K (E × F × W)) :
    rk (T δ * (A * S s) - T (δ * s)) ≤ rk (A - 1) ∧
      rk (T δ * (A * S s) - T (-(δ * s))) ≤ rk (A - D3) := by
  constructor
  · have : T δ * (A * S s) - T (δ * s) = (T δ * (A - 1)) * S s := by
      rw [← T_mul_S]; simp only [mul_sub, sub_mul, mul_one, one_mul, mul_assoc]
    rw [this]; exact (rk_mul_le_left _ _).trans (rk_mul_le_right _ _)
  · have : T δ * (A * S s) - T (-(δ * s)) = (T δ * (A - D3)) * S s := by
      rw [T_neg_eq₂]; simp only [mul_sub, sub_mul, mul_one, one_mul, mul_assoc]
    rw [this]; exact (rk_mul_le_left _ _).trans (rk_mul_le_right _ _)

omit [FiniteDimensional K E] [FiniteDimensional K F] [FiniteDimensional K W] in
lemma half_add (h2 : (2 : K) ≠ 0) {M : Type*} [AddCommGroup M] [Module K M] (x : M) :
    (2 : K)⁻¹ • x + (2 : K)⁻¹ • x = x := by
  rw [← add_smul, ← two_mul, mul_inv_cancel₀ h2, one_smul]

lemma le_rk_of_inj {M : Type*} [AddCommGroup M] [Module K M] [FiniteDimensional K M]
    (Y : Module.End K (E × F × W)) (ψ : M →ₗ[K] E × F × W)
    (h : Function.Injective (Y ∘ₗ ψ)) : finrank K M ≤ rk Y := by
  rw [← LinearMap.finrank_range_of_inj h]
  exact Submodule.finrank_mono (LinearMap.range_comp_le_range ψ Y)

/-- rank(T u − I) ≤ 2 forces u = I (the −2I on V_Q already uses up rank 2). -/
lemma eq_one_of_rk_T (h2 : (2 : K) ≠ 0) (hE : finrank K E = 2) (u : Module.End K F)
    (h : rk (T u - 1 : Module.End K (E × F × W)) ≤ 2) : u = 1 := by
  by_contra hu
  obtain ⟨f, hf⟩ : ∃ f, u f - f ≠ 0 := by
    by_contra hc
    push Not at hc
    exact hu (LinearMap.ext fun f => by simpa [sub_eq_zero] using hc f)
  let ψ : E × K →ₗ[K] E × F × W :=
    { toFun := fun p => (-(2 : K)⁻¹ • p.1, p.2 • f, 0)
      map_add' := fun x y => by simp [add_smul, smul_add]
      map_smul' := fun c x => by simp [smul_smul, mul_comm] }
  have hval : ∀ p : E × K, (T u - 1 : Module.End K (E × F × W)) (ψ p)
      = (p.1, p.2 • (u f - f), (0 : W)) := by
    intro p
    simp [ψ, T_apply, smul_sub]
    exact half_add h2 p.1
  have hinj : Function.Injective ((T u - 1 : Module.End K (E × F × W)) ∘ₗ ψ) := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro p hp
    rw [LinearMap.comp_apply, hval] at hp
    simp only [Prod.mk_eq_zero, and_true] at hp
    exact Prod.ext hp.1 ((smul_eq_zero.1 hp.2).resolve_right hf)
  have := le_rk_of_inj _ ψ hinj
  rw [Module.finrank_prod, hE, Module.finrank_self] at this
  omega

/-- rank(T 1 − D3) ≥ 4: T 1 − D3 = (−2I) ⊕ (2I) ⊕ 0. -/
lemma rk_T1_D3 (h2 : (2 : K) ≠ 0) (hE : finrank K E = 2) (hF : finrank K F = 2) :
    4 ≤ rk (T 1 - D3 : Module.End K (E × F × W)) := by
  let ψ : E × F →ₗ[K] E × F × W :=
    { toFun := fun p => (-(2 : K)⁻¹ • p.1, (2 : K)⁻¹ • p.2, 0)
      map_add' := fun x y => by simp [smul_add]
      map_smul' := fun c x => by simp [smul_smul, mul_comm] }
  have hval : ∀ p : E × F, (T 1 - D3 : Module.End K (E × F × W)) (ψ p) = (p.1, p.2, (0 : W)) := by
    intro p
    simp [ψ, T_apply, D3]
    exact ⟨half_add h2 p.1, half_add h2 p.2⟩
  have hinj : Function.Injective ((T 1 - D3 : Module.End K (E × F × W)) ∘ₗ ψ) := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro p hp
    rw [LinearMap.comp_apply, hval] at hp
    simp only [Prod.mk_eq_zero, and_true] at hp
    exact Prod.ext hp.1 hp.2
  have := le_rk_of_inj _ ψ hinj
  rwa [Module.finrank_prod, hE, hF] at this

/-! ## §3. The kill -/

local notation "𝔼" => Module.End K (E × F × W)

lemma rk_prod_units (L : List 𝔼ˣ) (hL : ∀ u ∈ L, rk ((u : 𝔼) - 1) ≤ 1) :
    rk ((L.prod : 𝔼) - 1) ≤ L.length := by
  rw [val_prod]
  refine (rk_prod_sub_one _ ?_).trans (by simp)
  intro g hg
  rcases List.mem_map.1 hg with ⟨v, hv, hveq⟩
  rw [← hveq]; exact hL v hv

/-- **Kill at μ1 (R25 §3).** Over a field with 2 ≠ 0, dim V_Q = dim V_− = 2, any ancillas V_0.
Data: D1 = T δ (δ = D1|V_−, an involution of det −1), D3 = I ⊕ (−I) ⊕ I, the pinned q-reflection
σ = I ⊕ s ⊕ I, jobs a, a′ (reflections). Word w1 is the μ1 product: staying letters a, a′, σ with σ
OUTERMOST among them (`[σ, a, a′]` or `[a, a′, σ]` in multiplication order), moved letters = the U ≤ 2
units (transvections), any interleaving; its product is D1. Word w3 is the μ3 product: staying
letters a, a′ (same order), moved letters ≤ 2 reflections (b, b′), any interleaving, product D3.
Conclusion: impossible. -/
theorem kill_mu1 (h2 : (2 : K) ≠ 0) (hE : finrank K E = 2) (hF : finrank K F = 2)
    (δ s : Module.End K F) (hδ2 : δ * δ = 1) (hδdet : LinearMap.det δ = -1) (hs : IsRefl s)
    (a a' σ : 𝔼ˣ) (ha : IsRefl (a : 𝔼)) (ha' : IsRefl (a' : 𝔼)) (hσ : (σ : 𝔼) = S s)
    (w1 w3 : List (𝔼ˣ ⊕ 𝔼ˣ))
    (h1k : keeps w1 = [σ, a, a'] ∨ keeps w1 = [a, a', σ])
    (h1u : ∀ u ∈ movs w1, IsTv (u : 𝔼)) (hU : (movs w1).length ≤ 2)
    (h1 : ((ev w1 : 𝔼ˣ) : 𝔼) = T δ)
    (h3k : keeps w3 = [a, a']) (h3b : ∀ b ∈ movs w3, IsRefl (b : 𝔼))
    (h3l : (movs w3).length ≤ 2) (h3 : ((ev w3 : 𝔼ˣ) : 𝔼) = D3) : False := by
  set A : 𝔼ˣ := a * a' with hAdef
  -- (R2) rank(A − I) ≤ 2 and rank(A − D3) ≤ 2
  have hA1 : rk ((A : 𝔼) - 1) ≤ 2 := by
    simp only [hAdef, Units.val_mul]
    have := rk_mul_sub_one (a : 𝔼) a'
    have := rk_refl ha; have := rk_refl ha'; omega
  set C := (conjs w3).prod with hCdef
  have hC : rk ((C : 𝔼) - 1) ≤ 2 := by
    refine (rk_prod_units _ fun u hu => rk_refl (conjs_mem refl_closed w3 h3b u hu)).trans ?_
    rw [length_conjs]; exact h3l
  have hev3 : ((ev w3 : 𝔼ˣ) : 𝔼) = (A : 𝔼) * (C : 𝔼) := by
    rw [ev_eq, h3k, ← hCdef]
    simp [hAdef, mul_assoc]
  have hAD : rk ((A : 𝔼) - D3) ≤ 2 := by
    have : (A : 𝔼) - D3 = (A : 𝔼) * (1 - (C : 𝔼)) := by
      rw [← h3, hev3, mul_sub, mul_one]
    rw [this]; exact (rk_mul_le_right _ _).trans (by rw [← neg_sub, rk_neg]; exact hC)
  -- (R1) units to the right: D1 = A_q · g1
  set Aq := (keeps w1).prod with hAqdef
  set g1 := (conjs w1).prod with hg1def
  have hg1tv : ∀ u ∈ conjs w1, IsTv (u : 𝔼) := conjs_mem tv_closed w1 h1u
  have hg1len : (conjs w1).length ≤ 2 := by rw [length_conjs]; exact hU
  have hev1 : (Aq : 𝔼) * (g1 : 𝔼) = T δ := by rw [← h1, ev_eq]; simp [hAqdef, hg1def]
  set X : 𝔼 := T δ * (Aq : 𝔼) with hXdef
  have hTT : (T δ : 𝔼) * T δ = 1 := by rw [T_mul_T, hδ2, S_one]
  have hXg : X * (g1 : 𝔼) = 1 := by rw [hXdef, mul_assoc, hev1, hTT]
  have hXinv : X = ((g1⁻¹ : 𝔼ˣ) : 𝔼) := Units.eq_inv_of_mul_eq_one_right hXg
  have hX1 : rk (X - 1) ≤ 2 := by
    have : X - 1 = ((g1⁻¹ : 𝔼ˣ) : 𝔼) * (1 - (g1 : 𝔼)) := by
      rw [hXinv, mul_sub, mul_one, Units.inv_mul]
    rw [this]
    refine (rk_mul_le_right _ _).trans ?_
    rw [← neg_sub, rk_neg]
    exact (rk_prod_units _ fun u hu => rk_tv (hg1tv u hu)).trans hg1len
  -- (R3) the other two rank bounds; Aq = σA or Aσ
  have hAq : (Aq : 𝔼) = S s * (A : 𝔼) ∨ (Aq : 𝔼) = (A : 𝔼) * S s := by
    rcases h1k with h | h
    · left; rw [hAqdef, h]; simp [hAdef, hσ, mul_assoc]
    · right; rw [hAqdef, h]; simp [hAdef, hσ, mul_assoc]
  have hnear : rk (X - T (δ * s)) ≤ 2 ∧ rk (X - T (-(δ * s))) ≤ 2 := by
    rcases hAq with h | h
    · obtain ⟨p, m⟩ := near_sigmaA δ s (A : 𝔼)
      rw [hXdef, h]; exact ⟨p.trans hA1, m.trans hAD⟩
    · obtain ⟨p, m⟩ := near_Asigma δ s (A : 𝔼)
      rw [hXdef, h]; exact ⟨p.trans hA1, m.trans hAD⟩
  -- Lemma PG: X² = I
  have hdet : LinearMap.det (δ * s) = 1 := by
    rw [map_mul, hδdet, det_refl hs]; norm_num
  have hXX : X * X = 1 :=
    LemmaPG.lemmaPG h2 hE hF (δ * s) hdet X hX1 hnear.1 hnear.2
  -- so g1 is an involution, hence g1 = I (≤ 2 transvections)
  have hgg : (g1 : 𝔼) * (g1 : 𝔼) = 1 := by
    have hu : g1⁻¹ * g1⁻¹ = 1 := Units.ext (by rw [Units.val_mul, ← hXinv, hXX, Units.val_one])
    have : g1 * g1 = 1 := by
      rw [← inv_inj, mul_inv_rev, hu, inv_one]
    rw [← Units.val_mul, this, Units.val_one]
  have hg1 : (g1 : 𝔼) = 1 := by
    rw [hg1def, val_prod] at hgg ⊢
    refine tv_list_invol h2 _ ?_ (by simpa using hg1len) hgg
    intro g hg
    rcases List.mem_map.1 hg with ⟨v, hv, hveq⟩
    rw [← hveq]; exact hg1tv v hv
  -- rank 0: A_q = D1, so A = T u for u = sδ or δs
  rw [hg1, mul_one] at hev1
  have hSS : (S s : 𝔼) * S s = 1 := by rw [S_mul_S, refl_sq hs, S_one]
  obtain ⟨u, hu⟩ : ∃ u, (A : 𝔼) = T u := by
    rcases hAq with h | h
    · refine ⟨s * δ, ?_⟩
      rw [← S_mul_T, ← hev1, h, ← mul_assoc, hSS, one_mul]
    · refine ⟨δ * s, ?_⟩
      rw [← T_mul_S, ← hev1, h, mul_assoc, hSS, mul_one]
  rw [hu] at hA1 hAD
  have hu1 := eq_one_of_rk_T h2 hE u hA1
  rw [hu1] at hAD
  have := rk_T1_D3 (W := W) h2 hE hF
  omega

/-- **Kill at μ2**: the e1 ↔ e2 mirror (D1 ↔ D2 = T(−δ); D3 and the pin fixed). In the μ3 word the
b's now stay and the a's move. -/
theorem kill_mu2 (h2 : (2 : K) ≠ 0) (hE : finrank K E = 2) (hF : finrank K F = 2)
    (δ s : Module.End K F) (hδ2 : δ * δ = 1) (hδdet : LinearMap.det δ = -1) (hs : IsRefl s)
    (b b' σ : 𝔼ˣ) (hb : IsRefl (b : 𝔼)) (hb' : IsRefl (b' : 𝔼)) (hσ : (σ : 𝔼) = S s)
    (w2 w3 : List (𝔼ˣ ⊕ 𝔼ˣ))
    (h2k : keeps w2 = [σ, b, b'] ∨ keeps w2 = [b, b', σ])
    (h2u : ∀ u ∈ movs w2, IsTv (u : 𝔼)) (hU : (movs w2).length ≤ 2)
    (h2e : ((ev w2 : 𝔼ˣ) : 𝔼) = T (-δ))
    (h3m : movs w3 = [b, b']) (h3a : ∀ a ∈ keeps w3, IsRefl (a : 𝔼))
    (h3l : (keeps w3).length ≤ 2) (h3 : ((ev w3 : 𝔼ˣ) : 𝔼) = D3) : False := by
  have hdet : LinearMap.det (-δ) = -1 := by
    rw [← neg_one_smul K δ, LinearMap.det_smul, hF, hδdet]; norm_num
  exact kill_mu1 h2 hE hF (-δ) s (by rw [neg_mul_neg, hδ2]) hdet hs b b' σ hb hb' hσ w2
    (w3.map Sum.swap) h2k h2u hU h2e (by rw [keeps_swap, h3m]) (by rwa [movs_swap])
    (by rwa [movs_swap]) (by rw [ev_swap, h3])

/-- **R25 §3, both sides.** If q is outer among a, a′ at μ1, or outer among b, b′ at μ2, the pinned
d = 2 core has no realisation with U ≤ 2 units at either μ1 or μ2. Only the 84 "middle" words
({a,b} q {a,b}) escape. -/
theorem kill_outer (h2 : (2 : K) ≠ 0) (hE : finrank K E = 2) (hF : finrank K F = 2)
    (δ s : Module.End K F) (hδ2 : δ * δ = 1) (hδdet : LinearMap.det δ = -1) (hs : IsRefl s)
    (a a' b b' σ : 𝔼ˣ) (ha : IsRefl (a : 𝔼)) (ha' : IsRefl (a' : 𝔼)) (hb : IsRefl (b : 𝔼))
    (hb' : IsRefl (b' : 𝔼)) (hσ : (σ : 𝔼) = S s)
    (w1 w2 w3 : List (𝔼ˣ ⊕ 𝔼ˣ))
    (h1u : ∀ u ∈ movs w1, IsTv (u : 𝔼)) (hU1 : (movs w1).length ≤ 2) (h1 : ((ev w1 : 𝔼ˣ) : 𝔼) = T δ)
    (h2u : ∀ u ∈ movs w2, IsTv (u : 𝔼)) (hU2 : (movs w2).length ≤ 2)
    (h2e : ((ev w2 : 𝔼ˣ) : 𝔼) = T (-δ))
    (h3k : keeps w3 = [a, a']) (h3m : movs w3 = [b, b']) (h3 : ((ev w3 : 𝔼ˣ) : 𝔼) = D3)
    (houter : (keeps w1 = [σ, a, a'] ∨ keeps w1 = [a, a', σ]) ∨
      (keeps w2 = [σ, b, b'] ∨ keeps w2 = [b, b', σ])) : False := by
  rcases houter with h | h
  · exact kill_mu1 h2 hE hF δ s hδ2 hδdet hs a a' σ ha ha' hσ w1 w3 h h1u hU1 h1 h3k
      (by rw [h3m]; simp [hb, hb']) (by simp [h3m]) h3
  · exact kill_mu2 h2 hE hF δ s hδ2 hδdet hs b b' σ hb hb' hσ w2 w3 h h2u hU2 h2e h3m
      (by rw [h3k]; simp [ha, ha']) (by simp [h3k]) h3

end Blocks

/-! ## Word count (546 of 630) -/
section Count
/-- all length-5 words over {0 = a, 1 = b, 2 = q} (a and a′ written alike, global order fixes them) -/
def allWords : List (List (Fin 3)) :=
  (List.range 243).map (fun n => [n % 3, n / 3 % 3, n / 9 % 3, n / 27 % 3, n / 81 % 3].map
    (fun k => (⟨k % 3, Nat.mod_lt _ (by decide)⟩ : Fin 3)))
/-- job words: two a's, two b's, one q -/
def isJob (w : List (Fin 3)) : Bool := w.count 0 == 2 && w.count 1 == 2 && w.count 2 == 1
/-- q strictly between the two copies of letter x -/
def inside (w : List (Fin 3)) (x : Fin 3) : Bool := ((w.take (w.idxOf 2)).count x == 1)
/-- the words `kill_outer` does NOT cover: q strictly inside both pairs -/
def middle (w : List (Fin 3)) : Bool := inside w 0 && inside w 1

theorem n_jobs : (allWords.filter isJob).length = 30 := by decide
theorem n_middle : ((allWords.filter isJob).filter middle).length = 4 := by decide
/-- with 21 = C(7,2) placements of U = 2 identical units: 630 words, 84 middle, 546 killed -/
theorem n_words : 30 * Nat.choose 7 2 = 630 ∧ 4 * Nat.choose 7 2 = 84 ∧ 630 - 84 = 546 := by decide
end Count

#print axioms R25Kill.P3_iff
#print axioms R25Kill.near_sigmaA
#print axioms R25Kill.near_Asigma
#print axioms R25Kill.tv_list_invol
#print axioms R25Kill.kill_outer
#print axioms R25Kill.n_middle

end R25Kill
