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

def block43Piece00 : List Mark :=
  [.relabel (.inl 345), .relabel (.inl 351)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 347), .relabel (.inl 349)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 343), .relabel (.inl 341)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 338), .relabel (.inl 336)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 342), .relabel (.inl 339)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 340), .relabel (.inl 337)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 344), .relabel (.inl 346)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 28), .relabel (.inl 86)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 348), .relabel (.inl 93)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 350), .relabel (.inl 58)] ++
  List.replicate 1 Mark.passive

def block43Piece01 : List Mark :=
  [.relabel (.inl 58), .relabel (.inl 93)] ++
  List.replicate 5 Mark.passive ++
  [.relabel (.inl 336)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 337)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 86)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 339)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 341)] ++
  List.replicate 4 Mark.passive ++
  [.relabel (.inl 346)] ++
  List.replicate 10 Mark.passive

def block43Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block43Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block43Piece04 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 352)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 353)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 354)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 355)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 356)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 357)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 358)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 359)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 360)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 361)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 362)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 363)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 364)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 365)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 366)] ++
  List.replicate 1 Mark.passive

def block43Piece05 : List Mark :=
  [.relabel (.inl 367)] ++
  List.replicate 17 Mark.passive ++
  [.relabel (.inl 83), .relabel (.inl 74)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 352), .relabel (.inl 30)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 353), .relabel (.inl 60)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 73), .relabel (.inl 84)]

def block43Piece06 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 354), .relabel (.inl 59)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 355), .relabel (.inl 29)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 356), .relabel (.inl 360)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 357), .relabel (.inl 366)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 358), .relabel (.inl 362)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 359), .relabel (.inl 364)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 361), .relabel (.inl 367)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 363), .relabel (.inl 365)]

def block43Piece07 : List Mark :=
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 359), .relabel (.inl 357)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 354), .relabel (.inl 352)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 358), .relabel (.inl 355)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 356), .relabel (.inl 353)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 360), .relabel (.inl 362)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 60), .relabel (.inl 29)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 364), .relabel (.inl 59)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 366), .relabel (.inl 30)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 30), .relabel (.inl 59)] ++
  List.replicate 4 Mark.passive

def block43 : List Mark :=
  block43Piece00 ++ block43Piece01 ++ block43Piece02 ++ block43Piece03 ++ block43Piece04 ++ block43Piece05 ++ block43Piece06 ++ block43Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43

theorem block43Piece00_length : block43Piece00.length = 32 := by
  simp only [block43Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block43Piece00_scan : scanFrom 11008 block43Piece00 =
    [] := by
  simp only [block43Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43Piece00_scan

theorem block43Piece01_length : block43Piece01.length = 32 := by
  simp only [block43Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block43Piece01_scan : scanFrom 11040 block43Piece01 =
    [] := by
  simp only [block43Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43Piece01_scan

theorem block43Piece02_length : block43Piece02.length = 32 := by
  simp only [block43Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block43Piece02_scan : scanFrom 11072 block43Piece02 =
    [] := by
  simpa only [block43Piece02] using (scan_passive 11072 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43Piece02_scan

theorem block43Piece03_length : block43Piece03.length = 32 := by
  simp only [block43Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block43Piece03_scan : scanFrom 11104 block43Piece03 =
    [] := by
  simpa only [block43Piece03] using (scan_passive 11104 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43Piece03_scan

theorem block43Piece04_length : block43Piece04.length = 32 := by
  simp only [block43Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block43Piece04_scan : scanFrom 11136 block43Piece04 =
    [] := by
  simp only [block43Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43Piece04_scan

theorem block43Piece05_length : block43Piece05.length = 32 := by
  simp only [block43Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block43Piece05_scan : scanFrom 11168 block43Piece05 =
    [] := by
  simp only [block43Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43Piece05_scan

theorem block43Piece06_length : block43Piece06.length = 32 := by
  simp only [block43Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block43Piece06_scan : scanFrom 11200 block43Piece06 =
    [] := by
  simp only [block43Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43Piece06_scan

theorem block43Piece07_length : block43Piece07.length = 32 := by
  simp only [block43Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block43Piece07_scan : scanFrom 11232 block43Piece07 =
    [] := by
  simp only [block43Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43Piece07_scan

theorem block43_length : block43.length = 256 := by
  rw [block43]
  simp only [List.append_assoc]
  rw [List.length_append, block43Piece00_length]
  rw [List.length_append, block43Piece01_length]
  rw [List.length_append, block43Piece02_length]
  rw [List.length_append, block43Piece03_length]
  rw [List.length_append, block43Piece04_length]
  rw [List.length_append, block43Piece05_length]
  rw [List.length_append, block43Piece06_length]
  rw [block43Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43_length

theorem block43_scan : scanFrom 11008 block43 =
    [] := by
  rw [block43]
  simp only [List.append_assoc]
  rw [scan_append, block43Piece00_scan, block43Piece00_length]
  rw [scan_append, block43Piece01_scan, block43Piece01_length]
  rw [scan_append, block43Piece02_scan, block43Piece02_length]
  rw [scan_append, block43Piece03_scan, block43Piece03_length]
  rw [scan_append, block43Piece04_scan, block43Piece04_length]
  rw [scan_append, block43Piece05_scan, block43Piece05_length]
  rw [scan_append, block43Piece06_scan, block43Piece06_length]
  rw [block43Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block43_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
