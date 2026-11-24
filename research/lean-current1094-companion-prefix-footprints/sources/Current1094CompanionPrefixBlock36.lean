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

def block36Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block36Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block36Piece02 : List Mark :=
  List.replicate 17 Mark.passive ++
  [.relabel (.inl 546)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 560)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 547)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 568)] ++
  List.replicate 7 Mark.passive

def block36Piece03 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 548)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 558)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 549)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 570)] ++
  List.replicate 7 Mark.passive ++
  [.relabel (.inl 464)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 465)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 470)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 471)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 478)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 479)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 514)] ++
  List.replicate 1 Mark.passive

def block36Piece04 : List Mark :=
  [.relabel (.inl 515)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 468)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 469)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 480)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 481)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 516)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 517)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 466)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 467)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 490)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 491)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 502)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 503)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 492)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 493)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 504)] ++
  List.replicate 1 Mark.passive

def block36Piece05 : List Mark :=
  [.relabel (.inl 505)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 456)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 457)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 462)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 463)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 460)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 461)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 458)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 459)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 224)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 225)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 226)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 227)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 228)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 229)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 230)] ++
  List.replicate 1 Mark.passive

def block36Piece06 : List Mark :=
  [.relabel (.inl 231)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 232)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 233)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 234)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 235)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 236)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 237)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 238)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 239)] ++
  List.replicate 15 Mark.passive

def block36Piece07 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 0), .relabel (.inl 27)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 224), .relabel (.inl 57)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 225), .relabel (.inl 7)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 76), .relabel (.inl 87)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 226), .relabel (.inl 92)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 227), .relabel (.inl 81)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 228), .relabel (.inl 232)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 229), .relabel (.inl 238)]

def block36 : List Mark :=
  block36Piece00 ++ block36Piece01 ++ block36Piece02 ++ block36Piece03 ++ block36Piece04 ++ block36Piece05 ++ block36Piece06 ++ block36Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36

theorem block36Piece00_length : block36Piece00.length = 32 := by
  simp only [block36Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block36Piece00_scan : scanFrom 9216 block36Piece00 =
    [] := by
  simpa only [block36Piece00] using (scan_passive 9216 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36Piece00_scan

theorem block36Piece01_length : block36Piece01.length = 32 := by
  simp only [block36Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block36Piece01_scan : scanFrom 9248 block36Piece01 =
    [] := by
  simpa only [block36Piece01] using (scan_passive 9248 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36Piece01_scan

theorem block36Piece02_length : block36Piece02.length = 32 := by
  simp only [block36Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block36Piece02_scan : scanFrom 9280 block36Piece02 =
    [] := by
  simp only [block36Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36Piece02_scan

theorem block36Piece03_length : block36Piece03.length = 32 := by
  simp only [block36Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block36Piece03_scan : scanFrom 9312 block36Piece03 =
    [] := by
  simp only [block36Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36Piece03_scan

theorem block36Piece04_length : block36Piece04.length = 32 := by
  simp only [block36Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block36Piece04_scan : scanFrom 9344 block36Piece04 =
    [] := by
  simp only [block36Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36Piece04_scan

theorem block36Piece05_length : block36Piece05.length = 32 := by
  simp only [block36Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block36Piece05_scan : scanFrom 9376 block36Piece05 =
    [(9406, .relabel (.inl 230))] := by
  simp only [block36Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36Piece05_scan

theorem block36Piece06_length : block36Piece06.length = 32 := by
  simp only [block36Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block36Piece06_scan : scanFrom 9408 block36Piece06 =
    [] := by
  simp only [block36Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36Piece06_scan

theorem block36Piece07_length : block36Piece07.length = 32 := by
  simp only [block36Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block36Piece07_scan : scanFrom 9440 block36Piece07 =
    [] := by
  simp only [block36Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36Piece07_scan

theorem block36_length : block36.length = 256 := by
  rw [block36]
  simp only [List.append_assoc]
  rw [List.length_append, block36Piece00_length]
  rw [List.length_append, block36Piece01_length]
  rw [List.length_append, block36Piece02_length]
  rw [List.length_append, block36Piece03_length]
  rw [List.length_append, block36Piece04_length]
  rw [List.length_append, block36Piece05_length]
  rw [List.length_append, block36Piece06_length]
  rw [block36Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36_length

theorem block36_scan : scanFrom 9216 block36 =
    [(9406, .relabel (.inl 230))] := by
  rw [block36]
  simp only [List.append_assoc]
  rw [scan_append, block36Piece00_scan, block36Piece00_length]
  rw [scan_append, block36Piece01_scan, block36Piece01_length]
  rw [scan_append, block36Piece02_scan, block36Piece02_length]
  rw [scan_append, block36Piece03_scan, block36Piece03_length]
  rw [scan_append, block36Piece04_scan, block36Piece04_length]
  rw [scan_append, block36Piece05_scan, block36Piece05_length]
  rw [scan_append, block36Piece06_scan, block36Piece06_length]
  rw [block36Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block36_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
