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

def block31Piece00 : List Mark :=
  [.relabel (.inl 534), .relabel (.inl 535), .relabel (.inl 536), .relabel (.inl 537), .relabel (.inl 538), .relabel (.inl 539), .relabel (.inl 540), .relabel (.inl 541), .relabel (.inl 542), .relabel (.inl 543), .relabel (.inl 544), .relabel (.inl 545), .relabel (.inl 546), .relabel (.inl 547), .relabel (.inl 548), .relabel (.inl 549), .relabel (.inl 550), .relabel (.inl 551), .relabel (.inl 552), .relabel (.inl 553), .relabel (.inl 554), .relabel (.inl 555), .relabel (.inl 556), .relabel (.inl 557), .relabel (.inl 558), .relabel (.inl 559), .relabel (.inl 560), .relabel (.inl 561), .relabel (.inl 562), .relabel (.inl 563), .relabel (.inl 564), .relabel (.inl 565)]

def block31Piece01 : List Mark :=
  [.relabel (.inl 566), .relabel (.inl 567), .relabel (.inl 568), .relabel (.inl 569), .relabel (.inl 570), .relabel (.inl 571), .relabel (.inl 572), .relabel (.inl 573), .relabel (.inl 574), .relabel (.inl 575), .relabel (.inl 576), .relabel (.inl 577), .relabel (.inl 578), .relabel (.inl 579), .relabel (.inl 580), .relabel (.inl 581), .relabel (.inl 582), .relabel (.inl 583), .relabel (.inl 584), .relabel (.inl 585), .relabel (.inl 586), .relabel (.inl 587), .relabel (.inl 588), .relabel (.inl 589), .relabel (.inl 590), .relabel (.inl 591), .relabel (.inl 592), .relabel (.inl 593), .relabel (.inl 594), .relabel (.inl 595), .relabel (.inl 596), .relabel (.inl 597)]

def block31Piece02 : List Mark :=
  [.relabel (.inl 598), .relabel (.inl 599), .relabel (.inl 600), .relabel (.inl 601), .relabel (.inl 602), .relabel (.inl 603), .relabel (.inl 604), .relabel (.inl 605), .relabel (.inl 606), .relabel (.inl 607), .relabel (.inl 608), .relabel (.inl 609), .relabel (.inl 610), .relabel (.inl 611), .relabel (.inl 612), .relabel (.inl 613), .relabel (.inl 614), .relabel (.inl 615), .relabel (.inl 616), .relabel (.inl 617), .relabel (.inl 618), .relabel (.inl 619), .relabel (.inl 620), .relabel (.inl 621), .relabel (.inl 622), .relabel (.inl 623), .relabel (.inl 624), .relabel (.inl 625), .relabel (.inl 626), .relabel (.inl 627), .relabel (.inl 628), .relabel (.inl 629)]

def block31Piece03 : List Mark :=
  [.relabel (.inl 630), .relabel (.inl 631), .relabel (.inl 632), .relabel (.inl 633), .relabel (.inl 634), .relabel (.inl 635), .relabel (.inl 636), .relabel (.inl 637), .relabel (.inl 638), .relabel (.inl 639), .relabel (.inl 640), .relabel (.inl 641), .relabel (.inl 642), .relabel (.inl 643), .relabel (.inl 644), .relabel (.inl 645), .relabel (.inl 646), .relabel (.inl 647), .relabel (.inl 648), .relabel (.inl 649), .relabel (.inl 650), .relabel (.inl 651), .relabel (.inl 652), .relabel (.inl 653), .relabel (.inl 654), .relabel (.inl 655), .relabel (.inl 656), .relabel (.inl 657), .relabel (.inl 658), .relabel (.inl 659), .relabel (.inl 660), .relabel (.inl 661)]

def block31Piece04 : List Mark :=
  [.relabel (.inl 662), .relabel (.inl 663), .relabel (.inl 664), .relabel (.inl 665), .relabel (.inl 666), .relabel (.inl 667), .relabel (.inl 668), .relabel (.inl 669), .relabel (.inl 670), .relabel (.inl 671), .relabel (.inl 672), .relabel (.inl 673), .relabel (.inl 674), .relabel (.inl 675), .relabel (.inl 676), .relabel (.inl 677), .relabel (.inl 678), .relabel (.inl 679), .relabel (.inl 680), .relabel (.inl 681), .relabel (.inl 682), .relabel (.inl 683), .relabel (.inl 684), .relabel (.inl 685), .relabel (.inl 686), .relabel (.inl 687), .relabel (.inl 688), .relabel (.inl 689), .relabel (.inl 690), .relabel (.inl 691), .relabel (.inl 692), .relabel (.inl 693)]

def block31Piece05 : List Mark :=
  [.relabel (.inl 694), .relabel (.inl 695), .relabel (.inl 696), .relabel (.inl 697), .relabel (.inl 698), .relabel (.inl 699), .relabel (.inl 700), .relabel (.inl 701), .relabel (.inl 702), .relabel (.inl 703), .phase "A"] ++
  List.replicate 21 Mark.passive

def block31Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block31Piece07 : List Mark :=
  List.replicate 32 Mark.passive

def block31 : List Mark :=
  block31Piece00 ++ block31Piece01 ++ block31Piece02 ++ block31Piece03 ++ block31Piece04 ++ block31Piece05 ++ block31Piece06 ++ block31Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31

theorem block31Piece00_length : block31Piece00.length = 32 := by
  simp only [block31Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block31Piece00_scan : scanFrom 7936 block31Piece00 =
    [] := by
  simp only [block31Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31Piece00_scan

theorem block31Piece01_length : block31Piece01.length = 32 := by
  simp only [block31Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block31Piece01_scan : scanFrom 7968 block31Piece01 =
    [] := by
  simp only [block31Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31Piece01_scan

theorem block31Piece02_length : block31Piece02.length = 32 := by
  simp only [block31Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block31Piece02_scan : scanFrom 8000 block31Piece02 =
    [] := by
  simp only [block31Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31Piece02_scan

theorem block31Piece03_length : block31Piece03.length = 32 := by
  simp only [block31Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block31Piece03_scan : scanFrom 8032 block31Piece03 =
    [] := by
  simp only [block31Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31Piece03_scan

theorem block31Piece04_length : block31Piece04.length = 32 := by
  simp only [block31Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block31Piece04_scan : scanFrom 8064 block31Piece04 =
    [] := by
  simp only [block31Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31Piece04_scan

theorem block31Piece05_length : block31Piece05.length = 32 := by
  simp only [block31Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block31Piece05_scan : scanFrom 8096 block31Piece05 =
    [(8106, .phase "A")] := by
  simp only [block31Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31Piece05_scan

theorem block31Piece06_length : block31Piece06.length = 32 := by
  simp only [block31Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block31Piece06_scan : scanFrom 8128 block31Piece06 =
    [] := by
  simpa only [block31Piece06] using (scan_passive 8128 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31Piece06_scan

theorem block31Piece07_length : block31Piece07.length = 32 := by
  simp only [block31Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block31Piece07_scan : scanFrom 8160 block31Piece07 =
    [] := by
  simpa only [block31Piece07] using (scan_passive 8160 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31Piece07_scan

theorem block31_length : block31.length = 256 := by
  rw [block31]
  simp only [List.append_assoc]
  rw [List.length_append, block31Piece00_length]
  rw [List.length_append, block31Piece01_length]
  rw [List.length_append, block31Piece02_length]
  rw [List.length_append, block31Piece03_length]
  rw [List.length_append, block31Piece04_length]
  rw [List.length_append, block31Piece05_length]
  rw [List.length_append, block31Piece06_length]
  rw [block31Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31_length

theorem block31_scan : scanFrom 7936 block31 =
    [(8106, .phase "A")] := by
  rw [block31]
  simp only [List.append_assoc]
  rw [scan_append, block31Piece00_scan, block31Piece00_length]
  rw [scan_append, block31Piece01_scan, block31Piece01_length]
  rw [scan_append, block31Piece02_scan, block31Piece02_length]
  rw [scan_append, block31Piece03_scan, block31Piece03_length]
  rw [scan_append, block31Piece04_scan, block31Piece04_length]
  rw [scan_append, block31Piece05_scan, block31Piece05_length]
  rw [scan_append, block31Piece06_scan, block31Piece06_length]
  rw [block31Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block31_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
