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

def block62Piece00 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 634)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 637)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 635), .relabel (.inl 636)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 635)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 636)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 458), .relabel (.inl 380)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 145), .relabel (.inl 458)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 221), .relabel (.inl 380)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 459), .relabel (.inl 382)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 161), .relabel (.inl 459)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 134)]

def block62Piece01 : List Mark :=
  [.relabel (.inl 382)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 464), .relabel (.inl 392)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 464)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 392)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 465), .relabel (.inl 97)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 465)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 97)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 640), .relabel (.inl 647)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 162), .relabel (.inl 640)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 135), .relabel (.inl 647)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 641), .relabel (.inl 646)] ++
  List.replicate 2 Mark.passive

def block62Piece02 : List Mark :=
  [.relabel (.inl 146), .relabel (.inl 641)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 220), .relabel (.inl 646)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 642), .relabel (.inl 645)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 642)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 645)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 643), .relabel (.inl 644)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 643)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 644)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 248), .relabel (.inl 300)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 113), .relabel (.inl 248)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 140), .relabel (.inl 300)] ++
  List.replicate 1 Mark.passive

def block62Piece03 : List Mark :=
  [.relabel (.inl 10), .relabel (.inl 302)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 118), .relabel (.inl 10)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 170), .relabel (.inl 302)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 268), .relabel (.inl 280)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 268)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 280)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 270), .relabel (.inl 38)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 270)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 38)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 648), .relabel (.inl 655)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 187), .relabel (.inl 648)]

def block62Piece04 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 198), .relabel (.inl 655)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 649), .relabel (.inl 654)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 194), .relabel (.inl 649)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 205), .relabel (.inl 654)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 650), .relabel (.inl 653)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 650)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 653)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 651), .relabel (.inl 652)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 651)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 652)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 252), .relabel (.inl 284)]

def block62Piece05 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 186), .relabel (.inl 252)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 172), .relabel (.inl 284)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 254), .relabel (.inl 286)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 195), .relabel (.inl 254)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 142), .relabel (.inl 286)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 264), .relabel (.inl 296)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 264)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 296)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 79), .relabel (.inl 19)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 79)] ++
  List.replicate 1 Mark.passive

def block62Piece06 : List Mark :=
  [.relabel (.inl 19)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 656), .relabel (.inl 663)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 196), .relabel (.inl 656)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 141), .relabel (.inl 663)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 657), .relabel (.inl 662)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 185), .relabel (.inl 657)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 171), .relabel (.inl 662)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 658), .relabel (.inl 661)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 658)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 661)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 659), .relabel (.inl 660)]

def block62Piece07 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 659)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 660)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 460), .relabel (.inl 332)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 200), .relabel (.inl 460)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 178), .relabel (.inl 332)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 461), .relabel (.inl 334)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 192), .relabel (.inl 461)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 207), .relabel (.inl 334)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 468), .relabel (.inl 312)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 468)] ++
  List.replicate 1 Mark.passive

def block62 : List Mark :=
  block62Piece00 ++ block62Piece01 ++ block62Piece02 ++ block62Piece03 ++ block62Piece04 ++ block62Piece05 ++ block62Piece06 ++ block62Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62

theorem block62Piece00_length : block62Piece00.length = 32 := by
  simp only [block62Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block62Piece00_scan : scanFrom 15872 block62Piece00 =
    [] := by
  simp only [block62Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62Piece00_scan

theorem block62Piece01_length : block62Piece01.length = 32 := by
  simp only [block62Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block62Piece01_scan : scanFrom 15904 block62Piece01 =
    [] := by
  simp only [block62Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62Piece01_scan

theorem block62Piece02_length : block62Piece02.length = 32 := by
  simp only [block62Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block62Piece02_scan : scanFrom 15936 block62Piece02 =
    [] := by
  simp only [block62Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62Piece02_scan

theorem block62Piece03_length : block62Piece03.length = 32 := by
  simp only [block62Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block62Piece03_scan : scanFrom 15968 block62Piece03 =
    [] := by
  simp only [block62Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62Piece03_scan

theorem block62Piece04_length : block62Piece04.length = 32 := by
  simp only [block62Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block62Piece04_scan : scanFrom 16000 block62Piece04 =
    [] := by
  simp only [block62Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62Piece04_scan

theorem block62Piece05_length : block62Piece05.length = 32 := by
  simp only [block62Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block62Piece05_scan : scanFrom 16032 block62Piece05 =
    [] := by
  simp only [block62Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62Piece05_scan

theorem block62Piece06_length : block62Piece06.length = 32 := by
  simp only [block62Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block62Piece06_scan : scanFrom 16064 block62Piece06 =
    [] := by
  simp only [block62Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62Piece06_scan

theorem block62Piece07_length : block62Piece07.length = 32 := by
  simp only [block62Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block62Piece07_scan : scanFrom 16096 block62Piece07 =
    [] := by
  simp only [block62Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62Piece07_scan

theorem block62_length : block62.length = 256 := by
  rw [block62]
  simp only [List.append_assoc]
  rw [List.length_append, block62Piece00_length]
  rw [List.length_append, block62Piece01_length]
  rw [List.length_append, block62Piece02_length]
  rw [List.length_append, block62Piece03_length]
  rw [List.length_append, block62Piece04_length]
  rw [List.length_append, block62Piece05_length]
  rw [List.length_append, block62Piece06_length]
  rw [block62Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62_length

theorem block62_scan : scanFrom 15872 block62 =
    [] := by
  rw [block62]
  simp only [List.append_assoc]
  rw [scan_append, block62Piece00_scan, block62Piece00_length]
  rw [scan_append, block62Piece01_scan, block62Piece01_length]
  rw [scan_append, block62Piece02_scan, block62Piece02_length]
  rw [scan_append, block62Piece03_scan, block62Piece03_length]
  rw [scan_append, block62Piece04_scan, block62Piece04_length]
  rw [scan_append, block62Piece05_scan, block62Piece05_length]
  rw [scan_append, block62Piece06_scan, block62Piece06_length]
  rw [block62Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block62_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
