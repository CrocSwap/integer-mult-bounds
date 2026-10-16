import Work.Bridge.Roles

/-!
# (key: bridge-net) The invocation as an abstract package, and a stage of such invocations

`Inv H T Sl C` is everything a network needs to know about one helper-circuit invocation
(PLAN2.md B1 item 5):

* `tv t`      the line of the bank pair `t`;
* `kx`, `ky`  the two climbs of a bank role across one window (label facts, no circuit);
* `cost`      the price of one invocation, for every price list;
* `fwd`, `bwd` the two statements of `CB.xinvocation_fwd_dirty` / `_bwd_dirty`: started on
  helper slots that carry ARBITRARY matrices `Z q`, the invocation is an exact block route
  with scalar map `shearF` (`y += x`) resp. `shearB` (`x -= y`); banks go from
  (line, 0) to (window, line-perp); every slot leaves with `Wn * Z q`.

`XCircuit.inv`: every block circuit `XCircuit` gives such a package (price `X.cost`).
`istage_fwd`, `istage_bwd`: `RF.sstage_fwd` / `_bwd` for a package.

No `sorry`.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace BR
open Binary Matrix Finset RAM SS CB RF
noncomputable section

section Pkg
variable {H T Sl C : Type} [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
  [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C]
variable {α : Type} [Fintype α] [DecidableEq α]

/-- frame matrices at the START of an invocation (as `CB.xin`, with the lines `tv`). -/
def iin (Xm : XMap H α) (tv : T → Space H) (Z : Sl → CMat α) (c : C → CMat α) :
    Box T Sl C → CMat α :=
  stamp (fun t => Xm.Φ (tt (tv t))) (fun _ => Xm.Φ 0) Z c

/-- frame matrices at the END of an invocation (as `CB.xout`). -/
def iout (Xm : XMap H α) (tv : T → Space H) (Z : Sl → CMat α) (c : C → CMat α) :
    Box T Sl C → CMat α :=
  stamp (fun _ => Xm.Φ 1) (fun t => Xm.Φ (1 + tt (tv t))) Z c

end Pkg

/-- **An invocation, as a package.**  See the file header. -/
structure Inv (H T Sl C : Type) [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
    [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C] where
  tv : T → Space H
  kx : ∀ t, Climb (lineL (tv t)) fullL
  ky : ∀ t, Climb zeroL (perpL (tv t))
  cost : (ℕ → ℝ) → ℝ
  fwd : ∀ {α : Type} [Fintype α] [DecidableEq α] (Xm : XMap H α) (N0 Wn : CMat α),
    Xm.Φ 0 * N0 = 1 → Xm.Φ 1 = Wn * Xm.Φ 0 → ∀ (Z : Sl → CMat α) (c0 c1 : C → CMat α),
    XRoute (iin Xm tv Z c0) (iout Xm tv (fun q => Wn * Z q) c1) shearF cost
  bwd : ∀ {α : Type} [Fintype α] [DecidableEq α] (Xm : XMap H α) (N0 Wn : CMat α),
    Xm.Φ 0 * N0 = 1 → Xm.Φ 1 = Wn * Xm.Φ 0 → ∀ (Z : Sl → CMat α) (c0 c1 : C → CMat α),
    XRoute (iin Xm tv Z c0) (iout Xm tv (fun q => Wn * Z q) c1) shearB cost

section Stage
variable {H T Sl C α Γ : Type} [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
  [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C] [Fintype α] [DecidableEq α]
  [Fintype Γ] [DecidableEq Γ]

/-- every block circuit gives a package, with the price `X.cost`. -/
def _root_.OAI.PowerSaving.CB.XCircuit.inv (X : XCircuit H T Sl C) : Inv H T Sl C where
  tv := X.K.tv
  kx := X.kx
  ky := X.ky
  cost := X.cost
  fwd := fun Xm N0 Wn hN hW Z c0 c1 => xinvocation_fwd_dirty X Xm N0 Wn hN hW Z c0 c1
  bwd := fun Xm N0 Wn hN hW Z c0 c1 => xinvocation_bwd_dirty X Xm N0 Wn hN hW Z c0 c1

@[simp] lemma inv_cost (X : XCircuit H T Sl C) (φ : ℕ → ℝ) : X.inv.cost φ = X.cost φ := rfl
@[simp] lemma inv_tv (X : XCircuit H T Sl C) : X.inv.tv = X.K.tv := rfl

/-- the two idle climbs of a bank role across one window: ONE block of rank `card H - 1`. -/
lemma Inv.climbX (I : Inv H T Sl C) (Xm : XMap H α) (t : T) :
    XReach (Xm.Φ (tt (I.tv t))) (Xm.Φ 1) (fun φ => bcost φ (Fintype.card H - 1)) := by
  have h := Xm.climb (I.kx t)
  exact h.cast (fun φ => by simp [fullL, lineL])

lemma Inv.climbY (I : Inv H T Sl C) (Xm : XMap H α) (t : T) :
    XReach (Xm.Φ 0) (Xm.Φ (1 + tt (I.tv t))) (fun φ => bcost φ (Fintype.card H - 1)) := by
  have h := Xm.climb (I.ky t)
  exact h.cast (fun φ => by simp [perpL, zeroL])

/-- frames at the START of a stage (as `RF.sIn`, with the lines `tv`). -/
def bIn (tv : T → Space H) (εX : T → Γ ≃ Γ) (M : Γ → XMap H α) (Z : Γ → Sl → CMat α)
    (c : Γ → C → CMat α) : SRole Γ T Sl C → CMat α :=
  mkS (fun g t => (M (εX t g)).Φ (tt (tv t))) (fun g t => (M (εX t g)).Φ 0) Z c

/-- frames at the END of a stage. -/
def bOut (tv : T → Space H) (εX : T → Γ ≃ Γ) (M : Γ → XMap H α) (Z : Γ → Sl → CMat α)
    (c : Γ → C → CMat α) : SRole Γ T Sl C → CMat α :=
  mkS (fun g t => (M (εX t g)).Φ 1) (fun g t => (M (εX t g)).Φ (1 + tt (tv t))) Z c

lemma bIn_sem (tv : T → Space H) (εX : T → Γ ≃ Γ) (εS : Γ ≃ Γ) (M : Γ → XMap H α)
    (Z : Γ → Sl → CMat α) (c : Γ → C → CMat α) (d : Γ) :
    bIn tv εX M Z c ∘ sem εX εS d = iin (M d) tv (fun q => Z (εS d) q) (fun k => c (εS d) k) := by
  funext b
  rcases b with ((t|t)|(q|k))
  · show (M (εX t ((εX t).symm d))).Φ (tt (tv t)) = (M d).Φ (tt (tv t))
    rw [Equiv.apply_symm_apply]
  · show (M (εX t ((εX t).symm d))).Φ 0 = (M d).Φ 0
    rw [Equiv.apply_symm_apply]
  · rfl
  · rfl

lemma bOut_sem (tv : T → Space H) (εX : T → Γ ≃ Γ) (εS : Γ ≃ Γ) (M : Γ → XMap H α)
    (Z : Γ → Sl → CMat α) (c : Γ → C → CMat α) (d : Γ) :
    bOut tv εX M Z c ∘ sem εX εS d = iout (M d) tv (fun q => Z (εS d) q) (fun k => c (εS d) k) := by
  funext b
  rcases b with ((t|t)|(q|k))
  · show (M (εX t ((εX t).symm d))).Φ 1 = (M d).Φ 1
    rw [Equiv.apply_symm_apply]
  · show (M (εX t ((εX t).symm d))).Φ (1 + tt (tv t)) = (M d).Φ (1 + tt (tv t))
    rw [Equiv.apply_symm_apply]
  · rfl
  · rfl

variable (I : Inv H T Sl C)

/-- **A forward stage of packaged invocations on shared helper sets** (as `RF.sstage_fwd`). -/
theorem istage_fwd (εX : T → Γ ≃ Γ) (εS : Γ ≃ Γ) (M : Γ → XMap H α) (N0 Wn : Γ → CMat α)
    (hN : ∀ d, (M d).Φ 0 * N0 d = 1) (hW : ∀ d, (M d).Φ 1 = Wn d * (M d).Φ 0)
    (Z : Γ → Sl → CMat α) (c0 c1 : Γ → C → CMat α) :
    XRoute (bIn I.tv εX M Z c0) (bOut I.tv εX M (fun g q => Wn (εS.symm g) * Z g q) c1)
      GF (fun φ => (Fintype.card Γ : ℝ) * I.cost φ) := by
  refine sstage εX εS (h := shearF) (cost := I.cost) (fun d => ?_) (fun d x => ?_)
  · rw [bIn_sem, bOut_sem]
    exact I.fwd (M d) (N0 d) (Wn (εS.symm (εS d))) (hN d)
      (by rw [Equiv.symm_apply_apply]; exact hW d) _ _ _
  · funext b
    rcases b with ((t|t)|(q|k)) <;> rfl

/-- **A backward stage of packaged invocations on shared helper sets.** -/
theorem istage_bwd (εX : T → Γ ≃ Γ) (εS : Γ ≃ Γ) (M : Γ → XMap H α) (N0 Wn : Γ → CMat α)
    (hN : ∀ d, (M d).Φ 0 * N0 d = 1) (hW : ∀ d, (M d).Φ 1 = Wn d * (M d).Φ 0)
    (Z : Γ → Sl → CMat α) (c0 c1 : Γ → C → CMat α) :
    XRoute (bIn I.tv εX M Z c0) (bOut I.tv εX M (fun g q => Wn (εS.symm g) * Z g q) c1)
      GB (fun φ => (Fintype.card Γ : ℝ) * I.cost φ) := by
  refine sstage εX εS (h := shearB) (cost := I.cost) (fun d => ?_) (fun d x => ?_)
  · rw [bIn_sem, bOut_sem]
    exact I.bwd (M d) (N0 d) (Wn (εS.symm (εS d))) (hN d)
      (by rw [Equiv.symm_apply_apply]; exact hW d) _ _ _
  · funext b
    rcases b with ((t|t)|(q|k)) <;> rfl

end Stage
end
end BR
end PowerSaving
end OAI

#print axioms OAI.PowerSaving.CB.XCircuit.inv
#print axioms OAI.PowerSaving.BR.istage_fwd
#print axioms OAI.PowerSaving.BR.istage_bwd
