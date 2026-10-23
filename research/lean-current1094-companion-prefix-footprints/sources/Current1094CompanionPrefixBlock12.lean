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

def block12Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block12Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block12Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block12Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block12Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block12Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block12Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block12Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block12 : List Mark :=
  block12Piece00 ++ block12Piece01 ++ block12Piece02 ++ block12Piece03 ++ block12Piece04 ++ block12Piece05 ++ block12Piece06 ++ block12Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12

theorem block12Piece00_length : block12Piece00.length = 32 := by
  simp only [block12Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block12Piece00_scan : scanFrom 3072 block12Piece00 =
    [] := by
  simpa only [block12Piece00] using (scan_passive 3072 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12Piece00_scan

theorem block12Piece01_length : block12Piece01.length = 32 := by
  simp only [block12Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block12Piece01_scan : scanFrom 3104 block12Piece01 =
    [] := by
  simpa only [block12Piece01] using (scan_passive 3104 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12Piece01_scan

theorem block12Piece02_length : block12Piece02.length = 32 := by
  simp only [block12Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block12Piece02_scan : scanFrom 3136 block12Piece02 =
    [] := by
  simpa only [block12Piece02] using (scan_passive 3136 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12Piece02_scan

theorem block12Piece03_length : block12Piece03.length = 32 := by
  simp only [block12Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block12Piece03_scan : scanFrom 3168 block12Piece03 =
    [] := by
  simpa only [block12Piece03] using (scan_passive 3168 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12Piece03_scan

theorem block12Piece04_length : block12Piece04.length = 32 := by
  simp only [block12Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block12Piece04_scan : scanFrom 3200 block12Piece04 =
    [] := by
  simpa only [block12Piece04] using (scan_passive 3200 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12Piece04_scan

theorem block12Piece05_length : block12Piece05.length = 32 := by
  simp only [block12Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block12Piece05_scan : scanFrom 3232 block12Piece05 =
    [] := by
  simpa only [block12Piece05] using (scan_passive 3232 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12Piece05_scan

theorem block12Piece06_length : block12Piece06.length = 32 := by
  simp only [block12Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block12Piece06_scan : scanFrom 3264 block12Piece06 =
    [] := by
  simpa only [block12Piece06] using (scan_passive 3264 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12Piece06_scan

theorem block12Piece07_length : block12Piece07.length = 32 := by
  simp only [block12Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block12Piece07_scan : scanFrom 3296 block12Piece07 =
    [] := by
  simpa only [block12Piece07] using (scan_passive 3296 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12Piece07_scan

theorem block12_length : block12.length = 256 := by
  rw [block12]
  simp only [List.append_assoc]
  rw [List.length_append, block12Piece00_length]
  rw [List.length_append, block12Piece01_length]
  rw [List.length_append, block12Piece02_length]
  rw [List.length_append, block12Piece03_length]
  rw [List.length_append, block12Piece04_length]
  rw [List.length_append, block12Piece05_length]
  rw [List.length_append, block12Piece06_length]
  rw [block12Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12_length

theorem block12_scan : scanFrom 3072 block12 =
    [] := by
  rw [block12]
  simp only [List.append_assoc]
  rw [scan_append, block12Piece00_scan, block12Piece00_length]
  rw [scan_append, block12Piece01_scan, block12Piece01_length]
  rw [scan_append, block12Piece02_scan, block12Piece02_length]
  rw [scan_append, block12Piece03_scan, block12Piece03_length]
  rw [scan_append, block12Piece04_scan, block12Piece04_length]
  rw [scan_append, block12Piece05_scan, block12Piece05_length]
  rw [scan_append, block12Piece06_scan, block12Piece06_length]
  rw [block12Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block12_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
