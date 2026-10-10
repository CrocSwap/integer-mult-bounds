import Work.Bridge.Inv

/-!
# (key: bridge-net) The BRIDGED five-stage network B_2 with shared helper sets, abstract form

Generalises `RF.Fold3S` / `RF.fold3s_certificate` (`Work.Reframe.SCert`) to the bridged word
of PLAN2.md B1: every class `(g,t)` has TWO bank pairs `(X1,Y1)`, `(X2,Y2)` with the same
line; five stages of invocations

    stage 0  forward   on pair 1      invocation of the class (g,t):  g
    stage 1  backward  on pair 1                                      r1 t g
    stage 2  forward   on pair 1                                      r2 t g
    stage 3  backward  on pair 2                                      r3 t g
    stage 4  forward   on pair 2                                      r4 t g

and three layers of FREE gates between twins at equal frames:

    after stage 1 (pair 2 has climbed to the frames of pair 1):   X1 += X2,  Y2 -= Y1
    after stage 2 (pair 2 has climbed one more window):           Y2 += Y1,  X1 -= X2
    after the final climbs (all four roles at their end frames):  Y1 -= Y2,  X2 += X1

Result on both pairs: `X_i = -y_i`, `Y_i = x_i`; then the usual signed exchange.

The idle pair does not move during a stage.  Its climbs are ONE block per role:
`aX2`, `aY2` (pair 2 before the first gate layer, prices `caX`, `caY`; in B_2 ONE block of
rank `2h-2` each),
the window of stage 2 (pair 2 before the second gate layer, rank `card H - 1`, from the
package: `Inv.climbX`, `Inv.climbY`), `fX1`, `fY1` (pair 1 at the end, prices `cX1`, `cY1`;
in B_2 ONE block of rank `2h+2` each), `fX2`, `fY2` (pair 2 at the end, prices `cX2`, `cY2`;
in B_2 one block of rank `4` each).  The prices are arbitrary functions of the price list, so
a geometry that makes an idle climb in several blocks can be plugged in as well.

`Bridge2 H T Sl C α Γ` is everything the wiring needs to know about the geometry;
`bridge2_certificate`: a `BCert` on the live roles `BLive Γ T Sl`
(`card Γ * (4 card T + card Sl)` of them, `BR.card_BLive`) whose price, for EVERY price
list, is `card Γ * N.unit φ`,

    N.unit φ = 5 * N.I.cost φ + card T * ((caX φ + caY φ) + 2 * bcost φ (card H - 1)
                 + (cX1 φ + cY1 φ) + (cX2 φ + cY2 φ)).
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace BR
open Binary Matrix Finset RAM SS CB RF
noncomputable section

/-- See the file header.  Fields in the style of `RF.Fold3S`; stages are numbered 0 to 4. -/
structure Bridge2 (H T Sl C α Γ : Type) [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
    [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C] [Fintype α] [DecidableEq α] where
  /-- the invocation (for a block circuit `X`: `X.inv`). -/
  I : Inv H T Sl C
  /-- frame maps of the invocations of the five stages. -/
  M0 : Γ → XMap H α
  M1 : Γ → XMap H α
  M2 : Γ → XMap H α
  M3 : Γ → XMap H α
  M4 : Γ → XMap H α
  /-- the class `(g,t)` is served by the invocation `g` in stage 0 and `r_l t g` in stage `l`. -/
  r1 : T → Γ ≃ Γ
  r2 : T → Γ ≃ Γ
  r3 : T → Γ ≃ Γ
  r4 : T → Γ ≃ Γ
  /-- the invocation `d` of stage `l` uses the helper set (and the copies) `s_l d`. -/
  s1 : Γ ≃ Γ
  s2 : Γ ≃ Γ
  s3 : Γ ≃ Γ
  s4 : Γ ≃ Γ
  /-- inverse of the frame of the base, and frame of the window, of every invocation. -/
  N1 : Γ → CMat α
  W1 : Γ → CMat α
  N2 : Γ → CMat α
  W2 : Γ → CMat α
  N3 : Γ → CMat α
  W3 : Γ → CMat α
  N4 : Γ → CMat α
  W4 : Γ → CMat α
  u : Γ → T → Space α
  YF : Γ → T → CMat α
  hm : 2 ≤ Fintype.card α
  /-- prices of the idle climbs, for every price list.  B_2 with merged climbs:
  `caX = caY = fun φ => bcost φ (2h-2)`, `cX1 = cY1 = fun φ => bcost φ (2h+2)`,
  `cX2 = cY2 = fun φ => bcost φ 4`. -/
  caX : (ℕ → ℝ) → ℝ
  caY : (ℕ → ℝ) → ℝ
  cX1 : (ℕ → ℝ) → ℝ
  cY1 : (ℕ → ℝ) → ℝ
  cX2 : (ℕ → ℝ) → ℝ
  cY2 : (ℕ → ℝ) → ℝ
  inv0 : ∀ g t, ∃ N : CMat α, (M0 g).Φ (tt (I.tv t)) * N = 1
  z0 : ∀ g, (M0 g).Φ 0 = 1
  hN1 : ∀ d, (M1 d).Φ 0 * N1 d = 1
  hW1 : ∀ d, (M1 d).Φ 1 = W1 d * (M1 d).Φ 0
  hN2 : ∀ d, (M2 d).Φ 0 * N2 d = 1
  hW2 : ∀ d, (M2 d).Φ 1 = W2 d * (M2 d).Φ 0
  hN3 : ∀ d, (M3 d).Φ 0 * N3 d = 1
  hW3 : ∀ d, (M3 d).Φ 1 = W3 d * (M3 d).Φ 0
  hN4 : ∀ d, (M4 d).Φ 0 * N4 d = 1
  hW4 : ∀ d, (M4 d).Φ 1 = W4 d * (M4 d).Φ 0
  /-- the bank frames a stage leaves are the bank frames the next stage starts from. -/
  x01 : ∀ g t, (M0 g).Φ 1 = (M1 (r1 t g)).Φ (tt (I.tv t))
  y01 : ∀ g t, (M0 g).Φ (1 + tt (I.tv t)) = (M1 (r1 t g)).Φ 0
  x12 : ∀ g t, (M1 (r1 t g)).Φ 1 = (M2 (r2 t g)).Φ (tt (I.tv t))
  y12 : ∀ g t, (M1 (r1 t g)).Φ (1 + tt (I.tv t)) = (M2 (r2 t g)).Φ 0
  x23 : ∀ g t, (M2 (r2 t g)).Φ 1 = (M3 (r3 t g)).Φ (tt (I.tv t))
  y23 : ∀ g t, (M2 (r2 t g)).Φ (1 + tt (I.tv t)) = (M3 (r3 t g)).Φ 0
  x34 : ∀ g t, (M3 (r3 t g)).Φ 1 = (M4 (r4 t g)).Φ (tt (I.tv t))
  y34 : ∀ g t, (M3 (r3 t g)).Φ (1 + tt (I.tv t)) = (M4 (r4 t g)).Φ 0
  /-- the five windows of a helper set make up the kernel. -/
  sfin : ∀ g, W4 (s4.symm g) * (W3 (s3.symm g) * (W2 (s2.symm g) *
    (W1 (s1.symm g) * (M0 g).Φ 1))) = kernel α
  /-- pair 2, idle in stages 0 and 1: ONE block from its start frame to the frame of its
  twin after stage 1. -/
  aX2 : ∀ g t, XReach ((M0 g).Φ (tt (I.tv t))) ((M1 (r1 t g)).Φ 1) caX
  aY2 : ∀ g t, XReach ((M0 g).Φ 0) ((M1 (r1 t g)).Φ (1 + tt (I.tv t))) caY
  /-- pair 1, idle in stages 3 and 4: ONE block from its frame after stage 2 to the end. -/
  fX1 : ∀ g t, XReach ((M2 (r2 t g)).Φ 1) (kernel α) cX1
  fY1 : ∀ g t, XReach ((M2 (r2 t g)).Φ (1 + tt (I.tv t))) (YF g t) cY1
  /-- pair 2 after stage 4: ONE final block. -/
  fX2 : ∀ g t, XReach ((M4 (r4 t g)).Φ 1) (kernel α) cX2
  fY2 : ∀ g t, XReach ((M4 (r4 t g)).Φ (1 + tt (I.tv t))) (YF g t) cY2
  term : ∀ g t, kernel α * (M0 g).Φ (tt (I.tv t)) = shift (u g t) * YF g t

section Net
variable {H T Sl C α Γ : Type} [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
  [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C] [Fintype α] [DecidableEq α]
  [Fintype Γ] [DecidableEq Γ]
variable (N : Bridge2 H T Sl C α Γ)

/-- price of the blocks of one unit (one element of `Γ`): five invocations and the idle
climbs of the four bank roles of every class. -/
def Bridge2.unit (φ : ℕ → ℝ) : ℝ :=
  5 * N.I.cost φ + (Fintype.card T : ℝ) * ((N.caX φ + N.caY φ)
    + 2 * bcost φ (Fintype.card H - 1)
    + (N.cX1 φ + N.cY1 φ) + (N.cX2 φ + N.cY2 φ))

/-- scratch copies always enter and leave with the matrix `1` (also: the helper slots at the
start, with `C := Sl`). -/
def cOne (Γ C α : Type) [Fintype α] [DecidableEq α] : Γ → C → CMat α := fun _ _ => 1

/-- the bank index of stage 0: the class `(g,t)` belongs to the invocation `g`. -/
abbrev bid (Γ T : Type) : T → Γ ≃ Γ := fun _ => Equiv.refl Γ

/-! bank frames of the class `(g,t)`: `xi l`, `yi l` at the START of stage `l`; `xo l`,
`yo l` at the END of stage `l` (only where no next stage follows on that pair). -/
def Bridge2.xi0 (g : Γ) (t : T) : CMat α := (N.M0 g).Φ (tt (N.I.tv t))
def Bridge2.yi0 (g : Γ) (t : T) : CMat α := (N.M0 g).Φ 0
def Bridge2.xi1 (g : Γ) (t : T) : CMat α := (N.M1 (N.r1 t g)).Φ (tt (N.I.tv t))
def Bridge2.yi1 (g : Γ) (t : T) : CMat α := (N.M1 (N.r1 t g)).Φ 0
def Bridge2.xi2 (g : Γ) (t : T) : CMat α := (N.M2 (N.r2 t g)).Φ (tt (N.I.tv t))
def Bridge2.yi2 (g : Γ) (t : T) : CMat α := (N.M2 (N.r2 t g)).Φ 0
def Bridge2.xo2 (g : Γ) (t : T) : CMat α := (N.M2 (N.r2 t g)).Φ 1
def Bridge2.yo2 (g : Γ) (t : T) : CMat α := (N.M2 (N.r2 t g)).Φ (1 + tt (N.I.tv t))
def Bridge2.xi3 (g : Γ) (t : T) : CMat α := (N.M3 (N.r3 t g)).Φ (tt (N.I.tv t))
def Bridge2.yi3 (g : Γ) (t : T) : CMat α := (N.M3 (N.r3 t g)).Φ 0
def Bridge2.xi4 (g : Γ) (t : T) : CMat α := (N.M4 (N.r4 t g)).Φ (tt (N.I.tv t))
def Bridge2.yi4 (g : Γ) (t : T) : CMat α := (N.M4 (N.r4 t g)).Φ 0
def Bridge2.xo4 (g : Γ) (t : T) : CMat α := (N.M4 (N.r4 t g)).Φ 1
def Bridge2.yo4 (g : Γ) (t : T) : CMat α := (N.M4 (N.r4 t g)).Φ (1 + tt (N.I.tv t))

/-- helper slots after the stages 0, 1, 2, 3, 4 (at the start: `cOne Γ Sl α`). -/
def Bridge2.Z1 : Γ → Sl → CMat α := fun g _ => (N.M0 g).Φ 1
def Bridge2.Z2 : Γ → Sl → CMat α := fun g q => N.W1 (N.s1.symm g) * N.Z1 g q
def Bridge2.Z3 : Γ → Sl → CMat α := fun g q => N.W2 (N.s2.symm g) * N.Z2 g q
def Bridge2.Z4 : Γ → Sl → CMat α := fun g q => N.W3 (N.s3.symm g) * N.Z3 g q
def Bridge2.Z5 : Γ → Sl → CMat α := fun g q => N.W4 (N.s4.symm g) * N.Z4 g q

/-- frames: at the start; after stage 0; after stage 1; after the first idle climb of pair 2
(first gate layer here); after stage 2; after the second idle climb of pair 2 (second gate
layer here); after stage 3; after stage 4; after the final climbs (third gate layer here). -/
def Bridge2.S0 : BRole Γ T Sl C → CMat α := mkB N.xi0 N.yi0 N.xi0 N.yi0 (cOne Γ Sl α) (cOne Γ C α)
def Bridge2.S1 : BRole Γ T Sl C → CMat α := mkB N.xi1 N.yi1 N.xi0 N.yi0 N.Z1 (cOne Γ C α)
def Bridge2.S2 : BRole Γ T Sl C → CMat α := mkB N.xi2 N.yi2 N.xi0 N.yi0 N.Z2 (cOne Γ C α)
def Bridge2.S3 : BRole Γ T Sl C → CMat α := mkB N.xi2 N.yi2 N.xi2 N.yi2 N.Z2 (cOne Γ C α)
def Bridge2.S4 : BRole Γ T Sl C → CMat α := mkB N.xo2 N.yo2 N.xi2 N.yi2 N.Z3 (cOne Γ C α)
def Bridge2.S5 : BRole Γ T Sl C → CMat α := mkB N.xo2 N.yo2 N.xi3 N.yi3 N.Z3 (cOne Γ C α)
def Bridge2.S6 : BRole Γ T Sl C → CMat α := mkB N.xo2 N.yo2 N.xi4 N.yi4 N.Z4 (cOne Γ C α)
def Bridge2.S7 : BRole Γ T Sl C → CMat α := mkB N.xo2 N.yo2 N.xo4 N.yo4 N.Z5 (cOne Γ C α)
def Bridge2.S8 : BRole Γ T Sl C → CMat α :=
  mkB (fun _ _ => kernel α) N.YF (fun _ _ => kernel α) N.YF (fun _ _ => kernel α) (cOne Γ C α)

/-- stage 0: forward on pair 1, every helper set starts at the matrix `1`. -/
lemma Bridge2.stage0 :
    XRoute N.S0 N.S1 (lift1 GF) (fun φ => (Fintype.card Γ : ℝ) * N.I.cost φ) := by
  have h := istage_fwd N.I (bid Γ T) (Equiv.refl Γ) N.M0 (fun _ => 1) (fun g => (N.M0 g).Φ 1)
    (fun d => by rw [N.z0, Matrix.mul_one]) (fun d => by rw [N.z0, Matrix.mul_one])
    (cOne Γ Sl α) (cOne Γ C α) (cOne Γ C α)
  have e : bOut N.I.tv (bid Γ T) N.M0
      (fun g (q : Sl) => (N.M0 ((Equiv.refl Γ).symm g)).Φ 1 * cOne Γ Sl α g q) (cOne Γ C α)
      = mkS N.xi1 N.yi1 N.Z1 (cOne Γ C α) := by
    funext r
    rcases r with (((⟨g,t⟩|⟨g,t⟩)|⟨g,q⟩)|⟨g,c⟩)
    · exact N.x01 g t
    · exact N.y01 g t
    · show (N.M0 g).Φ 1 * 1 = (N.M0 g).Φ 1
      rw [Matrix.mul_one]
    · rfl
  have h' : XRoute (bIn N.I.tv (bid Γ T) N.M0 (cOne Γ Sl α) (cOne Γ C α))
      (mkS N.xi1 N.yi1 N.Z1 (cOne Γ C α)) GF (fun φ => (Fintype.card Γ : ℝ) * N.I.cost φ) := by
    rw [← e]
    exact h
  exact blift1 N.xi0 N.yi0 h'

/-- stage 1: backward on pair 1; the helper set `g` serves the invocation `s1⁻¹ g`. -/
lemma Bridge2.stage1 :
    XRoute N.S1 N.S2 (lift1 GB) (fun φ => (Fintype.card Γ : ℝ) * N.I.cost φ) := by
  have h := istage_bwd N.I N.r1 N.s1 N.M1 N.N1 N.W1 N.hN1 N.hW1 N.Z1 (cOne Γ C α) (cOne Γ C α)
  have e : bOut N.I.tv N.r1 N.M1 (fun g q => N.W1 (N.s1.symm g) * N.Z1 g q) (cOne Γ C α)
      = mkS N.xi2 N.yi2 N.Z2 (cOne Γ C α) := by
    funext r
    rcases r with (((⟨g,t⟩|⟨g,t⟩)|⟨g,q⟩)|⟨g,c⟩)
    · exact N.x12 g t
    · exact N.y12 g t
    · rfl
    · rfl
  have h' : XRoute (bIn N.I.tv N.r1 N.M1 N.Z1 (cOne Γ C α))
      (mkS N.xi2 N.yi2 N.Z2 (cOne Γ C α)) GB (fun φ => (Fintype.card Γ : ℝ) * N.I.cost φ) := by
    rw [← e]
    exact h
  exact blift1 N.xi0 N.yi0 h'

/-- stage 2: forward on pair 1. -/
lemma Bridge2.stage2 :
    XRoute N.S3 N.S4 (lift1 GF) (fun φ => (Fintype.card Γ : ℝ) * N.I.cost φ) :=
  blift1 N.xi2 N.yi2
    (istage_fwd N.I N.r2 N.s2 N.M2 N.N2 N.W2 N.hN2 N.hW2 N.Z2 (cOne Γ C α) (cOne Γ C α))

/-- stage 3: backward on pair 2. -/
lemma Bridge2.stage3 :
    XRoute N.S5 N.S6 (lift2 GB) (fun φ => (Fintype.card Γ : ℝ) * N.I.cost φ) := by
  have h := istage_bwd N.I N.r3 N.s3 N.M3 N.N3 N.W3 N.hN3 N.hW3 N.Z3 (cOne Γ C α) (cOne Γ C α)
  have e : bOut N.I.tv N.r3 N.M3 (fun g q => N.W3 (N.s3.symm g) * N.Z3 g q) (cOne Γ C α)
      = mkS N.xi4 N.yi4 N.Z4 (cOne Γ C α) := by
    funext r
    rcases r with (((⟨g,t⟩|⟨g,t⟩)|⟨g,q⟩)|⟨g,c⟩)
    · exact N.x34 g t
    · exact N.y34 g t
    · rfl
    · rfl
  have h' : XRoute (bIn N.I.tv N.r3 N.M3 N.Z3 (cOne Γ C α))
      (mkS N.xi4 N.yi4 N.Z4 (cOne Γ C α)) GB (fun φ => (Fintype.card Γ : ℝ) * N.I.cost φ) := by
    rw [← e]
    exact h
  exact blift2 N.xo2 N.yo2 h'

/-- stage 4: forward on pair 2. -/
lemma Bridge2.stage4 :
    XRoute N.S6 N.S7 (lift2 GF) (fun φ => (Fintype.card Γ : ℝ) * N.I.cost φ) :=
  blift2 N.xo2 N.yo2
    (istage_fwd N.I N.r4 N.s4 N.M4 N.N4 N.W4 N.hN4 N.hW4 N.Z4 (cOne Γ C α) (cOne Γ C α))

/-- first idle climb of pair 2 (stages 0 and 1 in ONE block per role), to the frames of
pair 1 after stage 1. -/
lemma Bridge2.climbA :
    XRoute N.S2 N.S3 id (fun φ => (Fintype.card Γ : ℝ) *
      ((Fintype.card T : ℝ) * (N.caX φ + N.caY φ))) := by
  have H1 := XRoute.reach_all N.S2 N.S3
    (mkB (fun _ _ _ => 0) (fun _ _ _ => 0) (fun _ _ => N.caX)
      (fun _ _ => N.caY) (fun _ _ _ => 0) (fun _ _ _ => 0)) (by
      rintro ((((⟨g,t⟩|⟨g,t⟩)|(⟨g,t⟩|⟨g,t⟩))|⟨g,q⟩)|⟨g,c⟩)
      · exact XReach.refl _
      · exact XReach.refl _
      · show XReach ((N.M0 g).Φ (tt (N.I.tv t))) ((N.M2 (N.r2 t g)).Φ (tt (N.I.tv t))) N.caX
        rw [← N.x12 g t]
        exact N.aX2 g t
      · show XReach ((N.M0 g).Φ 0) ((N.M2 (N.r2 t g)).Φ 0) N.caY
        rw [← N.y12 g t]
        exact N.aY2 g t
      · exact XReach.refl _
      · exact XReach.refl _)
  refine H1.cast (fun φ => ?_)
  simp_rw [mkB_map (fun c : (ℕ → ℝ) → ℝ => c φ)]
  rw [sum_mkB]
  simp only [sum_const, card_univ, nsmul_eq_mul, mul_zero, add_zero, zero_add]
  ring

/-- second idle climb of pair 2: the window of stage 2, ONE block of rank `card H - 1` per
role, to the frames of pair 1 after stage 2. -/
lemma Bridge2.climbB :
    XRoute N.S4 N.S5 id (fun φ => (Fintype.card Γ : ℝ) *
      ((Fintype.card T : ℝ) * (2 * bcost φ (Fintype.card H - 1)))) := by
  have H1 := XRoute.reach_all N.S4 N.S5
    (mkB (fun _ _ _ => 0) (fun _ _ _ => 0) (fun _ _ φ => bcost φ (Fintype.card H - 1))
      (fun _ _ φ => bcost φ (Fintype.card H - 1)) (fun _ _ _ => 0) (fun _ _ _ => 0)) (by
      rintro ((((⟨g,t⟩|⟨g,t⟩)|(⟨g,t⟩|⟨g,t⟩))|⟨g,q⟩)|⟨g,c⟩)
      · exact XReach.refl _
      · exact XReach.refl _
      · show XReach ((N.M2 (N.r2 t g)).Φ (tt (N.I.tv t))) ((N.M3 (N.r3 t g)).Φ (tt (N.I.tv t)))
          (fun φ => bcost φ (Fintype.card H - 1))
        rw [← N.x23 g t]
        exact N.I.climbX (N.M2 (N.r2 t g)) t
      · show XReach ((N.M2 (N.r2 t g)).Φ 0) ((N.M3 (N.r3 t g)).Φ 0)
          (fun φ => bcost φ (Fintype.card H - 1))
        rw [← N.y23 g t]
        exact N.I.climbY (N.M2 (N.r2 t g)) t
      · exact XReach.refl _
      · exact XReach.refl _)
  refine H1.cast (fun φ => ?_)
  simp_rw [mkB_map (fun c : (ℕ → ℝ) → ℝ => c φ)]
  rw [sum_mkB]
  simp only [sum_const, card_univ, nsmul_eq_mul, mul_zero, add_zero, zero_add]
  ring

/-- the final climbs: pair 1 from its frames after stage 2 (ONE block per role for the
stages 3, 4 and the rest), pair 2 from its frames after stage 4; the helper slots are
already at the kernel. -/
lemma Bridge2.fin :
    XRoute N.S7 N.S8 id (fun φ => (Fintype.card Γ : ℝ) *
      ((Fintype.card T : ℝ) * ((N.cX1 φ + N.cY1 φ) + (N.cX2 φ + N.cY2 φ)))) := by
  have H1 := XRoute.reach_all N.S7 N.S8
    (mkB (fun _ _ => N.cX1) (fun _ _ => N.cY1) (fun _ _ => N.cX2) (fun _ _ => N.cY2)
      (fun _ _ _ => 0) (fun _ _ _ => 0)) (by
      rintro ((((⟨g,t⟩|⟨g,t⟩)|(⟨g,t⟩|⟨g,t⟩))|⟨g,q⟩)|⟨g,c⟩)
      · exact N.fX1 g t
      · exact N.fY1 g t
      · exact N.fX2 g t
      · exact N.fY2 g t
      · show XReach (N.W4 (N.s4.symm g) * (N.W3 (N.s3.symm g) * (N.W2 (N.s2.symm g) *
          (N.W1 (N.s1.symm g) * (N.M0 g).Φ 1)))) (kernel α) (fun _ => 0)
        rw [N.sfin g]
        exact XReach.refl _
      · exact XReach.refl _)
  refine H1.cast (fun φ => ?_)
  simp_rw [mkB_map (fun c : (ℕ → ℝ) → ℝ => c φ)]
  rw [sum_mkB]
  simp only [sum_const, card_univ, nsmul_eq_mul, mul_zero, add_zero, zero_add]
  ring

end Net
end
end BR
end PowerSaving
end OAI

#print axioms OAI.PowerSaving.BR.Bridge2.stage0
#print axioms OAI.PowerSaving.BR.Bridge2.stage1
#print axioms OAI.PowerSaving.BR.Bridge2.stage2
#print axioms OAI.PowerSaving.BR.Bridge2.stage3
#print axioms OAI.PowerSaving.BR.Bridge2.stage4
#print axioms OAI.PowerSaving.BR.Bridge2.climbA
#print axioms OAI.PowerSaving.BR.Bridge2.climbB
#print axioms OAI.PowerSaving.BR.Bridge2.fin
