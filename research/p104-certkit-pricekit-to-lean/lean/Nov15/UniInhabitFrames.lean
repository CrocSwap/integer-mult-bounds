/-
UniInhabitFrames (lane UNI-INHABIT, Nov 19).  frameOK: closure certificate of a 512-bit frame mask.  Core Lean only.
-/
import Nov15.UniInhabitTabs

namespace UniInhabit

/-- xor-reduction by a basis (any deterministic choice b' ∈ {b, b ^^^ g} is sound). -/
def red : List Nat → Nat → Nat
  | [], v => v
  | g :: G, v => red G (cond (Nat.blt (v ^^^ g) v) (v ^^^ g) v)

/-- closure certificate: 0 ∈ S, S ⊆ [0,512), S closed under ^^^ g (g ∈ G), every v ∈ S reduces to 0 by G. -/
def frameOK (m : Nat) (G : List Nat) : Bool :=
  Nat.testBit m 0 && Nat.blt m (2 ^ 512) &&
  (List.range 512).all (fun v => !Nat.testBit m v || (G.all (fun g => Nat.testBit m (v ^^^ g)) && Nat.beq (red G v) 0))

end UniInhabit
