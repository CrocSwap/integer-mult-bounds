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

def block33Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block33Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block33Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block33Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block33Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block33Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block33Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block33Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block33 : List Mark :=
  block33Piece00 ++ block33Piece01 ++ block33Piece02 ++ block33Piece03 ++ block33Piece04 ++ block33Piece05 ++ block33Piece06 ++ block33Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33

theorem block33Piece00_length : block33Piece00.length = 32 := by
  simp only [block33Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block33Piece00_scan : scanFrom 8448 block33Piece00 =
    [] := by
  simpa only [block33Piece00] using (scan_passive 8448 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33Piece00_scan

theorem block33Piece01_length : block33Piece01.length = 32 := by
  simp only [block33Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block33Piece01_scan : scanFrom 8480 block33Piece01 =
    [] := by
  simpa only [block33Piece01] using (scan_passive 8480 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33Piece01_scan

theorem block33Piece02_length : block33Piece02.length = 32 := by
  simp only [block33Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block33Piece02_scan : scanFrom 8512 block33Piece02 =
    [] := by
  simpa only [block33Piece02] using (scan_passive 8512 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33Piece02_scan

theorem block33Piece03_length : block33Piece03.length = 32 := by
  simp only [block33Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block33Piece03_scan : scanFrom 8544 block33Piece03 =
    [] := by
  simpa only [block33Piece03] using (scan_passive 8544 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33Piece03_scan

theorem block33Piece04_length : block33Piece04.length = 32 := by
  simp only [block33Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block33Piece04_scan : scanFrom 8576 block33Piece04 =
    [] := by
  simpa only [block33Piece04] using (scan_passive 8576 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33Piece04_scan

theorem block33Piece05_length : block33Piece05.length = 32 := by
  simp only [block33Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block33Piece05_scan : scanFrom 8608 block33Piece05 =
    [] := by
  simpa only [block33Piece05] using (scan_passive 8608 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33Piece05_scan

theorem block33Piece06_length : block33Piece06.length = 32 := by
  simp only [block33Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block33Piece06_scan : scanFrom 8640 block33Piece06 =
    [] := by
  simpa only [block33Piece06] using (scan_passive 8640 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33Piece06_scan

theorem block33Piece07_length : block33Piece07.length = 32 := by
  simp only [block33Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block33Piece07_scan : scanFrom 8672 block33Piece07 =
    [] := by
  simpa only [block33Piece07] using (scan_passive 8672 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33Piece07_scan

theorem block33_length : block33.length = 256 := by
  rw [block33]
  simp only [List.append_assoc]
  rw [List.length_append, block33Piece00_length]
  rw [List.length_append, block33Piece01_length]
  rw [List.length_append, block33Piece02_length]
  rw [List.length_append, block33Piece03_length]
  rw [List.length_append, block33Piece04_length]
  rw [List.length_append, block33Piece05_length]
  rw [List.length_append, block33Piece06_length]
  rw [block33Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33_length

theorem block33_scan : scanFrom 8448 block33 =
    [] := by
  rw [block33]
  simp only [List.append_assoc]
  rw [scan_append, block33Piece00_scan, block33Piece00_length]
  rw [scan_append, block33Piece01_scan, block33Piece01_length]
  rw [scan_append, block33Piece02_scan, block33Piece02_length]
  rw [scan_append, block33Piece03_scan, block33Piece03_length]
  rw [scan_append, block33Piece04_scan, block33Piece04_length]
  rw [scan_append, block33Piece05_scan, block33Piece05_length]
  rw [scan_append, block33Piece06_scan, block33Piece06_length]
  rw [block33Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block33_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
