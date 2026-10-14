import GeometryCatalog
import SignedTraceCore

/-! Fresh reconstruction of the chronological geometry checker after executor loss.
The public finite certificate retains the original source-bound event interface.
No mathematical result or receipt from the lost executor is assumed. -/
namespace CurrentMain.ComplexGeometry
open CurrentMain.SignedTrace CurrentMain.BinaryFrame

structure Port where
  target : Bool
  role : Nat
  frame : Nat
  deriving DecidableEq, Repr

structure Move where
  target : Bool
  role : Nat
  before : Nat
  after : Nat
  edge : Nat
  deriving DecidableEq, Repr

def Move.key (m : Move) : Nat := if m.target then 16384 + m.role else m.role

def Move.port (m : Move) : Port := ⟨m.target,m.role,m.after⟩

def activePortCheck (m : Move) : Bool :=
  if m.target then decide (m.role < 1320) else decide (m.role < 10732)

def moveState (m : Move) (state : Nat → Nat) : Nat → Nat :=
  fun i => if i=m.key then m.after else state i

def runMoves : List Move → (Nat → Nat) → Nat → Nat
  | [], state => state
  | m::rest, state => runMoves rest (moveState m state)

def ValidRun (frames : Nat → FrameRecord) (edges : Nat → EdgeRecord) :
    List Move → (Nat → Nat) → Prop
  | [], _ => True
  | m::rest, state => m.key < 32768 ∧ state m.key=m.before ∧
      edgeMatches frames edges m.before m.after m.edge=true ∧
      ValidRun frames edges rest (moveState m state)

def moveCheck (frames : Nat → FrameRecord) (edges : Nat → EdgeRecord)
    (t : Table Nat) (m : Move) : Bool :=
  decide (m.key < 32768 ∧ get t m.key=m.before) &&
    edgeMatches frames edges m.before m.after m.edge

def traceCheck (frames : Nat → FrameRecord) (edges : Nat → EdgeRecord) :
    Table Nat → List Move → Bool
  | _, [] => true
  | t, m::rest => moveCheck frames edges t m &&
      traceCheck frames edges (put 15 t m.key m.after) rest

theorem runMoves_append (first second : List Move) (state : Nat → Nat) :
    runMoves (first++second) state = runMoves second (runMoves first state) := by
  induction first generalizing state with
  | nil => rfl
  | cons m rest ih => exact ih _

theorem runMoves_congr (moves : List Move) (left right : Nat → Nat)
    (same : ∀ i, i<32768 → left i=right i) (i : Nat) (hi : i<32768) :
    runMoves moves left i=runMoves moves right i := by
  induction moves generalizing left right with
  | nil => exact same i hi
  | cons m rest ih =>
    apply ih
    intro j hj
    simp only [moveState]
    split <;> simp_all

theorem validRun_congr (frames : Nat → FrameRecord) (edges : Nat → EdgeRecord)
    (moves : List Move) (left right : Nat → Nat)
    (same : ∀ i, i<32768 → left i=right i)
    (valid : ValidRun frames edges moves left) : ValidRun frames edges moves right := by
  induction moves generalizing left right with
  | nil => trivial
  | cons m rest ih =>
    rcases valid with ⟨bound,current,edge,tail⟩
    refine ⟨bound, (same m.key bound).symm.trans current, edge, ih _ _ ?_ tail⟩
    intro j hj
    simp only [moveState]
    split <;> simp_all

theorem traceCheck_sound (frames : Nat → FrameRecord) (edges : Nat → EdgeRecord)
    (moves : List Move) (start : Table Nat)
    (checked : traceCheck frames edges start moves=true) :
    ValidRun frames edges moves (get start) := by
  induction moves generalizing start with
  | nil => trivial
  | cons m rest ih =>
    have both := Bool.and_eq_true_iff.mp checked
    have one := Bool.and_eq_true_iff.mp both.1
    have facts : m.key<32768 ∧ get start m.key=m.before := of_decide_eq_true one.1
    refine ⟨facts.1,facts.2,one.2,?_⟩
    apply validRun_congr frames edges rest (get (put 15 start m.key m.after))
      (moveState m (get start))
    · intro i hi
      exact get_put 15 start m.key i m.after facts.1 hi
    · exact ih _ both.2

theorem validRun_bounds (frames : Nat → FrameRecord) (edges : Nat → EdgeRecord)
    (moves : List Move) (state : Nat → Nat) (valid : ValidRun frames edges moves state) :
    ∀ m ∈ moves, m.key<32768 := by
  induction moves generalizing state with
  | nil => simp
  | cons m rest ih =>
    intro n hn
    rcases List.mem_cons.mp hn with eq | member
    · subst n; exact valid.1
    · exact ih _ valid.2.2.2 n member

theorem validRun_append (frames : Nat → FrameRecord) (edges : Nat → EdgeRecord)
    (first second : List Move) (state : Nat → Nat)
    (left : ValidRun frames edges first state)
    (right : ValidRun frames edges second (runMoves first state)) :
    ValidRun frames edges (first++second) state := by
  induction first generalizing state with
  | nil => exact right
  | cons m rest ih => exact ⟨left.1,left.2.1,left.2.2.1,ih _ left.2.2.2 right⟩

structure TraceCertificate (frames : Nat → FrameRecord) (edges : Nat → EdgeRecord)
    (start finish : Table Nat) (moves : List Move) : Prop where
  valid : ValidRun frames edges moves (get start)
  endpoint : ∀ i, i<32768 → runMoves moves (get start) i=get finish i

theorem append_trace_certificate (frames : Nat → FrameRecord) (edges : Nat → EdgeRecord)
    (start middle finish : Table Nat) (first second : List Move)
    (left : TraceCertificate frames edges start middle first)
    (right : TraceCertificate frames edges middle finish second) :
    TraceCertificate frames edges start finish (first++second) := by
  constructor
  · apply validRun_append frames edges first second (get start) left.valid
    exact validRun_congr frames edges second (get middle) (runMoves first (get start))
      (fun i hi => (left.endpoint i hi).symm) right.valid
  · intro i hi
    rw [runMoves_append]
    exact (runMoves_congr second _ _ left.endpoint i hi).trans (right.endpoint i hi)

theorem runMoves_span_mono (bases : Nat → BasisRecord) (frames : Nat → FrameRecord)
    (edges : Nat → EdgeRecord) (catalog : ValidCatalog bases frames edges)
    (moves : List Move) (state : Nat → Nat) (valid : ValidRun frames edges moves state)
    (i n : Nat) (member : Span (frameRows bases frames (state i)) n) :
    Span (frameRows bases frames (runMoves moves state i)) n := by
  induction moves generalizing state with
  | nil => exact member
  | cons m rest ih =>
    apply ih _ valid.2.2.2
    by_cases same : i=m.key
    · subst i
      have edge := (checked_frame_edge bases frames edges catalog _ _ _ valid.2.2.1).1
      have mem : Span (frameRows bases frames m.before) n := by simpa only [valid.2.1] using member
      simpa only [moveState, if_pos rfl] using edge n mem
    · simpa only [moveState, if_neg same] using member

structure Metric where
  target : Bool
  rank : Nat
  deriving DecidableEq, Repr

def measure (bases : Nat → BasisRecord) (frames : Nat → FrameRecord) (m : Move) : Metric :=
  ⟨m.target, (frameRows bases frames m.after).length-(frameRows bases frames m.before).length⟩

def charges (target : Bool) (rank : Nat) (metrics : List Metric) : Nat :=
  (metrics.filter (fun m => m.target==target && m.rank==rank)).length

def EventLookup (eventAt : Nat → Move) (offset : Nat) (moves : List Move) : Prop :=
  ∀ i, i<moves.length → moves[i]?=some (eventAt (offset+i))

end CurrentMain.ComplexGeometry
#print axioms CurrentMain.ComplexGeometry.runMoves_append
#print axioms CurrentMain.ComplexGeometry.runMoves_congr
#print axioms CurrentMain.ComplexGeometry.validRun_congr
#print axioms CurrentMain.ComplexGeometry.traceCheck_sound
#print axioms CurrentMain.ComplexGeometry.validRun_bounds
#print axioms CurrentMain.ComplexGeometry.validRun_append
#print axioms CurrentMain.ComplexGeometry.append_trace_certificate
#print axioms CurrentMain.ComplexGeometry.runMoves_span_mono
