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

def block64Piece00 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 691)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 692)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 482), .relabel (.inl 494)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 223), .relabel (.inl 482)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 158), .relabel (.inl 494)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 483), .relabel (.inl 495)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 148), .relabel (.inl 483)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 132), .relabel (.inl 495)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 506), .relabel (.inl 518)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 506)] ++
  List.replicate 1 Mark.passive

def block64Piece01 : List Mark :=
  [.relabel (.inl 518)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 507), .relabel (.inl 519)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 507)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 519)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 696), .relabel (.inl 703)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 159), .relabel (.inl 696)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 222), .relabel (.inl 703)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 697), .relabel (.inl 702)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 133), .relabel (.inl 697)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 149), .relabel (.inl 702)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 698), .relabel (.inl 701)]

def block64Piece02 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 698)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 701)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 699), .relabel (.inl 700)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 699)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 700)] ++
  List.replicate 1 Mark.passive ++
  [.phase "cleanup_tail", .relabel (.inl 3), .relabel (.inl 584)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 556), .relabel (.inl 454)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 351), .relabel (.inl 587)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 383), .relabel (.inl 585)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 557), .relabel (.inl 455)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 399), .relabel (.inl 591)]

def block64Piece03 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 69), .relabel (.inl 590)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 533), .relabel (.inl 453)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 532), .relabel (.inl 452)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 509), .relabel (.inl 451)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 508), .relabel (.inl 450)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 485), .relabel (.inl 449)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 484), .relabel (.inl 448)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 231)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 226)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 230)] ++
  List.replicate 1 Mark.passive

def block64 : List Mark :=
  block64Piece00 ++ block64Piece01 ++ block64Piece02 ++ block64Piece03

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block64

theorem block64Piece00_length : block64Piece00.length = 32 := by
  simp only [block64Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block64Piece00_scan : scanFrom 16384 block64Piece00 =
    [] := by
  simp only [block64Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block64Piece00_scan

theorem block64Piece01_length : block64Piece01.length = 32 := by
  simp only [block64Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block64Piece01_scan : scanFrom 16416 block64Piece01 =
    [] := by
  simp only [block64Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block64Piece01_scan

theorem block64Piece02_length : block64Piece02.length = 32 := by
  simp only [block64Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block64Piece02_scan : scanFrom 16448 block64Piece02 =
    [(16462, .phase "cleanup_tail")] := by
  simp only [block64Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block64Piece02_scan

theorem block64Piece03_length : block64Piece03.length = 28 := by
  simp only [block64Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block64Piece03_scan : scanFrom 16480 block64Piece03 =
    [(16493, .relabel (.inl 508)), (16506, .relabel (.inl 230))] := by
  simp only [block64Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block64Piece03_scan

theorem block64_length : block64.length = 124 := by
  rw [block64]
  simp only [List.append_assoc]
  rw [List.length_append, block64Piece00_length]
  rw [List.length_append, block64Piece01_length]
  rw [List.length_append, block64Piece02_length]
  rw [block64Piece03_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block64_length

theorem block64_scan : scanFrom 16384 block64 =
    [(16462, .phase "cleanup_tail"), (16493, .relabel (.inl 508)), (16506, .relabel (.inl 230))] := by
  rw [block64]
  simp only [List.append_assoc]
  rw [scan_append, block64Piece00_scan, block64Piece00_length]
  rw [scan_append, block64Piece01_scan, block64Piece01_length]
  rw [scan_append, block64Piece02_scan, block64Piece02_length]
  rw [block64Piece03_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block64_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
