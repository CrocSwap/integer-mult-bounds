import RippleCounter

namespace CounterArithmetic
open RippleCounter

/-- Standard nonnegative value of a little-endian fixed-width binary word. -/
def value : List Bool → ℕ
  | [] => 0
  | b::rest => (if b then 1 else 0) + 2 * value rest

/-- Amortized credit is the number of bits that propagate this direction's carry. -/
def potential (d : Bool) : List Bool → ℕ
  | [] => 0
  | b::rest => (if b = d then 1 else 0) + potential d rest

theorem updated_nil (d : Bool) : updated d [] = [] := rfl

theorem updated_carry (d : Bool) (rest : List Bool) :
    updated d (d::rest) = (!d)::updated d rest := by
  simp [updated, carryLength, stopTail, List.replicate_succ]

theorem updated_stop (d b : Bool) (rest : List Bool) (h : b ≠ d) :
    updated d (b::rest) = (!b)::rest := by
  simp [updated, carryLength, stopTail, h]

theorem updated_length (d : Bool) (bits : List Bool) :
    (updated d bits).length = bits.length := by
  induction bits with
  | nil => rfl
  | cons b rest ih =>
    by_cases h : b = d
    · subst b; rw [updated_carry]; simp [ih]
    · rw [updated_stop d b rest h]; rfl

theorem carryLength_le_length (d : Bool) (bits : List Bool) :
    carryLength d bits ≤ bits.length := by
  induction bits with
  | nil => rfl
  | cons b rest ih =>
    simp only [carryLength, List.length_cons]
    split_ifs <;> omega

theorem potential_le_length (d : Bool) (bits : List Bool) :
    potential d bits ≤ bits.length := by
  induction bits with
  | nil => rfl
  | cons b rest ih =>
    simp only [potential, List.length_cons]
    split_ifs <;> omega

/-- A successful operation replaces k carry bits by k non-carry bits and creates
one carry bit; overflow only deletes carry bits. This includes width zero. -/
theorem potential_accounting (d : Bool) (bits : List Bool) :
    carryLength d bits + potential d (updated d bits) ≤ potential d bits + 1 := by
  induction bits with
  | nil => simp [carryLength, potential, updated_nil]
  | cons b rest ih =>
    by_cases h : b = d
    · subst b
      rw [updated_carry]
      have hne : (!d) ≠ d := by cases d <;> decide
      simp only [carryLength, potential, if_pos, if_neg hne]
      omega
    · rw [updated_stop d b rest h]
      have heq : (!b) = d := by cases b <;> cases d <;> simp_all
      simp [carryLength, potential, h, heq, Nat.add_comm]

theorem amortized_step (d : Bool) (bits : List Bool) :
    steps d bits + 2 * potential d (updated d bits) ≤ 4 + 2 * potential d bits := by
  have h := potential_accounting d bits
  unfold steps
  omega

def iterate (d : Bool) : ℕ → List Bool → List Bool
  | 0, bits => bits
  | n+1, bits => iterate d n (updated d bits)

theorem iterate_length (d : Bool) (n : ℕ) (bits : List Bool) :
    (iterate d n bits).length = bits.length := by
  induction n generalizing bits with
  | zero => rfl
  | succ n ih => rw [iterate, ih, updated_length]

def totalSteps (d : Bool) : ℕ → List Bool → ℕ
  | 0, _ => 0
  | n+1, bits => steps d bits + totalSteps d n (updated d bits)

theorem amortized_total (d : Bool) (n : ℕ) (bits : List Bool) :
    totalSteps d n bits + 2 * potential d (iterate d n bits) ≤ 4*n + 2 * potential d bits := by
  induction n generalizing bits with
  | zero => simp [totalSteps, iterate]
  | succ n ih =>
    have h := amortized_step d bits
    have hn := ih (updated d bits)
    simp only [totalSteps, iterate]
    omega

/-- Total literal head-local counting transitions, including every head return.
Arbitrary starting words are permitted; their initial potential is charged by w. -/
theorem total_steps_bound (d : Bool) (n : ℕ) (bits : List Bool) :
    totalSteps d n bits ≤ 4*n + 2*bits.length := by
  have h := amortized_total d n bits
  have hp := potential_le_length d bits
  omega

theorem value_bound (bits : List Bool) : value bits < 2 ^ bits.length := by
  induction bits with
  | nil => simp [value]
  | cons b rest ih =>
    cases b <;> simp only [value, Bool.false_eq_true, ↓reduceIte, List.length_cons, pow_succ] <;>
      omega

/-- Exact modular increment equation; no infinite-precision counter is assumed. -/
theorem increment_value (bits : List Bool) :
    value (updated true bits) + (if overflow true bits then 2^bits.length else 0) = value bits + 1 := by
  induction bits with
  | nil => simp [updated_nil, value, overflow]
  | cons b rest ih =>
    cases b with
    | false => simp [updated_stop, value, overflow, Nat.add_comm]
    | true =>
      rw [updated_carry]
      simp only [value, Bool.not_true, Bool.false_eq_true, ↓reduceIte, overflow,
        List.length_cons, pow_succ] at *
      cases ho : overflow true rest <;> simp [ho] at ih ⊢ <;> omega

/-- Exact modular decrement equation. Underflow returns all ones and raises
its flag; clients reset from the local template before the next block. -/
theorem decrement_value (bits : List Bool) :
    value bits + (if overflow false bits then 2^bits.length else 0) = value (updated false bits) + 1 := by
  induction bits with
  | nil => simp [updated_nil, value, overflow]
  | cons b rest ih =>
    cases b with
    | false =>
      rw [updated_carry]
      simp only [value, Bool.not_false, Bool.false_eq_true, ↓reduceIte, overflow,
        List.length_cons, pow_succ] at *
      cases ho : overflow false rest <;> simp [ho] at ih ⊢ <;> omega
    | true => simp [updated_stop, value, overflow, Nat.add_comm]

/-- Underflow detects exactly zero in the INPUT counter, without a separate scan. -/
theorem decrement_underflow_iff_zero (bits : List Bool) :
    overflow false bits = true ↔ value bits = 0 := by
  induction bits with
  | nil => simp [overflow, value]
  | cons b rest ih =>
    cases b <;> simp [overflow, value, ih]

theorem overflow_updated (d : Bool) (bits : List Bool) (h : overflow d bits = true) :
    updated d bits = List.replicate bits.length (!d) := by
  induction bits with
  | nil => rfl
  | cons b rest ih =>
    by_cases hb : b = d
    · subst b
      rw [updated_carry]
      simp only [overflow, if_pos] at h
      rw [ih h, List.length_cons, List.replicate_succ]
    · simp [overflow, hb] at h

theorem zero_replicate_value (n : ℕ) : value (List.replicate n false) = 0 := by
  induction n with
  | zero => rfl
  | succ n ih => simp [List.replicate_succ, value, ih]

theorem increment_overflow_iff_max (bits : List Bool) :
    overflow true bits = true ↔ value bits + 1 = 2^bits.length := by
  have heq := increment_value bits
  constructor
  · intro h
    rw [overflow_updated true bits h] at heq
    simpa [h, zero_replicate_value] using heq.symm
  · intro h
    cases ho : overflow true bits
    · have hb := value_bound (updated true bits)
      rw [updated_length] at hb
      simp [ho] at heq
      omega
    · rfl

/-- Every decrement before zero reduces the represented value by exactly one. -/
theorem decrement_positive (bits : List Bool) (h : 0 < value bits) :
    overflow false bits = false ∧ value (updated false bits) + 1 = value bits := by
  have hn : overflow false bits ≠ true := by
    intro hflag
    have := (decrement_underflow_iff_zero bits).mp hflag
    omega
  have hf : overflow false bits = false := by cases hflag : overflow false bits <;> simp_all
  refine ⟨hf, ?_⟩
  have hv := decrement_value bits
  simpa [hf] using hv.symm

theorem countdown_value (bits : List Bool) (n : ℕ) (hn : n ≤ value bits) :
    value (iterate false n bits) = value bits - n := by
  induction n generalizing bits with
  | zero => simp [iterate]
  | succ n ih =>
    have hp : 0 < value bits := by omega
    have hv := (decrement_positive bits hp).2
    have hnext : n ≤ value (updated false bits) := by omega
    rw [iterate, ih (updated false bits) hnext]
    omega

theorem countdown_not_finished (bits : List Bool) (n : ℕ) (hn : n < value bits) :
    overflow false (iterate false n bits) = false := by
  have hv := countdown_value bits n (Nat.le_of_lt hn)
  apply (decrement_positive (iterate false n bits) (by omega)).1

/-- Starting with B-1, the B-th post-emission decrement detects the end of
exactly B payload positions. No comparison against the whole descriptor occurs. -/
theorem countdown_final_underflow (bits : List Bool) :
    overflow false (iterate false (value bits) bits) = true := by
  apply (decrement_underflow_iff_zero _).mpr
  rw [countdown_value bits (value bits) (Nat.le_refl _)]
  omega

/-- When the locally stored width w is at most block length B, counting B
payload positions including the terminal borrow costs at most 6B transitions. -/
theorem complete_block_cost (bits : List Bool) (hw : bits.length ≤ value bits + 1) :
    totalSteps false (value bits + 1) bits ≤ 6 * (value bits + 1) := by
  have h := total_steps_bound false (value bits + 1) bits
  omega

end CounterArithmetic

#print axioms CounterArithmetic.updated_nil
#print axioms CounterArithmetic.updated_carry
#print axioms CounterArithmetic.updated_stop
#print axioms CounterArithmetic.updated_length
#print axioms CounterArithmetic.carryLength_le_length
#print axioms CounterArithmetic.potential_le_length
#print axioms CounterArithmetic.potential_accounting
#print axioms CounterArithmetic.amortized_step
#print axioms CounterArithmetic.iterate_length
#print axioms CounterArithmetic.amortized_total
#print axioms CounterArithmetic.total_steps_bound
#print axioms CounterArithmetic.value_bound
#print axioms CounterArithmetic.increment_value
#print axioms CounterArithmetic.decrement_value
#print axioms CounterArithmetic.decrement_underflow_iff_zero
#print axioms CounterArithmetic.overflow_updated
#print axioms CounterArithmetic.zero_replicate_value
#print axioms CounterArithmetic.increment_overflow_iff_max
#print axioms CounterArithmetic.decrement_positive
#print axioms CounterArithmetic.countdown_value
#print axioms CounterArithmetic.countdown_not_finished
#print axioms CounterArithmetic.countdown_final_underflow
#print axioms CounterArithmetic.complete_block_cost
