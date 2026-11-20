import Funding
import RankMoments

/-! Both tensor debit comparisons use the actual enclosed source moments. -/
namespace CertifiedPrices
open RankMoments

def ratio (a b : Nat) : Rat := (a : Rat) / (b : Rat)

def bitDebit : Rat :=
  let target := lowerTarget bitMain
  let α := ratio (upperPaid bitMain) target
  let firstLow := ratio (upperPaid bitLow (fun r => r ≤ 4) * grid) (lowCut.lo * target)
  let anyLow := ratio (upperPaid bitLow * grid) (lowCut.lo * target)
  let firstHigh := ratio (upperPaid bitHigh (fun r => 4 < r) * grid) (highCut.lo * target)
  let anyHigh := ratio (upperPaid bitHigh * grid) (highCut.lo * target)
  let dropped := ratio (floorCost.hi * upperTarget bitDrop) (grid * target)
  1 / (1 + 480*(1-α)) + 2*firstLow*anyLow^(479 : Nat) +
      2*firstHigh*anyHigh^(479 : Nat) + dropped^(480 : Nat)

def complexDebit : Rat :=
  let target := lowerTarget complexMain
  let α := ratio (upperPaid complexMain) target
  let γ := ratio (upperPaid complexTilt * grid) (complexCut.lo * target)
  let δ := ratio (12 * targetCount complexMain * grid^2) (complexCost.lo * target)
  1 / (1 + 1920*(1-α)) + 2*γ^(1920 : Nat) + 2*δ^(1920 : Nat)

def commonDen : Nat := 7*10^15
def bitSaving : Nat := 7*3879928046148
def complexSaving : Nat := 70*387992803563

def hasExponent (value : Nat) (c : DyadicRoot.Claim) : Bool := c.num*commonDen == value*c.den

def weights (xs : List Row) (weight : Row → Nat) : List (Nat × Nat) :=
  xs.filterMap (fun r => if weight r = 0 then none else some (r.power.rank, weight r))

def sourceBindings : Bool :=
  let b := commonDen-bitSaving
  let c := commonDen-complexSaving
  bitMain.all (fun r => hasExponent b r.power) &&
  bitLow.all (fun r => hasExponent (b+11*(commonDen/50)) r.power) &&
  bitHigh.all (fun r => hasExponent (b+13*(commonDen/50)) r.power) &&
  bitDrop.all (fun r => hasExponent (b-17*(commonDen/50)) r.power) &&
  complexMain.all (fun r => hasExponent c r.power) &&
  complexTilt.all (fun r => hasExponent (c+commonDen/7) r.power) &&
  hasExponent (11*(commonDen/50)) lowCut && lowCut.rank == 10 &&
  hasExponent (13*(commonDen/50)) highCut && highCut.rank == 11 &&
  hasExponent (17*(commonDen/50)) floorCost && floorCost.rank == 16 &&
  hasExponent (commonDen/7) complexCut && complexCut.rank == 11 &&
  hasExponent complexSaving complexCost && complexCost.rank == 11 &&
  weights bitMain Row.paid == weights bitLow Row.paid &&
  weights bitMain Row.paid == weights bitHigh Row.paid &&
  weights bitMain Row.target == weights bitDrop Row.target &&
  weights complexMain Row.paid == weights complexTilt Row.paid &&
  targetCount bitMain == 20706 && (bitMain.map Row.paid).sum == 107460 &&
  targetCount complexMain == 52512 && (complexMain.map Row.paid).sum == 283152 &&
  bitMain.any (fun r => r.power.rank == 4 && 0 < r.target) &&
  bitMain.any (fun r => r.power.rank == 64 && 1 < r.target)

set_option maxRecDepth 16384
set_option maxHeartbeats 10000000

theorem bit_funded : bitDebit < 1 - 12309863319385 / 10^25 := by decide +kernel
theorem complex_funded : complexDebit < 1 := by decide +kernel
theorem source_exponents_and_weights : sourceBindings = true := by decide +kernel
theorem source_savings :
    ratio bitSaving commonDen = MixedFunding.rawBit ∧
    ratio complexSaving commonDen = MixedFunding.trialC := by decide +kernel

theorem bit_floor_occurs : (4 : Nat)^240*64^240 = 16^480 := by decide +kernel

/-- Source root bounds, the two paid tensor totals, the six ordinary stage
inequalities and their common application price hold together. -/
theorem mixed_prices :
    (∀ c ∈ claims, 0 < c.den ∧ c.lo^c.den ≤ c.rank^c.num * 2^(frac*c.den) ∧
      c.rank^c.num * 2^(frac*c.den) ≤ c.hi^c.den) ∧
    sourceBindings = true ∧ ratio bitSaving commonDen = MixedFunding.rawBit ∧
    ratio complexSaving commonDen = MixedFunding.trialC ∧
    bitDebit < 1 - 12309863319385 / 10^25 ∧
    complexDebit < 1 ∧ MixedFunding.validStages 0 MixedFunding.stages ∧
    MixedFunding.trialC = MixedFunding.finalClaim + 7 / 10^14 :=
  ⟨table_sound, source_exponents_and_weights, source_savings.1, source_savings.2,
    bit_funded, complex_funded, MixedFunding.cold_through_six_stages, MixedFunding.supplier_room.1⟩

end CertifiedPrices

#print axioms CertifiedPrices.mixed_prices
