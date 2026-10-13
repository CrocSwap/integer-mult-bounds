import CurrentFiveStageBankAddressFactor

/-!
Inactive typed source translation at commit
12a4934d15006e8c10f9b2264f13f8f341be802b, from
research/five-stage-gen4-banks/{bank_template.py,code/global_lowering.py}.

This binds the literal five-stage lowering and BankPlan phase order.  Local
records, their frame registry, the cover enumeration and resolved normalizers
are still caller inputs, as in the Python sources.  No matrix, finite-record
digest, physical endpoint, arbitrary-dirty provider, or cost is certified here.
All lists below are chronological.  BankEndpoints.runCompleted is tail-first;
its semantic connection uses a reversed endpoint list in the separate bank
completion adapter, never an unproved coincidence of the two orders.
-/
namespace CurrentMain.FiveStageBankSource
open CurrentMain.BankRouting CurrentMain.FiveStageBankAddress

universe u v w

inductive Stage where
  | s0 | s1 | s2 | s3 | s4
  deriving DecidableEq, Repr

def stageIndex : Stage → Nat
  | .s0 => 0 | .s1 => 1 | .s2 => 2 | .s3 => 3 | .s4 => 4

def stages : List Stage := [.s0, .s1, .s2, .s3, .s4]
def replicas : List Nat := List.range 60

/-- Both exact source files use this ordered source/target bank table. -/
def active : Stage → Nat × Nat
  | .s0 => (0, 1) | .s1 => (1, 0) | .s2 => (0, 1)
  | .s3 => (3, 2) | .s4 => (2, 3)

def complemented : Stage → Bool
  | .s1 | .s3 => true
  | _ => false

def boundary : Stage → Option Nat
  | .s1 => some 0 | .s2 => some 1 | .s4 => some 2
  | _ => none

/-- global_lowering.family on its asserted domain 0 <= local <= 19930. -/
def logicalFamily (s : Stage) (localIndex : Int) : Int :=
  if localIndex = 19930 then 23450
  else if localIndex < 1760 then Int.ofNat ((active s).1 * 1760) + localIndex
  else if localIndex < 3520 then Int.ofNat ((active s).2 * 1760) + localIndex - 1760
  else 7040 + localIndex - 3520

def validLocalIndex (localIndex : Int) : Prop := 0 ≤ localIndex ∧ localIndex ≤ 19930

def dataFamily (replica bank port : Nat) : Nat := (4 * replica + bank) * 1760 + port

def bankFamily (s : Stage) (stageBank : Nat) : Nat :=
  422400 + stageIndex s * 172127 + stageBank

/-- The local six-field word has MOVE, ADD, LOCAL_BEGIN and LOCAL_END. -/
inductive LocalOp where
  | move | add | localBegin | localEnd
  deriving DecidableEq, Repr

structure LocalRow where
  op : LocalOp
  a : Int
  b : Int
  c : Int
  f : Int
  z : Int
  deriving DecidableEq, Repr

/-- Eight signed fields in the exact Python output order. -/
structure StageRow where
  op : Nat
  a : Int
  b : Int
  c : Int
  f : Int
  z : Int
  stage : Nat
  reverse : Nat
  deriving DecidableEq, Repr

def row (s : Stage) (op : Nat) (a b c f z : Int) : StageRow :=
  ⟨op, a, b, c, f, z, stageIndex s, if complemented s then 1 else 0⟩

/-- Exact iter_stage branches.  Reversal never turns ERASE into an inverse. -/
def lowerRow (s : Stage) (family : Int → Int) (r : LocalRow) : List StageRow :=
  let copyOpen := [row s 2 (family r.b) (family r.a) 0 r.c 0,
    row s 0 (family r.b) r.c r.f r.z 0]
  let erase := [row s 3 (family r.b) (-1) 0 r.f 0]
  match r.op with
  | .move => [row s 0 (family r.a)
      (if complemented s then r.c else r.b)
      (if complemented s then r.b else r.c) r.f 0]
  | .add => [row s 1 (family r.a) (family r.b)
      (if complemented s then -r.c else r.c) r.f r.z]
  | .localBegin => if complemented s then erase else copyOpen
  | .localEnd => if complemented s then copyOpen else erase

def lowerStage (s : Stage) (family : Int → Int) (records : List LocalRow) : List StageRow :=
  (if complemented s then records.reverse else records).flatMap (lowerRow s family)

def lowerSelectedStage (s : Stage) (records : List LocalRow) : List StageRow :=
  lowerStage s (logicalFamily s) records

/-- map_stage_row changes stream slots only; MOVE frame IDs remain metadata. -/
inductive SecondOperand (Address : Type u) where
  | stream (address : Address)
  | metadata (value : Int)

structure AddressedRow (Address : Type u) where
  op : Nat
  a : Address
  b : SecondOperand Address
  c : Int
  f : Int
  z : Int
  stage : Nat
  reverse : Nat

def mapStageRow {Address : Type u} (address : Int → Address) (r : StageRow) :
    AddressedRow Address :=
  ⟨r.op, address r.a,
    if r.op = 1 ∨ r.op = 2 then .stream (address r.b) else .metadata r.b,
    r.c, r.f, r.z, r.stage, r.reverse⟩

/-- Source iter_bridges triples are (destination, source, coefficient). -/
def bridges : Nat → List (Nat × Nat × Int)
  | 0 => [(0, 2, 1), (3, 1, -1)]
  | 1 => [(3, 1, 1), (0, 2, -1)]
  | 2 => [(1, 3, -1), (2, 0, 1)]
  | _ => []

def terminalPairs : List (Nat × Nat) := [(0, 1), (2, 3)]

/-- A phase denotes an entire cover sweep, not one arbitrary cover class. -/
inductive Phase where
  | stage (s : Stage) (replica : Nat)
  | idle (s : Stage) (replica : Nat)
  | bridge (s : Stage) (replica : Nat)
  | terminalExchange (replica : Nat)
  deriving DecidableEq, Repr

def stagePhases (s : Stage) : List Phase :=
  replicas.map (Phase.stage s) ++
    match boundary s with
    | none => []
    | some _ => replicas.flatMap (fun r => [.idle s r, .bridge s r])

/-- Literal BankPlan.phase_schedule order, retaining all sixty replicas. -/
def phaseSchedule : List Phase :=
  stages.flatMap stagePhases ++ replicas.map Phase.terminalExchange

/-- Full-bank completion needs all sixty replica sweeps at one stage: allocation
uses role_index * 60 + replica, so one replica alone need not fill a bank. -/
def stageInvocationOrder {Cover : Type u} (cover : List Cover) : List (Nat × Cover) :=
  replicas.flatMap (fun r => cover.map (fun d => (r, d)))

/-- The supplied inverse-chart factor is already embedded in the stage window.
Its equality to the source rational factor program is a provider obligation. -/
structure NormalizerFactors (G : Type u) where
  scalarMatrix : G
  permutationMatrix : G
  embeddedInverseChart : G

def normalizer {G : Type u} (A : GroupLaws G) (n : NormalizerFactors G) : G :=
  A.mul n.scalarMatrix (A.mul n.permutationMatrix n.embeddedInverseChart)

/-- Family tags are retained even though different roles can share a family. -/
def helperAddress {G : Type u} (A : GroupLaws G) (d tau : G)
    (family : Nat) (n : NormalizerFactors G) : Nat × G :=
  (family, sourceAddress A d tau (normalizer A n))

theorem helperAddress_factor {G : Type u} (A : GroupLaws G) (d tau : G)
    (family : Nat) (n : NormalizerFactors G) :
    helperAddress A d tau family n =
      (family, route A d (effectiveEmbedding A tau (normalizer A n))) := by
  unfold helperAddress
  rw [address_factor]

/-- One stage phase keeps each complete local telescope contiguous. -/
def expandPhase {Cover : Type u} {Op : Type v} (cover : List Cover)
    (stageWord idleWord bridgeWord : Stage → Nat → Cover → List Op)
    (terminalWord : Nat → Cover → List Op) : Phase → List Op
  | .stage s r => cover.flatMap (stageWord s r)
  | .idle s r => cover.flatMap (idleWord s r)
  | .bridge s r => cover.flatMap (bridgeWord s r)
  | .terminalExchange r => cover.flatMap (terminalWord r)

def chronologicalWord {Cover : Type u} {Op : Type v} (cover : List Cover)
    (stageWord idleWord bridgeWord : Stage → Nat → Cover → List Op)
    (terminalWord : Nat → Cover → List Op) : List Op :=
  phaseSchedule.flatMap (expandPhase cover stageWord idleWord bridgeWord terminalWord)

theorem stage_sweep_literal {Cover : Type u} {Op : Type v} (cover : List Cover)
    (stageWord idleWord bridgeWord : Stage → Nat → Cover → List Op)
    (terminalWord : Nat → Cover → List Op) (s : Stage) (r : Nat) :
    expandPhase cover stageWord idleWord bridgeWord terminalWord (.stage s r) =
      cover.flatMap (stageWord s r) := rfl

/-- The exact chronological order passed to the sequential completed-bank API.
The full-bank partition and universal local endpoints are separate premises. -/
theorem replica_major_stage_word {Cover : Type u} {Op : Type v} (cover : List Cover)
    (stageWord idleWord bridgeWord : Stage → Nat → Cover → List Op)
    (terminalWord : Nat → Cover → List Op) (s : Stage) :
    (stageInvocationOrder cover).flatMap (fun rd => stageWord s rd.1 rd.2) =
      (replicas.map (Phase.stage s)).flatMap
        (expandPhase cover stageWord idleWord bridgeWord terminalWord) := by
  simp only [stageInvocationOrder, List.flatMap_assoc, List.flatMap_map, expandPhase]

theorem lowering_stage_one (family : Int → Int) (records : List LocalRow) :
    lowerStage .s1 family records = records.reverse.flatMap (lowerRow .s1 family) := rfl

theorem lowering_stage_three (family : Int → Int) (records : List LocalRow) :
    lowerStage .s3 family records = records.reverse.flatMap (lowerRow .s3 family) := rfl

end CurrentMain.FiveStageBankSource

#print axioms CurrentMain.FiveStageBankSource.helperAddress_factor
#print axioms CurrentMain.FiveStageBankSource.stage_sweep_literal
#print axioms CurrentMain.FiveStageBankSource.replica_major_stage_word
#print axioms CurrentMain.FiveStageBankSource.lowering_stage_one
#print axioms CurrentMain.FiveStageBankSource.lowering_stage_three
