import PhysicalHosting

/-!
A nonempty example of the physical projection adapter. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

This is a toy validation of the interface, not a repository source provider.
One whole-stream residual precedes an idle factor on that stream. The old
auxiliary layout is Int, the relocated layout is Bool, and both banks change.
Each complete retained endpoint is independent of every auxiliary input.
The real auxiliary outputs persist into the second call. Their equality or
restoration is not claimed, and this example assigns no implementation cost.
-/

namespace WholeHosting.PhysicalExample

abbrev State := WindowState Unit Bool Bool Int

def first : WindowEvent Unit Int :=
  { idle := fun _ => false, residual := fun _ => true, other := fun n => n + 1 }

def second : WindowEvent Unit Int :=
  { idle := fun _ => true, residual := fun _ => false, other := fun n => n + 1 }

def contract (e : WindowEvent Unit Int) :
    PhysicalContract (K := Bool) (A := Bool) e Int Bool where
  original := fun state => (e.base state.1, state.2 + state.1.2)
  relocated := fun state => (e.hosted state.1, !state.2)
  original_retained := fun _ _ => rfl
  relocated_retained := fun _ _ => rfl

def program : PhysicalImplementations (K := Bool) (A := Bool) Int Bool [first, second] :=
  .cons (contract first) (.cons (contract second) .nil)

/-- The second invocation receives the first invocation's changed old bank. -/
theorem old_output_is_threaded (s : State) (bank : Int) :
    (program.runOriginal (s, bank)).2 = (bank + s.2) + (s.2 + 1) := rfl

/-- The relocated bank is threaded in its own, different state space. -/
theorem relocated_output_is_threaded (s : State) (bank : Bool) :
    (program.runRelocated (s, bank)).2 = !(!bank) := rfl

/-- A nonempty hosted residual is absorbed for every retained stream and
every pair of old/new auxiliary inputs, without matching or clearing them. -/
theorem absorption (s : State) (oldBank : Int) (newBank : Bool) :
    onHost (remainderMask (fun _ => true) (maskUnion (residuals [first, second])))
        (program.runRelocated (s, newBank)).1 =
      onHost (fun _ => true) (program.runOriginal (s, oldBank)).1 := by
  apply physical_whole_hosting
  · simp [residuals, DisjointMasks, MasksDisjoint, maskUnion, unionMask, first, second]
  · simp [residuals, MaskSubset, maskUnion, unionMask, first, second]

end WholeHosting.PhysicalExample

#print axioms WholeHosting.PhysicalExample.old_output_is_threaded
#print axioms WholeHosting.PhysicalExample.relocated_output_is_threaded
#print axioms WholeHosting.PhysicalExample.absorption
