/-
FloorCert definitions . Core Lean only, so the generated data file
Nov15/FloorCertData.lean elaborates cheaply. See FloorCert.md.
-/

namespace FloorCert

/-- Integer Braun tree: index 0 at the root, odd i ↦ left subtree at (i-1)/2, even i > 0 ↦ right
subtree at (i-2)/2. Missing indices read 0. Used for O(log n) kernel lookups of the dual. -/
inductive ITree where
  | leaf : ITree
  | node : ITree → Int → ITree → ITree

def ITree.get : ITree → Nat → Int
  | .leaf, _ => 0
  | .node l v r, i => if i = 0 then v else if i % 2 = 1 then l.get (i / 2) else r.get (i / 2 - 1)

/-- Sparse column dot product Σ_{(i,a) ∈ l} Y(i)·a in ℤ. -/
def colDot (Y : Nat → Int) (l : List (Nat × Int)) : Int := (l.map fun p => Y p.1 * p.2).sum

/-- One column check: all row indices < R, and Σ Y(i)·a ≤ den · cost. -/
def colOK (R : Nat) (Y : Nat → Int) (den : Int) (c : Int × List (Nat × Int)) : Bool :=
  c.2.all (fun p => decide (p.1 < R)) && decide (colDot Y c.2 ≤ den * c.1)

/-- Σ_{i < bs.length} Y(i)·b_i, scanning bs from index i0. -/
def bDot (Y : Nat → Int) : List Int → Nat → Int
  | [], _ => 0
  | b :: bs, i => Y i * b + bDot Y bs (i + 1)

end FloorCert
