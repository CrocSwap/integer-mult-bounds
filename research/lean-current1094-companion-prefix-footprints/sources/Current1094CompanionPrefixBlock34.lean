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

def block34Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block34Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block34Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block34Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block34Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block34Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block34Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block34Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block34 : List Mark :=
  block34Piece00 ++ block34Piece01 ++ block34Piece02 ++ block34Piece03 ++ block34Piece04 ++ block34Piece05 ++ block34Piece06 ++ block34Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34

theorem block34Piece00_length : block34Piece00.length = 32 := by
  simp only [block34Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block34Piece00_scan : scanFrom 8704 block34Piece00 =
    [] := by
  simpa only [block34Piece00] using (scan_passive 8704 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34Piece00_scan

theorem block34Piece01_length : block34Piece01.length = 32 := by
  simp only [block34Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block34Piece01_scan : scanFrom 8736 block34Piece01 =
    [] := by
  simpa only [block34Piece01] using (scan_passive 8736 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34Piece01_scan

theorem block34Piece02_length : block34Piece02.length = 32 := by
  simp only [block34Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block34Piece02_scan : scanFrom 8768 block34Piece02 =
    [] := by
  simpa only [block34Piece02] using (scan_passive 8768 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34Piece02_scan

theorem block34Piece03_length : block34Piece03.length = 32 := by
  simp only [block34Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block34Piece03_scan : scanFrom 8800 block34Piece03 =
    [] := by
  simpa only [block34Piece03] using (scan_passive 8800 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34Piece03_scan

theorem block34Piece04_length : block34Piece04.length = 32 := by
  simp only [block34Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block34Piece04_scan : scanFrom 8832 block34Piece04 =
    [] := by
  simpa only [block34Piece04] using (scan_passive 8832 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34Piece04_scan

theorem block34Piece05_length : block34Piece05.length = 32 := by
  simp only [block34Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block34Piece05_scan : scanFrom 8864 block34Piece05 =
    [] := by
  simpa only [block34Piece05] using (scan_passive 8864 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34Piece05_scan

theorem block34Piece06_length : block34Piece06.length = 32 := by
  simp only [block34Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block34Piece06_scan : scanFrom 8896 block34Piece06 =
    [] := by
  simpa only [block34Piece06] using (scan_passive 8896 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34Piece06_scan

theorem block34Piece07_length : block34Piece07.length = 32 := by
  simp only [block34Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block34Piece07_scan : scanFrom 8928 block34Piece07 =
    [] := by
  simpa only [block34Piece07] using (scan_passive 8928 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34Piece07_scan

theorem block34_length : block34.length = 256 := by
  rw [block34]
  simp only [List.append_assoc]
  rw [List.length_append, block34Piece00_length]
  rw [List.length_append, block34Piece01_length]
  rw [List.length_append, block34Piece02_length]
  rw [List.length_append, block34Piece03_length]
  rw [List.length_append, block34Piece04_length]
  rw [List.length_append, block34Piece05_length]
  rw [List.length_append, block34Piece06_length]
  rw [block34Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34_length

theorem block34_scan : scanFrom 8704 block34 =
    [] := by
  rw [block34]
  simp only [List.append_assoc]
  rw [scan_append, block34Piece00_scan, block34Piece00_length]
  rw [scan_append, block34Piece01_scan, block34Piece01_length]
  rw [scan_append, block34Piece02_scan, block34Piece02_length]
  rw [scan_append, block34Piece03_scan, block34Piece03_length]
  rw [scan_append, block34Piece04_scan, block34Piece04_length]
  rw [scan_append, block34Piece05_scan, block34Piece05_length]
  rw [scan_append, block34Piece06_scan, block34Piece06_length]
  rw [block34Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block34_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
