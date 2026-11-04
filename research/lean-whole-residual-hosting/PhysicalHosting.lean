import Hosting

/-!
Projection adapter for layouts with different auxiliary banks. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

Relocation can remove/re-tile old banks, so equality of every old and new
physical register is neither well-typed nor intended. The common retained
state is (one host stream, R). B and C are the original and relocated
auxiliary layouts. The endpoint hypotheses below quantify over EVERY
auxiliary input, allowing arbitrary dirt and arbitrary correlations.

The theorem compares retained outputs only. Every output/workspace component
whose equality or restoration matters must be included in R or verified by
an additional contract. Auxiliary outputs are not certified or discarded by
this theorem. A later computation may ignore them only with a proved scope
or independence argument. These source obligations remain explicit.
-/
namespace WholeHosting

structure PhysicalContract {ι K A R} (e : WindowEvent ι R) (B : Type b) (C : Type c) where
  original : (WindowState ι K A R × B) → (WindowState ι K A R × B)
  relocated : (WindowState ι K A R × C) → (WindowState ι K A R × C)
  original_retained : ∀ s bank, (original (s, bank)).1 = e.base s
  relocated_retained : ∀ s bank, (relocated (s, bank)).1 = e.hosted s

/-- The banks persist through the whole window; each subsequent invocation
receives the actual dirty output of its predecessor. -/
inductive PhysicalImplementations {ι K A R} (B : Type b) (C : Type c) :
    List (WindowEvent ι R) → Type _ where
  | nil : PhysicalImplementations (K := K) (A := A) B C []
  | cons {e es} (contract : PhysicalContract (K := K) (A := A) e B C)
      (rest : PhysicalImplementations (K := K) (A := A) B C es) :
      PhysicalImplementations (K := K) (A := A) B C (e :: es)

def PhysicalImplementations.runOriginal {ι K A R B C}
    {events : List (WindowEvent ι R)} :
    PhysicalImplementations (K := K) (A := A) B C events →
      (WindowState ι K A R × B) → (WindowState ι K A R × B)
  | .nil, s => s
  | .cons contract rest, s => rest.runOriginal (contract.original s)

def PhysicalImplementations.runRelocated {ι K A R B C}
    {events : List (WindowEvent ι R)} :
    PhysicalImplementations (K := K) (A := A) B C events →
      (WindowState ι K A R × C) → (WindowState ι K A R × C)
  | .nil, s => s
  | .cons contract rest, s => rest.runRelocated (contract.relocated s)

theorem PhysicalImplementations.original_projection {ι K A R B C}
    {events : List (WindowEvent ι R)}
    (program : PhysicalImplementations (K := K) (A := A) B C events)
    (state : WindowState ι K A R × B) :
    (program.runOriginal state).1 = runBase events state.1 := by
  induction program generalizing state with
  | nil => rfl
  | cons contract rest ih =>
    change (rest.runOriginal (contract.original state)).1 = runBase _ state.1
    rw [ih]
    change runBase _ (contract.original (state.1, state.2)).1 = _
    rw [contract.original_retained]
    rfl

theorem PhysicalImplementations.relocated_projection {ι K A R B C}
    {events : List (WindowEvent ι R)}
    (program : PhysicalImplementations (K := K) (A := A) B C events)
    (state : WindowState ι K A R × C) :
    (program.runRelocated state).1 = runHosted events state.1 := by
  induction program generalizing state with
  | nil => rfl
  | cons contract rest ih =>
    change (rest.runRelocated (contract.relocated state)).1 = runHosted _ state.1
    rw [ih]
    change runHosted _ (contract.relocated (state.1, state.2)).1 = _
    rw [contract.relocated_retained]
    rfl

/-- Exact retained-output equality for physically different bank layouts,
with actual bank outputs threaded through every complete invocation. -/
theorem physical_whole_hosting {ι K A R B C} {events : List (WindowEvent ι R)}
    (program : PhysicalImplementations (K := K) (A := A) B C events)
    (pending : Mask ι) (hd : DisjointMasks (residuals events))
    (hs : MaskSubset (maskUnion (residuals events)) pending)
    (s : WindowState ι K A R) (oldBank : B) (newBank : C) :
    onHost (remainderMask pending (maskUnion (residuals events)))
        (program.runRelocated (s, newBank)).1 =
      onHost pending (program.runOriginal (s, oldBank)).1 := by
  rw [program.original_projection, program.relocated_projection]
  exact whole_hosting events pending hd hs s

/-- External correlations and arbitrary observations of retained outputs
are permitted. Equality of the retained inputs is the only coupling required
between the original and relocated layouts. -/
theorem physical_hosting_in_context {ι K A R B C X Y}
    {events : List (WindowEvent ι R)}
    (program : PhysicalImplementations (K := K) (A := A) B C events)
    (pending : Mask ι) (hd : DisjointMasks (residuals events))
    (hs : MaskSubset (maskUnion (residuals events)) pending)
    (originalInput : X → WindowState ι K A R × B)
    (relocatedInput : X → WindowState ι K A R × C)
    (sameRetained : ∀ x, (originalInput x).1 = (relocatedInput x).1)
    (observe : WindowState ι K A R → Y) (x : X) :
    observe (onHost (remainderMask pending (maskUnion (residuals events)))
        (program.runRelocated (relocatedInput x)).1) =
      observe (onHost pending (program.runOriginal (originalInput x)).1) := by
  rw [program.original_projection, program.relocated_projection, sameRetained x]
  exact congrArg observe (whole_hosting events pending hd hs (relocatedInput x).1)

end WholeHosting

#print axioms WholeHosting.PhysicalImplementations.original_projection
#print axioms WholeHosting.PhysicalImplementations.relocated_projection
#print axioms WholeHosting.physical_whole_hosting
#print axioms WholeHosting.physical_hosting_in_context
