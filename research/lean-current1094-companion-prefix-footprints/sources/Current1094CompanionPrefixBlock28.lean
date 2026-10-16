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

def block28Piece00 : List Mark :=
  List.replicate 32 Mark.passive

def block28Piece01 : List Mark :=
  List.replicate 32 Mark.passive

def block28Piece02 : List Mark :=
  List.replicate 32 Mark.passive

def block28Piece03 : List Mark :=
  List.replicate 32 Mark.passive

def block28Piece04 : List Mark :=
  List.replicate 32 Mark.passive

def block28Piece05 : List Mark :=
  List.replicate 32 Mark.passive

def block28Piece06 : List Mark :=
  List.replicate 32 Mark.passive

def block28Piece07 : List Mark :=
  List.replicate 9 Mark.passive ++
  [.phase "entry_adapters", .relabel (.inl 0), .relabel (.inl 1), .relabel (.inl 2), .relabel (.inl 3), .relabel (.inl 4), .relabel (.inl 5), .relabel (.inl 6), .relabel (.inl 7), .relabel (.inl 8), .relabel (.inl 9), .relabel (.inl 10), .relabel (.inl 11), .relabel (.inl 12), .relabel (.inl 13), .relabel (.inl 14), .relabel (.inl 15), .relabel (.inl 16), .relabel (.inl 17), .relabel (.inl 18), .relabel (.inl 19), .relabel (.inl 20), .relabel (.inl 21)]

def block28 : List Mark :=
  block28Piece00 ++ block28Piece01 ++ block28Piece02 ++ block28Piece03 ++ block28Piece04 ++ block28Piece05 ++ block28Piece06 ++ block28Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28

theorem block28Piece00_length : block28Piece00.length = 32 := by
  simp only [block28Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block28Piece00_scan : scanFrom 7168 block28Piece00 =
    [] := by
  simpa only [block28Piece00] using (scan_passive 7168 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28Piece00_scan

theorem block28Piece01_length : block28Piece01.length = 32 := by
  simp only [block28Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block28Piece01_scan : scanFrom 7200 block28Piece01 =
    [] := by
  simpa only [block28Piece01] using (scan_passive 7200 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28Piece01_scan

theorem block28Piece02_length : block28Piece02.length = 32 := by
  simp only [block28Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block28Piece02_scan : scanFrom 7232 block28Piece02 =
    [] := by
  simpa only [block28Piece02] using (scan_passive 7232 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28Piece02_scan

theorem block28Piece03_length : block28Piece03.length = 32 := by
  simp only [block28Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block28Piece03_scan : scanFrom 7264 block28Piece03 =
    [] := by
  simpa only [block28Piece03] using (scan_passive 7264 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28Piece03_scan

theorem block28Piece04_length : block28Piece04.length = 32 := by
  simp only [block28Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block28Piece04_scan : scanFrom 7296 block28Piece04 =
    [] := by
  simpa only [block28Piece04] using (scan_passive 7296 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28Piece04_scan

theorem block28Piece05_length : block28Piece05.length = 32 := by
  simp only [block28Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block28Piece05_scan : scanFrom 7328 block28Piece05 =
    [] := by
  simpa only [block28Piece05] using (scan_passive 7328 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28Piece05_scan

theorem block28Piece06_length : block28Piece06.length = 32 := by
  simp only [block28Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block28Piece06_scan : scanFrom 7360 block28Piece06 =
    [] := by
  simpa only [block28Piece06] using (scan_passive 7360 32)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28Piece06_scan

theorem block28Piece07_length : block28Piece07.length = 32 := by
  simp only [block28Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block28Piece07_scan : scanFrom 7392 block28Piece07 =
    [(7401, .phase "entry_adapters")] := by
  simp only [block28Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28Piece07_scan

theorem block28_length : block28.length = 256 := by
  rw [block28]
  simp only [List.append_assoc]
  rw [List.length_append, block28Piece00_length]
  rw [List.length_append, block28Piece01_length]
  rw [List.length_append, block28Piece02_length]
  rw [List.length_append, block28Piece03_length]
  rw [List.length_append, block28Piece04_length]
  rw [List.length_append, block28Piece05_length]
  rw [List.length_append, block28Piece06_length]
  rw [block28Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28_length

theorem block28_scan : scanFrom 7168 block28 =
    [(7401, .phase "entry_adapters")] := by
  rw [block28]
  simp only [List.append_assoc]
  rw [scan_append, block28Piece00_scan, block28Piece00_length]
  rw [scan_append, block28Piece01_scan, block28Piece01_length]
  rw [scan_append, block28Piece02_scan, block28Piece02_length]
  rw [scan_append, block28Piece03_scan, block28Piece03_length]
  rw [scan_append, block28Piece04_scan, block28Piece04_length]
  rw [scan_append, block28Piece05_scan, block28Piece05_length]
  rw [scan_append, block28Piece06_scan, block28Piece06_length]
  rw [block28Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block28_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
