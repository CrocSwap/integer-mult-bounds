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

def block37Piece00 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 230), .relabel (.inl 234)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 231), .relabel (.inl 236)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 233), .relabel (.inl 239)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 235), .relabel (.inl 237)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 231), .relabel (.inl 229)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 226), .relabel (.inl 224)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 230), .relabel (.inl 227)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 228), .relabel (.inl 225)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 232), .relabel (.inl 234)]

def block37Piece01 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 7), .relabel (.inl 81)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 236), .relabel (.inl 92)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 238), .relabel (.inl 57)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 57), .relabel (.inl 92)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 224)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 225)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 81)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 227)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 229)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 234)]

def block37Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block37Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block37Piece04 : List Mark :=
  List.replicate 12 Mark.passive ++
  [.relabel (.inl 240)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 241)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 242)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 243)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 244)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 245)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 246)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 247)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 248)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 249)] ++
  List.replicate 1 Mark.passive

def block37Piece05 : List Mark :=
  [.relabel (.inl 250)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 251)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 252)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 253)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 254)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 255)] ++
  List.replicate 17 Mark.passive ++
  [.relabel (.inl 70), .relabel (.inl 91)] ++
  List.replicate 2 Mark.passive

def block37Piece06 : List Mark :=
  [.relabel (.inl 240), .relabel (.inl 62)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 241), .relabel (.inl 10)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 71), .relabel (.inl 90)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 242), .relabel (.inl 63)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 243), .relabel (.inl 11)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 244), .relabel (.inl 248)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 245), .relabel (.inl 254)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 246), .relabel (.inl 250)] ++
  List.replicate 2 Mark.passive

def block37Piece07 : List Mark :=
  [.relabel (.inl 247), .relabel (.inl 252)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 249), .relabel (.inl 255)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 251), .relabel (.inl 253)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 247), .relabel (.inl 245)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 242), .relabel (.inl 240)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 246), .relabel (.inl 243)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 244), .relabel (.inl 241)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 248), .relabel (.inl 250)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 10), .relabel (.inl 11)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 252), .relabel (.inl 63)]

def block37 : List Mark :=
  block37Piece00 ++ block37Piece01 ++ block37Piece02 ++ block37Piece03 ++ block37Piece04 ++ block37Piece05 ++ block37Piece06 ++ block37Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37

theorem block37Piece00_length : block37Piece00.length = 32 := by
  simp only [block37Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block37Piece00_scan : scanFrom 9472 block37Piece00 =
    [(9474, .relabel (.inl 230)), (9496, .relabel (.inl 230))] := by
  simp only [block37Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37Piece00_scan

theorem block37Piece01_length : block37Piece01.length = 32 := by
  simp only [block37Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block37Piece01_scan : scanFrom 9504 block37Piece01 =
    [] := by
  simp only [block37Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37Piece01_scan

theorem block37Piece02_length : block37Piece02.length = 32 := by
  simp only [block37Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block37Piece02_scan : scanFrom 9536 block37Piece02 =
    [] := by
  simpa only [block37Piece02] using (scan_passive 9536 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37Piece02_scan

theorem block37Piece03_length : block37Piece03.length = 32 := by
  simp only [block37Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block37Piece03_scan : scanFrom 9568 block37Piece03 =
    [] := by
  simpa only [block37Piece03] using (scan_passive 9568 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37Piece03_scan

theorem block37Piece04_length : block37Piece04.length = 32 := by
  simp only [block37Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block37Piece04_scan : scanFrom 9600 block37Piece04 =
    [] := by
  simp only [block37Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37Piece04_scan

theorem block37Piece05_length : block37Piece05.length = 32 := by
  simp only [block37Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block37Piece05_scan : scanFrom 9632 block37Piece05 =
    [] := by
  simp only [block37Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37Piece05_scan

theorem block37Piece06_length : block37Piece06.length = 32 := by
  simp only [block37Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block37Piece06_scan : scanFrom 9664 block37Piece06 =
    [] := by
  simp only [block37Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37Piece06_scan

theorem block37Piece07_length : block37Piece07.length = 32 := by
  simp only [block37Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block37Piece07_scan : scanFrom 9696 block37Piece07 =
    [] := by
  simp only [block37Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37Piece07_scan

theorem block37_length : block37.length = 256 := by
  rw [block37]
  simp only [List.append_assoc]
  rw [List.length_append, block37Piece00_length]
  rw [List.length_append, block37Piece01_length]
  rw [List.length_append, block37Piece02_length]
  rw [List.length_append, block37Piece03_length]
  rw [List.length_append, block37Piece04_length]
  rw [List.length_append, block37Piece05_length]
  rw [List.length_append, block37Piece06_length]
  rw [block37Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37_length

theorem block37_scan : scanFrom 9472 block37 =
    [(9474, .relabel (.inl 230)), (9496, .relabel (.inl 230))] := by
  rw [block37]
  simp only [List.append_assoc]
  rw [scan_append, block37Piece00_scan, block37Piece00_length]
  rw [scan_append, block37Piece01_scan, block37Piece01_length]
  rw [scan_append, block37Piece02_scan, block37Piece02_length]
  rw [scan_append, block37Piece03_scan, block37Piece03_length]
  rw [scan_append, block37Piece04_scan, block37Piece04_length]
  rw [scan_append, block37Piece05_scan, block37Piece05_length]
  rw [scan_append, block37Piece06_scan, block37Piece06_length]
  rw [block37Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block37_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
