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

def block51Piece00 : List Mark :=
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 126)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 164)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 153)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 218)] ++
  List.replicate 13 Mark.passive ++
  [.relabel (.inl 190)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 211)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 155)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 216)] ++
  List.replicate 1 Mark.passive

def block51Piece01 : List Mark :=
  List.replicate 12 Mark.passive ++
  [.relabel (.inl 133)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 159)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 149)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 222)] ++
  List.replicate 13 Mark.passive

def block51Piece02 : List Mark :=
  [.relabel (.inl 672)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 673)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 674)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 676)] ++
  List.replicate 7 Mark.passive ++
  [.relabel (.inl 680)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 681)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 682)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 684)] ++
  List.replicate 7 Mark.passive

def block51Piece03 : List Mark :=
  [.relabel (.inl 696)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 697)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 698)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 700)] ++
  List.replicate 7 Mark.passive ++
  [.relabel (.inl 688)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 689)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 690)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 692)] ++
  List.replicate 7 Mark.passive

def block51Piece04 : List Mark :=
  [.relabel (.inl 482)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 664)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 665)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 666)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 668)] ++
  List.replicate 7 Mark.passive ++
  [.relabel (.inl 656)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 657)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 658)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 660)] ++
  List.replicate 1 Mark.passive

def block51Piece05 : List Mark :=
  List.replicate 6 Mark.passive ++
  [.relabel (.inl 640)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 641)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 642)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 644)] ++
  List.replicate 7 Mark.passive ++
  [.relabel (.inl 632)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 633)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 634)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 636)] ++
  List.replicate 1 Mark.passive

def block51Piece06 : List Mark :=
  List.replicate 6 Mark.passive ++
  [.relabel (.inl 624)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 625)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 626)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 628)] ++
  List.replicate 7 Mark.passive ++
  [.relabel (.inl 600)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 601)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 602)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 604)] ++
  List.replicate 1 Mark.passive

def block51Piece07 : List Mark :=
  List.replicate 6 Mark.passive ++
  [.relabel (.inl 608)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 609)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 610)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 612)] ++
  List.replicate 7 Mark.passive ++
  [.relabel (.inl 592)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 593)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 594)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 596)] ++
  List.replicate 1 Mark.passive

def block51 : List Mark :=
  block51Piece00 ++ block51Piece01 ++ block51Piece02 ++ block51Piece03 ++ block51Piece04 ++ block51Piece05 ++ block51Piece06 ++ block51Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51

theorem block51Piece00_length : block51Piece00.length = 32 := by
  simp only [block51Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block51Piece00_scan : scanFrom 13056 block51Piece00 =
    [] := by
  simp only [block51Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51Piece00_scan

theorem block51Piece01_length : block51Piece01.length = 32 := by
  simp only [block51Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block51Piece01_scan : scanFrom 13088 block51Piece01 =
    [] := by
  simp only [block51Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51Piece01_scan

theorem block51Piece02_length : block51Piece02.length = 32 := by
  simp only [block51Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block51Piece02_scan : scanFrom 13120 block51Piece02 =
    [] := by
  simp only [block51Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51Piece02_scan

theorem block51Piece03_length : block51Piece03.length = 32 := by
  simp only [block51Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block51Piece03_scan : scanFrom 13152 block51Piece03 =
    [] := by
  simp only [block51Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51Piece03_scan

theorem block51Piece04_length : block51Piece04.length = 32 := by
  simp only [block51Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block51Piece04_scan : scanFrom 13184 block51Piece04 =
    [] := by
  simp only [block51Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51Piece04_scan

theorem block51Piece05_length : block51Piece05.length = 32 := by
  simp only [block51Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block51Piece05_scan : scanFrom 13216 block51Piece05 =
    [] := by
  simp only [block51Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51Piece05_scan

theorem block51Piece06_length : block51Piece06.length = 32 := by
  simp only [block51Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block51Piece06_scan : scanFrom 13248 block51Piece06 =
    [] := by
  simp only [block51Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51Piece06_scan

theorem block51Piece07_length : block51Piece07.length = 32 := by
  simp only [block51Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block51Piece07_scan : scanFrom 13280 block51Piece07 =
    [] := by
  simp only [block51Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51Piece07_scan

theorem block51_length : block51.length = 256 := by
  rw [block51]
  simp only [List.append_assoc]
  rw [List.length_append, block51Piece00_length]
  rw [List.length_append, block51Piece01_length]
  rw [List.length_append, block51Piece02_length]
  rw [List.length_append, block51Piece03_length]
  rw [List.length_append, block51Piece04_length]
  rw [List.length_append, block51Piece05_length]
  rw [List.length_append, block51Piece06_length]
  rw [block51Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51_length

theorem block51_scan : scanFrom 13056 block51 =
    [] := by
  rw [block51]
  simp only [List.append_assoc]
  rw [scan_append, block51Piece00_scan, block51Piece00_length]
  rw [scan_append, block51Piece01_scan, block51Piece01_length]
  rw [scan_append, block51Piece02_scan, block51Piece02_length]
  rw [scan_append, block51Piece03_scan, block51Piece03_length]
  rw [scan_append, block51Piece04_scan, block51Piece04_length]
  rw [scan_append, block51Piece05_scan, block51Piece05_length]
  rw [scan_append, block51Piece06_scan, block51Piece06_length]
  rw [block51Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block51_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
