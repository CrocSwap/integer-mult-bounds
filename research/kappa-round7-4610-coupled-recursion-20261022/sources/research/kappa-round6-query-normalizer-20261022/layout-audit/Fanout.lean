/- All-column address identity used by the strided-bit Pauli phase adapter.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
No tape or recursive-supplier theorem is asserted here. -/
import Std

namespace StridedFanout

variable {I : Type} [DecidableEq I]

def fanout (pivot : I) (x : I → Bool) (j : I) : Bool :=
  if j = pivot then x j else x j != x pivot

def complement (x : I → Bool) (j : I) : Bool := !(x j)

def pivotFlip (pivot : I) (x : I → Bool) (j : I) : Bool :=
  if j = pivot then !(x j) else x j

theorem fanout_involutive (pivot : I) (x : I → Bool) :
    fanout pivot (fanout pivot x) = x := by
  funext j
  by_cases h : j = pivot
  · subst j; simp [fanout]
  · simp only [fanout, h, if_false, if_true]
    cases x j <;> cases x pivot <;> rfl

theorem conjugates_global_complement (pivot : I) (x : I → Bool) :
    fanout pivot (complement (fanout pivot x)) = pivotFlip pivot x := by
  funext j
  by_cases h : j = pivot
  · subst j; simp [fanout, complement, pivotFlip]
  · simp only [fanout, complement, pivotFlip, h, if_false, if_true]
    cases x j <;> cases x pivot <;> rfl

#print axioms fanout_involutive
#print axioms conjugates_global_complement

end StridedFanout
