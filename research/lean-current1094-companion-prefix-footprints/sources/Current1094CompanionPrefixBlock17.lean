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

def block17Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block17Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block17Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block17Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block17Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block17Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block17Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block17Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block17 : List Mark :=
  block17Piece00 ++ block17Piece01 ++ block17Piece02 ++ block17Piece03 ++ block17Piece04 ++ block17Piece05 ++ block17Piece06 ++ block17Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17

theorem block17Piece00_length : block17Piece00.length = 32 := by
  simp only [block17Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block17Piece00_scan : scanFrom 4352 block17Piece00 =
    [] := by
  simpa only [block17Piece00] using (scan_passive 4352 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17Piece00_scan

theorem block17Piece01_length : block17Piece01.length = 32 := by
  simp only [block17Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block17Piece01_scan : scanFrom 4384 block17Piece01 =
    [] := by
  simpa only [block17Piece01] using (scan_passive 4384 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17Piece01_scan

theorem block17Piece02_length : block17Piece02.length = 32 := by
  simp only [block17Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block17Piece02_scan : scanFrom 4416 block17Piece02 =
    [] := by
  simpa only [block17Piece02] using (scan_passive 4416 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17Piece02_scan

theorem block17Piece03_length : block17Piece03.length = 32 := by
  simp only [block17Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block17Piece03_scan : scanFrom 4448 block17Piece03 =
    [] := by
  simpa only [block17Piece03] using (scan_passive 4448 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17Piece03_scan

theorem block17Piece04_length : block17Piece04.length = 32 := by
  simp only [block17Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block17Piece04_scan : scanFrom 4480 block17Piece04 =
    [] := by
  simpa only [block17Piece04] using (scan_passive 4480 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17Piece04_scan

theorem block17Piece05_length : block17Piece05.length = 32 := by
  simp only [block17Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block17Piece05_scan : scanFrom 4512 block17Piece05 =
    [] := by
  simpa only [block17Piece05] using (scan_passive 4512 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17Piece05_scan

theorem block17Piece06_length : block17Piece06.length = 32 := by
  simp only [block17Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block17Piece06_scan : scanFrom 4544 block17Piece06 =
    [] := by
  simpa only [block17Piece06] using (scan_passive 4544 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17Piece06_scan

theorem block17Piece07_length : block17Piece07.length = 32 := by
  simp only [block17Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block17Piece07_scan : scanFrom 4576 block17Piece07 =
    [] := by
  simpa only [block17Piece07] using (scan_passive 4576 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17Piece07_scan

theorem block17_length : block17.length = 256 := by
  rw [block17]
  simp only [List.append_assoc]
  rw [List.length_append, block17Piece00_length]
  rw [List.length_append, block17Piece01_length]
  rw [List.length_append, block17Piece02_length]
  rw [List.length_append, block17Piece03_length]
  rw [List.length_append, block17Piece04_length]
  rw [List.length_append, block17Piece05_length]
  rw [List.length_append, block17Piece06_length]
  rw [block17Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17_length

theorem block17_scan : scanFrom 4352 block17 =
    [] := by
  rw [block17]
  simp only [List.append_assoc]
  rw [scan_append, block17Piece00_scan, block17Piece00_length]
  rw [scan_append, block17Piece01_scan, block17Piece01_length]
  rw [scan_append, block17Piece02_scan, block17Piece02_length]
  rw [scan_append, block17Piece03_scan, block17Piece03_length]
  rw [scan_append, block17Piece04_scan, block17Piece04_length]
  rw [scan_append, block17Piece05_scan, block17Piece05_length]
  rw [scan_append, block17Piece06_scan, block17Piece06_length]
  rw [block17Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block17_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
