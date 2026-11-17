/-
CARRIER-FORCE (NEWNATIVE R2 sec B / R1 sec 4), lane LEAN-NEXT38, Nov 17. See CarrierForce.md.
Frames = submodules (FrameSep.Route).  Content as membership.  Per-cluster hypotheses explicit:
 (Pub)  every register route in the cluster is public (no owned step touches the cluster's charts);
 (Held) HeldAlone u: any frame containing u is the frame of a carrier that ascended from the line span{u}.
-/
import Nov15.FrameSep
import Mathlib.LinearAlgebra.LinearIndependent.Basic
import Mathlib.LinearAlgebra.Dimension.Finrank
import Mathlib.LinearAlgebra.FiniteDimensional.Defs
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.LinearAlgebra.Dimension.Constructions

namespace CarrierForce
open FrameSep

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- line chart of a port vector -/
abbrev ln (u : V) : Submodule K V := Submodule.span K {u}

section Indep
variable {u₁ u₂ : V}

theorem not_mem_line (h : LinearIndependent K ![u₁, u₂]) : u₁ ∉ (ln u₂ : Submodule K V) := by
  intro hm
  obtain ⟨a, ha⟩ := Submodule.mem_span_singleton.mp hm
  rw [LinearIndependent.pair_iff] at h
  have := h 1 (-a) (by simp [ha])
  simp at this

theorem not_mem_line' (h : LinearIndependent K ![u₁, u₂]) : u₂ ∉ (ln u₁ : Submodule K V) := by
  have h' : LinearIndependent K ![u₂, u₁] := by
    rw [LinearIndependent.pair_iff] at h ⊢
    intro s t hst
    have := h t s (by rw [add_comm]; exact hst)
    exact ⟨this.2, this.1⟩
  exact not_mem_line h'

theorem lines_ne (h : LinearIndependent K ![u₁, u₂]) : (ln u₁ : Submodule K V) ≠ ln u₂ := by
  intro e
  exact not_mem_line h (e ▸ Submodule.mem_span_singleton_self u₁)

/-- a public route cannot pass through both port lines (ladder passes exactly one line) -/
theorem no_two_lines (h : LinearIndependent K ![u₁, u₂]) (R : Route K V) (hR : R.IsPublic)
    {s t : ℕ} (hs : R.f s = ln u₁) (ht : R.f t = ln u₂) : False := by
  rcases le_total s t with hst | hts
  · have := hR.mono hst
    rw [hs, ht] at this
    exact not_mem_line h (this (Submodule.mem_span_singleton_self u₁))
  · have := hR.mono hts
    rw [hs, ht] at this
    exact not_mem_line' h (this (Submodule.mem_span_singleton_self u₂))

/-- the plane -/
abbrev plane (u₁ u₂ : V) : Submodule K V := ln u₁ ⊔ ln u₂

theorem finrank_plane (h : LinearIndependent K ![u₁, u₂]) :
    Module.finrank K (plane u₁ u₂ : Submodule K V) = 2 := by
  have hr : Set.range ![u₁, u₂] = {u₁, u₂} := by
    ext x; simp [or_comm]
  have e : (plane u₁ u₂ : Submodule K V) = Submodule.span K (Set.range ![u₁, u₂]) := by
    rw [hr, Submodule.span_insert]
  rw [e, finrank_span_eq_card h]; simp


/-- the only chart of rank <= 2 that contains both ports is the plane -/
theorem chart_eq_plane (h : LinearIndependent K ![u₁, u₂]) {c : Submodule K V}
    (h1 : u₁ ∈ c) (h2 : u₂ ∈ c) [FiniteDimensional K c] (hc : Module.finrank K c ≤ 2) :
    c = plane u₁ u₂ := by
  have hle : (plane u₁ u₂ : Submodule K V) ≤ c :=
    sup_le ((Submodule.span_singleton_le_iff_mem _ _).2 h1)
      ((Submodule.span_singleton_le_iff_mem _ _).2 h2)
  have hfp := finrank_plane h
  exact (Submodule.eq_of_le_of_finrank_le hle (by omega)).symm

theorem line_lt_plane (h : LinearIndependent K ![u₁, u₂]) :
    (ln u₁ : Submodule K V) < plane u₁ u₂ ∧ (ln u₂ : Submodule K V) < plane u₁ u₂ := by
  refine ⟨lt_of_le_of_ne le_sup_left fun e => ?_, lt_of_le_of_ne le_sup_right fun e => ?_⟩
  · exact not_mem_line' h (e ▸ (le_sup_right : ln u₂ ≤ plane u₁ u₂) (Submodule.mem_span_singleton_self u₂))
  · exact not_mem_line h (e ▸ (le_sup_left : ln u₁ ≤ plane u₁ u₂) (Submodule.mem_span_singleton_self u₁))

end Indep

/-- Held alone: a frame holding `u` is the frame of some carrier of the family that has
  ascended from the line chart `ln u` (no other origin of `u` content in the cluster). -/
def HeldAlone (𝓡 : Set (Route K V)) (u : V) : Prop :=
  ∀ R ∈ 𝓡, ∀ t, u ∈ R.f t → ∃ Q ∈ 𝓡, ∃ s₀ s₁, s₀ ≤ s₁ ∧ Q.f s₀ = ln u ∧ Q.f s₁ = R.f t

/-- Carrier from the line `ℓ` arriving at the chart `c`. -/
def Carrier (Q : Route K V) (ℓ c : Submodule K V) : Prop := ∃ s₀ s₁, s₀ ≤ s₁ ∧ Q.f s₀ = ℓ ∧ Q.f s₁ = c

section Main
variable {u₁ u₂ : V}

/-- CARRIER-FORCE.  Cluster = family 𝓡 of public routes (no owned register), held-alone for both
  ports.  A register of 𝓡 leaving a chart of rank <= 2 with content from both ports (membership)
  forces (i) a stop at the plane, (ii) two DISTINCT carriers, one ascending from each line to P.
  Hence 2 line stops + 1 plane stop is minimal. -/
theorem two_port_exit (h : LinearIndependent K ![u₁, u₂]) (𝓡 : Set (Route K V))
    (hpub : ∀ R ∈ 𝓡, R.IsPublic) (H₁ : HeldAlone 𝓡 u₁) (H₂ : HeldAlone 𝓡 u₂)
    (R : Route K V) (hR : R ∈ 𝓡) (t : ℕ) (h1 : u₁ ∈ R.f t) (h2 : u₂ ∈ R.f t)
    [FiniteDimensional K (R.f t)] (hr : Module.finrank K (R.f t) ≤ 2) :
    R.f t = plane u₁ u₂ ∧
    ∃ Q₁ ∈ 𝓡, ∃ Q₂ ∈ 𝓡, Q₁ ≠ Q₂ ∧ Carrier Q₁ (ln u₁) (plane u₁ u₂) ∧
      Carrier Q₂ (ln u₂) (plane u₁ u₂) := by
  have hP := chart_eq_plane h h1 h2 hr
  refine ⟨hP, ?_⟩
  obtain ⟨Q₁, hQ₁, a₀, a₁, ha, ha0, ha1⟩ := H₁ R hR t h1
  obtain ⟨Q₂, hQ₂, b₀, b₁, hb, hb0, hb1⟩ := H₂ R hR t h2
  refine ⟨Q₁, hQ₁, Q₂, hQ₂, ?_, ⟨a₀, a₁, ha, ha0, ha1.trans hP⟩, ⟨b₀, b₁, hb, hb0, hb1.trans hP⟩⟩
  rintro rfl
  exact no_two_lines h Q₁ (hpub _ hQ₁) ha0 hb0

/-- The three stop charts are pairwise distinct (2 line stops + 1 plane stop). -/
theorem three_stops_distinct (h : LinearIndependent K ![u₁, u₂]) :
    (ln u₁ : Submodule K V) ≠ ln u₂ ∧ (ln u₁ : Submodule K V) ≠ plane u₁ u₂ ∧
      (ln u₂ : Submodule K V) ≠ plane u₁ u₂ :=
  ⟨lines_ne h, (line_lt_plane h).1.ne, (line_lt_plane h).2.ne⟩

/-- Line-stop pinning: a helper co-present with a fixed main event at the line chart `ln u₁`
  has a stop at `ln u₁`, and (public) never stops at `ln u₂`. -/
theorem line_pin (h : LinearIndependent K ![u₁, u₂]) (M H : Route K V) (hH : H.IsPublic)
    {s t : ℕ} (hev : M.f s = ln u₁) (hco : H.f t = M.f s) :
    H.f t = ln u₁ ∧ ∀ t', H.f t' ≠ ln u₂ :=
  ⟨hco.trans hev, fun t' ht' => no_two_lines h H hH (hco.trans hev) ht'⟩

/-- Scope: without the public hypothesis a single route passes both lines (owned step). -/
theorem owned_passes_two_lines :
    ∃ (R : Route ℚ (ℚ × ℚ)) (u₁ u₂ : ℚ × ℚ), LinearIndependent ℚ ![u₁, u₂] ∧
      R.f 0 = ln u₁ ∧ R.f 1 = ln u₂ := by
  refine ⟨⟨fun t => if t = 0 then ln ((1:ℚ),(0:ℚ)) else ln ((0:ℚ),(1:ℚ)),
    fun t => t = 0, ?_⟩, (1,0), (0,1), ?_, by simp, by simp⟩
  · intro t ht
    have : t ≠ 0 := ht
    simp [this]
  · rw [LinearIndependent.pair_iff]
    intro s t hst
    have h1 := congrArg Prod.fst hst
    have h2 := congrArg Prod.snd hst
    simp at h1 h2
    exact ⟨h1, h2⟩

/-- Scope: if the exit may leave from the rank-3 chart itself, no plane stop is forced
  (ℚ³: carriers go ℓ₁ → ⊤ and ℓ₂ → ⊤, no frame equals the plane). -/
theorem no_plane_if_rank3 :
    ∃ (u₁ u₂ : ℚ × ℚ × ℚ) (𝓡 : Set (Route ℚ (ℚ × ℚ × ℚ))),
      LinearIndependent ℚ ![u₁, u₂] ∧ (∀ R ∈ 𝓡, R.IsPublic) ∧ HeldAlone 𝓡 u₁ ∧ HeldAlone 𝓡 u₂ ∧
      (∃ R ∈ 𝓡, u₁ ∈ R.f 1 ∧ u₂ ∈ R.f 1) ∧ ∀ R ∈ 𝓡, ∀ t, R.f t ≠ plane u₁ u₂ := by
  set u₁ : ℚ × ℚ × ℚ := (1, 0, 0) with hu₁
  set u₂ : ℚ × ℚ × ℚ := (0, 1, 0) with hu₂
  have hind : LinearIndependent ℚ ![u₁, u₂] := by
    rw [LinearIndependent.pair_iff]
    intro s t hst
    have h1 := congrArg Prod.fst hst
    have h2 := congrArg (fun x => x.2.1) hst
    simp [hu₁, hu₂] at h1 h2
    exact ⟨h1, h2⟩
  let mk : Submodule ℚ (ℚ × ℚ × ℚ) → Route ℚ (ℚ × ℚ × ℚ) := fun L =>
    ⟨fun t => if t = 0 then L else ⊤, fun _ => False, fun t _ => by
      by_cases h : t = 0
      · subst h; simp
      · simp [h]⟩
  have hmk : ∀ L, (mk L).IsPublic := fun L t h => h
  have hmk0 : ∀ L, (mk L).f 0 = L := fun L => by simp [mk]
  have hmk1 : ∀ L t, t ≠ 0 → (mk L).f t = ⊤ := fun L t h => by simp [mk, h]
  have hnotop : (⊤ : Submodule ℚ (ℚ × ℚ × ℚ)) ≠ plane u₁ u₂ := by
    intro e
    have hle : plane u₁ u₂ ≤ LinearMap.ker ((LinearMap.snd ℚ ℚ ℚ).comp (LinearMap.snd ℚ ℚ (ℚ × ℚ))) := by
      refine sup_le ?_ ?_ <;>
      · rw [Submodule.span_singleton_le_iff_mem]; simp [hu₁, hu₂]
    have : ((0 : ℚ), (0 : ℚ), (1 : ℚ)) ∈ plane u₁ u₂ := e ▸ Submodule.mem_top
    have := hle this
    simp at this
  refine ⟨u₁, u₂, {mk (ln u₁), mk (ln u₂)}, hind, ?_, ?_, ?_, ⟨mk (ln u₁), by simp, ?_, ?_⟩, ?_⟩
  · intro R hR
    rcases hR with rfl | rfl <;> exact hmk _
  · rintro R hR t ht
    refine ⟨mk (ln u₁), by simp, 0, t, Nat.zero_le _, hmk0 _, ?_⟩
    rcases hR with rfl | rfl
    · rfl
    · by_cases h0 : t = 0
      · subst h0; rw [hmk0] at ht; exact absurd ht (not_mem_line hind)
      · rw [hmk1 _ _ h0, hmk1 _ _ h0]
  · rintro R hR t ht
    refine ⟨mk (ln u₂), by simp, 0, t, Nat.zero_le _, hmk0 _, ?_⟩
    rcases hR with rfl | rfl
    · by_cases h0 : t = 0
      · subst h0; rw [hmk0] at ht; exact absurd ht (not_mem_line' hind)
      · rw [hmk1 _ _ h0, hmk1 _ _ h0]
    · rfl
  · rw [hmk1 _ 1 one_ne_zero]; trivial
  · rw [hmk1 _ 1 one_ne_zero]; trivial
  · rintro R hR t
    have hl := line_lt_plane hind
    rcases hR with rfl | rfl <;> by_cases h0 : t = 0
    · subst h0; rw [hmk0]; exact hl.1.ne
    · rw [hmk1 _ _ h0]; exact hnotop
    · subst h0; rw [hmk0]; exact hl.2.ne
    · rw [hmk1 _ _ h0]; exact hnotop

end Main
end CarrierForce

#print axioms CarrierForce.no_two_lines
#print axioms CarrierForce.finrank_plane
#print axioms CarrierForce.chart_eq_plane
#print axioms CarrierForce.line_lt_plane
#print axioms CarrierForce.two_port_exit
#print axioms CarrierForce.three_stops_distinct
#print axioms CarrierForce.line_pin
#print axioms CarrierForce.owned_passes_two_lines
#print axioms CarrierForce.no_plane_if_rank3
