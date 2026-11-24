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

def block02Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block02Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block02Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block02Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block02Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block02Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block02Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block02Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block02 : List Mark :=
  block02Piece00 ++ block02Piece01 ++ block02Piece02 ++ block02Piece03 ++ block02Piece04 ++ block02Piece05 ++ block02Piece06 ++ block02Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02

theorem block02Piece00_length : block02Piece00.length = 32 := by
  simp only [block02Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block02Piece00_scan : scanFrom 512 block02Piece00 =
    [] := by
  simpa only [block02Piece00] using (scan_passive 512 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02Piece00_scan

theorem block02Piece01_length : block02Piece01.length = 32 := by
  simp only [block02Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block02Piece01_scan : scanFrom 544 block02Piece01 =
    [] := by
  simpa only [block02Piece01] using (scan_passive 544 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02Piece01_scan

theorem block02Piece02_length : block02Piece02.length = 32 := by
  simp only [block02Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block02Piece02_scan : scanFrom 576 block02Piece02 =
    [] := by
  simpa only [block02Piece02] using (scan_passive 576 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02Piece02_scan

theorem block02Piece03_length : block02Piece03.length = 32 := by
  simp only [block02Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block02Piece03_scan : scanFrom 608 block02Piece03 =
    [] := by
  simpa only [block02Piece03] using (scan_passive 608 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02Piece03_scan

theorem block02Piece04_length : block02Piece04.length = 32 := by
  simp only [block02Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block02Piece04_scan : scanFrom 640 block02Piece04 =
    [] := by
  simpa only [block02Piece04] using (scan_passive 640 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02Piece04_scan

theorem block02Piece05_length : block02Piece05.length = 32 := by
  simp only [block02Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block02Piece05_scan : scanFrom 672 block02Piece05 =
    [] := by
  simpa only [block02Piece05] using (scan_passive 672 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02Piece05_scan

theorem block02Piece06_length : block02Piece06.length = 32 := by
  simp only [block02Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block02Piece06_scan : scanFrom 704 block02Piece06 =
    [] := by
  simpa only [block02Piece06] using (scan_passive 704 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02Piece06_scan

theorem block02Piece07_length : block02Piece07.length = 32 := by
  simp only [block02Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block02Piece07_scan : scanFrom 736 block02Piece07 =
    [] := by
  simpa only [block02Piece07] using (scan_passive 736 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02Piece07_scan

theorem block02_length : block02.length = 256 := by
  rw [block02]
  simp only [List.append_assoc]
  rw [List.length_append, block02Piece00_length]
  rw [List.length_append, block02Piece01_length]
  rw [List.length_append, block02Piece02_length]
  rw [List.length_append, block02Piece03_length]
  rw [List.length_append, block02Piece04_length]
  rw [List.length_append, block02Piece05_length]
  rw [List.length_append, block02Piece06_length]
  rw [block02Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02_length

theorem block02_scan : scanFrom 512 block02 =
    [] := by
  rw [block02]
  simp only [List.append_assoc]
  rw [scan_append, block02Piece00_scan, block02Piece00_length]
  rw [scan_append, block02Piece01_scan, block02Piece01_length]
  rw [scan_append, block02Piece02_scan, block02Piece02_length]
  rw [scan_append, block02Piece03_scan, block02Piece03_length]
  rw [scan_append, block02Piece04_scan, block02Piece04_length]
  rw [scan_append, block02Piece05_scan, block02Piece05_length]
  rw [scan_append, block02Piece06_scan, block02Piece06_length]
  rw [block02Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block02_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
