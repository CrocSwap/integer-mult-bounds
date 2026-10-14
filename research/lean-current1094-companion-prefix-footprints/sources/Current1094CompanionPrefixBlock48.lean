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

def block48Piece00 : List Mark :=
  [.relabel (.inl 21), .relabel (.inl 47)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 434), .relabel (.inl 37)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 435), .relabel (.inl 110)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 436), .relabel (.inl 440)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 437), .relabel (.inl 446)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 438), .relabel (.inl 442)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 439), .relabel (.inl 444)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 441), .relabel (.inl 447)] ++
  List.replicate 2 Mark.passive

def block48Piece01 : List Mark :=
  [.relabel (.inl 443), .relabel (.inl 445)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 439), .relabel (.inl 437)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 434), .relabel (.inl 432)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 438), .relabel (.inl 435)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 436), .relabel (.inl 433)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 440), .relabel (.inl 442)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 46), .relabel (.inl 110)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 444), .relabel (.inl 37)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 446), .relabel (.inl 20)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 20), .relabel (.inl 37)] ++
  List.replicate 2 Mark.passive

def block48Piece02 : List Mark :=
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 432)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 433)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 110)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 435)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 437)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 442)] ++
  List.replicate 14 Mark.passive

def block48Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block48Piece04 : List Mark :=
  List.replicate 30 Mark.passive ++
  [.relabel (.inl 92), .relabel (.inl 63)]

def block48Piece05 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 61)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 103)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 18)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 45)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 108)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 57), .relabel (.inl 62)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 94)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 93)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 59)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 8)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 96)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 81), .relabel (.inl 17)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 40)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 58)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 30)]

def block48Piece06 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 41)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 43)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 224), .relabel (.inl 107)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 22)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 95)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 64)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 42)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 16)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 11), .relabel (.inl 77)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 35)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 86)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 26)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 106)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 37)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 240)]

def block48Piece07 : List Mark :=
  [.relabel (.inl 39)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 23)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 29)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 65)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 400)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 20)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 9), .relabel (.inl 272)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 320)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 352)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 368)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 104)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 110)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 256), .relabel (.inl 288)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 304)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 336)] ++
  List.replicate 1 Mark.passive

def block48 : List Mark :=
  block48Piece00 ++ block48Piece01 ++ block48Piece02 ++ block48Piece03 ++ block48Piece04 ++ block48Piece05 ++ block48Piece06 ++ block48Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48

theorem block48Piece00_length : block48Piece00.length = 32 := by
  simp only [block48Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block48Piece00_scan : scanFrom 12288 block48Piece00 =
    [] := by
  simp only [block48Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48Piece00_scan

theorem block48Piece01_length : block48Piece01.length = 32 := by
  simp only [block48Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block48Piece01_scan : scanFrom 12320 block48Piece01 =
    [] := by
  simp only [block48Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48Piece01_scan

theorem block48Piece02_length : block48Piece02.length = 32 := by
  simp only [block48Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block48Piece02_scan : scanFrom 12352 block48Piece02 =
    [] := by
  simp only [block48Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48Piece02_scan

theorem block48Piece03_length : block48Piece03.length = 32 := by
  simp only [block48Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block48Piece03_scan : scanFrom 12384 block48Piece03 =
    [] := by
  simpa only [block48Piece03] using (scan_passive 12384 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48Piece03_scan

theorem block48Piece04_length : block48Piece04.length = 32 := by
  simp only [block48Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block48Piece04_scan : scanFrom 12416 block48Piece04 =
    [] := by
  simp only [block48Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48Piece04_scan

theorem block48Piece05_length : block48Piece05.length = 32 := by
  simp only [block48Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block48Piece05_scan : scanFrom 12448 block48Piece05 =
    [] := by
  simp only [block48Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48Piece05_scan

theorem block48Piece06_length : block48Piece06.length = 32 := by
  simp only [block48Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block48Piece06_scan : scanFrom 12480 block48Piece06 =
    [] := by
  simp only [block48Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48Piece06_scan

theorem block48Piece07_length : block48Piece07.length = 32 := by
  simp only [block48Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block48Piece07_scan : scanFrom 12512 block48Piece07 =
    [] := by
  simp only [block48Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48Piece07_scan

theorem block48_length : block48.length = 256 := by
  rw [block48]
  simp only [List.append_assoc]
  rw [List.length_append, block48Piece00_length]
  rw [List.length_append, block48Piece01_length]
  rw [List.length_append, block48Piece02_length]
  rw [List.length_append, block48Piece03_length]
  rw [List.length_append, block48Piece04_length]
  rw [List.length_append, block48Piece05_length]
  rw [List.length_append, block48Piece06_length]
  rw [block48Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48_length

theorem block48_scan : scanFrom 12288 block48 =
    [] := by
  rw [block48]
  simp only [List.append_assoc]
  rw [scan_append, block48Piece00_scan, block48Piece00_length]
  rw [scan_append, block48Piece01_scan, block48Piece01_length]
  rw [scan_append, block48Piece02_scan, block48Piece02_length]
  rw [scan_append, block48Piece03_scan, block48Piece03_length]
  rw [scan_append, block48Piece04_scan, block48Piece04_length]
  rw [scan_append, block48Piece05_scan, block48Piece05_length]
  rw [scan_append, block48Piece06_scan, block48Piece06_length]
  rw [block48Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block48_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
