import Lean
import Mathlib.Algebra.Group.Nat.Defs
import Mathlib.Tactic.SplitIfs

/-! Exact five list definitions extracted from the published PR64 RippleCounter.
No tape execution or new counter/potential proof is included. The original
source and current-main publication manifest are retained by the correspondence
audit; this module must not be jointly imported with the original RippleCounter. -/
namespace RippleCounter

def carryLength (d : Bool) : List Bool → ℕ
  | [] => 0
  | b::rest => if b = d then carryLength d rest + 1 else 0

def stopTail (d : Bool) : List Bool → List Bool
  | [] => []
  | b::rest => if b = d then stopTail d rest else (!b) :: rest

def overflow (d : Bool) : List Bool → Bool
  | [] => true
  | b::rest => if b = d then overflow d rest else false

def updated (d : Bool) (bits : List Bool) : List Bool :=
  List.replicate (carryLength d bits) (!d) ++ stopTail d bits

def steps (d : Bool) (bits : List Bool) : ℕ := 2 * carryLength d bits + 2

end RippleCounter
