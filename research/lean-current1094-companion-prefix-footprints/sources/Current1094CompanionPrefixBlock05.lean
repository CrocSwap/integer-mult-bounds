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

def block05Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block05Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block05Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block05Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block05Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block05Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block05Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block05Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block05 : List Mark :=
  block05Piece00 ++ block05Piece01 ++ block05Piece02 ++ block05Piece03 ++ block05Piece04 ++ block05Piece05 ++ block05Piece06 ++ block05Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05

theorem block05Piece00_length : block05Piece00.length = 32 := by
  simp only [block05Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block05Piece00_scan : scanFrom 1280 block05Piece00 =
    [] := by
  simpa only [block05Piece00] using (scan_passive 1280 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05Piece00_scan

theorem block05Piece01_length : block05Piece01.length = 32 := by
  simp only [block05Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block05Piece01_scan : scanFrom 1312 block05Piece01 =
    [] := by
  simpa only [block05Piece01] using (scan_passive 1312 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05Piece01_scan

theorem block05Piece02_length : block05Piece02.length = 32 := by
  simp only [block05Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block05Piece02_scan : scanFrom 1344 block05Piece02 =
    [] := by
  simpa only [block05Piece02] using (scan_passive 1344 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05Piece02_scan

theorem block05Piece03_length : block05Piece03.length = 32 := by
  simp only [block05Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block05Piece03_scan : scanFrom 1376 block05Piece03 =
    [] := by
  simpa only [block05Piece03] using (scan_passive 1376 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05Piece03_scan

theorem block05Piece04_length : block05Piece04.length = 32 := by
  simp only [block05Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block05Piece04_scan : scanFrom 1408 block05Piece04 =
    [] := by
  simpa only [block05Piece04] using (scan_passive 1408 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05Piece04_scan

theorem block05Piece05_length : block05Piece05.length = 32 := by
  simp only [block05Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block05Piece05_scan : scanFrom 1440 block05Piece05 =
    [] := by
  simpa only [block05Piece05] using (scan_passive 1440 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05Piece05_scan

theorem block05Piece06_length : block05Piece06.length = 32 := by
  simp only [block05Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block05Piece06_scan : scanFrom 1472 block05Piece06 =
    [] := by
  simpa only [block05Piece06] using (scan_passive 1472 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05Piece06_scan

theorem block05Piece07_length : block05Piece07.length = 32 := by
  simp only [block05Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block05Piece07_scan : scanFrom 1504 block05Piece07 =
    [] := by
  simpa only [block05Piece07] using (scan_passive 1504 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05Piece07_scan

theorem block05_length : block05.length = 256 := by
  rw [block05]
  simp only [List.append_assoc]
  rw [List.length_append, block05Piece00_length]
  rw [List.length_append, block05Piece01_length]
  rw [List.length_append, block05Piece02_length]
  rw [List.length_append, block05Piece03_length]
  rw [List.length_append, block05Piece04_length]
  rw [List.length_append, block05Piece05_length]
  rw [List.length_append, block05Piece06_length]
  rw [block05Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05_length

theorem block05_scan : scanFrom 1280 block05 =
    [] := by
  rw [block05]
  simp only [List.append_assoc]
  rw [scan_append, block05Piece00_scan, block05Piece00_length]
  rw [scan_append, block05Piece01_scan, block05Piece01_length]
  rw [scan_append, block05Piece02_scan, block05Piece02_length]
  rw [scan_append, block05Piece03_scan, block05Piece03_length]
  rw [scan_append, block05Piece04_scan, block05Piece04_length]
  rw [scan_append, block05Piece05_scan, block05Piece05_length]
  rw [scan_append, block05Piece06_scan, block05Piece06_length]
  rw [block05Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block05_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
