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

def block01Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block01Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block01Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block01Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block01Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block01Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block01Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block01Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block01 : List Mark :=
  block01Piece00 ++ block01Piece01 ++ block01Piece02 ++ block01Piece03 ++ block01Piece04 ++ block01Piece05 ++ block01Piece06 ++ block01Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01

theorem block01Piece00_length : block01Piece00.length = 32 := by
  simp only [block01Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block01Piece00_scan : scanFrom 256 block01Piece00 =
    [] := by
  simpa only [block01Piece00] using (scan_passive 256 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01Piece00_scan

theorem block01Piece01_length : block01Piece01.length = 32 := by
  simp only [block01Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block01Piece01_scan : scanFrom 288 block01Piece01 =
    [] := by
  simpa only [block01Piece01] using (scan_passive 288 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01Piece01_scan

theorem block01Piece02_length : block01Piece02.length = 32 := by
  simp only [block01Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block01Piece02_scan : scanFrom 320 block01Piece02 =
    [] := by
  simpa only [block01Piece02] using (scan_passive 320 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01Piece02_scan

theorem block01Piece03_length : block01Piece03.length = 32 := by
  simp only [block01Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block01Piece03_scan : scanFrom 352 block01Piece03 =
    [] := by
  simpa only [block01Piece03] using (scan_passive 352 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01Piece03_scan

theorem block01Piece04_length : block01Piece04.length = 32 := by
  simp only [block01Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block01Piece04_scan : scanFrom 384 block01Piece04 =
    [] := by
  simpa only [block01Piece04] using (scan_passive 384 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01Piece04_scan

theorem block01Piece05_length : block01Piece05.length = 32 := by
  simp only [block01Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block01Piece05_scan : scanFrom 416 block01Piece05 =
    [] := by
  simpa only [block01Piece05] using (scan_passive 416 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01Piece05_scan

theorem block01Piece06_length : block01Piece06.length = 32 := by
  simp only [block01Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block01Piece06_scan : scanFrom 448 block01Piece06 =
    [] := by
  simpa only [block01Piece06] using (scan_passive 448 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01Piece06_scan

theorem block01Piece07_length : block01Piece07.length = 32 := by
  simp only [block01Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block01Piece07_scan : scanFrom 480 block01Piece07 =
    [] := by
  simpa only [block01Piece07] using (scan_passive 480 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01Piece07_scan

theorem block01_length : block01.length = 256 := by
  rw [block01]
  simp only [List.append_assoc]
  rw [List.length_append, block01Piece00_length]
  rw [List.length_append, block01Piece01_length]
  rw [List.length_append, block01Piece02_length]
  rw [List.length_append, block01Piece03_length]
  rw [List.length_append, block01Piece04_length]
  rw [List.length_append, block01Piece05_length]
  rw [List.length_append, block01Piece06_length]
  rw [block01Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01_length

theorem block01_scan : scanFrom 256 block01 =
    [] := by
  rw [block01]
  simp only [List.append_assoc]
  rw [scan_append, block01Piece00_scan, block01Piece00_length]
  rw [scan_append, block01Piece01_scan, block01Piece01_length]
  rw [scan_append, block01Piece02_scan, block01Piece02_length]
  rw [scan_append, block01Piece03_scan, block01Piece03_length]
  rw [scan_append, block01Piece04_scan, block01Piece04_length]
  rw [scan_append, block01Piece05_scan, block01Piece05_length]
  rw [scan_append, block01Piece06_scan, block01Piece06_length]
  rw [block01Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block01_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
