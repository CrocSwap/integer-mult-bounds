import Current1094Row2DyadicReference

/-!
Concrete numerator/exponent budgets for the accepted exact encoded interpreter.
Only the finite set of addresses mentioned by the actual instruction trace is
bounded initially; all other initial memory is unrestricted. Scratch is visible.

The invariant uses numerator < 2^(B + cell.fractionalBits). Thus arbitrary
alignment shifts cancel against the current exponent, each addMemory contributes
one carry bit to B, and each exact halve contributes one to the exponent bound.
The resulting numerator budget is b + A + P + H for A additions and H halvings.
No shift, addition, exponent or address operation is assigned constant bit cost.

This is a trace bound for actual definitions, not a selected global precision
schedule or a uniform timing coefficient. The full selected program still has
non-SCALE/ADD events, allocation/encoding, rounding, cleanup and cost obligations.
Attribution: selected PR1094 emitter, machine reference instructions, analytic
Cell implementation and signed grid boundary. Apache-2.0; OpenAI-assisted.
Author-checked contextual kappa836330098538459/500000000000000000 is unchanged.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.DyadicTraceBitBudget
open Current1094Row1DyadicReference DyadicCellAddition Current1094Row2DyadicReference
abbrev Instruction := Current1094Row2AddReference.Instruction

/-- All memory addresses read or written by one actual instruction. -/
def addresses : Instruction → List Nat
  | .core (.read a) => [a]
  | .core (.write a) => [a]
  | .addMemory a => [a]
  | .core .halve => []
  | .core .negate => []

def accessed (ops : List Instruction) : List Nat := ops.flatMap addresses

def addition : Instruction → Nat
  | .addMemory _ => 1
  | .core _ => 0

def halving : Instruction → Nat
  | .core .halve => 1
  | _ => 0

def additions : List Instruction → Nat
  | [] => 0
  | op :: ops => addition op + additions ops

def halvings : List Instruction → Nat
  | [] => 0
  | op :: ops => halving op + halvings ops

/-- A value-scaled numerator budget; exponent storage is bounded separately. -/
def CellBound (B P : Nat) (c : Cell) : Prop :=
  c.fractionalBits ≤ P ∧ c.numerator.natAbs < 2 ^ (B + c.fractionalBits)

def StateBound (S : List Nat) (B P : Nat) (s : EncodedState) : Prop :=
  (∀ a ∈ S, CellBound B P (s.memory a)) ∧ CellBound B P s.accumulator

private theorem cell_mono {B P B' P' : Nat} {c : Cell}
    (h : CellBound B P c) (hb : B ≤ B') (hp : P ≤ P') : CellBound B' P' c := by
  refine ⟨h.1.trans hp, h.2.trans_le ?_⟩
  exact pow_le_pow_right₀ (by norm_num) (by omega)

private theorem half_bound {B P : Nat} {c : Cell} (h : CellBound B P c) :
    CellBound B (P + 1) (halfCell c) := by
  refine ⟨Nat.add_le_add_right h.1 1, ?_⟩
  change c.numerator.natAbs < 2 ^ (B + (c.fractionalBits + 1))
  exact h.2.trans_le (pow_le_pow_right₀ (by norm_num) (by omega))

private theorem neg_bound {B P : Nat} {c : Cell} (h : CellBound B P c) :
    CellBound B P (negCell c) := by
  simpa only [CellBound, negCell, Int.natAbs_neg] using h

private theorem add_bound {B P : Nat} {a b : Cell}
    (ha : CellBound B P a) (hb : CellBound B P b) :
    CellBound (B + 1) P (addCell a b) := by
  refine ⟨max_le ha.1 hb.1, ?_⟩
  have h := addCell_bit_budget a b (B + a.fractionalBits) (B + b.fractionalBits)
    ha.2 hb.2
  have hqa : a.fractionalBits ≤ commonExponent a b := le_max_left _ _
  have hqb : b.fractionalBits ≤ commonExponent a b := le_max_right _ _
  have ea : (B + a.fractionalBits) + (commonExponent a b - a.fractionalBits) =
      B + commonExponent a b := by omega
  have eb : (B + b.fractionalBits) + (commonExponent a b - b.fractionalBits) =
      B + commonExponent a b := by omega
  rw [ea, eb, max_self] at h
  change (addCell a b).numerator.natAbs < 2 ^ ((B + 1) + commonExponent a b)
  have e : (B + 1) + commonExponent a b = (B + commonExponent a b) + 1 := by omega
  rw [e]
  exact h

/-- Actual step preservation, with exactly one carry or exponent increment
according to the instruction. No arithmetic result is an input hypothesis. -/
theorem step_bound (S : List Nat) (B P : Nat) (op : Instruction) (s : EncodedState)
    (h : StateBound S B P s) (ha : ∀ a ∈ addresses op, a ∈ S) :
    StateBound S (B + addition op) (P + halving op) (stepAdd op s) := by
  cases op with
  | core op =>
      cases op with
      | read a =>
          change (∀ x ∈ S, CellBound B P (s.memory x)) ∧ CellBound B P (s.memory a)
          exact ⟨h.1, h.1 a (ha a (by simp [addresses]))⟩
      | halve =>
          change (∀ x ∈ S, CellBound B (P+1) (s.memory x)) ∧
            CellBound B (P+1) (halfCell s.accumulator)
          exact ⟨fun x hx => cell_mono (h.1 x hx) (le_refl B) (by omega), half_bound h.2⟩
      | negate =>
          change (∀ x ∈ S, CellBound B P (s.memory x)) ∧ CellBound B P (negCell s.accumulator)
          exact ⟨h.1, neg_bound h.2⟩
      | write a =>
          change (∀ x ∈ S, CellBound B P (Function.update s.memory a s.accumulator x)) ∧
            CellBound B P s.accumulator
          refine ⟨?_, h.2⟩
          intro x hx
          by_cases he : x = a
          · subst x
            simpa only [Function.update_self] using h.2
          · rw [Function.update_of_ne he]
            exact h.1 x hx
  | addMemory a =>
      change (∀ x ∈ S, CellBound (B+1) P (s.memory x)) ∧
        CellBound (B+1) P (addCell (s.memory a) s.accumulator)
      exact ⟨fun x hx => cell_mono (h.1 x hx) (by omega) (le_refl P),
        add_bound (h.1 a (ha a (by simp [addresses]))) h.2⟩

/-- The invariant follows the concrete chronological run and visible scratch. -/
theorem run_bound (S : List Nat) (ops : List Instruction) :
    ∀ (B P : Nat) (s : EncodedState), StateBound S B P s →
      (∀ op ∈ ops, ∀ a ∈ addresses op, a ∈ S) →
      StateBound S (B + additions ops) (P + halvings ops) (runAdd ops s) := by
  induction ops with
  | nil => intro B P s h _; exact h
  | cons op ops ih =>
      intro B P s h haddr
      have first := step_bound S B P op s h (haddr op (by simp))
      have rest := ih (B + addition op) (P + halving op) (stepAdd op s) first
        (fun x hx => haddr x (by simp [hx]))
      simpa only [runAdd, additions, halvings, Nat.add_assoc] using rest

private theorem initial_bound {b P : Nat} {c : Cell}
    (h : c.fractionalBits ≤ P ∧ c.numerator.natAbs < 2 ^ b) : CellBound b P c := by
  exact ⟨h.1, h.2.trans_le (pow_le_pow_right₀ (by norm_num) (by omega))⟩

private theorem uniform_bound {B P : Nat} {c : Cell} (h : CellBound B P c) :
    c.fractionalBits ≤ P ∧ c.numerator.natAbs < 2 ^ (B + P) := by
  exact ⟨h.1, h.2.trans_le (pow_le_pow_right₀ (by norm_num) (Nat.add_le_add_left h.1 B))⟩

/-- Explicit bit budget on any address set containing the actual trace access.
Each alignment shift is at most P+H because all current cell exponents are. -/
theorem run_bit_budget (S : List Nat) (ops : List Instruction) (s : EncodedState)
    (b P : Nat)
    (hm : ∀ a ∈ S, (s.memory a).fractionalBits ≤ P ∧ (s.memory a).numerator.natAbs < 2 ^ b)
    (hs : s.accumulator.fractionalBits ≤ P ∧ s.accumulator.numerator.natAbs < 2 ^ b)
    (haddr : ∀ op ∈ ops, ∀ a ∈ addresses op, a ∈ S) :
    (∀ a ∈ S, ((runAdd ops s).memory a).fractionalBits ≤ P + halvings ops ∧
      ((runAdd ops s).memory a).numerator.natAbs < 2 ^ (b + additions ops + (P + halvings ops))) ∧
    (runAdd ops s).accumulator.fractionalBits ≤ P + halvings ops ∧
      (runAdd ops s).accumulator.numerator.natAbs < 2 ^ (b + additions ops + (P + halvings ops)) := by
  have h := run_bound S ops b P s ⟨fun a ha => initial_bound (hm a ha), initial_bound hs⟩ haddr
  exact ⟨fun a ha => uniform_bound (h.1 a ha), uniform_bound h.2⟩

/-- Every actual prefix has its own addition/halving counts. Initial bounds are
needed only on the finite full-trace footprint and the incoming accumulator. -/
theorem trace_prefix_bit_budget (ops : List Instruction) (k : Nat) (s : EncodedState)
    (b P : Nat)
    (hm : ∀ a ∈ accessed ops, (s.memory a).fractionalBits ≤ P ∧
      (s.memory a).numerator.natAbs < 2 ^ b)
    (hs : s.accumulator.fractionalBits ≤ P ∧ s.accumulator.numerator.natAbs < 2 ^ b) :
    (∀ a ∈ accessed ops, ((runAdd (ops.take k) s).memory a).fractionalBits ≤ P + halvings (ops.take k) ∧
      ((runAdd (ops.take k) s).memory a).numerator.natAbs <
        2 ^ (b + additions (ops.take k) + (P + halvings (ops.take k)))) ∧
    (runAdd (ops.take k) s).accumulator.fractionalBits ≤ P + halvings (ops.take k) ∧
      (runAdd (ops.take k) s).accumulator.numerator.natAbs <
        2 ^ (b + additions (ops.take k) + (P + halvings (ops.take k))) := by
  apply run_bit_budget (accessed ops) (ops.take k) s b P hm hs
  intro op hop a ha
  exact List.mem_flatMap_of_mem (List.mem_of_mem_take hop) ha

end CurrentMain.DyadicTraceBitBudget
#print axioms CurrentMain.DyadicTraceBitBudget.step_bound
#print axioms CurrentMain.DyadicTraceBitBudget.run_bound
#print axioms CurrentMain.DyadicTraceBitBudget.run_bit_budget
#print axioms CurrentMain.DyadicTraceBitBudget.trace_prefix_bit_budget
