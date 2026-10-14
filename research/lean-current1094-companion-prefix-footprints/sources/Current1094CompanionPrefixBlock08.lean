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

def block08Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block08Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block08Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block08Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block08Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block08Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block08Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block08Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block08 : List Mark :=
  block08Piece00 ++ block08Piece01 ++ block08Piece02 ++ block08Piece03 ++ block08Piece04 ++ block08Piece05 ++ block08Piece06 ++ block08Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08

theorem block08Piece00_length : block08Piece00.length = 32 := by
  simp only [block08Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block08Piece00_scan : scanFrom 2048 block08Piece00 =
    [] := by
  simpa only [block08Piece00] using (scan_passive 2048 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08Piece00_scan

theorem block08Piece01_length : block08Piece01.length = 32 := by
  simp only [block08Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block08Piece01_scan : scanFrom 2080 block08Piece01 =
    [] := by
  simpa only [block08Piece01] using (scan_passive 2080 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08Piece01_scan

theorem block08Piece02_length : block08Piece02.length = 32 := by
  simp only [block08Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block08Piece02_scan : scanFrom 2112 block08Piece02 =
    [] := by
  simpa only [block08Piece02] using (scan_passive 2112 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08Piece02_scan

theorem block08Piece03_length : block08Piece03.length = 32 := by
  simp only [block08Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block08Piece03_scan : scanFrom 2144 block08Piece03 =
    [] := by
  simpa only [block08Piece03] using (scan_passive 2144 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08Piece03_scan

theorem block08Piece04_length : block08Piece04.length = 32 := by
  simp only [block08Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block08Piece04_scan : scanFrom 2176 block08Piece04 =
    [] := by
  simpa only [block08Piece04] using (scan_passive 2176 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08Piece04_scan

theorem block08Piece05_length : block08Piece05.length = 32 := by
  simp only [block08Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block08Piece05_scan : scanFrom 2208 block08Piece05 =
    [] := by
  simpa only [block08Piece05] using (scan_passive 2208 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08Piece05_scan

theorem block08Piece06_length : block08Piece06.length = 32 := by
  simp only [block08Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block08Piece06_scan : scanFrom 2240 block08Piece06 =
    [] := by
  simpa only [block08Piece06] using (scan_passive 2240 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08Piece06_scan

theorem block08Piece07_length : block08Piece07.length = 32 := by
  simp only [block08Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block08Piece07_scan : scanFrom 2272 block08Piece07 =
    [] := by
  simpa only [block08Piece07] using (scan_passive 2272 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08Piece07_scan

theorem block08_length : block08.length = 256 := by
  rw [block08]
  simp only [List.append_assoc]
  rw [List.length_append, block08Piece00_length]
  rw [List.length_append, block08Piece01_length]
  rw [List.length_append, block08Piece02_length]
  rw [List.length_append, block08Piece03_length]
  rw [List.length_append, block08Piece04_length]
  rw [List.length_append, block08Piece05_length]
  rw [List.length_append, block08Piece06_length]
  rw [block08Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08_length

theorem block08_scan : scanFrom 2048 block08 =
    [] := by
  rw [block08]
  simp only [List.append_assoc]
  rw [scan_append, block08Piece00_scan, block08Piece00_length]
  rw [scan_append, block08Piece01_scan, block08Piece01_length]
  rw [scan_append, block08Piece02_scan, block08Piece02_length]
  rw [scan_append, block08Piece03_scan, block08Piece03_length]
  rw [scan_append, block08Piece04_scan, block08Piece04_length]
  rw [scan_append, block08Piece05_scan, block08Piece05_length]
  rw [scan_append, block08Piece06_scan, block08Piece06_length]
  rw [block08Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block08_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
