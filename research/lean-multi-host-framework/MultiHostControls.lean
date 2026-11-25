import MultiHosting

/-!
Boundary controls for the multi-host framework. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

These small models are not source providers. They show why retaining every
host does not permit arbitrary host mixing, and why distinct abstract host
indices must refine to distinct physical streams.
-/
namespace MultiHosting.Controls
open WholeHosting

def full : Mask Unit := fun _ => true
def firstOnly : HostMask Bool Unit := fun h _ => !h
def both : HostMask Bool Unit := fun _ => full
def address : Address Unit Bool := fun _ => (false, true)
def value : Stream Unit Bool Bool := fun a => (a ()).1

def initial : MultiHosting.WindowState Bool Unit Bool Bool Unit :=
  (fun h => if h then fun _ => false else value, ())

/-- A genuine cross-host XOR, outside the product endpoint interface. -/
def mixHosts (s : MultiHosting.WindowState Bool Unit Bool Bool Unit) :
    MultiHosting.WindowState Bool Unit Bool Bool Unit :=
  (fun h => if h then fun a => s.1 true a ^^ s.1 false a else s.1 false, s.2)

theorem mixing_does_not_commute :
    mixHosts (onHosts firstOnly initial) ≠ onHosts firstOnly (mixHosts initial) := by
  intro equality
  have observation := congrArg
    (fun s : MultiHosting.WindowState Bool Unit Bool Bool Unit => s.1 true address)
    equality
  change true = false at observation
  cases observation

/-- An invalid ownership interpretation: both abstract hosts are views of
the same physical stream. A source owner-injectivity proof must exclude it. -/
def aliasedView (s : Stream Unit Bool Bool) :
    MultiHosting.WindowState Bool Unit Bool Bool Unit := (fun _ => s, ())

def aliasedPhysicalRun (s : Stream Unit Bool Bool) : Stream Unit Bool Bool :=
  bitAction full (bitAction full s)

/-- Each nominal host receives one residual in the abstract endpoint, but
the actual aliased stream receives both, so the abstract endpoint is wrong. -/
theorem alias_breaks_refinement :
    onHosts both (aliasedView value) ≠ aliasedView (aliasedPhysicalRun value) := by
  intro equality
  have observation := congrArg
    (fun s : MultiHosting.WindowState Bool Unit Bool Bool Unit => s.1 false address)
    equality
  change true = false at observation
  cases observation

end MultiHosting.Controls

#print axioms MultiHosting.Controls.mixing_does_not_commute
#print axioms MultiHosting.Controls.alias_breaks_refinement
