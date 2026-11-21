/-
CallerSupport (lane LEAN-SUPPORT).  SUPPORT and RESCUE of cards/WILD/UNIMODEL/routes/maindepth/MD.md (items 1-2), kernel-checked.
Model (minimal roles/masks/pieces layer): roles `ι` with coordinates V = ι → K (e_s = Pi.single s 1), stages `T`, mask M_s ⊆ T,
events `J`, each with a piece p_j ⊆ T, a host/idle flag, and an update Pi_j : V → V.  E_p = coordinate projector onto the
roles s with p ⊆ M_s.  Hypotheses, stated explicitly (they are the per-stage orthogonality content of MD item 1):
  orth  : Pi_j = E_{p_j} Pi_j E_{p_j}
  resol : for every stage t, the events at t (t ∈ p_j) resolve E_{ {t} }:  sum_{j at t} Pi_j = E_{ {t} }.
SUPPORT: image / kernel / matrix-entry support of every event; host subspace U_t = range(sum of host events at t) lies on roles with t ∈ M_s.
RESCUE: if t ∈ M_r and no idle piece p has t ∈ p ⊆ M_r (t "unrescued" for r) then e_r ∈ U_t; with U_a ∩ U_b = 0 (a ≠ b) a role has at most
one unrescued stage.  Bridge: CallerSign lemmaA's IsInternal conclusion gives that pairwise disjointness; instantiated on CallerSignInst's k=3 hosts.
NOT formalised: derivation of orth/resol from D3 §1 (assumed), and U_a ∩ U_b = 0 for ALL pairs (here a hypothesis; bridge gives it for the pairs lemmaA covers).
-/
import Nov15.CallerSignInst

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerSupport
open CallerSign Module
open scoped Classical

section
variable {K : Type*} [Field K] {ι T J : Type*} [Fintype ι] [DecidableEq ι] [Fintype J]

/-- coordinate projector onto the roles `s` with `p ⊆ M s` -/
noncomputable def E (M : ι → Set T) (p : Set T) : (ι → K) →ₗ[K] (ι → K) :=
  LinearMap.pi (fun s => if p ⊆ M s then LinearMap.proj s else 0)

theorem E_apply (M : ι → Set T) (p : Set T) (x : ι → K) (s : ι) :
    E M p x s = if p ⊆ M s then x s else 0 := by
  unfold E; by_cases h : p ⊆ M s <;> simp [h]

structure Model (K : Type*) [Field K] (ι T J : Type*) [Fintype ι] [Fintype J] where
  mask : ι → Set T
  piece : J → Set T
  isHost : J → Prop
  Pi : J → (ι → K) →ₗ[K] (ι → K)
  orth : ∀ j, Pi j = E mask (piece j) ∘ₗ Pi j ∘ₗ E mask (piece j)
  resol : ∀ t, (∑ j, if t ∈ piece j then Pi j else 0) = E mask {t}

variable (m : Model K ι T J)

/-- host part of stage `t`: sum of the host events at `t` -/
noncomputable def hostSum (t : T) : (ι → K) →ₗ[K] (ι → K) :=
  ∑ j, if m.isHost j ∧ t ∈ m.piece j then m.Pi j else 0

/-- host subspace `U_t` -/
noncomputable def hostSub (t : T) : Submodule K (ι → K) := LinearMap.range (hostSum m t)

/-! ### SUPPORT -/

/-- image support: `Pi_j x` vanishes on roles whose mask misses the piece -/
theorem support_image (j : J) (x : ι → K) (s : ι) (hs : ¬ m.piece j ⊆ m.mask s) :
    m.Pi j x s = 0 := by
  have h := LinearMap.congr_fun (m.orth j) x
  rw [h]
  simp [E_apply, hs]

/-- coimage support: `Pi_j` kills vectors supported off the roles containing the piece -/
theorem support_coimage (j : J) (x : ι → K) (hx : ∀ s, m.piece j ⊆ m.mask s → x s = 0) :
    m.Pi j x = 0 := by
  have h := LinearMap.congr_fun (m.orth j) x
  have hE : E m.mask (m.piece j) x = 0 := by
    ext s; rw [E_apply]; split_ifs with h1
    · exact hx s h1
    · rfl
  rw [h]; simp [hE]

/-- matrix-entry form: a nonzero entry `(s, s')` needs both masks to contain the piece -/
theorem support_entry (j : J) (s s' : ι)
    (h : m.Pi j (Pi.single s' (1 : K)) s ≠ 0) :
    m.piece j ⊆ m.mask s ∧ m.piece j ⊆ m.mask s' := by
  constructor
  · by_contra hs; exact h (support_image m j _ s hs)
  · by_contra hs'
    refine h ?_
    rw [support_coimage m j _ ?_]; rfl
    intro s'' hs''
    have : s'' ≠ s' := fun e => hs' (e ▸ hs'')
    simp [Pi.single_apply, this]

/-- host subspace sits on roles whose mask contains the stage -/
theorem support_host (t : T) (y : ι → K) (hy : y ∈ hostSub m t) (s : ι) (hs : t ∉ m.mask s) :
    y s = 0 := by
  obtain ⟨x, rfl⟩ := hy
  simp only [hostSum, LinearMap.sum_apply, Finset.sum_apply]
  refine Finset.sum_eq_zero fun j _ => ?_
  split_ifs with h
  · exact support_image m j x s (fun hsub => hs (hsub h.2))
  · rfl

/-! ### RESCUE -/

/-- `t` is unrescued for role `r`: `t ∈ M_r` and no idle piece `p` has `t ∈ p ⊆ M_r` -/
def Unrescued (r : ι) (t : T) : Prop :=
  t ∈ m.mask r ∧ ∀ j, ¬ m.isHost j → t ∈ m.piece j → ¬ m.piece j ⊆ m.mask r

theorem single_mem_hostSub [Nontrivial K] (r : ι) (t : T) (h : Unrescued m r t) :
    (Pi.single r (1 : K) : ι → K) ∈ hostSub m t := by
  set e : ι → K := Pi.single r (1 : K) with he
  have hE : E m.mask {t} e = e := by
    ext s; rw [E_apply]; split_ifs with h1
    · rfl
    · have : s ≠ r := fun hsr => h1 (by rw [hsr]; simpa using h.1)
      simp [he, Pi.single_apply, this]
  have hres := LinearMap.congr_fun (m.resol t) e
  rw [hE] at hres
  have hidle : ∀ j, ¬ m.isHost j → t ∈ m.piece j → m.Pi j e = 0 := by
    intro j hj ht
    apply support_coimage
    intro s hs
    have : s ≠ r := fun hsr => h.2 j hj ht (hsr ▸ hs)
    simp [he, Pi.single_apply, this]
  refine ⟨e, ?_⟩
  have h1 : hostSum m t e = ∑ j, (if m.isHost j ∧ t ∈ m.piece j then m.Pi j e else 0) := by
    simp only [hostSum, LinearMap.sum_apply]
    refine Finset.sum_congr rfl fun j _ => ?_
    split_ifs <;> simp
  have h3 : ∀ j, ((if t ∈ m.piece j then m.Pi j else 0 : (ι → K) →ₗ[K] (ι → K)) e) =
      if t ∈ m.piece j then m.Pi j e else 0 := fun j => by split_ifs <;> simp
  have h2 : (∑ j, (if t ∈ m.piece j then m.Pi j e else 0)) = e := by
    rw [LinearMap.sum_apply] at hres
    simpa only [h3] using hres
  refine h1.trans (Eq.trans ?_ h2)
  refine Finset.sum_congr rfl fun j _ => ?_
  by_cases hj : m.isHost j
  · by_cases ht : t ∈ m.piece j <;> simp [hj, ht]
  · by_cases ht : t ∈ m.piece j
    · simp [hj, ht, hidle j hj ht]
    · simp [ht]

/-- RESCUE: a role has at most one unrescued stage, given pairwise disjoint host subspaces. -/
theorem rescue_at_most_one [Nontrivial K] (hdisj : ∀ a b : T, a ≠ b → Disjoint (hostSub m a) (hostSub m b))
    (r : ι) (a b : T) (ha : Unrescued m r a) (hb : Unrescued m r b) : a = b := by
  by_contra hab
  have h := (Submodule.disjoint_def.mp (hdisj a b hab)) _ (single_mem_hostSub m r a ha)
    (single_mem_hostSub m r b hb)
  have := congrFun h r
  simp at this

/-- consequence (MD item 2): two stages both in `M_r` and both unrescued for `r` coincide;
    equivalently two distinct stages of `M_r` cannot both lack an idle rescuer. -/
theorem rescue_corollary [Nontrivial K] (hdisj : ∀ a b : T, a ≠ b → Disjoint (hostSub m a) (hostSub m b))
    (r : ι) (a b : T) (hab : a ≠ b) (ha : a ∈ m.mask r) (hb : b ∈ m.mask r) :
    (∃ j, ¬ m.isHost j ∧ a ∈ m.piece j ∧ m.piece j ⊆ m.mask r) ∨
    (∃ j, ¬ m.isHost j ∧ b ∈ m.piece j ∧ m.piece j ⊆ m.mask r) := by
  by_contra hcon
  push_neg at hcon
  exact hab (rescue_at_most_one m hdisj r a b ⟨ha, fun j hj hja hs => hcon.1 j hj hja hs⟩
    ⟨hb, fun j hj hjb hs => hcon.2 j hj hjb hs⟩)

end

/-! ### Bridge to CallerSign (lemmaA ⇒ pairwise disjoint hosts) -/

theorem disjoint_of_internal {κ : Type*} [DecidableEq κ] {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    (A : κ → Submodule K V) (h : DirectSum.IsInternal A) (a b : κ) (hab : a ≠ b) :
    Disjoint (A a) (A b) :=
  (h.submodule_iSupIndep).pairwiseDisjoint hab

/-- on CallerSignInst's k = 3 design, the hosts of stages 2 and 3 are disjoint (from `lemmaA_first`) -/
theorem inst_hosts_disjoint : Disjoint s2.host s3.host := by
  have h := (instance_laws).1
  have := disjoint_of_internal _ h 0 1 (by decide)
  simpa using this

/-! ### Non-vacuity: a 2-stage, 3-role, 3-event model satisfying orth, resol and U_0 ∩ U_1 = 0 -/

noncomputable def Pr (s : Fin 3) : (Fin 3 → ℝ) →ₗ[ℝ] (Fin 3 → ℝ) :=
  LinearMap.pi (fun s' => if s' = s then LinearMap.proj s else 0)

theorem Pr_apply (s : Fin 3) (x : Fin 3 → ℝ) (s' : Fin 3) : Pr s x s' = if s' = s then x s else 0 := by
  unfold Pr; by_cases h : s' = s <;> simp [h]

/-- roles a=0 (mask {0,1}), b=1 (mask {0}), c=2 (mask {1}); events: host {0} on b, idle {0,1} on a, host {1} on c -/
noncomputable def toy : Model ℝ (Fin 3) (Fin 2) (Fin 3) where
  mask := ![{0, 1}, {0}, {1}]
  piece := ![{0}, {0, 1}, {1}]
  isHost := ![True, False, True]
  Pi := ![Pr 1, Pr 0, Pr 2]
  orth := by
    intro j
    refine LinearMap.ext fun x => ?_
    ext s
    fin_cases j <;> fin_cases s <;>
      simp [E_apply, Pr_apply, Set.subset_def, Set.mem_insert_iff]
  resol := by
    intro t
    refine LinearMap.ext fun x => ?_
    ext s
    fin_cases t <;> fin_cases s <;>
      simp [E_apply, Pr_apply, Set.subset_def, Set.mem_insert_iff, Fin.sum_univ_three]

theorem toy_U0 (y : Fin 3 → ℝ) (h : y ∈ hostSub toy 0) : y 0 = 0 ∧ y 2 = 0 := by
  obtain ⟨x, rfl⟩ := h
  simp [hostSum, toy, Fin.sum_univ_three, Pr_apply, LinearMap.sum_apply]

theorem toy_U1 (y : Fin 3 → ℝ) (h : y ∈ hostSub toy 1) : y 0 = 0 ∧ y 1 = 0 := by
  obtain ⟨x, rfl⟩ := h
  simp [hostSum, toy, Fin.sum_univ_three, Pr_apply, LinearMap.sum_apply]

theorem toy_disjoint : ∀ a b : Fin 2, a ≠ b → Disjoint (hostSub toy a) (hostSub toy b) := by
  intro a b hab
  rw [Submodule.disjoint_def]
  have key : ∀ y : Fin 3 → ℝ, y ∈ hostSub toy 0 → y ∈ hostSub toy 1 → y = 0 := by
    intro y h0 h1
    obtain ⟨a0, a2⟩ := toy_U0 y h0
    obtain ⟨b0, b1⟩ := toy_U1 y h1
    ext s; fin_cases s <;> simp [a0, a2, b1]
  fin_cases a <;> fin_cases b <;> simp at hab ⊢
  · exact fun y h0 h1 => key y h0 h1
  · exact fun y h1 h0 => key y h0 h1

/-- non-vacuity of RESCUE: role b (index 1) has stage 0 unrescued, so e_b ∈ U_0 (and indeed U_0 = span e_b) -/
theorem toy_rescue : (Pi.single 1 (1 : ℝ) : Fin 3 → ℝ) ∈ hostSub toy 0 :=
  single_mem_hostSub toy 1 0 ⟨by simp [toy], by
    intro j hj ht
    fin_cases j <;> simp [toy] at hj ht ⊢ <;> simp [Set.subset_def]⟩

/-- the toy model satisfies the hypotheses of `rescue_corollary` (role a, stages 0,1: rescued by the idle piece {0,1}) -/
theorem toy_corollary :
    (∃ j, ¬ toy.isHost j ∧ (0 : Fin 2) ∈ toy.piece j ∧ toy.piece j ⊆ toy.mask 0) ∨
    (∃ j, ¬ toy.isHost j ∧ (1 : Fin 2) ∈ toy.piece j ∧ toy.piece j ⊆ toy.mask 0) :=
  rescue_corollary toy toy_disjoint 0 0 1 (by decide) (by simp [toy]) (by simp [toy])

end CallerSupport

#print axioms CallerSupport.rescue_at_most_one
#print axioms CallerSupport.rescue_corollary
#print axioms CallerSupport.support_entry
#print axioms CallerSupport.support_host
#print axioms CallerSupport.inst_hosts_disjoint
#print axioms CallerSupport.toy_rescue
#print axioms CallerSupport.toy_corollary
#print axioms CallerSupport.toy_disjoint
