import CliffordNineBitDecoder

/-!
Source-ordered nine-bit addresses for the pinned current535 Clifford interpreter.
Packed bit i has weight 2^i, exactly as mv/qvalue and the source vector indices.
The inverse is explicit little-endian bit assembly, not a cardinality choice.
This root supplies coordinates and payload reindexing only. It does not identify
packed matrix/parity, phases, dyadic arithmetic or expanded physical execution.
Apache-2.0; prepared with OpenAI assistance. See SOURCE_SCOPE.json.
-/
set_option Elab.async false
namespace CurrentMain.Current535PackedCoordinates
open CliffordNineBitDecoder (Bit Address mask)
open CliffordMonomialDecoder (push)

abbrev Packed := Fin 512

def unpack (x : Packed) : Address := mask x.val

private def packBits (x : Address) : BitVec 9 :=
  (BitVec.ofBoolListLE (List.ofFn (fun i : Fin 9 => decide (x i = 1)))).cast
    (by simp only [List.length_ofFn])

def pack (x : Address) : Packed := (packBits x).toFin

private theorem packBits_getLsb (x : Address) (i : Fin 9) :
    (packBits x).getLsbD i.val = decide (x i = 1) := by
  unfold packBits
  rw [BitVec.getLsbD_cast, BitVec.getLsbD_ofBoolListLE]
  simp only [List.getD_eq_getElem?_getD, List.getElem?_ofFn,
    dif_pos i.isLt, Option.getD_some]

private theorem bit_cases (x : Bit) : x = 0 ∨ x = 1 := by
  have hx := ZMod.val_lt x
  have hv : x.val = 0 ∨ x.val = 1 := by omega
  rcases hv with h | h
  · left
    apply ZMod.val_injective 2
    simpa using h
  · right
    apply ZMod.val_injective 2
    simpa using h

/-- Exact little-endian packed bit formula. -/
theorem unpack_apply (x : Packed) (i : Fin 9) :
    unpack x i = if x.val.testBit i.val then 1 else 0 := rfl

theorem pack_bit_order (x : Address) (i : Fin 9) :
    (pack x).val.testBit i.val = decide (x i = 1) :=
  packBits_getLsb x i

theorem unpack_pack (x : Address) : unpack (pack x) = x := by
  funext i
  rw [unpack_apply, pack_bit_order]
  rcases bit_cases (x i) with h | h <;> simp [h]

theorem pack_unpack (x : Packed) : pack (unpack x) = x := by
  have hb : packBits (unpack x) = BitVec.ofFin (w := 9) x := by
    apply BitVec.eq_of_getLsbD_eq
    intro i hi
    rw [packBits_getLsb (unpack x) ⟨i, hi⟩]
    change decide ((if x.val.testBit i then (1 : Bit) else 0) = 1) = x.val.testBit i
    cases hx : x.val.testBit i <;> decide +kernel
  exact congrArg BitVec.toFin hb

def addressEquiv : Packed ≃ Address where
  toFun := unpack
  invFun := pack
  left_inv := pack_unpack
  right_inv := unpack_pack

/-- Fixed-width XOR agrees with the source x xor mask operation on nine bits. -/
def packedXor (x y : Packed) : Packed :=
  ((BitVec.ofFin (w := 9) x) ^^^ (BitVec.ofFin (w := 9) y)).toFin

theorem unpack_xor (x y : Packed) :
    unpack (packedXor x y) = unpack x + unpack y := by
  funext i
  change (if ((BitVec.ofFin (w := 9) x) ^^^ (BitVec.ofFin (w := 9) y)).getLsbD i.val then (1 : Bit) else 0) =
    (if (BitVec.ofFin (w := 9) x).getLsbD i.val then (1 : Bit) else 0) +
    (if (BitVec.ofFin (w := 9) y).getLsbD i.val then (1 : Bit) else 0)
  rw [BitVec.getLsbD_xor]
  cases hx : (BitVec.ofFin (w := 9) x).getLsbD i.val <;>
    cases hy : (BitVec.ofFin (w := 9) y).getLsbD i.val <;> decide +kernel

theorem unpack_one : unpack 1 = mask 1 := rfl

noncomputable section

/-- Packed payloads are pulled back along the explicit inverse address map. -/
def payloadEquiv : (Packed → ℂ) ≃ₗ[ℂ] (Address → ℂ) :=
  LinearEquiv.funCongrLeft ℂ ℂ addressEquiv.symm

theorem payload_apply (v : Packed → ℂ) (a : Address) :
    payloadEquiv v a = v (pack a) := rfl

theorem payload_symm_apply (v : Address → ℂ) (x : Packed) :
    payloadEquiv.symm v x = v (unpack x) := rfl

/-- A certified packed permutation changes address representation by conjugation. -/
def liftPermutation (p : Packed ≃ Packed) : Address ≃ Address :=
  (addressEquiv.symm.trans p).trans addressEquiv

/-- Source P scatters input x to p(x); its read formula uses p inverse. -/
theorem scatter_apply_at (p : Packed ≃ Packed) (v : Packed → ℂ) (x : Packed) :
    push (K := ℂ) p v (p x) = v x := by
  rw [CliffordMonomialDecoder.push_apply, Equiv.symm_apply_apply]

/-- Reuse the accepted push operator; no source matrix correctness is assumed. -/
theorem scatter_reindex (p : Packed ≃ Packed) (v : Packed → ℂ) :
    payloadEquiv (push (K := ℂ) p v) =
      push (K := ℂ) (liftPermutation p) (payloadEquiv v) := by
  funext a
  change v (p.symm (pack a)) = v (pack (unpack (p.symm (pack a))))
  rw [pack_unpack]

end
end CurrentMain.Current535PackedCoordinates

#print axioms CurrentMain.Current535PackedCoordinates.unpack_apply
#print axioms CurrentMain.Current535PackedCoordinates.pack_bit_order
#print axioms CurrentMain.Current535PackedCoordinates.unpack_pack
#print axioms CurrentMain.Current535PackedCoordinates.pack_unpack
#print axioms CurrentMain.Current535PackedCoordinates.unpack_xor
#print axioms CurrentMain.Current535PackedCoordinates.unpack_one
#print axioms CurrentMain.Current535PackedCoordinates.payload_apply
#print axioms CurrentMain.Current535PackedCoordinates.payload_symm_apply
#print axioms CurrentMain.Current535PackedCoordinates.scatter_apply_at
#print axioms CurrentMain.Current535PackedCoordinates.scatter_reindex
