module

public import IntegerMultBounds.MathlibTM2.Fast.Final
public import IntegerMultBounds.MathlibTM2.Cost.MatchSynLoop

/-!
# Integer multiplication below `n log n` on Mathlib's Turing machines

`mulInTime` exposes the explicit improved saving; `statement` retains the existential
interface in `Statement.lean`. Both follow from the fast host multiplier bundles and
the cost bound of its synthetic transforms (`Cost/MatchSynLoop.mr_loop_cost_le`).
-/

@[expose] public section


namespace IntegerMultBounds.MathlibTM2

/-- The explicit saving after retuning the dimension and chunk root indices. -/
theorem mulInTime_exact : MulInTime (296 / (10 ^ 11 * 2 ^ 64)) := by
  rw [← Cost.tot_kappa_eq]
  let L := Fast.Main.blLayDs Fast.Main.dsyV₀ Fast.Main.dsyV₀_wires
    (Fast.Main.finCost Cost.mr_loop_cost_le)
  let D := Fast.Main.bdDist Fast.Main.dsyWires Fast.Main.mn_postParam_bd
  have hw : ∀ᶠ n in Filter.atTop, Mult.Sizes.p n + 2 ≤ Fast.Main.bdW n := by
    filter_upwards [D.widths] with n hn
    have := hn.1
    omega
  exact Fast.Main.mulInTime_of_bundles
    ⟨Fast.Main.mnKa, Fast.Main.mnLb, Fast.Main.bdW, Fast.Main.mnσL L,
      ⟨Fast.Main.mnSynOfLay L hw⟩, ⟨D⟩⟩

/-- A power-of-two saving supported by the exact cost margin. -/
theorem mulInTime : MulInTime (2 ^ 93 : ℝ)⁻¹ := by
  obtain ⟨M, hM⟩ := mulInTime_exact
  exact ⟨M, hM.trans (Cost.gr_isBigO_rpow_mono (by norm_num))⟩

theorem statement : Statement :=
  ⟨_, by positivity, mulInTime⟩

end IntegerMultBounds.MathlibTM2
