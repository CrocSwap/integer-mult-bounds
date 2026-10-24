/- Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
   Arbitrary selected-position controlled additions. The physical compact
   tape implementation and its cost are stated separately. -/
import Std

namespace ParallelSelectedControls

variable {I : Type}

def apply (route : I → Option I) (x : I → Bool) (j : I) : Bool :=
  match route j with
  | none => x j
  | some source => x j != x source

theorem involutive (route : I → Option I)
    (disjoint : ∀ j source, route j = some source → route source = none)
    (x : I → Bool) : apply route (apply route x) = x := by
  funext j
  cases hj : route j with
  | none => simp [apply, hj]
  | some source =>
    have hs := disjoint j source hj
    simp only [apply, hj, hs]
    cases x j <;> cases x source <;> rfl

theorem three_additions_swap (x y : Bool) :
    let a := x != y
    let b := y != a
    (a != b, b) = (y, x) := by
  cases x <;> cases y <;> rfl

end ParallelSelectedControls

#print axioms ParallelSelectedControls.involutive
#print axioms ParallelSelectedControls.three_additions_swap
