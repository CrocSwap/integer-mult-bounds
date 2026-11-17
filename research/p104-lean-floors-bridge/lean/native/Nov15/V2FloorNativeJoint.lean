/-
V2FloorNativeJoint (lane LEAN-NEXT21, Nov 16): V2-FLOOR joint bound via native_decide.

*** THIS FILE DEPENDS ON Lean.ofReduceBool (native_decide). *** It is the fallback route: it discharges `IntFeasible` for the
current joint certificate (check.c's per-edge inequality over ALL subspaces of F₂⁹) by running the compiled enumerator
`fullCheck`. The kernel-only theorems (V2FloorFinal.floor_joint with its hypothesis, V2FloorCover) do NOT import this file.
-/
import Nov15.V2FloorFinal
import Nov15.V2FloorNativeChk

set_option maxRecDepth 100000
namespace V2Floor

/-- Mstar (b, c): max over subspaces Y of dim b of the number of distinct upper spaces of log-size c containing Y (rows b = 1..8, cols c = 0..9). -/
def Mjoint : List (List ℕ) :=
  [[0,0,1,5,0,0,25,10,62,0], [0,0,1,2,0,0,15,8,36,0], [0,0,0,1,0,0,8,6,20,0], [0,0,0,0,0,0,5,4,12,0],
   [0,0,0,0,0,0,4,3,8,0], [0,0,0,0,0,0,1,2,4,0], [0,0,0,0,0,0,0,1,2,0], [0,0,0,0,0,0,0,0,1,0]]

theorem native_check_joint : fullCheck (fun i => D_joint.get i) N_joint T_joint Mjoint = true := by
  native_decide

theorem intFeasible_joint_native :
    IntFeasible (fun p => Lsub (LBj p)) (fun p => Usub (UHj p)) numj T_joint :=
  fullCheck_sound (fun i => D_joint.get i) N_joint T_joint Mjoint native_check_joint

/-- **V2-FLOOR joint, native route**: 1839727178682 / 2^30 = 1,713.38… ≤ cost of every plan realising the 2,625 pairs.
Depends on Lean.ofReduceBool (native_decide). -/
theorem v2floor_joint_native (E : Finset (Sub × Sub)) (hE : ∀ e ∈ E, e.1 < e.2)
    (hreal : ∀ p, Reach E (Lsub (LBj p)) (Usub (UHj p))) :
    (1839727178682 : ℝ) / 2 ^ 30 ≤ ∑ e ∈ E, wcut (22257 / 524288) (fdim e.1) (fdim e.2) :=
  floor_joint intFeasible_joint_native E hE hreal

#print axioms v2floor_joint_native
end V2Floor
