/-
UniInhabitDefs (lane UNI-INHABIT, Nov 19).  Computable LOC replay checker for a packed word trace (kernel `decide`).
State: depth-11 tree over register codes j < 2048 of loc codes: 0 unborn, 1 cleared, i+2 = sits at frame i.
Event slot (96 bits): op 0-2 | r 3-13 | a 14-24 | c 25-35 | d 36-46 | sign 47 | num 48-71 | den 72-95;
op 0 birthPub, 1 INIT (owned birth), 2 ADD, 3 SCALE, 4 MOVE, 5 CLEAR.
Core Lean only (no Mathlib) so data / segment files compile fast.
-/

namespace UniInhabit

inductive Tr (α : Type) where
  | lf : α → Tr α
  | nd : Tr α → Tr α → Tr α

def Tr.lft {α : Type} (t : Tr α) : Tr α := match t with | .nd l _ => l | t => t
def Tr.rgt {α : Type} (t : Tr α) : Tr α := match t with | .nd _ r => r | t => t
def Tr.val {α : Type} (z : α) (t : Tr α) : α := match t with | .lf x => x | _ => z

/-- read leaf j of a depth-d tree (default 0). -/
def gt : Nat → Tr Nat → Nat → Nat
  | 0, t, _ => Tr.val 0 t
  | d + 1, t, j => cond (Nat.beq (j % 2) 0) (gt d (Tr.lft t) (j / 2)) (gt d (Tr.rgt t) (j / 2))

/-- write leaf j. -/
def st : Nat → Tr Nat → Nat → Nat → Tr Nat
  | 0, _, _, x => .lf x
  | d + 1, t, j, x => cond (Nat.beq (j % 2) 0) (.nd (st d (Tr.lft t) (j / 2) x) (Tr.rgt t))
      (.nd (Tr.lft t) (st d (Tr.rgt t) (j / 2) x))

def Tr.full {α : Type} (x : α) : Nat → Tr α
  | 0 => .lf x
  | d + 1 => .nd (Tr.full x d) (Tr.full x d)

def Tr.beq : Tr Nat → Tr Nat → Bool
  | .lf x, .lf y => Nat.beq x y
  | .nd l r, .nd l' r' => Tr.beq l l' && Tr.beq r r'
  | _, _ => false

structure PE where
  op : Nat
  r : Nat
  a : Nat
  c : Nat
  d : Nat
  neg : Bool
  num : Nat
  den : Nat

def PE.ofNat (x : Nat) : PE :=
  ⟨x % 8, x / 8 % 2048, x / 16384 % 2048, x / 33554432 % 2048, x / 68719476736 % 2048,
    Nat.beq (x / 140737488355328 % 2) 1, x / 281474976710656 % 16777216, x / 4722366482869645213696 % 16777216⟩

/-- decode `n` slots of 96 bits. -/
def decode : Nat → Nat → List PE
  | 0, _ => []
  | n + 1, x => PE.ofNat (x % 79228162514264337593543950336) :: decode n (x / 79228162514264337593543950336)

/-- the decoded event list of a chunk list. -/
def decodeAll : List (Nat × Nat) → List PE
  | [] => []
  | (n, x) :: cs => decode n x ++ decodeAll cs

/-- replay parameters: NP public, NR registers in events, NF frames, frame masks. -/
structure Par where
  NP : Nat
  NR : Nat
  NF : Nat
  mask : Tr Nat

/-- c ⊊ d on frame masks (both < 2^512). -/
def Par.ssub (p : Par) (c d : Nat) : Bool :=
  let mc := gt 11 p.mask c
  let md := gt 11 p.mask d
  Nat.beq (mc &&& md) mc && !(Nat.beq mc md) && Nat.blt md (2 ^ 512)

/-- one event (op dispatch); `l` = current loc code of e.r. -/
def Par.stepOp (p : Par) (t : Tr Nat) (e : PE) (l : Nat) : Option (Tr Nat) :=
  cond (Nat.beq e.op 0) (cond (Nat.beq l 0 && Nat.blt e.r p.NP) (some (st 11 t e.r (e.c + 2))) none) <|
  cond (Nat.beq e.op 1) (cond (Nat.beq l 0 && Nat.ble p.NP e.r) (some (st 11 t e.r (e.c + 2))) none) <|
  cond (Nat.beq e.op 2 || Nat.beq e.op 3) (cond (Nat.beq l (e.c + 2)) (some t) none) <|
  cond (Nat.beq e.op 4) (cond (Nat.beq l (e.c + 2) && Nat.blt e.d p.NF &&
      cond (Nat.blt e.r p.NP) (p.ssub e.c e.d) (p.ssub e.c e.d || p.ssub e.d e.c))
    (some (st 11 t e.r (e.d + 2))) none) <|
  cond (Nat.beq e.op 5) (cond (Nat.beq l (e.c + 2) && Nat.ble p.NP e.r) (some (st 11 t e.r 1)) none) none

/-- one event; `none` = illegal / outside the checked class (public MOVEs strictly ascending, owned nested). -/
def Par.step (p : Par) (t : Tr Nat) (e : PE) : Option (Tr Nat) :=
  cond (Nat.blt e.r p.NR && Nat.blt e.c p.NF) (p.stepOp t e (gt 11 t e.r)) none

def Par.run (p : Par) : Tr Nat → List PE → Option (Tr Nat)
  | t, [] => some t
  | t, e :: es => match p.step t e with
    | some t' => p.run t' es
    | none => none

/-- segment check: from checkpoint `a`, the chunks `cs` replay legally and land exactly on checkpoint `b`. -/
def Par.seg (p : Par) (a : Tr Nat) (cs : List (Nat × Nat)) (b : Tr Nat) : Bool :=
  match p.run a (decodeAll cs) with
  | some t => Tr.beq t b
  | none => false

/-- MOVE chart pairs of an event list (frame indices), in trace order. -/
def mvOf (e : PE) : Option (Nat × Nat) := cond (Nat.beq e.op 4) (some (e.c, e.d)) none

def init0 : Tr Nat := Tr.full 0 11

end UniInhabit
