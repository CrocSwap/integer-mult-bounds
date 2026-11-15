import Work.Bridge.Net

/-!
# (key: bridge-net) The certificate of the BRIDGED five-stage network B_2

The three layers of free gates between twins, the signed exchange, and

    theorem bridge2_certificate (N : Bridge2 H T Sl C α Γ) :
        BCert α (Sum.inl : BLive Γ T Sl → BRole Γ T Sl C) (fun φ => card Γ * N.unit φ)

Scalar chain of one class (`x1 y1 x2 y2` on `X1 Y1 X2 Y2`), as in `bridged-word.md`:

    stage 0  F on pair 1     Y1 = y1 + x1
    stage 1  B on pair 1     X1 = -y1
    gates A  X1 += X2,  Y2 -= Y1
    stage 2  F on pair 1     Y1 = x1 + x2
    gates B  Y2 += Y1,  X1 -= X2          (X1 = -y1, Y2 = y2 - y1 + x2)
    stage 3  B on pair 2     X2 = y1 - y2
    stage 4  F on pair 2     Y2 = x2
    gates C  Y1 -= Y2,  X2 += X1          (X1 = -y1, X2 = -y2, Y1 = x1, Y2 = x2)
    exchange X_i := Y_i, Y_i := -X_i
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace BR
open Binary Matrix Finset RAM SS CB RF
noncomputable section

section Gates
variable {Γ T Sl C : Type}

/-- source of the gates of the layers A and B: `X1 ← X2`, `Y2 ← Y1`. -/
def pAB : BRole Γ T Sl C → BRole Γ T Sl C :=
  mkB (fun g t => kX2 (g,t)) (fun g t => kY1 (g,t)) (fun g t => kX2 (g,t))
    (fun g t => kY1 (g,t)) (fun g q => kS (g,q)) (fun g c => kC (g,c))

/-- layer A: `X1 += X2`, `Y2 -= Y1`. -/
def kA : BRole Γ T Sl C → ℚ :=
  mkB (fun _ _ => 1) (fun _ _ => 0) (fun _ _ => 0) (fun _ _ => -1) (fun _ _ => 0) (fun _ _ => 0)

/-- layer B: `X1 -= X2`, `Y2 += Y1`. -/
def kB : BRole Γ T Sl C → ℚ :=
  mkB (fun _ _ => -1) (fun _ _ => 0) (fun _ _ => 0) (fun _ _ => 1) (fun _ _ => 0) (fun _ _ => 0)

/-- source of the gates of the layer C: `Y1 ← Y2`, `X2 ← X1`. -/
def pC : BRole Γ T Sl C → BRole Γ T Sl C :=
  mkB (fun g t => kX1 (g,t)) (fun g t => kY2 (g,t)) (fun g t => kX1 (g,t))
    (fun g t => kY2 (g,t)) (fun g q => kS (g,q)) (fun g c => kC (g,c))

/-- layer C: `Y1 -= Y2`, `X2 += X1`. -/
def kCc : BRole Γ T Sl C → ℚ :=
  mkB (fun _ _ => 0) (fun _ _ => -1) (fun _ _ => 1) (fun _ _ => 0) (fun _ _ => 0) (fun _ _ => 0)

/-- scalar map of a gate layer. -/
def gsc (p : BRole Γ T Sl C → BRole Γ T Sl C) (k : BRole Γ T Sl C → ℚ)
    (x : BRole Γ T Sl C → ℂ) : BRole Γ T Sl C → ℂ := fun i => x i + (k i : ℂ) * x (p i)

/-- the signed exchange `X_i := Y_i`, `Y_i := -X_i` on both pairs. -/
def bpull : BRole Γ T Sl C → BRole Γ T Sl C :=
  mkB (fun g t => kY1 (g,t)) (fun g t => kX1 (g,t)) (fun g t => kY2 (g,t))
    (fun g t => kX2 (g,t)) (fun g q => kS (g,q)) (fun g c => kC (g,c))

def bsgn : BRole Γ T Sl C → ℚ :=
  mkB (fun _ _ => 1) (fun _ _ => -1) (fun _ _ => 1) (fun _ _ => -1) (fun _ _ => 1) (fun _ _ => 1)

variable [Fintype Γ] [DecidableEq Γ] [Fintype T] [DecidableEq T]
  [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C]

def brecM : Matrix (BRole Γ T Sl C) (BRole Γ T Sl C) ℚ :=
  fun i j => if j = bpull i then bsgn i else 0

lemma actPoint_brecM (x : BRole Γ T Sl C → ℂ) (i : BRole Γ T Sl C) :
    actPoint brecM x i = (bsgn i : ℂ) * x (bpull i) := by
  unfold actPoint
  rw [sum_eq_single (bpull i)]
  · simp [brecM]
  · intro j _ hj; simp [brecM, hj]
  · simp

/-- the scalar map of the whole network before the exchange, on one class. -/
def chain (x : BRole Γ T Sl C → ℂ) : BRole Γ T Sl C → ℂ :=
  gsc pC kCc (lift2 GF (lift2 GB (gsc pAB kB (lift1 GF (gsc pAB kA (lift1 GB (lift1 GF x)))))))

/-- **The scalar identity of the bridged chain**: `X_i = -y_i`, `Y_i = x_i` on both pairs,
helper slots unchanged. -/
lemma chain_eq (x : BRole Γ T Sl C → ℂ) (l : BLive Γ T Sl) :
    chain x (Sum.inl l) = mkB (fun g t => -x (kY1 (g,t))) (fun g t => x (kX1 (g,t)))
      (fun g t => -x (kY2 (g,t))) (fun g t => x (kX2 (g,t)))
      (fun g q => x (kS (g,q))) (fun g c => x (kC (g,c))) (Sum.inl l) := by
  rcases l with (((⟨g,t⟩|⟨g,t⟩)|(⟨g,t⟩|⟨g,t⟩))|⟨g,q⟩)
  all_goals
    simp only [chain, gsc, lift1, lift2, GF, GB, mkB, mkS, pAB, pC, kA, kB, kCc, pos1, pos2,
      kX1, kY1, kX2, kY2, kS, kC, jX, jY, jS, jC, Function.comp_apply]
    first
      | (push_cast; ring)
      | (push_cast; done)
      | ring

end Gates

section Net
variable {H T Sl C α Γ : Type} [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
  [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C] [Fintype α] [DecidableEq α]
  [Fintype Γ] [DecidableEq Γ]
variable (N : Bridge2 H T Sl C α Γ)

/-- gate layer A, after stage 1 and the first idle climb of pair 2: twins have equal frames. -/
lemma Bridge2.gateA : XRoute N.S3 N.S3 (gsc pAB kA) (fun _ => 0) := by
  refine gateP pAB kA N.S3 ?_
  rintro ((((⟨g,t⟩|⟨g,t⟩)|(⟨g,t⟩|⟨g,t⟩))|⟨g,q⟩)|⟨g,c⟩) hk
  · rfl
  · exact (hk rfl).elim
  · exact (hk rfl).elim
  · rfl
  · exact (hk rfl).elim
  · exact (hk rfl).elim

/-- gate layer B, after stage 2 and the second idle climb of pair 2. -/
lemma Bridge2.gateB : XRoute N.S5 N.S5 (gsc pAB kB) (fun _ => 0) := by
  refine gateP pAB kB N.S5 ?_
  rintro ((((⟨g,t⟩|⟨g,t⟩)|(⟨g,t⟩|⟨g,t⟩))|⟨g,q⟩)|⟨g,c⟩) hk
  · exact N.x23 g t
  · exact (hk rfl).elim
  · exact (hk rfl).elim
  · exact (N.y23 g t).symm
  · exact (hk rfl).elim
  · exact (hk rfl).elim

/-- gate layer C, after the final climbs. -/
lemma Bridge2.gateC : XRoute N.S8 N.S8 (gsc pC kCc) (fun _ => 0) := by
  refine gateP pC kCc N.S8 ?_
  rintro ((((⟨g,t⟩|⟨g,t⟩)|(⟨g,t⟩|⟨g,t⟩))|⟨g,q⟩)|⟨g,c⟩) hk
  · exact (hk rfl).elim
  · rfl
  · rfl
  · exact (hk rfl).elim
  · exact (hk rfl).elim
  · exact (hk rfl).elim

/-- the free shifts at the end. -/
def Bridge2.corr : BRole Γ T Sl C → Space α :=
  mkB (fun _ _ => 0) (fun g t => N.u g t) (fun _ _ => 0) (fun g t => N.u g t)
    (fun _ _ => 0) (fun _ _ => 0)

def Bridge2.S9 : BRole Γ T Sl C → CMat α := fun r => shift (N.corr r) * N.S8 r

/-- the whole word before the exchange: five stages, three idle-climb layers, three gate
layers. -/
lemma Bridge2.route :
    XRoute N.S0 N.S8 chain (fun φ => (Fintype.card Γ : ℝ) * N.unit φ) := by
  have R := ((((((((((N.stage0.trans N.stage1).trans N.climbA).trans N.gateA).trans
    N.stage2).trans N.climbB).trans N.gateB).trans N.stage3).trans N.stage4).trans
    N.fin).trans N.gateC)
  refine (R.castg ?_).cast (fun φ => ?_)
  · rfl
  · simp only [Bridge2.unit]
    ring

/-- **The scratch certificate of the bridged five-stage network with shared helper sets**,
in whole blocks, with its exact price for every price list. -/
theorem bridge2_certificate :
    BCert α (Sum.inl : BLive Γ T Sl → BRole Γ T Sl C)
      (fun φ => (Fintype.card Γ : ℝ) * N.unit φ) := by
  have R2 : XRoute N.S8 N.S9 id (fun _ => 0) := XRoute.shifts N.hm N.S8 N.corr
  have R3 : XRoute N.S9 (fun r => N.S9 (bpull r)) (actPoint brecM) (fun _ => 0) :=
    XRoute.gate brecM N.S9 _ (fun i j h => by
      have hj : j = bpull i := by
        by_contra hne
        exact h (by simp [brecM, hne])
      rw [hj])
  have Rt := ((N.route.trans R2).trans R3).cast (c' := fun φ => (Fintype.card Γ : ℝ) * N.unit φ)
    (fun φ => by first | ring | simp)
  have hSinv : ∀ r, ∃ M, N.S0 r * M = 1 := by
    rintro ((((⟨g,t⟩|⟨g,t⟩)|(⟨g,t⟩|⟨g,t⟩))|⟨g,q⟩)|⟨g,c⟩)
    · exact N.inv0 g t
    · refine ⟨1, ?_⟩
      show (N.M0 g).Φ 0 * 1 = 1
      rw [N.z0, Matrix.mul_one]
    · exact N.inv0 g t
    · refine ⟨1, ?_⟩
      show (N.M0 g).Φ 0 * 1 = 1
      rw [N.z0, Matrix.mul_one]
    · exact ⟨1, Matrix.mul_one _⟩
    · exact ⟨1, Matrix.mul_one _⟩
  choose S' hS' using hSinv
  have hT : ∀ l : BLive Γ T Sl, N.S9 (bpull (Sum.inl l)) = kernel α * N.S0 (Sum.inl l) := by
    rintro (((⟨g,t⟩|⟨g,t⟩)|(⟨g,t⟩|⟨g,t⟩))|⟨g,q⟩)
    · show shift (N.u g t) * N.YF g t = kernel α * (N.M0 g).Φ (tt (N.I.tv t))
      exact (N.term g t).symm
    · show shift (0 : Space α) * kernel α = kernel α * (N.M0 g).Φ 0
      rw [shift_zero, Matrix.one_mul, N.z0, Matrix.mul_one]
    · show shift (N.u g t) * N.YF g t = kernel α * (N.M0 g).Φ (tt (N.I.tv t))
      exact (N.term g t).symm
    · show shift (0 : Space α) * kernel α = kernel α * (N.M0 g).Φ 0
      rw [shift_zero, Matrix.one_mul, N.z0, Matrix.mul_one]
    · show shift (0 : Space α) * kernel α = kernel α * 1
      rw [shift_zero, Matrix.one_mul, Matrix.mul_one]
  have hg : ∀ x : BRole Γ T Sl C → ℂ,
      (∀ s, (∀ l : BLive Γ T Sl, (Sum.inl l : BRole Γ T Sl C) ≠ s) → x s = 0) →
      ∀ l : BLive Γ T Sl,
        (actPoint brecM ∘ (id ∘ chain)) x (Sum.inl l) = x (Sum.inl l) := by
    intro x _ l
    change actPoint brecM (chain x) (Sum.inl l) = _
    rw [actPoint_brecM]
    rcases l with (((⟨g,t⟩|⟨g,t⟩)|(⟨g,t⟩|⟨g,t⟩))|⟨g,q⟩)
    · show ((1:ℚ):ℂ) * chain x (Sum.inl (Sum.inl (Sum.inl (Sum.inr (g,t))))) = _
      rw [chain_eq]
      show ((1:ℚ):ℂ) * x (kX1 (g,t)) = x (kX1 (g,t))
      first | (push_cast; ring) | simp
    · show ((-1:ℚ):ℂ) * chain x (Sum.inl (Sum.inl (Sum.inl (Sum.inl (g,t))))) = _
      rw [chain_eq]
      show ((-1:ℚ):ℂ) * (-x (kY1 (g,t))) = x (kY1 (g,t))
      first | (push_cast; ring) | simp
    · show ((1:ℚ):ℂ) * chain x (Sum.inl (Sum.inl (Sum.inr (Sum.inr (g,t))))) = _
      rw [chain_eq]
      show ((1:ℚ):ℂ) * x (kX2 (g,t)) = x (kX2 (g,t))
      first | (push_cast; ring) | simp
    · show ((-1:ℚ):ℂ) * chain x (Sum.inl (Sum.inl (Sum.inr (Sum.inl (g,t))))) = _
      rw [chain_eq]
      show ((-1:ℚ):ℂ) * (-x (kY2 (g,t))) = x (kY2 (g,t))
      first | (push_cast; ring) | simp
    · show ((1:ℚ):ℂ) * chain x (Sum.inl (Sum.inr (g,q))) = _
      rw [chain_eq]
      show ((1:ℚ):ℂ) * x (kS (g,q)) = x (kS (g,q))
      first | (push_cast; ring) | simp
  exact XRoute.liveKernel (Sum.inl : BLive Γ T Sl → BRole Γ T Sl C) N.S0 S'
    (fun r => N.S9 (bpull r)) hS' _ _ Rt hg hT

end Net
end
end BR
end PowerSaving
end OAI

#print axioms OAI.PowerSaving.BR.chain_eq
#print axioms OAI.PowerSaving.BR.Bridge2.route
#print axioms OAI.PowerSaving.BR.bridge2_certificate
