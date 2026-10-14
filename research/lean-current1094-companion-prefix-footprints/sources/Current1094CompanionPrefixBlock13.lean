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

def block13Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block13Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block13Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block13Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block13Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block13Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block13Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block13Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block13 : List Mark :=
  block13Piece00 ++ block13Piece01 ++ block13Piece02 ++ block13Piece03 ++ block13Piece04 ++ block13Piece05 ++ block13Piece06 ++ block13Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13

theorem block13Piece00_length : block13Piece00.length = 32 := by
  simp only [block13Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block13Piece00_scan : scanFrom 3328 block13Piece00 =
    [] := by
  simpa only [block13Piece00] using (scan_passive 3328 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13Piece00_scan

theorem block13Piece01_length : block13Piece01.length = 32 := by
  simp only [block13Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block13Piece01_scan : scanFrom 3360 block13Piece01 =
    [] := by
  simpa only [block13Piece01] using (scan_passive 3360 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13Piece01_scan

theorem block13Piece02_length : block13Piece02.length = 32 := by
  simp only [block13Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block13Piece02_scan : scanFrom 3392 block13Piece02 =
    [] := by
  simpa only [block13Piece02] using (scan_passive 3392 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13Piece02_scan

theorem block13Piece03_length : block13Piece03.length = 32 := by
  simp only [block13Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block13Piece03_scan : scanFrom 3424 block13Piece03 =
    [] := by
  simpa only [block13Piece03] using (scan_passive 3424 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13Piece03_scan

theorem block13Piece04_length : block13Piece04.length = 32 := by
  simp only [block13Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block13Piece04_scan : scanFrom 3456 block13Piece04 =
    [] := by
  simpa only [block13Piece04] using (scan_passive 3456 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13Piece04_scan

theorem block13Piece05_length : block13Piece05.length = 32 := by
  simp only [block13Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block13Piece05_scan : scanFrom 3488 block13Piece05 =
    [] := by
  simpa only [block13Piece05] using (scan_passive 3488 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13Piece05_scan

theorem block13Piece06_length : block13Piece06.length = 32 := by
  simp only [block13Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block13Piece06_scan : scanFrom 3520 block13Piece06 =
    [] := by
  simpa only [block13Piece06] using (scan_passive 3520 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13Piece06_scan

theorem block13Piece07_length : block13Piece07.length = 32 := by
  simp only [block13Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block13Piece07_scan : scanFrom 3552 block13Piece07 =
    [] := by
  simpa only [block13Piece07] using (scan_passive 3552 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13Piece07_scan

theorem block13_length : block13.length = 256 := by
  rw [block13]
  simp only [List.append_assoc]
  rw [List.length_append, block13Piece00_length]
  rw [List.length_append, block13Piece01_length]
  rw [List.length_append, block13Piece02_length]
  rw [List.length_append, block13Piece03_length]
  rw [List.length_append, block13Piece04_length]
  rw [List.length_append, block13Piece05_length]
  rw [List.length_append, block13Piece06_length]
  rw [block13Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13_length

theorem block13_scan : scanFrom 3328 block13 =
    [] := by
  rw [block13]
  simp only [List.append_assoc]
  rw [scan_append, block13Piece00_scan, block13Piece00_length]
  rw [scan_append, block13Piece01_scan, block13Piece01_length]
  rw [scan_append, block13Piece02_scan, block13Piece02_length]
  rw [scan_append, block13Piece03_scan, block13Piece03_length]
  rw [scan_append, block13Piece04_scan, block13Piece04_length]
  rw [scan_append, block13Piece05_scan, block13Piece05_length]
  rw [scan_append, block13Piece06_scan, block13Piece06_length]
  rw [block13Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block13_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
