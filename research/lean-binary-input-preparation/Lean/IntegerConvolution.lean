import Lean

/-! Literal little-endian coefficient convolution. The packing identity is
pure finite arithmetic, independent of any transform, rounding or compiler. -/
namespace CurrentMain.IntegerConvolution

def value (base : Nat) : List Nat → Nat
  | [] => 0
  | x::xs => x + base*value base xs

def addCoefficients : List Nat → List Nat → List Nat
  | [], ys => ys
  | xs, [] => xs
  | x::xs, y::ys => (x+y)::addCoefficients xs ys

def convolution : List Nat → List Nat → List Nat
  | [], _ => []
  | x::xs, ys => addCoefficients (ys.map (x*·)) (0::convolution xs ys)

theorem value_addCoefficients (base : Nat) (xs ys : List Nat) :
    value base (addCoefficients xs ys) = value base xs + value base ys := by
  induction xs generalizing ys with
  | nil => simp [addCoefficients,value]
  | cons x xs ih =>
    cases ys with
    | nil => simp [addCoefficients,value]
    | cons y ys =>
      simp only [addCoefficients,value,ih,Nat.mul_add]
      omega

theorem value_map_mul (base a : Nat) (xs : List Nat) :
    value base (xs.map (a*·)) = a*value base xs := by
  induction xs with
  | nil => simp [value]
  | cons x xs ih =>
    simp only [List.map_cons,value,ih,Nat.mul_add]
    rw [Nat.mul_left_comm base a]

theorem convolution_value (base : Nat) (xs ys : List Nat) :
    value base (convolution xs ys) = value base xs * value base ys := by
  induction xs with
  | nil => simp [convolution,value]
  | cons x xs ih =>
    rw [convolution,value_addCoefficients,value_map_mul,value,ih,value]
    simp only [Nat.zero_add,Nat.add_mul,Nat.mul_assoc]

def binaryValue (xs : List Nat) : Nat := value 2 xs

theorem binary_convolution (xs ys : List Nat) :
    binaryValue (convolution xs ys) = binaryValue xs * binaryValue ys :=
  convolution_value 2 xs ys

end CurrentMain.IntegerConvolution
#print axioms CurrentMain.IntegerConvolution.value_addCoefficients
#print axioms CurrentMain.IntegerConvolution.value_map_mul
#print axioms CurrentMain.IntegerConvolution.convolution_value
#print axioms CurrentMain.IntegerConvolution.binary_convolution
