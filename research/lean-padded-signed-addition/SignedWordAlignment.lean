import MarkedZeroPadding

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

Arithmetic/length specification for joining two actually padded bit words to
an equal-width signed adder. Sign extension preserves value, then the existing
adder's two actual sign columns produce an exact wider signed sum. The source
below does NOT implement List.zip, sign-column allocation, or tape transport.
Those operations belong to the separate explicit marked zip/copy controller.
The two sign bits are explicit inputs; their extraction from a selected Cell
encoding is not assumed to have been implemented. No selected table is added.
Author-checked context: kappa=836330098538459/500000000000000000.
UNCOMPILED source candidate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace SignedWordAlignment
open SequentialBitAddition

theorem decode_append (xs ys : List Bool) :
    decode (xs ++ ys) = decode xs + (2 : Int)^xs.length * decode ys := by
  induction xs with
  | nil => simp [decode]
  | cons a xs ih =>
      simp only [List.cons_append, decode, List.length_cons, pow_succ, ih]
      ring

theorem decode_repeat (b : Bool) (d : Nat) :
    decode (List.replicate d b) = bit b * ((2 : Int)^d - 1) := by
  induction d with
  | zero => simp [decode]
  | succ d ih =>
      simp only [List.replicate_succ, decode, ih, pow_succ]
      ring

/-- Appending sign bits changes the represented width without changing value. -/
theorem signed_extension (xs : List Bool) (sign : Bool) (d : Nat) :
    signedValue (xs ++ List.replicate d sign) sign = signedValue xs sign := by
  simp only [signedValue, decode_append, decode_repeat, List.length_append,
    List.length_replicate, pow_add]
  ring

def extendTo (width : Nat) (xs : List Bool) (sign : Bool) : List Bool :=
  xs ++ List.replicate (width - xs.length) sign

theorem extend_length (width : Nat) (xs : List Bool) (sign : Bool)
    (h : xs.length ≤ width) : (extendTo width xs sign).length = width := by
  simp only [extendTo, List.length_append, List.length_replicate]
  omega

theorem extend_value (width : Nat) (xs : List Bool) (sign : Bool) :
    signedValue (extendTo width xs sign) sign = signedValue xs sign :=
  signed_extension xs sign (width - xs.length)

def width (xs ys : List Bool) : Nat := max xs.length ys.length

/-- Unpriced specification for the forthcoming symbol-driven zip controller.
The controller must actually write these rows and its two trailing sign rows. -/
def aligned (xs : List Bool) (sx : Bool) (ys : List Bool) (sy : Bool) : List PairBit :=
  (extendTo (width xs ys) xs sx).zip (extendTo (width xs ys) ys sy)

theorem aligned_left (xs : List Bool) (sx : Bool) (ys : List Bool) (sy : Bool) :
    leftBits (aligned xs sx ys sy) = extendTo (width xs ys) xs sx := by
  have hx := extend_length (width xs ys) xs sx (Nat.le_max_left _ _)
  have hy := extend_length (width xs ys) ys sy (Nat.le_max_right _ _)
  apply List.map_fst_zip
  omega

theorem aligned_right (xs : List Bool) (sx : Bool) (ys : List Bool) (sy : Bool) :
    rightBits (aligned xs sx ys sy) = extendTo (width xs ys) ys sy := by
  have hx := extend_length (width xs ys) xs sx (Nat.le_max_left _ _)
  have hy := extend_length (width xs ys) ys sy (Nat.le_max_right _ _)
  apply List.map_snd_zip
  omega

theorem aligned_length (xs : List Bool) (sx : Bool) (ys : List Bool) (sy : Bool) :
    (aligned xs sx ys sy).length = width xs ys := by
  have h := congrArg List.length (aligned_left xs sx ys sy)
  calc
    (aligned xs sx ys sy).length = (extendTo (width xs ys) xs sx).length := by
      simpa only [leftBits, List.length_map] using h
    _ = width xs ys := extend_length (width xs ys) xs sx (Nat.le_max_left _ _)

/-- Full arithmetic interface, with both physical sign-column bits specified.
No signed-value equality is supplied as a premise. -/
theorem aligned_signed_sum (xs : List Bool) (sx : Bool) (ys : List Bool) (sy : Bool)
    (r : Registers) :
    let p := aligned xs sx ys sy
    let low := scan p (zeroCarry r)
    let lastLow := sumBit sx sy low.registers.carry
    let sign := sumBit sx sy (carryBit sx sy low.registers.carry)
    (signedScan p sx sy r).output = low.output ++ [lastLow, sign] ∧
      signedValue (low.output ++ [lastLow]) sign = signedValue xs sx + signedValue ys sy := by
  simpa only [aligned_left, aligned_right, extend_value] using
    signed_scan_exact (aligned xs sx ys sy) sx sy r

/-- Join the actual padding word formula to the alignment arithmetic. The
padding execution is checked separately; materializing `aligned` is still due. -/
theorem padded_signed_sum (dx : Nat) (xs : List Bool) (sx : Bool)
    (dy : Nat) (ys : List Bool) (sy : Bool) (r : Registers) :
    let p := aligned (MarkedZeroPadding.padded dx xs) sx (MarkedZeroPadding.padded dy ys) sy
    let low := scan p (zeroCarry r)
    let lastLow := sumBit sx sy low.registers.carry
    let sign := sumBit sx sy (carryBit sx sy low.registers.carry)
    (signedScan p sx sy r).output = low.output ++ [lastLow, sign] ∧
      signedValue (low.output ++ [lastLow]) sign =
        (2 : Int)^dx * signedValue xs sx + (2 : Int)^dy * signedValue ys sy := by
  simpa only [MarkedZeroPadding.signed_padding_value] using
    aligned_signed_sum (MarkedZeroPadding.padded dx xs) sx
      (MarkedZeroPadding.padded dy ys) sy r

theorem aligned_output_length (xs : List Bool) (sx : Bool)
    (ys : List Bool) (sy : Bool) (r : Registers) :
    (signedScan (aligned xs sx ys sy) sx sy r).output.length = width xs ys + 2 := by
  rw [signed_scan_storage, aligned_length]

end SignedWordAlignment

#print axioms SignedWordAlignment.signed_extension
#print axioms SignedWordAlignment.extend_length
#print axioms SignedWordAlignment.extend_value
#print axioms SignedWordAlignment.aligned_left
#print axioms SignedWordAlignment.aligned_right
#print axioms SignedWordAlignment.aligned_length
#print axioms SignedWordAlignment.aligned_signed_sum
#print axioms SignedWordAlignment.padded_signed_sum
#print axioms SignedWordAlignment.aligned_output_length
#check @SignedWordAlignment.padded_signed_sum
