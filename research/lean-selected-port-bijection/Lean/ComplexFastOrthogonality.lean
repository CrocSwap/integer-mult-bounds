import ComplexBinarySpan
namespace CurrentMain.BinaryFrame

local instance : Std.Associative (fun a b : Bool => a ^^ b) := ⟨Bool.xor_assoc⟩
local instance : Std.Commutative (fun a b : Bool => a ^^ b) := ⟨Bool.xor_comm⟩

def dotMask : Nat → Nat → Nat → Bool
  | 0, _, _ => false
  | h+1, a, b => dotMask h a b ^^ (a.testBit h && b.testBit h)

def xorFold (n shift : Nat) : Nat := n ^^^ (n >>> shift)

/-- Only the lower 22 coordinates contribute; padding bits are explicitly masked. -/
def dot22 (a b : Nat) : Bool :=
  (xorFold (xorFold (xorFold (xorFold (xorFold
    ((a &&& b) &&& (2^22-1)) 16) 8) 4) 2) 1).testBit 0

theorem dot22_eq (a b : Nat) : dot22 a b = dotMask 22 a b := by
  simp only [dot22, xorFold, dotMask, Nat.testBit_shiftRight, Nat.testBit_xor,
    Nat.testBit_and, Nat.testBit_two_pow_sub_one]
  simp only [Nat.reduceAdd, Nat.reduceLT, decide_true, decide_false,
    Bool.and_true, Bool.and_false, Bool.true_and, Bool.false_and,
    Bool.false_xor, Bool.xor_false]
  ac_rfl

theorem dotMask_zero (h a : Nat) : dotMask h a 0 = false := by
  induction h with
  | zero => rfl
  | succ h ih => simp [dotMask, ih]

theorem dotMask_comm (h a b : Nat) : dotMask h a b = dotMask h b a := by
  induction h with
  | zero => rfl
  | succ h ih => simp [dotMask, ih, Bool.and_comm]

theorem dotMask_xor_left (h a b c : Nat) :
    dotMask h (a ^^^ b) c = (dotMask h a c ^^ dotMask h b c) := by
  induction h with
  | zero => rfl
  | succ h ih =>
    simp [dotMask, ih, Nat.testBit_xor, Bool.and_xor_distrib_right,
      Bool.xor_assoc, Bool.xor_left_comm, Bool.xor_comm]

theorem dotMask_xor_right (h a b c : Nat) :
    dotMask h a (b ^^^ c) = (dotMask h a b ^^ dotMask h a c) := by
  rw [dotMask_comm h a (b ^^^ c), dotMask_xor_left,
    dotMask_comm h b a, dotMask_comm h c a]

def orthogonalCheck (h : Nat) (B A : List Nat) : Bool :=
  B.all (fun b => A.all (fun a => !(dotMask h b a)))

def orthogonal22 (B A : List Nat) : Bool :=
  B.all (fun b => A.all (fun a => !(dot22 b a)))

theorem orthogonal22_sound (B A : List Nat) (checked : orthogonal22 B A = true) :
    orthogonalCheck 22 B A = true := by
  simpa only [orthogonal22, orthogonalCheck, dot22_eq] using checked

theorem orthogonalCheck_sound (h : Nat) (B A : List Nat)
    (checked : orthogonalCheck h B A = true) :
    ∀ b ∈ B, ∀ a ∈ A, dotMask h b a = false := by
  intro b hb a ha
  simpa using List.all_eq_true.mp (List.all_eq_true.mp checked b hb) a ha

end CurrentMain.BinaryFrame
#print axioms CurrentMain.BinaryFrame.dot22_eq
#print axioms CurrentMain.BinaryFrame.dotMask_zero
#print axioms CurrentMain.BinaryFrame.dotMask_comm
#print axioms CurrentMain.BinaryFrame.dotMask_xor_left
#print axioms CurrentMain.BinaryFrame.dotMask_xor_right
#print axioms CurrentMain.BinaryFrame.orthogonal22_sound
#print axioms CurrentMain.BinaryFrame.orthogonalCheck_sound
