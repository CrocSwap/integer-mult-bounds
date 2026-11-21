import Std

/-! These exact tests use the true ambient, productive floor and paid ceiling.
The terminal reserves include the additional dyadic specialization. -/
namespace CarrierGuards
set_option maxRecDepth 100000
set_option maxHeartbeats 10000000

def bitA := 134^480
def complexA := 153^264
def bitH := 240000000000000
def complexH := 3300000000
def bitC : Rat := 3879928046148/10^15
def rawC : Rat := 388013/10^8
def covered : Rat := 3879928035648/10^15
def caller : Rat := 387992803556/10^14
def gap : Rat := 1/10^14

structure Bound where
  ambient : Nat
  ceiling : Nat
  floor : Nat
  bits : Nat
  logPower : Nat
  shift : Nat
  num : Nat
  den : Nat
  amplitude : Nat
  maxLog : Nat

def bit : Bound := ⟨bitA,11^480,16^480,bitH,71,8192,32,37,9300,3394⟩
def complex : Bound := ⟨complexA,10^264,17^264,complexH,31,2048,48,59,204,1918⟩

def valid (v : Bound) (cnum cden : Nat) : Prop :=
  0 < v.num ∧ v.num < v.den ∧ v.ceiling^v.den ≤ v.floor^v.num ∧
  2^(v.shift*(v.den-v.num))*v.ceiling^v.den ≤ (4*v.ambient)^v.num ∧
  (4*v.ambient)^cnum ≤ v.amplitude^cden ∧
  4*v.ambient ≤ 2^v.maxLog ∧
  cnum*(v.shift+v.maxLog) ≤ cden*v.logPower ∧
  128*v.amplitude*v.num^v.logPower ≤ 45*v.den^v.logPower

instance (v : Bound) (a b : Nat) : Decidable (valid v a b) := by unfold valid; infer_instance

theorem bit_guard : valid bit 97 25000 := by decide +kernel
theorem complex_guard : valid complex 1 250 := by decide +kernel

theorem caps : 0 < bitC ∧ bitC < 97/25000 ∧ 0 < rawC ∧ rawC < 1/250 ∧
    128/(45:Rat) = (16/15*2)/(3/4) := by decide +kernel

theorem product_and_root_depth :
    (2:Nat)*bitA ≤ 2^3400 ∧ 3400 < bitH ∧
    856*264*complexA*(complexH+1)^2 < 2^14000 ∧ 14000 < complexH := by
  decide +kernel

theorem bit_final :
    bitH*(bitC-covered) = 2520 ∧
    (bitH+bit.shift)^bit.logPower*2^5 < bit.shift^bit.logPower*2^2520 ∧
    (13*16 : Nat) < 15*2^5 := by decide +kernel

theorem complex_final :
    (666:Rat) ≤ complexH*(rawC-(caller+5*gap)) ∧
    (complexH+complex.shift)^complex.logPower*2 < complex.shift^complex.logPower*2^666 := by
  decide +kernel

#print axioms bit_guard
#print axioms complex_guard
#print axioms caps
#print axioms product_and_root_depth
#print axioms bit_final
#print axioms complex_final
end CarrierGuards
