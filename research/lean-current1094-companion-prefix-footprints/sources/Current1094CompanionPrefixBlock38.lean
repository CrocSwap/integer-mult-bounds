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

def block38Piece00 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 254), .relabel (.inl 62)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 62), .relabel (.inl 63)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 240)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 241)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 11)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 243)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 245)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 250)] ++
  List.replicate 6 Mark.passive

def block38Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block38Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block38Piece03 : List Mark :=
  List.replicate 6 Mark.passive ++
  [.relabel (.inl 256)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 257)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 258)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 259)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 260)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 261)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 262)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 263)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 264)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 265)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 266)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 267)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 268)] ++
  List.replicate 1 Mark.passive

def block38Piece04 : List Mark :=
  [.relabel (.inl 269)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 270)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 271)] ++
  List.replicate 17 Mark.passive ++
  [.relabel (.inl 72), .relabel (.inl 89)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 256), .relabel (.inl 94)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 257), .relabel (.inl 79)]

def block38Piece05 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 2), .relabel (.inl 25)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 258), .relabel (.inl 61)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 259), .relabel (.inl 9)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 260), .relabel (.inl 264)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 261), .relabel (.inl 270)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 262), .relabel (.inl 266)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 263), .relabel (.inl 268)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 265), .relabel (.inl 271)]

def block38Piece06 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 267), .relabel (.inl 269)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 263), .relabel (.inl 261)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 258), .relabel (.inl 256)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 262), .relabel (.inl 259)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 260), .relabel (.inl 257)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 264), .relabel (.inl 266)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 79), .relabel (.inl 9)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 268), .relabel (.inl 61)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 270), .relabel (.inl 94)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 94), .relabel (.inl 61)]

def block38Piece07 : List Mark :=
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 256)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 257)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 9)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 259)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 261)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 266)] ++
  List.replicate 12 Mark.passive

def block38 : List Mark :=
  block38Piece00 ++ block38Piece01 ++ block38Piece02 ++ block38Piece03 ++ block38Piece04 ++ block38Piece05 ++ block38Piece06 ++ block38Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38

theorem block38Piece00_length : block38Piece00.length = 32 := by
  simp only [block38Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block38Piece00_scan : scanFrom 9728 block38Piece00 =
    [] := by
  simp only [block38Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38Piece00_scan

theorem block38Piece01_length : block38Piece01.length = 32 := by
  simp only [block38Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block38Piece01_scan : scanFrom 9760 block38Piece01 =
    [] := by
  simpa only [block38Piece01] using (scan_passive 9760 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38Piece01_scan

theorem block38Piece02_length : block38Piece02.length = 32 := by
  simp only [block38Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block38Piece02_scan : scanFrom 9792 block38Piece02 =
    [] := by
  simpa only [block38Piece02] using (scan_passive 9792 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38Piece02_scan

theorem block38Piece03_length : block38Piece03.length = 32 := by
  simp only [block38Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block38Piece03_scan : scanFrom 9824 block38Piece03 =
    [] := by
  simp only [block38Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38Piece03_scan

theorem block38Piece04_length : block38Piece04.length = 32 := by
  simp only [block38Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block38Piece04_scan : scanFrom 9856 block38Piece04 =
    [] := by
  simp only [block38Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38Piece04_scan

theorem block38Piece05_length : block38Piece05.length = 32 := by
  simp only [block38Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block38Piece05_scan : scanFrom 9888 block38Piece05 =
    [] := by
  simp only [block38Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38Piece05_scan

theorem block38Piece06_length : block38Piece06.length = 32 := by
  simp only [block38Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block38Piece06_scan : scanFrom 9920 block38Piece06 =
    [] := by
  simp only [block38Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38Piece06_scan

theorem block38Piece07_length : block38Piece07.length = 32 := by
  simp only [block38Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block38Piece07_scan : scanFrom 9952 block38Piece07 =
    [] := by
  simp only [block38Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38Piece07_scan

theorem block38_length : block38.length = 256 := by
  rw [block38]
  simp only [List.append_assoc]
  rw [List.length_append, block38Piece00_length]
  rw [List.length_append, block38Piece01_length]
  rw [List.length_append, block38Piece02_length]
  rw [List.length_append, block38Piece03_length]
  rw [List.length_append, block38Piece04_length]
  rw [List.length_append, block38Piece05_length]
  rw [List.length_append, block38Piece06_length]
  rw [block38Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38_length

theorem block38_scan : scanFrom 9728 block38 =
    [] := by
  rw [block38]
  simp only [List.append_assoc]
  rw [scan_append, block38Piece00_scan, block38Piece00_length]
  rw [scan_append, block38Piece01_scan, block38Piece01_length]
  rw [scan_append, block38Piece02_scan, block38Piece02_length]
  rw [scan_append, block38Piece03_scan, block38Piece03_length]
  rw [scan_append, block38Piece04_scan, block38Piece04_length]
  rw [scan_append, block38Piece05_scan, block38Piece05_length]
  rw [scan_append, block38Piece06_scan, block38Piece06_length]
  rw [block38Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block38_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
