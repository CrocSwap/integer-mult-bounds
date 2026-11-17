/-
V2KernelBridge (lane LEAN-NEXT32, Nov 17): kernel-only V2-FLOOR covers (V2FloorKernel_j / _b) composed with the
bridge (V2Bridge) into helper-D0 floors. No native_decide; no IntFeasible hypothesis (the certificate is checked
in-kernel). Hypothesis `hreal` is the same object as in V2BridgeFinal: Reach (relayE ι H ini w) (Lsub (LBj p)) (Usub (UHj p))
over the same V2FloorData pair list (N_joint / N_beta), same Sub, Lsub, Usub, Reach, wcut.
-/
import Nov15.V2Bridge
import Nov15.V2FloorKernel_j
import Nov15.V2FloorKernel_b

namespace V2Bridge
open FloorE2E FloorD0
open V2Floor (Lsub Usub LBj UHj N_joint LBb UHb N_beta Reach Sub fdim wcut B1)

variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]
variable {Pub H : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}

/-- joint (JB) kernel floor: 919.92 ≤ helper D0 + Σ_h corr_θ, θ = 79793/2^20. -/
theorem v2kernel_helperD0_joint
    (dim : C → ℕ) (ι : C → Sub) (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c)
    (hA : Accepted Pub H ini w)
    (hreal : ∀ p : Fin N_joint, Reach (relayE ι H ini w) (Lsub (LBj p)) (Usub (UHj p))) :
    (987754236107 : ℝ) / 2 ^ 30 ≤
      helperD0 JunkLB2.fL dim H ini w + ∑ h ∈ H, hcorr (79793 / 1048576) dim ini w h :=
  le_trans (V2Floor.v2floor_joint_kernel _ (relayE_lt ι hι hA) hreal)
    (bridge _ (by norm_num) (by norm_num) dim ι hι hιd hA)

/-- joint kernel floor, {0}→V helpers: 919.92 ≤ helper D0. -/
theorem v2kernel_helperD0_joint_0V
    (dim : C → ℕ) (ι : C → Sub) (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c)
    (hA : Accepted Pub H ini w)
    (h0V : ∀ h ∈ H, natLoc dim (ini h) = 0 ∧ natLoc dim ((grun (s0 ini) w).loc h) = 9)
    (hreal : ∀ p : Fin N_joint, Reach (relayE ι H ini w) (Lsub (LBj p)) (Usub (UHj p))) :
    (987754236107 : ℝ) / 2 ^ 30 ≤ helperD0 JunkLB2.fL dim H ini w :=
  le_trans (V2Floor.v2floor_joint_kernel _ (relayE_lt ι hι hA) hreal)
    (bridge_0V _ (by norm_num) (by norm_num) dim ι hι hιd hA h0V)

/-- β kernel floor (θ = 1): 877.28 ≤ helper D0 + Σ_h corr_1. -/
theorem v2kernel_helperD0_beta
    (dim : C → ℕ) (ι : C → Sub) (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c)
    (hA : Accepted Pub H ini w)
    (hreal : ∀ p : Fin N_beta, Reach (relayE ι H ini w) (Lsub (LBb p)) (Usub (UHb p))) :
    (941971821916 : ℝ) / 2 ^ 30 ≤ helperD0 JunkLB2.fL dim H ini w + ∑ h ∈ H, hcorr 1 dim ini w h :=
  le_trans (V2Floor.v2floor_beta_kernel _ (relayE_lt ι hι hA) hreal)
    (bridge 1 zero_le_one le_rfl dim ι hι hιd hA)

/-- β kernel floor, helpers ending at V: 877.28 ≤ helper D0 + B1 · #(line-born helpers). -/
theorem v2kernel_helperD0_beta_V
    (dim : C → ℕ) (ι : C → Sub) (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c)
    (hA : Accepted Pub H ini w)
    (hV : ∀ h ∈ H, natLoc dim ((grun (s0 ini) w).loc h) = 9)
    (hreal : ∀ p : Fin N_beta, Reach (relayE ι H ini w) (Lsub (LBb p)) (Usub (UHb p))) :
    (941971821916 : ℝ) / 2 ^ 30 ≤
      helperD0 JunkLB2.fL dim H ini w + B1 * (H.filter fun h => natLoc dim (ini h) = 1).card :=
  le_trans (V2Floor.v2floor_beta_kernel _ (relayE_lt ι hι hA) hreal)
    (bridge_beta_V dim ι hι hιd hA hV)

end V2Bridge

#print axioms V2Bridge.v2kernel_helperD0_joint
#print axioms V2Bridge.v2kernel_helperD0_joint_0V
#print axioms V2Bridge.v2kernel_helperD0_beta
#print axioms V2Bridge.v2kernel_helperD0_beta_V
