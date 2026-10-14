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

def block49Piece00 : List Mark :=
  [.relabel (.inl 384)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 416)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 432)] ++
  List.replicate 1 Mark.passive ++
  [.phase "centers", .clear (.inr 0), .copy (.inr 0), .relabel (.inr 0)] ++
  List.replicate 22 Mark.passive

def block49Piece01 : List Mark :=
  [.clear (.inr 0), .clear (.inr 1), .copy (.inr 1), .relabel (.inr 1)] ++
  List.replicate 22 Mark.passive ++
  [.clear (.inr 1), .clear (.inr 2), .copy (.inr 2), .relabel (.inr 2)] ++
  List.replicate 2 Mark.passive

def block49Piece02 : List Mark :=
  List.replicate 20 Mark.passive ++
  [.clear (.inr 2), .clear (.inr 3), .copy (.inr 3), .relabel (.inr 3)] ++
  List.replicate 8 Mark.passive

def block49Piece03 : List Mark :=
  List.replicate 14 Mark.passive ++
  [.clear (.inr 3), .clear (.inr 4), .copy (.inr 4), .relabel (.inr 4)] ++
  List.replicate 14 Mark.passive

def block49Piece04 : List Mark :=
  List.replicate 8 Mark.passive ++
  [.clear (.inr 4), .clear (.inr 5), .copy (.inr 5), .relabel (.inr 5)] ++
  List.replicate 20 Mark.passive

def block49Piece05 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.clear (.inr 5), .clear (.inr 6), .copy (.inr 6), .relabel (.inr 6)] ++
  List.replicate 22 Mark.passive ++
  [.clear (.inr 6), .clear (.inr 7), .copy (.inr 7), .relabel (.inr 7)]

def block49Piece06 : List Mark :=
  List.replicate 22 Mark.passive ++
  [.clear (.inr 7), .phase "B", .relabel (.inl 215)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 129)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 124)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 212)] ++
  List.replicate 1 Mark.passive

def block49Piece07 : List Mark :=
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

def block49 : List Mark :=
  block49Piece00 ++ block49Piece01 ++ block49Piece02 ++ block49Piece03 ++ block49Piece04 ++ block49Piece05 ++ block49Piece06 ++ block49Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49

theorem block49Piece00_length : block49Piece00.length = 32 := by
  simp only [block49Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49Piece00_scan : scanFrom 12544 block49Piece00 =
    [(12550, .phase "centers")] := by
  simp only [block49Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Piece00_scan

theorem block49Piece01_length : block49Piece01.length = 32 := by
  simp only [block49Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49Piece01_scan : scanFrom 12576 block49Piece01 =
    [] := by
  simp only [block49Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Piece01_scan

theorem block49Piece02_length : block49Piece02.length = 32 := by
  simp only [block49Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49Piece02_scan : scanFrom 12608 block49Piece02 =
    [] := by
  simp only [block49Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Piece02_scan

theorem block49Piece03_length : block49Piece03.length = 32 := by
  simp only [block49Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49Piece03_scan : scanFrom 12640 block49Piece03 =
    [] := by
  simp only [block49Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Piece03_scan

theorem block49Piece04_length : block49Piece04.length = 32 := by
  simp only [block49Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49Piece04_scan : scanFrom 12672 block49Piece04 =
    [] := by
  simp only [block49Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Piece04_scan

theorem block49Piece05_length : block49Piece05.length = 32 := by
  simp only [block49Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49Piece05_scan : scanFrom 12704 block49Piece05 =
    [] := by
  simp only [block49Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Piece05_scan

theorem block49Piece06_length : block49Piece06.length = 32 := by
  simp only [block49Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49Piece06_scan : scanFrom 12736 block49Piece06 =
    [(12759, .phase "B")] := by
  simp only [block49Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Piece06_scan

theorem block49Piece07_length : block49Piece07.length = 32 := by
  simp only [block49Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block49Piece07_scan : scanFrom 12768 block49Piece07 =
    [(12768, .relabel (.inl 157)), (12770, .relabel (.inl 219))] := by
  simp only [block49Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49Piece07_scan

theorem block49_length : block49.length = 256 := by
  rw [block49]
  simp only [List.append_assoc]
  rw [List.length_append, block49Piece00_length]
  rw [List.length_append, block49Piece01_length]
  rw [List.length_append, block49Piece02_length]
  rw [List.length_append, block49Piece03_length]
  rw [List.length_append, block49Piece04_length]
  rw [List.length_append, block49Piece05_length]
  rw [List.length_append, block49Piece06_length]
  rw [block49Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49_length

theorem block49_scan : scanFrom 12544 block49 =
    [(12550, .phase "centers"), (12759, .phase "B"), (12768, .relabel (.inl 157)), (12770, .relabel (.inl 219))] := by
  rw [block49]
  simp only [List.append_assoc]
  rw [scan_append, block49Piece00_scan, block49Piece00_length]
  rw [scan_append, block49Piece01_scan, block49Piece01_length]
  rw [scan_append, block49Piece02_scan, block49Piece02_length]
  rw [scan_append, block49Piece03_scan, block49Piece03_length]
  rw [scan_append, block49Piece04_scan, block49Piece04_length]
  rw [scan_append, block49Piece05_scan, block49Piece05_length]
  rw [scan_append, block49Piece06_scan, block49Piece06_length]
  rw [block49Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block49_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
