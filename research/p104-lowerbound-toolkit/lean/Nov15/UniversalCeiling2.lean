/-
UniversalCeiling2 (lane LEAN-UC, Nov 18).  cards/WILD/UCEIL/UC3.md sec 1-2, UC4.md sec 1, AUDIT1.md (b).
(2) PER-REGISTER DIRECTION SPLIT.  One register = a chart path in the subspace lattice.  Gathers u (u in the
    chart and u in Y = annihilator of the deposits so far), deposits phi (chart <= ker phi), rises, descents.
    Potential Phi = dim G - dim (G n chart n Y):  never raised by gather / deposit / rise, raised by <= d by a
    rank-d descent.  So  dim G - dim (G n Y)  (the DEC row price r(B,A)) <= total DESCENT mass  (`live_desc_price`).
    Hosted: same model along f |-> p f (p antitone, rank-complementary): rises are descents of p f of equal
    rank  (`host_rise_price`).  Mixed chains and INIT-anywhere are covered: any path is allowed.
    `owned_mass_ge_two_mstar_price` restates OwnedFloor.B1 with PRICE hypotheses (CL <= desc mass, CH <= rise
    mass) instead of the literally false  RL S -> RL (S.filter isDesc)  (deleting a rise breaks the word).
(3) RESTORE-FREE SIMULATION (abstract, UC4): every public register makes <= 1 MOVE, the owned layer is
    verbatim, couriers net 0.  Event-list model only: no chart geometry.
Kernel only, no sorry / native_decide / axioms.
-/
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

set_option linter.unusedSectionVars false
namespace UniversalCeiling2
open Module

section Dir
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]

/-- descent by d changes dim (f n Z) by at most d. -/
theorem desc_bound (f f' Z : Submodule K V) (h : f' ≤ f) :
    finrank K ↥(f ⊓ Z) ≤ finrank K ↥(f' ⊓ Z) + (finrank K ↥f - finrank K ↥f') := by
  have h1 := Submodule.finrank_sup_add_finrank_inf_eq f' (f ⊓ Z)
  have e : f' ⊓ (f ⊓ Z) = f' ⊓ Z := by
    rw [← inf_assoc, inf_eq_left.2 h]
  rw [e] at h1
  have h2 : finrank K ↥(f' ⊔ f ⊓ Z) ≤ finrank K ↥f :=
    Submodule.finrank_mono (sup_le h inf_le_left)
  have h3 : finrank K ↥f' ≤ finrank K ↥f := Submodule.finrank_mono h
  omega

variable {S : Type*}

/-- One register.  `view σ` is the live subspace the chart carries (live: the chart itself; hosted: p of it);
`Mv σ σ' d` is a MOVE of price d. -/
inductive Reach (view : S → Submodule K V) (Mv : S → S → ℕ → Prop) :
    S → Submodule K V → Submodule K V → ℕ → Prop
  | init (σ : S) : Reach view Mv σ ⊥ ⊤ 0
  | gather {σ : S} {G Y : Submodule K V} {c : ℕ} (u : V) :
      u ∈ view σ → u ∈ Y → Reach view Mv σ G Y c →
      Reach view Mv σ (G ⊔ Submodule.span K {u}) Y c
  | deposit {σ : S} {G Y : Submodule K V} {c : ℕ} (φ : V →ₗ[K] K) :
      view σ ≤ LinearMap.ker φ → Reach view Mv σ G Y c →
      Reach view Mv σ G (Y ⊓ LinearMap.ker φ) c
  | move {σ σ' : S} {G Y : Submodule K V} {c d : ℕ} :
      Mv σ σ' d → Reach view Mv σ G Y c → Reach view Mv σ' G Y (c + d)

theorem reach_invariant (view : S → Submodule K V) (Mv : S → S → ℕ → Prop)
    (hMv : ∀ σ σ' d, Mv σ σ' d → view σ ≤ view σ' ∨
      (view σ' ≤ view σ ∧ finrank K ↥(view σ) ≤ finrank K ↥(view σ') + d))
    {σ : S} {G Y : Submodule K V} {c : ℕ} (h : Reach view Mv σ G Y c) :
    finrank K ↥G ≤ c + finrank K ↥(G ⊓ (view σ ⊓ Y)) := by
  induction h with
  | init σ => simp
  | @gather σ G Y c u hu hY _ ih =>
    set w : Submodule K V := Submodule.span K {u} with hw
    have hwX : w ≤ view σ ⊓ Y := by
      rw [hw, Submodule.span_singleton_le_iff_mem]; exact ⟨hu, hY⟩
    have e1 : (G ⊔ w) ⊓ (view σ ⊓ Y) = w ⊔ G ⊓ (view σ ⊓ Y) := by
      rw [sup_comm, sup_inf_assoc_of_le G hwX]
    have e2 : w ⊓ (G ⊓ (view σ ⊓ Y)) = G ⊓ w := by
      rw [inf_left_comm, inf_eq_left.2 hwX, inf_comm]
    have a1 := Submodule.finrank_sup_add_finrank_inf_eq G w
    have a2 := Submodule.finrank_sup_add_finrank_inf_eq w (G ⊓ (view σ ⊓ Y))
    rw [e2] at a2
    rw [e1]
    have : (w ⊔ G ⊓ (view σ ⊓ Y)) = (w ⊔ G ⊓ (view σ ⊓ Y)) := rfl
    omega
  | @deposit σ G Y c φ hφ _ ih =>
    have e : view σ ⊓ (Y ⊓ LinearMap.ker φ) = view σ ⊓ Y :=
      le_antisymm (inf_le_inf_left _ inf_le_left)
        (le_inf inf_le_left (le_inf inf_le_right (inf_le_left.trans hφ)))
    rw [e]; exact ih
  | @move σ σ' G Y c d hm _ ih =>
    rcases hMv σ σ' d hm with hr | ⟨hd, hk⟩
    · have : finrank K ↥(G ⊓ (view σ ⊓ Y)) ≤ finrank K ↥(G ⊓ (view σ' ⊓ Y)) :=
        Submodule.finrank_mono (inf_le_inf_left _ (inf_le_inf_right _ hr))
      omega
    · have a := desc_bound (view σ) (view σ') (G ⊓ Y) hd
      have e1 : G ⊓ (view σ ⊓ Y) = view σ ⊓ (G ⊓ Y) := inf_left_comm _ _ _
      have e2 : G ⊓ (view σ' ⊓ Y) = view σ' ⊓ (G ⊓ Y) := inf_left_comm _ _ _
      rw [e1] at ih
      rw [e2]
      omega

/-- Price of the live row r(B,A) = dim G - dim (G n Y) is at most the total price paid by the moves. -/
theorem reach_price (view : S → Submodule K V) (Mv : S → S → ℕ → Prop)
    (hMv : ∀ σ σ' d, Mv σ σ' d → view σ ≤ view σ' ∨
      (view σ' ≤ view σ ∧ finrank K ↥(view σ) ≤ finrank K ↥(view σ') + d))
    {σ : S} {G Y : Submodule K V} {c : ℕ} (h : Reach view Mv σ G Y c) :
    finrank K ↥G ≤ c + finrank K ↥(G ⊓ Y) := by
  have := reach_invariant view Mv hMv h
  have h2 : finrank K ↥(G ⊓ (view σ ⊓ Y)) ≤ finrank K ↥(G ⊓ Y) :=
    Submodule.finrank_mono (inf_le_inf_left _ inf_le_right)
  omega

/-- LIVE: moves are rises (price 0) or descents (price = rank).  Row price <= descent mass. -/
def MvLive (σ σ' : Submodule K V) (d : ℕ) : Prop :=
  (σ ≤ σ' ∧ d = 0) ∨ (σ' ≤ σ ∧ d = finrank K ↥σ - finrank K ↥σ')

theorem live_desc_price {σ G Y : Submodule K V} {c : ℕ}
    (h : Reach (id : Submodule K V → Submodule K V) MvLive σ G Y c) :
    finrank K ↥G ≤ c + finrank K ↥(G ⊓ Y) := by
  refine reach_price id MvLive ?_ h
  intro a b d hm
  rcases hm with ⟨h1, _⟩ | ⟨h1, h2⟩
  · left; exact h1
  · right
    have := Submodule.finrank_mono h1
    exact ⟨h1, by show finrank K ↥a ≤ finrank K ↥b + d; omega⟩

end Dir

section Host
variable {K V W : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]
  [AddCommGroup W] [Module K W] [FiniteDimensional K W]

/-- HOSTED: chart f in W, view = p f in V with p antitone and rank-complementary.  Moves: descents free,
rises priced by rank.  Row price <= RISE mass (rises of f are descents of p f of equal rank). -/
def MvHost (σ σ' : Submodule K W) (d : ℕ) : Prop :=
  (σ' ≤ σ ∧ d = 0) ∨ (σ ≤ σ' ∧ d = finrank K ↥σ' - finrank K ↥σ)

theorem host_rise_price (p : Submodule K W → Submodule K V) (n : ℕ)
    (hanti : ∀ f f' : Submodule K W, f ≤ f' → p f' ≤ p f)
    (hrk : ∀ f : Submodule K W, finrank K ↥f + finrank K ↥(p f) = n)
    {σ : Submodule K W} {G Y : Submodule K V} {c : ℕ}
    (h : Reach p MvHost σ G Y c) :
    finrank K ↥G ≤ c + finrank K ↥(G ⊓ Y) := by
  refine reach_price p MvHost ?_ h
  intro a b d hm
  rcases hm with ⟨h1, _⟩ | ⟨h1, h2⟩
  · left; exact hanti _ _ h1
  · right
    have := Submodule.finrank_mono h1
    have e1 := hrk a
    have e2 := hrk b
    exact ⟨hanti _ _ h1, by omega⟩

end Host

section Floor
open Finset
variable {M : Type*} [DecidableEq M]

/-- OwnedFloor.B1 with PRICE hypotheses.  hL_price : the live row price is paid by descents;
hH_price : the hosted row price is paid by rises (both are `live_desc_price` / `host_rise_price`). -/
theorem owned_mass_ge_two_mstar_price (mass : M → ℕ) (isDesc : M → Prop) [DecidablePred isDesc]
    (S : Finset M) (CL CH mstar : ℕ)
    (hL_price : CL ≤ ∑ x ∈ S.filter isDesc, mass x)
    (hH_price : CH ≤ ∑ x ∈ S.filter (fun x => ¬ isDesc x), mass x)
    (hmL : mstar ≤ CL) (hmH : mstar ≤ CH) :
    2 * mstar ≤ ∑ x ∈ S, mass x := by
  have h3 : ∑ x ∈ S.filter isDesc, mass x + ∑ x ∈ S.filter (fun x => ¬ isDesc x), mass x
      = ∑ x ∈ S, mass x := by
    convert Finset.sum_filter_add_sum_filter_not S isDesc mass
  omega

/-- Many registers: per-register prices add up (registers have disjoint MOVEs). -/
theorem owned_mass_ge_two_mstar_registers {ι : Type*} (R : Finset ι) (CL CH desc rise : ι → ℕ)
    (mstar : ℕ) (hL : ∀ i ∈ R, CL i ≤ desc i) (hH : ∀ i ∈ R, CH i ≤ rise i)
    (hmL : mstar ≤ ∑ i ∈ R, CL i) (hmH : mstar ≤ ∑ i ∈ R, CH i) :
    2 * mstar ≤ ∑ i ∈ R, (desc i + rise i) := by
  have a := Finset.sum_le_sum hL
  have b := Finset.sum_le_sum hH
  rw [Finset.sum_add_distrib]
  omega

end Floor

section Sim
/-- Abstract event list: public MOVE of register r with rank k, owned MOVE of rank k, any other op. -/
inductive Ev | pub (r k : ℕ) | own (k : ℕ) | op
  deriving DecidableEq

/-- number of public MOVEs of register x. -/
def cnt (x : ℕ) : List Ev → ℕ
  | [] => 0
  | Ev.pub r _ :: t => (if r = x then 1 else 0) + cnt x t
  | _ :: t => cnt x t

def ownRanks : List Ev → List ℕ
  | [] => []
  | Ev.own k :: t => k :: ownRanks t
  | _ :: t => ownRanks t

/-- Each public MOVE becomes: birth, COPY (both `op`), one MOVE of the fresh courier N+i.  Owned and ops verbatim. -/
def simAux (N : ℕ) : ℕ → List Ev → List Ev
  | _, [] => []
  | i, Ev.pub _ k :: t => Ev.op :: Ev.op :: Ev.pub (N + i) k :: simAux N (i + 1) t
  | i, e :: t => e :: simAux N (i + 1) t

/-- W' = couriers, then one final jump per original public register (rank `jump r`). -/
def sim (N : ℕ) (jump : ℕ → ℕ) (regs : List ℕ) (W : List Ev) : List Ev :=
  simAux N 0 W ++ regs.map (fun r => Ev.pub r (jump r))

theorem simAux_cnt (N x : ℕ) (W : List Ev) : ∀ i, cnt x (simAux N i W) ≤ 1 ∧ (x < N + i → cnt x (simAux N i W) = 0) := by
  induction W with
  | nil => intro i; simp [simAux, cnt]
  | cons e t ih =>
    intro i
    have h := ih (i + 1)
    cases e with
    | pub r k =>
      simp only [simAux, cnt]
      by_cases hx : x = N + i
      · have : cnt x (simAux N (i + 1) t) = 0 := h.2 (by omega)
        subst hx
        simp [this]
      · have hx' : ¬ (N + i = x) := fun h' => hx h'.symm
        simp only [hx', if_false, zero_add]
        refine ⟨h.1, fun hlt => h.2 (by omega)⟩
    | own k => simpa [simAux, cnt] using ⟨h.1, fun hlt => h.2 (by omega)⟩
    | op => simpa [simAux, cnt] using ⟨h.1, fun hlt => h.2 (by omega)⟩

theorem cnt_jumps (jump : ℕ → ℕ) (regs : List ℕ) (hnd : regs.Nodup) (x : ℕ) :
    cnt x (regs.map (fun r => Ev.pub r (jump r))) ≤ 1 ∧ (x ∉ regs → cnt x (regs.map (fun r => Ev.pub r (jump r))) = 0) := by
  induction regs with
  | nil => simp [cnt]
  | cons a t ih =>
    have hnd' := List.nodup_cons.1 hnd
    have h := ih hnd'.2
    simp only [List.map_cons, cnt]
    by_cases hax : a = x
    · subst hax
      have : cnt a (t.map (fun r => Ev.pub r (jump r))) = 0 := h.2 hnd'.1
      simp [this]
    · simp only [hax, if_false, zero_add]
      exact ⟨h.1, fun hn => h.2 (fun hm => hn (List.mem_cons_of_mem _ hm))⟩

/-- RESTORE-FREE SIMULATION (UC4 sec 1): every public register makes at most 1 MOVE in W'. -/
theorem sim_one_move (N : ℕ) (jump : ℕ → ℕ) (regs : List ℕ) (hnd : regs.Nodup)
    (hN : ∀ r ∈ regs, r < N) (W : List Ev) (x : ℕ) : cnt x (sim N jump regs W) ≤ 1 := by
  have cnt_append : ∀ (a b : List Ev), cnt x (a ++ b) = cnt x a + cnt x b := by
    intro a b
    induction a with
    | nil => simp [cnt]
    | cons e t ih =>
      cases e <;> simp [cnt, ih] <;> omega
  unfold sim
  rw [cnt_append]
  have a := simAux_cnt N x W 0
  have b := cnt_jumps jump regs hnd x
  by_cases hx : x < N
  · have := a.2 (by omega); omega
  · have hnot : x ∉ regs := fun hm => hx (hN x hm)
    have := b.2 hnot; omega

/-- the owned layer of W' is W's own (same paid histogram). -/
theorem sim_owned (N : ℕ) (jump : ℕ → ℕ) (regs : List ℕ) (W : List Ev) :
    ownRanks (sim N jump regs W) = ownRanks W := by
  have h : ∀ i (W : List Ev), ownRanks (simAux N i W) = ownRanks W := by
    intro i W
    induction W generalizing i with
    | nil => rfl
    | cons e t ih =>
      cases e <;> simp [simAux, ownRanks, ih]
  have h2 : ∀ (a : List Ev), ownRanks (a ++ regs.map (fun r => Ev.pub r (jump r))) = ownRanks a := by
    intro a
    induction a with
    | nil =>
      induction regs with
      | nil => rfl
      | cons r t ih => simpa [ownRanks] using ih
    | cons e t ih => cases e <;> simp [ownRanks, ih]
  unfold sim; rw [h2, h]

/-- a one-MOVE courier lifetime has climb T = paid P: net T - P = 0 (invoice coefficient 0). -/
theorem courier_net_zero (k : ℕ) : ((k : ℤ) - k) = 0 := by simp

end Sim
end UniversalCeiling2
