/-
V2BridgeFinal: V2-FLOOR certificates (V2FloorFinal.floor_joint / floor_beta) composed with the bridge
(V2Bridge) into helper-D0 floors for accepted (in particular class-K) words. Lane LEAN-BRIDGE, Nov 16.
Hypotheses: `IntFeasible` (as in V2FloorFinal) and `hreal` — the helper relay realises every forced pair
(V2FloorCert.Reach on relayE), a named data hypothesis (r7-taint extraction), not a consequence of class K.
-/
import Nov15.V2Bridge
import Nov15.V2FloorFinal

namespace V2Bridge
open FloorE2E FloorD0
open V2Floor (IntFeasible Lsub Usub LBj UHj numj T_joint LBb UHb numb T_beta Reach Sub fdim wcut B1)

variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]
variable {Pub H : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}

/-- **joint α+β helper-D0 floor** (θ = 22257/2^19): 1,713.38 ≤ helper D0 + Σ_h corr_θ(dim ini h, dim fin h). -/
theorem v2floor_helperD0_joint
    (hfeas : IntFeasible (fun p => Lsub (LBj p)) (fun p => Usub (UHj p)) numj T_joint)
    (dim : C → ℕ) (ι : C → Sub) (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c)
    (hA : Accepted Pub H ini w)
    (hreal : ∀ p, Reach (relayE ι H ini w) (Lsub (LBj p)) (Usub (UHj p))) :
    (1839727178682 : ℝ) / 2 ^ 30 ≤
      helperD0 JunkLB2.fL dim H ini w + ∑ h ∈ H, hcorr (22257 / 524288) dim ini w h :=
  le_trans (V2Floor.floor_joint hfeas _ (relayE_lt ι hι hA) hreal)
    (bridge _ (by norm_num) (by norm_num) dim ι hι hιd hA)

/-- **joint floor, {0}→V helpers**: 1,713.38 ≤ helper D0. -/
theorem v2floor_helperD0_joint_0V
    (hfeas : IntFeasible (fun p => Lsub (LBj p)) (fun p => Usub (UHj p)) numj T_joint)
    (dim : C → ℕ) (ι : C → Sub) (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c)
    (hA : Accepted Pub H ini w)
    (h0V : ∀ h ∈ H, natLoc dim (ini h) = 0 ∧ natLoc dim ((grun (s0 ini) w).loc h) = 9)
    (hreal : ∀ p, Reach (relayE ι H ini w) (Lsub (LBj p)) (Usub (UHj p))) :
    (1839727178682 : ℝ) / 2 ^ 30 ≤ helperD0 JunkLB2.fL dim H ini w :=
  le_trans (V2Floor.floor_joint hfeas _ (relayE_lt ι hι hA) hreal)
    (bridge_0V _ (by norm_num) (by norm_num) dim ι hι hιd hA h0V)

/-- **β helper-D0 floor** (θ = 1): 1,431.05 ≤ helper D0 + Σ_h corr_1(dim ini h, dim fin h). -/
theorem v2floor_helperD0_beta
    (hfeas : IntFeasible (fun p => Lsub (LBb p)) (fun p => Usub (UHb p)) numb T_beta)
    (dim : C → ℕ) (ι : C → Sub) (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c)
    (hA : Accepted Pub H ini w)
    (hreal : ∀ p, Reach (relayE ι H ini w) (Lsub (LBb p)) (Usub (UHb p))) :
    (1536575200417 : ℝ) / 2 ^ 30 ≤ helperD0 JunkLB2.fL dim H ini w + ∑ h ∈ H, hcorr 1 dim ini w h :=
  le_trans (V2Floor.floor_beta hfeas _ (relayE_lt ι hι hA) hreal)
    (bridge 1 zero_le_one le_rfl dim ι hι hιd hA)

/-- **β floor, helpers ending at V**: 1,431.05 ≤ helper D0 + B1 · #(line-born helpers). -/
theorem v2floor_helperD0_beta_V
    (hfeas : IntFeasible (fun p => Lsub (LBb p)) (fun p => Usub (UHb p)) numb T_beta)
    (dim : C → ℕ) (ι : C → Sub) (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c)
    (hA : Accepted Pub H ini w)
    (hV : ∀ h ∈ H, natLoc dim ((grun (s0 ini) w).loc h) = 9)
    (hreal : ∀ p, Reach (relayE ι H ini w) (Lsub (LBb p)) (Usub (UHb p))) :
    (1536575200417 : ℝ) / 2 ^ 30 ≤
      helperD0 JunkLB2.fL dim H ini w + B1 * (H.filter fun h => natLoc dim (ini h) = 1).card :=
  le_trans (V2Floor.floor_beta hfeas _ (relayE_lt ι hι hA) hreal)
    (bridge_beta_V dim ι hι hιd hA hV)

end V2Bridge

#print axioms V2Bridge.v2floor_helperD0_joint
#print axioms V2Bridge.v2floor_helperD0_joint_0V
#print axioms V2Bridge.v2floor_helperD0_beta
#print axioms V2Bridge.v2floor_helperD0_beta_V
