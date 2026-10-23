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

def block20Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block20Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block20Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block20Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block20Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block20Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block20Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block20Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block20 : List Mark :=
  block20Piece00 ++ block20Piece01 ++ block20Piece02 ++ block20Piece03 ++ block20Piece04 ++ block20Piece05 ++ block20Piece06 ++ block20Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20

theorem block20Piece00_length : block20Piece00.length = 32 := by
  simp only [block20Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block20Piece00_scan : scanFrom 5120 block20Piece00 =
    [] := by
  simpa only [block20Piece00] using (scan_passive 5120 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20Piece00_scan

theorem block20Piece01_length : block20Piece01.length = 32 := by
  simp only [block20Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block20Piece01_scan : scanFrom 5152 block20Piece01 =
    [] := by
  simpa only [block20Piece01] using (scan_passive 5152 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20Piece01_scan

theorem block20Piece02_length : block20Piece02.length = 32 := by
  simp only [block20Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block20Piece02_scan : scanFrom 5184 block20Piece02 =
    [] := by
  simpa only [block20Piece02] using (scan_passive 5184 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20Piece02_scan

theorem block20Piece03_length : block20Piece03.length = 32 := by
  simp only [block20Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block20Piece03_scan : scanFrom 5216 block20Piece03 =
    [] := by
  simpa only [block20Piece03] using (scan_passive 5216 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20Piece03_scan

theorem block20Piece04_length : block20Piece04.length = 32 := by
  simp only [block20Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block20Piece04_scan : scanFrom 5248 block20Piece04 =
    [] := by
  simpa only [block20Piece04] using (scan_passive 5248 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20Piece04_scan

theorem block20Piece05_length : block20Piece05.length = 32 := by
  simp only [block20Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block20Piece05_scan : scanFrom 5280 block20Piece05 =
    [] := by
  simpa only [block20Piece05] using (scan_passive 5280 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20Piece05_scan

theorem block20Piece06_length : block20Piece06.length = 32 := by
  simp only [block20Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block20Piece06_scan : scanFrom 5312 block20Piece06 =
    [] := by
  simpa only [block20Piece06] using (scan_passive 5312 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20Piece06_scan

theorem block20Piece07_length : block20Piece07.length = 32 := by
  simp only [block20Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block20Piece07_scan : scanFrom 5344 block20Piece07 =
    [] := by
  simpa only [block20Piece07] using (scan_passive 5344 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20Piece07_scan

theorem block20_length : block20.length = 256 := by
  rw [block20]
  simp only [List.append_assoc]
  rw [List.length_append, block20Piece00_length]
  rw [List.length_append, block20Piece01_length]
  rw [List.length_append, block20Piece02_length]
  rw [List.length_append, block20Piece03_length]
  rw [List.length_append, block20Piece04_length]
  rw [List.length_append, block20Piece05_length]
  rw [List.length_append, block20Piece06_length]
  rw [block20Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20_length

theorem block20_scan : scanFrom 5120 block20 =
    [] := by
  rw [block20]
  simp only [List.append_assoc]
  rw [scan_append, block20Piece00_scan, block20Piece00_length]
  rw [scan_append, block20Piece01_scan, block20Piece01_length]
  rw [scan_append, block20Piece02_scan, block20Piece02_length]
  rw [scan_append, block20Piece03_scan, block20Piece03_length]
  rw [scan_append, block20Piece04_scan, block20Piece04_length]
  rw [scan_append, block20Piece05_scan, block20Piece05_length]
  rw [scan_append, block20Piece06_scan, block20Piece06_length]
  rw [block20Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block20_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
