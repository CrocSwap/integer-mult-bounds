import CoordinateSwap

/-!
Whole residual hosting on all affected physical streams. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

`H` indexes distinct physical streams, not merely source family labels.
Each stream has a fixed coordinate chart throughout the window. Source
ownership and chart transport must establish this interpretation; they are
not consequences of the abstract product type. `R` contains all remaining
retained outputs, including scratch whose restoration is to be compared.
The complete endpoint contracts quantify over arbitrary stream contents,
retained state and auxiliary dirt; no independence or initialization is
assumed. Source refinement remains a separate obligation.
-/
namespace MultiHosting
open WholeHosting

abbrev HostMask (H : Type h) (ι : Type u) := H → Mask ι
abbrev WindowState (H : Type h) (ι : Type u) (K : Type v) (A : Type w) (R : Type z) :=
  (H → Stream ι K A) × R

/-- One complete invocation endpoint in fixed charts for every host. `other`
cannot depend on any host, although a physical implementation may temporarily
read them if its complete endpoint satisfies the universal contract. -/
structure WindowEvent (H : Type h) (ι : Type u) (R : Type z) where
  idle : HostMask H ι
  residual : HostMask H ι
  other : R → R

def onHosts {H ι K A R} (masks : HostMask H ι)
    (s : WindowState H ι K A R) : WindowState H ι K A R :=
  (fun h => bitAction (masks h) (s.1 h), s.2)

def WindowEvent.base {H ι K A R} (e : WindowEvent H ι R)
    (s : WindowState H ι K A R) : WindowState H ι K A R :=
  (fun h => bitAction (e.idle h) (s.1 h), e.other s.2)

def WindowEvent.hosted {H ι K A R} (e : WindowEvent H ι R)
    (s : WindowState H ι K A R) : WindowState H ι K A R :=
  onHosts e.residual (e.base s)

def runBase {H ι K A R} :
    List (WindowEvent H ι R) → WindowState H ι K A R → WindowState H ι K A R
  | [], s => s
  | e :: es, s => runBase es (e.base s)

def runHosted {H ι K A R} :
    List (WindowEvent H ι R) → WindowState H ι K A R → WindowState H ι K A R
  | [], s => s
  | e :: es, s => runHosted es (e.hosted s)

def residuals {H ι R} (events : List (WindowEvent H ι R)) (h : H) : List (Mask ι) :=
  events.map (fun e => e.residual h)

def masksUnion {H ι R} (events : List (WindowEvent H ι R)) : HostMask H ι :=
  fun h => maskUnion (residuals events h)

def remainders {H ι R} (pending : HostMask H ι)
    (events : List (WindowEvent H ι R)) : HostMask H ι :=
  fun h => remainderMask (pending h) (masksUnion events h)

def allOnHosts {H ι K A R} (events : List (WindowEvent H ι R))
    (s : WindowState H ι K A R) : WindowState H ι K A R :=
  (fun h => bitFactors (residuals events h) (s.1 h), s.2)

theorem base_commutes {H ι K A R} (e : WindowEvent H ι R) (p : HostMask H ι)
    (s : WindowState H ι K A R) : e.base (onHosts p s) = onHosts p (e.base s) := by
  apply Prod.ext
  · funext h
    exact bitAction_commute (p h) (e.idle h) (s.1 h)
  · rfl

theorem runBase_commutes {H ι K A R} (events : List (WindowEvent H ι R))
    (p : HostMask H ι) (s : WindowState H ι K A R) :
    runBase events (onHosts p s) = onHosts p (runBase events s) := by
  induction events generalizing s with
  | nil => rfl
  | cons e es ih =>
    change runBase es (e.base (onHosts p s)) = onHosts p (runBase es (e.base s))
    rw [base_commutes, ih]

/-- Simultaneously move the residual on every host to the end. This permits
several hosts to change during the same complete invocation. -/
theorem delay_residuals {H ι K A R} (events : List (WindowEvent H ι R))
    (s : WindowState H ι K A R) :
    runHosted events s = allOnHosts events (runBase events s) := by
  induction events generalizing s with
  | nil => rfl
  | cons e es ih =>
    change runHosted es (onHosts e.residual (e.base s)) =
      allOnHosts (e :: es) (runBase es (e.base s))
    rw [ih, runBase_commutes]
    rfl

/-- Each physical host has its own disjoint-mask and pending-subset
obligations. The equality covers every host and all of `R` on every input.
It does not by itself prove that a source program implements these endpoints. -/
theorem multi_hosting {H ι K A R} (events : List (WindowEvent H ι R))
    (pending : HostMask H ι)
    (hd : ∀ h, DisjointMasks (residuals events h))
    (hs : ∀ h, MaskSubset (masksUnion events h) (pending h))
    (s : WindowState H ι K A R) :
    onHosts (remainders pending events) (runHosted events s) =
      onHosts pending (runBase events s) := by
  rw [delay_residuals]
  apply Prod.ext
  · funext h
    exact bitFactors_complete (pending h) (residuals events h) (hd h) (hs h)
      ((runBase events s).1 h)
  · rfl

theorem multi_hosting_in_context {H ι K A R X Y}
    (events : List (WindowEvent H ι R)) (pending : HostMask H ι)
    (hd : ∀ h, DisjointMasks (residuals events h))
    (hs : ∀ h, MaskSubset (masksUnion events h) (pending h))
    (before : X → WindowState H ι K A R)
    (after : WindowState H ι K A R → Y) (x : X) :
    after (onHosts (remainders pending events) (runHosted events (before x))) =
      after (onHosts pending (runBase events (before x))) :=
  congrArg after (multi_hosting events pending hd hs (before x))

/-- `B` and `C` may be different auxiliary layouts. All semantically relevant
outputs must remain in the host family or `R`; this type grants no permission
to omit a changed output. Auxiliary outputs require a separate scope or
restoration argument before later code can ignore or reuse them. -/
structure PhysicalContract {H ι K A R} (e : WindowEvent H ι R)
    (B : Type b) (C : Type c) where
  original : (WindowState H ι K A R × B) → (WindowState H ι K A R × B)
  relocated : (WindowState H ι K A R × C) → (WindowState H ι K A R × C)
  original_retained : ∀ s bank, (original (s, bank)).1 = e.base s
  relocated_retained : ∀ s bank, (relocated (s, bank)).1 = e.hosted s

/-- Actual auxiliary outputs, including arbitrary changed dirt, feed the
next invocation. No resetting or replacing the bank between calls occurs. -/
inductive PhysicalImplementations {H ι K A R} (B : Type b) (C : Type c) :
    List (WindowEvent H ι R) → Type _ where
  | nil : PhysicalImplementations (K := K) (A := A) B C []
  | cons {e es} (contract : PhysicalContract (K := K) (A := A) e B C)
      (rest : PhysicalImplementations (K := K) (A := A) B C es) :
      PhysicalImplementations (K := K) (A := A) B C (e :: es)

def PhysicalImplementations.runOriginal {H ι K A R B C}
    {events : List (WindowEvent H ι R)} :
    PhysicalImplementations (K := K) (A := A) B C events →
      (WindowState H ι K A R × B) → (WindowState H ι K A R × B)
  | .nil, s => s
  | .cons contract rest, s => rest.runOriginal (contract.original s)

def PhysicalImplementations.runRelocated {H ι K A R B C}
    {events : List (WindowEvent H ι R)} :
    PhysicalImplementations (K := K) (A := A) B C events →
      (WindowState H ι K A R × C) → (WindowState H ι K A R × C)
  | .nil, s => s
  | .cons contract rest, s => rest.runRelocated (contract.relocated s)

theorem PhysicalImplementations.original_projection {H ι K A R B C}
    {events : List (WindowEvent H ι R)}
    (program : PhysicalImplementations (K := K) (A := A) B C events)
    (state : WindowState H ι K A R × B) :
    (program.runOriginal state).1 = runBase events state.1 := by
  induction program generalizing state with
  | nil => rfl
  | cons contract rest ih =>
    change (rest.runOriginal (contract.original state)).1 = runBase _ state.1
    rw [ih]
    change runBase _ (contract.original (state.1, state.2)).1 = _
    rw [contract.original_retained]
    rfl

theorem PhysicalImplementations.relocated_projection {H ι K A R B C}
    {events : List (WindowEvent H ι R)}
    (program : PhysicalImplementations (K := K) (A := A) B C events)
    (state : WindowState H ι K A R × C) :
    (program.runRelocated state).1 = runHosted events state.1 := by
  induction program generalizing state with
  | nil => rfl
  | cons contract rest ih =>
    change (rest.runRelocated (contract.relocated state)).1 = runHosted _ state.1
    rw [ih]
    change runHosted _ (contract.relocated (state.1, state.2)).1 = _
    rw [contract.relocated_retained]
    rfl

theorem physical_multi_hosting {H ι K A R B C}
    {events : List (WindowEvent H ι R)}
    (program : PhysicalImplementations (K := K) (A := A) B C events)
    (pending : HostMask H ι)
    (hd : ∀ h, DisjointMasks (residuals events h))
    (hs : ∀ h, MaskSubset (masksUnion events h) (pending h))
    (s : WindowState H ι K A R) (oldBank : B) (newBank : C) :
    onHosts (remainders pending events) (program.runRelocated (s, newBank)).1 =
      onHosts pending (program.runOriginal (s, oldBank)).1 := by
  rw [program.original_projection, program.relocated_projection]
  exact multi_hosting events pending hd hs s

theorem physical_multi_hosting_in_context {H ι K A R B C X Y}
    {events : List (WindowEvent H ι R)}
    (program : PhysicalImplementations (K := K) (A := A) B C events)
    (pending : HostMask H ι)
    (hd : ∀ h, DisjointMasks (residuals events h))
    (hs : ∀ h, MaskSubset (masksUnion events h) (pending h))
    (originalInput : X → WindowState H ι K A R × B)
    (relocatedInput : X → WindowState H ι K A R × C)
    (sameRetained : ∀ x, (originalInput x).1 = (relocatedInput x).1)
    (observe : WindowState H ι K A R → Y) (x : X) :
    observe (onHosts (remainders pending events)
        (program.runRelocated (relocatedInput x)).1) =
      observe (onHosts pending (program.runOriginal (originalInput x)).1) := by
  rw [program.original_projection, program.relocated_projection, sameRetained x]
  exact congrArg observe (multi_hosting events pending hd hs (relocatedInput x).1)

end MultiHosting

#print axioms MultiHosting.base_commutes
#print axioms MultiHosting.runBase_commutes
#print axioms MultiHosting.delay_residuals
#print axioms MultiHosting.multi_hosting
#print axioms MultiHosting.multi_hosting_in_context
#print axioms MultiHosting.PhysicalImplementations.original_projection
#print axioms MultiHosting.PhysicalImplementations.relocated_projection
#print axioms MultiHosting.physical_multi_hosting
#print axioms MultiHosting.physical_multi_hosting_in_context
