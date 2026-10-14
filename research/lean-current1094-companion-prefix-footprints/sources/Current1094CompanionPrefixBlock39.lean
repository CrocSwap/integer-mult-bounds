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

def block39Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block39Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block39Piece02 : List Mark :=
  [.relabel (.inl 272)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 273)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 274)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 275)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 276)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 277)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 278)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 279)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 280)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 281)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 282)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 283)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 284)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 285)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 286)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 287)] ++
  List.replicate 1 Mark.passive

def block39Piece03 : List Mark :=
  List.replicate 16 Mark.passive ++
  [.relabel (.inl 12), .relabel (.inl 31)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 272), .relabel (.inl 17)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 273), .relabel (.inl 38)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 100), .relabel (.inl 56)] ++
  List.replicate 2 Mark.passive

def block39Piece04 : List Mark :=
  [.relabel (.inl 274), .relabel (.inl 103)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 275), .relabel (.inl 77)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 276), .relabel (.inl 280)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 277), .relabel (.inl 286)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 278), .relabel (.inl 282)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 279), .relabel (.inl 284)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 281), .relabel (.inl 287)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 283), .relabel (.inl 285)] ++
  List.replicate 2 Mark.passive

def block39Piece05 : List Mark :=
  [.relabel (.inl 279), .relabel (.inl 277)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 274), .relabel (.inl 272)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 278), .relabel (.inl 275)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 276), .relabel (.inl 273)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 280), .relabel (.inl 282)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 38), .relabel (.inl 77)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 284), .relabel (.inl 103)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 286), .relabel (.inl 17)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 17), .relabel (.inl 103)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 272)]

def block39Piece06 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 273)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 77)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 275)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 277)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 282)] ++
  List.replicate 18 Mark.passive

def block39Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block39 : List Mark :=
  block39Piece00 ++ block39Piece01 ++ block39Piece02 ++ block39Piece03 ++ block39Piece04 ++ block39Piece05 ++ block39Piece06 ++ block39Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39

theorem block39Piece00_length : block39Piece00.length = 32 := by
  simp only [block39Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block39Piece00_scan : scanFrom 9984 block39Piece00 =
    [] := by
  simpa only [block39Piece00] using (scan_passive 9984 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39Piece00_scan

theorem block39Piece01_length : block39Piece01.length = 32 := by
  simp only [block39Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block39Piece01_scan : scanFrom 10016 block39Piece01 =
    [] := by
  simpa only [block39Piece01] using (scan_passive 10016 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39Piece01_scan

theorem block39Piece02_length : block39Piece02.length = 32 := by
  simp only [block39Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block39Piece02_scan : scanFrom 10048 block39Piece02 =
    [] := by
  simp only [block39Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39Piece02_scan

theorem block39Piece03_length : block39Piece03.length = 32 := by
  simp only [block39Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block39Piece03_scan : scanFrom 10080 block39Piece03 =
    [] := by
  simp only [block39Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39Piece03_scan

theorem block39Piece04_length : block39Piece04.length = 32 := by
  simp only [block39Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block39Piece04_scan : scanFrom 10112 block39Piece04 =
    [] := by
  simp only [block39Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39Piece04_scan

theorem block39Piece05_length : block39Piece05.length = 32 := by
  simp only [block39Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block39Piece05_scan : scanFrom 10144 block39Piece05 =
    [] := by
  simp only [block39Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39Piece05_scan

theorem block39Piece06_length : block39Piece06.length = 32 := by
  simp only [block39Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block39Piece06_scan : scanFrom 10176 block39Piece06 =
    [] := by
  simp only [block39Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39Piece06_scan

theorem block39Piece07_length : block39Piece07.length = 32 := by
  simp only [block39Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block39Piece07_scan : scanFrom 10208 block39Piece07 =
    [] := by
  simpa only [block39Piece07] using (scan_passive 10208 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39Piece07_scan

theorem block39_length : block39.length = 256 := by
  rw [block39]
  simp only [List.append_assoc]
  rw [List.length_append, block39Piece00_length]
  rw [List.length_append, block39Piece01_length]
  rw [List.length_append, block39Piece02_length]
  rw [List.length_append, block39Piece03_length]
  rw [List.length_append, block39Piece04_length]
  rw [List.length_append, block39Piece05_length]
  rw [List.length_append, block39Piece06_length]
  rw [block39Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39_length

theorem block39_scan : scanFrom 9984 block39 =
    [] := by
  rw [block39]
  simp only [List.append_assoc]
  rw [scan_append, block39Piece00_scan, block39Piece00_length]
  rw [scan_append, block39Piece01_scan, block39Piece01_length]
  rw [scan_append, block39Piece02_scan, block39Piece02_length]
  rw [scan_append, block39Piece03_scan, block39Piece03_length]
  rw [scan_append, block39Piece04_scan, block39Piece04_length]
  rw [scan_append, block39Piece05_scan, block39Piece05_length]
  rw [scan_append, block39Piece06_scan, block39Piece06_length]
  rw [block39Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block39_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
