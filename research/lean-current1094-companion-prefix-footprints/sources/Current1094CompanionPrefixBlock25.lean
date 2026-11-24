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

def block25Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block25Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block25Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block25Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block25Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block25Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block25Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block25Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block25 : List Mark :=
  block25Piece00 ++ block25Piece01 ++ block25Piece02 ++ block25Piece03 ++ block25Piece04 ++ block25Piece05 ++ block25Piece06 ++ block25Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25

theorem block25Piece00_length : block25Piece00.length = 32 := by
  simp only [block25Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block25Piece00_scan : scanFrom 6400 block25Piece00 =
    [] := by
  simpa only [block25Piece00] using (scan_passive 6400 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25Piece00_scan

theorem block25Piece01_length : block25Piece01.length = 32 := by
  simp only [block25Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block25Piece01_scan : scanFrom 6432 block25Piece01 =
    [] := by
  simpa only [block25Piece01] using (scan_passive 6432 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25Piece01_scan

theorem block25Piece02_length : block25Piece02.length = 32 := by
  simp only [block25Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block25Piece02_scan : scanFrom 6464 block25Piece02 =
    [] := by
  simpa only [block25Piece02] using (scan_passive 6464 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25Piece02_scan

theorem block25Piece03_length : block25Piece03.length = 32 := by
  simp only [block25Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block25Piece03_scan : scanFrom 6496 block25Piece03 =
    [] := by
  simpa only [block25Piece03] using (scan_passive 6496 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25Piece03_scan

theorem block25Piece04_length : block25Piece04.length = 32 := by
  simp only [block25Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block25Piece04_scan : scanFrom 6528 block25Piece04 =
    [] := by
  simpa only [block25Piece04] using (scan_passive 6528 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25Piece04_scan

theorem block25Piece05_length : block25Piece05.length = 32 := by
  simp only [block25Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block25Piece05_scan : scanFrom 6560 block25Piece05 =
    [] := by
  simpa only [block25Piece05] using (scan_passive 6560 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25Piece05_scan

theorem block25Piece06_length : block25Piece06.length = 32 := by
  simp only [block25Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block25Piece06_scan : scanFrom 6592 block25Piece06 =
    [] := by
  simpa only [block25Piece06] using (scan_passive 6592 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25Piece06_scan

theorem block25Piece07_length : block25Piece07.length = 32 := by
  simp only [block25Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block25Piece07_scan : scanFrom 6624 block25Piece07 =
    [] := by
  simpa only [block25Piece07] using (scan_passive 6624 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25Piece07_scan

theorem block25_length : block25.length = 256 := by
  rw [block25]
  simp only [List.append_assoc]
  rw [List.length_append, block25Piece00_length]
  rw [List.length_append, block25Piece01_length]
  rw [List.length_append, block25Piece02_length]
  rw [List.length_append, block25Piece03_length]
  rw [List.length_append, block25Piece04_length]
  rw [List.length_append, block25Piece05_length]
  rw [List.length_append, block25Piece06_length]
  rw [block25Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25_length

theorem block25_scan : scanFrom 6400 block25 =
    [] := by
  rw [block25]
  simp only [List.append_assoc]
  rw [scan_append, block25Piece00_scan, block25Piece00_length]
  rw [scan_append, block25Piece01_scan, block25Piece01_length]
  rw [scan_append, block25Piece02_scan, block25Piece02_length]
  rw [scan_append, block25Piece03_scan, block25Piece03_length]
  rw [scan_append, block25Piece04_scan, block25Piece04_length]
  rw [scan_append, block25Piece05_scan, block25Piece05_length]
  rw [scan_append, block25Piece06_scan, block25Piece06_length]
  rw [block25Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block25_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
