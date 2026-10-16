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

def block42Piece00 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 320), .relabel (.inl 22)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 321), .relabel (.inl 109)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 34), .relabel (.inl 50)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 322), .relabel (.inl 108)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 323), .relabel (.inl 23)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 324), .relabel (.inl 328)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 325), .relabel (.inl 334)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 326), .relabel (.inl 330)]

def block42Piece01 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 327), .relabel (.inl 332)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 329), .relabel (.inl 335)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 331), .relabel (.inl 333)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 327), .relabel (.inl 325)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 322), .relabel (.inl 320)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 326), .relabel (.inl 323)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 324), .relabel (.inl 321)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 328), .relabel (.inl 330)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 109), .relabel (.inl 23)] ++
  List.replicate 1 Mark.passive

def block42Piece02 : List Mark :=
  [.relabel (.inl 332), .relabel (.inl 108)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 334), .relabel (.inl 22)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 22), .relabel (.inl 108)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 320)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 321)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 23)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 323)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 325)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 330)] ++
  List.replicate 4 Mark.passive

def block42Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block42Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block42Piece05 : List Mark :=
  List.replicate 8 Mark.passive ++
  [.relabel (.inl 336)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 337)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 338)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 339)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 340)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 341)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 342)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 343)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 344)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 345)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 346)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 347)] ++
  List.replicate 1 Mark.passive

def block42Piece06 : List Mark :=
  [.relabel (.inl 348)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 349)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 350)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 351)] ++
  List.replicate 17 Mark.passive ++
  [.relabel (.inl 6), .relabel (.inl 1)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 336), .relabel (.inl 58)] ++
  List.replicate 2 Mark.passive

def block42Piece07 : List Mark :=
  [.relabel (.inl 337), .relabel (.inl 28)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 82), .relabel (.inl 75)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 338), .relabel (.inl 93)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 339), .relabel (.inl 86)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 340), .relabel (.inl 344)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 341), .relabel (.inl 350)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 342), .relabel (.inl 346)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 343), .relabel (.inl 348)] ++
  List.replicate 2 Mark.passive

def block42 : List Mark :=
  block42Piece00 ++ block42Piece01 ++ block42Piece02 ++ block42Piece03 ++ block42Piece04 ++ block42Piece05 ++ block42Piece06 ++ block42Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42

theorem block42Piece00_length : block42Piece00.length = 32 := by
  simp only [block42Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block42Piece00_scan : scanFrom 10752 block42Piece00 =
    [] := by
  simp only [block42Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42Piece00_scan

theorem block42Piece01_length : block42Piece01.length = 32 := by
  simp only [block42Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block42Piece01_scan : scanFrom 10784 block42Piece01 =
    [] := by
  simp only [block42Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42Piece01_scan

theorem block42Piece02_length : block42Piece02.length = 32 := by
  simp only [block42Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block42Piece02_scan : scanFrom 10816 block42Piece02 =
    [] := by
  simp only [block42Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42Piece02_scan

theorem block42Piece03_length : block42Piece03.length = 32 := by
  simp only [block42Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block42Piece03_scan : scanFrom 10848 block42Piece03 =
    [] := by
  simpa only [block42Piece03] using (scan_passive 10848 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42Piece03_scan

theorem block42Piece04_length : block42Piece04.length = 32 := by
  simp only [block42Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block42Piece04_scan : scanFrom 10880 block42Piece04 =
    [] := by
  simpa only [block42Piece04] using (scan_passive 10880 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42Piece04_scan

theorem block42Piece05_length : block42Piece05.length = 32 := by
  simp only [block42Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block42Piece05_scan : scanFrom 10912 block42Piece05 =
    [] := by
  simp only [block42Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42Piece05_scan

theorem block42Piece06_length : block42Piece06.length = 32 := by
  simp only [block42Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block42Piece06_scan : scanFrom 10944 block42Piece06 =
    [] := by
  simp only [block42Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42Piece06_scan

theorem block42Piece07_length : block42Piece07.length = 32 := by
  simp only [block42Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block42Piece07_scan : scanFrom 10976 block42Piece07 =
    [] := by
  simp only [block42Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42Piece07_scan

theorem block42_length : block42.length = 256 := by
  rw [block42]
  simp only [List.append_assoc]
  rw [List.length_append, block42Piece00_length]
  rw [List.length_append, block42Piece01_length]
  rw [List.length_append, block42Piece02_length]
  rw [List.length_append, block42Piece03_length]
  rw [List.length_append, block42Piece04_length]
  rw [List.length_append, block42Piece05_length]
  rw [List.length_append, block42Piece06_length]
  rw [block42Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42_length

theorem block42_scan : scanFrom 10752 block42 =
    [] := by
  rw [block42]
  simp only [List.append_assoc]
  rw [scan_append, block42Piece00_scan, block42Piece00_length]
  rw [scan_append, block42Piece01_scan, block42Piece01_length]
  rw [scan_append, block42Piece02_scan, block42Piece02_length]
  rw [scan_append, block42Piece03_scan, block42Piece03_length]
  rw [scan_append, block42Piece04_scan, block42Piece04_length]
  rw [scan_append, block42Piece05_scan, block42Piece05_length]
  rw [scan_append, block42Piece06_scan, block42Piece06_length]
  rw [block42Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block42_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
