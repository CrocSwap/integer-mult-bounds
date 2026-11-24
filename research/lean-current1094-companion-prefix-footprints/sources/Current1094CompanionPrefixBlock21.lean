import Current1094CompanionPrefixBlock00

/-! UNCOMPILED structural block certificate. The exact original marks are
partitioned into consecutive pieces of at most32 rows. Passive runs use the
accepted symbolic scan_passive lemma; only bounded nonpassive pieces reduce.
All source values, order, raw offset and final statements are preserved.
Original emitter/LemmaG/HyperplaneEnd/PR1611 attribution and explicit parser,
whole guarded-word and physical interpretation limits remain. Apache-2.0;
prepared with OpenAI assistance. No resource limit or selected input changes. -/
set_option Elab.async false
namespace CurrentMain.Current1094CompanionPrefixSkeleton
open CurrentMain.Current1094Helper450RelabelSlice

def block21Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block21Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block21Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block21Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block21Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block21Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block21Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block21Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block21 : List Mark :=
  block21Piece00 ++ block21Piece01 ++ block21Piece02 ++ block21Piece03 ++ block21Piece04 ++ block21Piece05 ++ block21Piece06 ++ block21Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21

theorem block21Piece00_length : block21Piece00.length = 32 := by
  simp only [block21Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block21Piece00_scan : scanFrom 5376 block21Piece00 =
    [] := by
  simpa only [block21Piece00] using (scan_passive 5376 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21Piece00_scan

theorem block21Piece01_length : block21Piece01.length = 32 := by
  simp only [block21Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block21Piece01_scan : scanFrom 5408 block21Piece01 =
    [] := by
  simpa only [block21Piece01] using (scan_passive 5408 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21Piece01_scan

theorem block21Piece02_length : block21Piece02.length = 32 := by
  simp only [block21Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block21Piece02_scan : scanFrom 5440 block21Piece02 =
    [] := by
  simpa only [block21Piece02] using (scan_passive 5440 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21Piece02_scan

theorem block21Piece03_length : block21Piece03.length = 32 := by
  simp only [block21Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block21Piece03_scan : scanFrom 5472 block21Piece03 =
    [] := by
  simpa only [block21Piece03] using (scan_passive 5472 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21Piece03_scan

theorem block21Piece04_length : block21Piece04.length = 32 := by
  simp only [block21Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block21Piece04_scan : scanFrom 5504 block21Piece04 =
    [] := by
  simpa only [block21Piece04] using (scan_passive 5504 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21Piece04_scan

theorem block21Piece05_length : block21Piece05.length = 32 := by
  simp only [block21Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block21Piece05_scan : scanFrom 5536 block21Piece05 =
    [] := by
  simpa only [block21Piece05] using (scan_passive 5536 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21Piece05_scan

theorem block21Piece06_length : block21Piece06.length = 32 := by
  simp only [block21Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block21Piece06_scan : scanFrom 5568 block21Piece06 =
    [] := by
  simpa only [block21Piece06] using (scan_passive 5568 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21Piece06_scan

theorem block21Piece07_length : block21Piece07.length = 32 := by
  simp only [block21Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block21Piece07_scan : scanFrom 5600 block21Piece07 =
    [] := by
  simpa only [block21Piece07] using (scan_passive 5600 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21Piece07_scan

theorem block21_length : block21.length = 256 := by
  rw [block21]
  simp only [List.append_assoc]
  rw [List.length_append, block21Piece00_length]
  rw [List.length_append, block21Piece01_length]
  rw [List.length_append, block21Piece02_length]
  rw [List.length_append, block21Piece03_length]
  rw [List.length_append, block21Piece04_length]
  rw [List.length_append, block21Piece05_length]
  rw [List.length_append, block21Piece06_length]
  rw [block21Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21_length

theorem block21_scan : scanFrom 5376 block21 =
    [] := by
  rw [block21]
  simp only [List.append_assoc]
  rw [scan_append, block21Piece00_scan, block21Piece00_length]
  rw [scan_append, block21Piece01_scan, block21Piece01_length]
  rw [scan_append, block21Piece02_scan, block21Piece02_length]
  rw [scan_append, block21Piece03_scan, block21Piece03_length]
  rw [scan_append, block21Piece04_scan, block21Piece04_length]
  rw [scan_append, block21Piece05_scan, block21Piece05_length]
  rw [scan_append, block21Piece06_scan, block21Piece06_length]
  rw [block21Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block21_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
