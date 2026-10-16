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

def block44Piece00 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 352)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 353)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 29)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 355)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 357)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 362)] ++
  List.replicate 16 Mark.passive

def block44Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block44Piece02 : List Mark :=
  List.replicate 28 Mark.passive ++
  [.relabel (.inl 368)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 369)] ++
  List.replicate 1 Mark.passive

def block44Piece03 : List Mark :=
  [.relabel (.inl 370)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 371)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 372)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 373)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 374)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 375)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 376)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 377)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 378)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 379)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 380)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 381)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 382)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 383)] ++
  List.replicate 5 Mark.passive

def block44Piece04 : List Mark :=
  List.replicate 12 Mark.passive ++
  [.relabel (.inl 80), .relabel (.inl 88)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 368), .relabel (.inl 95)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 369), .relabel (.inl 66)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 67), .relabel (.inl 3)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 370), .relabel (.inl 8)] ++
  List.replicate 2 Mark.passive

def block44Piece05 : List Mark :=
  [.relabel (.inl 371), .relabel (.inl 26)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 372), .relabel (.inl 376)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 373), .relabel (.inl 382)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 374), .relabel (.inl 378)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 375), .relabel (.inl 380)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 377), .relabel (.inl 383)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 379), .relabel (.inl 381)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 375), .relabel (.inl 373)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 370)]

def block44Piece06 : List Mark :=
  [.relabel (.inl 368)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 374), .relabel (.inl 371)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 372), .relabel (.inl 369)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 376), .relabel (.inl 378)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 66), .relabel (.inl 26)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 380), .relabel (.inl 8)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 382), .relabel (.inl 95)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 95), .relabel (.inl 8)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 368)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 369)] ++
  List.replicate 2 Mark.passive

def block44Piece07 : List Mark :=
  [.relabel (.inl 26)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 371)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 373)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 378)] ++
  List.replicate 22 Mark.passive

def block44 : List Mark :=
  block44Piece00 ++ block44Piece01 ++ block44Piece02 ++ block44Piece03 ++ block44Piece04 ++ block44Piece05 ++ block44Piece06 ++ block44Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44

theorem block44Piece00_length : block44Piece00.length = 32 := by
  simp only [block44Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block44Piece00_scan : scanFrom 11264 block44Piece00 =
    [] := by
  simp only [block44Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44Piece00_scan

theorem block44Piece01_length : block44Piece01.length = 32 := by
  simp only [block44Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block44Piece01_scan : scanFrom 11296 block44Piece01 =
    [] := by
  simpa only [block44Piece01] using (scan_passive 11296 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44Piece01_scan

theorem block44Piece02_length : block44Piece02.length = 32 := by
  simp only [block44Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block44Piece02_scan : scanFrom 11328 block44Piece02 =
    [] := by
  simp only [block44Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44Piece02_scan

theorem block44Piece03_length : block44Piece03.length = 32 := by
  simp only [block44Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block44Piece03_scan : scanFrom 11360 block44Piece03 =
    [] := by
  simp only [block44Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44Piece03_scan

theorem block44Piece04_length : block44Piece04.length = 32 := by
  simp only [block44Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block44Piece04_scan : scanFrom 11392 block44Piece04 =
    [] := by
  simp only [block44Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44Piece04_scan

theorem block44Piece05_length : block44Piece05.length = 32 := by
  simp only [block44Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block44Piece05_scan : scanFrom 11424 block44Piece05 =
    [] := by
  simp only [block44Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44Piece05_scan

theorem block44Piece06_length : block44Piece06.length = 32 := by
  simp only [block44Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block44Piece06_scan : scanFrom 11456 block44Piece06 =
    [] := by
  simp only [block44Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44Piece06_scan

theorem block44Piece07_length : block44Piece07.length = 32 := by
  simp only [block44Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block44Piece07_scan : scanFrom 11488 block44Piece07 =
    [] := by
  simp only [block44Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44Piece07_scan

theorem block44_length : block44.length = 256 := by
  rw [block44]
  simp only [List.append_assoc]
  rw [List.length_append, block44Piece00_length]
  rw [List.length_append, block44Piece01_length]
  rw [List.length_append, block44Piece02_length]
  rw [List.length_append, block44Piece03_length]
  rw [List.length_append, block44Piece04_length]
  rw [List.length_append, block44Piece05_length]
  rw [List.length_append, block44Piece06_length]
  rw [block44Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44_length

theorem block44_scan : scanFrom 11264 block44 =
    [] := by
  rw [block44]
  simp only [List.append_assoc]
  rw [scan_append, block44Piece00_scan, block44Piece00_length]
  rw [scan_append, block44Piece01_scan, block44Piece01_length]
  rw [scan_append, block44Piece02_scan, block44Piece02_length]
  rw [scan_append, block44Piece03_scan, block44Piece03_length]
  rw [scan_append, block44Piece04_scan, block44Piece04_length]
  rw [scan_append, block44Piece05_scan, block44Piece05_length]
  rw [scan_append, block44Piece06_scan, block44Piece06_length]
  rw [block44Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block44_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
