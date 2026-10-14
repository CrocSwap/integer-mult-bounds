import Lean

/-!
Signed-destination word semantics for the current-main extension.
Unlike the old PairedWord.Step, both coefficients may be -1.
Only the distinct-port condition is needed for invertibility; no zero-state,
independence, or uncorrelated-dirty-state premise is made.
-/
namespace CurrentMain.SignedWord
open Lean.Grind
set_option maxRecDepth 4000
set_option maxHeartbeats 1000000

structure Step where
  dst : Nat
  src : Nat
  dstNegative : Bool
  srcNegative : Bool
  deriving DecidableEq, Repr

abbrev State (F : Type u) := Nat → F
variable {F : Type u} [Ring F]

def signed (negative : Bool) (x : F) : F := if negative then -x else x
def add (x y : State F) : State F := fun i => x i + y i
def sub (x y : State F) : State F := fun i => x i - y i
def scale (a : F) (x : State F) : State F := fun i => a * x i

def forward (s : Step) (x : State F) : State F :=
  fun i => if i = s.dst then signed s.dstNegative (x s.dst) + signed s.srcNegative (x s.src)
    else x i

def backward (s : Step) (x : State F) : State F :=
  fun i => if i = s.dst then signed s.dstNegative (x s.dst - signed s.srcNegative (x s.src))
    else x i

/-- The inverse coefficient is -ca*cb, rather than simply -cb. -/
def inverse (s : Step) : Step :=
  { s with srcNegative := if s.dstNegative then s.srcNegative else !s.srcNegative }

def legal (s : Step) : Prop := s.dst ≠ s.src
instance (s : Step) : Decidable (legal s) := inferInstanceAs (Decidable (s.dst ≠ s.src))
def good (s : Step) : Bool := decide (legal s)
def Legal (ss : List Step) : Prop := ss.all good = true

def run : List Step → State F → State F
  | [], x => x
  | s :: ss, x => run ss (forward s x)

def undo : List Step → State F → State F
  | [], x => x
  | s :: ss, x => backward s (undo ss x)

def reverseWord (ss : List Step) : List Step := (ss.map inverse).reverse

theorem signed_involutive (b : Bool) (x : F) : signed b (signed b x) = x := by
  cases b <;> simp [signed, Ring.neg_neg]

theorem signed_add (b : Bool) (x y : F) : signed b (x+y) = signed b x + signed b y := by
  cases b <;> simp [signed, Ring.neg_add]

theorem signed_neg (b : Bool) (x : F) : signed b (-x) = -signed b x := by
  cases b <;> simp [signed]

theorem signed_scale (b : Bool) (a x : F) : signed b (a*x) = a*signed b x := by
  cases b <;> simp [signed, Ring.mul_neg]

theorem backward_forward (s : Step) (h : legal s) (x : State F) :
    backward s (forward s x) = x := by
  funext i
  have hs : s.src ≠ s.dst := Ne.symm h
  by_cases hi : i = s.dst
  · subst i
    simp only [backward, forward, if_pos rfl, if_neg hs]
    simp [Ring.sub_eq_add_neg, Semiring.add_assoc, Ring.add_neg_cancel,
      Semiring.add_zero, signed_involutive]
  · simp only [backward, forward, if_neg hi]

theorem forward_backward (s : Step) (h : legal s) (x : State F) :
    forward s (backward s x) = x := by
  funext i
  have hs : s.src ≠ s.dst := Ne.symm h
  by_cases hi : i = s.dst
  · subst i
    simp only [backward, forward, if_pos rfl, if_neg hs, signed_involutive]
    simp [signed_involutive, Ring.sub_eq_add_neg, Semiring.add_assoc, Ring.neg_add_cancel, Semiring.add_zero]
  · simp only [backward, forward, if_neg hi]

theorem forward_inverse (s : Step) (x : State F) : forward (inverse s) x = backward s x := by
  funext i
  by_cases hi : i = s.dst
  · subst i
    cases ha : s.dstNegative <;> cases hb : s.srcNegative <;>
      simp [forward, backward, inverse, signed, ha, hb, Ring.sub_eq_add_neg,
        Ring.neg_add, Ring.neg_neg]
  · simp [forward, backward, inverse, hi]

theorem inverse_involutive (s : Step) : inverse (inverse s) = s := by
  cases s with
  | mk d r a b => cases a <;> cases b <;> rfl

theorem inverse_legal (s : Step) : legal (inverse s) = legal s := rfl

theorem forward_add (s : Step) (x y : State F) :
    forward s (add x y) = add (forward s x) (forward s y) := by
  funext i
  by_cases hi : i = s.dst
  · subst i
    simp only [forward, add, if_pos rfl, signed_add]
    simp [Semiring.add_assoc, Semiring.add_comm, Semiring.add_left_comm]
  · simp only [forward, add, if_neg hi]

theorem forward_scale (s : Step) (a : F) (x : State F) :
    forward s (scale a x) = scale a (forward s x) := by
  funext i
  by_cases hi : i = s.dst
  · subst i
    simp [forward, scale, signed_scale, Semiring.left_distrib]
  · simp only [forward, scale, if_neg hi]

theorem forward_neg (s : Step) (x : State F) :
    forward s (fun i => -x i) = fun i => -(forward s x i) := by
  funext i
  by_cases hi : i = s.dst
  · subst i
    simp [forward, signed_neg, Ring.neg_add]
  · simp [forward, hi]

theorem backward_add (s : Step) (x y : State F) :
    backward s (add x y) = add (backward s x) (backward s y) := by
  simpa only [forward_inverse] using forward_add (inverse s) x y

theorem undo_run (ss : List Step) (h : Legal ss) (x : State F) : undo ss (run ss x) = x := by
  induction ss generalizing x with
  | nil => rfl
  | cons s ss ih =>
    have hh : good s = true ∧ ss.all good = true := Bool.and_eq_true_iff.mp h
    have hs : legal s := of_decide_eq_true hh.1
    simp only [run, undo]
    rw [ih hh.2, backward_forward s hs]

theorem run_undo (ss : List Step) (h : Legal ss) (x : State F) : run ss (undo ss x) = x := by
  induction ss generalizing x with
  | nil => rfl
  | cons s ss ih =>
    have hh : good s = true ∧ ss.all good = true := Bool.and_eq_true_iff.mp h
    have hs : legal s := of_decide_eq_true hh.1
    simp only [run, undo]
    rw [forward_backward s hs, ih hh.2]

theorem run_add (ss : List Step) (x y : State F) :
    run ss (add x y) = add (run ss x) (run ss y) := by
  induction ss generalizing x y with
  | nil => rfl
  | cons s ss ih => simp only [run, forward_add, ih]

theorem undo_add (ss : List Step) (x y : State F) :
    undo ss (add x y) = add (undo ss x) (undo ss y) := by
  induction ss with
  | nil => rfl
  | cons s ss ih => simp only [undo, ih, backward_add]

theorem run_scale (ss : List Step) (a : F) (x : State F) :
    run ss (scale a x) = scale a (run ss x) := by
  induction ss generalizing x with
  | nil => rfl
  | cons s ss ih => simp only [run, forward_scale, ih]

theorem run_neg (ss : List Step) (x : State F) :
    run ss (fun i => -x i) = fun i => -(run ss x i) := by
  induction ss generalizing x with
  | nil => rfl
  | cons s ss ih => simp only [run, forward_neg, ih]

theorem run_sub (ss : List Step) (x y : State F) :
    run ss (sub x y) = sub (run ss x) (run ss y) := by
  have eqsub (a b : State F) : sub a b = add a (fun i => -b i) := by
    funext i; exact Ring.sub_eq_add_neg _ _
  rw [eqsub, run_add, run_neg, eqsub]

theorem run_append (as bs : List Step) (x : State F) :
    run (as ++ bs) x = run bs (run as x) := by
  induction as generalizing x with
  | nil => rfl
  | cons s ss ih => simp only [List.cons_append, run, ih]

theorem reverse_run_eq_undo (ss : List Step) (x : State F) : run (reverseWord ss) x = undo ss x := by
  induction ss with
  | nil => rfl
  | cons s ss ih =>
    simp only [reverseWord, List.map_cons, List.reverse_cons, run_append, run]
    rw [← reverseWord, ih, forward_inverse]
    rfl

theorem literal_reverse_restores (ss : List Step) (h : Legal ss) (dirty : State F) :
    run (reverseWord ss) (run ss dirty) = dirty := by
  rw [reverse_run_eq_undo, undo_run ss h]

/-- Correlations or nonzero initial values in dirty have no effect on restoration. -/
theorem reverse_then_forward_restores (ss : List Step) (h : Legal ss) (dirty : State F) :
    run ss (run (reverseWord ss) dirty) = dirty := by
  rw [reverse_run_eq_undo, run_undo ss h]

/-- Forward response differences cancel every arbitrary incoming dirty component. -/
theorem dirty_response_cancels (ss : List Step) (dirty input : State F) :
    sub (run ss (add dirty input)) (run ss dirty) = run ss input := by
  rw [run_add]
  funext i
  simp only [sub, add, Ring.sub_eq_add_neg]
  rw [Semiring.add_comm (run ss dirty i), Semiring.add_assoc,
    Ring.add_neg_cancel, Semiring.add_zero]

/-- Adding an output-space signal between a word and its reverse transports only
that signal back; the complete dirty state survives unchanged. -/
theorem dirty_sandwich (ss : List Step) (h : Legal ss) (dirty signal : State F) :
    run (reverseWord ss) (add (run ss dirty) signal) = add dirty (undo ss signal) := by
  rw [reverse_run_eq_undo, undo_add, undo_run ss h]

/-- Coordinates never written by the word are preserved, even if they are read. -/
theorem run_unwritten (ss : List Step) (i : Nat) (h : ∀ s ∈ ss, i ≠ s.dst) (x : State F) :
    run ss x i = x i := by
  induction ss generalizing x with
  | nil => rfl
  | cons s ss ih =>
    have hs : i ≠ s.dst := h s (by simp)
    have ht : ∀ t ∈ ss, i ≠ t.dst := by
      intro t ht; exact h t (by simp [ht])
    rw [run, ih ht]
    simp [forward, hs]

end CurrentMain.SignedWord

#print axioms CurrentMain.SignedWord.signed_involutive
#print axioms CurrentMain.SignedWord.signed_add
#print axioms CurrentMain.SignedWord.signed_neg
#print axioms CurrentMain.SignedWord.signed_scale
#print axioms CurrentMain.SignedWord.backward_forward
#print axioms CurrentMain.SignedWord.forward_backward
#print axioms CurrentMain.SignedWord.forward_inverse
#print axioms CurrentMain.SignedWord.inverse_involutive
#print axioms CurrentMain.SignedWord.inverse_legal
#print axioms CurrentMain.SignedWord.forward_add
#print axioms CurrentMain.SignedWord.forward_scale
#print axioms CurrentMain.SignedWord.forward_neg
#print axioms CurrentMain.SignedWord.backward_add
#print axioms CurrentMain.SignedWord.undo_run
#print axioms CurrentMain.SignedWord.run_undo
#print axioms CurrentMain.SignedWord.run_add
#print axioms CurrentMain.SignedWord.undo_add
#print axioms CurrentMain.SignedWord.run_scale
#print axioms CurrentMain.SignedWord.run_neg
#print axioms CurrentMain.SignedWord.run_sub
#print axioms CurrentMain.SignedWord.run_append
#print axioms CurrentMain.SignedWord.reverse_run_eq_undo
#print axioms CurrentMain.SignedWord.literal_reverse_restores
#print axioms CurrentMain.SignedWord.reverse_then_forward_restores
#print axioms CurrentMain.SignedWord.dirty_response_cancels
#print axioms CurrentMain.SignedWord.dirty_sandwich
#print axioms CurrentMain.SignedWord.run_unwritten
