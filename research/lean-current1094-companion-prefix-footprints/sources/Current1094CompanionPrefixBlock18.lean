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

def block18Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block18Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block18Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block18Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block18Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block18Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block18Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block18Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block18 : List Mark :=
  block18Piece00 ++ block18Piece01 ++ block18Piece02 ++ block18Piece03 ++ block18Piece04 ++ block18Piece05 ++ block18Piece06 ++ block18Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18

theorem block18Piece00_length : block18Piece00.length = 32 := by
  simp only [block18Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block18Piece00_scan : scanFrom 4608 block18Piece00 =
    [] := by
  simpa only [block18Piece00] using (scan_passive 4608 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18Piece00_scan

theorem block18Piece01_length : block18Piece01.length = 32 := by
  simp only [block18Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block18Piece01_scan : scanFrom 4640 block18Piece01 =
    [] := by
  simpa only [block18Piece01] using (scan_passive 4640 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18Piece01_scan

theorem block18Piece02_length : block18Piece02.length = 32 := by
  simp only [block18Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block18Piece02_scan : scanFrom 4672 block18Piece02 =
    [] := by
  simpa only [block18Piece02] using (scan_passive 4672 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18Piece02_scan

theorem block18Piece03_length : block18Piece03.length = 32 := by
  simp only [block18Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block18Piece03_scan : scanFrom 4704 block18Piece03 =
    [] := by
  simpa only [block18Piece03] using (scan_passive 4704 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18Piece03_scan

theorem block18Piece04_length : block18Piece04.length = 32 := by
  simp only [block18Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block18Piece04_scan : scanFrom 4736 block18Piece04 =
    [] := by
  simpa only [block18Piece04] using (scan_passive 4736 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18Piece04_scan

theorem block18Piece05_length : block18Piece05.length = 32 := by
  simp only [block18Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block18Piece05_scan : scanFrom 4768 block18Piece05 =
    [] := by
  simpa only [block18Piece05] using (scan_passive 4768 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18Piece05_scan

theorem block18Piece06_length : block18Piece06.length = 32 := by
  simp only [block18Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block18Piece06_scan : scanFrom 4800 block18Piece06 =
    [] := by
  simpa only [block18Piece06] using (scan_passive 4800 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18Piece06_scan

theorem block18Piece07_length : block18Piece07.length = 32 := by
  simp only [block18Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block18Piece07_scan : scanFrom 4832 block18Piece07 =
    [] := by
  simpa only [block18Piece07] using (scan_passive 4832 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18Piece07_scan

theorem block18_length : block18.length = 256 := by
  rw [block18]
  simp only [List.append_assoc]
  rw [List.length_append, block18Piece00_length]
  rw [List.length_append, block18Piece01_length]
  rw [List.length_append, block18Piece02_length]
  rw [List.length_append, block18Piece03_length]
  rw [List.length_append, block18Piece04_length]
  rw [List.length_append, block18Piece05_length]
  rw [List.length_append, block18Piece06_length]
  rw [block18Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18_length

theorem block18_scan : scanFrom 4608 block18 =
    [] := by
  rw [block18]
  simp only [List.append_assoc]
  rw [scan_append, block18Piece00_scan, block18Piece00_length]
  rw [scan_append, block18Piece01_scan, block18Piece01_length]
  rw [scan_append, block18Piece02_scan, block18Piece02_length]
  rw [scan_append, block18Piece03_scan, block18Piece03_length]
  rw [scan_append, block18Piece04_scan, block18Piece04_length]
  rw [scan_append, block18Piece05_scan, block18Piece05_length]
  rw [scan_append, block18Piece06_scan, block18Piece06_length]
  rw [block18Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block18_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
