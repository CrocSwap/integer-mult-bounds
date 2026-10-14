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

def block04Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block04Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block04Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block04Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block04Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block04Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block04Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block04Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block04 : List Mark :=
  block04Piece00 ++ block04Piece01 ++ block04Piece02 ++ block04Piece03 ++ block04Piece04 ++ block04Piece05 ++ block04Piece06 ++ block04Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04

theorem block04Piece00_length : block04Piece00.length = 32 := by
  simp only [block04Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block04Piece00_scan : scanFrom 1024 block04Piece00 =
    [] := by
  simpa only [block04Piece00] using (scan_passive 1024 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04Piece00_scan

theorem block04Piece01_length : block04Piece01.length = 32 := by
  simp only [block04Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block04Piece01_scan : scanFrom 1056 block04Piece01 =
    [] := by
  simpa only [block04Piece01] using (scan_passive 1056 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04Piece01_scan

theorem block04Piece02_length : block04Piece02.length = 32 := by
  simp only [block04Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block04Piece02_scan : scanFrom 1088 block04Piece02 =
    [] := by
  simpa only [block04Piece02] using (scan_passive 1088 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04Piece02_scan

theorem block04Piece03_length : block04Piece03.length = 32 := by
  simp only [block04Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block04Piece03_scan : scanFrom 1120 block04Piece03 =
    [] := by
  simpa only [block04Piece03] using (scan_passive 1120 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04Piece03_scan

theorem block04Piece04_length : block04Piece04.length = 32 := by
  simp only [block04Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block04Piece04_scan : scanFrom 1152 block04Piece04 =
    [] := by
  simpa only [block04Piece04] using (scan_passive 1152 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04Piece04_scan

theorem block04Piece05_length : block04Piece05.length = 32 := by
  simp only [block04Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block04Piece05_scan : scanFrom 1184 block04Piece05 =
    [] := by
  simpa only [block04Piece05] using (scan_passive 1184 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04Piece05_scan

theorem block04Piece06_length : block04Piece06.length = 32 := by
  simp only [block04Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block04Piece06_scan : scanFrom 1216 block04Piece06 =
    [] := by
  simpa only [block04Piece06] using (scan_passive 1216 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04Piece06_scan

theorem block04Piece07_length : block04Piece07.length = 32 := by
  simp only [block04Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block04Piece07_scan : scanFrom 1248 block04Piece07 =
    [] := by
  simpa only [block04Piece07] using (scan_passive 1248 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04Piece07_scan

theorem block04_length : block04.length = 256 := by
  rw [block04]
  simp only [List.append_assoc]
  rw [List.length_append, block04Piece00_length]
  rw [List.length_append, block04Piece01_length]
  rw [List.length_append, block04Piece02_length]
  rw [List.length_append, block04Piece03_length]
  rw [List.length_append, block04Piece04_length]
  rw [List.length_append, block04Piece05_length]
  rw [List.length_append, block04Piece06_length]
  rw [block04Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04_length

theorem block04_scan : scanFrom 1024 block04 =
    [] := by
  rw [block04]
  simp only [List.append_assoc]
  rw [scan_append, block04Piece00_scan, block04Piece00_length]
  rw [scan_append, block04Piece01_scan, block04Piece01_length]
  rw [scan_append, block04Piece02_scan, block04Piece02_length]
  rw [scan_append, block04Piece03_scan, block04Piece03_length]
  rw [scan_append, block04Piece04_scan, block04Piece04_length]
  rw [scan_append, block04Piece05_scan, block04Piece05_length]
  rw [scan_append, block04Piece06_scan, block04Piece06_length]
  rw [block04Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block04_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
