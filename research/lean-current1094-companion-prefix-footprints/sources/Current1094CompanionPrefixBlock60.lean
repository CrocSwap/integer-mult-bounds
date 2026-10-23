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

def block60Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block60Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block60Piece02 : List Mark :=
  List.replicate 30 Mark.passive ++
  [.relabel (.inl 283), .relabel (.inl 379)]

def block60Piece03 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 139), .relabel (.inl 283)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 119), .relabel (.inl 379)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 100), .relabel (.inl 67)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 112), .relabel (.inl 100)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 169), .relabel (.inl 67)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 315), .relabel (.inl 347)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 315)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 347)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 48), .relabel (.inl 82)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 48)] ++
  List.replicate 1 Mark.passive

def block60Piece04 : List Mark :=
  [.relabel (.inl 82)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 592), .relabel (.inl 599)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 199), .relabel (.inl 592)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 193), .relabel (.inl 599)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 593), .relabel (.inl 598)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 188), .relabel (.inl 593)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 204), .relabel (.inl 598)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 594), .relabel (.inl 597)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 594)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 597)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 595), .relabel (.inl 596)]

def block60Piece05 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 595)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 596)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 279), .relabel (.inl 359)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 203), .relabel (.inl 279)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 122), .relabel (.inl 359)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 274), .relabel (.inl 354)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 182), .relabel (.inl 274)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 174), .relabel (.inl 354)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 295), .relabel (.inl 343)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 295)] ++
  List.replicate 1 Mark.passive

def block60Piece06 : List Mark :=
  [.relabel (.inl 343)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 290), .relabel (.inl 338)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 290)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 338)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 600), .relabel (.inl 607)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 202), .relabel (.inl 600)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 123), .relabel (.inl 607)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 601), .relabel (.inl 606)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 183), .relabel (.inl 601)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 175), .relabel (.inl 606)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 602), .relabel (.inl 605)]

def block60Piece07 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 602)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 605)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 603), .relabel (.inl 604)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 603)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 604)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 278), .relabel (.inl 342)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 201), .relabel (.inl 278)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 191), .relabel (.inl 342)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 276), .relabel (.inl 340)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 184), .relabel (.inl 276)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 206)]

def block60 : List Mark :=
  block60Piece00 ++ block60Piece01 ++ block60Piece02 ++ block60Piece03 ++ block60Piece04 ++ block60Piece05 ++ block60Piece06 ++ block60Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60

theorem block60Piece00_length : block60Piece00.length = 32 := by
  simp only [block60Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block60Piece00_scan : scanFrom 15360 block60Piece00 =
    [] := by
  simpa only [block60Piece00] using (scan_passive 15360 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60Piece00_scan

theorem block60Piece01_length : block60Piece01.length = 32 := by
  simp only [block60Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block60Piece01_scan : scanFrom 15392 block60Piece01 =
    [] := by
  simpa only [block60Piece01] using (scan_passive 15392 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60Piece01_scan

theorem block60Piece02_length : block60Piece02.length = 32 := by
  simp only [block60Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block60Piece02_scan : scanFrom 15424 block60Piece02 =
    [] := by
  simp only [block60Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60Piece02_scan

theorem block60Piece03_length : block60Piece03.length = 32 := by
  simp only [block60Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block60Piece03_scan : scanFrom 15456 block60Piece03 =
    [] := by
  simp only [block60Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60Piece03_scan

theorem block60Piece04_length : block60Piece04.length = 32 := by
  simp only [block60Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block60Piece04_scan : scanFrom 15488 block60Piece04 =
    [] := by
  simp only [block60Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60Piece04_scan

theorem block60Piece05_length : block60Piece05.length = 32 := by
  simp only [block60Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block60Piece05_scan : scanFrom 15520 block60Piece05 =
    [] := by
  simp only [block60Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60Piece05_scan

theorem block60Piece06_length : block60Piece06.length = 32 := by
  simp only [block60Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block60Piece06_scan : scanFrom 15552 block60Piece06 =
    [] := by
  simp only [block60Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60Piece06_scan

theorem block60Piece07_length : block60Piece07.length = 32 := by
  simp only [block60Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block60Piece07_scan : scanFrom 15584 block60Piece07 =
    [] := by
  simp only [block60Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60Piece07_scan

theorem block60_length : block60.length = 256 := by
  rw [block60]
  simp only [List.append_assoc]
  rw [List.length_append, block60Piece00_length]
  rw [List.length_append, block60Piece01_length]
  rw [List.length_append, block60Piece02_length]
  rw [List.length_append, block60Piece03_length]
  rw [List.length_append, block60Piece04_length]
  rw [List.length_append, block60Piece05_length]
  rw [List.length_append, block60Piece06_length]
  rw [block60Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60_length

theorem block60_scan : scanFrom 15360 block60 =
    [] := by
  rw [block60]
  simp only [List.append_assoc]
  rw [scan_append, block60Piece00_scan, block60Piece00_length]
  rw [scan_append, block60Piece01_scan, block60Piece01_length]
  rw [scan_append, block60Piece02_scan, block60Piece02_length]
  rw [scan_append, block60Piece03_scan, block60Piece03_length]
  rw [scan_append, block60Piece04_scan, block60Piece04_length]
  rw [scan_append, block60Piece05_scan, block60Piece05_length]
  rw [scan_append, block60Piece06_scan, block60Piece06_length]
  rw [block60Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block60_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
