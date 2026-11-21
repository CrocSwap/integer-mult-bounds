/-
CallerAdj (lane LEAN-ADJ).  ADJ, ADJ-COMMUTE and the all-degree-2 corollary of
cards/WILD/UNIMODEL/routes/deg2rigid/DR.md (item 2) and routes/countlaw/CW.md (item 3), kernel-checked.
Model (explicit hypotheses): roles `ι` = coordinates of V = ι → K (e_s = Pi.single s 1), stages `T`, masks M_s ⊆ T, stage maps V_t with
  rowid : t ∉ M_s ⇒ (V_t x)_s = x_s          colid : t ∉ M_s ⇒ V_t e_s = e_s
(a stage touches only the roles whose mask contains it: S_t = {s | t ∈ M_s}).  Hosts U_t with `Mod V_t U_t` (CallerSign).
ADJ: product V_b V_a N = -1, N fixes e_r for every role with mask exactly {a,b}, V_a+1, V_b+1 injective, U_a ∩ U_b = 0
  ⇒ (some role has mask {a,b}) → some role has a,b ∈ mask and mask ≠ {a,b} (degree ≥ 3 hub).
ADJ-COMMUTE: for the call list L ++ a :: (M ++ b :: R) (product -1), stages of M with support disjoint from a's, the other stages ∉ {a,b}: same conclusion.
ALLDEG2: all roles of degree exactly 2, hosts pairwise disjoint, no -1 eigenvalues: no stage can lie in a role (contradiction) in any call order.
NOT formalised: derivation of rowid/colid from the twist model (assumed, as orth/resol in CallerSupport); disjointness of hosts for all pairs
  (hypothesis; Lemma A/E give it for k ≥ 3, see CallerSign); DR's DEG1 translation is the `hdeg` hypothesis of adj_dr.
-/
import Nov15.CallerSignCore
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.LinearAlgebra.Matrix.ToLin

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerAdj
open CallerSign Module

section
variable {K : Type*} [Field K] {ι T : Type*} [Fintype ι] [DecidableEq ι]

structure Caller (K : Type*) [Field K] (ι T : Type*) [Fintype ι] [DecidableEq ι] where
  mask : ι → Set T
  V : T → (ι → K) →ₗ[K] (ι → K)
  rowid : ∀ t s, t ∉ mask s → ∀ x, V t x s = x s
  colid : ∀ t s, t ∉ mask s → V t (Pi.single s (1 : K)) = Pi.single s 1

/-- a linear map fixing the unit vectors of `P` fixes every vector supported in `P` -/
theorem fix_of_cols (g : (ι → K) →ₗ[K] (ι → K)) (P : ι → Prop)
    (hg : ∀ s, P s → g (Pi.single s (1 : K)) = Pi.single s 1) (x : ι → K) (hx : ∀ s, ¬ P s → x s = 0) :
    g x = x := by
  have hx' : x = ∑ s, x s • (Pi.single s (1 : K) : ι → K) := by
    ext i; simp [Finset.sum_apply, Pi.single_apply]
  conv_lhs => rw [hx']
  rw [map_sum]
  conv_rhs => rw [hx']
  refine Finset.sum_congr rfl fun s _ => ?_
  by_cases h : P s
  · rw [map_smul, hg s h]
  · rw [hx s h]; simp

/-- injective-on-`W` plus invariance gives surjectivity on `W` (finite dimension) -/
theorem surj_on (W : Submodule K (ι → K)) (f : (ι → K) →ₗ[K] (ι → K)) (hf : ∀ x ∈ W, f x ∈ W)
    (hinj : ∀ x ∈ W, f x = 0 → x = 0) : ∀ w ∈ W, ∃ g ∈ W, f g = w := by
  have hi : Function.Injective (f.restrict hf) := by
    rw [injective_iff_map_eq_zero]
    intro x hx
    have h1 : f x.1 = 0 := by
      have := congrArg Subtype.val hx
      simpa [LinearMap.restrict_apply] using this
    exact Subtype.ext (hinj x.1 x.2 h1)
  have hs := LinearMap.injective_iff_surjective.mp hi
  intro w hw
  obtain ⟨g, hg⟩ := hs ⟨w, hw⟩
  exact ⟨g.1, g.2, by simpa [LinearMap.restrict_apply] using congrArg Subtype.val hg⟩

theorem inj_of_isUnit {g : (ι → K) →ₗ[K] (ι → K)} (h : IsUnit g) (x : ι → K) (hx : g x = 0) : x = 0 := by
  obtain ⟨u, rfl⟩ := h
  have : (↑u⁻¹ * ↑u : (ι → K) →ₗ[K] (ι → K)) = 1 := u.inv_mul
  have h2 := LinearMap.congr_fun this x
  rw [Module.End.mul_apply, hx] at h2
  simpa using h2.symm

/-- ADJ, core form (DR item 2). -/
theorem adj_core (C : Caller K ι T) (a b : T) (Ua Ub : Submodule K (ι → K))
    (N : (ι → K) →ₗ[K] (ι → K))
    (hN : ∀ r, C.mask r = {a, b} → N (Pi.single r (1 : K)) = Pi.single r 1)
    (hprod : C.V b * C.V a * N = -1)
    (ha : ∀ x, C.V a x + x = 0 → x = 0) (hb : ∀ x, C.V b x + x = 0 → x = 0)
    (hMa : Mod (C.V a) Ua) (hMb : Mod (C.V b) Ub) (hd : Disjoint Ua Ub) :
    (∃ r, C.mask r = {a, b}) → ∃ r, a ∈ C.mask r ∧ b ∈ C.mask r ∧ C.mask r ≠ {a, b} := by
  rintro ⟨r0, hr0⟩
  by_contra hno
  push Not at hno
  -- W = vectors supported on the roles with mask exactly {a,b}
  let W : Submodule K (ι → K) :=
    { carrier := {x | ∀ s, C.mask s ≠ {a, b} → x s = 0}
      add_mem' := fun {x y} hx hy s hs => by simp [hx s hs, hy s hs]
      zero_mem' := fun s _ => rfl
      smul_mem' := fun c x hx s hs => by simp [hx s hs] }
  have hmem : ∀ x, x ∈ W ↔ ∀ s, C.mask s ≠ {a, b} → x s = 0 := fun x => Iff.rfl
  have hNW : ∀ x ∈ W, N x = x := fun x hx =>
    fix_of_cols N (fun s => C.mask s = {a, b}) hN x (fun s hs => (hmem x).1 hx s hs)
  have hpx : ∀ x ∈ W, C.V b (C.V a x) = -x := by
    intro x hx
    have := LinearMap.congr_fun hprod x
    simpa [Module.End.mul_apply, hNW x hx] using this
  have hVaW : ∀ x ∈ W, C.V a x ∈ W := by
    intro x hx s hs
    by_cases hbs : b ∈ C.mask s
    · by_cases has : a ∈ C.mask s
      · exact absurd (hno s has hbs) hs
      · rw [C.rowid a s has]; exact hx s hs
    · have h1 := C.rowid b s hbs (C.V a x)
      rw [hpx x hx] at h1
      rw [← h1]; simp [hx s hs]
  have hinjA : ∀ x ∈ W, C.V a x = 0 → x = 0 := by
    intro x hx h0
    have := hpx x hx
    rw [h0] at this
    simpa using this.symm
  have hsA := surj_on W (C.V a) hVaW hinjA
  -- W ≤ Ua
  have hWUa : ∀ w ∈ W, w ∈ Ua := by
    have hmap : ∀ x ∈ W, (C.V a - 1) x ∈ W := fun x hx => by
      simpa using W.sub_mem (hVaW x hx) hx
    have hinj : ∀ x ∈ W, (C.V a - 1) x = 0 → x = 0 := by
      intro x hx h0
      have h1 : C.V a x = x := by simpa [sub_eq_zero] using h0
      have h2 := hpx x hx
      rw [h1] at h2
      exact hb x (by simp [h2])
    intro w hw
    obtain ⟨g, _, hg⟩ := surj_on W (C.V a - 1) hmap hinj w hw
    rw [← hg]; simpa using hMa g
  have hVbW : ∀ w ∈ W, C.V b w ∈ W := by
    intro w hw
    obtain ⟨g, hgW, rfl⟩ := hsA w hw
    rw [hpx g hgW]; exact W.neg_mem hgW
  have hWUb : ∀ w ∈ W, w ∈ Ub := by
    have hmap : ∀ x ∈ W, (C.V b - 1) x ∈ W := fun x hx => by
      simpa using W.sub_mem (hVbW x hx) hx
    have hinj : ∀ x ∈ W, (C.V b - 1) x = 0 → x = 0 := by
      intro w hw h0
      have h1 : C.V b w = w := by simpa [sub_eq_zero] using h0
      obtain ⟨g, hgW, rfl⟩ := hsA w hw
      rw [hpx g hgW] at h1
      have : g = 0 := ha g (by rw [← h1]; simp)
      simp [this]
    intro w hw
    obtain ⟨g, _, hg⟩ := surj_on W (C.V b - 1) hmap hinj w hw
    rw [← hg]; simpa using hMb g
  have he : (Pi.single r0 (1 : K) : ι → K) ∈ W := by
    intro s hs
    have : s ≠ r0 := fun h => hs (h ▸ hr0)
    simp [Pi.single_apply, this]
  have h0 := (Submodule.disjoint_def.mp hd) _ (hWUa _ he) (hWUb _ he)
  have := congrFun h0 r0
  simp at this

/-- DR formulation: mask ⊆ {a,b} with every role of degree ≥ 2 (DEG1 frame). -/
theorem adj_dr (C : Caller K ι T) (a b : T) (Ua Ub : Submodule K (ι → K))
    (N : (ι → K) →ₗ[K] (ι → K))
    (hN : ∀ r, C.mask r = {a, b} → N (Pi.single r (1 : K)) = Pi.single r 1)
    (hprod : C.V b * C.V a * N = -1)
    (ha : ∀ x, C.V a x + x = 0 → x = 0) (hb : ∀ x, C.V b x + x = 0 → x = 0)
    (hMa : Mod (C.V a) Ua) (hMb : Mod (C.V b) Ub) (hd : Disjoint Ua Ub)
    (hdeg : ∀ r, ∃ x y, x ≠ y ∧ x ∈ C.mask r ∧ y ∈ C.mask r) :
    (∃ r, C.mask r ⊆ {a, b}) → ∃ r, a ∈ C.mask r ∧ b ∈ C.mask r ∧ ¬ C.mask r ⊆ {a, b} := by
  rintro ⟨r, hr⟩
  have hab : C.mask r = {a, b} := by
    obtain ⟨x, y, hxy, hx, hy⟩ := hdeg r
    have hx' := hr hx
    have hy' := hr hy
    simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hx' hy'
    apply Set.Subset.antisymm hr
    intro z hz
    simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hz
    rcases hx' with rfl | rfl <;> rcases hy' with rfl | rfl <;> first | exact absurd rfl hxy | skip
    all_goals rcases hz with rfl | rfl <;> assumption
  obtain ⟨r', h1, h2, h3⟩ := adj_core C a b Ua Ub N hN hprod ha hb hMa hMb hd ⟨r, hab⟩
  refine ⟨r', h1, h2, fun hs => h3 (Set.Subset.antisymm hs ?_)⟩
  intro z hz
  simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hz
  rcases hz with rfl | rfl <;> assumption

/-! ### commuting -/

theorem prod_fix (C : Caller K ι T) (l : List T) (r : ι) (h : ∀ c ∈ l, c ∉ C.mask r) :
    (l.map C.V).prod (Pi.single r (1 : K)) = Pi.single r 1 := by
  induction l with
  | nil => simp
  | cons c l ih =>
    simp only [List.map_cons, List.prod_cons, Module.End.mul_apply]
    rw [ih fun d hd => h d (by simp [hd])]
    exact C.colid c r (h c (by simp))

/-- vectors supported off `S_s` are fixed by `V_s` -/
theorem fix_off (C : Caller K ι T) (s : T) (x : ι → K) (hx : ∀ r, s ∈ C.mask r → x r = 0) :
    C.V s x = x :=
  fix_of_cols (C.V s) (fun r => s ∉ C.mask r) (fun r hr => C.colid s r hr) x
    (fun r hr => hx r (by simpa using hr))

/-- stages with disjoint supports commute -/
theorem stage_commute (C : Caller K ι T) (s t : T) (hst : ∀ r, ¬ (s ∈ C.mask r ∧ t ∈ C.mask r)) :
    C.V s * C.V t = C.V t * C.V s := by
  refine (Pi.basisFun K ι).ext fun r => ?_
  simp only [Pi.basisFun_apply, Module.End.mul_apply]
  by_cases hs : s ∈ C.mask r
  · have ht : t ∉ C.mask r := fun h => hst r ⟨hs, h⟩
    rw [C.colid t r ht]
    -- V_s e_r is supported on S_s, disjoint from S_t
    refine (fix_off C t _ ?_).symm
    intro r' hr'
    by_cases hrr : r' = r
    · exact absurd (hrr ▸ hr') ht
    · rw [C.rowid s r' (fun h => hst r' ⟨h, hr'⟩)]
      simp [Pi.single_apply, hrr]
  · rw [C.colid s r hs]
    by_cases ht : t ∈ C.mask r
    · refine (fix_off C s _ ?_)
      intro r' hr'
      by_cases hrr : r' = r
      · exact absurd (hrr ▸ hr') hs
      · rw [C.rowid t r' (fun h => hst r' ⟨hr', h⟩)]
        simp [Pi.single_apply, hrr]
    · rw [C.colid t r ht, C.colid s r hs]

theorem rot_neg_one {p q : (ι → K) →ₗ[K] (ι → K)} (h : p * q = -1) : q * p = -1 := by
  have h1 : (-p) * q = 1 := by
    have : (-p) * q = -(p * q) := by simp [Module.End.mul_eq_comp, LinearMap.neg_comp]
    rw [this, h, neg_neg]
  have h2 := comm_one h1
  have h3 : q * -p = -(q * p) := by ext x; simp [Module.End.mul_apply]
  rw [h3] at h2
  simpa using congrArg Neg.neg h2

/-- ADJ-COMMUTE (CW item 3): call list `L ++ a :: (M ++ b :: R)`, product `-1`; the stages in `M` have support disjoint
from `a`'s; every stage of `L, M, R` differs from `a` and `b`. Same conclusion as ADJ for the pair `a,b`. -/
theorem adj_commute (C : Caller K ι T) (L M R : List T) (a b : T) (Ua Ub : Submodule K (ι → K))
    (hother : ∀ c ∈ L ++ M ++ R, c ≠ a ∧ c ≠ b)
    (hM : ∀ c ∈ M, ∀ r, ¬ (a ∈ C.mask r ∧ c ∈ C.mask r))
    (hprod : ((L ++ a :: (M ++ b :: R)).map C.V).prod = -1)
    (ha : ∀ x, C.V a x + x = 0 → x = 0) (hb : ∀ x, C.V b x + x = 0 → x = 0)
    (hMa : Mod (C.V a) Ua) (hMb : Mod (C.V b) Ub) (hd : Disjoint Ua Ub) :
    (∃ r, C.mask r = {a, b}) → ∃ r, a ∈ C.mask r ∧ b ∈ C.mask r ∧ C.mask r ≠ {a, b} := by
  set pL := (L.map C.V).prod
  set pM := (M.map C.V).prod
  set pR := (R.map C.V).prod
  have h0 : pL * (C.V a * (pM * (C.V b * pR))) = -1 := by
    simpa [pL, pM, pR, mul_assoc] using hprod
  have h1 : C.V a * (pM * (C.V b * (pR * pL))) = -1 := by
    have := rot_neg_one h0
    simpa [mul_assoc] using this
  have hcomm : C.V a * pM = pM * C.V a := by
    have : Commute (C.V a) pM := by
      refine Commute.list_prod_right _ _ ?_
      intro y hy
      obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hy
      exact (stage_commute C a c (hM c hc))
    exact this
  have h2 : pM * (C.V a * (C.V b * (pR * pL))) = -1 := by
    rw [← mul_assoc, ← hcomm, mul_assoc]; exact h1
  have h3 : C.V a * C.V b * (pR * pL * pM) = -1 := by
    have := rot_neg_one h2
    simpa [mul_assoc] using this
  have hN : ∀ r, C.mask r = {b, a} → (pR * pL * pM) (Pi.single r (1 : K)) = Pi.single r 1 := by
    intro r hr
    have hr' : ∀ c, c ≠ a → c ≠ b → c ∉ C.mask r := by
      intro c hca hcb hc
      rw [hr] at hc
      simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hc
      rcases hc with h | h
      · exact hcb h
      · exact hca h
    simp only [Module.End.mul_apply]
    rw [prod_fix C M r (fun c hc => hr' c (hother c (by simp [hc])).1 (hother c (by simp [hc])).2),
      prod_fix C L r (fun c hc => hr' c (hother c (by simp [hc])).1 (hother c (by simp [hc])).2),
      prod_fix C R r (fun c hc => hr' c (hother c (by simp [hc])).1 (hother c (by simp [hc])).2)]
  rintro ⟨r, hr⟩
  obtain ⟨r', h1, h2, h3'⟩ := adj_core C b a Ub Ua (pR * pL * pM) hN h3 hb ha hMb hMa hd.symm
    ⟨r, by rw [hr, Set.pair_comm]⟩
  exact ⟨r', h2, h1, fun h => h3' (by rw [h, Set.pair_comm])⟩

/-- first element of a list satisfying `P` -/
theorem list_first {P : T → Prop} : ∀ (l : List T), (∃ c ∈ l, P c) →
    ∃ M b R, l = M ++ b :: R ∧ (∀ c ∈ M, ¬ P c) ∧ P b := by
  intro l
  induction l with
  | nil => rintro ⟨c, hc, _⟩; simp at hc
  | cons x l ih =>
    intro ⟨c, hc, hP⟩
    by_cases hx : P x
    · exact ⟨[], x, l, rfl, by simp, hx⟩
    · have : ∃ c ∈ l, P c := by
        rcases List.mem_cons.mp hc with rfl | h
        · exact absurd hP hx
        · exact ⟨c, h, hP⟩
      obtain ⟨M, b, R, rfl, hM, hb⟩ := ih this
      exact ⟨x :: M, b, R, rfl, by
        intro d hd; rcases List.mem_cons.mp hd with rfl | h
        · exact hx
        · exact hM d h, hb⟩

theorem pair_eq {x y a b : T} (hab : a ≠ b) (ha : a ∈ ({x, y} : Set T)) (hb : b ∈ ({x, y} : Set T)) :
    ({x, y} : Set T) = {a, b} := by
  ext z
  simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at *
  rcases ha with rfl | rfl <;> rcases hb with rfl | rfl <;> aesop

/-- ALL-DEG2 (CW corollary): every role has exactly two stages in its mask, the call list `l` (nodup, all stages) has
product `-1`, all hosts pairwise disjoint, no `-1` eigenvalue: then no stage `a ∈ l` lies in any role — i.e. no
stage is used at all. (k ≥ 3 enters through the host-disjointness hypothesis, i.e. Lemma A/E.) -/
theorem all_deg2_dead (C : Caller K ι T) (l : List T) (U : T → Submodule K (ι → K))
    (hnd : l.Nodup) (hall : ∀ r t, t ∈ C.mask r → t ∈ l)
    (hdeg : ∀ r, ∃ x y, x ≠ y ∧ C.mask r = {x, y})
    (hprod : (l.map C.V).prod = -1)
    (hno : ∀ t, ∀ x, C.V t x + x = 0 → x = 0)
    (hMod : ∀ t, Mod (C.V t) (U t)) (hdisj : ∀ a b, a ≠ b → Disjoint (U a) (U b))
    (a : T) (hal : a ∈ l) (r : ι) (har : a ∈ C.mask r) : False := by
  -- another stage c in the same role
  obtain ⟨x, y, hxy, hm⟩ := hdeg r
  obtain ⟨c, hca, hcr⟩ : ∃ c, c ≠ a ∧ c ∈ C.mask r := by
    rw [hm] at har ⊢
    simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at har
    rcases har with rfl | rfl
    · exact ⟨y, fun h => hxy h.symm, by simp⟩
    · exact ⟨x, hxy, by simp⟩
  -- rotate the call list to start at a
  obtain ⟨s, t, hl⟩ := List.append_of_mem hal
  have hnd' : (s ++ a :: t).Nodup := hl ▸ hnd
  have hrot : (((a :: t) ++ s).map C.V).prod = -1 := by
    have h1 : (s.map C.V).prod * ((a :: t).map C.V).prod = -1 := by
      rw [← List.prod_append, ← List.map_append, ← hl]; exact hprod
    have := rot_neg_one h1
    rw [← List.prod_append, ← List.map_append] at this
    exact this
  have hnd2 : ((a :: t) ++ s).Nodup := by
    have := List.nodup_append_comm.mp hnd'
    simpa using this
  have hcl : c ∈ t ++ s := by
    have hc : c ∈ s ++ a :: t := hl ▸ hall r c hcr
    simp only [List.mem_append, List.mem_cons] at hc ⊢
    rcases hc with h | h | h
    · exact Or.inr h
    · exact absurd h hca
    · exact Or.inl h
  obtain ⟨M, b, R, hMR, hM, hb⟩ :=
    list_first (P := fun d => ∃ r', a ∈ C.mask r' ∧ d ∈ C.mask r') (t ++ s) ⟨c, hcl, r, har, hcr⟩
  obtain ⟨r', har', hbr'⟩ := hb
  have hnd3 : (a :: (M ++ b :: R)).Nodup := by rw [← hMR]; simpa using hnd2
  have hab : a ≠ b := by
    intro h; subst h
    simp [List.nodup_cons] at hnd3
  have hoth : ∀ d ∈ [] ++ M ++ R, d ≠ a ∧ d ≠ b := by
    intro d hd
    simp only [List.nil_append, List.mem_append] at hd
    simp only [List.nodup_cons, List.mem_append, List.mem_cons, not_or] at hnd3
    have hn := hnd3.2
    rw [List.nodup_append] at hn
    refine ⟨fun h => ?_, fun h => ?_⟩
    · subst h; rcases hd with hd | hd
      · exact hnd3.1.1 hd
      · exact hnd3.1.2.2 hd
    · subst h
      rcases hd with hd | hd
      · simp [List.nodup_cons] at hn
        exact (hn.2.2 d hd).1 rfl
      · simp [List.nodup_cons] at hn
        exact hn.2.1.1 hd
  have hprod' : (([] ++ a :: (M ++ b :: R)).map C.V).prod = -1 := by
    simpa [hMR] using hrot
  obtain ⟨r'', h1, h2, h3⟩ := adj_commute C [] M R a b (U a) (U b) hoth
    (fun d hd r0 h => hM d hd ⟨r0, h⟩) hprod' (hno a) (hno b) (hMod a) (hMod b) (hdisj a b hab)
    (by
      obtain ⟨x', y', hxy', hm'⟩ := hdeg r'
      refine ⟨r', ?_⟩
      rw [hm'] at har' hbr' ⊢
      exact pair_eq hab (by simpa using har') (by simpa using hbr'))
  obtain ⟨x', y', hxy', hm'⟩ := hdeg r''
  rw [hm'] at h1 h2 h3
  exact h3 (pair_eq hab h1 h2)

end

/-! ### Non-vacuity: k = 3 stages, 2 roles; role 0 is a hub (mask {0,1,2}), role 1 has mask {0,1}.
V0 = [[2,1],[-1,0]], V1 = [[0,-3],[-1,-2]], V2 = diag(-1/3,1); V1 V0 V2 = -1, hosts span(1,-1), span(1,1). -/

noncomputable def M0 : Matrix (Fin 2) (Fin 2) ℝ := !![2, 1; -1, 0]
noncomputable def M1 : Matrix (Fin 2) (Fin 2) ℝ := !![0, -3; -1, -2]
noncomputable def M2 : Matrix (Fin 2) (Fin 2) ℝ := !![-1/3, 0; 0, 1]

noncomputable def toy : Caller ℝ (Fin 2) (Fin 3) where
  mask := ![{0, 1, 2}, {0, 1}]
  V := ![M0.mulVecLin, M1.mulVecLin, M2.mulVecLin]
  rowid := by
    intro t s ht x
    fin_cases t <;> fin_cases s <;>
      simp [M0, M1, M2, Matrix.mulVec, dotProduct, Fin.sum_univ_two, Matrix.mulVecLin_apply] at ht ⊢
  colid := by
    intro t s ht
    fin_cases t <;> fin_cases s <;>
      simp [M0, M1, M2, Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Fin.sum_univ_two] at ht ⊢ <;>
      (ext i; fin_cases i <;> simp [Pi.single_apply])

theorem toy_prod : toy.V 1 * toy.V 0 * toy.V 2 = -1 := by
  refine LinearMap.ext fun x => ?_
  ext i
  fin_cases i <;>
    simp [toy, M0, M1, M2, Module.End.mul_apply, Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct,
      Fin.sum_univ_two] <;> ring

noncomputable def UA : Submodule ℝ (Fin 2 → ℝ) := Submodule.span ℝ {![1, -1]}
noncomputable def UB : Submodule ℝ (Fin 2 → ℝ) := Submodule.span ℝ {![1, 1]}

theorem toy_disj : Disjoint UA UB := by
  rw [Submodule.disjoint_def]
  intro y h1 h2
  obtain ⟨c, rfl⟩ := Submodule.mem_span_singleton.mp h1
  obtain ⟨d, hd⟩ := Submodule.mem_span_singleton.mp h2
  have e0 := congrFun hd 0
  have e1 := congrFun hd 1
  simp at e0 e1
  have : c = 0 := by linarith
  simp [this]

theorem toy_hyps :
    ∃ r, toy.mask r = {0, 1} := ⟨1, by simp [toy]⟩

theorem toy_modA : Mod (toy.V 0) UA := by
  intro x
  refine Submodule.mem_span_singleton.mpr ⟨x 0 + x 1, ?_⟩
  ext i; fin_cases i <;> simp [toy, M0, Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Fin.sum_univ_two] <;> ring

theorem toy_modB : Mod (toy.V 1) UB := by
  intro x
  refine Submodule.mem_span_singleton.mpr ⟨-x 0 - 3 * x 1, ?_⟩
  ext i; fin_cases i <;> simp [toy, M1, Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Fin.sum_univ_two] <;> ring

/-- the toy meets every hypothesis of `adj_commute` (call list `[1, 0, 2]`, a = 1, b = 0, L = M = ∅, R = [2]),
and the conclusion (a hub of degree 3: role 0) is witnessed. -/
theorem toy_adj : ∃ r, (1 : Fin 3) ∈ toy.mask r ∧ (0 : Fin 3) ∈ toy.mask r ∧ toy.mask r ≠ {1, 0} := by
  refine adj_commute toy [] [] [2] 1 0 UB UA ?_ ?_ ?_ ?_ ?_ toy_modB toy_modA toy_disj.symm ⟨1, ?_⟩
  · intro c hc; simp at hc; subst hc; decide
  · intro c hc; simp at hc
  · have h := toy_prod
    simp only [List.nil_append, List.map_cons, List.prod_cons, List.prod_nil, mul_one, Module.End.mul_eq_comp] at h ⊢
    exact h
  · intro x hx
    have e0 := congrFun hx 0
    have e1 := congrFun hx 1
    simp [toy, M1, Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Fin.sum_univ_two] at e0 e1
    ext i; fin_cases i <;> simp <;> linarith
  · intro x hx
    have e0 := congrFun hx 0
    have e1 := congrFun hx 1
    simp [toy, M0, Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Fin.sum_univ_two] at e0 e1
    ext i; fin_cases i <;> simp <;> linarith
  · ext z; simp [toy, Set.pair_comm]

#print axioms CallerAdj.adj_core
#print axioms CallerAdj.adj_dr
#print axioms CallerAdj.stage_commute
#print axioms CallerAdj.adj_commute
#print axioms CallerAdj.all_deg2_dead
#print axioms CallerAdj.toy_adj

end CallerAdj
