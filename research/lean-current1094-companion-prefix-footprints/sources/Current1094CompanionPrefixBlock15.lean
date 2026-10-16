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

def block15Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block15Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block15Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block15Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block15Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block15Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block15Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block15Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block15 : List Mark :=
  block15Piece00 ++ block15Piece01 ++ block15Piece02 ++ block15Piece03 ++ block15Piece04 ++ block15Piece05 ++ block15Piece06 ++ block15Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15

theorem block15Piece00_length : block15Piece00.length = 32 := by
  simp only [block15Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block15Piece00_scan : scanFrom 3840 block15Piece00 =
    [] := by
  simpa only [block15Piece00] using (scan_passive 3840 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15Piece00_scan

theorem block15Piece01_length : block15Piece01.length = 32 := by
  simp only [block15Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block15Piece01_scan : scanFrom 3872 block15Piece01 =
    [] := by
  simpa only [block15Piece01] using (scan_passive 3872 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15Piece01_scan

theorem block15Piece02_length : block15Piece02.length = 32 := by
  simp only [block15Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block15Piece02_scan : scanFrom 3904 block15Piece02 =
    [] := by
  simpa only [block15Piece02] using (scan_passive 3904 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15Piece02_scan

theorem block15Piece03_length : block15Piece03.length = 32 := by
  simp only [block15Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block15Piece03_scan : scanFrom 3936 block15Piece03 =
    [] := by
  simpa only [block15Piece03] using (scan_passive 3936 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15Piece03_scan

theorem block15Piece04_length : block15Piece04.length = 32 := by
  simp only [block15Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block15Piece04_scan : scanFrom 3968 block15Piece04 =
    [] := by
  simpa only [block15Piece04] using (scan_passive 3968 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15Piece04_scan

theorem block15Piece05_length : block15Piece05.length = 32 := by
  simp only [block15Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block15Piece05_scan : scanFrom 4000 block15Piece05 =
    [] := by
  simpa only [block15Piece05] using (scan_passive 4000 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15Piece05_scan

theorem block15Piece06_length : block15Piece06.length = 32 := by
  simp only [block15Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block15Piece06_scan : scanFrom 4032 block15Piece06 =
    [] := by
  simpa only [block15Piece06] using (scan_passive 4032 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15Piece06_scan

theorem block15Piece07_length : block15Piece07.length = 32 := by
  simp only [block15Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block15Piece07_scan : scanFrom 4064 block15Piece07 =
    [] := by
  simpa only [block15Piece07] using (scan_passive 4064 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15Piece07_scan

theorem block15_length : block15.length = 256 := by
  rw [block15]
  simp only [List.append_assoc]
  rw [List.length_append, block15Piece00_length]
  rw [List.length_append, block15Piece01_length]
  rw [List.length_append, block15Piece02_length]
  rw [List.length_append, block15Piece03_length]
  rw [List.length_append, block15Piece04_length]
  rw [List.length_append, block15Piece05_length]
  rw [List.length_append, block15Piece06_length]
  rw [block15Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15_length

theorem block15_scan : scanFrom 3840 block15 =
    [] := by
  rw [block15]
  simp only [List.append_assoc]
  rw [scan_append, block15Piece00_scan, block15Piece00_length]
  rw [scan_append, block15Piece01_scan, block15Piece01_length]
  rw [scan_append, block15Piece02_scan, block15Piece02_length]
  rw [scan_append, block15Piece03_scan, block15Piece03_length]
  rw [scan_append, block15Piece04_scan, block15Piece04_length]
  rw [scan_append, block15Piece05_scan, block15Piece05_length]
  rw [scan_append, block15Piece06_scan, block15Piece06_length]
  rw [block15Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block15_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
