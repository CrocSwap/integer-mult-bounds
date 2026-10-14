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

def block09Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block09Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block09Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block09Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block09Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block09Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block09Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block09Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block09 : List Mark :=
  block09Piece00 ++ block09Piece01 ++ block09Piece02 ++ block09Piece03 ++ block09Piece04 ++ block09Piece05 ++ block09Piece06 ++ block09Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09

theorem block09Piece00_length : block09Piece00.length = 32 := by
  simp only [block09Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block09Piece00_scan : scanFrom 2304 block09Piece00 =
    [] := by
  simpa only [block09Piece00] using (scan_passive 2304 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09Piece00_scan

theorem block09Piece01_length : block09Piece01.length = 32 := by
  simp only [block09Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block09Piece01_scan : scanFrom 2336 block09Piece01 =
    [] := by
  simpa only [block09Piece01] using (scan_passive 2336 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09Piece01_scan

theorem block09Piece02_length : block09Piece02.length = 32 := by
  simp only [block09Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block09Piece02_scan : scanFrom 2368 block09Piece02 =
    [] := by
  simpa only [block09Piece02] using (scan_passive 2368 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09Piece02_scan

theorem block09Piece03_length : block09Piece03.length = 32 := by
  simp only [block09Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block09Piece03_scan : scanFrom 2400 block09Piece03 =
    [] := by
  simpa only [block09Piece03] using (scan_passive 2400 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09Piece03_scan

theorem block09Piece04_length : block09Piece04.length = 32 := by
  simp only [block09Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block09Piece04_scan : scanFrom 2432 block09Piece04 =
    [] := by
  simpa only [block09Piece04] using (scan_passive 2432 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09Piece04_scan

theorem block09Piece05_length : block09Piece05.length = 32 := by
  simp only [block09Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block09Piece05_scan : scanFrom 2464 block09Piece05 =
    [] := by
  simpa only [block09Piece05] using (scan_passive 2464 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09Piece05_scan

theorem block09Piece06_length : block09Piece06.length = 32 := by
  simp only [block09Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block09Piece06_scan : scanFrom 2496 block09Piece06 =
    [] := by
  simpa only [block09Piece06] using (scan_passive 2496 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09Piece06_scan

theorem block09Piece07_length : block09Piece07.length = 32 := by
  simp only [block09Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block09Piece07_scan : scanFrom 2528 block09Piece07 =
    [] := by
  simpa only [block09Piece07] using (scan_passive 2528 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09Piece07_scan

theorem block09_length : block09.length = 256 := by
  rw [block09]
  simp only [List.append_assoc]
  rw [List.length_append, block09Piece00_length]
  rw [List.length_append, block09Piece01_length]
  rw [List.length_append, block09Piece02_length]
  rw [List.length_append, block09Piece03_length]
  rw [List.length_append, block09Piece04_length]
  rw [List.length_append, block09Piece05_length]
  rw [List.length_append, block09Piece06_length]
  rw [block09Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09_length

theorem block09_scan : scanFrom 2304 block09 =
    [] := by
  rw [block09]
  simp only [List.append_assoc]
  rw [scan_append, block09Piece00_scan, block09Piece00_length]
  rw [scan_append, block09Piece01_scan, block09Piece01_length]
  rw [scan_append, block09Piece02_scan, block09Piece02_length]
  rw [scan_append, block09Piece03_scan, block09Piece03_length]
  rw [scan_append, block09Piece04_scan, block09Piece04_length]
  rw [scan_append, block09Piece05_scan, block09Piece05_length]
  rw [scan_append, block09Piece06_scan, block09Piece06_length]
  rw [block09Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block09_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
