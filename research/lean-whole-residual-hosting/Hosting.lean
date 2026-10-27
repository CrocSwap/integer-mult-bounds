import CoordinateSwap

/-!
Whole-residual absorption through a window of COMPLETE invocation endpoints.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.

This proves the bit operator step in PR442 PROOF.md §2, conditional on its
inherited complete dirty-invocation endpoint and owner/chart interfaces.
The host is ONE whole stream. `R` contains all other retained live state,
including every scratch component whose endpoint is to be compared. The
original and relocated layouts may have different auxiliary banks; this
module compares their common retained-state projections. PhysicalHosting
provides the projection adapter with universal auxiliary-input contracts. No operation in `other` can read the host. Temporary
reads inside a complete invocation are allowed by `EndpointContract` if its
full endpoint has the stated product form on every input.

All coordinate masks in a window use one common address chart. An idle
factor may act on the host between invocations; the proof commutes it past
hosted residuals rather than claiming the host is untouched.
-/
namespace WholeHosting

abbrev WindowState (ι : Type u) (K : Type v) (A : Type w) (R : Type z) :=
  Stream ι K A × R

/-- One complete macro endpoint. For a local invocation `idle` is empty;
for an intervening idle child `residual` is empty. Allowing both gives a
convenient closed representation without assuming primitive-gate locality. -/
structure WindowEvent (ι : Type u) (R : Type z) where
  idle : Mask ι
  residual : Mask ι
  other : R → R

def onHost {ι K A R} (mask : Mask ι) (s : WindowState ι K A R) : WindowState ι K A R :=
  (bitAction mask s.1, s.2)

def WindowEvent.base {ι K A R} (e : WindowEvent ι R)
    (s : WindowState ι K A R) : WindowState ι K A R :=
  (bitAction e.idle s.1, e.other s.2)

def WindowEvent.hosted {ι K A R} (e : WindowEvent ι R)
    (s : WindowState ι K A R) : WindowState ι K A R :=
  onHost e.residual (e.base s)

/-- Full endpoint contracts, for arbitrary and possibly correlated dirt.
The functions here are retained endpoint maps. These are premises to
instantiate from an actual physical provider, not axioms or consequences of
the template's combinatorial slot check. Their common `other` map must hold
for every auxiliary-bank input; old and relocated banks need not be the
same state space. Scratch restoration is only as strong as `other` specifies. -/
structure EndpointContract {ι K A R} (e : WindowEvent ι R) where
  original : WindowState ι K A R → WindowState ι K A R
  relocated : WindowState ι K A R → WindowState ι K A R
  original_spec : ∀ s, original s = e.base s
  relocated_spec : ∀ s, relocated s = e.hosted s

def runBase {ι K A R} : List (WindowEvent ι R) → WindowState ι K A R → WindowState ι K A R
  | [], s => s
  | e :: es, s => runBase es (e.base s)

def runHosted {ι K A R} : List (WindowEvent ι R) → WindowState ι K A R → WindowState ι K A R
  | [], s => s
  | e :: es, s => runHosted es (e.hosted s)

def residuals {ι R} (events : List (WindowEvent ι R)) : List (Mask ι) :=
  events.map WindowEvent.residual

def allOnHost {ι K A R} (masks : List (Mask ι))
    (s : WindowState ι K A R) : WindowState ι K A R :=
  (bitFactors masks s.1, s.2)

/-- Product endpoint independence plus same-chart coordinate commutation:
merely preserving the host component would not suffice for this equation. -/
theorem base_commutes {ι K A R} (e : WindowEvent ι R) (p : Mask ι)
    (s : WindowState ι K A R) : e.base (onHost p s) = onHost p (e.base s) := by
  apply Prod.ext
  · exact bitAction_commute p e.idle s.1
  · rfl

theorem runBase_commutes {ι K A R} (events : List (WindowEvent ι R))
    (p : Mask ι) (s : WindowState ι K A R) :
    runBase events (onHost p s) = onHost p (runBase events s) := by
  induction events generalizing s with
  | nil => rfl
  | cons e es ih =>
    change runBase es (e.base (onHost p s)) = onHost p (runBase es (e.base s))
    rw [base_commutes, ih]

/-- Move every hosted residual to the end of the window without changing
its order. The proof is over arbitrary finite windows and arbitrary arrays. -/
theorem delay_residuals {ι K A R} (events : List (WindowEvent ι R))
    (s : WindowState ι K A R) :
    runHosted events s = allOnHost (residuals events) (runBase events s) := by
  induction events generalizing s with
  | nil => rfl
  | cons e es ih =>
    change runHosted es (onHost e.residual (e.base s)) =
      allOnHost (e.residual :: residuals es) (runBase es (e.base s))
    rw [ih, runBase_commutes]
    rfl

/-- The whole-hosting operator lemma. Complete invocations plus any
intervening same-chart idle factors, followed by the exact remainder child,
equal the original window followed by the entire pending child. -/
theorem whole_hosting {ι K A R} (events : List (WindowEvent ι R))
    (pending : Mask ι) (hd : DisjointMasks (residuals events))
    (hs : MaskSubset (maskUnion (residuals events)) pending)
    (s : WindowState ι K A R) :
    onHost (remainderMask pending (maskUnion (residuals events))) (runHosted events s) =
      onHost pending (runBase events s) := by
  rw [delay_residuals]
  apply Prod.ext
  · exact bitFactors_complete pending (residuals events) hd hs (runBase events s).1
  · rfl

/-- Prefixes and suffixes may mix all live state arbitrarily. Universality
of the window equality is what permits composition and correlated inputs. -/
theorem whole_hosting_in_context {ι K A R X Y}
    (events : List (WindowEvent ι R)) (pending : Mask ι)
    (hd : DisjointMasks (residuals events))
    (hs : MaskSubset (maskUnion (residuals events)) pending)
    (before : X → WindowState ι K A R) (after : WindowState ι K A R → Y) (x : X) :
    after (onHost (remainderMask pending (maskUnion (residuals events)))
      (runHosted events (before x))) =
      after (onHost pending (runBase events (before x))) :=
  congrArg after (whole_hosting events pending hd hs (before x))

/-- A chronological list of actual complete implementations, one contract
per event; the implementation may use and restore temporary dirty scratch. -/
inductive Implementations {ι K A R} : List (WindowEvent ι R) → Type _ where
  | nil : Implementations (K := K) (A := A) []
  | cons {e es} (contract : EndpointContract (K := K) (A := A) e)
      (rest : Implementations (K := K) (A := A) es) :
      Implementations (K := K) (A := A) (e :: es)

def Implementations.runOriginal {ι K A R} {events : List (WindowEvent ι R)} :
    Implementations (K := K) (A := A) events → WindowState ι K A R → WindowState ι K A R
  | .nil, s => s
  | .cons contract rest, s => rest.runOriginal (contract.original s)

def Implementations.runRelocated {ι K A R} {events : List (WindowEvent ι R)} :
    Implementations (K := K) (A := A) events → WindowState ι K A R → WindowState ι K A R
  | .nil, s => s
  | .cons contract rest, s => rest.runRelocated (contract.relocated s)

theorem Implementations.original_eq {ι K A R} {events : List (WindowEvent ι R)}
    (program : Implementations (K := K) (A := A) events) (s : WindowState ι K A R) :
    program.runOriginal s = runBase events s := by
  induction program generalizing s with
  | nil => rfl
  | cons contract rest ih =>
    change rest.runOriginal (contract.original s) = runBase _ (_)
    rw [contract.original_spec, ih]
    rfl

theorem Implementations.relocated_eq {ι K A R} {events : List (WindowEvent ι R)}
    (program : Implementations (K := K) (A := A) events) (s : WindowState ι K A R) :
    program.runRelocated s = runHosted events s := by
  induction program generalizing s with
  | nil => rfl
  | cons contract rest ih =>
    change rest.runRelocated (contract.relocated s) = runHosted _ (_)
    rw [contract.relocated_spec, ih]
    rfl

/-- The result for supplied implementations rather than only symbolic
endpoints. Instantiating the contracts for a source word remains mandatory. -/
theorem implementation_whole_hosting {ι K A R} {events : List (WindowEvent ι R)}
    (program : Implementations (K := K) (A := A) events) (pending : Mask ι)
    (hd : DisjointMasks (residuals events))
    (hs : MaskSubset (maskUnion (residuals events)) pending) (s : WindowState ι K A R) :
    onHost (remainderMask pending (maskUnion (residuals events))) (program.runRelocated s) =
      onHost pending (program.runOriginal s) := by
  rw [program.original_eq, program.relocated_eq]
  exact whole_hosting events pending hd hs s

end WholeHosting

#print axioms WholeHosting.base_commutes
#print axioms WholeHosting.runBase_commutes
#print axioms WholeHosting.delay_residuals
#print axioms WholeHosting.whole_hosting
#print axioms WholeHosting.whole_hosting_in_context
#print axioms WholeHosting.Implementations.original_eq
#print axioms WholeHosting.Implementations.relocated_eq
#print axioms WholeHosting.implementation_whole_hosting
