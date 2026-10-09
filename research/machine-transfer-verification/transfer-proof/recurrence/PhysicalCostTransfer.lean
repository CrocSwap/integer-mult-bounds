import SelectedFloorTransfer

/-! Cost transfer for actual invocation states, with no normalized supremum.
States include any volumes, spectators and machine metadata. The explicit
physical contracts give each indexed call its floor width and exact volume.
Finite multiplicities remain symbolic sums over Fin n, never expanded lists.
-/
namespace PhysicalCostTransfer
open scoped BigOperators

/-- Uniform state-indexed cost bound. The only physical assumptions are the
per-state recurrence, uniform finite-width base bound, and child interfaces.
No worst-case normalized function or supremum over states is introduced. -/
theorem state_all_width_bound {S ι : Type} (rows : List ι)
    (rank count : ι → ℕ) (m W : ℕ)
    (width : S → ℕ) (volume cost : S → ℝ)
    (child : S → (r : ι) → Fin (count r) → S)
    (p A B C γ : ℝ) (hm : 0 < m) (hW : 0 < W) (hp : 0 ≤ p)
    (hA : 0 ≤ A) (hBA : B ≤ A) (hbudget : C ≤ A * (1 - γ))
    (hvolume : ∀ s, 0 ≤ volume s)
    (hrank : ∀ r ∈ rows, 0 < rank r) (hrankm : ∀ r ∈ rows, rank r < m)
    (hγ : γ = (rows.map (fun r => (count r : ℝ) / W * ((rank r : ℝ) / m) ^ p)).sum)
    (hγ1 : γ < 1)
    (child_width : ∀ s, m ≤ width s → ∀ r ∈ rows, ∀ j,
      width (child s r j) = rank r * (width s / m))
    (child_volume : ∀ s, m ≤ width s → ∀ r ∈ rows, ∀ j,
      volume (child s r j) = volume s / W)
    (uniform_base : ∀ s, 0 < width s → width s < m → cost s ≤ B * volume s)
    (physical_recurrence : ∀ s, m ≤ width s → cost s ≤ C * volume s +
      (rows.map (fun r => ∑ j : Fin (count r), cost (child s r j))).sum) :
    ∀ s, 0 < width s → cost s ≤ A * volume s * (width s : ℝ) ^ p := by
  have main : ∀ e, ∀ s, width s = e → 0 < e → cost s ≤ A * volume s * (e : ℝ) ^ p := by
    intro e
    induction e using Nat.strong_induction_on with
    | h e ih =>
      intro s hwidth he
      have hAV : 0 ≤ A * volume s := mul_nonneg hA (hvolume s)
      have hepow := FloorRecurrence.one_le_width_power e p he hp
      by_cases hb : e < m
      · calc
          cost s ≤ B * volume s := uniform_base s (by simpa [hwidth] using he) (by simpa [hwidth] using hb)
          _ ≤ A * volume s := mul_le_mul_of_nonneg_right hBA (hvolume s)
          _ ≤ A * volume s * (e : ℝ) ^ p := by simpa using mul_le_mul_of_nonneg_left hepow hAV
      · have hem : m ≤ e := Nat.le_of_not_gt hb
        have hinternal : m ≤ width s := by simpa [hwidth] using hem
        have hrow : ∀ r ∈ rows, (∑ j : Fin (count r), cost (child s r j)) ≤
            (count r : ℝ) * (A * (volume s / W) * (((rank r : ℝ) / m) ^ p * (e : ℝ) ^ p)) := by
          intro r hr
          have hpoint : ∀ j : Fin (count r), cost (child s r j) ≤
              A * (volume s / W) * (((rank r : ℝ) / m) ^ p * (e : ℝ) ^ p) := by
            intro j
            have hcw : width (child s r j) = FloorDepth.child m (rank r) e := by
              simpa [FloorDepth.child, hwidth] using child_width s hinternal r hr j
            have hcpos := FloorDepth.child_pos m (rank r) e hm (hrank r hr) hem
            have hclt := FloorDepth.child_lt m (rank r) e (hrankm r hr) hem
            have hbnd := ih (FloorDepth.child m (rank r) e) hclt (child s r j) hcw hcpos
            rw [child_volume s hinternal r hr j] at hbnd
            have hfactor : 0 ≤ A * (volume s / W) :=
              mul_nonneg hA (div_nonneg (hvolume s) (by exact_mod_cast hW.le))
            exact hbnd.trans (mul_le_mul_of_nonneg_left
              (FloorRecurrence.floor_child_power m (rank r) e p hm hp) hfactor)
          calc
            _ ≤ ∑ _j : Fin (count r),
                A * (volume s / W) * (((rank r : ℝ) / m) ^ p * (e : ℝ) ^ p) :=
              Finset.sum_le_sum (fun j _ => hpoint j)
            _ = _ := by simp
        have hsum : (rows.map (fun r => (count r : ℝ) *
            (A * (volume s / W) * (((rank r : ℝ) / m) ^ p * (e : ℝ) ^ p)))).sum =
            A * volume s * γ * (e : ℝ) ^ p := by
          calc
            _ = (rows.map (fun r => ((count r : ℝ) / W * ((rank r : ℝ) / m) ^ p) *
                (A * volume s * (e : ℝ) ^ p))).sum := by
              congr 1
              apply List.map_congr_left
              intro r hr
              ring
            _ = γ * (A * volume s * (e : ℝ) ^ p) := by rw [List.sum_map_mul_right, ← hγ]
            _ = _ := by ring
        have hgap : 0 ≤ A * volume s * (1 - γ) := mul_nonneg hAV (by linarith)
        have hover : C * volume s ≤ A * volume s * (1 - γ) := by
          have h := mul_le_mul_of_nonneg_right hbudget (hvolume s)
          nlinarith
        have hpaid : C * volume s ≤ A * volume s * (1 - γ) * (e : ℝ) ^ p :=
          hover.trans (by simpa using mul_le_mul_of_nonneg_left hepow hgap)
        calc
          cost s ≤ C * volume s + (rows.map (fun r => ∑ j : Fin (count r), cost (child s r j))).sum :=
            physical_recurrence s hinternal
          _ ≤ C * volume s + (rows.map (fun r => (count r : ℝ) *
              (A * (volume s / W) * (((rank r : ℝ) / m) ^ p * (e : ℝ) ^ p)))).sum :=
            add_le_add_left (List.sum_le_sum hrow) (C * volume s)
          _ = C * volume s + A * volume s * γ * (e : ℝ) ^ p := by rw [hsum]
          _ ≤ A * volume s * (e : ℝ) ^ p := by nlinarith [hpaid]
  intro s hs
  exact main (width s) s rfl hs

/-- A uniform cost constant depends only on the physical base and overhead
constants and the fixed finite characteristic; never on volume or spectators. -/
noncomputable def uniformConstant (B C γ : ℝ) : ℝ := max 0 B + |C| / (1 - γ)

theorem uniformConstant_nonneg (B C γ : ℝ) (hγ : γ < 1) : 0 ≤ uniformConstant B C γ := by
  unfold uniformConstant
  exact add_nonneg (le_max_left _ _) (div_nonneg (abs_nonneg _) (by linarith))

theorem uniformConstant_base (B C γ : ℝ) (hγ : γ < 1) : B ≤ uniformConstant B C γ := by
  have hmax : B ≤ max 0 B := le_max_right _ _
  have hquot : 0 ≤ |C| / (1 - γ) := div_nonneg (abs_nonneg _) (by linarith)
  unfold uniformConstant
  linarith

theorem uniformConstant_overhead (B C γ : ℝ) (hγ : γ < 1) :
    C ≤ uniformConstant B C γ * (1 - γ) := by
  have hgap : 0 < 1 - γ := by linarith
  have hmax : 0 ≤ max 0 B := le_max_left _ _
  have hle : |C| / (1 - γ) ≤ uniformConstant B C γ := by unfold uniformConstant; linarith
  have h := mul_le_mul_of_nonneg_right hle hgap.le
  rw [div_mul_cancel₀ _ hgap.ne'] at h
  exact (le_abs_self C).trans h

open SelectedProfileCertificate

noncomputable def selectedConstant (B C : ℝ) : ℝ :=
  uniformConstant B C SelectedProfileReal.powerCharacteristic

/-- The actual selected characteristic is already proved. Every member of
every state family obeys this unnormalized bound under uniform physical
contracts; the family can contain arbitrarily many volumes and spectators. -/
theorem selected_state_cost_bound {S : Type}
    (width : S → ℕ) (volume cost : S → ℝ)
    (child : S → (r : Row) → Fin r.multiplicity → S)
    (B C : ℝ) (hvolume : ∀ s, 0 ≤ volume s)
    (child_width : ∀ s, m ≤ width s → ∀ r ∈ rows, ∀ j,
      width (child s r j) = r.width * (width s / m))
    (child_volume : ∀ s, m ≤ width s → ∀ r ∈ rows, ∀ j,
      volume (child s r j) = volume s / W)
    (uniform_base : ∀ s, 0 < width s → width s < m → cost s ≤ B * volume s)
    (physical_recurrence : ∀ s, m ≤ width s → cost s ≤ C * volume s +
      (rows.map (fun r => ∑ j : Fin r.multiplicity, cost (child s r j))).sum) :
    ∀ s, 0 < width s → cost s ≤ selectedConstant B C * volume s *
      (width s : ℝ) ^ (1 - (saving : ℝ)) := by
  apply state_all_width_bound rows (fun r => r.width) (fun r => r.multiplicity) m W
    width volume cost child (1 - (saving : ℝ)) (selectedConstant B C) B C
    SelectedProfileReal.powerCharacteristic
  · norm_num [m]
  · norm_num [W]
  · norm_num [saving]
  · exact uniformConstant_nonneg B C _ SelectedProfileReal.actual_power_characteristic_lt_one
  · exact uniformConstant_base B C _ SelectedProfileReal.actual_power_characteristic_lt_one
  · exact uniformConstant_overhead B C _ SelectedProfileReal.actual_power_characteristic_lt_one
  · exact hvolume
  · intro r hr; exact (SelectedProfileReal.row_valid r hr).1
  · intro r hr; exact (SelectedProfileReal.row_valid r hr).2.1
  · rfl
  · exact SelectedProfileReal.actual_power_characteristic_lt_one
  · exact child_width
  · exact child_volume
  · exact uniform_base
  · exact physical_recurrence

end PhysicalCostTransfer

#print axioms PhysicalCostTransfer.state_all_width_bound
#print axioms PhysicalCostTransfer.uniformConstant_nonneg
#print axioms PhysicalCostTransfer.uniformConstant_base
#print axioms PhysicalCostTransfer.uniformConstant_overhead
#print axioms PhysicalCostTransfer.selected_state_cost_bound
