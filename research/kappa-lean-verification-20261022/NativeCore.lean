import Std

/-!
Finite, executable native-frame certificate.  This file deliberately does not
model amplitudes, Clifford phases, or the free noncommutative endpoint algebra.
All checks below use ordinary kernel reduction, never `native_decide`.
-/
namespace NativeCertificate

abbrev Basis := Array Nat

/-- A balanced tree avoids quadratic reduction of long array-literal lookups.
The stored left size is checked once for each source catalogue/state. -/
inductive Table (α : Type) where
  | empty
  | leaf (value : α)
  | branch (leftSize : Nat) (left right : Table α)
  deriving Inhabited, Repr, BEq

namespace Table
def size : Table α → Nat
  | .empty => 0
  | .leaf _ => 1
  | .branch n _ r => n + r.size

def wellFormed : Table α → Bool
  | .empty | .leaf _ => true
  | .branch n l r => n == l.size && l.wellFormed && r.wellFormed

def get [Inhabited α] : Table α → Nat → α
  | .empty, _ => default
  | .leaf v, i => if i == 0 then v else default
  | .branch n l r, i => if i < n then l.get i else r.get (i-n)

def set : Table α → Nat → α → Table α
  | .empty, _, _ => .empty
  | .leaf x, i, v => if i == 0 then .leaf v else .leaf x
  | .branch n l r, i, v =>
    if i < n then .branch n (l.set i v) r else .branch n l (r.set (i-n) v)

def toList : Table α → List α
  | .empty => []
  | .leaf v => [v]
  | .branch _ l r => l.toList ++ r.toList
end Table

def combination (basis : Basis) (mask : Nat) : Nat :=
  (basis.toList.zipIdx).foldl
    (fun acc (v, i) => if (mask / 2^i) % 2 == 1 then Nat.xor acc v else acc) 0

/-- Independence over F₂, expressed by its complete finite coefficient domain. -/
def independent (basis : Basis) : Bool :=
  basis.size ≤ 9 && basis.all (· < 512) &&
  (List.range (2^basis.size)).all (fun mask => mask == 0 || combination basis mask != 0)

structure CheckedBasis where
  data : Basis
  valid : independent data = true

/-- A coordinate witness for every source generator in the destination span. -/
def embeds (src dst : Basis) (coordinates : Array Nat) : Bool :=
  coordinates.size == src.size &&
  (src.toList.zipIdx).all (fun (v, i) =>
    coordinates[i]! < 2^dst.size && combination dst coordinates[i]! == v)

structure Paid where
  input : Nat
  output : Nat
  rank : Nat
  /-- True for an ascending borrowed edge; false for a descending owned edge. -/
  ascending : Bool
  coordinates : Array Nat
  deriving Inhabited, Repr

def checkPaid (frames : Table Basis) (e : Paid) : Bool :=
  e.input < frames.size && e.output < frames.size && e.rank > 0 &&
  let a := frames.get e.input
  let b := frames.get e.output
  if e.ascending then
    a.size + e.rank == b.size && embeds a b e.coordinates
  else
    b.size + e.rank == a.size && embeds b a e.coordinates

structure CheckedPaid (frames : Table Basis) where
  data : Paid
  valid : checkPaid frames data = true

structure Operator where
  columns : Basis
  inverse : Basis
  oldColumns : Basis
  deriving Inhabited, Repr

def checkOperator (g : Operator) : Bool :=
  g.columns.size == 9 && g.inverse.size == 9 &&
  g.columns.all (· < 512) && g.inverse.all (· < 512) &&
  (List.range 512).all (fun v =>
    combination g.inverse (combination g.columns v) == v &&
    combination g.columns (combination g.inverse v) == v)

structure CheckedOperator where
  data : Operator
  valid : checkOperator data = true

structure Warp where
  operator : Int
  input : Nat
  output : Nat
  /-- Coordinates of mapped input generators in the output basis. -/
  forwardCoordinates : Array Nat
  /-- Coordinates of inverse-mapped output generators in the input basis. -/
  inverseCoordinates : Array Nat
  deriving Inhabited, Repr

def checkWarp (frames : Table Basis) (ops : Table Operator) (w : Warp) : Bool :=
  w.operator != 0 && w.operator.natAbs ≤ ops.size &&
  w.input < frames.size && w.output < frames.size &&
  let g := ops.get (w.operator.natAbs - 1)
  let direct := if w.operator > 0 then g.columns else g.inverse
  let inverse := if w.operator > 0 then g.inverse else g.columns
  let a := frames.get w.input
  let b := frames.get w.output
  a.size == b.size &&
  embeds (a.map (combination direct)) b w.forwardCoordinates &&
  embeds (b.map (combination inverse)) a w.inverseCoordinates

structure CheckedWarp (frames : Table Basis) (ops : Table Operator) where
  data : Warp
  valid : checkWarp frames ops data = true

/-- Numeric projection of an emitted event; no scalar coefficient is discarded.
kind: 0 marker, 1 climb, 2 center, 3 warp, 4 add, 5 scale, 6 clear,
7 copy, 8 adapter.  Persistent roles are 0..631; owned C₀ is role632.
reference indexes the paid or warp catalogue where applicable.
-/
structure Event where
  kind : Nat
  role : Nat
  source : Nat
  input : Nat
  output : Nat
  reference : Nat
  operator : Int
  numerator : Int
  denominator : Int
  deriving Inhabited, Repr

def bitLength : Nat → Nat → Nat
  | 0, _ => 0
  | _ + 1, 0 => 0
  | fuel + 1, n => 1 + bitLength fuel (n / 2)

def bitCount : Nat → Nat → Nat
  | 0, _ => 0
  | fuel + 1, n => n % 2 + bitCount fuel (n / 2)

def powerTwo (n : Nat) : Bool := n > 0 && Nat.land n (n - 1) == 0

def scalarValid (e : Event) : Bool :=
  e.numerator != 0 && powerTwo e.denominator.natAbs &&
  e.numerator.natAbs < 65536 && e.denominator.natAbs < 65536 &&
  (e.kind != 5 || powerTwo (e.numerator.natAbs / Nat.gcd e.numerator.natAbs e.denominator.natAbs))

/-- The exact conservative real-primitive tariff of the retained native code. -/
def scalarAllowance (e : Event) : Nat :=
  if e.kind == 6 || e.kind == 7 then 2 else
  let gcd := Nat.gcd e.numerator.natAbs e.denominator.natAbs
  let numerator := e.numerator.natAbs / gcd
  let denominator := e.denominator.natAbs / gcd
  let n := bitLength 16 numerator
  let d := bitLength 16 denominator
  if e.kind == 5 then
    2 * (n - d + (d - n) + if e.numerator * e.denominator < 0 then 1 else 0)
  else 2 * (3 + (n - 1) + bitCount 16 numerator + (d - 1))

structure State where
  frames : Table Nat
  paid : Array Nat := #[0,0,0,0,0,0,0,0,0,0]
  scalarCost : Nat := 0
  ok : Bool := true
  deriving Inhabited, Repr

def step (frameData : Table Basis) (paidData : Table Paid)
    (warpData : Table Warp) (s : State) (e : Event) : State := Id.run do
  let mut t := s
  if e.kind == 0 || e.kind == 8 then return t
  t := { t with ok := t.ok && e.role < 633 && e.input < frameData.size }
  if e.kind == 1 || e.kind == 2 then
    let p := paidData.get e.reference
    t := { t with
      ok := t.ok && e.reference < paidData.size &&
      p.input == e.input && p.output == e.output &&
      (e.kind != 1 || (e.role < 632 && p.ascending)) &&
      (e.kind != 2 || e.role == 632) && t.frames.get e.role == e.input && p.rank < 10
      frames := t.frames.set e.role e.output
      paid := t.paid.set! p.rank (t.paid[p.rank]! + 1) }
  else if e.kind == 3 then
    let w := warpData.get e.reference
    t := { t with
      ok := t.ok && e.reference < warpData.size &&
      w.input == e.input && w.output == e.output && w.operator == e.operator &&
      t.frames.get e.role == e.input
      frames := t.frames.set e.role e.output }
  else if e.kind == 6 then
    t := { t with
      ok := t.ok && e.role == 632
      frames := t.frames.set e.role e.input
      scalarCost := t.scalarCost + scalarAllowance e }
  else if e.kind == 4 || e.kind == 5 || e.kind == 7 then
    t := { t with
      ok := t.ok && t.frames.get e.role == e.input &&
      (e.kind == 7 || scalarValid e) &&
      (e.kind != 4 || e.role != e.source) &&
      (e.kind != 7 || e.role == 632) &&
      (e.kind == 5 || (e.source < 633 && t.frames.get e.source == e.input))
      scalarCost := t.scalarCost + scalarAllowance e }
  else
    t := { t with ok := false }
  return t

structure Segment where
  initial : Table Nat
  final : Table Nat
  events : List Event
  paid : Array Nat
  scalarCost : Nat
  deriving Inhabited, Repr

def checkSegment (frames : Table Basis) (paid : Table Paid)
    (warps : Table Warp) (s : Segment) : Bool :=
  let result := s.events.foldl (step frames paid warps) {frames := s.initial}
  s.initial.size == 633 && s.final.size == 633 &&
  s.initial.wellFormed && s.final.wellFormed && result.ok &&
  result.frames == s.final && result.paid == s.paid && result.scalarCost == s.scalarCost

structure CheckedSegment (frames : Table Basis) (paid : Table Paid)
    (warps : Table Warp) where
  data : Segment
  valid : checkSegment frames paid warps data = true

def linked (initial final : Table Nat) : List Segment → Bool
  | [] => initial == final
  | s :: ss => s.initial == initial && linked s.final final ss

def totalPaid (segments : List Segment) : Array Nat :=
  (List.range 10).toArray.map (fun r => segments.foldl (fun n s => n + s.paid[r]!) 0)

def totalScalarCost (segments : List Segment) : Nat :=
  segments.foldl (fun n s => n + s.scalarCost) 0

def totalEvents (segments : List Segment) : Nat :=
  segments.foldl (fun n s => n + s.events.length) 0

end NativeCertificate
