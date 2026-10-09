import Std

/-!
Finite binary dirty-scratch correctness, independently formalized for this audit.

`run` is a literal chronological word of XOR gates. Gate endpoints must differ.
There is no zero-scratch assumption. The theorem `compiled_wrapper_correct`
executes L,J,L⁻¹,V,L,J,L⁻¹,V and proves source preservation, restoration of
every auxiliary coordinate, and target addition of the specified output.

External interface: `scatter_linear` and `terminal_identity` must be supplied.
This file does not prove that a repository compiler emits the claimed word,
that address frames permit its gates, or that its tape cost has any bound.
-/

namespace DirtyWrapper

abbrev Vec (ι : Type) := ι → Bool

def vxor {ι : Type} (u v : Vec ι) : Vec ι := fun i => u i ^^ v i

theorem vxor_assoc {ι : Type} (u v w : Vec ι) :
    vxor (vxor u v) w = vxor u (vxor v w) := by
  funext i
  exact Bool.xor_assoc _ _ _

theorem vxor_cancel {ι : Type} (u v : Vec ι) : vxor (vxor u v) v = u := by
  funext i
  simp [vxor, Bool.xor_assoc]

theorem vxor_dirty_cancel {ι : Type} (z d y : Vec ι) :
    vxor (vxor z d) (vxor d y) = vxor z y := by
  funext i
  simp [vxor, ← Bool.xor_assoc]

def IsLinear {ι κ : Type} (f : Vec ι → Vec κ) : Prop :=
  ∀ u v, f (vxor u v) = vxor (f u) (f v)

structure Gate (ι : Type) where
  src : ι
  dst : ι
  distinct : src ≠ dst

def applyGate {ι : Type} [DecidableEq ι] (g : Gate ι) (u : Vec ι) : Vec ι :=
  fun i => if i = g.dst then u i ^^ u g.src else u i

theorem gate_involutive {ι : Type} [DecidableEq ι] (g : Gate ι) (u : Vec ι) :
    applyGate g (applyGate g u) = u := by
  funext i
  by_cases h : i = g.dst
  · subst i
    simp [applyGate, g.distinct, Bool.xor_assoc]
  · simp [applyGate, h]

theorem gate_linear {ι : Type} [DecidableEq ι] (g : Gate ι) :
    IsLinear (applyGate g) := by
  intro u v
  funext i
  by_cases h : i = g.dst
  · subst i
    simp only [applyGate, if_true, vxor]
    cases u g.dst <;> cases v g.dst <;> cases u g.src <;> cases v g.src <;> decide
  · simp [applyGate, h, vxor]

def run {ι : Type} [DecidableEq ι] : List (Gate ι) → Vec ι → Vec ι
  | [], u => u
  | g :: gs, u => run gs (applyGate g u)

theorem run_append {ι : Type} [DecidableEq ι] (xs ys : List (Gate ι)) (u : Vec ι) :
    run (xs ++ ys) u = run ys (run xs u) := by
  induction xs generalizing u with
  | nil => rfl
  | cons g gs ih => exact ih (applyGate g u)

theorem run_reverse_cancel {ι : Type} [DecidableEq ι] (gs : List (Gate ι))
    (u : Vec ι) : run gs.reverse (run gs u) = u := by
  induction gs generalizing u with
  | nil => rfl
  | cons g gs ih =>
    simp only [List.reverse_cons, run_append, run, ih]
    exact gate_involutive g u

theorem run_linear {ι : Type} [DecidableEq ι] (gs : List (Gate ι)) :
    IsLinear (run gs) := by
  induction gs with
  | nil => intro u v; rfl
  | cons g gs ih =>
    intro u v
    simp only [run, gate_linear g u v]
    exact ih (applyGate g u) (applyGate g v)

/-- A physical role now stores a full binary payload indexed by addresses. -/
abbrev Rows (D A : Type) := D → A → Bool

def applyRowGate {D A : Type} [DecidableEq D] (g : Gate D) (u : Rows D A) : Rows D A :=
  fun d a => if d = g.dst then u d a ^^ u g.src a else u d a

def runRows {D A : Type} [DecidableEq D] : List (Gate D) → Rows D A → Rows D A
  | [], u => u
  | g :: gs, u => runRows gs (applyRowGate g u)

/-- The same address map is applied to every role in the region. A permutation
is a special case; commutation itself does not need bijectivity. -/
def reindex {D A B : Type} (π : B → A) (u : Rows D A) : Rows D B :=
  fun d a => u d (π a)

theorem gate_reindex {D A B : Type} [DecidableEq D]
    (g : Gate D) (π : B → A) (u : Rows D A) :
    applyRowGate g (reindex π u) = reindex π (applyRowGate g u) := by
  rfl

/-- Equal-frame commutation: a common address reindexing commutes with an
arbitrary literal XOR word, for all initial payloads including dirty rows. -/
theorem word_reindex {D A B : Type} [DecidableEq D]
    (word : List (Gate D)) (π : B → A) (u : Rows D A) :
    runRows word (reindex π u) = reindex π (runRows word u) := by
  induction word generalizing u with
  | nil => rfl
  | cons g gs ih =>
    simp only [runRows, gate_reindex]
    exact ih (applyRowGate g u)

/-- The addresswise semantics of `runRows` is exactly the scalar semantics
already used in the dirty-wrapper theorem; this closes that correspondence. -/
theorem word_addresswise {D A : Type} [DecidableEq D]
    (word : List (Gate D)) (u : Rows D A) (a : A) :
    (fun d => runRows word u d a) = run word (fun d => u d a) := by
  induction word generalizing u with
  | nil => rfl
  | cons g gs ih =>
    simp only [runRows, run]
    exact ih (applyRowGate g u)

structure State (X : Type) (D Z : Type) where
  source : X
  scratch : Vec D
  target : Vec Z

def mix {X D Z : Type} (L : Vec D → Vec D) (s : State X D Z) : State X D Z :=
  { s with scratch := L s.scratch }

def scatter {X D Z : Type} (J : Vec D → Vec Z) (s : State X D Z) : State X D Z :=
  { s with target := vxor s.target (J s.scratch) }

def inject {X D Z : Type} (V : X → Vec D) (s : State X D Z) : State X D Z :=
  { s with scratch := vxor s.scratch (V s.source) }

/-- Literal chronological execution of L,J,L⁻¹,V,L,J,L⁻¹,V. -/
def wrapper {X D Z : Type} (L Linv : Vec D → Vec D) (J : Vec D → Vec Z)
    (V : X → Vec D) (s : State X D Z) : State X D Z :=
  let s1 := mix L s
  let s2 := scatter J s1
  let s3 := mix Linv s2
  let s4 := inject V s3
  let s5 := mix L s4
  let s6 := scatter J s5
  let s7 := mix Linv s6
  inject V s7

/-- Abstract wrapper theorem: reversibility, linearity and the terminal identity
are explicit local hypotheses; arbitrary dirty input is universally quantified. -/
theorem wrapper_correct {X D Z : Type}
    (L Linv : Vec D → Vec D) (J : Vec D → Vec Z) (V : X → Vec D)
    (output : X → Vec Z)
    (inverse : ∀ d, Linv (L d) = d)
    (mixer_linear : IsLinear L)
    (scatter_linear : IsLinear J)
    (terminal_identity : ∀ x, J (L (V x)) = output x)
    (x : X) (d : Vec D) (z : Vec Z) :
    wrapper L Linv J V ⟨x, d, z⟩ = ⟨x, d, vxor z (output x)⟩ := by
  unfold IsLinear at mixer_linear scatter_linear
  simp only [wrapper, mix, scatter, inject]
  simp only [inverse, vxor_cancel]
  simp only [mixer_linear, scatter_linear,
    terminal_identity, vxor_dirty_cancel]

/-- A serialized XOR word automatically supplies both reversibility and mixer
linearity; no separate hypotheses for those properties are required. -/
theorem compiled_wrapper_correct {X D Z : Type} [DecidableEq D]
    (word : List (Gate D)) (J : Vec D → Vec Z) (V : X → Vec D)
    (output : X → Vec Z)
    (scatter_linear : IsLinear J)
    (terminal_identity : ∀ x, J (run word (V x)) = output x)
    (x : X) (d : Vec D) (z : Vec Z) :
    wrapper (run word) (run word.reverse) J V ⟨x, d, z⟩ =
      ⟨x, d, vxor z (output x)⟩ := by
  exact wrapper_correct (run word) (run word.reverse) J V output
    (run_reverse_cancel word) (run_linear word) scatter_linear
    terminal_identity x d z

#print axioms vxor_assoc
#print axioms vxor_cancel
#print axioms vxor_dirty_cancel
#print axioms gate_involutive
#print axioms gate_linear
#print axioms run_append
#print axioms run_reverse_cancel
#print axioms run_linear
#print axioms gate_reindex
#print axioms word_reindex
#print axioms word_addresswise
#print axioms wrapper_correct
#print axioms compiled_wrapper_correct

end DirtyWrapper
