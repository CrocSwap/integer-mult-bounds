import MultiHosting
import PhysicalHosting

/-!
Exact recovery of the previous one-host theorems from `MultiHosting`.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.

The singleton embedding keeps the entire retained state. Its inverse shows
that the multi-host theorem specializes to the old theorem without dropping
any observations. The proof below calls the new `multi_hosting` theorem,
not the old `WholeHosting.whole_hosting` theorem. The physical corollary
uses the old adapter's independently proved projection lemmas, which thread
actual auxiliary-bank outputs and quantify over every dirty input.

This compatibility result supplies no source-program endpoint contract.
-/
namespace MultiHosting.SingleHost

def embed {ι K A R} (s : WholeHosting.WindowState ι K A R) :
    MultiHosting.WindowState Unit ι K A R :=
  (fun _ => s.1, s.2)

def collapse {ι K A R} (s : MultiHosting.WindowState Unit ι K A R) :
    WholeHosting.WindowState ι K A R :=
  (s.1 (), s.2)

theorem collapse_embed {ι K A R} (s : WholeHosting.WindowState ι K A R) :
    collapse (embed s) = s := by
  rfl

theorem embed_collapse {ι K A R} (s : MultiHosting.WindowState Unit ι K A R) :
    embed (collapse s) = s := by
  apply Prod.ext
  · funext h
    cases h
    rfl
  · rfl

def event {ι R} (e : WholeHosting.WindowEvent ι R) :
    MultiHosting.WindowEvent Unit ι R :=
  { idle := fun _ => e.idle
    residual := fun _ => e.residual
    other := e.other }

theorem collapse_onHosts {ι K A R} (p : MultiHosting.HostMask Unit ι)
    (s : MultiHosting.WindowState Unit ι K A R) :
    collapse (MultiHosting.onHosts p s) = WholeHosting.onHost (p ()) (collapse s) := by
  rfl

theorem collapse_base {ι K A R} (e : WholeHosting.WindowEvent ι R)
    (s : MultiHosting.WindowState Unit ι K A R) :
    collapse ((event e).base s) = e.base (collapse s) := by
  rfl

theorem collapse_hosted {ι K A R} (e : WholeHosting.WindowEvent ι R)
    (s : MultiHosting.WindowState Unit ι K A R) :
    collapse ((event e).hosted s) = e.hosted (collapse s) := by
  rfl

theorem collapse_runBase {ι K A R} (events : List (WholeHosting.WindowEvent ι R))
    (s : MultiHosting.WindowState Unit ι K A R) :
    collapse (MultiHosting.runBase (events.map event) s) =
      WholeHosting.runBase events (collapse s) := by
  induction events generalizing s with
  | nil => rfl
  | cons e es ih =>
    change collapse (MultiHosting.runBase (es.map event) ((event e).base s)) = _
    rw [ih, collapse_base]
    rfl

theorem collapse_runHosted {ι K A R} (events : List (WholeHosting.WindowEvent ι R))
    (s : MultiHosting.WindowState Unit ι K A R) :
    collapse (MultiHosting.runHosted (events.map event) s) =
      WholeHosting.runHosted events (collapse s) := by
  induction events generalizing s with
  | nil => rfl
  | cons e es ih =>
    change collapse (MultiHosting.runHosted (es.map event) ((event e).hosted s)) = _
    rw [ih, collapse_hosted]
    rfl

theorem residuals_event {ι R} (events : List (WholeHosting.WindowEvent ι R)) (h : Unit) :
    MultiHosting.residuals (events.map event) h = WholeHosting.residuals events := by
  induction events with
  | nil => rfl
  | cons e es ih =>
    change e.residual :: MultiHosting.residuals (es.map event) h =
      e.residual :: WholeHosting.residuals es
    rw [ih]

/-- The exact statement of `WholeHosting.whole_hosting`, derived from the
multi-host theorem by an invertible singleton-host change of state space. -/
theorem whole_hosting_recovered {ι K A R} (events : List (WholeHosting.WindowEvent ι R))
    (pending : WholeHosting.Mask ι)
    (hd : WholeHosting.DisjointMasks (WholeHosting.residuals events))
    (hs : WholeHosting.MaskSubset (WholeHosting.maskUnion (WholeHosting.residuals events)) pending)
    (s : WholeHosting.WindowState ι K A R) :
    WholeHosting.onHost
        (WholeHosting.remainderMask pending (WholeHosting.maskUnion (WholeHosting.residuals events)))
        (WholeHosting.runHosted events s) =
      WholeHosting.onHost pending (WholeHosting.runBase events s) := by
  have hd' : ∀ h, WholeHosting.DisjointMasks (MultiHosting.residuals (events.map event) h) := by
    intro h
    simpa only [residuals_event] using hd
  have hs' : ∀ h, WholeHosting.MaskSubset
      (MultiHosting.masksUnion (events.map event) h) pending := by
    intro h
    simpa only [MultiHosting.masksUnion, residuals_event] using hs
  have equality := MultiHosting.multi_hosting (events.map event) (fun _ => pending) hd' hs' (embed s)
  have projected := congrArg collapse equality
  simpa only [collapse_onHosts, MultiHosting.remainders, MultiHosting.masksUnion,
    residuals_event, collapse_runHosted, collapse_runBase, collapse_embed] using projected

/-- The exact previous physical theorem also follows. No auxiliary output
is reset between invocations; the existing projection lemmas establish that
the actual original and relocated banks are threaded through each word. -/
theorem physical_whole_hosting_recovered {ι K A R B C}
    {events : List (WholeHosting.WindowEvent ι R)}
    (program : WholeHosting.PhysicalImplementations (K := K) (A := A) B C events)
    (pending : WholeHosting.Mask ι)
    (hd : WholeHosting.DisjointMasks (WholeHosting.residuals events))
    (hs : WholeHosting.MaskSubset (WholeHosting.maskUnion (WholeHosting.residuals events)) pending)
    (s : WholeHosting.WindowState ι K A R) (oldBank : B) (newBank : C) :
    WholeHosting.onHost
        (WholeHosting.remainderMask pending (WholeHosting.maskUnion (WholeHosting.residuals events)))
        (program.runRelocated (s, newBank)).1 =
      WholeHosting.onHost pending (program.runOriginal (s, oldBank)).1 := by
  rw [program.original_projection, program.relocated_projection]
  exact whole_hosting_recovered events pending hd hs s

end MultiHosting.SingleHost

#print axioms MultiHosting.SingleHost.collapse_embed
#print axioms MultiHosting.SingleHost.embed_collapse
#print axioms MultiHosting.SingleHost.collapse_onHosts
#print axioms MultiHosting.SingleHost.collapse_base
#print axioms MultiHosting.SingleHost.collapse_hosted
#print axioms MultiHosting.SingleHost.collapse_runBase
#print axioms MultiHosting.SingleHost.collapse_runHosted
#print axioms MultiHosting.SingleHost.residuals_event
#print axioms MultiHosting.SingleHost.whole_hosting_recovered
#print axioms MultiHosting.SingleHost.physical_whole_hosting_recovered
