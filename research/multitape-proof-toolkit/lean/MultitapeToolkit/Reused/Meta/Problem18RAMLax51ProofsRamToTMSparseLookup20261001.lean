import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMSymbolEqualMacro20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

def SparseMemory.find? : SparseMemory → ℕ → Option ℕ
  | [], _ => none
  | (a, v) :: m, target =>
      if target = a then some v else SparseMemory.find? m target

@[simp] theorem SparseMemory.find?_getD (m : SparseMemory) (a : ℕ) :
    (SparseMemory.find? m a).getD 0 = m.read a := by
  induction m with
  | nil => rfl
  | cons cell m ih =>
      rcases cell with ⟨b, v⟩
      by_cases h : a = b <;> simp [SparseMemory.find?, SparseMemory.read, h, ih]

structure EncodedLookupResult where
  value : Option ℕ
  rest : List SparseSymbol

/-- Functional semantics of the delimiter-driven scan performed by the TM.
It stops at the first matching cell, exactly as `SparseMemory.read` does. -/
def scanEncodedCells (w target : ℕ) : ℕ → List SparseSymbol → EncodedLookupResult
  | 0, tape => ⟨none, tape⟩
  | count + 1, tape =>
      let head := decodeSparseCell w tape
      if target = head.1.1 then ⟨some head.1.2, head.2⟩
      else scanEncodedCells w target count head.2

def normalizeAddress (w a : ℕ) : ℕ := a % 2 ^ w

/-- A simpler extensional correctness statement: defaulting a failed scan to
zero gives exactly the sparse-memory read operation. -/
theorem scanEncodedCells_value_getD {w target : ℕ} {m : SparseMemory}
    (hm : m.Normalized w) (suffix : List SparseSymbol) :
    (scanEncodedCells w target m.length (encodeSparseMemory w m ++ suffix)).value.getD 0 =
      m.read target := by
  induction m with
  | nil => simp [scanEncodedCells, encodeSparseMemory, SparseMemory.read]
  | cons cell m ih =>
      rcases cell with ⟨a, v⟩
      rcases hm with ⟨ha, hv, htail⟩
      rw [show encodeSparseMemory w ((a, v) :: m) ++ suffix =
          encodeSparseCell w (a, v) ++ (encodeSparseMemory w m ++ suffix) by
        simp [encodeSparseMemory, List.append_assoc]]
      simp only [List.length_cons, scanEncodedCells]
      rw [decodeSparseCell_encode]
      rw [Nat.mod_eq_of_lt ha, Nat.mod_eq_of_lt hv]
      by_cases h : target = a
      · simp [h, SparseMemory.read]
      · simp [h, SparseMemory.read, ih htail]

end Lax51Proofs.RamToTM
