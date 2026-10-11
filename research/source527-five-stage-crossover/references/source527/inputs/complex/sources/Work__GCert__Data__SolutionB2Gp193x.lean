import Work.GCert.Data.B2Gp193Main

/-!
Comparator solution `Work.GCert.Data.SolutionB2Gp193x` (not part of github.com/openai/math).

The whole proof is in `Work.GCert.Data.B2Gp193Main` (and its imports), which ends with

    theorem wht_main_B2Gp193x :
        ∃ solve W, WHTProgram solve W ∧ BlockWHT.WHTTimeBoundsAt (1 - 7474547/(10:ℝ)^10) W

This module adds nothing mathematical: it defines `WHT.WHTTimeBoundsAt` with the text of the
challenge (the same definition as `BlockWHT.WHTTimeBoundsAt` of `Work.Block.WHT`) and restates
the theorem under the name the challenge uses.  Its proof is that single term.
`WHTProgram`, `wht`, `whtInKind`, `whtOutKind` come from `WHTCheck.Solution`.
-/

namespace OAI
namespace PowerSaving
namespace WHT
open Filter Asymptotics

/-- `W = O(2^k (k+1)^β)` and `W = o(2^k k)` (`WHTTimeBounds` is the case `β = 1 - 2/10^11`). -/
def WHTTimeBoundsAt (β : ℝ) (W : ℕ → ℕ) : Prop :=
  let W' := fun k : ℕ => (W k : ℝ)
  W' =O[atTop] (fun k : ℕ => (2:ℝ)^k * ((k:ℝ)+1)^β) ∧
  W' =o[atTop] (fun k : ℕ => (2:ℝ)^k * (k:ℝ))

/-- **Walsh-Hadamard transform with the improved exponent**: the statement `WHTGoal` of
`WHTCheck/Challenge.lean` with `1 - 2/10^11` replaced by `1 - 7474547/10^10`. -/
theorem wht_main_block_B2Gp193x :
    ∃ solve W, WHTProgram solve W ∧ WHTTimeBoundsAt (1 - 7474547/(10:ℝ)^10) W :=
  wht_main_B2Gp193x

end WHT
end PowerSaving
end OAI

#print axioms OAI.PowerSaving.WHT.wht_main_block_B2Gp193x
