import CarryTape

namespace CurrentMain.CarryTape

/-- Logical overflow is specified separately; the four-state incrementer does
not retain an overflow flag after rewinding. -/
def overflow : List Bool → Bool
  | [] => true
  | false :: _ => false
  | true :: bits => overflow bits

def value : List Bool → Nat
  | [] => 0
  | b :: bits => (if b then 1 else 0) + 2 * value bits

theorem value_bound (bits : List Bool) : value bits < 2 ^ bits.length := by
  induction bits with
  | nil => decide
  | cons b bits ih => cases b <;> simp [value, Nat.pow_succ] <;> omega

theorem increment_value (bits : List Bool) :
    value (increment bits) + (if overflow bits then 2 ^ bits.length else 0) = value bits + 1 := by
  induction bits with
  | nil => rfl
  | cons b bits ih =>
    cases b with
    | false => simp [increment, overflow, value]; omega
    | true =>
      cases h : overflow bits <;>
        simp [increment, overflow, value, h, Nat.pow_succ] at ih ⊢ <;> omega

theorem increment_mod (bits : List Bool) :
    value (increment bits) = (value bits + 1) % 2 ^ bits.length := by
  have hi := increment_value bits
  have hx := value_bound bits
  have hy := value_bound (increment bits)
  rw [increment_length] at hy
  cases h : overflow bits with
  | false =>
    simp only [h, Bool.false_eq_true, if_false, Nat.add_zero] at hi
    rw [← hi, Nat.mod_eq_of_lt hy]
  | true =>
    simp only [h, if_true] at hi
    have hz : value (increment bits) = 0 := by omega
    have hp : value bits + 1 = 2 ^ bits.length := by omega
    rw [hz, hp, Nat.mod_self]

/-- Proven physical primitive receipt, including both endpoint-marker reads. -/
def incrementReceipt (bits : List Bool) : Receipt :=
  ⟨2 * trailingOnes bits + 4, bitWrites bits, 2 * trailingOnes bits + 2⟩

/-- Specification of repeated, head-restored physical increments.
The Nat loop is an iteration proof device; control and client costs are not
claimed to have been compiled to tape by this definition. -/
def pass : Nat → List Bool → List Bool × Receipt
  | 0, bits => (bits, Receipt.zero)
  | k + 1, bits =>
    let tail := pass k (increment bits)
    (tail.1, (incrementReceipt bits).add tail.2)

theorem pass_length (k : Nat) (bits : List Bool) : (pass k bits).1.length = bits.length := by
  induction k generalizing bits with
  | zero => rfl
  | succ k ih => simp only [pass, ih, increment_length]

theorem pass_value (k : Nat) (bits : List Bool) :
    value (pass k bits).1 = (value bits + k) % 2 ^ bits.length := by
  induction k generalizing bits with
  | zero => simp [pass, Nat.mod_eq_of_lt (value_bound bits)]
  | succ k ih =>
    simp only [pass, ih, increment_length, increment_mod, Nat.mod_add_mod]
    congr 1
    omega

/-- Two actual low-bit increments advance the tail once. This is the
amortization bridge; no list of all addresses is built. -/
theorem pass_even (k : Nat) (bits : List Bool) :
    pass (2 * k) (false :: bits) =
      (false :: (pass k bits).1,
        ⟨(pass k bits).2.reads + 6 * k,
          (pass k bits).2.writes + 2 * k,
          (pass k bits).2.moves + 4 * k⟩) := by
  induction k generalizing bits with
  | zero => rfl
  | succ k ih =>
    have he : 2 * (k + 1) = (2 * k + 1) + 1 := by omega
    rw [he]
    simp only [pass, increment]
    rw [ih]
    simp only [incrementReceipt, trailingOnes, bitWrites, Receipt.add]
    congr 2 <;> omega

theorem empty_pass_one : pass 1 [] = ([], ⟨4, 0, 2⟩) := rfl

/-- Exact all-width index-tape traffic for the full modular pass. This includes
all carry and rewind head movement, but excludes zero initialization, coefficient
evaluation, data-tape/client work and loop-control lowering. -/
theorem complete_pass (n : Nat) :
    pass (2 ^ n) (List.replicate n false) =
      (List.replicate n false,
        ⟨6 * 2 ^ n - 2, 2 * 2 ^ n - 2, 4 * 2 ^ n - 2⟩) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    have hp : 1 ≤ 2 ^ n := Nat.one_le_pow n 2 (by decide)
    rw [Nat.pow_succ, Nat.mul_comm (2 ^ n) 2, List.replicate_succ, pass_even, ih]
    dsimp only
    congr 2 <;> omega

/-- Every primitive used by the pass is bound to the finite-alphabet machine,
not merely assigned the receipt of a desired endpoint. -/
theorem incrementReceipt_realized (bits : List Bool) :
    run (incrementReceipt bits).reads (homeTape bits .enter) =
      (homeTape (increment bits) .halt, incrementReceipt bits) := increment_execution bits

/-- A physical call and its returned head-restored state have exactly the same
logical effect as one step of the repeated-increment specification. -/
theorem pass_successor_realized (k : Nat) (bits : List Bool) :
    let first := run (incrementReceipt bits).reads (homeTape bits .enter)
    let tail := pass k (increment bits)
    first.1 = homeTape (increment bits) .halt ∧
      pass (k + 1) bits = (tail.1, first.2.add tail.2) := by
  simp only [incrementReceipt_realized, pass]
  trivial

theorem full_pass24_index_traffic :
    (pass (2 ^ 24) (List.replicate 24 false)).2 =
      ⟨100663294, 33554430, 67108862⟩ := by
  rw [complete_pass]

end CurrentMain.CarryTape

#print axioms CurrentMain.CarryTape.value_bound
#print axioms CurrentMain.CarryTape.increment_value
#print axioms CurrentMain.CarryTape.increment_mod
#print axioms CurrentMain.CarryTape.pass_length
#print axioms CurrentMain.CarryTape.pass_value
#print axioms CurrentMain.CarryTape.pass_even
#print axioms CurrentMain.CarryTape.empty_pass_one
#print axioms CurrentMain.CarryTape.complete_pass
#print axioms CurrentMain.CarryTape.incrementReceipt_realized
#print axioms CurrentMain.CarryTape.pass_successor_realized
#print axioms CurrentMain.CarryTape.full_pass24_index_traffic
