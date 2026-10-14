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

def block49BackwardPiece00 : List Mark :=
  [.relabel (.inl 384)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 416)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 432)] ++
  List.replicate 1 Mark.passive ++
  [.phase "centers", .clear (.inr 0)] ++
  List.replicate 22 Mark.passive ++
  [.relabel (.inr 0)] ++
  List.replicate 1 Mark.passive

def block49BackwardPiece01 : List Mark :=
  [.clear (.inr 0), .clear (.inr 1)] ++
  List.replicate 22 Mark.passive ++
  [.relabel (.inr 1)] ++
  List.replicate 1 Mark.passive ++
  [.clear (.inr 1), .clear (.inr 2)] ++
  List.replicate 4 Mark.passive

def block49BackwardPiece02 : List Mark :=
  List.replicate 18 Mark.passive ++
  [.relabel (.inr 2)] ++
  List.replicate 1 Mark.passive ++
  [.clear (.inr 2), .clear (.inr 3)] ++
  List.replicate 10 Mark.passive

def block49BackwardPiece03 : List Mark :=
  List.replicate 12 Mark.passive ++
  [.relabel (.inr 3)] ++
  List.replicate 1 Mark.passive ++
  [.clear (.inr 3), .clear (.inr 4)] ++
  List.replicate 16 Mark.passive

def block49BackwardPiece04 : List Mark :=
  List.replicate 6 Mark.passive ++
  [.relabel (.inr 4)] ++
  List.replicate 1 Mark.passive ++
  [.clear (.inr 4), .clear (.inr 5)] ++
  List.replicate 22 Mark.passive

def block49BackwardPiece05 : List Mark :=
  [.relabel (.inr 5)] ++
  List.replicate 1 Mark.passive ++
  [.clear (.inr 5), .clear (.inr 6)] ++
  List.replicate 22 Mark.passive ++
  [.relabel (.inr 6)] ++
  List.replicate 1 Mark.passive ++
  [.clear (.inr 6), .clear (.inr 7)] ++
  List.replicate 2 Mark.passive

def block49BackwardPiece06 : List Mark :=
  List.replicate 20 Mark.passive ++
  [.relabel (.inr 7)] ++
  List.replicate 1 Mark.passive ++
  [.clear (.inr 7), .phase "B", .relabel (.inl 215)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 129)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 124)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 212)] ++
  List.replicate 1 Mark.passive

def block49BackwardPiece07 : List Mark :=
  [.relabel (.inl 157)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 219)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 210)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 160)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 205)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 170)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 118)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 194)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 120)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 207)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 192)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 179)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 130)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 213)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 220)] ++
  List.replicate 1 Mark.passive

def block49Backward : List Mark :=
  block49BackwardPiece00 ++ block49BackwardPiece01 ++ block49BackwardPiece02 ++ block49BackwardPiece03 ++ block49BackwardPiece04 ++ block49BackwardPiece05 ++ block49BackwardPiece06 ++ block49BackwardPiece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Backward

theorem block49BackwardPiece00_length : block49BackwardPiece00.length = 32 := by
  simp only [block49BackwardPiece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49BackwardPiece00_scan : scanFrom 12544 block49BackwardPiece00 =
    [(12550, .phase "centers")] := by
  simp only [block49BackwardPiece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49BackwardPiece00_scan

theorem block49BackwardPiece01_length : block49BackwardPiece01.length = 32 := by
  simp only [block49BackwardPiece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49BackwardPiece01_scan : scanFrom 12576 block49BackwardPiece01 =
    [] := by
  simp only [block49BackwardPiece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49BackwardPiece01_scan

theorem block49BackwardPiece02_length : block49BackwardPiece02.length = 32 := by
  simp only [block49BackwardPiece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49BackwardPiece02_scan : scanFrom 12608 block49BackwardPiece02 =
    [] := by
  simp only [block49BackwardPiece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49BackwardPiece02_scan

theorem block49BackwardPiece03_length : block49BackwardPiece03.length = 32 := by
  simp only [block49BackwardPiece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49BackwardPiece03_scan : scanFrom 12640 block49BackwardPiece03 =
    [] := by
  simp only [block49BackwardPiece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49BackwardPiece03_scan

theorem block49BackwardPiece04_length : block49BackwardPiece04.length = 32 := by
  simp only [block49BackwardPiece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49BackwardPiece04_scan : scanFrom 12672 block49BackwardPiece04 =
    [] := by
  simp only [block49BackwardPiece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49BackwardPiece04_scan

theorem block49BackwardPiece05_length : block49BackwardPiece05.length = 32 := by
  simp only [block49BackwardPiece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49BackwardPiece05_scan : scanFrom 12704 block49BackwardPiece05 =
    [] := by
  simp only [block49BackwardPiece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49BackwardPiece05_scan

theorem block49BackwardPiece06_length : block49BackwardPiece06.length = 32 := by
  simp only [block49BackwardPiece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49BackwardPiece06_scan : scanFrom 12736 block49BackwardPiece06 =
    [(12759, .phase "B")] := by
  simp only [block49BackwardPiece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49BackwardPiece06_scan

theorem block49BackwardPiece07_length : block49BackwardPiece07.length = 32 := by
  simp only [block49BackwardPiece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49BackwardPiece07_scan : scanFrom 12768 block49BackwardPiece07 =
    [(12768, .relabel (.inl 157)), (12770, .relabel (.inl 219))] := by
  simp only [block49BackwardPiece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49BackwardPiece07_scan

theorem block49Backward_length : block49Backward.length = 256 := by
  rw [block49Backward]
  simp only [List.append_assoc]
  rw [List.length_append, block49BackwardPiece00_length]
  rw [List.length_append, block49BackwardPiece01_length]
  rw [List.length_append, block49BackwardPiece02_length]
  rw [List.length_append, block49BackwardPiece03_length]
  rw [List.length_append, block49BackwardPiece04_length]
  rw [List.length_append, block49BackwardPiece05_length]
  rw [List.length_append, block49BackwardPiece06_length]
  rw [block49BackwardPiece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Backward_length

theorem block49Backward_scan : scanFrom 12544 block49Backward =
    [(12550, .phase "centers"), (12759, .phase "B"), (12768, .relabel (.inl 157)), (12770, .relabel (.inl 219))] := by
  rw [block49Backward]
  simp only [List.append_assoc]
  rw [scan_append, block49BackwardPiece00_scan, block49BackwardPiece00_length]
  rw [scan_append, block49BackwardPiece01_scan, block49BackwardPiece01_length]
  rw [scan_append, block49BackwardPiece02_scan, block49BackwardPiece02_length]
  rw [scan_append, block49BackwardPiece03_scan, block49BackwardPiece03_length]
  rw [scan_append, block49BackwardPiece04_scan, block49BackwardPiece04_length]
  rw [scan_append, block49BackwardPiece05_scan, block49BackwardPiece05_length]
  rw [scan_append, block49BackwardPiece06_scan, block49BackwardPiece06_length]
  rw [block49BackwardPiece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Backward_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
