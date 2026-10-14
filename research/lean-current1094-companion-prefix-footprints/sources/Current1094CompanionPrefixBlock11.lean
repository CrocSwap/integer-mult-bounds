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

def block11Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block11Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block11Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block11Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block11Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block11Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block11Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block11Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block11 : List Mark :=
  block11Piece00 ++ block11Piece01 ++ block11Piece02 ++ block11Piece03 ++ block11Piece04 ++ block11Piece05 ++ block11Piece06 ++ block11Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11

theorem block11Piece00_length : block11Piece00.length = 32 := by
  simp only [block11Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block11Piece00_scan : scanFrom 2816 block11Piece00 =
    [] := by
  simpa only [block11Piece00] using (scan_passive 2816 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11Piece00_scan

theorem block11Piece01_length : block11Piece01.length = 32 := by
  simp only [block11Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block11Piece01_scan : scanFrom 2848 block11Piece01 =
    [] := by
  simpa only [block11Piece01] using (scan_passive 2848 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11Piece01_scan

theorem block11Piece02_length : block11Piece02.length = 32 := by
  simp only [block11Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block11Piece02_scan : scanFrom 2880 block11Piece02 =
    [] := by
  simpa only [block11Piece02] using (scan_passive 2880 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11Piece02_scan

theorem block11Piece03_length : block11Piece03.length = 32 := by
  simp only [block11Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block11Piece03_scan : scanFrom 2912 block11Piece03 =
    [] := by
  simpa only [block11Piece03] using (scan_passive 2912 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11Piece03_scan

theorem block11Piece04_length : block11Piece04.length = 32 := by
  simp only [block11Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block11Piece04_scan : scanFrom 2944 block11Piece04 =
    [] := by
  simpa only [block11Piece04] using (scan_passive 2944 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11Piece04_scan

theorem block11Piece05_length : block11Piece05.length = 32 := by
  simp only [block11Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block11Piece05_scan : scanFrom 2976 block11Piece05 =
    [] := by
  simpa only [block11Piece05] using (scan_passive 2976 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11Piece05_scan

theorem block11Piece06_length : block11Piece06.length = 32 := by
  simp only [block11Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block11Piece06_scan : scanFrom 3008 block11Piece06 =
    [] := by
  simpa only [block11Piece06] using (scan_passive 3008 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11Piece06_scan

theorem block11Piece07_length : block11Piece07.length = 32 := by
  simp only [block11Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block11Piece07_scan : scanFrom 3040 block11Piece07 =
    [] := by
  simpa only [block11Piece07] using (scan_passive 3040 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11Piece07_scan

theorem block11_length : block11.length = 256 := by
  rw [block11]
  simp only [List.append_assoc]
  rw [List.length_append, block11Piece00_length]
  rw [List.length_append, block11Piece01_length]
  rw [List.length_append, block11Piece02_length]
  rw [List.length_append, block11Piece03_length]
  rw [List.length_append, block11Piece04_length]
  rw [List.length_append, block11Piece05_length]
  rw [List.length_append, block11Piece06_length]
  rw [block11Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11_length

theorem block11_scan : scanFrom 2816 block11 =
    [] := by
  rw [block11]
  simp only [List.append_assoc]
  rw [scan_append, block11Piece00_scan, block11Piece00_length]
  rw [scan_append, block11Piece01_scan, block11Piece01_length]
  rw [scan_append, block11Piece02_scan, block11Piece02_length]
  rw [scan_append, block11Piece03_scan, block11Piece03_length]
  rw [scan_append, block11Piece04_scan, block11Piece04_length]
  rw [scan_append, block11Piece05_scan, block11Piece05_length]
  rw [scan_append, block11Piece06_scan, block11Piece06_length]
  rw [block11Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block11_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
