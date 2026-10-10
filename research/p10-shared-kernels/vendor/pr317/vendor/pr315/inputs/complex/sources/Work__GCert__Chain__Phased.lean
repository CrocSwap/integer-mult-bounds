import Work.Carrier.Phases
import Work.GFrame.Labels.All

/-!
# (key: gx-chain) The certificate as two halves: `Scal` (scalar half) and `Lab` (label half)

`Scal T Sl C`: the scalar fields of `CR.Phased` (three facts about ONE matrix
`Mt = MB * scatM (Jr * Cc) * MA`).  The scalar identities of the forward and of the backward
word (`fwd_scalar`, `bwd_scalar`) are those of `Work/Carrier/Phases.lean`, word for word.

`Lab H S`: subspace labels (`GF.SLbl H`), routes of the three phases on the generalised engine
(`GF.GRoute`) through every stage-B frame map (`GF.BXMap H α`), and facts about dimensions at
the two ends.  No projector, no `Climb`.

No `sorry`.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace GX
open Binary Matrix Finset RAM SS CB BR CR GF
noncomputable section

/-- **The scalar half.** -/
structure Scal (T Sl C : Type) [Fintype T] [DecidableEq T]
    [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C] where
  Cc : Matrix C Sl ℚ
  Jr : Matrix T C ℚ
  MA : Matrix (L3 T Sl) (L3 T Sl) ℚ
  MAi : Matrix (L3 T Sl) (L3 T Sl) ℚ
  MB : Matrix (L3 T Sl) (L3 T Sl) ℚ
  MBi : Matrix (L3 T Sl) (L3 T Sl) ℚ
  hAi : MAi * MA = 1
  hBi : MBi * MB = 1
  hx : ∀ t j, (MB * scatM (Jr * Cc) * MA) (lX t) j = if lX t = j then 1 else 0
  hy : ∀ i t, (MB * scatM (Jr * Cc) * MA) i (lY t) = if i = lY t then 1 else 0
  hid : ∀ S t, (MB * scatM (Jr * Cc) * MA) (lY S) (lX t) = if S = t then 1 else 0

/-- **The label half.**  See `checks/wht26/shared/gcert-interface.md`, section CHAIN. -/
structure Lab (H : Type) [Fintype H] [DecidableEq H] {T Sl C : Type} [Fintype T] [DecidableEq T]
    [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C] (S : Scal T Sl C) where
  tv : T → Space H
  hunit : ∀ t, dot (tv t) (tv t) = 1
  hgap : ∀ t, ∃ p, tv t p = 0
  lab0 : L3 T Sl → SLbl H
  labA : L3 T Sl → SLbl H
  labB : L3 T Sl → SLbl H
  labF : L3 T Sl → SLbl H
  cen : C → SLbl H
  z0 : SLbl H
  hz0 : z0.dim = 0
  h0x : ∀ t, (lab0 (lX t)).dim = 1 ∧ (lab0 (lX t)).Mem (tv t)
  h0y : ∀ t, (lab0 (lY t)).dim = 0
  h0s : ∀ q, (lab0 (lS q)).dim = 0
  hAy : ∀ t, labA (lY t) = z0
  hAc : ∀ k q, S.Cc k q ≠ 0 → cen k = labA (lS q)
  hcen : ∀ k, 0 < (cen k).dim
  hFx : ∀ t, (labF (lX t)).dim = Fintype.card H
  hFs : ∀ q, (labF (lS q)).dim = Fintype.card H
  hFy : ∀ t, (labF (lY t)).dim + 1 = Fintype.card H ∧
    ∀ x, (labF (lY t)).Mem x → dot (tv t) x = 0
  rA : List ℕ
  rB : List ℕ
  rF : List ℕ
  pA : ∀ {α : Type} [Fintype α] [DecidableEq α] (X : BXMap H α),
    Fintype.card H < Fintype.card α →
    GRoute (fun r => X.Φ (lab0 r)) (fun r => X.Φ (labA r)) (actPoint S.MA)
        (fun φ => rcost φ rA) ∧
    GRoute (fun r => X.Φ (lab0 r)) (fun r => X.Φ (labA r)) (actPoint S.MAiᵀ)
        (fun φ => rcost φ rA)
  pB : ∀ {α : Type} [Fintype α] [DecidableEq α] (X : BXMap H α),
    Fintype.card H < Fintype.card α →
    GRoute (fun r => X.Φ (labA r)) (fun r => X.Φ (labB r)) (actPoint S.MB)
        (fun φ => rcost φ rB) ∧
    GRoute (fun r => X.Φ (labA r)) (fun r => X.Φ (labB r)) (actPoint S.MBiᵀ)
        (fun φ => rcost φ rB)
  pF : ∀ {α : Type} [Fintype α] [DecidableEq α] (X : BXMap H α),
    Fintype.card H < Fintype.card α →
    GRoute (fun r => X.Φ (labB r)) (fun r => X.Φ (labF r)) id (fun φ => rcost φ rF)

/-- price of one invocation: the blocks of the three phases and one block per copy. -/
def Lab.cost {H : Type} [Fintype H] [DecidableEq H] {T Sl C : Type} [Fintype T] [DecidableEq T]
    [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C] {S : Scal T Sl C} (L : Lab H S)
    (φ : ℕ → ℝ) : ℝ :=
  rcost φ L.rA + (∑ k, bcost φ (L.cen k).dim) + rcost φ L.rB + rcost φ L.rF

section Alg
variable {H T Sl C : Type} [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
  [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C]

namespace Scal
variable (K : Scal T Sl C)

/-- the product of ALL gates of the main phase (scatter with the copies eliminated). -/
def Mt : Matrix (L3 T Sl) (L3 T Sl) ℚ := K.MB * scatM (K.Jr * K.Cc) * K.MA
/-- its inverse. -/
def Mti : Matrix (L3 T Sl) (L3 T Sl) ℚ := K.MAi * scatMi (K.Jr * K.Cc) * K.MBi


lemma im : K.Mti * K.Mt = 1 := by
  unfold Mti Mt
  have hB : ∀ X : Matrix (L3 T Sl) (L3 T Sl) ℚ, K.MBi * (K.MB * X) = X := fun X => by
    rw [← Matrix.mul_assoc, K.hBi, Matrix.one_mul]
  have hS : ∀ X : Matrix (L3 T Sl) (L3 T Sl) ℚ,
      scatMi (K.Jr * K.Cc) * (scatM (K.Jr * K.Cc) * X) = X := fun X => by
    rw [← Matrix.mul_assoc, scat_inv, Matrix.one_mul]
  rw [Matrix.mul_assoc, Matrix.mul_assoc, Matrix.mul_assoc, hB, hS, K.hAi]

lemma mi : K.Mt * K.Mti = 1 := mul_eq_one_comm.mp K.im

lemma hxm : PX * K.Mt = PX := PX_mul_of (M := K.Mt) K.hx
lemma hmy : K.Mt * PY = PY := mul_PY_of (M := K.Mt) K.hy
lemma hiy : K.Mti * PY = PY := dirt_iy K.hmy K.im

/-- **the dirt rule, forward**, for the matrices of the circuit. -/
lemma hF : g8 K.Mti * K.Mt * g1 K.Mt = 1 + PY * K.Mt * PX := by
  unfold g8 g1
  exact dirt_fwd PX_sq PY_sq PX_PY PY_PX K.hxm K.hmy K.im K.mi

/-- **the dirt rule, backward.** -/
lemma hB : g1i K.Mt * K.Mti * h8 K.Mt = 1 - PY * K.Mt * PX := by
  unfold g1i h8
  exact dirt_bwd PX_sq PY_sq PX_PY PY_PX K.hxm K.hmy K.im K.mi

/-- live part of the forward word before the scatter: `y -= K s`, then phase A. -/
def f1 (u : L3 T Sl → ℂ) : L3 T Sl → ℂ := actPoint K.MA (actPoint (g1 K.Mt) u)
/-- after the scatter: phase B, then the slot rows of the inverse. -/
def f2 (u : L3 T Sl → ℂ) : L3 T Sl → ℂ := actPoint (g8 K.Mti) (actPoint K.MB u)
/-- the same for the backward word (transposed inverses). -/
def b1 (u : L3 T Sl → ℂ) : L3 T Sl → ℂ := actPoint K.MAiᵀ (actPoint (g1i K.Mt)ᵀ u)
def b2 (u : L3 T Sl → ℂ) : L3 T Sl → ℂ := actPoint (h8 K.Mt)ᵀ (actPoint K.MBiᵀ u)

lemma fwd_live (u : L3 T Sl → ℂ) :
    K.f2 (actPoint (scatM (K.Jr * K.Cc)) (K.f1 u)) = actPoint (1 + PY * K.Mt * PX) u := by
  rw [← K.hF]
  show actPoint (g8 K.Mti) (actPoint K.MB (actPoint (scatM (K.Jr * K.Cc))
      (actPoint K.MA (actPoint (g1 K.Mt) u))))
    = actPoint (g8 K.Mti * (K.MB * scatM (K.Jr * K.Cc) * K.MA) * g1 K.Mt) u
  rw [actPoint_mul, actPoint_mul, actPoint_mul, actPoint_mul]

lemma bwd_live (u : L3 T Sl → ℂ) :
    K.b2 (actPoint ((scatMi (K.Jr * K.Cc))ᵀ) (K.b1 u))
      = actPoint ((1 - PY * K.Mt * PX)ᵀ) u := by
  rw [← K.hB]
  show actPoint (h8 K.Mt)ᵀ (actPoint K.MBiᵀ (actPoint (scatMi (K.Jr * K.Cc))ᵀ
      (actPoint K.MAiᵀ (actPoint (g1i K.Mt)ᵀ u))))
    = actPoint ((g1i K.Mt * (K.MAi * scatMi (K.Jr * K.Cc) * K.MBi) * h8 K.Mt)ᵀ) u
  rw [Matrix.transpose_mul, Matrix.transpose_mul, Matrix.transpose_mul, Matrix.transpose_mul,
    actPoint_mul, actPoint_mul, actPoint_mul, actPoint_mul]

lemma liveAct_glue (φ : (L3 T Sl → ℂ) → (L3 T Sl → ℂ)) (u : L3 T Sl → ℂ) (c : C → ℂ) :
    liveAct φ (glue u c) = glue (φ u) c :=
  congrArg (fun v => glue (φ v) c) (glue_up u c)

/-- **Scalar identity of the forward word**: `y += x`, slots restored, for ARBITRARY slot
contents (the copies are erased before and after). -/
theorem fwd_scalar (z : Box T Sl C → ℂ) :
    eraseC (liveAct K.f2 (gateS bY bC K.Jr (gateS bC bS K.Cc (liveAct K.f1 (eraseC z)))))
      = shearF z := by
  have h1 : liveAct K.f1 (eraseC z) = glue (K.f1 (z ∘ upE)) (fun _ => 0) := by
    rw [erase_glue z, liveAct_glue]
  have hs : gateS bY bC K.Jr (gateS bC bS K.Cc (glue (K.f1 (z ∘ upE)) (fun _ => 0))) ∘ upE
      = actPoint (scatM (K.Jr * K.Cc)) (K.f1 (z ∘ upE)) := by
    have h := scat_glue K.Jr K.Cc (glue (K.f1 (z ∘ upE)) (fun _ => 0)) rfl
    rw [glue_up] at h
    exact h
  rw [h1]
  unfold liveAct
  rw [erase_of_glue, hs, K.fwd_live, act_shear K.Mt K.hid]
  exact glue_shearF z

/-- **Scalar identity of the backward word**: `x -= y`, slots restored. -/
theorem bwd_scalar (z : Box T Sl C → ℂ) :
    eraseC (liveAct K.b2 (gateS bS bC (-K.Ccᵀ) (gateS bC bY K.Jrᵀ (liveAct K.b1 (eraseC z)))))
      = shearB z := by
  have h1 : liveAct K.b1 (eraseC z) = glue (K.b1 (z ∘ upE)) (fun _ => 0) := by
    rw [erase_glue z, liveAct_glue]
  have hs : gateS bS bC (-K.Ccᵀ) (gateS bC bY K.Jrᵀ (glue (K.b1 (z ∘ upE)) (fun _ => 0))) ∘ upE
      = actPoint ((scatMi (K.Jr * K.Cc))ᵀ) (K.b1 (z ∘ upE)) := by
    have h := scat_glueT K.Jr K.Cc (glue (K.b1 (z ∘ upE)) (fun _ => 0)) rfl
    rw [glue_up] at h
    exact h
  rw [h1]
  unfold liveAct
  rw [erase_of_glue, hs, K.bwd_live, act_shearT K.Mt K.hid]
  exact glue_shearB z

end Scal
end Alg
end
end GX
end PowerSaving
end OAI

#print axioms OAI.PowerSaving.GX.Scal.fwd_scalar
#print axioms OAI.PowerSaving.GX.Scal.bwd_scalar
