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

def block47Piece00 : List Mark :=
  [.relabel (.inl 427)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 428)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 429)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 430)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 431)] ++
  List.replicate 17 Mark.passive ++
  [.relabel (.inl 13), .relabel (.inl 51)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 416), .relabel (.inl 16)]

def block47Piece01 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 417), .relabel (.inl 44)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 78), .relabel (.inl 99)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 418), .relabel (.inl 43)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 419), .relabel (.inl 104)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 420), .relabel (.inl 424)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 421), .relabel (.inl 430)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 422), .relabel (.inl 426)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 423), .relabel (.inl 428)]

def block47Piece02 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 425), .relabel (.inl 431)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 427), .relabel (.inl 429)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 423), .relabel (.inl 421)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 418), .relabel (.inl 416)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 422), .relabel (.inl 419)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 420), .relabel (.inl 417)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 424), .relabel (.inl 426)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 44), .relabel (.inl 104)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 428), .relabel (.inl 43)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 430)]

def block47Piece03 : List Mark :=
  [.relabel (.inl 16)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 16), .relabel (.inl 43)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 416)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 417)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 104)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 419)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 421)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 426)] ++
  List.replicate 8 Mark.passive

def block47Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block47Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block47Piece06 : List Mark :=
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 432)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 433)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 434)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 435)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 436)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 437)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 438)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 439)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 440)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 441)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 442)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 443)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 444)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 445)] ++
  List.replicate 1 Mark.passive

def block47Piece07 : List Mark :=
  [.relabel (.inl 446)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 447)] ++
  List.replicate 17 Mark.passive ++
  [.relabel (.inl 36), .relabel (.inl 111)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 432), .relabel (.inl 20)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 433), .relabel (.inl 46)] ++
  List.replicate 2 Mark.passive

def block47 : List Mark :=
  block47Piece00 ++ block47Piece01 ++ block47Piece02 ++ block47Piece03 ++ block47Piece04 ++ block47Piece05 ++ block47Piece06 ++ block47Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47

theorem block47Piece00_length : block47Piece00.length = 32 := by
  simp only [block47Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block47Piece00_scan : scanFrom 12032 block47Piece00 =
    [] := by
  simp only [block47Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47Piece00_scan

theorem block47Piece01_length : block47Piece01.length = 32 := by
  simp only [block47Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block47Piece01_scan : scanFrom 12064 block47Piece01 =
    [] := by
  simp only [block47Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47Piece01_scan

theorem block47Piece02_length : block47Piece02.length = 32 := by
  simp only [block47Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block47Piece02_scan : scanFrom 12096 block47Piece02 =
    [] := by
  simp only [block47Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47Piece02_scan

theorem block47Piece03_length : block47Piece03.length = 32 := by
  simp only [block47Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block47Piece03_scan : scanFrom 12128 block47Piece03 =
    [] := by
  simp only [block47Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47Piece03_scan

theorem block47Piece04_length : block47Piece04.length = 32 := by
  simp only [block47Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block47Piece04_scan : scanFrom 12160 block47Piece04 =
    [] := by
  simpa only [block47Piece04] using (scan_passive 12160 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47Piece04_scan

theorem block47Piece05_length : block47Piece05.length = 32 := by
  simp only [block47Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block47Piece05_scan : scanFrom 12192 block47Piece05 =
    [] := by
  simpa only [block47Piece05] using (scan_passive 12192 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47Piece05_scan

theorem block47Piece06_length : block47Piece06.length = 32 := by
  simp only [block47Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block47Piece06_scan : scanFrom 12224 block47Piece06 =
    [] := by
  simp only [block47Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47Piece06_scan

theorem block47Piece07_length : block47Piece07.length = 32 := by
  simp only [block47Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block47Piece07_scan : scanFrom 12256 block47Piece07 =
    [] := by
  simp only [block47Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47Piece07_scan

theorem block47_length : block47.length = 256 := by
  rw [block47]
  simp only [List.append_assoc]
  rw [List.length_append, block47Piece00_length]
  rw [List.length_append, block47Piece01_length]
  rw [List.length_append, block47Piece02_length]
  rw [List.length_append, block47Piece03_length]
  rw [List.length_append, block47Piece04_length]
  rw [List.length_append, block47Piece05_length]
  rw [List.length_append, block47Piece06_length]
  rw [block47Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47_length

theorem block47_scan : scanFrom 12032 block47 =
    [] := by
  rw [block47]
  simp only [List.append_assoc]
  rw [scan_append, block47Piece00_scan, block47Piece00_length]
  rw [scan_append, block47Piece01_scan, block47Piece01_length]
  rw [scan_append, block47Piece02_scan, block47Piece02_length]
  rw [scan_append, block47Piece03_scan, block47Piece03_length]
  rw [scan_append, block47Piece04_scan, block47Piece04_length]
  rw [scan_append, block47Piece05_scan, block47Piece05_length]
  rw [scan_append, block47Piece06_scan, block47Piece06_length]
  rw [block47Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block47_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
