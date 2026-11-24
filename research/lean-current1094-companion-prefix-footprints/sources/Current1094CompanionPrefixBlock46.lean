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

def block46Piece00 : List Mark :=
  List.replicate 16 Mark.passive ++
  [.relabel (.inl 400)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 401)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 402)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 403)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 404)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 405)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 406)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 407)] ++
  List.replicate 1 Mark.passive

def block46Piece01 : List Mark :=
  [.relabel (.inl 408)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 409)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 410)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 411)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 412)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 413)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 414)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 415)] ++
  List.replicate 17 Mark.passive

def block46Piece02 : List Mark :=
  [.relabel (.inl 15), .relabel (.inl 53)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 400), .relabel (.inl 42)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 401), .relabel (.inl 105)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 14), .relabel (.inl 52)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 402), .relabel (.inl 41)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 403), .relabel (.inl 106)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 404), .relabel (.inl 408)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 405), .relabel (.inl 414)] ++
  List.replicate 2 Mark.passive

def block46Piece03 : List Mark :=
  [.relabel (.inl 406), .relabel (.inl 410)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 407), .relabel (.inl 412)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 409), .relabel (.inl 415)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 411), .relabel (.inl 413)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 407), .relabel (.inl 405)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 402), .relabel (.inl 400)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 406), .relabel (.inl 403)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 404), .relabel (.inl 401)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 408), .relabel (.inl 410)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 105)]

def block46Piece04 : List Mark :=
  [.relabel (.inl 106)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 412), .relabel (.inl 41)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 414), .relabel (.inl 42)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 42), .relabel (.inl 41)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 400)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 401)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 106)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 403)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 405)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 410)] ++
  List.replicate 2 Mark.passive

def block46Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block46Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block46Piece07 : List Mark :=
  List.replicate 10 Mark.passive ++
  [.relabel (.inl 416)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 417)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 418)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 419)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 420)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 421)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 422)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 423)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 424)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 425)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 426)] ++
  List.replicate 1 Mark.passive

def block46 : List Mark :=
  block46Piece00 ++ block46Piece01 ++ block46Piece02 ++ block46Piece03 ++ block46Piece04 ++ block46Piece05 ++ block46Piece06 ++ block46Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46

theorem block46Piece00_length : block46Piece00.length = 32 := by
  simp only [block46Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block46Piece00_scan : scanFrom 11776 block46Piece00 =
    [] := by
  simp only [block46Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46Piece00_scan

theorem block46Piece01_length : block46Piece01.length = 32 := by
  simp only [block46Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block46Piece01_scan : scanFrom 11808 block46Piece01 =
    [] := by
  simp only [block46Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46Piece01_scan

theorem block46Piece02_length : block46Piece02.length = 32 := by
  simp only [block46Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block46Piece02_scan : scanFrom 11840 block46Piece02 =
    [] := by
  simp only [block46Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46Piece02_scan

theorem block46Piece03_length : block46Piece03.length = 32 := by
  simp only [block46Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block46Piece03_scan : scanFrom 11872 block46Piece03 =
    [] := by
  simp only [block46Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46Piece03_scan

theorem block46Piece04_length : block46Piece04.length = 32 := by
  simp only [block46Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block46Piece04_scan : scanFrom 11904 block46Piece04 =
    [] := by
  simp only [block46Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46Piece04_scan

theorem block46Piece05_length : block46Piece05.length = 32 := by
  simp only [block46Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block46Piece05_scan : scanFrom 11936 block46Piece05 =
    [] := by
  simpa only [block46Piece05] using (scan_passive 11936 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46Piece05_scan

theorem block46Piece06_length : block46Piece06.length = 32 := by
  simp only [block46Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block46Piece06_scan : scanFrom 11968 block46Piece06 =
    [] := by
  simpa only [block46Piece06] using (scan_passive 11968 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46Piece06_scan

theorem block46Piece07_length : block46Piece07.length = 32 := by
  simp only [block46Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block46Piece07_scan : scanFrom 12000 block46Piece07 =
    [] := by
  simp only [block46Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46Piece07_scan

theorem block46_length : block46.length = 256 := by
  rw [block46]
  simp only [List.append_assoc]
  rw [List.length_append, block46Piece00_length]
  rw [List.length_append, block46Piece01_length]
  rw [List.length_append, block46Piece02_length]
  rw [List.length_append, block46Piece03_length]
  rw [List.length_append, block46Piece04_length]
  rw [List.length_append, block46Piece05_length]
  rw [List.length_append, block46Piece06_length]
  rw [block46Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46_length

theorem block46_scan : scanFrom 11776 block46 =
    [] := by
  rw [block46]
  simp only [List.append_assoc]
  rw [scan_append, block46Piece00_scan, block46Piece00_length]
  rw [scan_append, block46Piece01_scan, block46Piece01_length]
  rw [scan_append, block46Piece02_scan, block46Piece02_length]
  rw [scan_append, block46Piece03_scan, block46Piece03_length]
  rw [scan_append, block46Piece04_scan, block46Piece04_length]
  rw [scan_append, block46Piece05_scan, block46Piece05_length]
  rw [scan_append, block46Piece06_scan, block46Piece06_length]
  rw [block46Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block46_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
