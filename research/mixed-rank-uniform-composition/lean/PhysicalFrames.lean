import Std

namespace PhysicalFrames

inductive Datum | empty | zero | one deriving DecidableEq, Repr

inductive Sym
  | blank | start | stop | data (x : Datum) (saved : Bool)
  deriving DecidableEq, Repr

structure Tape where
  left : List Sym
  right : List Sym
  deriving DecidableEq, Repr

def Tape.read (z : Tape) := z.right.headD .blank
def Tape.forward (z : Tape) (s : Sym) : Tape := ⟨s :: z.left, z.right.tail⟩
def Tape.backward (z : Tape) (s : Sym) : Tape :=
  ⟨z.left.tail, z.left.headD .blank :: s :: z.right.tail⟩
def Tape.stay (z : Tape) (s : Sym) : Tape := ⟨z.left, s :: z.right.tail⟩

inductive State
  | push | seek | init | initData | initTip | leave | clear | parentTip | find
  | halted | fault deriving DecidableEq, Repr

abbrev Config := State × Tape
def tick (c : Config) : Config :=
  let (q,z) := c
  match q, z.read with
  | .push, .data a false => (.seek, z.forward (.data a true))
  | .seek, .data a false => (.seek, z.forward (.data a false))
  | .seek, .stop => (.init, z.forward .stop)
  | .init, .blank => (.initData, z.forward .start)
  | .initData, .blank => (.initTip, z.forward (.data .empty false))
  | .initTip, .blank => (.halted, z.backward .stop)
  | .leave, .data a false => (.leave, z.forward (.data a false))
  | .leave, .stop => (.clear, z.backward .blank)
  | .clear, .data _ false => (.clear, z.backward .blank)
  | .clear, .start => (.parentTip, z.backward .blank)
  | .parentTip, .stop => (.find, z.backward .stop)
  | .find, .data a false => (.find, z.backward (.data a false))
  | .find, .data a true => (.halted, z.stay (.data a false))
  | .halted, _ => c
  | _, _ => (.fault, z)

def run : Nat → Config → Config
  | 0, c => c
  | n+1, c => run n (tick c)

theorem run_add (n k : Nat) (c : Config) :
    run (n+k) c = run k (run n c) := by
  induction n generalizing c with
  | zero => simp [run]
  | succ n ih =>
    rw [Nat.succ_add, run, run, ih]

def live (a : Datum) : Sym := .data a false

private theorem walk_right (q : State)
    (step : ∀ (a : Datum) (l r : List Sym),
        tick (q, ⟨l, live a :: r⟩) = (q, ⟨live a :: l, r⟩))
    (xs : List Datum) (l r : List Sym) :
    run xs.length (q, ⟨l, xs.map live ++ r⟩) =
      (q, ⟨(xs.map live).reverse ++ l, r⟩) := by
  induction xs generalizing l r with
  | nil => rfl
  | cons x xs ih =>
    simp only [List.length_cons, List.map_cons, List.cons_append, run,
      step, ih, List.reverse_cons, List.append_assoc, List.cons_append, List.nil_append]

def bwd (vis : List Datum) (endmark : Sym) (l r : List Sym) : Tape :=
  match vis with
  | [] => ⟨l, endmark :: r⟩
  | a :: xs => ⟨xs.map live ++ endmark :: l, live a :: r⟩

private theorem walk_left (q : State) (w : Datum → Sym)
    (step : ∀ (a : Datum) (l r : List Sym) (k : Sym),
        tick (q, ⟨k :: l, live a :: r⟩) = (q, ⟨l, k :: w a :: r⟩))
    (xs : List Datum) (endmark : Sym) (l r : List Sym) :
    run xs.length (q, bwd xs endmark l r) =
      (q, ⟨l, endmark :: (xs.map w).reverse ++ r⟩) := by
  induction xs generalizing l r with
  | nil => rfl
  | cons a xs ih =>
    simp only [List.length_cons, run]
    have mov : tick (q, bwd (a :: xs) endmark l r) =
        (q, bwd xs endmark l (w a :: r)) := by
      cases xs <;> simp [bwd, step]
    rw [mov, ih]
    simp

/-- Suspend the current head and install a child on three previously
untouched cells. The program never reads the lists l, r as metadata. -/
theorem push_correct (head : Datum) (suffix : List Datum) (l r : List Sym) :
    run (1+suffix.length+4)
      (.push, ⟨l, live head :: suffix.map live ++ [.stop,.blank,.blank,.blank] ++ r⟩) =
    (.halted, ⟨.start :: .stop :: (suffix.map live).reverse ++ .data head true :: l,
                    live .empty :: .stop :: r⟩) := by
  rw [run_add (1+suffix.length) 4, run_add 1 suffix.length]
  simp only [List.append_assoc, List.cons_append, List.nil_append]
  change run 4 (run suffix.length
    (.seek, ⟨.data head true :: l, suffix.map live ++ (.stop :: .blank :: .blank :: .blank :: r)⟩)) = _
  rw [walk_right .seek (fun _ _ _ => rfl) suffix (.data head true :: l)
    (.stop :: .blank :: .blank :: .blank :: r)]
  rfl

/-- Return from an arbitrary data position of a nonempty, dirty child.
The cleanup visits every cell of its old extent, including formerly blank
payloads. The parent original head, both sides of it and the old tail of
the tape are restored. -/
theorem leave_correct (parent child : Datum) (pTail cLeft cRight : List Datum)
    (l r : List Sym) :
    let pBack := (pTail.map live).reverse ++ .data parent true :: l
    let childWord := cLeft ++ [child] ++ cRight
    let childLen := childWord.length
    let z : Tape := ⟨(cLeft.map live).reverse ++ .start :: .stop :: pBack,
        live child :: cRight.map live ++ .stop :: r⟩
    run ((1+cRight.length) + 1 + childLen + 2 + pTail.length + 1) (.leave, z) =
      (.halted, ⟨l, live parent :: pTail.map live ++ .stop ::
        List.replicate (childLen+2) .blank ++ r⟩) := by
  dsimp only
  let x := cLeft ++ [child] ++ cRight
  let pb := (pTail.map live).reverse ++ .data parent true :: l
  have e₁ : run (1+cRight.length)
      (.leave, ⟨(cLeft.map live).reverse ++ .start :: .stop :: pb,
        live child :: cRight.map live ++ .stop :: r⟩) =
      (.leave, ⟨(x.map live).reverse ++ .start :: .stop :: pb, .stop :: r⟩) := by
    rw [run_add 1 cRight.length]
    change run cRight.length (.leave, ⟨live child :: (cLeft.map live).reverse ++
      Sym.start :: .stop :: pb, cRight.map live ++ .stop :: r⟩) = _
    rw [walk_right .leave (fun _ _ _ => rfl)]
    simp [x, List.append_assoc]
  have e₂ : run 1 (.leave, ⟨(x.map live).reverse ++ .start :: .stop :: pb, .stop :: r⟩) =
      (.clear, bwd x.reverse .start (.stop :: pb) (.blank :: r)) := by
    rw [← List.map_reverse]
    cases x.reverse <;> rfl
  have e₃ := walk_left .clear (fun _ => Sym.blank) (fun _ _ _ _ => rfl)
      x.reverse .start (.stop :: pb) (.blank :: r)
  simp only [List.length_reverse, List.map_const', List.length_reverse,
    List.reverse_replicate] at e₃
  let erased := List.replicate x.length Sym.blank ++ .blank :: r
  have e₄ : run 2 (.clear, ⟨.stop :: pb, .start :: erased⟩) =
      (.find, bwd pTail.reverse (.data parent true) l (.stop :: .blank :: erased)) := by
    dsimp [pb]
    rw [← List.map_reverse]
    cases pTail.reverse <;> rfl
  have e₅ := walk_left .find live (fun _ _ _ _ => rfl)
      pTail.reverse (.data parent true) l (.stop :: .blank :: erased)
  simp [List.map_reverse] at e₅
  change run (((((1+cRight.length)+1)+x.length)+2)+pTail.length+1)
    (.leave, ⟨(cLeft.map live).reverse ++ .start :: .stop :: pb,
        live child :: cRight.map live ++ .stop :: r⟩) = _
  simp only [List.cons_append] at e₃
  rw [run_add (((1+cRight.length+1)+x.length)+2+pTail.length) 1,
    run_add (((1+cRight.length+1)+x.length)+2) pTail.length,
    run_add ((1+cRight.length+1)+x.length) 2,
    run_add (1+cRight.length+1) x.length, run_add (1+cRight.length) 1, e₁, e₂, e₃, e₄, e₅]
  have blank_move (n : Nat) : List.replicate n Sym.blank ++ Sym.blank :: r =
      Sym.blank :: (List.replicate n Sym.blank ++ r) := by
    induction n with
    | zero => rfl
    | succ n ih => simp [List.replicate_succ, ih]
  simp [run, tick, Tape.read, Tape.stay, erased, x, live, List.replicate_succ,
    List.append_assoc, blank_move]

inductive Chain : Nat → List Nat → Prop
| base (v : Nat) : Chain v []
| next {v c : Nat} {tail : List Nat} (shrink : 2*c ≤ v) (inner : Chain c tail) :
    Chain v (c :: tail)

theorem chain_space {v : Nat} {tail : List Nat} (valid : Chain v tail) :
    tail.sum ≤ v := by
  induction valid with
  | base => simp
  | next shrink _ ih => simp only [List.sum_cons]; omega

#print axioms push_correct
#print axioms leave_correct
#print axioms chain_space

end PhysicalFrames
