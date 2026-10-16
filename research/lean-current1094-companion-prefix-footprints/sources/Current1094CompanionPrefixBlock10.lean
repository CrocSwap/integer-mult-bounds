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

def block10Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block10Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block10Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block10Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block10Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block10Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block10Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block10Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block10 : List Mark :=
  block10Piece00 ++ block10Piece01 ++ block10Piece02 ++ block10Piece03 ++ block10Piece04 ++ block10Piece05 ++ block10Piece06 ++ block10Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10

theorem block10Piece00_length : block10Piece00.length = 32 := by
  simp only [block10Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block10Piece00_scan : scanFrom 2560 block10Piece00 =
    [] := by
  simpa only [block10Piece00] using (scan_passive 2560 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10Piece00_scan

theorem block10Piece01_length : block10Piece01.length = 32 := by
  simp only [block10Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block10Piece01_scan : scanFrom 2592 block10Piece01 =
    [] := by
  simpa only [block10Piece01] using (scan_passive 2592 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10Piece01_scan

theorem block10Piece02_length : block10Piece02.length = 32 := by
  simp only [block10Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block10Piece02_scan : scanFrom 2624 block10Piece02 =
    [] := by
  simpa only [block10Piece02] using (scan_passive 2624 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10Piece02_scan

theorem block10Piece03_length : block10Piece03.length = 32 := by
  simp only [block10Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block10Piece03_scan : scanFrom 2656 block10Piece03 =
    [] := by
  simpa only [block10Piece03] using (scan_passive 2656 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10Piece03_scan

theorem block10Piece04_length : block10Piece04.length = 32 := by
  simp only [block10Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block10Piece04_scan : scanFrom 2688 block10Piece04 =
    [] := by
  simpa only [block10Piece04] using (scan_passive 2688 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10Piece04_scan

theorem block10Piece05_length : block10Piece05.length = 32 := by
  simp only [block10Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block10Piece05_scan : scanFrom 2720 block10Piece05 =
    [] := by
  simpa only [block10Piece05] using (scan_passive 2720 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10Piece05_scan

theorem block10Piece06_length : block10Piece06.length = 32 := by
  simp only [block10Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block10Piece06_scan : scanFrom 2752 block10Piece06 =
    [] := by
  simpa only [block10Piece06] using (scan_passive 2752 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10Piece06_scan

theorem block10Piece07_length : block10Piece07.length = 32 := by
  simp only [block10Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block10Piece07_scan : scanFrom 2784 block10Piece07 =
    [] := by
  simpa only [block10Piece07] using (scan_passive 2784 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10Piece07_scan

theorem block10_length : block10.length = 256 := by
  rw [block10]
  simp only [List.append_assoc]
  rw [List.length_append, block10Piece00_length]
  rw [List.length_append, block10Piece01_length]
  rw [List.length_append, block10Piece02_length]
  rw [List.length_append, block10Piece03_length]
  rw [List.length_append, block10Piece04_length]
  rw [List.length_append, block10Piece05_length]
  rw [List.length_append, block10Piece06_length]
  rw [block10Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10_length

theorem block10_scan : scanFrom 2560 block10 =
    [] := by
  rw [block10]
  simp only [List.append_assoc]
  rw [scan_append, block10Piece00_scan, block10Piece00_length]
  rw [scan_append, block10Piece01_scan, block10Piece01_length]
  rw [scan_append, block10Piece02_scan, block10Piece02_length]
  rw [scan_append, block10Piece03_scan, block10Piece03_length]
  rw [scan_append, block10Piece04_scan, block10Piece04_length]
  rw [scan_append, block10Piece05_scan, block10Piece05_length]
  rw [scan_append, block10Piece06_scan, block10Piece06_length]
  rw [block10Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block10_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
