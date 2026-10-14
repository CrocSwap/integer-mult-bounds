import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMShiftMacro20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

/-- Finite work alphabet for serialized word lists and sparse memory. -/
inductive SparseSymbol
  | bit (value : Bool)
  | wordEnd
  | cellEnd
  | memoryEnd
  | inputEnd
  | outputEnd
  deriving DecidableEq, Fintype, Inhabited

def encodeFixedWord (w n : ℕ) : List SparseSymbol :=
  (fixedBits w n).map SparseSymbol.bit ++ [.wordEnd]

@[simp] theorem encodeFixedWord_length (w n : ℕ) :
    (encodeFixedWord w n).length = w + 1 := by
  simp [encodeFixedWord]

def encodeWordList (w : ℕ) (xs : List ℕ) : List SparseSymbol :=
  xs.flatMap (encodeFixedWord w)

@[simp] theorem encodeWordList_length (w : ℕ) (xs : List ℕ) :
    (encodeWordList w xs).length = xs.length * (w + 1) := by
  induction xs with
  | nil => simp [encodeWordList]
  | cons x xs ih => simp [encodeWordList, ih, Nat.add_mul]; omega

def encodeSparseCell (w : ℕ) (cell : ℕ × ℕ) : List SparseSymbol :=
  encodeFixedWord w cell.1 ++ encodeFixedWord w cell.2 ++ [.cellEnd]

@[simp] theorem encodeSparseCell_length (w : ℕ) (cell : ℕ × ℕ) :
    (encodeSparseCell w cell).length = 2 * w + 3 := by
  simp [encodeSparseCell]
  omega

def encodeSparseMemory (w : ℕ) (m : SparseMemory) : List SparseSymbol :=
  m.flatMap (encodeSparseCell w)

@[simp] theorem encodeSparseMemory_length (w : ℕ) (m : SparseMemory) :
    (encodeSparseMemory w m).length = m.length * (2 * w + 3) := by
  induction m with
  | nil => simp [encodeSparseMemory]
  | cons cell m ih => simp [encodeSparseMemory, ih, Nat.add_mul]; omega

/-- Tape-level serialization of the unbounded parts of a sparse RAM state.
The program counter is finite control because the simulated program is fixed. -/
def encodeSparseState (w : ℕ) (s : SparseState) : List SparseSymbol :=
  encodeFixedWord w s.acc ++
    encodeSparseMemory w s.mem ++ [.memoryEnd] ++
    encodeWordList w s.inp ++ [.inputEnd] ++
    encodeWordList w s.out ++ [.outputEnd]

@[simp] theorem encodeSparseState_length (w : ℕ) (s : SparseState) :
    (encodeSparseState w s).length =
      (w + 1) + s.mem.length * (2 * w + 3) +
        s.inp.length * (w + 1) + s.out.length * (w + 1) + 3 := by
  simp [encodeSparseState]
  omega

theorem encodeSparseState_length_le {w t : ℕ} {s : SparseState}
    (hmem : s.mem.length ≤ t) :
    (encodeSparseState w s).length ≤
      (w + 1) + t * (2 * w + 3) +
        s.inp.length * (w + 1) + s.out.length * (w + 1) + 3 := by
  rw [encodeSparseState_length]
  have hm := Nat.mul_le_mul_right (2 * w + 3) hmem
  omega

theorem sparseRun_encoded_memory_le {w t : ℕ} {p : Lax51Proofs.Microcode.Program}
    {x : List ℕ} {s : SparseState}
    (hrun : sparseRun w p t (sparseInitState x) = some s) :
    (encodeSparseMemory w s.mem).length ≤ t * (2 * w + 3) := by
  rw [encodeSparseMemory_length]
  exact Nat.mul_le_mul_right _ (sparseRun_init_mem_length_le hrun)

end Lax51Proofs.RamToTM
