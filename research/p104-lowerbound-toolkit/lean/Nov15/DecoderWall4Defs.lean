import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.Data.Fin.VecNotation
import Nov15.DecoderWall4Data

open Matrix

namespace DW4
set_option maxHeartbeats 0

def lab (i : ℕ) : ℕ := labs.getD i 0
def g (i j : ℕ) : ℤ := (((gramRows.getD i 0 >>> (2 * j)) &&& 3 : ℕ) : ℤ) - 1
def dotb (a b : ℕ) : Bool := ((List.range 9).filter fun k => a.testBit k && b.testBit k).length % 2 == 1

def portOf (k i : ℕ) : ℕ := (catPorts.getD k 0 >>> (7 * i)) &&& 127
def xOf (k i j : ℕ) : ℤ := (((catX.getD k 0 >>> (9 * (8 * i + j))) &&& 511 : ℕ) : ℤ) - 256
def dOf (k : ℕ) : ℤ := (catD.getD k 0 : ℕ)

/-- Catalog entry `k`: ports `P` (< 104), `G[P,P]·X = d·I`, `d ≠ 0`. -/
def catOK (k : ℕ) : Prop :=
  dOf k ≠ 0 ∧ (∀ i : Fin 8, portOf k i < 104) ∧
  ∀ i j : Fin 8, ∑ l : Fin 8, g (portOf k i) (portOf k l) * xOf k l j = if (i : ℕ) = j then dOf k else 0

instance (k : ℕ) : Decidable (catOK k) := by unfold catOK; infer_instance


end DW4
