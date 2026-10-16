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

def block35Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block35Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block35Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block35Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block35Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block35Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block35Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block35Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block35 : List Mark :=
  block35Piece00 ++ block35Piece01 ++ block35Piece02 ++ block35Piece03 ++ block35Piece04 ++ block35Piece05 ++ block35Piece06 ++ block35Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35

theorem block35Piece00_length : block35Piece00.length = 32 := by
  simp only [block35Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block35Piece00_scan : scanFrom 8960 block35Piece00 =
    [] := by
  simpa only [block35Piece00] using (scan_passive 8960 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35Piece00_scan

theorem block35Piece01_length : block35Piece01.length = 32 := by
  simp only [block35Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block35Piece01_scan : scanFrom 8992 block35Piece01 =
    [] := by
  simpa only [block35Piece01] using (scan_passive 8992 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35Piece01_scan

theorem block35Piece02_length : block35Piece02.length = 32 := by
  simp only [block35Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block35Piece02_scan : scanFrom 9024 block35Piece02 =
    [] := by
  simpa only [block35Piece02] using (scan_passive 9024 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35Piece02_scan

theorem block35Piece03_length : block35Piece03.length = 32 := by
  simp only [block35Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block35Piece03_scan : scanFrom 9056 block35Piece03 =
    [] := by
  simpa only [block35Piece03] using (scan_passive 9056 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35Piece03_scan

theorem block35Piece04_length : block35Piece04.length = 32 := by
  simp only [block35Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block35Piece04_scan : scanFrom 9088 block35Piece04 =
    [] := by
  simpa only [block35Piece04] using (scan_passive 9088 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35Piece04_scan

theorem block35Piece05_length : block35Piece05.length = 32 := by
  simp only [block35Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block35Piece05_scan : scanFrom 9120 block35Piece05 =
    [] := by
  simpa only [block35Piece05] using (scan_passive 9120 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35Piece05_scan

theorem block35Piece06_length : block35Piece06.length = 32 := by
  simp only [block35Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block35Piece06_scan : scanFrom 9152 block35Piece06 =
    [] := by
  simpa only [block35Piece06] using (scan_passive 9152 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35Piece06_scan

theorem block35Piece07_length : block35Piece07.length = 32 := by
  simp only [block35Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block35Piece07_scan : scanFrom 9184 block35Piece07 =
    [] := by
  simpa only [block35Piece07] using (scan_passive 9184 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35Piece07_scan

theorem block35_length : block35.length = 256 := by
  rw [block35]
  simp only [List.append_assoc]
  rw [List.length_append, block35Piece00_length]
  rw [List.length_append, block35Piece01_length]
  rw [List.length_append, block35Piece02_length]
  rw [List.length_append, block35Piece03_length]
  rw [List.length_append, block35Piece04_length]
  rw [List.length_append, block35Piece05_length]
  rw [List.length_append, block35Piece06_length]
  rw [block35Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35_length

theorem block35_scan : scanFrom 8960 block35 =
    [] := by
  rw [block35]
  simp only [List.append_assoc]
  rw [scan_append, block35Piece00_scan, block35Piece00_length]
  rw [scan_append, block35Piece01_scan, block35Piece01_length]
  rw [scan_append, block35Piece02_scan, block35Piece02_length]
  rw [scan_append, block35Piece03_scan, block35Piece03_length]
  rw [scan_append, block35Piece04_scan, block35Piece04_length]
  rw [scan_append, block35Piece05_scan, block35Piece05_length]
  rw [scan_append, block35Piece06_scan, block35Piece06_length]
  rw [block35Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block35_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
