import LemmaG.Stream

namespace StreamShadowRowUpdate

open LemmaG LemmaG.Stream

variable {ι Λ K : Type*} [DecidableEq ι] [Semiring K]

/-- Running a prefix and then a suffix is the same as running the prefix first and
feeding its state to the suffix. `scalRun` uses the same left-to-right order as an
emitted event list. -/
theorem scalRun_append {M : Type*} [AddCommMonoid M] [Module K M]
    (a b : List (Event ι Λ K)) (x : ι → M) :
    scalRun (a ++ b) x = scalRun b (scalRun a x) := by
  induction a generalizing x with
  | nil => rfl
  | cons e a ih =>
      change scalRun (a ++ b) (e.scal x) = scalRun b (scalRun a (e.scal x))
      exact ih (e.scal x)

/-- Exact recurrence for one row of the scalar-shadow matrix after one appended event.

The five cases match the scalar semantics: relabels are erased, additions replace the
target row by `row_target + q * row_source`, scales multiply one row, copies replace a
row by the source row, and clears zero one row. This theorem has no label-admissibility,
recipe, field, commutativity, or finiteness assumptions. -/
theorem S_append_event (es : List (Event ι Λ K)) (e : Event ι Λ K) (r j : ι) :
    S (es ++ [e]) r j =
      match e with
      | .relabel _ _ _ => S es r j
      | .add t s q => if r = t then S es t j + q * S es s j else S es r j
      | .scale t q => if r = t then q * S es t j else S es r j
      | .copy c s _ => if r = c then S es s j else S es r j
      | .clear c _ => if r = c then 0 else S es r j := by
  simp only [S]
  rw [scalRun_append]
  cases e with
  | relabel t A B =>
      by_cases h : r = t
      · subst r
        simp [scalRun, physRun, Event.scal, Event.phys]
      · simp [scalRun, physRun, Event.scal, Event.phys, h]
  | add t s q => simp [scalRun, physRun, Event.scal, Event.phys, Function.update_apply, smul_eq_mul]
  | scale t q => simp [scalRun, physRun, Event.scal, Event.phys, Function.update_apply, smul_eq_mul]
  | copy c s F => simp [scalRun, physRun, Event.scal, Event.phys, Function.update_apply]
  | clear c F => simp [scalRun, physRun, Event.scal, Event.phys, Function.update_apply]

end StreamShadowRowUpdate
