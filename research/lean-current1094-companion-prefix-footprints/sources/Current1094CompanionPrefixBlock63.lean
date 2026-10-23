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

def block63Piece00 : List Mark :=
  [.relabel (.inl 312)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 469), .relabel (.inl 24)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 469)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 24)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 664), .relabel (.inl 671)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 115), .relabel (.inl 664)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 138), .relabel (.inl 671)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 665), .relabel (.inl 670)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 179), .relabel (.inl 665)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 120), .relabel (.inl 670)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 666), .relabel (.inl 669)]

def block63Piece01 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 666)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 669)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 667), .relabel (.inl 668)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 667)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 668)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 462), .relabel (.inl 316)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 116), .relabel (.inl 462)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 209), .relabel (.inl 316)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 463), .relabel (.inl 318)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 180), .relabel (.inl 463)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 176)]

def block63Piece02 : List Mark :=
  [.relabel (.inl 318)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 470), .relabel (.inl 328)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 470)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 328)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 471), .relabel (.inl 109)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 471)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 109)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 672), .relabel (.inl 679)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 181), .relabel (.inl 672)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 177), .relabel (.inl 679)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 673), .relabel (.inl 678)] ++
  List.replicate 2 Mark.passive

def block63Piece03 : List Mark :=
  [.relabel (.inl 117), .relabel (.inl 673)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 208), .relabel (.inl 678)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 674), .relabel (.inl 677)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 674)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 677)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 675), .relabel (.inl 676)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 675)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 676)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 478), .relabel (.inl 514)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 165), .relabel (.inl 478)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 217), .relabel (.inl 514)] ++
  List.replicate 1 Mark.passive

def block63Piece04 : List Mark :=
  [.relabel (.inl 479), .relabel (.inl 515)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 127), .relabel (.inl 479)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 154), .relabel (.inl 515)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 490), .relabel (.inl 502)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 490)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 502)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 491), .relabel (.inl 503)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 491)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 503)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 680), .relabel (.inl 687)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 164), .relabel (.inl 680)]

def block63Piece05 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 218), .relabel (.inl 687)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 681), .relabel (.inl 686)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 126), .relabel (.inl 681)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 153), .relabel (.inl 686)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 682), .relabel (.inl 685)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 682)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 685)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 683), .relabel (.inl 684)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 683)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 684)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 480), .relabel (.inl 504)]

def block63Piece06 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 163), .relabel (.inl 480)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 156), .relabel (.inl 504)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 481), .relabel (.inl 505)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 125), .relabel (.inl 481)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 128), .relabel (.inl 505)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 492), .relabel (.inl 516)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 492)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 516)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 493), .relabel (.inl 517)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 493)] ++
  List.replicate 1 Mark.passive

def block63Piece07 : List Mark :=
  [.relabel (.inl 517)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 688), .relabel (.inl 695)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 211), .relabel (.inl 688)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 216), .relabel (.inl 695)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 689), .relabel (.inl 694)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 190), .relabel (.inl 689)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 155), .relabel (.inl 694)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 690), .relabel (.inl 693)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 690)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 693)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 691), .relabel (.inl 692)]

def block63 : List Mark :=
  block63Piece00 ++ block63Piece01 ++ block63Piece02 ++ block63Piece03 ++ block63Piece04 ++ block63Piece05 ++ block63Piece06 ++ block63Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63

theorem block63Piece00_length : block63Piece00.length = 32 := by
  simp only [block63Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block63Piece00_scan : scanFrom 16128 block63Piece00 =
    [] := by
  simp only [block63Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63Piece00_scan

theorem block63Piece01_length : block63Piece01.length = 32 := by
  simp only [block63Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block63Piece01_scan : scanFrom 16160 block63Piece01 =
    [] := by
  simp only [block63Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63Piece01_scan

theorem block63Piece02_length : block63Piece02.length = 32 := by
  simp only [block63Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block63Piece02_scan : scanFrom 16192 block63Piece02 =
    [] := by
  simp only [block63Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63Piece02_scan

theorem block63Piece03_length : block63Piece03.length = 32 := by
  simp only [block63Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block63Piece03_scan : scanFrom 16224 block63Piece03 =
    [] := by
  simp only [block63Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63Piece03_scan

theorem block63Piece04_length : block63Piece04.length = 32 := by
  simp only [block63Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block63Piece04_scan : scanFrom 16256 block63Piece04 =
    [] := by
  simp only [block63Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63Piece04_scan

theorem block63Piece05_length : block63Piece05.length = 32 := by
  simp only [block63Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block63Piece05_scan : scanFrom 16288 block63Piece05 =
    [] := by
  simp only [block63Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63Piece05_scan

theorem block63Piece06_length : block63Piece06.length = 32 := by
  simp only [block63Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block63Piece06_scan : scanFrom 16320 block63Piece06 =
    [] := by
  simp only [block63Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63Piece06_scan

theorem block63Piece07_length : block63Piece07.length = 32 := by
  simp only [block63Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block63Piece07_scan : scanFrom 16352 block63Piece07 =
    [] := by
  simp only [block63Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63Piece07_scan

theorem block63_length : block63.length = 256 := by
  rw [block63]
  simp only [List.append_assoc]
  rw [List.length_append, block63Piece00_length]
  rw [List.length_append, block63Piece01_length]
  rw [List.length_append, block63Piece02_length]
  rw [List.length_append, block63Piece03_length]
  rw [List.length_append, block63Piece04_length]
  rw [List.length_append, block63Piece05_length]
  rw [List.length_append, block63Piece06_length]
  rw [block63Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63_length

theorem block63_scan : scanFrom 16128 block63 =
    [] := by
  rw [block63]
  simp only [List.append_assoc]
  rw [scan_append, block63Piece00_scan, block63Piece00_length]
  rw [scan_append, block63Piece01_scan, block63Piece01_length]
  rw [scan_append, block63Piece02_scan, block63Piece02_length]
  rw [scan_append, block63Piece03_scan, block63Piece03_length]
  rw [scan_append, block63Piece04_scan, block63Piece04_length]
  rw [scan_append, block63Piece05_scan, block63Piece05_length]
  rw [scan_append, block63Piece06_scan, block63Piece06_length]
  rw [block63Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block63_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
