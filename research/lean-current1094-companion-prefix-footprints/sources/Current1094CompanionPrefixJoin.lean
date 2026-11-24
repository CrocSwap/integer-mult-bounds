import Current1094CompanionPrefixBlock00
import Current1094CompanionPrefixBlock01
import Current1094CompanionPrefixBlock02
import Current1094CompanionPrefixBlock03
import Current1094CompanionPrefixBlock04
import Current1094CompanionPrefixBlock05
import Current1094CompanionPrefixBlock06
import Current1094CompanionPrefixBlock07
import Current1094CompanionPrefixBlock08
import Current1094CompanionPrefixBlock09
import Current1094CompanionPrefixBlock10
import Current1094CompanionPrefixBlock11
import Current1094CompanionPrefixBlock12
import Current1094CompanionPrefixBlock13
import Current1094CompanionPrefixBlock14
import Current1094CompanionPrefixBlock15
import Current1094CompanionPrefixBlock16
import Current1094CompanionPrefixBlock17
import Current1094CompanionPrefixBlock18
import Current1094CompanionPrefixBlock19
import Current1094CompanionPrefixBlock20
import Current1094CompanionPrefixBlock21
import Current1094CompanionPrefixBlock22
import Current1094CompanionPrefixBlock23
import Current1094CompanionPrefixBlock24
import Current1094CompanionPrefixBlock25
import Current1094CompanionPrefixBlock26
import Current1094CompanionPrefixBlock27
import Current1094CompanionPrefixBlock28
import Current1094CompanionPrefixBlock29
import Current1094CompanionPrefixBlock30
import Current1094CompanionPrefixBlock31
import Current1094CompanionPrefixBlock32
import Current1094CompanionPrefixBlock33
import Current1094CompanionPrefixBlock34
import Current1094CompanionPrefixBlock35
import Current1094CompanionPrefixBlock36
import Current1094CompanionPrefixBlock37
import Current1094CompanionPrefixBlock38
import Current1094CompanionPrefixBlock39
import Current1094CompanionPrefixBlock40
import Current1094CompanionPrefixBlock41
import Current1094CompanionPrefixBlock42
import Current1094CompanionPrefixBlock43
import Current1094CompanionPrefixBlock44
import Current1094CompanionPrefixBlock45
import Current1094CompanionPrefixBlock46
import Current1094CompanionPrefixBlock47
import Current1094CompanionPrefixBlock48
import Current1094CompanionPrefixBlock49
import Current1094CompanionPrefixBlock50
import Current1094CompanionPrefixBlock51
import Current1094CompanionPrefixBlock52
import Current1094CompanionPrefixBlock53
import Current1094CompanionPrefixBlock54
import Current1094CompanionPrefixBlock55
import Current1094CompanionPrefixBlock56
import Current1094CompanionPrefixBlock57
import Current1094CompanionPrefixBlock58
import Current1094CompanionPrefixBlock59
import Current1094CompanionPrefixBlock60
import Current1094CompanionPrefixBlock61
import Current1094CompanionPrefixBlock62
import Current1094CompanionPrefixBlock63
import Current1094CompanionPrefixBlock64
import Current1094CompanionPrefixBlock49Backward

/-! UNCOMPILED append join for separately compiled block certificates.
No block is unfolded or recomputed by the explicit rewrite joins.
Original ec2bc862 statements/data/attribution and all parser/physical limits remain. -/
set_option Elab.async false
namespace CurrentMain.Current1094CompanionPrefixSkeleton
open CurrentMain.Current1094Helper450RelabelSlice
open CurrentMain.GuardedParsedLabelLowering

def expectedSummary : List (Nat × Mark) :=
  [(0, .phase "zero_frame_precondition"), (7401, .phase "entry_adapters"), (7559, .relabel (.inl 157)), (7621, .relabel (.inl 219)), (7632, .relabel (.inl 230)), (7910, .relabel (.inl 508)), (8106, .phase "A"), (9406, .relabel (.inl 230)), (9474, .relabel (.inl 230)), (9496, .relabel (.inl 230)), (12550, .phase "centers"), (12759, .phase "B"), (12768, .relabel (.inl 157)), (12770, .relabel (.inl 219)), (13428, .relabel (.inl 157)), (13430, .relabel (.inl 219)), (14097, .relabel (.inl 230)), (14140, .relabel (.inl 508)), (14142, .relabel (.inl 508)), (14444, .relabel (.inl 219)), (15142, .relabel (.inl 157)), (15143, .relabel (.inl 508)), (15145, .relabel (.inl 219)), (15170, .relabel (.inl 230)), (15831, .relabel (.inl 219)), (15867, .relabel (.inl 157)), (16462, .phase "cleanup_tail"), (16493, .relabel (.inl 508)), (16506, .relabel (.inl 230))]

def forwardPrefix : List Mark :=
  block00 ++ block01 ++ block02 ++ block03 ++ block04 ++ block05 ++ block06 ++ block07 ++ block08 ++ block09 ++ block10 ++ block11 ++ block12 ++ block13 ++ block14 ++ block15 ++ block16 ++ block17 ++ block18 ++ block19 ++ block20 ++ block21 ++ block22 ++ block23 ++ block24 ++ block25 ++ block26 ++ block27 ++ block28 ++ block29 ++ block30 ++ block31 ++ block32 ++ block33 ++ block34 ++ block35 ++ block36 ++ block37 ++ block38 ++ block39 ++ block40 ++ block41 ++ block42 ++ block43 ++ block44 ++ block45 ++ block46 ++ block47 ++ block48 ++ block49 ++ block50 ++ block51 ++ block52 ++ block53 ++ block54 ++ block55 ++ block56 ++ block57 ++ block58 ++ block59 ++ block60 ++ block61 ++ block62 ++ block63 ++ block64

theorem forward_length : forwardPrefix.length = 16508 := by
  rw [forwardPrefix]
  simp only [List.append_assoc]
  rw [List.length_append, block00_length]
  rw [List.length_append, block01_length]
  rw [List.length_append, block02_length]
  rw [List.length_append, block03_length]
  rw [List.length_append, block04_length]
  rw [List.length_append, block05_length]
  rw [List.length_append, block06_length]
  rw [List.length_append, block07_length]
  rw [List.length_append, block08_length]
  rw [List.length_append, block09_length]
  rw [List.length_append, block10_length]
  rw [List.length_append, block11_length]
  rw [List.length_append, block12_length]
  rw [List.length_append, block13_length]
  rw [List.length_append, block14_length]
  rw [List.length_append, block15_length]
  rw [List.length_append, block16_length]
  rw [List.length_append, block17_length]
  rw [List.length_append, block18_length]
  rw [List.length_append, block19_length]
  rw [List.length_append, block20_length]
  rw [List.length_append, block21_length]
  rw [List.length_append, block22_length]
  rw [List.length_append, block23_length]
  rw [List.length_append, block24_length]
  rw [List.length_append, block25_length]
  rw [List.length_append, block26_length]
  rw [List.length_append, block27_length]
  rw [List.length_append, block28_length]
  rw [List.length_append, block29_length]
  rw [List.length_append, block30_length]
  rw [List.length_append, block31_length]
  rw [List.length_append, block32_length]
  rw [List.length_append, block33_length]
  rw [List.length_append, block34_length]
  rw [List.length_append, block35_length]
  rw [List.length_append, block36_length]
  rw [List.length_append, block37_length]
  rw [List.length_append, block38_length]
  rw [List.length_append, block39_length]
  rw [List.length_append, block40_length]
  rw [List.length_append, block41_length]
  rw [List.length_append, block42_length]
  rw [List.length_append, block43_length]
  rw [List.length_append, block44_length]
  rw [List.length_append, block45_length]
  rw [List.length_append, block46_length]
  rw [List.length_append, block47_length]
  rw [List.length_append, block48_length]
  rw [List.length_append, block49_length]
  rw [List.length_append, block50_length]
  rw [List.length_append, block51_length]
  rw [List.length_append, block52_length]
  rw [List.length_append, block53_length]
  rw [List.length_append, block54_length]
  rw [List.length_append, block55_length]
  rw [List.length_append, block56_length]
  rw [List.length_append, block57_length]
  rw [List.length_append, block58_length]
  rw [List.length_append, block59_length]
  rw [List.length_append, block60_length]
  rw [List.length_append, block61_length]
  rw [List.length_append, block62_length]
  rw [List.length_append, block63_length]
  rw [block64_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.forward_length


theorem forward_scan : scanFrom 0 forwardPrefix = expectedSummary := by
  rw [forwardPrefix]
  simp only [List.append_assoc]
  rw [scan_append, block00_scan, block00_length]
  rw [scan_append, block01_scan, block01_length]
  rw [scan_append, block02_scan, block02_length]
  rw [scan_append, block03_scan, block03_length]
  rw [scan_append, block04_scan, block04_length]
  rw [scan_append, block05_scan, block05_length]
  rw [scan_append, block06_scan, block06_length]
  rw [scan_append, block07_scan, block07_length]
  rw [scan_append, block08_scan, block08_length]
  rw [scan_append, block09_scan, block09_length]
  rw [scan_append, block10_scan, block10_length]
  rw [scan_append, block11_scan, block11_length]
  rw [scan_append, block12_scan, block12_length]
  rw [scan_append, block13_scan, block13_length]
  rw [scan_append, block14_scan, block14_length]
  rw [scan_append, block15_scan, block15_length]
  rw [scan_append, block16_scan, block16_length]
  rw [scan_append, block17_scan, block17_length]
  rw [scan_append, block18_scan, block18_length]
  rw [scan_append, block19_scan, block19_length]
  rw [scan_append, block20_scan, block20_length]
  rw [scan_append, block21_scan, block21_length]
  rw [scan_append, block22_scan, block22_length]
  rw [scan_append, block23_scan, block23_length]
  rw [scan_append, block24_scan, block24_length]
  rw [scan_append, block25_scan, block25_length]
  rw [scan_append, block26_scan, block26_length]
  rw [scan_append, block27_scan, block27_length]
  rw [scan_append, block28_scan, block28_length]
  rw [scan_append, block29_scan, block29_length]
  rw [scan_append, block30_scan, block30_length]
  rw [scan_append, block31_scan, block31_length]
  rw [scan_append, block32_scan, block32_length]
  rw [scan_append, block33_scan, block33_length]
  rw [scan_append, block34_scan, block34_length]
  rw [scan_append, block35_scan, block35_length]
  rw [scan_append, block36_scan, block36_length]
  rw [scan_append, block37_scan, block37_length]
  rw [scan_append, block38_scan, block38_length]
  rw [scan_append, block39_scan, block39_length]
  rw [scan_append, block40_scan, block40_length]
  rw [scan_append, block41_scan, block41_length]
  rw [scan_append, block42_scan, block42_length]
  rw [scan_append, block43_scan, block43_length]
  rw [scan_append, block44_scan, block44_length]
  rw [scan_append, block45_scan, block45_length]
  rw [scan_append, block46_scan, block46_length]
  rw [scan_append, block47_scan, block47_length]
  rw [scan_append, block48_scan, block48_length]
  rw [scan_append, block49_scan, block49_length]
  rw [scan_append, block50_scan, block50_length]
  rw [scan_append, block51_scan, block51_length]
  rw [scan_append, block52_scan, block52_length]
  rw [scan_append, block53_scan, block53_length]
  rw [scan_append, block54_scan, block54_length]
  rw [scan_append, block55_scan, block55_length]
  rw [scan_append, block56_scan, block56_length]
  rw [scan_append, block57_scan, block57_length]
  rw [scan_append, block58_scan, block58_length]
  rw [scan_append, block59_scan, block59_length]
  rw [scan_append, block60_scan, block60_length]
  rw [scan_append, block61_scan, block61_length]
  rw [scan_append, block62_scan, block62_length]
  rw [scan_append, block63_scan, block63_length]
  rw [block64_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.forward_scan


def backwardPrefix : List Mark :=
  block00 ++ block01 ++ block02 ++ block03 ++ block04 ++ block05 ++ block06 ++ block07 ++ block08 ++ block09 ++ block10 ++ block11 ++ block12 ++ block13 ++ block14 ++ block15 ++ block16 ++ block17 ++ block18 ++ block19 ++ block20 ++ block21 ++ block22 ++ block23 ++ block24 ++ block25 ++ block26 ++ block27 ++ block28 ++ block29 ++ block30 ++ block31 ++ block32 ++ block33 ++ block34 ++ block35 ++ block36 ++ block37 ++ block38 ++ block39 ++ block40 ++ block41 ++ block42 ++ block43 ++ block44 ++ block45 ++ block46 ++ block47 ++ block48 ++ block49Backward ++ block50 ++ block51 ++ block52 ++ block53 ++ block54 ++ block55 ++ block56 ++ block57 ++ block58 ++ block59 ++ block60 ++ block61 ++ block62 ++ block63 ++ block64

theorem backward_length : backwardPrefix.length = 16508 := by
  rw [backwardPrefix]
  simp only [List.append_assoc]
  rw [List.length_append, block00_length]
  rw [List.length_append, block01_length]
  rw [List.length_append, block02_length]
  rw [List.length_append, block03_length]
  rw [List.length_append, block04_length]
  rw [List.length_append, block05_length]
  rw [List.length_append, block06_length]
  rw [List.length_append, block07_length]
  rw [List.length_append, block08_length]
  rw [List.length_append, block09_length]
  rw [List.length_append, block10_length]
  rw [List.length_append, block11_length]
  rw [List.length_append, block12_length]
  rw [List.length_append, block13_length]
  rw [List.length_append, block14_length]
  rw [List.length_append, block15_length]
  rw [List.length_append, block16_length]
  rw [List.length_append, block17_length]
  rw [List.length_append, block18_length]
  rw [List.length_append, block19_length]
  rw [List.length_append, block20_length]
  rw [List.length_append, block21_length]
  rw [List.length_append, block22_length]
  rw [List.length_append, block23_length]
  rw [List.length_append, block24_length]
  rw [List.length_append, block25_length]
  rw [List.length_append, block26_length]
  rw [List.length_append, block27_length]
  rw [List.length_append, block28_length]
  rw [List.length_append, block29_length]
  rw [List.length_append, block30_length]
  rw [List.length_append, block31_length]
  rw [List.length_append, block32_length]
  rw [List.length_append, block33_length]
  rw [List.length_append, block34_length]
  rw [List.length_append, block35_length]
  rw [List.length_append, block36_length]
  rw [List.length_append, block37_length]
  rw [List.length_append, block38_length]
  rw [List.length_append, block39_length]
  rw [List.length_append, block40_length]
  rw [List.length_append, block41_length]
  rw [List.length_append, block42_length]
  rw [List.length_append, block43_length]
  rw [List.length_append, block44_length]
  rw [List.length_append, block45_length]
  rw [List.length_append, block46_length]
  rw [List.length_append, block47_length]
  rw [List.length_append, block48_length]
  rw [List.length_append, block49Backward_length]
  rw [List.length_append, block50_length]
  rw [List.length_append, block51_length]
  rw [List.length_append, block52_length]
  rw [List.length_append, block53_length]
  rw [List.length_append, block54_length]
  rw [List.length_append, block55_length]
  rw [List.length_append, block56_length]
  rw [List.length_append, block57_length]
  rw [List.length_append, block58_length]
  rw [List.length_append, block59_length]
  rw [List.length_append, block60_length]
  rw [List.length_append, block61_length]
  rw [List.length_append, block62_length]
  rw [List.length_append, block63_length]
  rw [block64_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.backward_length


theorem backward_scan : scanFrom 0 backwardPrefix = expectedSummary := by
  rw [backwardPrefix]
  simp only [List.append_assoc]
  rw [scan_append, block00_scan, block00_length]
  rw [scan_append, block01_scan, block01_length]
  rw [scan_append, block02_scan, block02_length]
  rw [scan_append, block03_scan, block03_length]
  rw [scan_append, block04_scan, block04_length]
  rw [scan_append, block05_scan, block05_length]
  rw [scan_append, block06_scan, block06_length]
  rw [scan_append, block07_scan, block07_length]
  rw [scan_append, block08_scan, block08_length]
  rw [scan_append, block09_scan, block09_length]
  rw [scan_append, block10_scan, block10_length]
  rw [scan_append, block11_scan, block11_length]
  rw [scan_append, block12_scan, block12_length]
  rw [scan_append, block13_scan, block13_length]
  rw [scan_append, block14_scan, block14_length]
  rw [scan_append, block15_scan, block15_length]
  rw [scan_append, block16_scan, block16_length]
  rw [scan_append, block17_scan, block17_length]
  rw [scan_append, block18_scan, block18_length]
  rw [scan_append, block19_scan, block19_length]
  rw [scan_append, block20_scan, block20_length]
  rw [scan_append, block21_scan, block21_length]
  rw [scan_append, block22_scan, block22_length]
  rw [scan_append, block23_scan, block23_length]
  rw [scan_append, block24_scan, block24_length]
  rw [scan_append, block25_scan, block25_length]
  rw [scan_append, block26_scan, block26_length]
  rw [scan_append, block27_scan, block27_length]
  rw [scan_append, block28_scan, block28_length]
  rw [scan_append, block29_scan, block29_length]
  rw [scan_append, block30_scan, block30_length]
  rw [scan_append, block31_scan, block31_length]
  rw [scan_append, block32_scan, block32_length]
  rw [scan_append, block33_scan, block33_length]
  rw [scan_append, block34_scan, block34_length]
  rw [scan_append, block35_scan, block35_length]
  rw [scan_append, block36_scan, block36_length]
  rw [scan_append, block37_scan, block37_length]
  rw [scan_append, block38_scan, block38_length]
  rw [scan_append, block39_scan, block39_length]
  rw [scan_append, block40_scan, block40_length]
  rw [scan_append, block41_scan, block41_length]
  rw [scan_append, block42_scan, block42_length]
  rw [scan_append, block43_scan, block43_length]
  rw [scan_append, block44_scan, block44_length]
  rw [scan_append, block45_scan, block45_length]
  rw [scan_append, block46_scan, block46_length]
  rw [scan_append, block47_scan, block47_length]
  rw [scan_append, block48_scan, block48_length]
  rw [scan_append, block49Backward_scan, block49Backward_length]
  rw [scan_append, block50_scan, block50_length]
  rw [scan_append, block51_scan, block51_length]
  rw [scan_append, block52_scan, block52_length]
  rw [scan_append, block53_scan, block53_length]
  rw [scan_append, block54_scan, block54_length]
  rw [scan_append, block55_scan, block55_length]
  rw [scan_append, block56_scan, block56_length]
  rw [scan_append, block57_scan, block57_length]
  rw [scan_append, block58_scan, block58_length]
  rw [scan_append, block59_scan, block59_length]
  rw [scan_append, block60_scan, block60_length]
  rw [scan_append, block61_scan, block61_length]
  rw [scan_append, block62_scan, block62_length]
  rw [scan_append, block63_scan, block63_length]
  rw [block64_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.backward_scan


def phaseEntry : Nat × Mark → Option (Nat × String)
  | (n,.phase s) => some (n,s)
  | _ => none

def phases : List (Nat × String) :=
  [(0,"zero_frame_precondition"), (7401,"entry_adapters"), (8106,"A"),
   (12550,"centers"), (12759,"B"), (16462,"cleanup_tail")]

theorem complete_phase_positions :
    (scanFrom 0 forwardPrefix).filterMap phaseEntry = phases ∧
    (scanFrom 0 backwardPrefix).filterMap phaseEntry = phases := by
  rw [forward_scan, backward_scan]
  exact ⟨rfl,rfl⟩
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.complete_phase_positions


/-- This complete scan includes COPY/CLEAR targets; neither adds a companion
write. Every retained write has the exact accepted raw index and relabel kind. -/
theorem complete_companion_writes :
    ((scanFrom 0 forwardPrefix).filter (fun p => labelTracked p.2)) =
      Current1094Helper450CompanionLabels.moves.map
        (fun m => (m.rawIndex, Mark.relabel (.inl m.register))) ∧
    ((scanFrom 0 backwardPrefix).filter (fun p => labelTracked p.2)) =
      Current1094Helper450CompanionLabels.moves.map
        (fun m => (m.rawIndex, Mark.relabel (.inl m.register))) := by
  rw [forward_scan, backward_scan]
  exact ⟨rfl,rfl⟩
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.complete_companion_writes


/-- Cut immediately before the zero-based raw row; only preceding phases count. -/
def eventCut (raw : Nat) : Nat :=
  raw - (phases.filter (fun p => p.1 < raw)).length

theorem all_move_phase_cuts :
    Current1094CompanionDecodedRows.selectedRawIndices.map eventCut =
      Current1094CompanionDecodedRows.selectedEventIndices := by rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.all_move_phase_cuts


def queryRawIndices : List Nat := [12769,12771,13949,14144,15147,16495,16507]
def queryEventIndices : List Nat := [12764,12766,13944,14139,15142,16489,16501]

theorem all_query_phase_cuts :
    queryRawIndices.map eventCut = queryEventIndices := by rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.all_query_phase_cuts


def precedingWrites (raw : Nat) : Nat :=
  (expectedSummary.filter (fun p => labelTracked p.2 && decide (p.1 < raw))).length

theorem all_query_projection_lengths :
    queryRawIndices.map precedingWrites = [8,9,11,14,18,22,23] := by rfl


#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.all_query_projection_lengths
end CurrentMain.Current1094CompanionPrefixSkeleton
