import BinaryCounterCompactCopy

/-! Numeric normalization for the accepted physical compact-copy routine.
This adapter reuses the marked-counter value binding, its strict binary bound,
and the installed log2 characterization. Zero is represented by the empty list;
no zero-digit caller convention or six-tape sequencing is asserted here. -/
namespace CurrentMain.BinaryCounterCompactValue
open FixedTapeMachine BinaryCounterCompactCopy
set_option Elab.async false

/-- The concrete little-endian snoc identity needed for high-zero deletion. -/
private theorem value_snoc (xs : List Bool) (b : Bool) :
    CarryTape.value (xs++[b]) =
      CarryTape.value xs + (if b then 2^xs.length else 0) := by
  induction xs with
  | nil => cases b <;> rfl
  | cons a xs ih =>
    simp only [List.cons_append,CarryTape.value,ih,List.length_cons,Nat.pow_succ]
    cases a <;> cases b <;>
      simp only [Bool.false_eq_true,if_false,if_true,Nat.add_zero,Nat.zero_add,
        Nat.mul_zero,Nat.mul_add] <;> omega

private theorem drop_reverse_value (xs : List Bool) :
    CarryTape.value (dropHighZeros xs).reverse = CarryTape.value xs.reverse := by
  induction xs with
  | nil => rfl
  | cons b xs ih =>
    cases b with
    | false =>
      simpa only [dropHighZeros,List.reverse_cons,value_snoc,Bool.false_eq_true,
        if_false,Nat.add_zero] using ih
    | true => rfl

private theorem drop_head (xs : List Bool) :
    dropHighZeros xs=[] ∨ ∃ rest, dropHighZeros xs=true::rest := by
  induction xs with
  | nil => exact Or.inl rfl
  | cons b xs ih =>
    cases b with
    | false => exact ih
    | true => exact Or.inr ⟨xs,rfl⟩

private theorem compact_shape (bits : List Bool) :
    compact bits=[] ∨ ∃ q, compact bits=q++[true] := by
  rcases drop_head bits.reverse with h|⟨rest,h⟩
  · exact Or.inl (by simp only [compact,h,List.reverse_nil])
  · exact Or.inr ⟨rest.reverse,by simp only [compact,h,List.reverse_cons]⟩

private theorem true_snoc_bounds (q : List Bool) :
    2^q.length ≤ wordValue (q++[true]) ∧
      wordValue (q++[true]) < 2^(q.length+1) := by
  have low : 2^q.length ≤ CarryTape.value (q++[true]) := by
    rw [value_snoc]
    simp only [if_true]
    omega
  have high := CarryTape.value_bound (q++[true])
  rw [BinaryCarryIncrement.value_binding] at low high
  refine ⟨low,?_⟩
  simpa only [List.length_append,List.length_cons,List.length_nil,Nat.zero_add] using high

/-- The physical routine's compact list represents the same natural number. -/
theorem compact_value (bits : List Bool) : wordValue (compact bits)=wordValue bits := by
  have h := drop_reverse_value bits.reverse
  simpa only [compact,List.reverse_reverse,BinaryCarryIncrement.value_binding] using h

/-- The empty-list zero convention is explicit. -/
theorem compact_eq_nil_iff (bits : List Bool) : compact bits=[] ↔ wordValue bits=0 := by
  constructor
  · intro h
    rw [← compact_value bits,h]
    rfl
  · intro hz
    rcases compact_shape bits with h|⟨q,h⟩
    · exact h
    · have low := (true_snoc_bounds q).1
      have pos : 0 < 2^q.length := Nat.two_pow_pos q.length
      rw [← h,compact_value bits,hz] at low
      omega

theorem compact_length_zero (bits : List Bool) (h : wordValue bits=0) :
    (compact bits).length=0 := by
  rw [(compact_eq_nil_iff bits).2 h]
  rfl

/-- For positive values the canonical length is exactly one plus log2. -/
theorem compact_length_positive (bits : List Bool) (h : wordValue bits≠0) :
    (compact bits).length=(wordValue bits).log2+1 := by
  rcases compact_shape bits with hz|⟨q,hq⟩
  · exact False.elim (h ((compact_eq_nil_iff bits).1 hz))
  · have bounds := true_snoc_bounds q
    rw [← hq,compact_value bits] at bounds
    have lo : q.length ≤ (wordValue bits).log2 := (Nat.le_log2 h).2 bounds.1
    have hi : (wordValue bits).log2 < q.length+1 := (Nat.log2_lt h).2 bounds.2
    rw [hq,List.length_append]
    simp only [List.length_cons,List.length_nil,Nat.zero_add]
    omega

/-- Zero uses no digits; every nonzero value uses its exact binary length. -/
theorem compact_length (bits : List Bool) :
    (compact bits).length = if wordValue bits=0 then 0 else (wordValue bits).log2+1 := by
  split
  · exact compact_length_zero bits ‹_›
  · exact compact_length_positive bits ‹_›

/-- The already accepted physical endpoint now carries its numeric specification. -/
theorem normalized_run (bits : List Bool) :
    run machine (elapsed bits) (initialConfiguration bits)=finalConfiguration bits ∧
    wordValue (compact bits)=wordValue bits ∧
    (compact bits).length=(if wordValue bits=0 then 0 else (wordValue bits).log2+1) :=
  ⟨compact_run_exact bits,compact_value bits,compact_length bits⟩

end CurrentMain.BinaryCounterCompactValue
#print axioms CurrentMain.BinaryCounterCompactValue.compact_value
#print axioms CurrentMain.BinaryCounterCompactValue.compact_eq_nil_iff
#print axioms CurrentMain.BinaryCounterCompactValue.compact_length_zero
#print axioms CurrentMain.BinaryCounterCompactValue.compact_length_positive
#print axioms CurrentMain.BinaryCounterCompactValue.compact_length
#print axioms CurrentMain.BinaryCounterCompactValue.normalized_run
