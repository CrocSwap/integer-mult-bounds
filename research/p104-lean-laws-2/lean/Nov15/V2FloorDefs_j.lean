import Nov15.V2FloorData

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace V2Floor
open Finset

def LBj (p : Fin N_joint) : List ℕ := (D_joint.get p.val).1
def UHj (p : Fin N_joint) : List ℕ := (D_joint.get p.val).2.1
def numj (p : Fin N_joint) (k : ℕ) : ℕ := (D_joint.get p.val).2.2.getD k 0

/-- the per-pair side conditions (L, U nondegenerate; levels in range; 9 levels). -/
def okj (i : ℕ) : Bool :=
  let d := D_joint.get i
  (d.1 != []) && decide (vec (d.1.headD 0) ≠ 0) && (d.2.1 != []) &&
  (List.finRange 9).any (fun j => decide (vec (d.2.1.headD 0) j = 1)) &&
  (d.2.2.length == 9) &&
  (List.range 9).all (fun k => d.2.2.getD k 0 == 0 || (d.1.length ≤ k && k < 9 - d.2.1.length))

/-- Σ_{lo ≤ i < lo+n} Σ_k num i k, by recursion. -/
def tsumj (lo : ℕ) : ℕ → ℕ
  | 0 => 0
  | n + 1 => tsumj lo n + ∑ k ∈ Finset.range 9, (D_joint.get (lo + n)).2.2.getD k 0

end V2Floor
