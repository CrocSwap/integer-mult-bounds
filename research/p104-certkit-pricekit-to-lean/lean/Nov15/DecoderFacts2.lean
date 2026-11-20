/-
DecoderFacts2 (lane LEAN-D56, Nov 18).  cards/WILD/UCEIL/MIX1.md (stage law, MIX8), UC3.md sec 1.
STAGE LAW (general, kernel only).  One live register, event lists: gather u, deposit phi, move (rise price 0 /
descent price = rank, `MvLive`), INIT anywhere, any interleaving.  Cut the trace at its descents:
`prev_k` = events before descent d_k (after d_{k-1}), `T_k` = events after d_k.  A_k = gathers of prev_k,
Y_k = deposit annihilator of T_k.  Then  sum_k (dim A_k - dim (A_k n Y_k))  <=  sum_k d_k   (`stage_law`).
Proof: delete the deposits of prev_k and the gathers of T_k (`Legal.filter`), the window is a `Reach` trace
(`Legal.toReach`), apply `live_desc_price` (UniversalCeiling2).
MIX8: with the named bridge `StageBridge` (rigid supports, = DYADICPORTS rigidity H applied per stage) every
stage costs >= 7 (kernel flats via DecoderFacts.row_span_ge_eight); 8 depositing descents => descent mass >= 56.
-/
import Nov15.UniversalCeiling2
import Nov15.DecoderFacts

open Module UniversalCeiling2
set_option maxHeartbeats 0
namespace DF2

section Stage
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]

inductive Ev (K V : Type*) [Field K] [AddCommGroup V] [Module K V]
  | gather (u : V)
  | deposit (φ : V →ₗ[K] K)
  | move (σ' : Submodule K V) (d : ℕ)

def evMass : Ev K V → ℕ
  | .gather _ => 0
  | .deposit _ => 0
  | .move _ d => d

def mass (l : List (Ev K V)) : ℕ := (l.map evMass).sum

def gsp : List (Ev K V) → Submodule K V
  | [] => ⊥
  | .gather u :: t => Submodule.span K {u} ⊔ gsp t
  | .deposit _ :: t => gsp t
  | .move _ _ :: t => gsp t

def dsp : List (Ev K V) → Submodule K V
  | [] => ⊤
  | .gather _ :: t => dsp t
  | .deposit φ :: t => LinearMap.ker φ ⊓ dsp t
  | .move _ _ :: t => dsp t

/-- Legal live trace from frame `σ`, with deposit annihilator `Y`, ending at frame `τ`. -/
inductive Legal : Submodule K V → Submodule K V → List (Ev K V) → Submodule K V → Prop
  | nil (σ Y : Submodule K V) : Legal σ Y [] σ
  | gather {σ Y τ : Submodule K V} {t : List (Ev K V)} (u : V) :
      u ∈ σ → u ∈ Y → Legal σ Y t τ → Legal σ Y (.gather u :: t) τ
  | deposit {σ Y τ : Submodule K V} {t : List (Ev K V)} (φ : V →ₗ[K] K) :
      σ ≤ LinearMap.ker φ → Legal σ (Y ⊓ LinearMap.ker φ) t τ → Legal σ Y (.deposit φ :: t) τ
  | move {σ σ' Y τ : Submodule K V} {t : List (Ev K V)} (d : ℕ) :
      MvLive σ σ' d → Legal σ' Y t τ → Legal σ Y (.move σ' d :: t) τ

theorem mass_cons (e : Ev K V) (t : List (Ev K V)) : mass (e :: t) = evMass e + mass t := by
  simp [mass]

theorem Legal.toReach {σ Y τ : Submodule K V} {l : List (Ev K V)} (h : Legal σ Y l τ) :
    ∀ (G : Submodule K V) (c : ℕ), Reach (id : Submodule K V → Submodule K V) MvLive σ G Y c →
      Reach (id : Submodule K V → Submodule K V) MvLive τ (G ⊔ gsp l) (Y ⊓ dsp l) (c + mass l) := by
  induction h with
  | nil σ Y => intro G c hR; simpa [gsp, dsp, mass] using hR
  | @gather σ Y τ t u hu hY _ ih =>
    intro G c hR
    have := ih _ _ (Reach.gather (view := (id : Submodule K V → Submodule K V)) u hu hY hR)
    have e : G ⊔ gsp (Ev.gather u :: t) = (G ⊔ Submodule.span K {u}) ⊔ gsp t := by
      simp [gsp, sup_assoc]
    rw [e, mass_cons]; simpa [evMass, dsp] using this
  | @deposit σ Y τ t φ hφ _ ih =>
    intro G c hR
    have := ih _ _ (Reach.deposit (view := (id : Submodule K V → Submodule K V)) φ hφ hR)
    have e : Y ⊓ dsp (Ev.deposit φ :: t) = (Y ⊓ LinearMap.ker φ) ⊓ dsp t := by
      simp [dsp, inf_assoc]
    rw [e, mass_cons]; simpa [evMass, gsp] using this
  | @move σ σ' Y τ t d hm _ ih =>
    intro G c hR
    have := ih _ _ (Reach.move hm hR)
    rw [mass_cons]; simpa [evMass, gsp, dsp, add_assoc] using this

theorem Legal.weaken {σ Y τ : Submodule K V} {l : List (Ev K V)} (h : Legal σ Y l τ) :
    ∀ Y', Y ≤ Y' → Legal σ Y' l τ := by
  induction h with
  | nil σ Y => intro Y' _; exact Legal.nil _ _
  | gather u hu hY _ ih => intro Y' hle; exact Legal.gather u hu (hle hY) (ih Y' hle)
  | deposit φ hφ _ ih => intro Y' hle; exact Legal.deposit φ hφ (ih _ (inf_le_inf_right _ hle))
  | move d hm _ ih => intro Y' hle; exact Legal.move d hm (ih Y' hle)

theorem Legal.filter {σ Y τ : Submodule K V} {l : List (Ev K V)} (h : Legal σ Y l τ)
    (keep : Ev K V → Bool) (hk : ∀ σ' d, keep (.move σ' d) = true) :
    Legal σ Y (l.filter keep) τ := by
  induction h with
  | nil σ Y => simpa using Legal.nil σ Y
  | @gather σ Y τ t u hu hY _ ih =>
    by_cases hb : keep (.gather u) = true
    · rw [List.filter_cons_of_pos hb]; exact Legal.gather u hu hY ih
    · rw [List.filter_cons_of_neg hb]; exact ih
  | @deposit σ Y τ t φ hφ _ ih =>
    by_cases hb : keep (.deposit φ) = true
    · rw [List.filter_cons_of_pos hb]; exact Legal.deposit φ hφ ih
    · rw [List.filter_cons_of_neg hb]; exact ih.weaken Y inf_le_left
  | @move σ σ' Y τ t d hm _ ih =>
    rw [List.filter_cons_of_pos (hk σ' d)]; exact Legal.move d hm ih

theorem Legal.move_inv {σ σ' Y τ : Submodule K V} {t : List (Ev K V)} {d : ℕ}
    (h : Legal σ Y (.move σ' d :: t) τ) : MvLive σ σ' d ∧ Legal σ' Y t τ := by
  cases h with
  | move _ hm h' => exact ⟨hm, h'⟩

theorem Legal.split : ∀ (l1 l2 : List (Ev K V)) {σ Y τ : Submodule K V},
    Legal σ Y (l1 ++ l2) τ → ∃ ρ Y', Legal σ Y l1 ρ ∧ Legal ρ Y' l2 τ := by
  intro l1
  induction l1 with
  | nil => intro l2 σ Y τ h; exact ⟨σ, Y, Legal.nil _ _, by simpa using h⟩
  | cons e t ih =>
    intro l2 σ Y τ h
    rw [List.cons_append] at h
    cases e with
    | gather u =>
      cases h with
      | gather _ hu hY h' =>
        obtain ⟨ρ, Y', h1, h2⟩ := ih l2 h'
        exact ⟨ρ, Y', Legal.gather u hu hY h1, h2⟩
    | deposit φ =>
      cases h with
      | deposit _ hφ h' =>
        obtain ⟨ρ, Y', h1, h2⟩ := ih l2 h'
        exact ⟨ρ, Y', Legal.deposit φ hφ h1, h2⟩
    | move σ' d =>
      cases h with
      | move _ hm h' =>
        obtain ⟨ρ, Y', h1, h2⟩ := ih l2 h'
        exact ⟨ρ, Y', Legal.move d hm h1, h2⟩

def isNotDep : Ev K V → Bool
  | .deposit _ => false
  | _ => true
def isNotGat : Ev K V → Bool
  | .gather _ => false
  | _ => true

theorem gsp_nd (l : List (Ev K V)) : gsp (l.filter isNotDep) = gsp l := by
  induction l with
  | nil => rfl
  | cons e t ih => cases e <;> simp [List.filter_cons, isNotDep, gsp, ih]

theorem dsp_nd (l : List (Ev K V)) : dsp (l.filter isNotDep) = ⊤ := by
  induction l with
  | nil => rfl
  | cons e t ih => cases e <;> simp [List.filter_cons, isNotDep, dsp, ih]

theorem gsp_ng (l : List (Ev K V)) : gsp (l.filter isNotGat) = ⊥ := by
  induction l with
  | nil => rfl
  | cons e t ih => cases e <;> simp [List.filter_cons, isNotGat, gsp, ih]

theorem dsp_ng (l : List (Ev K V)) : dsp (l.filter isNotGat) = dsp l := by
  induction l with
  | nil => rfl
  | cons e t ih => cases e <;> simp [List.filter_cons, isNotGat, dsp, ih]

def Quiet (l : List (Ev K V)) : Prop := ∀ e ∈ l, evMass e = 0

theorem mass_filter_zero {l : List (Ev K V)} (hq : Quiet l) (p : Ev K V → Bool) :
    mass (l.filter p) = 0 := by
  unfold mass
  apply List.sum_eq_zero
  intro x hx
  simp only [List.mem_map, List.mem_filter] at hx
  obtain ⟨e, ⟨he, _⟩, rfl⟩ := hx
  exact hq e he

noncomputable def rk (A Y : Submodule K V) : ℕ := finrank K ↥A - finrank K ↥(A ⊓ Y)

/-- One stage: the window `prev(no deposits) ++ move d ++ T(no gathers)` is a Reach trace, price <= d. -/
theorem stage_window {σ Y1 Y ρ1 ρ2 σ' : Submodule K V} {prev T : List (Ev K V)} {d : ℕ}
    (hprev : Legal σ Y prev ρ1) (hmv : MvLive ρ1 σ' d) (hT : Legal σ' Y1 T ρ2)
    (hqp : Quiet prev) (hqT : Quiet T) : rk (gsp prev) (dsp T) ≤ d := by
  have hk1 : ∀ σ' d, isNotDep (K := K) (V := V) (.move σ' d) = true := fun _ _ => rfl
  have hk2 : ∀ σ' d, isNotGat (K := K) (V := V) (.move σ' d) = true := fun _ _ => rfl
  have L1 : Legal σ ⊤ (prev.filter isNotDep) ρ1 := (hprev.filter isNotDep hk1).weaken ⊤ le_top
  have L2 : Legal σ' (⊤ ⊓ dsp (prev.filter isNotDep)) (T.filter isNotGat) ρ2 :=
    (hT.filter isNotGat hk2).weaken _ (by rw [dsp_nd]; simp)
  have R1 := L1.toReach ⊥ 0 (Reach.init σ)
  have R2 := Reach.move hmv R1
  have R3 := L2.toReach _ _ R2
  have := live_desc_price R3
  rw [gsp_nd, dsp_nd, gsp_ng, dsp_ng, mass_filter_zero hqp, mass_filter_zero hqT] at this
  have e1 : (⊥ ⊔ gsp prev ⊔ ⊥ : Submodule K V) = gsp prev := by simp
  have e2 : (⊤ ⊓ ⊤ ⊓ dsp T : Submodule K V) = dsp T := by simp
  rw [e1, e2] at this
  unfold rk
  omega

structure Stg (K V : Type*) [Field K] [AddCommGroup V] [Module K V] where
  σ' : Submodule K V
  d : ℕ
  T : List (Ev K V)

def flat : List (Stg K V) → List (Ev K V)
  | [] => []
  | s :: r => (Ev.move s.σ' s.d :: s.T) ++ flat r

noncomputable def stageSum : List (Ev K V) → List (Stg K V) → ℕ
  | _, [] => 0
  | prev, s :: r => rk (gsp prev) (dsp s.T) + stageSum s.T r

def dsum : List (Stg K V) → ℕ
  | [] => 0
  | s :: r => s.d + dsum r

/-- **STAGE LAW.**  Sum over depositing descents of r(B_k, A_k) <= descent mass. -/
theorem stage_law : ∀ (st : List (Stg K V)) (prev : List (Ev K V)) (σ Y τ : Submodule K V),
    Legal σ Y (prev ++ flat st) τ → Quiet prev → (∀ s ∈ st, Quiet s.T) → stageSum prev st ≤ dsum st := by
  intro st
  induction st with
  | nil => intros; simp [stageSum, dsum]
  | cons s r ih =>
    intro prev σ Y τ h hp hT
    have h' : Legal σ Y (prev ++ (Ev.move s.σ' s.d :: (s.T ++ flat r))) τ := by
      simpa [flat] using h
    obtain ⟨ρ1, Y1, hprev, hrest⟩ := Legal.split prev _ h'
    obtain ⟨hmv, hrest2⟩ := Legal.move_inv hrest
    obtain ⟨ρ2, Y2, hT', _⟩ := Legal.split s.T (flat r) hrest2
    have hs := stage_window hprev hmv hT' hp (hT s (by simp))
    have := ih s.T s.σ' Y1 τ hrest2 (hT s (by simp)) (fun x hx => hT x (by simp [hx]))
    simp only [stageSum, dsum]
    omega

end Stage

/-! ### MIX8: P104 labels, <= 8 depositing descents -/

section Mix8
abbrev V9 := Fin 9 → ZMod 2

/-- NAMED BRIDGE (DYADICPORTS rigidity H applied to one stage; MIX1 sec 2): the stage's deposit vector x_k and
fresh-gather vector g_k are nonzero lattice functionals, i.e. their port supports are rigid sets; the deposits
at supp x_k annihilate `Y_k` and the gathers at supp g_k lie in `A_k`. -/
def StageBridge (A Y : Submodule (ZMod 2) V9) : Prop :=
  ∃ Dd Dg : Finset (Fin 104), DF.RigidSet Dd ∧ DF.RigidSet Dg ∧
    (∀ p ∈ Dd, ∀ y ∈ Y, DecoderWall.dot y (DF.lq p) = 0) ∧ (∀ p ∈ Dg, DF.lq p ∈ A)

theorem stage_rank_ge_seven (A Y : Submodule (ZMod 2) V9) (h : StageBridge A Y) : 7 ≤ rk A Y := by
  obtain ⟨Dd, Dg, hd, hg, hY, hA⟩ := h
  have h8g := DF.row_span_ge_eight Dg hg
  have h8d := DF.row_span_ge_eight Dd hd
  have hsp : Submodule.span (ZMod 2) (Set.range fun t : Dg => DF.lq t) ≤ A := by
    rw [Submodule.span_le]; rintro _ ⟨t, rfl⟩; exact hA t t.2
  have hA8 : 8 ≤ finrank (ZMod 2) ↥A := h8g.trans (Submodule.finrank_mono hsp)
  have hYann : Y ≤ DecoderWall.annS (fun t : Dd => DF.lq t) := by
    intro y hy
    simp only [DecoderWall.annS, LinearMap.mem_ker]
    funext s
    rw [DecoderWall.Phi_apply]
    exact hY s s.2 y hy
  have h2 := DecoderWall.finrank_annS_add (fun t : Dd => DF.lq t)
  have h1 := (Nat.add_le_add_right (Submodule.finrank_mono hYann) _).trans h2.le
  have h3 : finrank (ZMod 2) ↥(A ⊓ Y) ≤ finrank (ZMod 2) ↥Y := Submodule.finrank_mono inf_le_right
  have h9 : Fintype.card (Fin 9) = 9 := by simp
  unfold rk
  omega

def AllStages (P : Submodule (ZMod 2) V9 → Submodule (ZMod 2) V9 → Prop) :
    List (Ev (ZMod 2) V9) → List (Stg (ZMod 2) V9) → Prop
  | _, [] => True
  | prev, s :: r => P (gsp prev) (dsp s.T) ∧ AllStages P s.T r

theorem stageSum_ge : ∀ (st : List (Stg (ZMod 2) V9)) (prev : List (Ev (ZMod 2) V9)),
    AllStages StageBridge prev st → 7 * st.length ≤ stageSum prev st := by
  intro st
  induction st with
  | nil => intros; simp [stageSum]
  | cons s r ih =>
    intro prev h
    have h1 := stage_rank_ge_seven _ _ h.1
    have h2 := ih s.T h.2
    simp only [stageSum, List.length_cons]
    omega

/-- **MIX8.**  A relay-free mixed live network (one register, any interleaving, free rises) for P104 with
>= 8 depositing descents, every stage bridged to rigid supports (`StageBridge`), has descent mass >= 56.
The >= 8 comes from the I_8 block (UC8); fewer is impossible, more is the open >= 9-stage escape. -/
theorem mix8 (st : List (Stg (ZMod 2) V9)) (prev : List (Ev (ZMod 2) V9)) (σ Y τ : Submodule (ZMod 2) V9)
    (h : Legal σ Y (prev ++ flat st) τ) (hp : Quiet prev) (hT : ∀ s ∈ st, Quiet s.T)
    (hb : AllStages StageBridge prev st) (h8 : 8 ≤ st.length) : 56 ≤ dsum st := by
  have := stageSum_ge st prev hb
  have := stage_law st prev σ Y τ h hp hT
  omega

end Mix8

end DF2

#print axioms DF2.stage_law
#print axioms DF2.stage_rank_ge_seven
#print axioms DF2.mix8
