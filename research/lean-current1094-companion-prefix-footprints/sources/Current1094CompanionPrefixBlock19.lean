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

def block19Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block19Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block19Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block19Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block19Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block19Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block19Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block19Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block19 : List Mark :=
  block19Piece00 ++ block19Piece01 ++ block19Piece02 ++ block19Piece03 ++ block19Piece04 ++ block19Piece05 ++ block19Piece06 ++ block19Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19

theorem block19Piece00_length : block19Piece00.length = 32 := by
  simp only [block19Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block19Piece00_scan : scanFrom 4864 block19Piece00 =
    [] := by
  simpa only [block19Piece00] using (scan_passive 4864 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19Piece00_scan

theorem block19Piece01_length : block19Piece01.length = 32 := by
  simp only [block19Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block19Piece01_scan : scanFrom 4896 block19Piece01 =
    [] := by
  simpa only [block19Piece01] using (scan_passive 4896 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19Piece01_scan

theorem block19Piece02_length : block19Piece02.length = 32 := by
  simp only [block19Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block19Piece02_scan : scanFrom 4928 block19Piece02 =
    [] := by
  simpa only [block19Piece02] using (scan_passive 4928 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19Piece02_scan

theorem block19Piece03_length : block19Piece03.length = 32 := by
  simp only [block19Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block19Piece03_scan : scanFrom 4960 block19Piece03 =
    [] := by
  simpa only [block19Piece03] using (scan_passive 4960 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19Piece03_scan

theorem block19Piece04_length : block19Piece04.length = 32 := by
  simp only [block19Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block19Piece04_scan : scanFrom 4992 block19Piece04 =
    [] := by
  simpa only [block19Piece04] using (scan_passive 4992 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19Piece04_scan

theorem block19Piece05_length : block19Piece05.length = 32 := by
  simp only [block19Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block19Piece05_scan : scanFrom 5024 block19Piece05 =
    [] := by
  simpa only [block19Piece05] using (scan_passive 5024 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19Piece05_scan

theorem block19Piece06_length : block19Piece06.length = 32 := by
  simp only [block19Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block19Piece06_scan : scanFrom 5056 block19Piece06 =
    [] := by
  simpa only [block19Piece06] using (scan_passive 5056 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19Piece06_scan

theorem block19Piece07_length : block19Piece07.length = 32 := by
  simp only [block19Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block19Piece07_scan : scanFrom 5088 block19Piece07 =
    [] := by
  simpa only [block19Piece07] using (scan_passive 5088 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19Piece07_scan

theorem block19_length : block19.length = 256 := by
  rw [block19]
  simp only [List.append_assoc]
  rw [List.length_append, block19Piece00_length]
  rw [List.length_append, block19Piece01_length]
  rw [List.length_append, block19Piece02_length]
  rw [List.length_append, block19Piece03_length]
  rw [List.length_append, block19Piece04_length]
  rw [List.length_append, block19Piece05_length]
  rw [List.length_append, block19Piece06_length]
  rw [block19Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19_length

theorem block19_scan : scanFrom 4864 block19 =
    [] := by
  rw [block19]
  simp only [List.append_assoc]
  rw [scan_append, block19Piece00_scan, block19Piece00_length]
  rw [scan_append, block19Piece01_scan, block19Piece01_length]
  rw [scan_append, block19Piece02_scan, block19Piece02_length]
  rw [scan_append, block19Piece03_scan, block19Piece03_length]
  rw [scan_append, block19Piece04_scan, block19Piece04_length]
  rw [scan_append, block19Piece05_scan, block19Piece05_length]
  rw [scan_append, block19Piece06_scan, block19Piece06_length]
  rw [block19Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block19_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
