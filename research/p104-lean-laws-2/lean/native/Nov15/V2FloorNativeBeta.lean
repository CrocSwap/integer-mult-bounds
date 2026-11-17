/-
V2FloorNativeBeta (lane LEAN-NEXT21, Nov 16): V2-FLOOR β-only bound via native_decide.

*** THIS FILE DEPENDS ON Lean.ofReduceBool (native_decide). *** Fallback route, see V2FloorNativeJoint.lean.
-/
import Nov15.V2FloorFinal
import Nov15.V2FloorNativeChk

set_option maxRecDepth 100000
namespace V2Floor

/-- Mstar for the β pair set (107 distinct upper spaces, all hyperplanes). -/
def Mbeta : List (List ℕ) :=
  [[0,0,0,0,0,0,0,0,62,0], [0,0,0,0,0,0,0,0,36,0], [0,0,0,0,0,0,0,0,20,0], [0,0,0,0,0,0,0,0,12,0],
   [0,0,0,0,0,0,0,0,8,0], [0,0,0,0,0,0,0,0,4,0], [0,0,0,0,0,0,0,0,2,0], [0,0,0,0,0,0,0,0,1,0]]

theorem native_check_beta : fullCheck (fun i => D_beta.get i) N_beta T_beta Mbeta = true := by
  native_decide

theorem intFeasible_beta_native :
    IntFeasible (fun p => Lsub (LBb p)) (fun p => Usub (UHb p)) numb T_beta :=
  fullCheck_sound (fun i => D_beta.get i) N_beta T_beta Mbeta native_check_beta

/-- **V2-FLOOR β-only, native route**: 1536575200417 / 2^30 = 1,431.05… ≤ cost. Depends on Lean.ofReduceBool (native_decide). -/
theorem v2floor_beta_native (E : Finset (Sub × Sub)) (hE : ∀ e ∈ E, e.1 < e.2)
    (hreal : ∀ p, Reach E (Lsub (LBb p)) (Usub (UHb p))) :
    (1536575200417 : ℝ) / 2 ^ 30 ≤ ∑ e ∈ E, wcut 1 (fdim e.1) (fdim e.2) :=
  floor_beta intFeasible_beta_native E hE hreal

#print axioms v2floor_beta_native
end V2Floor
