/-
DecoderBridge (lane LEAN-BRIDGE, Nov 18).  cards/WILD/LEANSWARM/BRIDGE.md.
HostPerp discharged.  Hosted register = chart f (in W), view p f (in V), moves `MvHost` (descents free, rises priced
by rank gain).  Theorem `legalH_toLive`: every legal hosted event list maps (move sigma' d |-> move (p sigma') d)
to a legal LIVE list with the same mass, as soon as p is antitone and rank-complementary.  `perp` (f |-> f^perp for
the dot product on F2^9) is such a p (`perp_anti`, `perp_rank`).  Hence `hosted_mix8`: hosted rise mass >= 56 from
the live stage law (`DF2.mix8`), with hosted StageBridge stated on the perp views.
-/
import Nov15.DecoderFacts2

open Module UniversalCeiling2 DF2
set_option maxHeartbeats 0
set_option linter.unusedSectionVars false
namespace DB

section Host
variable {K V W : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]
  [AddCommGroup W] [Module K W] [FiniteDimensional K W]

/-- Hosted events: gather/deposit act on the view in V; moves change the chart in W. -/
inductive HEv (K V W : Type*) [Field K] [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]
  | gather (u : V)
  | deposit (φ : V →ₗ[K] K)
  | move (σ' : Submodule K W) (d : ℕ)

def toLive (p : Submodule K W → Submodule K V) : HEv K V W → Ev K V
  | .gather u => .gather u
  | .deposit φ => .deposit φ
  | .move σ' d => .move (p σ') d

def hevMass : HEv K V W → ℕ
  | .gather _ => 0
  | .deposit _ => 0
  | .move _ d => d

theorem evMass_toLive (p : Submodule K W → Submodule K V) (e : HEv K V W) :
    evMass (toLive p e) = hevMass e := by
  cases e <;> rfl

/-- Legal hosted trace from chart `σ`, annihilator `Y`, ending at chart `τ`; view is `p σ`. -/
inductive LegalH (p : Submodule K W → Submodule K V) :
    Submodule K W → Submodule K V → List (HEv K V W) → Submodule K W → Prop
  | nil (σ : Submodule K W) (Y : Submodule K V) : LegalH p σ Y [] σ
  | gather {σ Y τ t} (u : V) : u ∈ p σ → u ∈ Y → LegalH p σ Y t τ → LegalH p σ Y (.gather u :: t) τ
  | deposit {σ Y τ t} (φ : V →ₗ[K] K) : p σ ≤ LinearMap.ker φ →
      LegalH p σ (Y ⊓ LinearMap.ker φ) t τ → LegalH p σ Y (.deposit φ :: t) τ
  | move {σ σ' Y τ t} (d : ℕ) : MvHost σ σ' d → LegalH p σ' Y t τ → LegalH p σ Y (.move σ' d :: t) τ

/-- A hosted move is a live move of the perp view with the same price. -/
theorem mvHost_mvLive (p : Submodule K W → Submodule K V) (n : ℕ)
    (hanti : ∀ f f' : Submodule K W, f ≤ f' → p f' ≤ p f)
    (hrk : ∀ f : Submodule K W, finrank K ↥f + finrank K ↥(p f) = n)
    {σ σ' : Submodule K W} {d : ℕ} (h : MvHost σ σ' d) : MvLive (p σ) (p σ') d := by
  rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩
  · left; exact ⟨hanti _ _ h1, h2⟩
  · right
    have := Submodule.finrank_mono h1
    have e1 := hrk σ
    have e2 := hrk σ'
    exact ⟨hanti _ _ h1, by omega⟩

theorem legalH_toLive (p : Submodule K W → Submodule K V) (n : ℕ)
    (hanti : ∀ f f' : Submodule K W, f ≤ f' → p f' ≤ p f)
    (hrk : ∀ f : Submodule K W, finrank K ↥f + finrank K ↥(p f) = n)
    {σ τ : Submodule K W} {Y : Submodule K V} {l : List (HEv K V W)} (h : LegalH p σ Y l τ) :
    Legal (p σ) Y (l.map (toLive p)) (p τ) := by
  induction h with
  | nil σ Y => exact Legal.nil _ _
  | gather u hu hY _ ih => exact Legal.gather u hu hY ih
  | deposit φ hφ _ ih => exact Legal.deposit φ hφ ih
  | move d hm _ ih => exact Legal.move d (mvHost_mvLive p n hanti hrk hm) ih

theorem mass_toLive (p : Submodule K W → Submodule K V) (l : List (HEv K V W)) :
    DF2.mass (l.map (toLive p)) = (l.map hevMass).sum := by
  unfold DF2.mass
  rw [List.map_map]
  congr 1
  apply List.map_congr_left
  intro e _
  exact evMass_toLive p e

structure HStg (K V W : Type*) [Field K] [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W] where
  σ' : Submodule K W
  d : ℕ
  T : List (HEv K V W)

def hflat : List (HStg K V W) → List (HEv K V W)
  | [] => []
  | s :: r => (HEv.move s.σ' s.d :: s.T) ++ hflat r

def toLiveStg (p : Submodule K W → Submodule K V) (s : HStg K V W) : Stg K V := ⟨p s.σ', s.d, s.T.map (toLive p)⟩

def hdsum : List (HStg K V W) → ℕ
  | [] => 0
  | s :: r => s.d + hdsum r

theorem flat_toLive (p : Submodule K W → Submodule K V) : ∀ st : List (HStg K V W),
    flat (st.map (toLiveStg p)) = (hflat st).map (toLive p) := by
  intro st
  induction st with
  | nil => rfl
  | cons s r ih =>
    simp only [List.map_cons, flat, hflat, List.map_append, ih, toLiveStg, toLive]

theorem dsum_toLive (p : Submodule K W → Submodule K V) : ∀ st : List (HStg K V W),
    DF2.dsum (st.map (toLiveStg p)) = hdsum st := by
  intro st
  induction st with
  | nil => rfl
  | cons s r ih => simp only [List.map_cons, DF2.dsum, hdsum, ih, toLiveStg]

end Host

/-! ### The perp map on F2^9 -/
section Perp
open DecoderWall

noncomputable instance fintypeSub (f : Submodule (ZMod 2) V9) : Fintype ↥f := Fintype.ofFinite _

/-- `f^perp` for the dot product on `F2^9`. -/
noncomputable def perp (f : Submodule (ZMod 2) V9) : Submodule (ZMod 2) V9 :=
  annS (fun t : f => (t : V9))

theorem mem_perp (f : Submodule (ZMod 2) V9) (v : V9) :
    v ∈ perp f ↔ ∀ x ∈ f, dot v x = 0 := by
  unfold perp
  simp only [annS, LinearMap.mem_ker]
  constructor
  · intro h x hx
    have := congrFun h ⟨x, hx⟩
    rwa [Phi_apply] at this
  · intro h
    funext s
    rw [Phi_apply]
    exact h s s.2

theorem perp_anti (f f' : Submodule (ZMod 2) V9) (h : f ≤ f') : perp f' ≤ perp f := by
  intro v hv
  rw [mem_perp] at hv ⊢
  exact fun x hx => hv x (h hx)

theorem perp_rank (f : Submodule (ZMod 2) V9) :
    finrank (ZMod 2) ↥f + finrank (ZMod 2) ↥(perp f) = 9 := by
  have h := finrank_annS_add (fun t : f => (t : V9))
  have e : Submodule.span (ZMod 2) (Set.range fun t : f => (t : V9)) = f := by
    have : (Set.range fun t : f => (t : V9)) = (f : Set V9) := by
      ext x; simp
    rw [this, Submodule.span_coe_eq_restrictScalars]
    simp
  rw [e] at h
  have hp : perp f = annS (fun t : f => (t : V9)) := by unfold perp; rfl
  rw [hp, Nat.add_comm, h]
  simp

/-- **HostPerp, proved.**  Hosted charts in `F2^9` with view `f^perp`: a hosted stage list (descents of the chart
free, rises priced by rank gain) whose perp-view stages satisfy `StageBridge` and with >= 8 depositing rises has
rise mass >= 56.  Reduces to the live `mix8`. -/
theorem hosted_mix8 (st : List (HStg (ZMod 2) V9 V9)) (prev : List (HEv (ZMod 2) V9 V9))
    (σ τ : Submodule (ZMod 2) V9) (Y : Submodule (ZMod 2) V9)
    (h : LegalH perp σ Y (prev ++ hflat st) τ)
    (hp : ∀ e ∈ prev, hevMass e = 0) (hT : ∀ s ∈ st, ∀ e ∈ s.T, hevMass e = 0)
    (hb : AllStages StageBridge (prev.map (toLive perp)) (st.map (toLiveStg perp)))
    (h8 : 8 ≤ st.length) : 56 ≤ hdsum st := by
  have hL := legalH_toLive perp 9 perp_anti perp_rank h
  rw [List.map_append, ← flat_toLive] at hL
  have := mix8 (st.map (toLiveStg perp)) (prev.map (toLive perp)) _ _ _ hL
    (by intro e he; obtain ⟨e', he', rfl⟩ := List.mem_map.1 he; rw [evMass_toLive]; exact hp e' he')
    (by
      intro s hs
      obtain ⟨s', hs', rfl⟩ := List.mem_map.1 hs
      intro e he
      obtain ⟨e', he', rfl⟩ := List.mem_map.1 he
      rw [evMass_toLive]; exact hT s' hs' e' he')
    hb (by simpa using h8)
  rwa [dsum_toLive] at this

end Perp
end DB

#print axioms DB.legalH_toLive
#print axioms DB.perp_rank
#print axioms DB.hosted_mix8
