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

def block26Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block26Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block26Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block26Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block26Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block26Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block26Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block26Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block26 : List Mark :=
  block26Piece00 ++ block26Piece01 ++ block26Piece02 ++ block26Piece03 ++ block26Piece04 ++ block26Piece05 ++ block26Piece06 ++ block26Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26

theorem block26Piece00_length : block26Piece00.length = 32 := by
  simp only [block26Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block26Piece00_scan : scanFrom 6656 block26Piece00 =
    [] := by
  simpa only [block26Piece00] using (scan_passive 6656 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26Piece00_scan

theorem block26Piece01_length : block26Piece01.length = 32 := by
  simp only [block26Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block26Piece01_scan : scanFrom 6688 block26Piece01 =
    [] := by
  simpa only [block26Piece01] using (scan_passive 6688 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26Piece01_scan

theorem block26Piece02_length : block26Piece02.length = 32 := by
  simp only [block26Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block26Piece02_scan : scanFrom 6720 block26Piece02 =
    [] := by
  simpa only [block26Piece02] using (scan_passive 6720 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26Piece02_scan

theorem block26Piece03_length : block26Piece03.length = 32 := by
  simp only [block26Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block26Piece03_scan : scanFrom 6752 block26Piece03 =
    [] := by
  simpa only [block26Piece03] using (scan_passive 6752 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26Piece03_scan

theorem block26Piece04_length : block26Piece04.length = 32 := by
  simp only [block26Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block26Piece04_scan : scanFrom 6784 block26Piece04 =
    [] := by
  simpa only [block26Piece04] using (scan_passive 6784 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26Piece04_scan

theorem block26Piece05_length : block26Piece05.length = 32 := by
  simp only [block26Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block26Piece05_scan : scanFrom 6816 block26Piece05 =
    [] := by
  simpa only [block26Piece05] using (scan_passive 6816 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26Piece05_scan

theorem block26Piece06_length : block26Piece06.length = 32 := by
  simp only [block26Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block26Piece06_scan : scanFrom 6848 block26Piece06 =
    [] := by
  simpa only [block26Piece06] using (scan_passive 6848 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26Piece06_scan

theorem block26Piece07_length : block26Piece07.length = 32 := by
  simp only [block26Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block26Piece07_scan : scanFrom 6880 block26Piece07 =
    [] := by
  simpa only [block26Piece07] using (scan_passive 6880 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26Piece07_scan

theorem block26_length : block26.length = 256 := by
  rw [block26]
  simp only [List.append_assoc]
  rw [List.length_append, block26Piece00_length]
  rw [List.length_append, block26Piece01_length]
  rw [List.length_append, block26Piece02_length]
  rw [List.length_append, block26Piece03_length]
  rw [List.length_append, block26Piece04_length]
  rw [List.length_append, block26Piece05_length]
  rw [List.length_append, block26Piece06_length]
  rw [block26Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26_length

theorem block26_scan : scanFrom 6656 block26 =
    [] := by
  rw [block26]
  simp only [List.append_assoc]
  rw [scan_append, block26Piece00_scan, block26Piece00_length]
  rw [scan_append, block26Piece01_scan, block26Piece01_length]
  rw [scan_append, block26Piece02_scan, block26Piece02_length]
  rw [scan_append, block26Piece03_scan, block26Piece03_length]
  rw [scan_append, block26Piece04_scan, block26Piece04_length]
  rw [scan_append, block26Piece05_scan, block26Piece05_length]
  rw [scan_append, block26Piece06_scan, block26Piece06_length]
  rw [block26Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block26_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
