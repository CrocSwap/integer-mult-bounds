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

def block16Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block16Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block16Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block16Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block16Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block16Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block16Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block16Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block16 : List Mark :=
  block16Piece00 ++ block16Piece01 ++ block16Piece02 ++ block16Piece03 ++ block16Piece04 ++ block16Piece05 ++ block16Piece06 ++ block16Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16

theorem block16Piece00_length : block16Piece00.length = 32 := by
  simp only [block16Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block16Piece00_scan : scanFrom 4096 block16Piece00 =
    [] := by
  simpa only [block16Piece00] using (scan_passive 4096 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16Piece00_scan

theorem block16Piece01_length : block16Piece01.length = 32 := by
  simp only [block16Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block16Piece01_scan : scanFrom 4128 block16Piece01 =
    [] := by
  simpa only [block16Piece01] using (scan_passive 4128 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16Piece01_scan

theorem block16Piece02_length : block16Piece02.length = 32 := by
  simp only [block16Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block16Piece02_scan : scanFrom 4160 block16Piece02 =
    [] := by
  simpa only [block16Piece02] using (scan_passive 4160 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16Piece02_scan

theorem block16Piece03_length : block16Piece03.length = 32 := by
  simp only [block16Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block16Piece03_scan : scanFrom 4192 block16Piece03 =
    [] := by
  simpa only [block16Piece03] using (scan_passive 4192 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16Piece03_scan

theorem block16Piece04_length : block16Piece04.length = 32 := by
  simp only [block16Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block16Piece04_scan : scanFrom 4224 block16Piece04 =
    [] := by
  simpa only [block16Piece04] using (scan_passive 4224 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16Piece04_scan

theorem block16Piece05_length : block16Piece05.length = 32 := by
  simp only [block16Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block16Piece05_scan : scanFrom 4256 block16Piece05 =
    [] := by
  simpa only [block16Piece05] using (scan_passive 4256 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16Piece05_scan

theorem block16Piece06_length : block16Piece06.length = 32 := by
  simp only [block16Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block16Piece06_scan : scanFrom 4288 block16Piece06 =
    [] := by
  simpa only [block16Piece06] using (scan_passive 4288 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16Piece06_scan

theorem block16Piece07_length : block16Piece07.length = 32 := by
  simp only [block16Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block16Piece07_scan : scanFrom 4320 block16Piece07 =
    [] := by
  simpa only [block16Piece07] using (scan_passive 4320 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16Piece07_scan

theorem block16_length : block16.length = 256 := by
  rw [block16]
  simp only [List.append_assoc]
  rw [List.length_append, block16Piece00_length]
  rw [List.length_append, block16Piece01_length]
  rw [List.length_append, block16Piece02_length]
  rw [List.length_append, block16Piece03_length]
  rw [List.length_append, block16Piece04_length]
  rw [List.length_append, block16Piece05_length]
  rw [List.length_append, block16Piece06_length]
  rw [block16Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16_length

theorem block16_scan : scanFrom 4096 block16 =
    [] := by
  rw [block16]
  simp only [List.append_assoc]
  rw [scan_append, block16Piece00_scan, block16Piece00_length]
  rw [scan_append, block16Piece01_scan, block16Piece01_length]
  rw [scan_append, block16Piece02_scan, block16Piece02_length]
  rw [scan_append, block16Piece03_scan, block16Piece03_length]
  rw [scan_append, block16Piece04_scan, block16Piece04_length]
  rw [scan_append, block16Piece05_scan, block16Piece05_length]
  rw [scan_append, block16Piece06_scan, block16Piece06_length]
  rw [block16Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block16_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
