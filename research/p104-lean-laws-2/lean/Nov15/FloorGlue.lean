/-
Floor glue, lane LEAN-NEXT7, Nov 16. See FloorGlue.md.

(1) `entry_count`: Floor's hypothesis `hent` (dim S_c ≤ hd + he + ka + oa + hb + kb) DERIVED from
    ExportLaw's one-chart op model (forward span law + stay count) and hOnce for kept registers.
(2) `chart_floor`: Floor.stay_floor instantiated on an ExportLaw run, so the per-chart floor
    rank ρ(X) ≤ hd + ka + oa + kb has no op-model hypotheses left beyond class N and ρ.
(3) `sum_chart_floors`, `global_floor_direct`, `global_floor_of_certificate`: summing chart floors
    over distinct stays, and the LP certificate on top. What stays input: the LP rows A x ≥ b (with
    the native-feasibility map x and objective ≤ #paid stays) and the dual vector y.

Build: this file imports the oleans of Nov15/ExportLaw.lean and Nov15/Floor.lean:
  lake env lean -o .lake/build/lib/lean/Nov15/ExportLaw.olean Nov15/ExportLaw.lean
  lake env lean -o .lake/build/lib/lean/Nov15/Floor.olean Nov15/Floor.lean
  lake env lean Nov15/FloorGlue.lean
-/
import Nov15.ExportLaw
import Nov15.Floor

open Finset Module Submodule

set_option linter.unusedSectionVars false

namespace FloorGlue

open ExportLaw

section Chart
variable {K Reg : Type*} [Field K] [Fintype Reg] [DecidableEq Reg]

lemma nEnt_eq_sum (C : Finset Reg) : ∀ evs : List (Ev K Reg), nEnt C evs = ∑ i ∈ C, nEnt {i} evs
  | [] => by simp [nEnt]
  | .arrive j _ :: evs => by
    simp only [nEnt, nEnt_eq_sum C evs, Finset.sum_add_distrib, Finset.mem_singleton]
    congr 1
    rw [Finset.sum_ite_eq C j]
  | .born j :: evs => by
    simp only [nEnt, nEnt_eq_sum C evs, Finset.sum_add_distrib, Finset.mem_singleton]
    congr 1
    rw [Finset.sum_ite_eq C j]
  | .add _ _ _ :: evs => by simp only [nEnt]; exact nEnt_eq_sum C evs
  | .scale _ _ :: evs => by simp only [nEnt]; exact nEnt_eq_sum C evs
  | .depart _ :: evs => by simp only [nEnt]; exact nEnt_eq_sum C evs
  | .clear _ :: evs => by simp only [nEnt]; exact nEnt_eq_sum C evs
  | .copy _ _ :: evs => by simp only [nEnt]; exact nEnt_eq_sum C evs

lemma one_le_nEnt_of_born : ∀ (evs : List (Ev K Reg)) (b : Reg), b ∈ bornSet evs →
    1 ≤ nEnt {b} evs
  | [], b, h => by simp [bornSet] at h
  | .born b' :: evs, b, h => by
    simp only [bornSet, Finset.mem_insert] at h
    simp only [nEnt, Finset.mem_singleton]
    rcases h with rfl | h
    · simp
    · have := one_le_nEnt_of_born evs b h; omega
  | .arrive _ _ :: evs, b, h => by
    simp only [nEnt]; have := one_le_nEnt_of_born evs b h; omega
  | .add _ _ _ :: evs, b, h => by simp only [nEnt]; exact one_le_nEnt_of_born evs b h
  | .scale _ _ :: evs, b, h => by simp only [nEnt]; exact one_le_nEnt_of_born evs b h
  | .depart _ :: evs, b, h => by simp only [nEnt]; exact one_le_nEnt_of_born evs b h
  | .clear _ :: evs, b, h => by simp only [nEnt]; exact one_le_nEnt_of_born evs b h
  | .copy _ _ :: evs, b, h => by simp only [nEnt]; exact one_le_nEnt_of_born evs b h

/-- per-register stay count from the empty state. -/
lemma stay_one (evs : List (Ev K Reg)) (hL : Legal start evs) (i : Reg) :
    nEnt {i} evs = nDep {i} evs + ((run start evs).pres ∩ {i}).card := by
  have := stay_count (K := K) {i} start evs hL
  have h0 : (start (K := K) (Reg := Reg)).pres = ∅ := rfl
  rw [h0] at this
  simpa using this

/-- **Entry count (Floor's `hent`), derived.** One chart, a legal run from the empty state, registers
partitioned into helpers `H`, kept `Kp`, owned `Ow`; hOnce for kept registers. With
hb = helpers born at c and gone at the end, he = helper enders, hd = helper departures − hb
(paid stays), ka = kept registers that arrive (not born at c), kb = kept births, oa = owned entries:
`hb ≤ helper departures` and `dim S_c ≤ hd + he + ka + oa + hb + kb`. -/
theorem entry_count (evs : List (Ev K Reg)) (hL : Legal start evs)
    (H Kp Ow : Finset Reg) (hHK : Disjoint H Kp) (hHO : Disjoint H Ow) (hKO : Disjoint Kp Ow)
    (hcov : H ∪ Kp ∪ Ow = univ) (hOnce : ∀ i ∈ Kp, nEnt {i} evs ≤ 1) :
    ((H ∩ bornSet evs) \ (run start evs).pres).card ≤ nDep H evs ∧
    finrank K (span K (held start evs)) ≤
      (nDep H evs - ((H ∩ bornSet evs) \ (run start evs).pres).card)
      + ((run start evs).pres ∩ H).card
      + ((Kp \ bornSet evs).filter fun i => 0 < nEnt {i} evs).card
      + nEnt Ow evs
      + ((H ∩ bornSet evs) \ (run start evs).pres).card
      + (Kp ∩ bornSet evs).card := by
  classical
  set F := (run (start (K := K) (Reg := Reg)) evs).pres
  set HB := (H ∩ bornSet evs) \ F
  -- dim S_c ≤ #entries
  have fc := forward_count (K := K) LinearMap.id evs hL ∅ (by simp) (by simp)
  rw [Submodule.map_id, Finset.card_empty, add_zero] at fc
  -- #entries split by class
  have hsplit : nEnt univ evs = nEnt H evs + nEnt Kp evs + nEnt Ow evs := by
    rw [nEnt_eq_sum, nEnt_eq_sum H, nEnt_eq_sum Kp, nEnt_eq_sum Ow, ← hcov,
      Finset.sum_union (Finset.disjoint_union_left.2 ⟨hHO, hKO⟩),
      Finset.sum_union hHK]
  -- helpers: entries = departures + enders
  have hH : nEnt H evs = nDep H evs + (F ∩ H).card := by
    have := stay_count (K := K) H start evs hL
    have h0 : (start (K := K) (Reg := Reg)).pres = ∅ := rfl
    rw [h0] at this; simpa using this
  -- hb ≤ helper departures
  have hHB : HB.card ≤ nDep H evs := by
    have hsub : HB ⊆ H := fun x hx => (Finset.mem_inter.1 (Finset.mem_sdiff.1 hx).1).1
    rw [nDep_eq_sum, Finset.card_eq_sum_ones]
    calc ∑ _i ∈ HB, 1 ≤ ∑ i ∈ HB, nDep {i} evs := Finset.sum_le_sum fun i hi => by
          obtain ⟨hi1, hiF⟩ := Finset.mem_sdiff.1 hi
          have h1 := one_le_nEnt_of_born (K := K) evs i (Finset.mem_inter.1 hi1).2
          have h2 : nEnt {i} evs = nDep {i} evs + (F ∩ {i}).card := stay_one evs hL i
          have h3 : (F ∩ {i}).card = 0 := by
            rw [Finset.card_eq_zero, Finset.inter_singleton_of_notMem hiF]
          omega
      _ ≤ ∑ i ∈ H, nDep {i} evs := Finset.sum_le_sum_of_subset hsub
  -- kept: entries ≤ ka + kb (hOnce)
  have hKp : nEnt Kp evs ≤ ((Kp \ bornSet evs).filter fun i => 0 < nEnt {i} evs).card
      + (Kp ∩ bornSet evs).card := by
    rw [nEnt_eq_sum]
    have h1 : ∑ i ∈ Kp, nEnt {i} evs ≤ (Kp.filter fun i => 0 < nEnt {i} evs).card := by
      rw [Finset.card_filter]
      exact Finset.sum_le_sum fun i hi => by
        have := hOnce i hi
        split_ifs with h <;> omega
    have h2 : (Kp.filter fun i => 0 < nEnt {i} evs) ⊆
        ((Kp \ bornSet evs).filter fun i => 0 < nEnt {i} evs) ∪ (Kp ∩ bornSet evs) := by
      intro i hi
      obtain ⟨hiK, hpos⟩ := Finset.mem_filter.1 hi
      by_cases hb : i ∈ bornSet evs
      · exact Finset.mem_union_right _ (Finset.mem_inter.2 ⟨hiK, hb⟩)
      · exact Finset.mem_union_left _ (Finset.mem_filter.2 ⟨Finset.mem_sdiff.2 ⟨hiK, hb⟩, hpos⟩)
    exact h1.trans ((Finset.card_le_card h2).trans (Finset.card_union_le _ _))
  refine ⟨hHB, ?_⟩
  omega

/-- **Per-chart floor on an ExportLaw run.** Floor.stay_floor with `hent` discharged by
`entry_count` and Tok = helper enders ∪ (helpers born at c and gone). Class N: a helper still at c
at the end ends as its own token; ρ kills helper tokens. For any rows X held at c:
`rank ρ(X) ≤ hd + ka + oa + kb`, hd = helper departures − hb (paid helper stays). -/
theorem chart_floor {W : Type*} [AddCommGroup W] [Module K W] (ρ : (Reg → K) →ₗ[K] W)
    (evs : List (Ev K Reg)) (hL : Legal start evs)
    (H Kp Ow : Finset Reg) (hHK : Disjoint H Kp) (hHO : Disjoint H Ow) (hKO : Disjoint Kp Ow)
    (hcov : H ∪ Kp ∪ Ow = univ) (hOnce : ∀ i ∈ Kp, nEnt {i} evs ≤ 1)
    (hN : ∀ h ∈ H, h ∈ (run start evs).pres → (run start evs).row h = Pi.single h 1)
    (hρ : ∀ h ∈ H, ρ (Pi.single h 1) = 0)
    (X : Set (Reg → K)) (hX : X ⊆ held start evs) :
    finrank K (span K (ρ '' X)) ≤
      (nDep H evs - ((H ∩ bornSet evs) \ (run start evs).pres).card)
      + ((Kp \ bornSet evs).filter fun i => 0 < nEnt {i} evs).card
      + nEnt Ow evs + (Kp ∩ bornSet evs).card := by
  classical
  set F := (run (start (K := K) (Reg := Reg)) evs).pres
  set HB := (H ∩ bornSet evs) \ F
  obtain ⟨-, hent⟩ := entry_count evs hL H Kp Ow hHK hHO hKO hcov hOnce
  set Tok := (F ∩ H) ∪ HB
  have hdisj : Disjoint (F ∩ H) HB := by
    rw [Finset.disjoint_left]
    intro x hx hx'
    exact (Finset.mem_sdiff.1 hx').2 (Finset.mem_inter.1 hx).1
  have hTokc : Tok.card = (F ∩ H).card + HB.card := Finset.card_union_of_disjoint hdisj
  have hTokS : ∀ i ∈ Tok, (Pi.single i 1 : Reg → K) ∈ span K (held start evs) := by
    intro i hi
    apply Submodule.subset_span
    rcases Finset.mem_union.1 hi with h | h
    · obtain ⟨hF, hH⟩ := Finset.mem_inter.1 h
      have : (run start evs).row i ∈ cur (run start evs) := ⟨i, hF, rfl⟩
      rw [hN i hH hF] at this
      exact final_sub_held start evs this
    · exact born_held start evs i (Finset.mem_inter.1 (Finset.mem_sdiff.1 h).1).2
  have hTokρ : ∀ i ∈ Tok, ρ (Pi.single i 1) = 0 := by
    intro i hi
    rcases Finset.mem_union.1 hi with h | h
    · exact hρ i (Finset.mem_inter.1 h).2
    · exact hρ i (Finset.mem_inter.1 (Finset.mem_sdiff.1 h).1).1
  exact Floor.stay_floor ρ (span K (held start evs)) X Tok _ _ _ _ _ _
    (hX.trans Submodule.subset_span) hTokS hTokρ hTokc hent

end Chart

/-! ## Summing chart floors over distinct stays; the global floor -/
section Global
variable {𝕜 : Type*} [Field 𝕜] [LinearOrder 𝕜] [IsStrictOrderedRing 𝕜]
  {C σ : Type*} [DecidableEq C]

/-- Distinct stays: each paid stay sits at exactly one chart (`at`), so hd(c) = #stays at c and
Σ_c hd(c) = #stays. Per-chart floors L(c) ≤ hd(c) sum to a floor on #stays. -/
theorem sum_chart_floors (charts : Finset C) (stays : Finset σ) (at_ : σ → C)
    (hat : ∀ s ∈ stays, at_ s ∈ charts) (L : C → ℤ)
    (hL : ∀ c ∈ charts, L c ≤ (stays.filter fun s => at_ s = c).card) :
    ∑ c ∈ charts, L c ≤ stays.card := by
  rw [Finset.card_eq_sum_card_fiberwise (f := at_) (t := charts) (fun s hs => hat s hs)]
  push_cast
  exact Finset.sum_le_sum hL

/-- each paid stay costs ≥ κ ⇒ total cost ≥ κ · #stays. -/
theorem cost_ge (stays : Finset σ) (cost : σ → 𝕜) (κ : 𝕜) (hκ : ∀ s ∈ stays, κ ≤ cost s) :
    κ * stays.card ≤ ∑ s ∈ stays, cost s := by
  have := Finset.card_nsmul_le_sum stays cost κ hκ
  rwa [nsmul_eq_mul, mul_comm] at this

/-- **Global floor, direct.** cost ≥ κ · Σ_c L(c) from per-chart floors L(c) ≤ hd(c). -/
theorem global_floor_direct (charts : Finset C) (stays : Finset σ) (at_ : σ → C)
    (hat : ∀ s ∈ stays, at_ s ∈ charts) (L : C → ℤ)
    (hL : ∀ c ∈ charts, L c ≤ (stays.filter fun s => at_ s = c).card)
    (cost : σ → 𝕜) (κ : 𝕜) (hκ0 : 0 ≤ κ) (hκ : ∀ s ∈ stays, κ ≤ cost s) :
    κ * ((∑ c ∈ charts, L c : ℤ) : 𝕜) ≤ ∑ s ∈ stays, cost s := by
  have h1 : ((∑ c ∈ charts, L c : ℤ) : 𝕜) ≤ (stays.card : 𝕜) := by
    exact_mod_cast sum_chart_floors charts stays at_ hat L hL
  exact (mul_le_mul_of_nonneg_left h1 hκ0).trans (cost_ge stays cost κ hκ)

/-- **Global floor, LP form.** Floor.floor_of_certificate with HD = #paid stays (distinct stays,
cost ≥ κ each). The remaining checked input is the LP data: the rows `A x ≥ b` satisfied by the
native's x (with objective ≤ #stays), and the dual vector y. -/
theorem global_floor_of_certificate {r n : Type*} [Fintype r] [Fintype n]
    (A : r → n → 𝕜) (b : r → 𝕜) (c : n → 𝕜) (x : n → 𝕜) (y : r → 𝕜)
    (hx : ∀ j, 0 ≤ x j) (hAx : ∀ i, b i ≤ ∑ j, A i j * x j)
    (hy : ∀ i, 0 ≤ y i) (hyA : ∀ j, ∑ i, y i * A i j ≤ c j)
    (stays : Finset σ) (cost : σ → 𝕜) (κ : 𝕜) (hκ0 : 0 ≤ κ) (hκ : ∀ s ∈ stays, κ ≤ cost s)
    (hobj : ∑ j, c j * x j ≤ stays.card) :
    κ * ∑ i, y i * b i ≤ ∑ s ∈ stays, cost s :=
  Floor.floor_of_certificate A b c x y hx hAx hy hyA κ _ _ hκ0 hobj (cost_ge stays cost κ hκ)

end Global

end FloorGlue

#print axioms FloorGlue.entry_count
#print axioms FloorGlue.chart_floor
#print axioms FloorGlue.sum_chart_floors
#print axioms FloorGlue.global_floor_direct
#print axioms FloorGlue.global_floor_of_certificate
