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

def block14Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block14Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block14Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block14Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block14Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block14Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block14Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block14Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block14 : List Mark :=
  block14Piece00 ++ block14Piece01 ++ block14Piece02 ++ block14Piece03 ++ block14Piece04 ++ block14Piece05 ++ block14Piece06 ++ block14Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14

theorem block14Piece00_length : block14Piece00.length = 32 := by
  simp only [block14Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block14Piece00_scan : scanFrom 3584 block14Piece00 =
    [] := by
  simpa only [block14Piece00] using (scan_passive 3584 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14Piece00_scan

theorem block14Piece01_length : block14Piece01.length = 32 := by
  simp only [block14Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block14Piece01_scan : scanFrom 3616 block14Piece01 =
    [] := by
  simpa only [block14Piece01] using (scan_passive 3616 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14Piece01_scan

theorem block14Piece02_length : block14Piece02.length = 32 := by
  simp only [block14Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block14Piece02_scan : scanFrom 3648 block14Piece02 =
    [] := by
  simpa only [block14Piece02] using (scan_passive 3648 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14Piece02_scan

theorem block14Piece03_length : block14Piece03.length = 32 := by
  simp only [block14Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block14Piece03_scan : scanFrom 3680 block14Piece03 =
    [] := by
  simpa only [block14Piece03] using (scan_passive 3680 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14Piece03_scan

theorem block14Piece04_length : block14Piece04.length = 32 := by
  simp only [block14Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block14Piece04_scan : scanFrom 3712 block14Piece04 =
    [] := by
  simpa only [block14Piece04] using (scan_passive 3712 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14Piece04_scan

theorem block14Piece05_length : block14Piece05.length = 32 := by
  simp only [block14Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block14Piece05_scan : scanFrom 3744 block14Piece05 =
    [] := by
  simpa only [block14Piece05] using (scan_passive 3744 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14Piece05_scan

theorem block14Piece06_length : block14Piece06.length = 32 := by
  simp only [block14Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block14Piece06_scan : scanFrom 3776 block14Piece06 =
    [] := by
  simpa only [block14Piece06] using (scan_passive 3776 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14Piece06_scan

theorem block14Piece07_length : block14Piece07.length = 32 := by
  simp only [block14Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block14Piece07_scan : scanFrom 3808 block14Piece07 =
    [] := by
  simpa only [block14Piece07] using (scan_passive 3808 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14Piece07_scan

theorem block14_length : block14.length = 256 := by
  rw [block14]
  simp only [List.append_assoc]
  rw [List.length_append, block14Piece00_length]
  rw [List.length_append, block14Piece01_length]
  rw [List.length_append, block14Piece02_length]
  rw [List.length_append, block14Piece03_length]
  rw [List.length_append, block14Piece04_length]
  rw [List.length_append, block14Piece05_length]
  rw [List.length_append, block14Piece06_length]
  rw [block14Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14_length

theorem block14_scan : scanFrom 3584 block14 =
    [] := by
  rw [block14]
  simp only [List.append_assoc]
  rw [scan_append, block14Piece00_scan, block14Piece00_length]
  rw [scan_append, block14Piece01_scan, block14Piece01_length]
  rw [scan_append, block14Piece02_scan, block14Piece02_length]
  rw [scan_append, block14Piece03_scan, block14Piece03_length]
  rw [scan_append, block14Piece04_scan, block14Piece04_length]
  rw [scan_append, block14Piece05_scan, block14Piece05_length]
  rw [scan_append, block14Piece06_scan, block14Piece06_length]
  rw [block14Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block14_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
