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

def block32Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block32Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block32Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block32Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block32Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block32Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block32Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block32Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block32 : List Mark :=
  block32Piece00 ++ block32Piece01 ++ block32Piece02 ++ block32Piece03 ++ block32Piece04 ++ block32Piece05 ++ block32Piece06 ++ block32Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32

theorem block32Piece00_length : block32Piece00.length = 32 := by
  simp only [block32Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block32Piece00_scan : scanFrom 8192 block32Piece00 =
    [] := by
  simpa only [block32Piece00] using (scan_passive 8192 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32Piece00_scan

theorem block32Piece01_length : block32Piece01.length = 32 := by
  simp only [block32Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block32Piece01_scan : scanFrom 8224 block32Piece01 =
    [] := by
  simpa only [block32Piece01] using (scan_passive 8224 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32Piece01_scan

theorem block32Piece02_length : block32Piece02.length = 32 := by
  simp only [block32Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block32Piece02_scan : scanFrom 8256 block32Piece02 =
    [] := by
  simpa only [block32Piece02] using (scan_passive 8256 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32Piece02_scan

theorem block32Piece03_length : block32Piece03.length = 32 := by
  simp only [block32Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block32Piece03_scan : scanFrom 8288 block32Piece03 =
    [] := by
  simpa only [block32Piece03] using (scan_passive 8288 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32Piece03_scan

theorem block32Piece04_length : block32Piece04.length = 32 := by
  simp only [block32Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block32Piece04_scan : scanFrom 8320 block32Piece04 =
    [] := by
  simpa only [block32Piece04] using (scan_passive 8320 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32Piece04_scan

theorem block32Piece05_length : block32Piece05.length = 32 := by
  simp only [block32Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block32Piece05_scan : scanFrom 8352 block32Piece05 =
    [] := by
  simpa only [block32Piece05] using (scan_passive 8352 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32Piece05_scan

theorem block32Piece06_length : block32Piece06.length = 32 := by
  simp only [block32Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block32Piece06_scan : scanFrom 8384 block32Piece06 =
    [] := by
  simpa only [block32Piece06] using (scan_passive 8384 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32Piece06_scan

theorem block32Piece07_length : block32Piece07.length = 32 := by
  simp only [block32Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block32Piece07_scan : scanFrom 8416 block32Piece07 =
    [] := by
  simpa only [block32Piece07] using (scan_passive 8416 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32Piece07_scan

theorem block32_length : block32.length = 256 := by
  rw [block32]
  simp only [List.append_assoc]
  rw [List.length_append, block32Piece00_length]
  rw [List.length_append, block32Piece01_length]
  rw [List.length_append, block32Piece02_length]
  rw [List.length_append, block32Piece03_length]
  rw [List.length_append, block32Piece04_length]
  rw [List.length_append, block32Piece05_length]
  rw [List.length_append, block32Piece06_length]
  rw [block32Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32_length

theorem block32_scan : scanFrom 8192 block32 =
    [] := by
  rw [block32]
  simp only [List.append_assoc]
  rw [scan_append, block32Piece00_scan, block32Piece00_length]
  rw [scan_append, block32Piece01_scan, block32Piece01_length]
  rw [scan_append, block32Piece02_scan, block32Piece02_length]
  rw [scan_append, block32Piece03_scan, block32Piece03_length]
  rw [scan_append, block32Piece04_scan, block32Piece04_length]
  rw [scan_append, block32Piece05_scan, block32Piece05_length]
  rw [scan_append, block32Piece06_scan, block32Piece06_length]
  rw [block32Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block32_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
