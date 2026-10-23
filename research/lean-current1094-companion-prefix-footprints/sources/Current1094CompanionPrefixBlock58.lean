import Current1094CompanionPrefixBlock00

/-! UNCOMPILED structural dense-block pilot. The exact original256 marks of
block58 are partitioned into eight consecutive32-row pieces without changing
any value or order. Long passive runs use the accepted symbolic scan_passive
lemma; only bounded literal nonpassive segments reduce. Final length/scan
statements are unchanged. Original emitter/LemmaG/HyperplaneEnd/PR1611
attribution and parser/whole-word/physical limits remain. No cap change. -/
set_option Elab.async false
namespace CurrentMain.Current1094CompanionPrefixSkeleton
open CurrentMain.Current1094Helper450RelabelSlice

def block58Piece00 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 483), .relabel (.inl 555)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 506), .relabel (.inl 530)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 507), .relabel (.inl 531)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 518), .relabel (.inl 542)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 519), .relabel (.inl 543)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 494), .relabel (.inl 566)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 495), .relabel (.inl 567)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 592)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 593)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 594)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 595)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 596)] ++
  List.replicate 1 Mark.passive

def block58Piece01 : List Mark :=
  [.relabel (.inl 597)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 598)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 599)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 600)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 601)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 602)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 603)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 604)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 605)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 606)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 607)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 608)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 609)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 610)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 611)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 612)] ++
  List.replicate 1 Mark.passive

def block58Piece02 : List Mark :=
  [.relabel (.inl 613)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 614)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 615)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 616)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 617)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 618)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 619)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 620)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 621)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 622)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 623)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 624)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 625)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 626)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 627)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 628)] ++
  List.replicate 1 Mark.passive

def block58Piece03 : List Mark :=
  [.relabel (.inl 629)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 630)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 631)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 632)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 633)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 634)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 635)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 636)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 637)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 638)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 639)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 640)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 641)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 642)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 643)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 644)] ++
  List.replicate 1 Mark.passive

def block58Piece04 : List Mark :=
  [.relabel (.inl 645)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 646)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 647)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 648)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 649)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 650)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 651)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 652)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 653)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 654)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 655)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 656)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 657)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 658)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 659)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 660)] ++
  List.replicate 1 Mark.passive

def block58Piece05 : List Mark :=
  [.relabel (.inl 661)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 662)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 663)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 664)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 665)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 666)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 667)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 668)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 669)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 670)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 671)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 672)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 673)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 674)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 675)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 676)] ++
  List.replicate 1 Mark.passive

def block58Piece06 : List Mark :=
  [.relabel (.inl 677)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 678)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 679)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 680)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 681)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 682)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 683)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 684)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 685)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 686)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 687)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 688)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 689)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 690)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 691)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 692)] ++
  List.replicate 1 Mark.passive

def block58Piece07 : List Mark :=
  [.relabel (.inl 693)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 694)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 695)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 696)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 697)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 698)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 699)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 700)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 701)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 702)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 703)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 215), .relabel (.inl 484)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 129), .relabel (.inl 448)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 124), .relabel (.inl 485)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 212)]

def block58 : List Mark :=
  block58Piece00 ++ block58Piece01 ++ block58Piece02 ++ block58Piece03 ++ block58Piece04 ++ block58Piece05 ++ block58Piece06 ++ block58Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58

theorem block58Piece00_length : block58Piece00.length = 32 := by
  simp only [block58Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block58Piece00_scan : scanFrom 14848 block58Piece00 =
    [] := by
  simp only [block58Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58Piece00_scan

theorem block58Piece01_length : block58Piece01.length = 32 := by
  simp only [block58Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block58Piece01_scan : scanFrom 14880 block58Piece01 =
    [] := by
  simp only [block58Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58Piece01_scan

theorem block58Piece02_length : block58Piece02.length = 32 := by
  simp only [block58Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block58Piece02_scan : scanFrom 14912 block58Piece02 =
    [] := by
  simp only [block58Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58Piece02_scan

theorem block58Piece03_length : block58Piece03.length = 32 := by
  simp only [block58Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block58Piece03_scan : scanFrom 14944 block58Piece03 =
    [] := by
  simp only [block58Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58Piece03_scan

theorem block58Piece04_length : block58Piece04.length = 32 := by
  simp only [block58Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block58Piece04_scan : scanFrom 14976 block58Piece04 =
    [] := by
  simp only [block58Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58Piece04_scan

theorem block58Piece05_length : block58Piece05.length = 32 := by
  simp only [block58Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block58Piece05_scan : scanFrom 15008 block58Piece05 =
    [] := by
  simp only [block58Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58Piece05_scan

theorem block58Piece06_length : block58Piece06.length = 32 := by
  simp only [block58Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block58Piece06_scan : scanFrom 15040 block58Piece06 =
    [] := by
  simp only [block58Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58Piece06_scan

theorem block58Piece07_length : block58Piece07.length = 32 := by
  simp only [block58Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block58Piece07_scan : scanFrom 15072 block58Piece07 =
    [] := by
  simp only [block58Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58Piece07_scan

theorem block58_length : block58.length = 256 := by
  rw [block58]
  simp only [List.append_assoc]
  rw [List.length_append, block58Piece00_length]
  rw [List.length_append, block58Piece01_length]
  rw [List.length_append, block58Piece02_length]
  rw [List.length_append, block58Piece03_length]
  rw [List.length_append, block58Piece04_length]
  rw [List.length_append, block58Piece05_length]
  rw [List.length_append, block58Piece06_length]
  rw [block58Piece07_length]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58_length

theorem block58_scan : scanFrom 14848 block58 =
    [] := by
  rw [block58]
  simp only [List.append_assoc]
  rw [scan_append, block58Piece00_scan, block58Piece00_length]
  rw [scan_append, block58Piece01_scan, block58Piece01_length]
  rw [scan_append, block58Piece02_scan, block58Piece02_length]
  rw [scan_append, block58Piece03_scan, block58Piece03_length]
  rw [scan_append, block58Piece04_scan, block58Piece04_length]
  rw [scan_append, block58Piece05_scan, block58Piece05_length]
  rw [scan_append, block58Piece06_scan, block58Piece06_length]
  rw [block58Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block58_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
