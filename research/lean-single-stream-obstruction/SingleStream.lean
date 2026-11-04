import Std

/-!
Single-stream interface obstruction. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

This is an abstract interface test, not a translation of a CrocSwap word.
Streams hold arbitrary independent values. A fixed owner permits a read of
one stream; an address permutation within that stream does not expose another
stream. The program model allows arbitrary visible state (including scratch)
and arbitrary hidden updates, but excludes reads from hidden to visible.
-/
namespace SingleStream

inductive Owner where
  | left | right
  deriving DecidableEq, Repr

def select {A : Type} : Owner → A × A → A
  | .left, p => p.1
  | .right, p => p.2

/-- One helper operand, with arbitrary processing of the owned stream. -/
def Realizes {A R : Type} (o : Owner) (read : A → A → R) : Prop :=
  ∃ localRead : A → R, ∀ a b, localRead (select o (a, b)) = read a b

/-- An exact criterion: a read factors through the owner iff it is constant
on that owner's fibres. The supplied `base` avoids any choice principle. -/
theorem realizes_iff {A R : Type} (base : A) (o : Owner) (read : A → A → R) :
    Realizes o read ↔
      ∀ a b a' b', select o (a, b) = select o (a', b') → read a b = read a' b' := by
  constructor
  · rintro ⟨localRead, h⟩ a b a' b' heq
    rw [← h a b, ← h a' b', heq]
  · intro h
    cases o with
    | left =>
      refine ⟨fun a => read a base, ?_⟩
      intro a b
      exact h a base a b rfl
    | right =>
      refine ⟨fun b => read base b, ?_⟩
      intro a b
      exact h base b a b rfl

/-- Dependence on both independent pieces rules out every fixed owner,
regardless of the computation performed within its stream. -/
theorem no_owner_of_two_dependencies {A R : Type} (read : A → A → R)
    (a b b' c c' d : A)
    (hiddenRight : read a b ≠ read a b')
    (hiddenLeft : read c d ≠ read c' d) :
    ∀ o, ¬ Realizes o read := by
  intro o h
  have hf := (realizes_iff a o read).mp h
  cases o with
  | left => exact hiddenRight (hf a b a b' rfl)
  | right => exact hiddenLeft (hf c d c' d rfl)

/-- Visible state may contain a target, the owned helper, and any local scratch.
Hidden updates may read visible state, but visible updates cannot read hidden.
No claim is made that arbitrary routing satisfies this restriction. -/
structure Step (V H : Type) where
  visible : V → V
  hidden : V → H → H

def Step.apply {V H : Type} (step : Step V H) (state : V × H) : V × H :=
  (step.visible state.1, step.hidden state.1 state.2)

def run {V H : Type} : List (Step V H) → V × H → V × H
  | [], state => state
  | step :: rest, state => run rest (step.apply state)

/-- Unbounded list induction, not a bounded enumeration of programs. -/
theorem run_visible_eq {V H : Type} (program : List (Step V H))
    (s t : V × H) (sameVisible : s.1 = t.1) :
    (run program s).1 = (run program t).1 := by
  induction program generalizing s t with
  | nil => exact sameVisible
  | cons step rest ih =>
    exact ih (step.apply s) (step.apply t) (congrArg step.visible sameVisible)

/-- A useful gate-level witness: x += a+b really reads both pieces. -/
def dirtyRead (x a b : Int) : Int := x + a + b

theorem dirty_read_no_owner (x : Int) :
    ∀ o, ¬ Realizes o (dirtyRead x) := by
  apply no_owner_of_two_dependencies (dirtyRead x) 0 0 1 0 1 0
  · simp only [dirtyRead]; omega
  · simp only [dirtyRead]; omega

/-- Even arbitrarily many operations and independent hidden transforms cannot
produce this read before information from the other stream is admitted.
Visible state is (target, owned helper); hidden state is the other helper. -/
theorem dirty_read_no_local_program
    (program : List (Step (Int × Int) Int)) :
    ¬ (∀ x a b : Int, (run program ((x, a), b)).1.1 = dirtyRead x a b) := by
  intro h
  have hn := congrArg Prod.fst
    (run_visible_eq program ((0, 0), 0) ((0, 0), 1) rfl)
  rw [h 0 0 0, h 0 0 1] at hn
  contradiction

/-- Positive control: a whole helper read has a single-stream realization. -/
theorem whole_read_realizes (x : Int) :
    Realizes .left (fun a (_ : Int) => x + a) := by
  exact ⟨fun a => x + a, fun _ _ => rfl⟩

/-- Positive control: two helper operands realize the split read. -/
def twoReads (x a b : Int) : Int := (x + a) + b

theorem two_reads_realize (x a b : Int) :
    twoReads x a b = dirtyRead x a b := rfl

/-- A one-owner residual operation leaves the unowned stream alone. -/
def oneResidual {A : Type} (o : Owner) (f : A → A) (p : A × A) : A × A :=
  match o with
  | .left => (f p.1, p.2)
  | .right => (p.1, f p.2)

def splitResidual {A : Type} (f g : A → A) (p : A × A) : A × A :=
  (f p.1, g p.2)

/-- Two nontrivial factors cannot be the action of a single owned-stream
operation. This is a support statement, not a matrix/coordinate theorem. -/
theorem split_residual_no_owner {A : Type} (f g : A → A) (a b : A)
    (hf : f a ≠ a) (hg : g b ≠ b) :
    ∀ o localFactor, ¬ (∀ p, oneResidual o localFactor p = splitResidual f g p) := by
  intro o localFactor h
  have hp := h (a, b)
  cases o with
  | left => exact hg (congrArg Prod.snd hp).symm
  | right => exact hf (congrArg Prod.fst hp).symm

/-- The one-coordinate bit factor D: swap two address coordinates within
one stream. The stream's payload, not its address, is Boolean. -/
def bitFactor (v : (Bool × Bool) → Bool) : (Bool × Bool) → Bool :=
  fun p => v (p.2, p.1)

def bitWitness : (Bool × Bool) → Bool := fun p => p.1 && !p.2

theorem bit_factor_nontrivial : bitFactor bitWitness ≠ bitWitness := by
  intro h
  have hpoint := congrFun h (true, false)
  contradiction

/-- Exact Gaussian integers, and a one-coordinate complex phase C.
At address true multiply by i; at false use phase 1. -/
def rotate (z : Int × Int) : Int × Int := (-z.2, z.1)
def complexFactor (v : Bool → Int × Int) : Bool → Int × Int :=
  fun y => if y then rotate (v y) else v y

def complexWitness : Bool → Int × Int := fun _ => (1, 0)

theorem complex_factor_nontrivial : complexFactor complexWitness ≠ complexWitness := by
  intro h
  have hpoint := congrArg Prod.snd (congrFun h true)
  contradiction

/-- A split D factor on two independent streams is not one owned-stream
operation, even with an arbitrary operator on that one stream. -/
theorem split_bit_factor_no_owner :
    ∀ o localFactor, ¬ (∀ p,
      oneResidual o localFactor p = splitResidual bitFactor bitFactor p) :=
  split_residual_no_owner bitFactor bitFactor bitWitness bitWitness
    bit_factor_nontrivial bit_factor_nontrivial

/-- The same obstruction for the exact one-coordinate complex phase. -/
theorem split_complex_factor_no_owner :
    ∀ o localFactor, ¬ (∀ p,
      oneResidual o localFactor p = splitResidual complexFactor complexFactor p) :=
  split_residual_no_owner complexFactor complexFactor complexWitness complexWitness
    complex_factor_nontrivial complex_factor_nontrivial

/-- Two separate owned-stream operations do implement the product. -/
theorem two_residuals_realize {A : Type} (f g : A → A) (p : A × A) :
    oneResidual .right g (oneResidual .left f p) = splitResidual f g p := rfl

/-- An exact integer dirty-wrapper control, with sign-flip residuals and an
arbitrary target map. Both helper reads are explicit. This is not D_S/C_S. -/
def twoHelperWord (target : Int → Int) (x a b : Int) : Int × (Int × Int) :=
  let read := twoReads x a b
  let a' := -a
  let b' := -b
  let cancel := read - (-a') - (-b')
  (target cancel, (a', b'))

theorem two_helper_word_endpoint (target : Int → Int) (x a b : Int) :
    twoHelperWord target x a b = (target x, (-a, -b)) := by
  have hc : twoReads x a b - (-(-a)) - (-(-b)) = x := by
    simp only [twoReads]; omega
  simp only [twoHelperWord, hc]

/-- Universal endpoints also hold for correlated dirty inputs, pointwise. -/
theorem correlated_two_helper_endpoint {Ω : Type} (target : Int → Int)
    (x a b : Ω → Int) (w : Ω) :
    twoHelperWord target (x w) (a w) (b w) =
      (target (x w), (-a w, -b w)) :=
  two_helper_word_endpoint target (x w) (a w) (b w)

end SingleStream

#print axioms SingleStream.realizes_iff
#print axioms SingleStream.no_owner_of_two_dependencies
#print axioms SingleStream.run_visible_eq
#print axioms SingleStream.dirty_read_no_owner
#print axioms SingleStream.dirty_read_no_local_program
#print axioms SingleStream.whole_read_realizes
#print axioms SingleStream.two_reads_realize
#print axioms SingleStream.split_residual_no_owner
#print axioms SingleStream.two_residuals_realize
#print axioms SingleStream.two_helper_word_endpoint
#print axioms SingleStream.correlated_two_helper_endpoint
#print axioms SingleStream.bit_factor_nontrivial
#print axioms SingleStream.complex_factor_nontrivial
#print axioms SingleStream.split_bit_factor_no_owner
#print axioms SingleStream.split_complex_factor_no_owner
