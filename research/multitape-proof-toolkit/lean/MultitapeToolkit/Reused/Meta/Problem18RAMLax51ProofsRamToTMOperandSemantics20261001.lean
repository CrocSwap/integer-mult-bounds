import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMPrependCellMacro20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Lax51Proofs.Microcode

/-! Semantic interface used by the concrete operand evaluator.  It separates
the low word that is placed on a work stack from the raw operand value.  The
distinction matters only for program literals: RAM subtraction, division and
shifts deliberately observe an oversized literal before final word
normalization. -/

def operandWordValue (w : ℕ) (o : Op) (m : SparseMemory) : ℕ :=
  sparseValue w o m % 2 ^ w

theorem SparseMemory.read_lt_of_normalized {w : ℕ} {m : SparseMemory}
    (hm : m.Normalized w) (a : ℕ) : m.read a < 2 ^ w := by
  induction m with
  | nil => simp [SparseMemory.read]
  | cons cell m ih =>
      rcases cell with ⟨b, v⟩
      rcases hm with ⟨_, hv, hm⟩
      by_cases hab : a = b
      · simpa [SparseMemory.read, hab] using hv
      · simpa [SparseMemory.read, hab] using ih hm

@[simp] theorem operandWordValue_lit (w n : ℕ) (m : SparseMemory) :
    operandWordValue w (.lit n) m = n % 2 ^ w := rfl

@[simp] theorem operandWordValue_mem (w a : ℕ) (m : SparseMemory) :
    operandWordValue w (.mem a) m = m.read (a % 2 ^ w) % 2 ^ w := rfl

@[simp] theorem operandWordValue_ind (w a : ℕ) (m : SparseMemory) :
    operandWordValue w (.ind a) m =
      m.read (m.read (a % 2 ^ w) % 2 ^ w) % 2 ^ w := rfl

theorem sparseValue_mem_lt {w : ℕ} {m : SparseMemory}
    (hm : m.Normalized w) (a : ℕ) : sparseValue w (.mem a) m < 2 ^ w := by
  exact SparseMemory.read_lt_of_normalized hm _

theorem sparseValue_ind_lt {w : ℕ} {m : SparseMemory}
    (hm : m.Normalized w) (a : ℕ) : sparseValue w (.ind a) m < 2 ^ w := by
  exact SparseMemory.read_lt_of_normalized hm _

theorem operandWordValue_mem_eq {w : ℕ} {m : SparseMemory}
    (hm : m.Normalized w) (a : ℕ) :
    operandWordValue w (.mem a) m = sparseValue w (.mem a) m := by
  exact Nat.mod_eq_of_lt (sparseValue_mem_lt hm a)

theorem operandWordValue_ind_eq {w : ℕ} {m : SparseMemory}
    (hm : m.Normalized w) (a : ℕ) :
    operandWordValue w (.ind a) m = sparseValue w (.ind a) m := by
  exact Nat.mod_eq_of_lt (sparseValue_ind_lt hm a)

theorem operandWordValue_lt (w : ℕ) (o : Op) (m : SparseMemory) :
    operandWordValue w o m < 2 ^ w := by
  exact Nat.mod_lt _ (by positivity)

theorem fixedBits_operandWordValue (w : ℕ) (o : Op) (m : SparseMemory) :
    fixedBits w (operandWordValue w o m) = fixedBits w (sparseValue w o m) := by
  rw [← fixedBits_bitsValue (fixedBits w (sparseValue w o m))]
  simp [operandWordValue]

/-- Nonliteral operands are always genuine words.  A literal fits precisely
when the quotient retained by `literalWordMachine` is zero. -/
theorem sparseValue_lt_word_iff : ∀ {w : ℕ} {m : SparseMemory} (hm : m.Normalized w)
    (o : Op), sparseValue w o m < 2 ^ w ↔
      match o with
      | .lit n => n / 2 ^ w = 0
      | .mem _ => True
      | .ind _ => True
  | w, m, hm, .lit n => by
      simp [sparseValue, Op.value, literalWord_remaining_eq_zero_iff]
  | w, m, hm, .mem a => by
      simp [sparseValue_mem_lt hm a]
  | w, m, hm, .ind a => by
      simp [sparseValue_ind_lt hm a]

end Lax51Proofs.RamToTM
