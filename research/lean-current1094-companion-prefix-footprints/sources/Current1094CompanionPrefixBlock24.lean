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

def block24Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block24Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block24Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block24Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block24Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block24Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block24Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block24Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block24 : List Mark :=
  block24Piece00 ++ block24Piece01 ++ block24Piece02 ++ block24Piece03 ++ block24Piece04 ++ block24Piece05 ++ block24Piece06 ++ block24Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24

theorem block24Piece00_length : block24Piece00.length = 32 := by
  simp only [block24Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block24Piece00_scan : scanFrom 6144 block24Piece00 =
    [] := by
  simpa only [block24Piece00] using (scan_passive 6144 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24Piece00_scan

theorem block24Piece01_length : block24Piece01.length = 32 := by
  simp only [block24Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block24Piece01_scan : scanFrom 6176 block24Piece01 =
    [] := by
  simpa only [block24Piece01] using (scan_passive 6176 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24Piece01_scan

theorem block24Piece02_length : block24Piece02.length = 32 := by
  simp only [block24Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block24Piece02_scan : scanFrom 6208 block24Piece02 =
    [] := by
  simpa only [block24Piece02] using (scan_passive 6208 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24Piece02_scan

theorem block24Piece03_length : block24Piece03.length = 32 := by
  simp only [block24Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block24Piece03_scan : scanFrom 6240 block24Piece03 =
    [] := by
  simpa only [block24Piece03] using (scan_passive 6240 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24Piece03_scan

theorem block24Piece04_length : block24Piece04.length = 32 := by
  simp only [block24Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block24Piece04_scan : scanFrom 6272 block24Piece04 =
    [] := by
  simpa only [block24Piece04] using (scan_passive 6272 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24Piece04_scan

theorem block24Piece05_length : block24Piece05.length = 32 := by
  simp only [block24Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block24Piece05_scan : scanFrom 6304 block24Piece05 =
    [] := by
  simpa only [block24Piece05] using (scan_passive 6304 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24Piece05_scan

theorem block24Piece06_length : block24Piece06.length = 32 := by
  simp only [block24Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block24Piece06_scan : scanFrom 6336 block24Piece06 =
    [] := by
  simpa only [block24Piece06] using (scan_passive 6336 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24Piece06_scan

theorem block24Piece07_length : block24Piece07.length = 32 := by
  simp only [block24Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block24Piece07_scan : scanFrom 6368 block24Piece07 =
    [] := by
  simpa only [block24Piece07] using (scan_passive 6368 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24Piece07_scan

theorem block24_length : block24.length = 256 := by
  rw [block24]
  simp only [List.append_assoc]
  rw [List.length_append, block24Piece00_length]
  rw [List.length_append, block24Piece01_length]
  rw [List.length_append, block24Piece02_length]
  rw [List.length_append, block24Piece03_length]
  rw [List.length_append, block24Piece04_length]
  rw [List.length_append, block24Piece05_length]
  rw [List.length_append, block24Piece06_length]
  rw [block24Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24_length

theorem block24_scan : scanFrom 6144 block24 =
    [] := by
  rw [block24]
  simp only [List.append_assoc]
  rw [scan_append, block24Piece00_scan, block24Piece00_length]
  rw [scan_append, block24Piece01_scan, block24Piece01_length]
  rw [scan_append, block24Piece02_scan, block24Piece02_length]
  rw [scan_append, block24Piece03_scan, block24Piece03_length]
  rw [scan_append, block24Piece04_scan, block24Piece04_length]
  rw [scan_append, block24Piece05_scan, block24Piece05_length]
  rw [scan_append, block24Piece06_scan, block24Piece06_length]
  rw [block24Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block24_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
