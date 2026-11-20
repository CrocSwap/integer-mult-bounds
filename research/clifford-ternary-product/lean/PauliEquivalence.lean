import PauliReadout

/-! The real local Pauli trace table and the trit leaves determine each other. -/
namespace PauliReadout
open TernaryCollect
open scoped BigOperators

variable {R : Type*} [CommRing R]

/-- Each Pauli matrix has one value on each of the three local classes. -/
def classEntry (v : Label) : Trit → R
  | some b => pauli v b b
  | none => pauli v false true

theorem local_class (v : Label) (x y : Bool) :
    pauli v x y = (classEntry v (trit x y) : R) := by
  cases x <;> cases y <;> simp [pauli, classEntry, trit]

def classWord {m : ℕ} (w : Fin m → Label) (t : TritWord m) : R :=
  ∏ i, classEntry (w i) (t i)

theorem word_on_class {m : ℕ} (w : Fin m → Label) (x y : Bits m) :
    word w x y = (classWord w (classify x y) : R) := by
  exact Finset.prod_congr rfl fun i _ ↦ local_class (w i) (x i) (y i)

theorem transcript_by_leaves {m : ℕ} (w : Fin m → Label) (Y : Matrix (Bits m) (Bits m) R) :
    pairing (word w) Y = ∑ t : TritWord m, classWord w t * leaf t Y := by
  classical
  rw [pairing_entries, ← (pairChart m).sum_comp, Fintype.sum_sigma]
  apply Finset.sum_congr rfl
  intro t _
  change (∑ u : Free t → Bool, word w (left t u) (right t u) * Y (left t u) (right t u)) =
    classWord w t * ∑ u : Free t → Bool, Y (left t u) (right t u)
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro u _
  rw [word_on_class, classify_expand]

/-- Over the integers, equal real Pauli traces are equivalent to equal trit leaves. -/
theorem same_integer_data {m : ℕ} (Y Z : Matrix (Bits m) (Bits m) ℤ) :
    (∀ w : Fin m → Label, pairing (word w) Y = pairing (word w) Z) ↔
    (∀ t : TritWord m, leaf t Y = leaf t Z) := by
  constructor
  · intro h t
    apply mul_left_cancel₀ (pow_ne_zero m (show (2:ℤ) ≠ 0 by norm_num))
    rw [← pauli_readout, ← pauli_readout]
    exact Finset.sum_congr rfl fun w _ ↦ congrArg (fun z => weight t w * z) (h w)
  · intro h w
    rw [transcript_by_leaves w Y, transcript_by_leaves w Z]
    exact Finset.sum_congr rfl fun t _ ↦ congrArg (fun z => classWord w t * z) (h t)

#print axioms transcript_by_leaves
#print axioms same_integer_data
end PauliReadout
