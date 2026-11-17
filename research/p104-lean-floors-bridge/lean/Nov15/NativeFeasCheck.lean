/-
NativeFeasCheck (lane LEAN-NEXT15, Nov 16): the native #7623's point x (Nov15/NativeFeasData.lean,
exported by Nov15/floorcert/export_native.py) meets the FloorCert support sub-LP. Integer checks by
kernel evaluation (`decide +kernel`; no `native_decide`, no `Lean.ofReduceBool`). Core Lean only;
the field-level bridge is in NativeFeas.lean. See FloorCert.md.
-/
import Nov15.NativeFeasData

set_option maxHeartbeats 0

namespace FloorCert

/-- add d at index i of a Braun tree (missing nodes are created with value 0); `fuel > i` suffices. -/
def ITree.upd : Nat → ITree → Nat → Int → ITree
  | 0, t, _, _ => t
  | fuel + 1, .leaf, i, d =>
    if i = 0 then .node .leaf d .leaf
    else if i % 2 = 1 then .node (ITree.upd fuel .leaf (i / 2) d) 0 .leaf
    else .node .leaf 0 (ITree.upd fuel .leaf (i / 2 - 1) d)
  | fuel + 1, .node l v r, i, d =>
    if i = 0 then .node l (v + d) r
    else if i % 2 = 1 then .node (ITree.upd fuel l (i / 2) d) v r
    else .node l v (ITree.upd fuel r (i / 2 - 1) d)

/-- add x · (column entries) into the row accumulator -/
def addEnts (x : Int) : ITree → List (Nat × Int) → ITree
  | t, [] => t
  | t, p :: l => addEnts x (ITree.upd (p.1 + 1) t p.1 (x * p.2)) l

/-- row accumulator: A·x, scanning the columns and x together -/
def accum : ITree → List (Int × List (Nat × Int)) → List Int → ITree
  | t, c :: cs, x :: xs => accum (if x = 0 then t else addEnts x t c.2) cs xs
  | t, _, _ => t

/-- every b_i ≤ (A·x)_i, scanning b from index i -/
def rowsGe (t : ITree) : List Int → Nat → Bool
  | [], _ => true
  | b :: bs, i => decide (b ≤ t.get i) && rowsGe t bs (i + 1)

/-- cᵀx, accumulated at index 0 of a tree (zero columns skipped, so the kernel's lazy sum stays shallow) -/
def costAcc : ITree → List (Int × List (Nat × Int)) → List Int → ITree
  | t, c :: cs, x :: xs => costAcc (if x = 0 then t else ITree.upd 1 t 0 (c.1 * x)) cs xs
  | t, _, _ => t

/-- A·x on the support rows -/
def nativeAx : ITree := accum .leaf colList xList

/-! ## The integer checks -/

theorem xlen_ok : xList.length = nCols := by decide +kernel

theorem x_nonneg_ok : xList.all (fun v => decide (0 ≤ v)) = true := by decide +kernel

theorem obj_ok : (costAcc .leaf colList xList).get 0 = nativeObj := by decide +kernel

theorem rows_ok : rowsGe nativeAx bList 0 = true := by decide +kernel

end FloorCert

#print axioms FloorCert.xlen_ok
#print axioms FloorCert.x_nonneg_ok
#print axioms FloorCert.obj_ok
#print axioms FloorCert.rows_ok
