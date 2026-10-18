import BankEndpoints

/-!
Source interface for the ordered completed-bank sweep in pinned main
12a4934d15006e8c10f9b2264f13f8f341be802b, BANK-PROOF.md and
bank_template.py phase_schedule. This file proves only the dimension-free
composition step. The actual local physical words, address normalizers,
full-state endpoints, cover order, partition and common chart remain inputs.

The local endpoint premise quantifies over every bank value and every rest
value. Thus it expresses a no-cross-block endpoint on arbitrary, possibly
correlated dirty contents. It is not a clean-input or projected-run test.
-/
namespace CurrentMain.SequentialCompleteBank

open Lean.Grind CurrentMain.FrameTransport CurrentMain.BankEndpoints
open CurrentMain.SplitProjectors

universe u v w

/-- Chronological execution concatenates complete words in their given order. -/
theorem chronological_append {V : Type u} (xs ys : List (V → V)) (x : V) :
    run (xs ++ ys) x = run ys (run xs x) := by
  induction xs generalizing x with
  | nil => rfl
  | cons f fs ih =>
      simp only [List.cons_append, run]
      exact ih (f x)

/-- The existing completed product uses the opposite list convention. -/
theorem completed_append {V : Type u} (xs ys : List (V → V)) (x : V) :
    runCompleted (xs ++ ys) x = runCompleted xs (runCompleted ys x) := by
  induction xs with
  | nil => rfl
  | cons f fs ih =>
      simp only [List.cons_append, runCompleted, ih]

/-- Reverse the list, not the operators, to match the two execution conventions. -/
theorem chronological_map_eq_completed_reverse {V : Type u} {Role : Type v}
    (step : Role → V → V) (order : List Role) (x : V) :
    run (order.map step) x = runCompleted (order.reverse.map step) x := by
  induction order generalizing x with
  | nil => rfl
  | cons r rs ih =>
      simp only [List.map_cons, run, List.reverse_cons, List.map_append,
        List.map_nil, completed_append, runCompleted]
      exact ih (step r x)

/-- Compose only completed local words. A universal separated endpoint keeps
both bank and rest outputs explicit, without a cleanliness or independence premise. -/
theorem completed_words_separate {Bank : Type u} {Rest : Type v} {Role : Type w}
    (word : Role → List ((Bank × Rest) → (Bank × Rest)))
    (bankStep : Role → Bank → Bank) (restStep : Role → Rest → Rest)
    (order : List Role) :
    (∀ r, r ∈ order → ∀ b s,
      run (word r) (b, s) = (bankStep r b, restStep r s)) →
    ∀ b s, run (order.flatMap word) (b, s) =
      (run (order.map bankStep) b, run (order.map restStep) s) := by
  induction order with
  | nil => intro _ b s; rfl
  | cons r rs ih =>
      intro local_endpoint b s
      have head := local_endpoint r (List.mem_cons_self) b s
      have tail : ∀ r', r' ∈ rs → ∀ b' s',
          run (word r') (b', s') = (bankStep r' b', restStep r' s') := by
        intro r' hr' b' s'
        exact local_endpoint r' (List.mem_cons_of_mem r hr') b' s'
      simp only [List.flatMap_cons, chronological_append, List.map_cons, run]
      rw [head]
      exact ih tail (bankStep r b) (restStep r s)

/-- A literal head-first sweep of complete local words has the weighted full-bank
endpoint once its exact no-cross-block local endpoints and reversed-list partition
are supplied. Reversal here is solely the list convention of runCompleted; it
makes no assertion about a complemented physical word or inverse erasure.

For the selected source, the scheduler owner must bind order.flatMap word to the
actual stage/replica/cover stream, and prove that each whole local word completes
before bank reuse. The normalizer owner supplies each exact projector and the
single bank chart. No physical-word, GL120, finite-census or cost theorem is assumed
proved by this generic conclusion. -/
theorem sequential_complete_bank {M : Type u} [CommRing M]
    {Rest : Type v} {Role : Type w}
    (word : Role → List (((M × M) × Rest) → ((M × M) × Rest)))
    (restStep : Role → Rest → Rest) (order : List Role)
    (C : Frame (M × M)) (projector : Role → AdditiveEnd M)
    (local_endpoint : ∀ r, r ∈ order → ∀ b s,
      run (word r) (b, s) =
        (conjugate C (partialSwap (projector r).map) b, restStep r s))
    (disjoint : DisjointList (order.reverse.map projector))
    (partition : ∀ x, (sumEnds (order.reverse.map projector)).map x = x)
    (b : M × M) (s : Rest) :
    run (order.flatMap word) (b, s) =
      (C.encode ((C.decode b).2, (C.decode b).1),
        run (order.map restStep) s) := by
  have bank_endpoint :
      run (order.map (fun r => conjugate C (partialSwap (projector r).map))) b =
        C.encode ((C.decode b).2, (C.decode b).1) := by
    rw [chronological_map_eq_completed_reverse]
    have h := weighted_partition_endpoint C (order.reverse.map projector)
      disjoint partition b
    simpa only [List.map_map, Function.comp_def] using h
  have separated := completed_words_separate word
    (fun r => conjugate C (partialSwap (projector r).map)) restStep order
    local_endpoint b s
  exact separated.trans (congrArg
    (fun bank => (bank, run (order.map restStep) s)) bank_endpoint)

end CurrentMain.SequentialCompleteBank

#print axioms CurrentMain.SequentialCompleteBank.chronological_append
#print axioms CurrentMain.SequentialCompleteBank.completed_append
#print axioms CurrentMain.SequentialCompleteBank.chronological_map_eq_completed_reverse
#print axioms CurrentMain.SequentialCompleteBank.completed_words_separate
#print axioms CurrentMain.SequentialCompleteBank.sequential_complete_bank
