import TrialRows

namespace CarrierTrial
open DyadicRoot

set_option maxRecDepth 65536
set_option maxHeartbeats 60000000

def grid : Nat := 2^160
def claims : List Claim := ((main++split++prune++lift).map Row.power)++[splitScale,floorScale]

theorem exact_roots : claims.all (valid 352 160) = true := by decide +kernel

theorem enclosing (c : Claim) (hc : c ∈ claims) :
    0<c.den ∧ c.lo^c.den ≤ c.rank^c.num * 2^(160*c.den) ∧
      c.rank^c.num * 2^(160*c.den) ≤ c.hi^c.den := by
  apply valid_sound 352
  exact List.all_eq_true.mp exact_roots c hc

def lowT (xs : List Row) := (xs.map (fun row ↦ row.target*row.power.lo)).sum
def upT (xs : List Row) := (xs.map (fun row ↦ row.target*row.power.hi)).sum
def upP (xs : List Row) := (xs.map (fun row ↦ row.paid*row.power.hi)).sum

def weights (xs : List Row) (weight : Row → Nat) : List (Nat × Nat) :=
  xs.filterMap (fun r ↦ if weight r = 0 then none else some (r.power.rank,weight r))

def price (n d : Nat) (c : Claim) : Bool := d*c.num == n*c.den
def cnum := 388013
def cden := 10^8
def tnum := cden-cnum

theorem one_source :
    (main.map Row.target).sum = 52512 ∧ (main.map Row.paid).sum = 283152 ∧
    main.any (fun r ↦ r.power.rank == 17 && 1 < r.target) = true ∧
    weights main Row.paid = weights split Row.paid ∧ weights main Row.target = weights prune Row.target ∧
    main.all (fun r ↦ price tnum cden r.power) = true ∧
    split.all (fun r ↦ price (tnum+22*10^6) cden r.power) = true ∧
    prune.all (fun r ↦ price (tnum-31*10^6) cden r.power) = true ∧
    splitScale.rank=10 ∧ price 11 50 splitScale = true ∧ floorScale.rank=17 ∧ price 31 100 floorScale = true ∧
    lift.all (fun r ↦ price tnum cden r.power) = true ∧
    weights lift Row.target = [(3,1),(5,1),(7,1)] ∧ weights lift Row.paid = [(1,2),(4,1),(9,1)] :=
  by decide +kernel

def ratio (u v : Nat) : Rat := (u : Rat) / v

theorem static_prices :
    ratio (upP main) (lowT main) < 1-88/(10^10:Rat) ∧
    ratio (upP split*grid) (lowT main*splitScale.lo) < 947/1000 ∧
    ratio (upT prune*floorScale.hi) (lowT main*grid) < 949/1000 ∧
    upP lift < lowT lift := by decide +kernel

theorem productive_surplus :
    1/(1+264*(88/(10^10:Rat))) + 2*(947/1000:Rat)^264 + (949/1000:Rat)^264 <
      1-1/(10^7:Rat) := by decide +kernel

/-- The ordinary service keeps its previously funded price. Only the
compile-time test of the fixed rational word uses the higher price. -/
theorem distinct_prices :
    (3879928035646 / (10^15:Rat)) > 387992803556/(10^14:Rat) + 4/(10^14:Rat) ∧
    388013/(10^8:Rat) > 3879928035646/(10^15:Rat) ∧
    388013/(10^8:Rat) - (387992803556/(10^14:Rat)+5/(10^14:Rat)) =
      20196439/(10^14:Rat) := by decide +kernel

#print axioms enclosing
#print axioms one_source
#print axioms static_prices
#print axioms productive_surplus
#print axioms distinct_prices
end CarrierTrial
