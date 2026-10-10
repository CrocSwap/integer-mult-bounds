import Work.Carrier.Glue

/-!
# (key: carrier-thm) A carrier circuit given by its phases: hypotheses and scalar identities

`Phased H T Sl C` is the hypothesis structure of the carrier invocation theorem in the general
scope (any ordered mix of gates `(x, slot)`, `(slot, slot)`, `(x, y)`, `(slot, y)`):

* phase A (before the scatter), phase B (after it) and the final climbs F are exact block routes
  on the LIVE roles `L3 T Sl` (`x`, `y`, slots: all on the same footing), for every block frame
  map, with the gate products `MA`, `MB` (and the transposed inverses for the backward word);
* the scatter goes through the scratch copies: `c += Cc s` at the labels `cen`, the copies come
  down, `y += Jr c` at 0;
* `hx`: no gate INTO an x role, `hy`: no gate READS a y role, `hid`: the y roles receive exactly
  the x roles — three facts about the ONE matrix `Mt = MB * scatM (Jr * Cc) * MA`.

This file: `Mt`, its inverse `Mti`, and the scalar identities of the forward and of the backward
word (`fwd_scalar`, `bwd_scalar`): with the two dirt gates `g1`, `g8` (resp. the transposes of
`g1i`, `h8`) the word does `y += x` (resp. `x -= y`) for ARBITRARY slot contents.

No `sorry`.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace CR
open Binary Matrix Finset RAM SS CB BR
noncomputable section

/-- labels of the live roles at the START of an invocation. -/
def lab3 {H T Sl : Type} (tv : T → Space H) : L3 T Sl → Lbl H :=
  Sum.elim (Sum.elim (fun t => lineL (tv t)) (fun _ => zeroL)) (fun _ => zeroL)

/-- **The hypotheses of the carrier invocation theorem, by phases.**  See the file header. -/
structure Phased (H T Sl C : Type) [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
    [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C] where
  tv : T → Space H
  kx : ∀ t, Climb (lineL (tv t)) fullL
  ky : ∀ t, Climb zeroL (perpL (tv t))
  cen : C → Lbl H
  kc : ∀ k, Climb zeroL (cen k)
  Cc : Matrix C Sl ℚ
  Jr : Matrix T C ℚ
  labA : L3 T Sl → Lbl H
  labB : L3 T Sl → Lbl H
  labF : L3 T Sl → Lbl H
  hAy : ∀ t, (labA (lY t)).P = 0
  hAc : ∀ k q, Cc k q ≠ 0 → (cen k).P = (labA (lS q)).P
  hFx : ∀ t, (labF (lX t)).P = 1
  hFy : ∀ t, (labF (lY t)).P = 1 + tt (tv t)
  hFs : ∀ q, (labF (lS q)).P = 1
  MA : Matrix (L3 T Sl) (L3 T Sl) ℚ
  MAi : Matrix (L3 T Sl) (L3 T Sl) ℚ
  MB : Matrix (L3 T Sl) (L3 T Sl) ℚ
  MBi : Matrix (L3 T Sl) (L3 T Sl) ℚ
  hAi : MAi * MA = 1
  hBi : MBi * MB = 1
  hx : ∀ t j, (MB * scatM (Jr * Cc) * MA) (lX t) j = if lX t = j then 1 else 0
  hy : ∀ i t, (MB * scatM (Jr * Cc) * MA) i (lY t) = if i = lY t then 1 else 0
  hid : ∀ S t, (MB * scatM (Jr * Cc) * MA) (lY S) (lX t) = if S = t then 1 else 0
  rA : List ℕ
  rB : List ℕ
  rF : List ℕ
  pA : ∀ {α : Type} [Fintype α] [DecidableEq α] (Xm : XMap H α),
    XRoute (fun r => Xm.Φ (lab3 tv r).P) (fun r => Xm.Φ (labA r).P) (actPoint MA)
        (fun φ => rcost φ rA) ∧
    XRoute (fun r => Xm.Φ (lab3 tv r).P) (fun r => Xm.Φ (labA r).P) (actPoint MAiᵀ)
        (fun φ => rcost φ rA)
  pB : ∀ {α : Type} [Fintype α] [DecidableEq α] (Xm : XMap H α),
    XRoute (fun r => Xm.Φ (labA r).P) (fun r => Xm.Φ (labB r).P) (actPoint MB)
        (fun φ => rcost φ rB) ∧
    XRoute (fun r => Xm.Φ (labA r).P) (fun r => Xm.Φ (labB r).P) (actPoint MBiᵀ)
        (fun φ => rcost φ rB)
  pF : ∀ {α : Type} [Fintype α] [DecidableEq α] (Xm : XMap H α),
    XRoute (fun r => Xm.Φ (labB r).P) (fun r => Xm.Φ (labF r).P) id (fun φ => rcost φ rF)

section Alg
variable {H T Sl C : Type} [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
  [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C]

namespace Phased
variable (K : Phased H T Sl C)

/-- the product of ALL gates of the main phase (scatter with the copies eliminated). -/
def Mt : Matrix (L3 T Sl) (L3 T Sl) ℚ := K.MB * scatM (K.Jr * K.Cc) * K.MA
/-- its inverse. -/
def Mti : Matrix (L3 T Sl) (L3 T Sl) ℚ := K.MAi * scatMi (K.Jr * K.Cc) * K.MBi

/-- price of one invocation: the blocks of the three phases and one block per copy. -/
def cost (φ : ℕ → ℝ) : ℝ :=
  rcost φ K.rA + (∑ k, bcost φ (K.cen k).d) + rcost φ K.rB + rcost φ K.rF

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

end Phased
end Alg
end
end CR
end PowerSaving
end OAI

#print axioms OAI.PowerSaving.CR.Phased.fwd_scalar
#print axioms OAI.PowerSaving.CR.Phased.bwd_scalar
