import Nov15.FloorK22
import Nov15.NumCertKData

/-!
NUMCERT-K22 : discharges FloorK22's `NumCert22 tbar22` by the kernel-checked interval arithmetic of
NumCertK / NumCertKData, and states `ceiling22_unconditional`.  Kernel only; no native_decide.
-/
namespace FloorK22
open JointCeiling CallerCost

/-- the K(S22) 17-call invoice, merged by rank, is F(s) = sum c_r r^s with the 24 coefficients `cfK`. -/
theorem invoice_eq_Fc (s : ℝ) :
    Finv s (invoice (caller 6 7) nK22 17) = NumCertK.Fc NumCertK.cfK s := by
  simp only [Finv, Fh, invoice, caller, callerT, callerP, armT, armP, nK22, scale, NumCertK.Fc, NumCertK.cfK,
    List.range_succ, List.range_zero]
  norm_num
  ring

/-- **NumCert22 discharged** (kernel-checked; F(s) < 0 for every s in (0, 1 - .0060197405]). -/
theorem numCert22 : NumCert22 tbar22 := by
  intro s hs0 hs
  rw [invoice_eq_Fc]
  apply NumCertK.cfK_neg s hs0.le
  have : (((9939802595 / 10 ^ 10 : ℚ)) : ℝ) = 1 - tbar22 := by unfold tbar22; push_cast; norm_num
  rw [this]; exact hs

section ClassK22
open FloorE2E FloorD0 FloorK22Data ExportLaw
variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C] [Fintype C]
variable {Pub H Kfin : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}
  {dim : C → ℕ} {e : C ≃ Fin rows.length} {D : KData C (Reg → K)}

/-- **kappa <= .0060197405 on class K(S22), no numeric hypothesis**: `ceiling22` with NumCert22 discharged. -/
theorem ceiling22_unconditional (hdim : ∀ a b : C, a < b → dim a < dim b)
    (hK : ClassK22 Pub H Kfin ini w dim e D) (n : Inv)
    (hF : ∀ s : ℝ, 0 < s → s ≤ 1 →
      Finv s n = helperD0 (fun x : ℝ => x ^ s) dim H ini w - keptCost (fun x : ℝ => x ^ s) dim H ini w)
    {s : ℝ} (hs0 : 0 < s) (hs : s ≤ 1 - tbar22) :
    Finv s (invoice (caller 6 7) n 17) < 0 :=
  ceiling22 hdim hK n hF numCert22 hs0 hs

end ClassK22
end FloorK22

#print axioms FloorK22.numCert22
#print axioms FloorK22.ceiling22_unconditional
