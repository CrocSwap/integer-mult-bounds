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

def block40Piece00 : List Mark :=
  List.replicate 26 Mark.passive ++
  [.relabel (.inl 288)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 289)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 290)] ++
  List.replicate 1 Mark.passive

def block40Piece01 : List Mark :=
  [.relabel (.inl 291)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 292)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 293)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 294)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 295)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 296)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 297)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 298)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 299)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 300)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 301)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 302)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 303)] ++
  List.replicate 7 Mark.passive

def block40Piece02 : List Mark :=
  List.replicate 10 Mark.passive ++
  [.relabel (.inl 101), .relabel (.inl 55)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 288), .relabel (.inl 40)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 289), .relabel (.inl 19)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 54), .relabel (.inl 102)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 290), .relabel (.inl 18)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 291), .relabel (.inl 39)]

def block40Piece03 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 292), .relabel (.inl 296)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 293), .relabel (.inl 302)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 294), .relabel (.inl 298)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 295), .relabel (.inl 300)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 297), .relabel (.inl 303)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 299), .relabel (.inl 301)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 295), .relabel (.inl 293)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 290), .relabel (.inl 288)] ++
  List.replicate 1 Mark.passive

def block40Piece04 : List Mark :=
  [.relabel (.inl 294), .relabel (.inl 291)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 292), .relabel (.inl 289)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 296), .relabel (.inl 298)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 19), .relabel (.inl 39)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 300), .relabel (.inl 18)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 302), .relabel (.inl 40)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 40), .relabel (.inl 18)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 288)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 289)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 39)] ++
  List.replicate 1 Mark.passive

def block40Piece05 : List Mark :=
  [.relabel (.inl 291)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 293)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 298)] ++
  List.replicate 24 Mark.passive

def block40Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block40Piece07 : List Mark :=
  List.replicate 20 Mark.passive ++
  [.relabel (.inl 304)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 305)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 306)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 307)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 308)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 309)] ++
  List.replicate 1 Mark.passive

def block40 : List Mark :=
  block40Piece00 ++ block40Piece01 ++ block40Piece02 ++ block40Piece03 ++ block40Piece04 ++ block40Piece05 ++ block40Piece06 ++ block40Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40

theorem block40Piece00_length : block40Piece00.length = 32 := by
  simp only [block40Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block40Piece00_scan : scanFrom 10240 block40Piece00 =
    [] := by
  simp only [block40Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40Piece00_scan

theorem block40Piece01_length : block40Piece01.length = 32 := by
  simp only [block40Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block40Piece01_scan : scanFrom 10272 block40Piece01 =
    [] := by
  simp only [block40Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40Piece01_scan

theorem block40Piece02_length : block40Piece02.length = 32 := by
  simp only [block40Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block40Piece02_scan : scanFrom 10304 block40Piece02 =
    [] := by
  simp only [block40Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40Piece02_scan

theorem block40Piece03_length : block40Piece03.length = 32 := by
  simp only [block40Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block40Piece03_scan : scanFrom 10336 block40Piece03 =
    [] := by
  simp only [block40Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40Piece03_scan

theorem block40Piece04_length : block40Piece04.length = 32 := by
  simp only [block40Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block40Piece04_scan : scanFrom 10368 block40Piece04 =
    [] := by
  simp only [block40Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40Piece04_scan

theorem block40Piece05_length : block40Piece05.length = 32 := by
  simp only [block40Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block40Piece05_scan : scanFrom 10400 block40Piece05 =
    [] := by
  simp only [block40Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40Piece05_scan

theorem block40Piece06_length : block40Piece06.length = 32 := by
  simp only [block40Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block40Piece06_scan : scanFrom 10432 block40Piece06 =
    [] := by
  simpa only [block40Piece06] using (scan_passive 10432 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40Piece06_scan

theorem block40Piece07_length : block40Piece07.length = 32 := by
  simp only [block40Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block40Piece07_scan : scanFrom 10464 block40Piece07 =
    [] := by
  simp only [block40Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40Piece07_scan

theorem block40_length : block40.length = 256 := by
  rw [block40]
  simp only [List.append_assoc]
  rw [List.length_append, block40Piece00_length]
  rw [List.length_append, block40Piece01_length]
  rw [List.length_append, block40Piece02_length]
  rw [List.length_append, block40Piece03_length]
  rw [List.length_append, block40Piece04_length]
  rw [List.length_append, block40Piece05_length]
  rw [List.length_append, block40Piece06_length]
  rw [block40Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40_length

theorem block40_scan : scanFrom 10240 block40 =
    [] := by
  rw [block40]
  simp only [List.append_assoc]
  rw [scan_append, block40Piece00_scan, block40Piece00_length]
  rw [scan_append, block40Piece01_scan, block40Piece01_length]
  rw [scan_append, block40Piece02_scan, block40Piece02_length]
  rw [scan_append, block40Piece03_scan, block40Piece03_length]
  rw [scan_append, block40Piece04_scan, block40Piece04_length]
  rw [scan_append, block40Piece05_scan, block40Piece05_length]
  rw [scan_append, block40Piece06_scan, block40Piece06_length]
  rw [block40Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block40_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
