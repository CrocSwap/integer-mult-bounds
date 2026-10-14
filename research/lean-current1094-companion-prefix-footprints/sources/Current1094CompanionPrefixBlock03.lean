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

def block03Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block03Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block03Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block03Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block03Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block03Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block03Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block03Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block03 : List Mark :=
  block03Piece00 ++ block03Piece01 ++ block03Piece02 ++ block03Piece03 ++ block03Piece04 ++ block03Piece05 ++ block03Piece06 ++ block03Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03

theorem block03Piece00_length : block03Piece00.length = 32 := by
  simp only [block03Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block03Piece00_scan : scanFrom 768 block03Piece00 =
    [] := by
  simpa only [block03Piece00] using (scan_passive 768 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03Piece00_scan

theorem block03Piece01_length : block03Piece01.length = 32 := by
  simp only [block03Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block03Piece01_scan : scanFrom 800 block03Piece01 =
    [] := by
  simpa only [block03Piece01] using (scan_passive 800 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03Piece01_scan

theorem block03Piece02_length : block03Piece02.length = 32 := by
  simp only [block03Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block03Piece02_scan : scanFrom 832 block03Piece02 =
    [] := by
  simpa only [block03Piece02] using (scan_passive 832 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03Piece02_scan

theorem block03Piece03_length : block03Piece03.length = 32 := by
  simp only [block03Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block03Piece03_scan : scanFrom 864 block03Piece03 =
    [] := by
  simpa only [block03Piece03] using (scan_passive 864 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03Piece03_scan

theorem block03Piece04_length : block03Piece04.length = 32 := by
  simp only [block03Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block03Piece04_scan : scanFrom 896 block03Piece04 =
    [] := by
  simpa only [block03Piece04] using (scan_passive 896 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03Piece04_scan

theorem block03Piece05_length : block03Piece05.length = 32 := by
  simp only [block03Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block03Piece05_scan : scanFrom 928 block03Piece05 =
    [] := by
  simpa only [block03Piece05] using (scan_passive 928 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03Piece05_scan

theorem block03Piece06_length : block03Piece06.length = 32 := by
  simp only [block03Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block03Piece06_scan : scanFrom 960 block03Piece06 =
    [] := by
  simpa only [block03Piece06] using (scan_passive 960 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03Piece06_scan

theorem block03Piece07_length : block03Piece07.length = 32 := by
  simp only [block03Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block03Piece07_scan : scanFrom 992 block03Piece07 =
    [] := by
  simpa only [block03Piece07] using (scan_passive 992 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03Piece07_scan

theorem block03_length : block03.length = 256 := by
  rw [block03]
  simp only [List.append_assoc]
  rw [List.length_append, block03Piece00_length]
  rw [List.length_append, block03Piece01_length]
  rw [List.length_append, block03Piece02_length]
  rw [List.length_append, block03Piece03_length]
  rw [List.length_append, block03Piece04_length]
  rw [List.length_append, block03Piece05_length]
  rw [List.length_append, block03Piece06_length]
  rw [block03Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03_length

theorem block03_scan : scanFrom 768 block03 =
    [] := by
  rw [block03]
  simp only [List.append_assoc]
  rw [scan_append, block03Piece00_scan, block03Piece00_length]
  rw [scan_append, block03Piece01_scan, block03Piece01_length]
  rw [scan_append, block03Piece02_scan, block03Piece02_length]
  rw [scan_append, block03Piece03_scan, block03Piece03_length]
  rw [scan_append, block03Piece04_scan, block03Piece04_length]
  rw [scan_append, block03Piece05_scan, block03Piece05_length]
  rw [scan_append, block03Piece06_scan, block03Piece06_length]
  rw [block03Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block03_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
