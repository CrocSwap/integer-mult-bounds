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

def block41Piece00 : List Mark :=
  [.relabel (.inl 310)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 311)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 312)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 313)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 314)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 315)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 316)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 317)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 318)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 319)] ++
  List.replicate 13 Mark.passive

def block41Piece01 : List Mark :=
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 98), .relabel (.inl 85)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 304), .relabel (.inl 107)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 305), .relabel (.inl 24)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 48), .relabel (.inl 32)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 306), .relabel (.inl 45)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 307), .relabel (.inl 35)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 308), .relabel (.inl 312)] ++
  List.replicate 2 Mark.passive

def block41Piece02 : List Mark :=
  [.relabel (.inl 309), .relabel (.inl 318)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 310), .relabel (.inl 314)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 311), .relabel (.inl 316)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 313), .relabel (.inl 319)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 315), .relabel (.inl 317)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 311), .relabel (.inl 309)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 306), .relabel (.inl 304)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 310), .relabel (.inl 307)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 308), .relabel (.inl 305)] ++
  List.replicate 1 Mark.passive

def block41Piece03 : List Mark :=
  [.relabel (.inl 312), .relabel (.inl 314)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 24), .relabel (.inl 35)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 316), .relabel (.inl 45)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 318), .relabel (.inl 107)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 107), .relabel (.inl 45)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 304)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 305)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 35)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 307)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 309)] ++
  List.replicate 3 Mark.passive

def block41Piece04 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 314)] ++
  List.replicate 30 Mark.passive

def block41Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block41Piece06 : List Mark :=
  List.replicate 14 Mark.passive ++
  [.relabel (.inl 320)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 321)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 322)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 323)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 324)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 325)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 326)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 327)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 328)] ++
  List.replicate 1 Mark.passive

def block41Piece07 : List Mark :=
  [.relabel (.inl 329)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 330)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 331)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 332)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 333)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 334)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 335)] ++
  List.replicate 17 Mark.passive ++
  [.relabel (.inl 49), .relabel (.inl 33)]

def block41 : List Mark :=
  block41Piece00 ++ block41Piece01 ++ block41Piece02 ++ block41Piece03 ++ block41Piece04 ++ block41Piece05 ++ block41Piece06 ++ block41Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41

theorem block41Piece00_length : block41Piece00.length = 32 := by
  simp only [block41Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block41Piece00_scan : scanFrom 10496 block41Piece00 =
    [] := by
  simp only [block41Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41Piece00_scan

theorem block41Piece01_length : block41Piece01.length = 32 := by
  simp only [block41Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block41Piece01_scan : scanFrom 10528 block41Piece01 =
    [] := by
  simp only [block41Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41Piece01_scan

theorem block41Piece02_length : block41Piece02.length = 32 := by
  simp only [block41Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block41Piece02_scan : scanFrom 10560 block41Piece02 =
    [] := by
  simp only [block41Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41Piece02_scan

theorem block41Piece03_length : block41Piece03.length = 32 := by
  simp only [block41Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block41Piece03_scan : scanFrom 10592 block41Piece03 =
    [] := by
  simp only [block41Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41Piece03_scan

theorem block41Piece04_length : block41Piece04.length = 32 := by
  simp only [block41Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block41Piece04_scan : scanFrom 10624 block41Piece04 =
    [] := by
  simp only [block41Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41Piece04_scan

theorem block41Piece05_length : block41Piece05.length = 32 := by
  simp only [block41Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block41Piece05_scan : scanFrom 10656 block41Piece05 =
    [] := by
  simpa only [block41Piece05] using (scan_passive 10656 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41Piece05_scan

theorem block41Piece06_length : block41Piece06.length = 32 := by
  simp only [block41Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block41Piece06_scan : scanFrom 10688 block41Piece06 =
    [] := by
  simp only [block41Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41Piece06_scan

theorem block41Piece07_length : block41Piece07.length = 32 := by
  simp only [block41Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block41Piece07_scan : scanFrom 10720 block41Piece07 =
    [] := by
  simp only [block41Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41Piece07_scan

theorem block41_length : block41.length = 256 := by
  rw [block41]
  simp only [List.append_assoc]
  rw [List.length_append, block41Piece00_length]
  rw [List.length_append, block41Piece01_length]
  rw [List.length_append, block41Piece02_length]
  rw [List.length_append, block41Piece03_length]
  rw [List.length_append, block41Piece04_length]
  rw [List.length_append, block41Piece05_length]
  rw [List.length_append, block41Piece06_length]
  rw [block41Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41_length

theorem block41_scan : scanFrom 10496 block41 =
    [] := by
  rw [block41]
  simp only [List.append_assoc]
  rw [scan_append, block41Piece00_scan, block41Piece00_length]
  rw [scan_append, block41Piece01_scan, block41Piece01_length]
  rw [scan_append, block41Piece02_scan, block41Piece02_length]
  rw [scan_append, block41Piece03_scan, block41Piece03_length]
  rw [scan_append, block41Piece04_scan, block41Piece04_length]
  rw [scan_append, block41Piece05_scan, block41Piece05_length]
  rw [scan_append, block41Piece06_scan, block41Piece06_length]
  rw [block41Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block41_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
