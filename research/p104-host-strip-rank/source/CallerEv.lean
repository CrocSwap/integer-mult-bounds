/-
CallerEv (lane CALLERASM, Nov 20).  RC2 with pieces indexed by EVENTS instead of role instances (no piece->role attribution).

Data: roles `r` with masks `M r` (stage sets), blocks `bh r s`, `ah r s` in K^m, events `e` (an IDLE / QUERY D-incidence) with
support `S e` (the stages it touches), kernel vector `x e` and biorthogonal `y e` (both indexed by roles).
(1) `ev_pair`  : pair form.  s /= t, Ghat_st invertible:
        m + #{events e : s in S e, 2 <= |S e|, (l <= |S e| or t in S e)} <= #{roles r : s in M r, (l <= |M r| or t in M r)}.
    The kernel vectors of the good events at s are independent by biorthogonality (shared stage s), supported on W by
    `S e ⊆ M r`; no role is attached to an event.
(2) `ev_avg`   : averaged row  m k (k-1) + sum_e sum_{s in S e} wl(|S e|) <= sum_r sum_{s in M r} wl(|M r|),   wl d = if l <= d then k-1 else d-1.
(3) `exists_match` : per stage a bijection (roles at s) -> (events at s) with S(ev r s) ⊆ M r  (Hall via det V /= 0, from
    biorthogonality + |roles at s| = |events at s|).  Only the multiset of sizes matters for the objective.
(4) `ev_frame_bound` : with a r s := |S(ev r s)|  the stage form of HP (roleVal, rowS, mains) is an exact re-expression of the
    EVENT-FORM invoice  sum_r (8 D_r + 1)^s - sum_{events} (8 |S e|)^s,  and  104/k * invoice <= HP(k).
Kernel only.
-/
import Nov15.CallerWordHP

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerEv
open Finset Matrix CallerSign CallerHP

section pair
variable {K : Type*} [Field K] {R E : Type*} [Fintype R] [DecidableEq R] [Fintype E] [DecidableEq E] {k m : ℕ}

/-- event data on masks `M`, blocks `bh`, supports `S`. -/
structure EvData (M : R → Finset (Fin k)) (bh : R → Fin k → Fin m → K) (S : E → Finset (Fin k)) where
  x : E → R → K
  y : E → R → K
  x_supp : ∀ e r, x e r ≠ 0 → S e ⊆ M r
  x_ker : ∀ e, 2 ≤ (S e).card → ∀ s' ∈ S e, ∀ a, ∑ r, x e r * bh r s' a = 0
  biorth : ∀ e f, (S e ∩ S f).Nonempty → ∑ r, y e r * x f r = if e = f then 1 else 0

def wSet (M : R → Finset (Fin k)) (s t : Fin k) (l : ℕ) : Finset R :=
  univ.filter fun r => s ∈ M r ∧ (l ≤ (M r).card ∨ t ∈ M r)

def gSet (S : E → Finset (Fin k)) (s t : Fin k) (l : ℕ) : Finset E :=
  univ.filter fun e => s ∈ S e ∧ 2 ≤ (S e).card ∧ (l ≤ (S e).card ∨ t ∈ S e)

theorem ev_pair (M : R → Finset (Fin k)) (bh ah : R → Fin k → Fin m → K) (S : E → Finset (Fin k))
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : EvData M bh S) (s t : Fin k) (hst : s ≠ t) (l : ℕ)
    (hG : IsUnit (gBlk bh ah s t).det) :
    m + (gSet S s t l).card ≤ (wSet M s t l).card := by
  classical
  set W := wSet M s t l with hW
  set Wg := gSet S s t l with hWg
  have hsurj : ∀ v : Fin m → K, ∃ c : R → K, (∀ r, r ∉ W → c r = 0) ∧
      ∀ a, ∑ r, c r * bh r s a = v a := by
    intro v
    have hinv := Matrix.mul_nonsing_inv _ hG
    set w : Fin m → K := (gBlk bh ah s t)⁻¹ *ᵥ v with hw
    have hGw : (gBlk bh ah s t) *ᵥ w = v := by
      rw [hw, Matrix.mulVec_mulVec, hinv, Matrix.one_mulVec]
    refine ⟨fun r => if r ∈ W then ∑ b, ah r t b * w b else 0, ?_, ?_⟩
    · intro r hr; simp [hr]
    · intro a
      rw [← hGw]
      simp only [Matrix.mulVec, dotProduct, gBlk, Matrix.of_apply]
      simp_rw [Finset.sum_mul]
      rw [Finset.sum_comm]
      refine Finset.sum_congr rfl fun r _ => ?_
      by_cases hr : r ∈ W
      · simp only [hr, if_true]
        rw [Finset.sum_mul]
        exact Finset.sum_congr rfl fun b _ => by ring
      · simp only [hr, if_false, zero_mul]
        have : s ∉ M r ∨ t ∉ M r := by
          by_contra h
          push Not at h
          exact hr (Finset.mem_filter.mpr ⟨Finset.mem_univ _, h.1, Or.inr h.2⟩)
        rcases this with h | h
        · simp [hbh r s h, Finset.sum_mul]
        · simp [hah r t h]
  let ι := {e // e ∈ Wg}
  let xs : ι → R → K := fun i => P.x i.1
  have hmemg : ∀ i : ι, s ∈ S i.1 ∧ 2 ≤ (S i.1).card := by
    intro i
    have := (Finset.mem_filter.mp i.2).2
    exact ⟨this.1, this.2.1⟩
  have hind : LinearIndependent K xs := by
    rw [Fintype.linearIndependent_iff]
    intro c hc j
    have h1 : ∑ r'', P.y j.1 r'' * (∑ i, c i * xs i r'') = 0 := by
      have : ∀ r'', ∑ i, c i * xs i r'' = 0 := fun r'' => by
        have := congrFun hc r''
        simpa [Finset.sum_apply] using this
      simp [this]
    have h2 : ∑ r'', P.y j.1 r'' * (∑ i, c i * xs i r'') = c j := by
      simp_rw [Finset.mul_sum]
      rw [Finset.sum_comm]
      have : ∀ i : ι, ∑ r'', P.y j.1 r'' * (c i * xs i r'') = c i * (if j = i then 1 else 0) := by
        intro i
        have hb := P.biorth j.1 i.1 ⟨s, Finset.mem_inter.mpr ⟨(hmemg j).1, (hmemg i).1⟩⟩
        have e : ∑ r'', P.y j.1 r'' * (c i * xs i r'') = c i * ∑ r'', P.y j.1 r'' * P.x i.1 r'' := by
          rw [Finset.mul_sum]
          refine Finset.sum_congr rfl fun r'' _ => ?_
          simp only [xs]; ring
        rw [e, hb]
        congr 1
        exact if_congr Subtype.ext_iff.symm rfl rfl
      simp only [this, mul_ite, mul_one, mul_zero]
      rw [Finset.sum_ite_eq]; simp
    rw [← h2, h1]
  have hsupp : ∀ i r, xs i r ≠ 0 → r ∈ W := by
    intro i r' hr'
    have hsub := P.x_supp i.1 r' hr'
    have hg := (Finset.mem_filter.mp i.2).2
    refine Finset.mem_filter.mpr ⟨Finset.mem_univ _, hsub hg.1, ?_⟩
    rcases hg.2.2 with h | h
    · left; exact h.trans (Finset.card_le_card hsub)
    · right; exact hsub h
  have hker : ∀ i a, ∑ r, xs i r * bh r s a = 0 := by
    intro i a
    exact P.x_ker i.1 (hmemg i).2 s (hmemg i).1 a
  have hmain := CallerSign.rc2_lin W (fun r => bh r s) hsurj xs hind hsupp hker
  have hιcard : Fintype.card ι = Wg.card := Fintype.card_coe Wg
  omega

end pair

section avg
variable {K : Type*} [Field K] {R E : Type*} [Fintype R] [DecidableEq R] [Fintype E] [DecidableEq E] {k m : ℕ}

/-- weight of a stage set of size `d` in the averaged row. -/
def wl (k l d : ℕ) : ℕ := if l ≤ d then k - 1 else d - 1

theorem cnt_t (A : Finset (Fin k)) (s : Fin k) (hs : s ∈ A) (l : ℕ) :
    ∑ t : Fin k, (if s ≠ t ∧ (l ≤ A.card ∨ t ∈ A) then 1 else 0 : ℕ) = wl k l A.card := by
  classical
  rw [Finset.sum_boole]
  unfold wl
  by_cases h : l ≤ A.card
  · have : (univ.filter fun t : Fin k => s ≠ t ∧ (l ≤ A.card ∨ t ∈ A)) = univ.erase s := by
      ext t; simp [h, eq_comm]
    rw [this, Finset.card_erase_of_mem (Finset.mem_univ _)]; simp [h]
  · have : (univ.filter fun t : Fin k => s ≠ t ∧ (l ≤ A.card ∨ t ∈ A)) = A.erase s := by
      ext t; simp [h, eq_comm, and_comm]
    rw [this, Finset.card_erase_of_mem hs]; simp [h]

theorem sum_pairs {X : Type*} [Fintype X] (S : X → Finset (Fin k)) (p : X → Prop) [DecidablePred p] (l : ℕ) :
    ∑ s : Fin k, ∑ t : Fin k, ∑ x : X, (if s ≠ t ∧ s ∈ S x ∧ (l ≤ (S x).card ∨ t ∈ S x) ∧ p x then 1 else 0 : ℕ)
      = ∑ x : X, (if p x then ∑ s ∈ S x, wl k l (S x).card else 0) := by
  classical
  rw [swap3]
  refine Finset.sum_congr rfl fun x _ => ?_
  by_cases hp : p x
  · simp only [hp, if_true, and_true]
    have h : ∑ s ∈ S x, wl k l (S x).card = ∑ s : Fin k, (if s ∈ S x then wl k l (S x).card else 0) := by
      rw [Finset.sum_ite_mem, Finset.univ_inter]
    rw [h]
    refine Finset.sum_congr rfl fun s _ => ?_
    by_cases hs : s ∈ S x
    · simp only [hs, true_and, if_true]
      exact cnt_t (S x) s hs l
    · simp [hs]
  · simp [hp]

theorem card_wSet_pairs (M : R → Finset (Fin k)) (l : ℕ) :
    ∑ s : Fin k, ∑ t : Fin k, (if s ≠ t then (wSet M s t l).card else 0)
      = ∑ r, ∑ s ∈ M r, wl k l (M r).card := by
  classical
  have h := sum_pairs M (fun _ => True) l
  simp only [and_true, if_true] at h
  rw [← h]
  refine Finset.sum_congr rfl fun s _ => Finset.sum_congr rfl fun t _ => ?_
  unfold wSet
  rw [Finset.card_filter]
  by_cases hst : s ≠ t
  · simp only [ne_eq, hst, not_false_eq_true, if_true, true_and]
  · simp [hst]

theorem card_gSet_pairs (S : E → Finset (Fin k)) (l : ℕ) :
    ∑ s : Fin k, ∑ t : Fin k, (if s ≠ t then (gSet S s t l).card else 0)
      = ∑ e, (if 2 ≤ (S e).card then ∑ s ∈ S e, wl k l (S e).card else 0) := by
  classical
  rw [← sum_pairs S (fun e => 2 ≤ (S e).card) l]
  refine Finset.sum_congr rfl fun s _ => Finset.sum_congr rfl fun t _ => ?_
  unfold gSet
  rw [Finset.card_filter]
  by_cases hst : s ≠ t
  · simp only [ne_eq, hst, not_false_eq_true, if_true, true_and]
    refine Finset.sum_congr rfl fun e _ => ?_
    by_cases h1 : s ∈ S e <;> by_cases h2 : 2 ≤ (S e).card <;> simp [h1, h2]
  · simp [hst]

theorem sum_ne_const (c : ℕ) :
    ∑ s : Fin k, ∑ t : Fin k, (if s ≠ t then c else 0) = c * (k * (k - 1)) := by
  classical
  have : ∀ s : Fin k, ∑ t : Fin k, (if s ≠ t then c else 0) = c * (k - 1) := by
    intro s
    rw [← Finset.sum_filter]
    have : (univ.filter fun t : Fin k => s ≠ t) = univ.erase s := by ext t; simp [eq_comm]
    rw [this, Finset.sum_const, Finset.card_erase_of_mem (Finset.mem_univ _)]; simp [mul_comm]
  simp only [this, Finset.sum_const, Finset.card_univ, Fintype.card_fin, smul_eq_mul]
  ring

/-- averaged event RC2 row (any `l`): `m k (k-1) + Σ_e (weights of e's stages) ≤ Σ_r (weights of r's stages)`. -/
theorem ev_avg (M : R → Finset (Fin k)) (bh ah : R → Fin k → Fin m → K) (S : E → Finset (Fin k))
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : EvData M bh S) (hG : ∀ s t, s ≠ t → IsUnit (gBlk bh ah s t).det) (l : ℕ) :
    m * (k * (k - 1)) + ∑ e, (if 2 ≤ (S e).card then ∑ s ∈ S e, wl k l (S e).card else 0)
      ≤ ∑ r, ∑ s ∈ M r, wl k l (M r).card := by
  classical
  rw [← card_wSet_pairs M l, ← card_gSet_pairs S l, ← sum_ne_const (k := k) m, ← Finset.sum_add_distrib]
  refine Finset.sum_le_sum fun s _ => ?_
  rw [← Finset.sum_add_distrib]
  refine Finset.sum_le_sum fun t _ => ?_
  by_cases hst : s ≠ t
  · simp only [ne_eq, hst, not_false_eq_true, if_true]
    exact ev_pair M bh ah S hbh hah P s t hst l (hG s t hst)
  · simp [hst]

end avg

section matching
variable {K : Type*} [Field K] {R E : Type*} [Fintype R] [DecidableEq R] [Fintype E] [DecidableEq E] {k m : ℕ}

/-- per stage a bijection roles-at-s -> events-at-s, event support inside the role's mask. -/
structure Match (M : R → Finset (Fin k)) (S : E → Finset (Fin k)) where
  ev : R → Fin k → E
  mem : ∀ r s, s ∈ M r → s ∈ S (ev r s)
  sub : ∀ r s, s ∈ M r → S (ev r s) ⊆ M r
  inj : ∀ s r r', s ∈ M r → s ∈ M r' → ev r s = ev r' s → r = r'
  surj : ∀ s e, s ∈ S e → ∃ r, s ∈ M r ∧ ev r s = e

theorem sum_match {β : Type*} [AddCommMonoid β] {M : R → Finset (Fin k)} {S : E → Finset (Fin k)}
    (P : Match M S) (g : E → β) :
    ∑ r, ∑ s ∈ M r, g (P.ev r s) = ∑ e, ∑ s ∈ S e, g e := by
  classical
  have h1 : ∑ r, ∑ s ∈ M r, g (P.ev r s) = ∑ s : Fin k, ∑ r ∈ univ.filter (fun r => s ∈ M r), g (P.ev r s) := by
    rw [Finset.sum_comm' (t' := (univ : Finset (Fin k))) (s' := fun s => univ.filter (fun r => s ∈ M r))]
    intro r s; simp
  have h2 : ∑ e, ∑ s ∈ S e, g e = ∑ s : Fin k, ∑ e ∈ univ.filter (fun e => s ∈ S e), g e := by
    rw [Finset.sum_comm' (t' := (univ : Finset (Fin k))) (s' := fun s => univ.filter (fun e => s ∈ S e))]
    intro e s; simp
  rw [h1, h2]
  refine Finset.sum_congr rfl fun s _ => ?_
  refine Finset.sum_bij (fun r _ => P.ev r s) ?_ ?_ ?_ ?_
  · intro r hr
    have := (Finset.mem_filter.mp hr).2
    exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, P.mem r s this⟩
  · intro r hr r' hr' h
    exact P.inj s r r' (Finset.mem_filter.mp hr).2 (Finset.mem_filter.mp hr').2 h
  · intro e he
    obtain ⟨r, hr, hre⟩ := P.surj s e (Finset.mem_filter.mp he).2
    exact ⟨r, Finset.mem_filter.mpr ⟨Finset.mem_univ _, hr⟩, hre⟩
  · intro r _; rfl

/-- one stage: V invertible (biorthogonality) + equal counts  ==>  a bijection with `S e ⊆ M r`. -/
theorem match_stage (M : R → Finset (Fin k)) (bh : R → Fin k → Fin m → K) (S : E → Finset (Fin k))
    (P : EvData M bh S) (s : Fin k) (e₀ : E)
    (hc : (univ.filter fun r => s ∈ M r).card = (univ.filter fun e => s ∈ S e).card) :
    ∃ f : R → E, (∀ r, s ∈ M r → s ∈ S (f r) ∧ S (f r) ⊆ M r) ∧
      (∀ r r', s ∈ M r → s ∈ M r' → f r = f r' → r = r') ∧ (∀ e, s ∈ S e → ∃ r, s ∈ M r ∧ f r = e) := by
  classical
  let Rs := {r // s ∈ M r}
  let Es := {e // s ∈ S e}
  have hcard : Fintype.card Es = Fintype.card Rs := by
    simp only [Es, Rs, Fintype.card_subtype]; exact hc.symm
  let e0 : Es ≃ Rs := Fintype.equivOfCardEq hcard
  let V' : Matrix Rs Rs K := Matrix.of fun i r => P.x (e0.symm i).1 r.1
  let Y' : Matrix Rs Rs K := Matrix.of fun i r => P.y (e0.symm i).1 r.1
  have hYV : Y' * V'ᵀ = 1 := by
    ext i j
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Y', V', Matrix.of_apply]
    have hb := P.biorth (e0.symm i).1 (e0.symm j).1
      ⟨s, Finset.mem_inter.mpr ⟨(e0.symm i).2, (e0.symm j).2⟩⟩
    have hsum : ∑ r : Rs, P.y (e0.symm i).1 r.1 * P.x (e0.symm j).1 r.1
        = ∑ r, P.y (e0.symm i).1 r * P.x (e0.symm j).1 r := by
      rw [← Finset.sum_subtype (univ.filter fun r => s ∈ M r) (by simp)
        (fun r => P.y (e0.symm i).1 r * P.x (e0.symm j).1 r)]
      rw [Finset.sum_filter_of_ne]
      intro r _ hr
      by_contra hs
      apply hr
      have : P.x (e0.symm j).1 r = 0 := by
        by_contra hx
        exact hs ((P.x_supp _ r hx) (e0.symm j).2)
      simp [this]
    rw [hsum, hb, Matrix.one_apply]
    congr 1
    apply propext
    constructor
    · intro h; exact e0.symm.injective (Subtype.ext h)
    · intro h; rw [h]
  have hdet : V'.det ≠ 0 := by
    have h := congrArg Matrix.det hYV
    rw [Matrix.det_mul, Matrix.det_transpose, Matrix.det_one] at h
    intro h0; rw [h0] at h; simp at h
  rw [Matrix.det_apply] at hdet
  obtain ⟨π, -, hπ⟩ := Finset.exists_ne_zero_of_sum_ne_zero hdet
  have hp : ∏ i, V' (π i) i ≠ 0 := fun h => hπ (by rw [h]; simp)
  have hprod : ∀ i, V' (π i) i ≠ 0 := fun i => Finset.prod_ne_zero_iff.mp hp i (Finset.mem_univ i)
  refine ⟨fun r => if h : s ∈ M r then (e0.symm (π ⟨r, h⟩)).1 else e₀, ?_, ?_, ?_⟩
  · intro r hr
    simp only [hr, dif_pos]
    exact ⟨(e0.symm (π ⟨r, hr⟩)).2, P.x_supp _ r (hprod ⟨r, hr⟩)⟩
  · intro r r' hr hr' h
    simp only [hr, hr', dif_pos] at h
    have := π.injective (e0.symm.injective (Subtype.ext h))
    exact congrArg Subtype.val this
  · intro e he
    refine ⟨((π.symm (e0 ⟨e, he⟩)) : Rs).1, ((π.symm (e0 ⟨e, he⟩)) : Rs).2, ?_⟩
    simp only [((π.symm (e0 ⟨e, he⟩)) : Rs).2, dif_pos]
    simp

theorem exists_match (M : R → Finset (Fin k)) (bh : R → Fin k → Fin m → K) (S : E → Finset (Fin k))
    (P : EvData M bh S) (e₀ : E)
    (hc : ∀ s, (univ.filter fun r => s ∈ M r).card = (univ.filter fun e => s ∈ S e).card) :
    Nonempty (Match M S) := by
  classical
  choose F hF1 hF2 hF3 using fun s => match_stage M bh S P s e₀ (hc s)
  exact ⟨⟨fun r s => F s r, fun r s hs => (hF1 s r hs).1, fun r s hs => (hF1 s r hs).2,
    fun s r r' h h' he => hF2 s r r' h h' he, fun s e he => hF3 s e he⟩⟩

end matching

section hp
variable {K : Type*} [Field K] {R E : Type*} [Fintype R] [DecidableEq R] [Fintype E] [DecidableEq E] {k : ℕ}

/-- the EVENT-FORM invoice (sum over roles of `(8 D_r + 1)^σ`, minus `(8 |S e|)^σ` per D-incidence event). -/
noncomputable def invoice (σ : ℝ) (M : R → Finset (Fin k)) (S : E → Finset (Fin k)) : ℝ :=
  ∑ r, (8 * ((M r).card : ℝ) + 1) ^ σ - ∑ e, (if S e = ∅ then 0 else (8 * ((S e).card : ℝ)) ^ σ)

theorem wl_split (l D a : ℕ) (hl : 2 ≤ l) (ha1 : 1 ≤ a) (haD : a ≤ D) (hDk : D ≤ k) :
    wl k l D = wl k l a + (if l ≤ D then (if a < l then k - a else 0) else D - a) := by
  unfold wl
  split_ifs <;> omega

theorem rc_row_nat (M : R → Finset (Fin k)) (bh ah : R → Fin k → Fin 2 → K) (S : E → Finset (Fin k))
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : EvData M bh S) (hG : ∀ s t, s ≠ t → IsUnit (gBlk bh ah s t).det) (Pm : Match M S) (l : ℕ) (hl : 2 ≤ l) :
    2 * (k * (k - 1)) ≤ ∑ r, ∑ s ∈ M r,
      (if l ≤ (M r).card then (if (S (Pm.ev r s)).card < l then k - (S (Pm.ev r s)).card else 0)
        else (M r).card - (S (Pm.ev r s)).card) := by
  have h := ev_avg M bh ah S hbh hah P hG l
  have hA : ∑ e, (if 2 ≤ (S e).card then ∑ s ∈ S e, wl k l (S e).card else 0)
      = ∑ r, ∑ s ∈ M r, wl k l (S (Pm.ev r s)).card := by
    rw [sum_match Pm (fun e => wl k l (S e).card)]
    refine Finset.sum_congr rfl fun e _ => ?_
    by_cases h2 : 2 ≤ (S e).card
    · simp [h2]
    · rw [if_neg h2]
      have : (S e).card = 0 ∨ (S e).card = 1 := by omega
      rcases this with h0 | h1
      · rw [Finset.card_eq_zero.mp h0]; simp
      · simp only [h1, wl]
        have : ¬ l ≤ 1 := by omega
        simp [this]
  have hB : ∑ r, ∑ s ∈ M r, wl k l (M r).card
      = ∑ r, ∑ s ∈ M r, (wl k l (S (Pm.ev r s)).card +
        (if l ≤ (M r).card then (if (S (Pm.ev r s)).card < l then k - (S (Pm.ev r s)).card else 0)
          else (M r).card - (S (Pm.ev r s)).card)) := by
    refine Finset.sum_congr rfl fun r _ => Finset.sum_congr rfl fun s hs => ?_
    refine wl_split l _ _ hl ?_ (Finset.card_le_card (Pm.sub r s hs)) (by simpa using Finset.card_le_univ (M r))
    exact Finset.card_pos.mpr ⟨s, Pm.mem r s hs⟩
  rw [hA, hB] at h
  simp only [Finset.sum_add_distrib] at h
  omega

end hp

section hp2
variable {K : Type*} [Field K] {R E : Type*} [Fintype R] [DecidableEq R] [Fintype E] [DecidableEq E] {k : ℕ}

theorem roleVal_sum (M : R → Finset (Fin k)) (S : E → Finset (Fin k)) (Pm : Match M S) (σ : ℝ) :
    ∑ r, roleVal σ (M r) (fun s => (S (Pm.ev r s)).card) = invoice σ M S := by
  unfold roleVal invoice
  rw [Finset.sum_sub_distrib]
  congr 1
  rw [sum_match Pm (fun e => (8 * ((S e).card : ℝ)) ^ σ / ((S e).card : ℝ))]
  refine Finset.sum_congr rfl fun e _ => ?_
  rw [Finset.sum_const, nsmul_eq_mul]
  by_cases h : S e = ∅
  · simp [h]
  · have hc : ((S e).card : ℝ) ≠ 0 := by
      have := Finset.card_pos.mpr (Finset.nonempty_iff_ne_empty.mpr h)
      exact_mod_cast this.ne'
    rw [if_neg h]; field_simp

theorem mains_sum (M : R → Finset (Fin k)) (S : E → Finset (Fin k)) (Pm : Match M S) :
    ∑ r, mainCnt (M r) (fun s => decide ((S (Pm.ev r s)).card = 1))
      = (((univ.filter fun e => (S e).card = 1).card : ℕ) : ℝ) := by
  unfold mainCnt
  have h := sum_match Pm (fun e => if (S e).card = 1 then (1 : ℝ) else 0)
  simp only [decide_eq_true_eq] at *
  rw [h, Finset.card_filter, Nat.cast_sum]
  refine Finset.sum_congr rfl fun e _ => ?_
  rw [Finset.sum_const, nsmul_eq_mul]
  by_cases h1 : (S e).card = 1 <;> simp [h1]

/-- HEADLINE (abstract event form).  Roles with masks `M` (stage sets), blocks `bh, ah` in K^2, D-incidence events with
supports `S`, kernel/biorthogonal vectors (`EvData`), Ghat_st invertible, `n + 2 <= 2k`, `D_r >= 2`, and at least `2k`
singleton events (MAINS):  the event-form invoice satisfies `104/k * invoice(.99) <= HP(k)`. -/
theorem ev_frame_bound (hk : 3 ≤ k) (M : R → Finset (Fin k)) (bh ah : R → Fin k → Fin 2 → K) (S : E → Finset (Fin k))
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : EvData M bh S) (hG : ∀ s t, s ≠ t → IsUnit (gBlk bh ah s t).det)
    (e₀ : E) (hc : ∀ s, (univ.filter fun r => s ∈ M r).card = (univ.filter fun e => s ∈ S e).card)
    (hn : Fintype.card R + 2 ≤ 2 * k) (hdeg : ∀ r, 2 ≤ (M r).card)
    (hmains : 2 * k ≤ (univ.filter fun e => (S e).card = 1).card) :
    104 / (k : ℝ) * invoice σ0 M S ≤ HPr k := by
  obtain ⟨Pm⟩ := exists_match M bh S P e₀ hc
  have hk3 : (3 : ℝ) ≤ k := by exact_mod_cast hk
  have hcard : (Fintype.card R : ℝ) ≤ 2 * (k : ℝ) - 2 := by
    have : ((Fintype.card R + 2 : ℕ) : ℝ) ≤ ((2 * k : ℕ) : ℝ) := by exact_mod_cast hn
    push_cast at this; linarith
  have hmains' : 2 * (k : ℝ) ≤ ∑ r, mainCnt (M r) (fun s => decide ((S (Pm.ev r s)).card = 1)) := by
    rw [mains_sum M S Pm]; exact_mod_cast hmains
  have hrow : ∀ l ∈ Finset.Icc 3 k, 2 * (k : ℝ) * ((k : ℝ) - 1) ≤
      ∑ r, rowS k (M r) (fun s => (S (Pm.ev r s)).card) l := by
    intro l hl
    have hl3 := (Finset.mem_Icc.mp hl).1
    have h := rc_row_nat M bh ah S hbh hah P hG Pm l (by omega)
    have hc2 : ((2 * (k * (k - 1)) : ℕ) : ℝ) ≤ ((∑ r, ∑ s ∈ M r,
      (if l ≤ (M r).card then (if (S (Pm.ev r s)).card < l then k - (S (Pm.ev r s)).card else 0)
        else (M r).card - (S (Pm.ev r s)).card) : ℕ) : ℝ) := by exact_mod_cast h
    rw [Nat.cast_sum] at hc2
    have e1 : ∀ r, (((∑ s ∈ M r,
      (if l ≤ (M r).card then (if (S (Pm.ev r s)).card < l then k - (S (Pm.ev r s)).card else 0)
        else (M r).card - (S (Pm.ev r s)).card) : ℕ)) : ℝ)
        = rowS k (M r) (fun s => (S (Pm.ev r s)).card) l := by
      intro r
      unfold rowS
      rw [Nat.cast_sum]
      refine Finset.sum_congr rfl fun s hs => ?_
      have hsub := Finset.card_le_card (Pm.sub r s hs)
      have hDk : (M r).card ≤ k := by simpa using Finset.card_le_univ (M r)
      by_cases h1 : l ≤ (M r).card
      · by_cases h2 : (S (Pm.ev r s)).card < l
        · simp only [h1, h2, if_true]
          rw [Nat.cast_sub (by omega)]
        · simp [h1, h2]
      · simp only [h1, if_false]
        rw [Nat.cast_sub hsub]
    simp_rw [e1] at hc2
    have hk1 : 1 ≤ k := by omega
    push_cast [Nat.cast_sub hk1] at hc2
    linarith
  have hT := total_le_le qf_sigma0 (by norm_num : (0:ℝ) < σ0) (by norm_num : σ0 < 1) hk M
    (fun r s => (S (Pm.ev r s)).card) (fun r s => decide ((S (Pm.ev r s)).card = 1)) hdeg
    (fun r => by simpa using Finset.card_le_univ (M r))
    (fun r s hs => Finset.card_pos.mpr ⟨s, Pm.mem r s hs⟩)
    (fun r s hs => Finset.card_le_card (Pm.sub r s hs))
    (fun r s hs hm => by simpa using hm) hcard hrow hmains'
  rw [roleVal_sum M S Pm] at hT
  unfold HPr
  have hk0 : (0 : ℝ) < k := by linarith
  calc 104 / (k : ℝ) * invoice σ0 M S
      ≤ 104 / (k : ℝ) * (2 * (((k : ℝ) - 2) * v2p σ0 + (8 * (k : ℝ) + 1) ^ σ0 - (8 : ℝ) ^ σ0 * k)) :=
        mul_le_mul_of_nonneg_left hT (by positivity)
    _ = _ := by ring

end hp2


/-! ## non-vacuity: CallerRC2's toy (3 roles, 2 stages, a genuine multi-stage kernel vector), now EVENT-indexed:
events e0..e3 = the singleton idles (role 0/1, stage 0/1), e4 = ONE 2-stage event with S = {0,1} and x = (1,0,-1).
No role is attached to e4 (role 2 carries it only through the count). -/
section toy
open CallerSign

def toyS : Fin 5 → Finset (Fin 2) := ![{0}, {0}, {1}, {1}, {0, 1}]

def toyX : Fin 5 → Fin 3 → ℚ := ![![1, 0, 0], ![0, 1, 0], ![1, 0, 0], ![0, 1, 0], ![1, 0, -1]]
def toyY : Fin 5 → Fin 3 → ℚ := ![![1, 0, 1], ![0, 1, 0], ![1, 0, 1], ![0, 1, 0], ![0, 0, -1]]

def toyEv : EvData toyM toyB toyS where
  x := toyX
  y := toyY
  x_supp := by intro e r _; fin_cases e <;> intro t ht <;> simp [toyS, toyM] at ht ⊢
  x_ker := by
    intro e h2 s' hs' a
    fin_cases e <;> simp [toyS] at h2 hs'
    fin_cases a <;> simp [toyX, toyB, Fin.sum_univ_three]
  biorth := by
    intro e f h
    fin_cases e <;> fin_cases f <;> simp [toyS, toyX, toyY, Fin.sum_univ_three] at h ⊢

/-- the event pair form on the toy, `l = 2`: `2 + 1 <= 3`, tight; the one good event is the multi-stage event e4. -/
theorem toy_ev_pair : 2 + (gSet toyS 0 1 2).card ≤ (wSet toyM 0 1 2).card :=
  ev_pair toyM toyB toyA toyS (by intro r s h; exact absurd (by simp [toyM]) h)
    (by intro r s h; exact absurd (by simp [toyM]) h) toyEv 0 1 (by decide) 2 toy_gunit

theorem toy_ev_val : (gSet toyS 0 1 2).card = 1 ∧ (wSet toyM 0 1 2).card = 3 := by
  constructor <;> decide +kernel

theorem toy_ev_piece : 2 ≤ (toyS 4).card ∧ toyX 4 0 ≠ 0 := by
  refine ⟨?_, ?_⟩ <;> simp [toyS, toyX]

end toy


/-! ## non-vacuity of `ev_frame_bound`: CallerSGram's k = 3 design (A3, B3: 4 roles, every role meets every stage),
with one singleton event per (role, stage). -/
section toyHP
open CallerSign

theorem mem_all (r : Fin 4) (s : Fin 3) : s ∈ maskOf A3 B3 r := by
  rw [mem_maskOf]
  refine ⟨⟨r.val % 2, by omega⟩, ?_⟩
  fin_cases r <;> fin_cases s <;> simp [A3, B3, uu, vv]

def sS : Fin 4 × Fin 3 → Finset (Fin 3) := fun p => {p.2}

def sEv : EvData (maskOf A3 B3) (fun r s a => B3 r (s, a)) sS where
  x := fun e r => if r = e.1 then 1 else 0
  y := fun e r => if r = e.1 then 1 else 0
  x_supp := by
    intro e r h t ht
    simp only [sS, Finset.mem_singleton] at ht
    subst ht; exact mem_all r _
  x_ker := by intro e h; simp [sS] at h
  biorth := by
    intro e f h
    obtain ⟨t, ht⟩ := h
    simp only [sS, Finset.mem_inter, Finset.mem_singleton] at ht
    obtain ⟨h1, h2⟩ := ht
    have e2 : e.2 = f.2 := h1.symm.trans h2
    simp only [mul_ite, mul_one, mul_zero, zero_mul]
    rw [Finset.sum_ite_eq']
    simp [Prod.ext_iff, e2, eq_comm]

theorem sEv_hG : ∀ s t : Fin 3, s ≠ t →
    IsUnit (gBlk (fun r s a => B3 r (s, a)) (fun r s a => A3 r (s, a)) s t).det := by
  intro s t hst
  rw [gBlk_eq_blkOf]
  exact sgG_blk_unit A3 B3 (by norm_num) prod_A3B3 (by norm_num) diag_unit_A3B3 s t hst

theorem toy_hp : 104 / ((3 : ℕ) : ℝ) * invoice σ0 (maskOf A3 B3) sS ≤ HPr 3 := by
  refine ev_frame_bound (by norm_num) (maskOf A3 B3) (fun r s a => B3 r (s, a)) (fun r s a => A3 r (s, a)) sS
    ?_ ?_ sEv sEv_hG ((0 : Fin 4), (0 : Fin 3)) ?_ (by simp) ?_ ?_
  · intro r s hs a; by_contra h; exact hs ((mem_maskOf A3 B3 r s).mpr ⟨a, Or.inr h⟩)
  · intro r s hs a; by_contra h; exact hs ((mem_maskOf A3 B3 r s).mpr ⟨a, Or.inl h⟩)
  · intro s
    have h1 : (Finset.univ.filter fun r : Fin 4 => s ∈ maskOf A3 B3 r) = Finset.univ := by
      ext r; simp [mem_all]
    rw [h1]
    simp only [sS, Finset.mem_singleton]
    fin_cases s <;> decide
  · intro r
    have : maskOf A3 B3 r = Finset.univ := by ext s; simp [mem_all]
    rw [this]; simp
  · simp [sS]

end toyHP

end CallerEv

#print axioms CallerEv.ev_pair
#print axioms CallerEv.ev_avg
#print axioms CallerEv.exists_match
#print axioms CallerEv.ev_frame_bound
#print axioms CallerEv.toy_ev_pair
#print axioms CallerEv.toy_ev_val
#print axioms CallerEv.toy_hp
