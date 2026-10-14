import Current1094Row1ScalarRealization
import Mathlib.Data.List.FinRange

/-!
A newly specified flat-memory implementation of the exact selected call000 raw1
coefficient. It visits real coordinates 0..n-1, then imaginary coordinates 0..n-1.
Every component executes read, halve, negate, write. The address layout, traversal
and instruction language here are explicit reference choices, not recovered code
from the selected emitter. Four abstract operations are not four bit operations.

The implementation derives its memory result without a supplied final update,
no-alias hypothesis, traversal hypothesis, or saved whole-vector buffer. Scratch
remains visible and may be dirty. Physical source-to-address correspondence,
rounding, finite-word costs and the actual selected runtime remain separate.

Reuse: the freshly checked independent-update, component-store and reference
routines; PR509/516 realization; PR1309 component interpretation. Author/source
attributions are retained in the predecessor packages. Prepared with OpenAI
assistance. Apache-2.0. Source proposal; this module has not been compiled.
-/
set_option Elab.async false
noncomputable section
namespace CurrentMain.Current1094Row1FlatReference

open ComponentStoreFoldRefinement ReferenceMinusHalfStore IndependentEntryFold
open Current1094Row1ScalarRealization

/-- A fixed complete traversal, with all real writes before imaginary writes. -/
def componentOrder (n : ℕ) : List (Slot (Fin n)) :=
  (List.finRange n).map Sum.inl ++ (List.finRange n).map Sum.inr

theorem componentOrder_nodup (n : ℕ) : (componentOrder n).Nodup := by
  apply List.Nodup.append
  · exact List.Nodup.map Sum.inl_injective (List.nodup_finRange n)
  · exact List.Nodup.map Sum.inr_injective (List.nodup_finRange n)
  · rw [List.disjoint_left]
    intro x hx hy
    rcases List.mem_map.mp hx with ⟨i, _, rfl⟩
    rcases List.mem_map.mp hy with ⟨j, _, h⟩
    cases h

theorem componentOrder_complete (n : ℕ) (s : Slot (Fin n)) :
    s ∈ componentOrder n := by
  cases s <;> simp [componentOrder]

theorem componentOrder_length (n : ℕ) : (componentOrder n).length = 2 * n := by
  simp [componentOrder, two_mul]

/-- A contiguous block: real at base+i, imaginary at base+n+i. -/
def flatAddress {n : ℕ} (base : ℕ) : Slot (Fin n) → ℕ
  | .inl i => base + i.val
  | .inr i => base + n + i.val

theorem flatAddress_injective (n base : ℕ) :
    Function.Injective (@flatAddress n base) := by
  intro a b hab
  cases a with
  | inl i =>
    cases b with
    | inl j =>
      apply congrArg Sum.inl
      apply Fin.ext
      change base + i.val = base + j.val at hab
      omega
    | inr j =>
      change base + i.val = base + n + j.val at hab
      have hi := i.isLt
      omega
  | inr i =>
    cases b with
    | inl j =>
      change base + n + i.val = base + j.val at hab
      have hj := j.isLt
      omega
    | inr j =>
      apply congrArg Sum.inr
      apply Fin.ext
      change base + n + i.val = base + n + j.val at hab
      omega

theorem flatAddress_bounds (n base : ℕ) (s : Slot (Fin n)) :
    base ≤ flatAddress base s ∧ flatAddress base s < base + 2 * n := by
  cases s with
  | inl i =>
    change base ≤ base + i.val ∧ base + i.val < base + 2 * n
    have hi := i.isLt
    omega
  | inr i =>
    change base ≤ base + n + i.val ∧ base + n + i.val < base + 2 * n
    have hi := i.isLt
    omega

inductive Instruction where
  | read (address : ℕ)
  | halve
  | negate
  | write (address : ℕ)

/-- Literal instruction semantics, reusing the four already checked operations. -/
def executeInstruction : Instruction → RefState ℕ → RefState ℕ
  | .read a => readSlot a
  | .halve => halve
  | .negate => negate
  | .write a => writeSlot a

def execute : List Instruction → RefState ℕ → RefState ℕ
  | [], s => s
  | op :: ops, s => execute ops (executeInstruction op s)

def componentCode (a : ℕ) : List Instruction :=
  [.read a, .halve, .negate, .write a]

def emit : List ℕ → List Instruction
  | [] => []
  | a :: rest => componentCode a ++ emit rest

theorem execute_append (xs ys : List Instruction) (s : RefState ℕ) :
    execute (xs ++ ys) s = execute ys (execute xs s) := by
  induction xs generalizing s with
  | nil => rfl
  | cons op ops ih =>
    exact ih (executeInstruction op s)

theorem execute_component (a : ℕ) (s : RefState ℕ) :
    execute (componentCode a) s = scalarStep a s := rfl

/-- All state fields, including the possibly dirty accumulator, match. -/
theorem execute_emit (addresses : List ℕ) (s : RefState ℕ) :
    execute (emit addresses) s = referenceRun addresses s := by
  induction addresses generalizing s with
  | nil => rfl
  | cons a rest ih =>
    simpa only [emit, execute_append, execute_component, referenceRun]
      using ih (scalarStep a s)

theorem emit_length (addresses : List ℕ) :
    (emit addresses).length = 4 * addresses.length := by
  induction addresses with
  | nil => rfl
  | cons a rest ih =>
    simp only [emit, List.length_append, componentCode, List.length_cons,
      List.length_nil, ih]
    omega

def program (n base : ℕ) : List Instruction :=
  emit ((componentOrder n).map (flatAddress base))

/-- Exact syntactic instruction count; it does not invoice bit-level work. -/
theorem program_length (n base : ℕ) : (program n base).length = 8 * n := by
  rw [program, emit_length, List.length_map, componentOrder_length]
  omega

/-- Every slot is written once, so the scalar action is derived from its own
original memory value. Both traversal and no-alias are proved above. -/
theorem program_slot (n base : ℕ) (s : RefState ℕ) (slot : Slot (Fin n)) :
    (execute (program n base) s).memory (flatAddress base slot) =
      (-1 / 2 : ℝ) * s.memory (flatAddress base slot) := by
  rw [program, execute_emit, referenceRun_memory]
  exact runUpdates_of_mem _ _
    (List.Nodup.map (flatAddress_injective n base) (componentOrder_nodup n))
    _ (List.mem_map.mpr ⟨slot, componentOrder_complete n slot, rfl⟩) _

/-- Every address outside the declared block is unchanged. -/
theorem program_outside (n base : ℕ) (s : RefState ℕ) (a : ℕ)
    (hout : a < base ∨ base + 2 * n ≤ a) :
    (execute (program n base) s).memory a = s.memory a := by
  rw [program, execute_emit, referenceRun_memory]
  apply runUpdates_of_not_mem
  intro ha
  rcases List.mem_map.mp ha with ⟨slot, _, heq⟩
  have hb := flatAddress_bounds n base slot
  omega

/-- The new flat-memory implementation refines the selected exact macro value
on the whole complex block; no endpoint equation is a premise. -/
theorem program_complex (n base : ℕ) (s : RefState ℕ) :
    decode (fun slot : Slot (Fin n) =>
      (execute (program n base) s).memory (flatAddress base slot)) =
    ((-1 / 2 : ℝ) : ℂ) •
      decode (fun slot : Slot (Fin n) => s.memory (flatAddress base slot)) := by
  rw [← real_scale_endpoint (-1 / 2)]
  apply PiLp.ext
  intro i
  apply Complex.ext
  · exact program_slot n base s (.inl i)
  · exact program_slot n base s (.inr i)

/-- Optional selected ordinary-family layout in this new implementation. The
source binds L119 to family119, but does not prescribe this numeric layout. -/
def selectedBase (n : ℕ) : ℕ := 119 * (2 * n)

/-- The checked Hosting specialization now has no traversal/no-alias premise.
This uses the fixed reference order, not a claim about the selected executor. -/
theorem fixed_row1_refines_realize {n : ℕ} {Φ M : Type*}
    [DecidableEq Φ] [AddCommMonoid M] [Module ℂ M]
    (σ : LemmaA.Hosting Current1094PrivateCentreHosting.Register Φ ℂ
      (EuclideanSpace ℂ (Fin n)) M)
    (rec : Fin 1004 → Fin 1004 → M → M)
    (y : Φ → EuclideanSpace ℂ (Fin n)) (scratch : ℝ) :
    (referenceFamilyStep (componentOrder n) (σ.own selectedRegister) y scratch).1 =
      LemmaA.realize σ rec selectedRow1 y := by
  exact selected_row1_refines_realize σ rec (componentOrder n)
    (componentOrder_nodup n) (componentOrder_complete n) y scratch

end CurrentMain.Current1094Row1FlatReference

#print axioms CurrentMain.Current1094Row1FlatReference.componentOrder_nodup
#print axioms CurrentMain.Current1094Row1FlatReference.componentOrder_complete
#print axioms CurrentMain.Current1094Row1FlatReference.flatAddress_injective
#print axioms CurrentMain.Current1094Row1FlatReference.flatAddress_bounds
#print axioms CurrentMain.Current1094Row1FlatReference.execute_emit
#print axioms CurrentMain.Current1094Row1FlatReference.program_length
#print axioms CurrentMain.Current1094Row1FlatReference.program_slot
#print axioms CurrentMain.Current1094Row1FlatReference.program_outside
#print axioms CurrentMain.Current1094Row1FlatReference.program_complex
#print axioms CurrentMain.Current1094Row1FlatReference.fixed_row1_refines_realize
#check @CurrentMain.Current1094Row1FlatReference.program_complex
#check @CurrentMain.Current1094Row1FlatReference.fixed_row1_refines_realize
