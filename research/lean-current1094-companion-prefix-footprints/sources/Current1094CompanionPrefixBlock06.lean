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

def block06Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block06Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block06Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block06Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block06Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block06Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block06Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block06Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block06 : List Mark :=
  block06Piece00 ++ block06Piece01 ++ block06Piece02 ++ block06Piece03 ++ block06Piece04 ++ block06Piece05 ++ block06Piece06 ++ block06Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06

theorem block06Piece00_length : block06Piece00.length = 32 := by
  simp only [block06Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block06Piece00_scan : scanFrom 1536 block06Piece00 =
    [] := by
  simpa only [block06Piece00] using (scan_passive 1536 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06Piece00_scan

theorem block06Piece01_length : block06Piece01.length = 32 := by
  simp only [block06Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block06Piece01_scan : scanFrom 1568 block06Piece01 =
    [] := by
  simpa only [block06Piece01] using (scan_passive 1568 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06Piece01_scan

theorem block06Piece02_length : block06Piece02.length = 32 := by
  simp only [block06Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block06Piece02_scan : scanFrom 1600 block06Piece02 =
    [] := by
  simpa only [block06Piece02] using (scan_passive 1600 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06Piece02_scan

theorem block06Piece03_length : block06Piece03.length = 32 := by
  simp only [block06Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block06Piece03_scan : scanFrom 1632 block06Piece03 =
    [] := by
  simpa only [block06Piece03] using (scan_passive 1632 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06Piece03_scan

theorem block06Piece04_length : block06Piece04.length = 32 := by
  simp only [block06Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block06Piece04_scan : scanFrom 1664 block06Piece04 =
    [] := by
  simpa only [block06Piece04] using (scan_passive 1664 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06Piece04_scan

theorem block06Piece05_length : block06Piece05.length = 32 := by
  simp only [block06Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block06Piece05_scan : scanFrom 1696 block06Piece05 =
    [] := by
  simpa only [block06Piece05] using (scan_passive 1696 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06Piece05_scan

theorem block06Piece06_length : block06Piece06.length = 32 := by
  simp only [block06Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block06Piece06_scan : scanFrom 1728 block06Piece06 =
    [] := by
  simpa only [block06Piece06] using (scan_passive 1728 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06Piece06_scan

theorem block06Piece07_length : block06Piece07.length = 32 := by
  simp only [block06Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block06Piece07_scan : scanFrom 1760 block06Piece07 =
    [] := by
  simpa only [block06Piece07] using (scan_passive 1760 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06Piece07_scan

theorem block06_length : block06.length = 256 := by
  rw [block06]
  simp only [List.append_assoc]
  rw [List.length_append, block06Piece00_length]
  rw [List.length_append, block06Piece01_length]
  rw [List.length_append, block06Piece02_length]
  rw [List.length_append, block06Piece03_length]
  rw [List.length_append, block06Piece04_length]
  rw [List.length_append, block06Piece05_length]
  rw [List.length_append, block06Piece06_length]
  rw [block06Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06_length

theorem block06_scan : scanFrom 1536 block06 =
    [] := by
  rw [block06]
  simp only [List.append_assoc]
  rw [scan_append, block06Piece00_scan, block06Piece00_length]
  rw [scan_append, block06Piece01_scan, block06Piece01_length]
  rw [scan_append, block06Piece02_scan, block06Piece02_length]
  rw [scan_append, block06Piece03_scan, block06Piece03_length]
  rw [scan_append, block06Piece04_scan, block06Piece04_length]
  rw [scan_append, block06Piece05_scan, block06Piece05_length]
  rw [scan_append, block06Piece06_scan, block06Piece06_length]
  rw [block06Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block06_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
