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

def block07Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block07Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block07Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block07Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block07Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block07Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block07Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block07Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block07 : List Mark :=
  block07Piece00 ++ block07Piece01 ++ block07Piece02 ++ block07Piece03 ++ block07Piece04 ++ block07Piece05 ++ block07Piece06 ++ block07Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07

theorem block07Piece00_length : block07Piece00.length = 32 := by
  simp only [block07Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block07Piece00_scan : scanFrom 1792 block07Piece00 =
    [] := by
  simpa only [block07Piece00] using (scan_passive 1792 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07Piece00_scan

theorem block07Piece01_length : block07Piece01.length = 32 := by
  simp only [block07Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block07Piece01_scan : scanFrom 1824 block07Piece01 =
    [] := by
  simpa only [block07Piece01] using (scan_passive 1824 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07Piece01_scan

theorem block07Piece02_length : block07Piece02.length = 32 := by
  simp only [block07Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block07Piece02_scan : scanFrom 1856 block07Piece02 =
    [] := by
  simpa only [block07Piece02] using (scan_passive 1856 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07Piece02_scan

theorem block07Piece03_length : block07Piece03.length = 32 := by
  simp only [block07Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block07Piece03_scan : scanFrom 1888 block07Piece03 =
    [] := by
  simpa only [block07Piece03] using (scan_passive 1888 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07Piece03_scan

theorem block07Piece04_length : block07Piece04.length = 32 := by
  simp only [block07Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block07Piece04_scan : scanFrom 1920 block07Piece04 =
    [] := by
  simpa only [block07Piece04] using (scan_passive 1920 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07Piece04_scan

theorem block07Piece05_length : block07Piece05.length = 32 := by
  simp only [block07Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block07Piece05_scan : scanFrom 1952 block07Piece05 =
    [] := by
  simpa only [block07Piece05] using (scan_passive 1952 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07Piece05_scan

theorem block07Piece06_length : block07Piece06.length = 32 := by
  simp only [block07Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block07Piece06_scan : scanFrom 1984 block07Piece06 =
    [] := by
  simpa only [block07Piece06] using (scan_passive 1984 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07Piece06_scan

theorem block07Piece07_length : block07Piece07.length = 32 := by
  simp only [block07Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block07Piece07_scan : scanFrom 2016 block07Piece07 =
    [] := by
  simpa only [block07Piece07] using (scan_passive 2016 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07Piece07_scan

theorem block07_length : block07.length = 256 := by
  rw [block07]
  simp only [List.append_assoc]
  rw [List.length_append, block07Piece00_length]
  rw [List.length_append, block07Piece01_length]
  rw [List.length_append, block07Piece02_length]
  rw [List.length_append, block07Piece03_length]
  rw [List.length_append, block07Piece04_length]
  rw [List.length_append, block07Piece05_length]
  rw [List.length_append, block07Piece06_length]
  rw [block07Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07_length

theorem block07_scan : scanFrom 1792 block07 =
    [] := by
  rw [block07]
  simp only [List.append_assoc]
  rw [scan_append, block07Piece00_scan, block07Piece00_length]
  rw [scan_append, block07Piece01_scan, block07Piece01_length]
  rw [scan_append, block07Piece02_scan, block07Piece02_length]
  rw [scan_append, block07Piece03_scan, block07Piece03_length]
  rw [scan_append, block07Piece04_scan, block07Piece04_length]
  rw [scan_append, block07Piece05_scan, block07Piece05_length]
  rw [scan_append, block07Piece06_scan, block07Piece06_length]
  rw [block07Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block07_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
