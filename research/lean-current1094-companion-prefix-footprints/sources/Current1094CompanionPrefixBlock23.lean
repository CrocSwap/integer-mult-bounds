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

def block23Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block23Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block23Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block23Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block23Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block23Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block23Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block23Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block23 : List Mark :=
  block23Piece00 ++ block23Piece01 ++ block23Piece02 ++ block23Piece03 ++ block23Piece04 ++ block23Piece05 ++ block23Piece06 ++ block23Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23

theorem block23Piece00_length : block23Piece00.length = 32 := by
  simp only [block23Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block23Piece00_scan : scanFrom 5888 block23Piece00 =
    [] := by
  simpa only [block23Piece00] using (scan_passive 5888 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23Piece00_scan

theorem block23Piece01_length : block23Piece01.length = 32 := by
  simp only [block23Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block23Piece01_scan : scanFrom 5920 block23Piece01 =
    [] := by
  simpa only [block23Piece01] using (scan_passive 5920 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23Piece01_scan

theorem block23Piece02_length : block23Piece02.length = 32 := by
  simp only [block23Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block23Piece02_scan : scanFrom 5952 block23Piece02 =
    [] := by
  simpa only [block23Piece02] using (scan_passive 5952 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23Piece02_scan

theorem block23Piece03_length : block23Piece03.length = 32 := by
  simp only [block23Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block23Piece03_scan : scanFrom 5984 block23Piece03 =
    [] := by
  simpa only [block23Piece03] using (scan_passive 5984 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23Piece03_scan

theorem block23Piece04_length : block23Piece04.length = 32 := by
  simp only [block23Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block23Piece04_scan : scanFrom 6016 block23Piece04 =
    [] := by
  simpa only [block23Piece04] using (scan_passive 6016 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23Piece04_scan

theorem block23Piece05_length : block23Piece05.length = 32 := by
  simp only [block23Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block23Piece05_scan : scanFrom 6048 block23Piece05 =
    [] := by
  simpa only [block23Piece05] using (scan_passive 6048 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23Piece05_scan

theorem block23Piece06_length : block23Piece06.length = 32 := by
  simp only [block23Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block23Piece06_scan : scanFrom 6080 block23Piece06 =
    [] := by
  simpa only [block23Piece06] using (scan_passive 6080 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23Piece06_scan

theorem block23Piece07_length : block23Piece07.length = 32 := by
  simp only [block23Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block23Piece07_scan : scanFrom 6112 block23Piece07 =
    [] := by
  simpa only [block23Piece07] using (scan_passive 6112 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23Piece07_scan

theorem block23_length : block23.length = 256 := by
  rw [block23]
  simp only [List.append_assoc]
  rw [List.length_append, block23Piece00_length]
  rw [List.length_append, block23Piece01_length]
  rw [List.length_append, block23Piece02_length]
  rw [List.length_append, block23Piece03_length]
  rw [List.length_append, block23Piece04_length]
  rw [List.length_append, block23Piece05_length]
  rw [List.length_append, block23Piece06_length]
  rw [block23Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23_length

theorem block23_scan : scanFrom 5888 block23 =
    [] := by
  rw [block23]
  simp only [List.append_assoc]
  rw [scan_append, block23Piece00_scan, block23Piece00_length]
  rw [scan_append, block23Piece01_scan, block23Piece01_length]
  rw [scan_append, block23Piece02_scan, block23Piece02_length]
  rw [scan_append, block23Piece03_scan, block23Piece03_length]
  rw [scan_append, block23Piece04_scan, block23Piece04_length]
  rw [scan_append, block23Piece05_scan, block23Piece05_length]
  rw [scan_append, block23Piece06_scan, block23Piece06_length]
  rw [block23Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block23_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
