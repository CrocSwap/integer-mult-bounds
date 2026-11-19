/-
Bridge7761R5 .  The #7761 `Net` instance, CONDITIONAL on the single expansion identity
  hO : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f      (the goal; everything else is checked)
Net.read holds by `dRec_read` + R4 side conditions (Net7761.read), Net.out by `outVec_out` + sc_out7761 + hO.
Also the BankedGraph fields stated on `Net7761 hO`: nest (R2), climb/cl/Mn/main8/card (R3).  Missing for a full BankedGraph: Contract (14+14 rows).
Kernel only.
-/
import Nov15.Bridge7761R4
import Nov15.Bridge7761R3
namespace Bridge7761
open Finset Module BankNC0 Submodule

noncomputable def Net7761 (hO : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f) :
    Net ℚ (Submodule (ZMod 2) BankWireC.V) (Fin 1262) (Fin 5746) where
  A := ChA7761
  B := ChB7761
  src k := chartOf (srcId k)
  dst k := chartOf (dstId k)
  d := dRec Recipe7761
  O := O7761
  read k := dRec_read Recipe7761 ChA7761 (fun k => chartOf (srcId k)) (fun k => chartOf (dstId k))
    (fun k p hp => sc_fld7761 k p hp) (fun k p hp => sc_ref7761 k p hp) k
  out f := by
    have := outVec_out Recipe7761 ChA7761 (fun k => chartOf (dstId k)) (ChB7761 f) (ofld7761 f) (oref7761 f)
      (fun p hp => by simp [ofld7761] at hp) (fun p hp => sc_out7761 f p hp)
    rw [hO f] at this
    exact this

theorem Net7761_nest (hO) (k : Fin 5746) :
    (Net7761 hO).src k ≤ (Net7761 hO).dst k ∨ (Net7761 hO).dst k ≤ (Net7761 hO).src k := nest7761 k k.2

theorem Net7761_climb (hO) (f : Fin 1262) : (Net7761 hO).A f ≤ (Net7761 hO).B f ∧
    finrank (ZMod 2) ((Net7761 hO).B f) = finrank (ZMod 2) ((Net7761 hO).A f) + cl7761 f := climbA7761 f

theorem Net7761_minors (hO) : ∀ C : Finset (Fin 1262),
    ((Net7761 hO).O.submatrix (fun c : C => (c : Fin 1262)) (fun c : C => (c : Fin 1262))).det ≠ 0 := minors7761

end Bridge7761
#print axioms Bridge7761.Net7761
#print axioms Bridge7761.Net7761_nest
#print axioms Bridge7761.Net7761_minors
