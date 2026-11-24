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

def block61Piece00 : List Mark :=
  [.relabel (.inl 340)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 294), .relabel (.inl 358)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 294)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 358)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 292), .relabel (.inl 356)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 292)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 356)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 608), .relabel (.inl 615)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 137), .relabel (.inl 608)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 121), .relabel (.inl 615)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 609), .relabel (.inl 614)] ++
  List.replicate 2 Mark.passive

def block61Piece01 : List Mark :=
  [.relabel (.inl 114), .relabel (.inl 609)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 173), .relabel (.inl 614)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 610), .relabel (.inl 613)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 610)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 613)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 611), .relabel (.inl 612)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 611)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 612)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 247), .relabel (.inl 364)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 143), .relabel (.inl 247)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 150), .relabel (.inl 364)] ++
  List.replicate 1 Mark.passive

def block61Piece02 : List Mark :=
  [.relabel (.inl 242), .relabel (.inl 366)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 124), .relabel (.inl 242)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 129), .relabel (.inl 366)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 263), .relabel (.inl 344)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 263)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 344)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 258), .relabel (.inl 28)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 258)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 28)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 616), .relabel (.inl 623)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 168), .relabel (.inl 616)]

def block61Piece03 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 189), .relabel (.inl 623)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 617), .relabel (.inl 622)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 212), .relabel (.inl 617)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 215), .relabel (.inl 622)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 618), .relabel (.inl 621)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 618)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 621)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 619), .relabel (.inl 620)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 619)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 620)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 246), .relabel (.inl 348)]

def block61Piece04 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 167), .relabel (.inl 246)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 131), .relabel (.inl 348)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 244), .relabel (.inl 350)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 213), .relabel (.inl 244)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 152), .relabel (.inl 350)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 262), .relabel (.inl 360)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 262)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 360)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 260), .relabel (.inl 60)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 260)] ++
  List.replicate 1 Mark.passive

def block61Piece05 : List Mark :=
  [.relabel (.inl 60)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 624), .relabel (.inl 631)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 214), .relabel (.inl 624)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 151), .relabel (.inl 631)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 625), .relabel (.inl 630)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 166), .relabel (.inl 625)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 130), .relabel (.inl 630)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 626), .relabel (.inl 629)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 626)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 629)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 627), .relabel (.inl 628)]

def block61Piece06 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 627)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 628)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 456), .relabel (.inl 396)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 197), .relabel (.inl 456)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 136), .relabel (.inl 396)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 457), .relabel (.inl 398)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 210), .relabel (.inl 457)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 219), .relabel (.inl 398)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 466), .relabel (.inl 376)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 466)] ++
  List.replicate 1 Mark.passive

def block61Piece07 : List Mark :=
  [.relabel (.inl 376)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 467), .relabel (.inl 66)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 467)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 66)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 632), .relabel (.inl 639)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 144), .relabel (.inl 632)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 147), .relabel (.inl 639)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 633), .relabel (.inl 638)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 160), .relabel (.inl 633)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 157), .relabel (.inl 638)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 634), .relabel (.inl 637)]

def block61 : List Mark :=
  block61Piece00 ++ block61Piece01 ++ block61Piece02 ++ block61Piece03 ++ block61Piece04 ++ block61Piece05 ++ block61Piece06 ++ block61Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61

theorem block61Piece00_length : block61Piece00.length = 32 := by
  simp only [block61Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block61Piece00_scan : scanFrom 15616 block61Piece00 =
    [] := by
  simp only [block61Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61Piece00_scan

theorem block61Piece01_length : block61Piece01.length = 32 := by
  simp only [block61Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block61Piece01_scan : scanFrom 15648 block61Piece01 =
    [] := by
  simp only [block61Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61Piece01_scan

theorem block61Piece02_length : block61Piece02.length = 32 := by
  simp only [block61Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block61Piece02_scan : scanFrom 15680 block61Piece02 =
    [] := by
  simp only [block61Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61Piece02_scan

theorem block61Piece03_length : block61Piece03.length = 32 := by
  simp only [block61Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block61Piece03_scan : scanFrom 15712 block61Piece03 =
    [] := by
  simp only [block61Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61Piece03_scan

theorem block61Piece04_length : block61Piece04.length = 32 := by
  simp only [block61Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block61Piece04_scan : scanFrom 15744 block61Piece04 =
    [] := by
  simp only [block61Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61Piece04_scan

theorem block61Piece05_length : block61Piece05.length = 32 := by
  simp only [block61Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block61Piece05_scan : scanFrom 15776 block61Piece05 =
    [] := by
  simp only [block61Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61Piece05_scan

theorem block61Piece06_length : block61Piece06.length = 32 := by
  simp only [block61Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block61Piece06_scan : scanFrom 15808 block61Piece06 =
    [(15831, .relabel (.inl 219))] := by
  simp only [block61Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61Piece06_scan

theorem block61Piece07_length : block61Piece07.length = 32 := by
  simp only [block61Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block61Piece07_scan : scanFrom 15840 block61Piece07 =
    [(15867, .relabel (.inl 157))] := by
  simp only [block61Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61Piece07_scan

theorem block61_length : block61.length = 256 := by
  rw [block61]
  simp only [List.append_assoc]
  rw [List.length_append, block61Piece00_length]
  rw [List.length_append, block61Piece01_length]
  rw [List.length_append, block61Piece02_length]
  rw [List.length_append, block61Piece03_length]
  rw [List.length_append, block61Piece04_length]
  rw [List.length_append, block61Piece05_length]
  rw [List.length_append, block61Piece06_length]
  rw [block61Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61_length

theorem block61_scan : scanFrom 15616 block61 =
    [(15831, .relabel (.inl 219)), (15867, .relabel (.inl 157))] := by
  rw [block61]
  simp only [List.append_assoc]
  rw [scan_append, block61Piece00_scan, block61Piece00_length]
  rw [scan_append, block61Piece01_scan, block61Piece01_length]
  rw [scan_append, block61Piece02_scan, block61Piece02_length]
  rw [scan_append, block61Piece03_scan, block61Piece03_length]
  rw [scan_append, block61Piece04_scan, block61Piece04_length]
  rw [scan_append, block61Piece05_scan, block61Piece05_length]
  rw [scan_append, block61Piece06_scan, block61Piece06_length]
  rw [block61Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block61_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
