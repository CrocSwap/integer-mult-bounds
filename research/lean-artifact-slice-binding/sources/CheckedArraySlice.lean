import Init.Data.Array.Extract
import Init.Data.ByteArray.Basic

/-!
A reusable, executable offset witness for exact ordered array containment.
The caller supplies an offset, not an equality or a successful result.
Both the complete interval bound and the extracted-array equality are checked.
The bound prevents Array.extract's clamping from accepting an out-of-range
interval. Soundness derives every original-position element and an exact
prefix/fragment/suffix decomposition. Empty fragments remain valid precisely
at offsets at or before the artifact's end.

The ByteArray specialization checks the actual underlying UInt8 arrays. This
proves byte containment in the supplied artifact value, not its file origin,
cryptographic identity, JSON field role, key uniqueness or parser success.
It introduces no grammar, search procedure, literal census or execution-cost
claim. Existing fragment/dictionary semantic checks can be applied separately.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; generic statements do not use or change kappa.
Credits: Lean Array.extract API and proofs (Lean FRO and contributors), accepted
bank/frame byte-fragment work. James Chang with OpenAI assistance, Apache-2.0.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.CheckedArraySlice
universe u

/-- Check the full untruncated interval, then every ordered element. -/
def checkSlice {α : Type u} [DecidableEq α]
    (artifact fragment : Array α) (start : Nat) : Bool :=
  decide (start + fragment.size ≤ artifact.size) &&
    decide (artifact.extract start (start + fragment.size) = fragment)

/-- Exact soundness and completeness of the two executed checks. -/
theorem checkSlice_iff {α : Type u} [DecidableEq α]
    (artifact fragment : Array α) (start : Nat) :
    checkSlice artifact fragment start = true ↔
      start + fragment.size ≤ artifact.size ∧
        artifact.extract start (start + fragment.size) = fragment := by
  simp only [checkSlice, Bool.and_eq_true, decide_eq_true_eq]

/-- An empty fragment is valid at every in-range offset, including the endpoint. -/
theorem checkSlice_empty {α : Type u} [DecidableEq α]
    (artifact : Array α) (start : Nat) :
    checkSlice artifact #[] start = decide (start ≤ artifact.size) := by
  simp only [checkSlice, Array.size_empty, Nat.add_zero,
    Array.extract_empty_of_stop_le_start (Nat.le_refl start), decide_true, Bool.and_true]

/-- Each byte/element is tied to its original offset, preserving repeats. -/
theorem checkSlice_position {α : Type u} [DecidableEq α]
    (artifact fragment : Array α) (start : Nat)
    (h : checkSlice artifact fragment start = true) (i : Fin fragment.size) :
    ∃ hi : start + i.val < artifact.size, artifact[start + i.val]'hi = fragment[i.val] := by
  obtain ⟨_, he⟩ := (checkSlice_iff artifact fragment start).mp h
  have hi : i.val < (artifact.extract start (start + fragment.size)).size := by
    rw [he]
    exact i.isLt
  have hp := Array.getElem_extract (xs := artifact) (start := start)
    (stop := start + fragment.size) hi
  refine ⟨Array.getElem_extract_aux hi, ?_⟩
  simpa only [he] using hp.symm

/-- The exact fragment is the middle block of the unchanged complete array. -/
theorem checkSlice_decomposition {α : Type u} [DecidableEq α]
    (artifact fragment : Array α) (start : Nat)
    (h : checkSlice artifact fragment start = true) :
    artifact.extract 0 start ++ fragment ++
      artifact.extract (start + fragment.size) artifact.size = artifact := by
  obtain ⟨hb, he⟩ := (checkSlice_iff artifact fragment start).mp h
  have first : artifact.extract 0 start ++ artifact.extract start (start + fragment.size) =
      artifact.extract 0 (start + fragment.size) := by
    rw [Array.extract_append_extract, Nat.zero_min,
      Nat.max_eq_right (Nat.le_add_right start fragment.size)]
  have last : artifact.extract 0 (start + fragment.size) ++
      artifact.extract (start + fragment.size) artifact.size = artifact := by
    rw [Array.extract_append_extract, Nat.zero_min, Nat.max_eq_right hb, Array.extract_size]
  calc
    artifact.extract 0 start ++ fragment ++ artifact.extract (start + fragment.size) artifact.size =
        (artifact.extract 0 start ++ artifact.extract start (start + fragment.size)) ++
          artifact.extract (start + fragment.size) artifact.size :=
      congrArg (fun middle => artifact.extract 0 start ++ middle ++
        artifact.extract (start + fragment.size) artifact.size) he.symm
    _ = artifact.extract 0 (start + fragment.size) ++
          artifact.extract (start + fragment.size) artifact.size :=
      congrArg (fun left => left ++ artifact.extract (start + fragment.size) artifact.size) first
    _ = artifact := last

/-- Direct ByteArray application; no UTF-8/JSON conversion or hashing is used. -/
def checkBytes (artifact fragment : ByteArray) (start : Nat) : Bool :=
  checkSlice artifact.data fragment.data start

theorem checkBytes_iff (artifact fragment : ByteArray) (start : Nat) :
    checkBytes artifact fragment start = true ↔
      start + fragment.size ≤ artifact.size ∧
        artifact.data.extract start (start + fragment.size) = fragment.data := by
  exact checkSlice_iff artifact.data fragment.data start

theorem checkBytes_position (artifact fragment : ByteArray) (start : Nat)
    (h : checkBytes artifact fragment start = true) (i : Fin fragment.size) :
    ∃ hi : start + i.val < artifact.size,
      artifact.data[start + i.val]'hi = fragment.data[i.val]'i.isLt := by
  exact checkSlice_position artifact.data fragment.data start h i

theorem checkBytes_decomposition (artifact fragment : ByteArray) (start : Nat)
    (h : checkBytes artifact fragment start = true) :
    artifact.data.extract 0 start ++ fragment.data ++
      artifact.data.extract (start + fragment.size) artifact.size = artifact.data := by
  exact checkSlice_decomposition artifact.data fragment.data start h

end CurrentMain.CheckedArraySlice
#print axioms CurrentMain.CheckedArraySlice.checkSlice_iff
#print axioms CurrentMain.CheckedArraySlice.checkSlice_empty
#print axioms CurrentMain.CheckedArraySlice.checkSlice_position
#print axioms CurrentMain.CheckedArraySlice.checkSlice_decomposition
#print axioms CurrentMain.CheckedArraySlice.checkBytes_iff
#print axioms CurrentMain.CheckedArraySlice.checkBytes_position
#print axioms CurrentMain.CheckedArraySlice.checkBytes_decomposition
#check @CurrentMain.CheckedArraySlice.checkBytes_position
#check @CurrentMain.CheckedArraySlice.checkBytes_decomposition
