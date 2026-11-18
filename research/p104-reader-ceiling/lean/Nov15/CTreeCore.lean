/-! CTreeCore: Row structure and kernel-checkable DP certificate conditions (Lean core only).
Data and kernel check for the CongestionTree DP certificates (no imports; Lean core only). -/
namespace CTree

/-- one shape (dim, n, m) of the 230-shape DAG with its certificate rows; `i` is the shape's label in `shapes.txt`,
`mask` the bit-set of allowed child labels, `g` the table G(x, k), `ge` the table Ge(x, j) (min over allowed children). -/
structure Row where
  i : Nat
  dim : Nat
  n : Nat
  m : Nat
  mask : Nat
  g : List Nat
  ge : List Nat

def Row.ok (r r' : Row) : Bool :=
  decide (r.dim < r'.dim) && decide (r.n ≤ r'.n) && decide (r'.m ≤ r.m) && ((r.mask >>> r'.i) % 2 == 1)

def ew (W : List (List Nat)) (r r' : Row) : Nat := ((W.getD r.dim []).getD r'.dim 0) / r.n

def rowLe : List Nat → List Nat → Nat → Bool
  | a :: as, b :: bs, w => decide (a ≤ w + b) && rowLe as bs w
  | _, _, _ => true

def monoB : List Nat → Bool
  | a :: b :: t => decide (a ≤ b) && monoB (b :: t)
  | _ => true

def Row.c4 (r : Row) : Bool :=
  (List.range r.m).all (fun k => (List.range (k + 1)).all (fun j =>
    decide (r.g.getD (k + 1) 0 ≤ r.ge.getD (j + 1) 0 + r.g.getD (k - j) 0)))

def Row.check (W : List (List Nat)) (rs : List Row) (r : Row) : Bool :=
  decide (1 ≤ r.dim) && decide (r.dim ≤ 8) && decide (1 ≤ r.n) && (r.g.length == r.m + 1) && (r.ge.length == r.m + 1)
  && (r.g.getD 0 0 == 0) && monoB r.g
  && (if r.dim == 8 then decide (r.m ≤ 1) && r.g.all (fun v => v == 0)
      else rs.all (fun r' => !(r.ok r') || rowLe (r.ge.drop 1) (r'.g.drop 1) (ew W r r')) && r.c4)

end CTree
