import SequentialBitAddition

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Reusable arithmetic for the actual paired-bit subtract/compare controller.
Every column reuses the accepted seven finite Boolean adder gates on (a, !b)
with initial carry true. Carry-out derives order; no order premise is assumed.
This module is a word specification, not a priced bulk complement or Nat
subtraction instruction. The companion controller supplies the symbol steps.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false

namespace PairedDifferenceArithmetic
open SequentialBitAddition

def oneCarry (r : Registers) : Registers := {r with carry := true}
def operands (reverse : Bool) (p : PairBit) : PairBit :=
  if reverse then (p.2,!p.1) else (p.1,!p.2)
def inputPairs (reverse : Bool) (p : List PairBit) : List PairBit := p.map (operands reverse)
def result (reverse : Bool) (p : List PairBit) (r : Registers) : Result :=
  scan (inputPairs reverse p) (oneCarry r)
def lhs (reverse : Bool) (p : List PairBit) : List Bool :=
  if reverse then rightBits p else leftBits p
def rhs (reverse : Bool) (p : List PairBit) : List Bool :=
  if reverse then leftBits p else rightBits p

/-- Finite Boolean-word range, independent of canonical leading bits. -/
theorem decode_bounds (xs : List Bool) : 0≤decode xs ∧ decode xs<(2:Int)^xs.length := by
  induction xs with
  | nil => simp [decode]
  | cons b xs ih =>
      cases b <;> simp only [decode,bit,Bool.false_eq_true,if_false,if_true,
        List.length_cons,pow_succ] <;> constructor <;> omega

/-- Complement is interpreted here; the controller performs one current-bit
complement per column rather than an unpriced word operation. -/
theorem decode_complement (xs : List Bool) :
    decode (xs.map (!·)) = (2:Int)^xs.length-1-decode xs := by
  induction xs with
  | nil => simp [decode]
  | cons b xs ih =>
      cases b <;> simp only [List.map_cons,decode,bit,Bool.not_false,Bool.not_true,
        Bool.false_eq_true,if_false,if_true,List.length_cons,pow_succ,ih] <;> ring

theorem result_length (reverse : Bool) (p : List PairBit) (r : Registers) :
    (result reverse p r).output.length=p.length := by
  simp only [result,scan_storage,inputPairs,List.length_map]

/-- Direct substitution into the already accepted full-adder scan identity. -/
theorem result_value (reverse : Bool) (p : List PairBit) (r : Registers) :
    decode (result reverse p r).output + (2:Int)^p.length * bit (result reverse p r).registers.carry =
      decode (lhs reverse p)-decode (rhs reverse p)+(2:Int)^p.length := by
  have h:=scan_value (inputPairs reverse p) (oneCarry r)
  have hl:leftBits (inputPairs reverse p)=lhs reverse p := by
    cases reverse <;> simp [leftBits,rightBits,inputPairs,operands,lhs,List.map_map,Function.comp_def]
  have hr:rightBits (inputPairs reverse p)=(rhs reverse p).map (!·) := by
    cases reverse <;> simp [leftBits,rightBits,inputPairs,operands,rhs,List.map_map,Function.comp_def]
  have hn:(inputPairs reverse p).length=p.length := by simp [inputPairs]
  have he:(rhs reverse p).length=p.length := by cases reverse <;> simp [rhs,leftBits,rightBits]
  rw [hl,hr,hn,decode_complement,he] at h
  change decode (result reverse p r).output + (2:Int)^p.length * bit (result reverse p r).registers.carry =
    decode (lhs reverse p) + ((2:Int)^p.length-1-decode (rhs reverse p)) + 1 at h
  omega

/-- The physical carry-out bit is a comparison result, including equality
and the empty pair word. No Nat/Int comparison is executed by this theorem. -/
theorem carry_order (reverse : Bool) (p : List PairBit) (r : Registers) :
    (result reverse p r).registers.carry=true ↔ decode (rhs reverse p)≤decode (lhs reverse p) := by
  have hv:=result_value reverse p r
  have ho:=decode_bounds (result reverse p r).output
  rw [result_length] at ho
  cases hc:(result reverse p r).registers.carry <;> simp [hc,bit] at hv ⊢ <;> omega

theorem nonnegative_difference (reverse : Bool) (p : List PairBit) (r : Registers)
    (h:(result reverse p r).registers.carry=true) :
    decode (result reverse p r).output=decode (lhs reverse p)-decode (rhs reverse p) := by
  have hv:=result_value reverse p r
  simp [h,bit] at hv
  omega

/-- If the first scan underflows, the same gates in the opposite direction
have a true carry-out. The second pass therefore emits a nonnegative result. -/
theorem reverse_resolves (p : List PairBit) (r s : Registers)
    (h:(result false p r).registers.carry=false) :
    (result true p s).registers.carry=true := by
  have ho:=carry_order false p r
  have hn:decode (leftBits p)<decode (rightBits p) := by
    simp [h,lhs,rhs] at ho
    omega
  apply (carry_order true p s).mpr
  simpa [lhs,rhs] using le_of_lt hn

/-- The final direction flag selects exactly which exponent receives the
nonzero shift; these are decoded equations, not runtime arithmetic. -/
theorem forward_shift (p : List PairBit) (r : Registers)
    (h:(result false p r).registers.carry=true) :
    decode (result false p r).output=decode (leftBits p)-decode (rightBits p) ∧
    decode (rightBits p)≤decode (leftBits p) := by
  exact ⟨by simpa [lhs,rhs] using nonnegative_difference false p r h,
    by simpa [lhs,rhs] using (carry_order false p r).mp h⟩

theorem reverse_shift (p : List PairBit) (r s : Registers)
    (h:(result false p r).registers.carry=false) :
    decode (result true p s).output=decode (rightBits p)-decode (leftBits p) ∧
    decode (leftBits p)<decode (rightBits p) := by
  have hr:=reverse_resolves p r s h
  refine ⟨by simpa [lhs,rhs] using nonnegative_difference true p s hr,?_⟩
  have ho:=carry_order false p r
  simp [h,lhs,rhs] at ho
  omega

end PairedDifferenceArithmetic

#print axioms PairedDifferenceArithmetic.decode_bounds
#print axioms PairedDifferenceArithmetic.decode_complement
#print axioms PairedDifferenceArithmetic.result_length
#print axioms PairedDifferenceArithmetic.result_value
#print axioms PairedDifferenceArithmetic.carry_order
#print axioms PairedDifferenceArithmetic.nonnegative_difference
#print axioms PairedDifferenceArithmetic.reverse_resolves
#print axioms PairedDifferenceArithmetic.forward_shift
#print axioms PairedDifferenceArithmetic.reverse_shift
#check @PairedDifferenceArithmetic.carry_order
