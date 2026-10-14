import Init

/-!
Reusable ordered finite-tape composition on labelled admissible domains.
Primitive instructions are indexed by their input and output domain labels.
Their forward and undo functions are supplied separately; no sign-flip or
precision change is interpreted as an inverse. Theorems propagate actual
intermediate domain membership before using a restricted primitive inverse.
Forward and backward directions have separate hypotheses, so one-sided local
laws do not silently become two-sided global invertibility.

Observable coordinates and per-primitive write supports are parameters. The
union of actual tape supports controls spectator preservation, including on
concatenations, without assuming a whole-tape endpoint or frame equation.
Typed concatenation matches boundary labels; semantic membership still follows
from the explicit primitive closure laws. Labels alone certify no arithmetic.

This generalizes the domain bookkeeping of DirtyDispatcherAdmissible and the
ordered reversal pattern of BitXorReversal without importing their selected
interpreters or repeating their primitive proofs. A client must bind actual
primitive functions, admissible domains and supports. Parsed rows, physical
storage/addresses/charts, initialized scratch, rounding and bit-cost remain
separate implementation obligations. No selected literal census is performed.
James Chang, with OpenAI assistance; Apache-2.0. Prior interface motivation:
Hanson Sun (@bbMisk), PR1530, and accepted PR590/597 ordered interpreter laws.
Author-checked selected context only:
kappa=836330098538459/500000000000000000. Uncompiled source candidate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.AdmissibleTypedTape
universe u v w x y

/-- Chronological composition; each primitive's output label is the next input. -/
inductive Tape {Label : Type u} (Op : Label → Label → Type v) :
    Label → Label → Type (max u v) where
  | nil (a : Label) : Tape Op a a
  | cons {a b c : Label} (op : Op a b) (tail : Tape Op b c) : Tape Op a c

variable {Label : Type u} {Op : Label → Label → Type v} {State : Type w}

def append {a b c : Label} (xs : Tape Op a b) (ys : Tape Op b c) : Tape Op a c :=
  match xs with
  | .nil _ => ys
  | .cons op tail => .cons op (append tail ys)

/-- Execute head first, retaining each primitive's actual supplied function. -/
def run (forward : ∀ {a b : Label}, Op a b → State → State) :
    ∀ {a b : Label}, Tape Op a b → State → State
  | _, _, .nil _, s => s
  | _, _, .cons op tail, s => run forward tail (forward op s)

/-- Execute actual undo functions in reverse order, tail before head. -/
def rewind (undo : ∀ {a b : Label}, Op a b → State → State) :
    ∀ {a b : Label}, Tape Op a b → State → State
  | _, _, .nil _, s => s
  | _, _, .cons op tail, s => undo op (rewind undo tail s)

theorem run_append (forward : ∀ {a b : Label}, Op a b → State → State)
    {a b : Label} (xs : Tape Op a b) :
    ∀ {c : Label} (ys : Tape Op b c) (s : State),
      run forward (append xs ys) s = run forward ys (run forward xs s) := by
  induction xs with
  | nil => intro c ys s; rfl
  | cons op tail ih => intro c ys s; exact ih ys (forward op s)

theorem rewind_append (undo : ∀ {a b : Label}, Op a b → State → State)
    {a b : Label} (xs : Tape Op a b) :
    ∀ {c : Label} (ys : Tape Op b c) (s : State),
      rewind undo (append xs ys) s = rewind undo xs (rewind undo ys s) := by
  induction xs with
  | nil => intro c ys s; rfl
  | cons op tail ih => intro c ys s; exact congrArg (undo op) (ih ys s)

/-- Applies to every typed prefix, not only a complete selected word. -/
theorem run_admissible
    (forward : ∀ {a b : Label}, Op a b → State → State)
    (D : Label → State → Prop)
    (hclosed : ∀ {a b : Label} (op : Op a b) (s : State),
      D a s → D b (forward op s))
    {a b : Label} (tape : Tape Op a b) :
    ∀ s, D a s → D b (run forward tape s) := by
  induction tape with
  | nil => intro s hs; exact hs
  | cons op tail ih =>
      intro s hs
      exact ih (forward op s) (hclosed op s hs)

/-- The reverse direction has its own domain-closure premise. -/
theorem rewind_admissible
    (undo : ∀ {a b : Label}, Op a b → State → State)
    (D : Label → State → Prop)
    (hclosed : ∀ {a b : Label} (op : Op a b) (s : State),
      D b s → D a (undo op s))
    {a b : Label} (tape : Tape Op a b) :
    ∀ s, D b s → D a (rewind undo tape s) := by
  induction tape with
  | nil => intro s hs; exact hs
  | cons op tail ih =>
      intro s hs
      exact hclosed op (rewind undo tail s) (ih s hs)

/-- Whole-tape left cancellation derived from restricted local left inverses.
No backward-closure or local right-inverse hypothesis is needed here. -/
theorem rewind_run
    (forward undo : ∀ {a b : Label}, Op a b → State → State)
    (D : Label → State → Prop)
    (hclosed : ∀ {a b : Label} (op : Op a b) (s : State),
      D a s → D b (forward op s))
    (hleft : ∀ {a b : Label} (op : Op a b) (s : State),
      D a s → undo op (forward op s) = s)
    {a b : Label} (tape : Tape Op a b) :
    ∀ s, D a s → rewind undo tape (run forward tape s) = s := by
  induction tape with
  | nil => intro s _hs; rfl
  | cons op tail ih =>
      intro s hs
      change undo op (rewind undo tail (run forward tail (forward op s))) = s
      rw [ih (forward op s) (hclosed op s hs)]
      exact hleft op s hs

/-- Whole-tape right cancellation uses separate local right inverses and
backward closure, at the actual reverse intermediate states. -/
theorem run_rewind
    (forward undo : ∀ {a b : Label}, Op a b → State → State)
    (D : Label → State → Prop)
    (hclosed : ∀ {a b : Label} (op : Op a b) (s : State),
      D b s → D a (undo op s))
    (hright : ∀ {a b : Label} (op : Op a b) (s : State),
      D b s → forward op (undo op s) = s)
    {a b : Label} (tape : Tape Op a b) :
    ∀ s, D b s → run forward tape (rewind undo tape s) = s := by
  induction tape with
  | nil => intro s _hs; rfl
  | cons op tail ih =>
      intro s hs
      have ht := rewind_admissible undo D hclosed tail s hs
      change run forward tail (forward op (undo op (rewind undo tail s))) = s
      rw [hright op (rewind undo tail s) ht]
      exact ih s hs

variable {Reg : Type x} {Value : Type y}

/-- Exact finite union of the primitive support predicates, with no deduplication
or claim that two logical coordinates denote distinct physical locations. -/
def touches (writes : ∀ {a b : Label}, Op a b → Reg → Prop) :
    ∀ {a b : Label}, Tape Op a b → Reg → Prop
  | _, _, .nil _, _ => False
  | _, _, .cons op tail, r => writes op r ∨ touches writes tail r

theorem touches_append (writes : ∀ {a b : Label}, Op a b → Reg → Prop)
    {a b : Label} (xs : Tape Op a b) :
    ∀ {c : Label} (ys : Tape Op b c) (r : Reg),
      touches writes (append xs ys) r ↔ touches writes xs r ∨ touches writes ys r := by
  induction xs with
  | nil => intro c ys r; simp only [append, touches, false_or]
  | cons op tail ih => intro c ys r; simp only [append, touches, ih, or_assoc]

/-- Domain-restricted primitive spectator laws compose in forward chronology. -/
theorem run_off_support
    (forward : ∀ {a b : Label}, Op a b → State → State)
    (D : Label → State → Prop)
    (observe : State → Reg → Value)
    (writes : ∀ {a b : Label}, Op a b → Reg → Prop)
    (hclosed : ∀ {a b : Label} (op : Op a b) (s : State),
      D a s → D b (forward op s))
    (hwrite : ∀ {a b : Label} (op : Op a b) (s : State), D a s →
      ∀ r, ¬ writes op r → observe (forward op s) r = observe s r)
    {a b : Label} (tape : Tape Op a b) :
    ∀ s, D a s → ∀ r, ¬ touches writes tape r →
      observe (run forward tape s) r = observe s r := by
  induction tape with
  | nil => intro s _hs r _hr; rfl
  | cons op tail ih =>
      intro s hs r hr
      have hhead : ¬ writes op r := fun h => hr (Or.inl h)
      have htail : ¬ touches writes tail r := fun h => hr (Or.inr h)
      exact (ih (forward op s) (hclosed op s hs) r htail).trans
        (hwrite op s hs r hhead)

/-- Reverse spectators require the actual undo support law and backward domain
closure; neither is inferred from a forward-only support or inverse statement. -/
theorem rewind_off_support
    (undo : ∀ {a b : Label}, Op a b → State → State)
    (D : Label → State → Prop)
    (observe : State → Reg → Value)
    (writes : ∀ {a b : Label}, Op a b → Reg → Prop)
    (hclosed : ∀ {a b : Label} (op : Op a b) (s : State),
      D b s → D a (undo op s))
    (hwrite : ∀ {a b : Label} (op : Op a b) (s : State), D b s →
      ∀ r, ¬ writes op r → observe (undo op s) r = observe s r)
    {a b : Label} (tape : Tape Op a b) :
    ∀ s, D b s → ∀ r, ¬ touches writes tape r →
      observe (rewind undo tape s) r = observe s r := by
  induction tape with
  | nil => intro s _hs r _hr; rfl
  | cons op tail ih =>
      intro s hs r hr
      have hhead : ¬ writes op r := fun h => hr (Or.inl h)
      have htail : ¬ touches writes tail r := fun h => hr (Or.inr h)
      have ht := rewind_admissible undo D hclosed tail s hs
      exact (hwrite op (rewind undo tail s) ht r hhead).trans (ih s hs r htail)

end CurrentMain.AdmissibleTypedTape
#print axioms CurrentMain.AdmissibleTypedTape.run_append
#print axioms CurrentMain.AdmissibleTypedTape.rewind_append
#print axioms CurrentMain.AdmissibleTypedTape.run_admissible
#print axioms CurrentMain.AdmissibleTypedTape.rewind_admissible
#print axioms CurrentMain.AdmissibleTypedTape.rewind_run
#print axioms CurrentMain.AdmissibleTypedTape.run_rewind
#print axioms CurrentMain.AdmissibleTypedTape.touches_append
#print axioms CurrentMain.AdmissibleTypedTape.run_off_support
#print axioms CurrentMain.AdmissibleTypedTape.rewind_off_support
#check @CurrentMain.AdmissibleTypedTape.rewind_run
#check @CurrentMain.AdmissibleTypedTape.run_off_support
