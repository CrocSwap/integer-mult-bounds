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

def block22Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block22Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block22Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block22Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block22Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block22Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block22Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block22Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block22 : List Mark :=
  block22Piece00 ++ block22Piece01 ++ block22Piece02 ++ block22Piece03 ++ block22Piece04 ++ block22Piece05 ++ block22Piece06 ++ block22Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22

theorem block22Piece00_length : block22Piece00.length = 32 := by
  simp only [block22Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block22Piece00_scan : scanFrom 5632 block22Piece00 =
    [] := by
  simpa only [block22Piece00] using (scan_passive 5632 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22Piece00_scan

theorem block22Piece01_length : block22Piece01.length = 32 := by
  simp only [block22Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block22Piece01_scan : scanFrom 5664 block22Piece01 =
    [] := by
  simpa only [block22Piece01] using (scan_passive 5664 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22Piece01_scan

theorem block22Piece02_length : block22Piece02.length = 32 := by
  simp only [block22Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block22Piece02_scan : scanFrom 5696 block22Piece02 =
    [] := by
  simpa only [block22Piece02] using (scan_passive 5696 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22Piece02_scan

theorem block22Piece03_length : block22Piece03.length = 32 := by
  simp only [block22Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block22Piece03_scan : scanFrom 5728 block22Piece03 =
    [] := by
  simpa only [block22Piece03] using (scan_passive 5728 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22Piece03_scan

theorem block22Piece04_length : block22Piece04.length = 32 := by
  simp only [block22Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block22Piece04_scan : scanFrom 5760 block22Piece04 =
    [] := by
  simpa only [block22Piece04] using (scan_passive 5760 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22Piece04_scan

theorem block22Piece05_length : block22Piece05.length = 32 := by
  simp only [block22Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block22Piece05_scan : scanFrom 5792 block22Piece05 =
    [] := by
  simpa only [block22Piece05] using (scan_passive 5792 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22Piece05_scan

theorem block22Piece06_length : block22Piece06.length = 32 := by
  simp only [block22Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block22Piece06_scan : scanFrom 5824 block22Piece06 =
    [] := by
  simpa only [block22Piece06] using (scan_passive 5824 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22Piece06_scan

theorem block22Piece07_length : block22Piece07.length = 32 := by
  simp only [block22Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block22Piece07_scan : scanFrom 5856 block22Piece07 =
    [] := by
  simpa only [block22Piece07] using (scan_passive 5856 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22Piece07_scan

theorem block22_length : block22.length = 256 := by
  rw [block22]
  simp only [List.append_assoc]
  rw [List.length_append, block22Piece00_length]
  rw [List.length_append, block22Piece01_length]
  rw [List.length_append, block22Piece02_length]
  rw [List.length_append, block22Piece03_length]
  rw [List.length_append, block22Piece04_length]
  rw [List.length_append, block22Piece05_length]
  rw [List.length_append, block22Piece06_length]
  rw [block22Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22_length

theorem block22_scan : scanFrom 5632 block22 =
    [] := by
  rw [block22]
  simp only [List.append_assoc]
  rw [scan_append, block22Piece00_scan, block22Piece00_length]
  rw [scan_append, block22Piece01_scan, block22Piece01_length]
  rw [scan_append, block22Piece02_scan, block22Piece02_length]
  rw [scan_append, block22Piece03_scan, block22Piece03_length]
  rw [scan_append, block22Piece04_scan, block22Piece04_length]
  rw [scan_append, block22Piece05_scan, block22Piece05_length]
  rw [scan_append, block22Piece06_scan, block22Piece06_length]
  rw [block22Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block22_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
