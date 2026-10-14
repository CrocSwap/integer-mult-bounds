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

def block27Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block27Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block27Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block27Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block27Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block27Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block27Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block27Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block27 : List Mark :=
  block27Piece00 ++ block27Piece01 ++ block27Piece02 ++ block27Piece03 ++ block27Piece04 ++ block27Piece05 ++ block27Piece06 ++ block27Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27

theorem block27Piece00_length : block27Piece00.length = 32 := by
  simp only [block27Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block27Piece00_scan : scanFrom 6912 block27Piece00 =
    [] := by
  simpa only [block27Piece00] using (scan_passive 6912 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27Piece00_scan

theorem block27Piece01_length : block27Piece01.length = 32 := by
  simp only [block27Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block27Piece01_scan : scanFrom 6944 block27Piece01 =
    [] := by
  simpa only [block27Piece01] using (scan_passive 6944 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27Piece01_scan

theorem block27Piece02_length : block27Piece02.length = 32 := by
  simp only [block27Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block27Piece02_scan : scanFrom 6976 block27Piece02 =
    [] := by
  simpa only [block27Piece02] using (scan_passive 6976 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27Piece02_scan

theorem block27Piece03_length : block27Piece03.length = 32 := by
  simp only [block27Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block27Piece03_scan : scanFrom 7008 block27Piece03 =
    [] := by
  simpa only [block27Piece03] using (scan_passive 7008 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27Piece03_scan

theorem block27Piece04_length : block27Piece04.length = 32 := by
  simp only [block27Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block27Piece04_scan : scanFrom 7040 block27Piece04 =
    [] := by
  simpa only [block27Piece04] using (scan_passive 7040 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27Piece04_scan

theorem block27Piece05_length : block27Piece05.length = 32 := by
  simp only [block27Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block27Piece05_scan : scanFrom 7072 block27Piece05 =
    [] := by
  simpa only [block27Piece05] using (scan_passive 7072 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27Piece05_scan

theorem block27Piece06_length : block27Piece06.length = 32 := by
  simp only [block27Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block27Piece06_scan : scanFrom 7104 block27Piece06 =
    [] := by
  simpa only [block27Piece06] using (scan_passive 7104 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27Piece06_scan

theorem block27Piece07_length : block27Piece07.length = 32 := by
  simp only [block27Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block27Piece07_scan : scanFrom 7136 block27Piece07 =
    [] := by
  simpa only [block27Piece07] using (scan_passive 7136 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27Piece07_scan

theorem block27_length : block27.length = 256 := by
  rw [block27]
  simp only [List.append_assoc]
  rw [List.length_append, block27Piece00_length]
  rw [List.length_append, block27Piece01_length]
  rw [List.length_append, block27Piece02_length]
  rw [List.length_append, block27Piece03_length]
  rw [List.length_append, block27Piece04_length]
  rw [List.length_append, block27Piece05_length]
  rw [List.length_append, block27Piece06_length]
  rw [block27Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27_length

theorem block27_scan : scanFrom 6912 block27 =
    [] := by
  rw [block27]
  simp only [List.append_assoc]
  rw [scan_append, block27Piece00_scan, block27Piece00_length]
  rw [scan_append, block27Piece01_scan, block27Piece01_length]
  rw [scan_append, block27Piece02_scan, block27Piece02_length]
  rw [scan_append, block27Piece03_scan, block27Piece03_length]
  rw [scan_append, block27Piece04_scan, block27Piece04_length]
  rw [scan_append, block27Piece05_scan, block27Piece05_length]
  rw [scan_append, block27Piece06_scan, block27Piece06_length]
  rw [block27Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block27_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
