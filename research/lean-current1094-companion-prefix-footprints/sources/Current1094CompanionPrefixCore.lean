import Current1094CompanionDecodedRows
import LabelCursorProjection

/-!
UNCOMPILED. Complete label-write/phase footprints of the exact selected PR1094
forward and backward raw prefixes [0,16508). The source reader retains every
row position, all COPY/CLEAR destinations and all six named phase markers.
Their centre footprints differ, so the backward centre block is preserved.
Only blocks with at most256 rows are reduced in each private finite fact.

The footprint is source-bound evidence, not a byte/JSON parser theorem or a
proof of successful complete decoding/guarded lowering. The accepted23 raw
rows retain their explicit L508 start=2 and terminal=999 hypotheses. Recipe
membership/full phase, arbitrary physical charts/execution and cost remain
outside this label-write/cut certificate. No physical event is discarded.
Attribution: icekylinx's selected emitter, DreamingOfClouds' LemmaG semantics,
Jeremy Kothe's HyperplaneEnd labels, and Hanson Sun's PR1611 helper450 lead.
New source prepared with OpenAI assistance; Apache-2.0.
-/
set_option Elab.async false

namespace CurrentMain.Current1094CompanionPrefixSkeleton
open CurrentMain.Current1094Helper450RelabelSlice
open CurrentMain.GuardedParsedLabelLowering

inductive Mark where
  | passive
  | phase (name : String)
  | relabel (r : Register)
  | copy (r : Register)
  | clear (r : Register)
  deriving DecidableEq

def Action.mark : Action → Mark
  | .relabel r _ _ _ => .relabel r
  | .add .. => .passive
  | .scale .. => .passive
  | .copy t _ _ => .copy t
  | .clear t _ => .clear t

def Instruction.mark : Instruction → Mark
  | .phase s => .phase s
  | .action a => (CurrentMain.Current1094CompanionPrefixSkeleton.Action.mark a)

def eventMark : LemmaG.Event Register Label Rat → Mark
  | .relabel r _ _ => .relabel r
  | .add .. => .passive
  | .scale .. => .passive
  | .copy t _ _ => .copy t
  | .clear t _ => .clear t

/-- COPY's changing stored full tag does not change its label-write target. -/
theorem event_mark_exact (a : Action) (l : Register → Label) :
    eventMark (a.event l) = (CurrentMain.Current1094CompanionPrefixSkeleton.Action.mark a) := by
  cases a <;> rfl

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.event_mark_exact

def keep (r : Register) : Bool :=
  decide (r = .inl 157 ∨ r = .inl 219 ∨ r = .inl 230 ∨ r = .inl 508)

def labelTracked : Mark → Bool
  | .relabel r => keep r
  | .copy r => keep r
  | .clear r => keep r
  | _ => false

def tracked : Mark → Bool
  | .phase _ => true
  | m => labelTracked m

/-- The mark's selected write test is exactly the accepted Event projection. -/
theorem event_write_test_exact (a : Action) (l : Register → Label) :
    CurrentMain.LabelCursorProjection.writesIn keep (a.event l) =
      labelTracked (CurrentMain.Current1094CompanionPrefixSkeleton.Action.mark a) := by
  cases a <;> rfl

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.event_write_test_exact

def scanFrom : Nat → List Mark → List (Nat × Mark)
  | _, [] => []
  | n, m :: ms =>
      if tracked m then (n,m) :: scanFrom (n+1) ms else scanFrom (n+1) ms

theorem scan_append (xs ys : List Mark) (n : Nat) :
    scanFrom n (xs ++ ys) = scanFrom n xs ++ scanFrom (n+xs.length) ys := by
  induction xs generalizing n with
  | nil => simp [scanFrom]
  | cons x xs ih =>
      cases hx : tracked x <;>
        simp [scanFrom, hx, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]


#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.scan_append

end CurrentMain.Current1094CompanionPrefixSkeleton
