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

def block45Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block45Piece01 : List Mark :=
  List.replicate 22 Mark.passive ++
  [.relabel (.inl 384)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 385)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 386)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 387)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 388)] ++
  List.replicate 1 Mark.passive

def block45Piece02 : List Mark :=
  [.relabel (.inl 389)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 390)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 391)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 392)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 393)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 394)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 395)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 396)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 397)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 398)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 399)] ++
  List.replicate 11 Mark.passive

def block45Piece03 : List Mark :=
  List.replicate 6 Mark.passive ++
  [.relabel (.inl 68), .relabel (.inl 4)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 384), .relabel (.inl 64)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 385), .relabel (.inl 97)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 5), .relabel (.inl 69)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 386), .relabel (.inl 96)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 387), .relabel (.inl 65)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 388), .relabel (.inl 392)]

def block45Piece04 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 389), .relabel (.inl 398)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 390), .relabel (.inl 394)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 391), .relabel (.inl 396)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 393), .relabel (.inl 399)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 395), .relabel (.inl 397)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 391), .relabel (.inl 389)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 386), .relabel (.inl 384)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 390), .relabel (.inl 387)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 388)]

def block45Piece05 : List Mark :=
  [.relabel (.inl 385)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 392), .relabel (.inl 394)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 97), .relabel (.inl 65)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 396), .relabel (.inl 96)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 398), .relabel (.inl 64)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 64), .relabel (.inl 96)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 384)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 385)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 65)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 387)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 389)] ++
  List.replicate 1 Mark.passive

def block45Piece06 : List Mark :=
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 394)] ++
  List.replicate 28 Mark.passive

def block45Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block45 : List Mark :=
  block45Piece00 ++ block45Piece01 ++ block45Piece02 ++ block45Piece03 ++ block45Piece04 ++ block45Piece05 ++ block45Piece06 ++ block45Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45

theorem block45Piece00_length : block45Piece00.length = 32 := by
  simp only [block45Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block45Piece00_scan : scanFrom 11520 block45Piece00 =
    [] := by
  simpa only [block45Piece00] using (scan_passive 11520 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45Piece00_scan

theorem block45Piece01_length : block45Piece01.length = 32 := by
  simp only [block45Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block45Piece01_scan : scanFrom 11552 block45Piece01 =
    [] := by
  simp only [block45Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45Piece01_scan

theorem block45Piece02_length : block45Piece02.length = 32 := by
  simp only [block45Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block45Piece02_scan : scanFrom 11584 block45Piece02 =
    [] := by
  simp only [block45Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45Piece02_scan

theorem block45Piece03_length : block45Piece03.length = 32 := by
  simp only [block45Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block45Piece03_scan : scanFrom 11616 block45Piece03 =
    [] := by
  simp only [block45Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45Piece03_scan

theorem block45Piece04_length : block45Piece04.length = 32 := by
  simp only [block45Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block45Piece04_scan : scanFrom 11648 block45Piece04 =
    [] := by
  simp only [block45Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45Piece04_scan

theorem block45Piece05_length : block45Piece05.length = 32 := by
  simp only [block45Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block45Piece05_scan : scanFrom 11680 block45Piece05 =
    [] := by
  simp only [block45Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45Piece05_scan

theorem block45Piece06_length : block45Piece06.length = 32 := by
  simp only [block45Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block45Piece06_scan : scanFrom 11712 block45Piece06 =
    [] := by
  simp only [block45Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45Piece06_scan

theorem block45Piece07_length : block45Piece07.length = 32 := by
  simp only [block45Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block45Piece07_scan : scanFrom 11744 block45Piece07 =
    [] := by
  simpa only [block45Piece07] using (scan_passive 11744 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45Piece07_scan

theorem block45_length : block45.length = 256 := by
  rw [block45]
  simp only [List.append_assoc]
  rw [List.length_append, block45Piece00_length]
  rw [List.length_append, block45Piece01_length]
  rw [List.length_append, block45Piece02_length]
  rw [List.length_append, block45Piece03_length]
  rw [List.length_append, block45Piece04_length]
  rw [List.length_append, block45Piece05_length]
  rw [List.length_append, block45Piece06_length]
  rw [block45Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45_length

theorem block45_scan : scanFrom 11520 block45 =
    [] := by
  rw [block45]
  simp only [List.append_assoc]
  rw [scan_append, block45Piece00_scan, block45Piece00_length]
  rw [scan_append, block45Piece01_scan, block45Piece01_length]
  rw [scan_append, block45Piece02_scan, block45Piece02_length]
  rw [scan_append, block45Piece03_scan, block45Piece03_length]
  rw [scan_append, block45Piece04_scan, block45Piece04_length]
  rw [scan_append, block45Piece05_scan, block45Piece05_length]
  rw [scan_append, block45Piece06_scan, block45Piece06_length]
  rw [block45Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block45_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
