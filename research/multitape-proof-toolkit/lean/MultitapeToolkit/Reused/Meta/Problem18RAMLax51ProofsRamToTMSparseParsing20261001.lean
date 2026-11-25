import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMWordOperations20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

def SparseSymbol.bitValue : SparseSymbol → Bool
  | .bit b => b
  | _ => false

@[simp] theorem SparseSymbol.bitValue_bit (b : Bool) :
    (SparseSymbol.bit b).bitValue = b := rfl

/-- Decode one fixed-width word and return the unconsumed suffix.  On the
well-formed encodings used by the interpreter the symbol after the bits is
`wordEnd`; malformed tapes are deliberately totalized by simply dropping it. -/
def decodeFixedWord (w : ℕ) (tape : List SparseSymbol) : ℕ × List SparseSymbol :=
  (bitsValue ((tape.take w).map SparseSymbol.bitValue), tape.drop (w + 1))

theorem decodeFixedWord_encode (w n : ℕ) (suffix : List SparseSymbol) :
    decodeFixedWord w (encodeFixedWord w n ++ suffix) =
      (n % 2 ^ w, suffix) := by
  unfold decodeFixedWord encodeFixedWord
  apply Prod.ext
  · rw [List.append_assoc, List.take_append_of_le_length (by simp)]
    rw [(List.take_eq_self_iff _).2 (by simp)]
    rw [List.map_map]
    have hfun : SparseSymbol.bitValue ∘ SparseSymbol.bit = id := by
      funext b
      cases b <;> rfl
    rw [hfun, List.map_id]
    exact bitsValue_fixedBits w n
  · simp [List.drop_append, fixedBits_length]

/-- Decode a known number of consecutive fixed-width words. -/
def decodeWordList : ℕ → ℕ → List SparseSymbol → List ℕ × List SparseSymbol
  | _, 0, tape => ([], tape)
  | w, count + 1, tape =>
      let head := decodeFixedWord w tape
      let tail := decodeWordList w count head.2
      (head.1 :: tail.1, tail.2)

theorem decodeWordList_encode (w : ℕ) (xs : List ℕ)
    (hfit : ∀ x ∈ xs, x < 2 ^ w) (suffix : List SparseSymbol) :
    decodeWordList w xs.length (encodeWordList w xs ++ suffix) = (xs, suffix) := by
  induction xs with
  | nil => simp [decodeWordList, encodeWordList]
  | cons x xs ih =>
      have hx : x < 2 ^ w := hfit x (by simp)
      have hxs : ∀ y ∈ xs, y < 2 ^ w := by
        intro y hy
        exact hfit y (by simp [hy])
      simp only [List.length_cons, encodeWordList, List.flatMap_cons,
        decodeWordList]
      have hhead := decodeFixedWord_encode w x (encodeWordList w xs ++ suffix)
      rw [show encodeFixedWord w x ++ List.flatMap (encodeFixedWord w) xs ++ suffix =
          encodeFixedWord w x ++ (encodeWordList w xs ++ suffix) by
        simp [encodeWordList, List.append_assoc]]
      rw [hhead, Nat.mod_eq_of_lt hx, ih hxs]

def decodeSparseCell (w : ℕ) (tape : List SparseSymbol) :
    (ℕ × ℕ) × List SparseSymbol :=
  let address := decodeFixedWord w tape
  let value := decodeFixedWord w address.2
  ((address.1, value.1), value.2.tail)

theorem decodeSparseCell_encode (w : ℕ) (cell : ℕ × ℕ)
    (suffix : List SparseSymbol) :
    decodeSparseCell w (encodeSparseCell w cell ++ suffix) =
      ((cell.1 % 2 ^ w, cell.2 % 2 ^ w), suffix) := by
  rcases cell with ⟨a, v⟩
  simp [decodeSparseCell, encodeSparseCell, decodeFixedWord_encode,
    List.append_assoc]

/-- Decode a known number of sparse cells.  The actual interpreter discovers
that number by scanning for `memoryEnd`; this counted form is the induction
principle used in its correctness proof. -/
def decodeSparseMemory : ℕ → ℕ → List SparseSymbol →
    SparseMemory × List SparseSymbol
  | _, 0, tape => ([], tape)
  | w, count + 1, tape =>
      let head := decodeSparseCell w tape
      let tail := decodeSparseMemory w count head.2
      (head.1 :: tail.1, tail.2)

def normalizeSparseMemory (w : ℕ) (m : SparseMemory) : SparseMemory :=
  m.map fun cell => (cell.1 % 2 ^ w, cell.2 % 2 ^ w)

theorem decodeSparseMemory_encode (w : ℕ) (m : SparseMemory)
    (suffix : List SparseSymbol) :
    decodeSparseMemory w m.length (encodeSparseMemory w m ++ suffix) =
      (normalizeSparseMemory w m, suffix) := by
  induction m with
  | nil => simp [decodeSparseMemory, encodeSparseMemory, normalizeSparseMemory]
  | cons cell m ih =>
      simp only [List.length_cons, encodeSparseMemory, List.flatMap_cons,
        decodeSparseMemory, normalizeSparseMemory, List.map_cons]
      have hhead := decodeSparseCell_encode w cell (encodeSparseMemory w m ++ suffix)
      rw [show encodeSparseCell w cell ++ List.flatMap (encodeSparseCell w) m ++ suffix =
          encodeSparseCell w cell ++ (encodeSparseMemory w m ++ suffix) by
        simp [encodeSparseMemory, List.append_assoc]]
      rw [hhead, ih]
      simp [normalizeSparseMemory]

@[simp] theorem drop_one_cons {α : Type} (a : α) (xs : List α) :
    (a :: xs).drop 1 = xs := rfl

def consumeMarker : List SparseSymbol → List SparseSymbol
  | [] => []
  | _ :: xs => xs

@[simp] theorem consumeMarker_cons (a : SparseSymbol) (xs : List SparseSymbol) :
    consumeMarker (a :: xs) = xs := rfl

/-- Counted state decoder.  The program counter is represented in the finite
control of the interpreter, so it is supplied separately.  Section markers
are consumed between the variable-length components. -/
def decodeSparseState (w pc memCount inpCount outCount : ℕ)
    (tape : List SparseSymbol) : SparseState × List SparseSymbol :=
  let acc := decodeFixedWord w tape
  let mem := decodeSparseMemory w memCount acc.2
  let inp := decodeWordList w inpCount (consumeMarker mem.2)
  let out := decodeWordList w outCount (consumeMarker inp.2)
  ({ pc := pc, acc := acc.1, mem := mem.1, inp := inp.1, out := out.1 },
    out.2.tail)

def normalizeSparseState (w : ℕ) (s : SparseState) : SparseState where
  pc := s.pc
  acc := s.acc % 2 ^ w
  mem := normalizeSparseMemory w s.mem
  inp := s.inp.map fun x => x % 2 ^ w
  out := s.out.map fun x => x % 2 ^ w

theorem encodeFixedWord_mod (w x : ℕ) :
    encodeFixedWord w (x % 2 ^ w) = encodeFixedWord w x := by
  unfold encodeFixedWord
  rw [show fixedBits w (x % 2 ^ w) = fixedBits w x by
    simpa [bitsValue_fixedBits] using fixedBits_bitsValue (fixedBits w x)]

theorem encodeWordList_normalize (w : ℕ) (xs : List ℕ) :
    encodeWordList w (xs.map fun x => x % 2 ^ w) = encodeWordList w xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
      change encodeFixedWord w (x % 2 ^ w) ++
          encodeWordList w (xs.map fun x => x % 2 ^ w) =
        encodeFixedWord w x ++ encodeWordList w xs
      rw [encodeFixedWord_mod, ih]

theorem decodeWordList_encode_normalized (w : ℕ) (xs : List ℕ)
    (suffix : List SparseSymbol) :
    decodeWordList w xs.length (encodeWordList w xs ++ suffix) =
      (xs.map fun x => x % 2 ^ w, suffix) := by
  rw [← encodeWordList_normalize w xs]
  simpa using decodeWordList_encode w (xs.map fun x => x % 2 ^ w)
    (by
      intro x hx
      rcases List.mem_map.mp hx with ⟨y, -, rfl⟩
      exact Nat.mod_lt _ (by positivity)) suffix

end Lax51Proofs.RamToTM
