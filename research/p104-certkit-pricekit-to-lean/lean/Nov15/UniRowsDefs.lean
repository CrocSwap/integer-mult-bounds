/-
UniRowsDefs (lane ROWS, Nov 19).  Computable REVERSE-MODE (adjoint) row checker for a packed word trace
(UniInhabitDefs event format), kernel-checked.  Generic: any word with packed events (gen_rows.py makes the data).
State walking BACKWARD (`BS`):
  t : loc tree (UniInhabitDefs codes: 0 unborn, 1 cleared, i+2 at frame i), the loc BEFORE-side of the next event,
  z : bit mask; bit j = 0 ⇒ g_j = [] (lets the checker skip events whose target co-row is zero),
  g : register j ↦ sparse co-row over OUTPUT registers (List (o, D·value)),
  a : register j ↦ sparse co-row collected at j's public birth.
Meaning (UniRowsSound): Σ_j g_j(o)/D · row_j + Σ_j a_j(o)/D · e_j is invariant along the trace.
Values are integers scaled by a fixed D (every division is checked exact).  Core Lean only (no Mathlib).
-/
import Nov15.UniInhabitDefs

namespace UniRows
open UniInhabit

abbrev SV := List (Nat × Int)

/-- read leaf j of a depth-d tree (default `z`). -/
def gtA {α : Type} (z : α) : Nat → Tr α → Nat → α
  | 0, t, _ => Tr.val z t
  | d + 1, t, j => cond (Nat.beq (j % 2) 0) (gtA z d (Tr.lft t) (j / 2)) (gtA z d (Tr.rgt t) (j / 2))

/-- write leaf j. -/
def stA {α : Type} : Nat → Tr α → Nat → α → Tr α
  | 0, _, _, x => .lf x
  | d + 1, t, j, x => cond (Nat.beq (j % 2) 0) (.nd (stA d (Tr.lft t) (j / 2) x) (Tr.rgt t))
      (.nd (Tr.lft t) (stA d (Tr.rgt t) (j / 2) x))

/-- x·p/q (integer division; exactness checked separately by `dvdAll`). -/
def mq (p : Int) (q : Nat) (x : Int) : Int := (x * p) / (q : Int)

def dvdAll (p : Int) (q : Nat) : SV → Bool
  | [] => true
  | (_, x) :: xs => (x * p % (q : Int) == 0) && dvdAll p q xs

def scl (p : Int) (q : Nat) : SV → SV
  | [] => []
  | (i, x) :: xs => (i, mq p q x) :: scl p q xs

/-- merge `ys + (p/q)·xs` (keys summed, zeros dropped); fuel ≥ |xs| + |ys| + 1. -/
def mrg (p : Int) (q : Nat) : Nat → SV → SV → SV
  | 0, xs, ys => scl p q xs ++ ys
  | _ + 1, [], ys => ys
  | _ + 1, xs, [] => scl p q xs
  | f + 1, (i, x) :: xs, (j, y) :: ys =>
    cond (Nat.blt i j) ((i, mq p q x) :: mrg p q f xs ((j, y) :: ys)) <|
    cond (Nat.blt j i) ((j, y) :: mrg p q f ((i, x) :: xs) ys) <|
    let z := y + mq p q x
    cond (z == 0) (mrg p q f xs ys) ((i, z) :: mrg p q f xs ys)

def sgn (e : PE) : Int := cond e.neg (-(e.num : Int)) (e.num : Int)

structure BS where
  t : Tr Nat
  z : Nat
  g : Tr SV
  a : Tr SV

def gG (s : BS) (j : Nat) : SV := gtA [] 11 s.g j

/-- one BACKWARD event: from the state after `e` to the state before it; `none` = a check failed.
Events whose target register has mask bit 0 (co-row known empty) only move the loc tree. -/
def bstep (NR : Nat) (s : BS) (e : PE) : Option BS :=
  let hot := Nat.testBit s.z e.r
  cond (Nat.blt e.r NR) (
  cond (Nat.beq e.op 0) (some ⟨st 11 s.t e.r 0, s.z,
      cond hot (stA 11 s.g e.r []) s.g, cond hot (stA 11 s.a e.r (gG s e.r ++ gtA [] 11 s.a e.r)) s.a⟩) <|
  cond (Nat.beq e.op 1) (some ⟨st 11 s.t e.r 0, s.z, cond hot (stA 11 s.g e.r []) s.g, s.a⟩) <|
  cond (Nat.beq e.op 2) (cond hot (
    let gr := gG s e.r
    let ga := gG s e.a
    cond (Nat.blt e.a NR && !(Nat.beq e.a e.r) && Nat.beq (gt 11 s.t e.a) (e.c + 2) && !(Nat.beq e.den 0) &&
        dvdAll (sgn e) e.den gr)
      (some ⟨s.t, s.z ||| 2 ^ e.a, stA 11 s.g e.a (mrg (sgn e) e.den (gr.length + ga.length + 1) gr ga), s.a⟩)
      none) (some s)) <|
  cond (Nat.beq e.op 3) (cond hot (
    let gr := gG s e.r
    cond (!(Nat.beq e.den 0) && dvdAll (sgn e) e.den gr)
      (some ⟨s.t, s.z, stA 11 s.g e.r (scl (sgn e) e.den gr), s.a⟩) none) (some s)) <|
  cond (Nat.beq e.op 4) (some ⟨st 11 s.t e.r (e.c + 2), s.z, s.g, s.a⟩) <|
  cond (Nat.beq e.op 5) (some ⟨st 11 s.t e.r (e.c + 2), s.z, cond hot (stA 11 s.g e.r []) s.g, s.a⟩) none) none

/-- run backward over a REVERSED event list (head = latest event). -/
def brun (NR : Nat) : BS → List PE → Option BS
  | s, [] => some s
  | s, e :: es => match bstep NR s e with
    | some s' => brun NR s' es
    | none => none

end UniRows
