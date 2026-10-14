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

def block50Piece00 : List Mark :=
  [.relabel (.inl 161)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 171)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 195)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 208)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 180)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 168)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 150)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 143)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 189)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 187)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 136)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 197)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 147)]

def block50Piece01 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 196)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 221)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 186)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 135)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 214)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 131)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 167)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 151)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 116)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 188)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 199)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 204)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 193)] ++
  List.replicate 5 Mark.passive

def block50Piece02 : List Mark :=
  List.replicate 8 Mark.passive ++
  [.relabel (.inl 183)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 202)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 175)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 123)] ++
  List.replicate 13 Mark.passive ++
  [.relabel (.inl 114)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 137)] ++
  List.replicate 1 Mark.passive

def block50Piece03 : List Mark :=
  [.relabel (.inl 173)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 121)] ++
  List.replicate 29 Mark.passive

def block50Piece04 : List Mark :=
  [.relabel (.inl 166)] ++
  List.replicate 19 Mark.passive ++
  [.relabel (.inl 144)] ++
  List.replicate 11 Mark.passive

def block50Piece05 : List Mark :=
  List.replicate 6 Mark.passive ++
  [.relabel (.inl 146)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 162)] ++
  List.replicate 20 Mark.passive ++
  [.relabel (.inl 198)] ++
  List.replicate 2 Mark.passive

def block50Piece06 : List Mark :=
  List.replicate 11 Mark.passive ++
  [.relabel (.inl 185)] ++
  List.replicate 3 Mark.passive ++
  [.relabel (.inl 141)] ++
  List.replicate 14 Mark.passive ++
  [.relabel (.inl 115)] ++
  List.replicate 1 Mark.passive

def block50Piece07 : List Mark :=
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 138)] ++
  List.replicate 13 Mark.passive ++
  [.relabel (.inl 117)] ++
  List.replicate 1 Mark.passive ++
  [.relabel (.inl 181)] ++
  List.replicate 2 Mark.passive ++
  [.relabel (.inl 177)] ++
  List.replicate 11 Mark.passive

def block50 : List Mark :=
  block50Piece00 ++ block50Piece01 ++ block50Piece02 ++ block50Piece03 ++ block50Piece04 ++ block50Piece05 ++ block50Piece06 ++ block50Piece07

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50

theorem block50Piece00_length : block50Piece00.length = 32 := by
  simp only [block50Piece00, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block50Piece00_scan : scanFrom 12800 block50Piece00 =
    [] := by
  simp only [block50Piece00, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50Piece00_scan

theorem block50Piece01_length : block50Piece01.length = 32 := by
  simp only [block50Piece01, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block50Piece01_scan : scanFrom 12832 block50Piece01 =
    [] := by
  simp only [block50Piece01, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50Piece01_scan

theorem block50Piece02_length : block50Piece02.length = 32 := by
  simp only [block50Piece02, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block50Piece02_scan : scanFrom 12864 block50Piece02 =
    [] := by
  simp only [block50Piece02, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50Piece02_scan

theorem block50Piece03_length : block50Piece03.length = 32 := by
  simp only [block50Piece03, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block50Piece03_scan : scanFrom 12896 block50Piece03 =
    [] := by
  simp only [block50Piece03, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50Piece03_scan

theorem block50Piece04_length : block50Piece04.length = 32 := by
  simp only [block50Piece04, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block50Piece04_scan : scanFrom 12928 block50Piece04 =
    [] := by
  simp only [block50Piece04, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50Piece04_scan

theorem block50Piece05_length : block50Piece05.length = 32 := by
  simp only [block50Piece05, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block50Piece05_scan : scanFrom 12960 block50Piece05 =
    [] := by
  simp only [block50Piece05, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50Piece05_scan

theorem block50Piece06_length : block50Piece06.length = 32 := by
  simp only [block50Piece06, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block50Piece06_scan : scanFrom 12992 block50Piece06 =
    [] := by
  simp only [block50Piece06, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50Piece06_scan

theorem block50Piece07_length : block50Piece07.length = 32 := by
  simp only [block50Piece07, List.length_append, List.length_replicate, List.length_cons, List.length_nil]

theorem block50Piece07_scan : scanFrom 13024 block50Piece07 =
    [] := by
  simp only [block50Piece07, scan_append, scan_passive, List.length_append, List.length_replicate, List.length_cons, List.length_nil]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50Piece07_scan

theorem block50_length : block50.length = 256 := by
  rw [block50]
  simp only [List.append_assoc]
  rw [List.length_append, block50Piece00_length]
  rw [List.length_append, block50Piece01_length]
  rw [List.length_append, block50Piece02_length]
  rw [List.length_append, block50Piece03_length]
  rw [List.length_append, block50Piece04_length]
  rw [List.length_append, block50Piece05_length]
  rw [List.length_append, block50Piece06_length]
  rw [block50Piece07_length]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50_length

theorem block50_scan : scanFrom 12800 block50 =
    [] := by
  rw [block50]
  simp only [List.append_assoc]
  rw [scan_append, block50Piece00_scan, block50Piece00_length]
  rw [scan_append, block50Piece01_scan, block50Piece01_length]
  rw [scan_append, block50Piece02_scan, block50Piece02_length]
  rw [scan_append, block50Piece03_scan, block50Piece03_length]
  rw [scan_append, block50Piece04_scan, block50Piece04_length]
  rw [scan_append, block50Piece05_scan, block50Piece05_length]
  rw [scan_append, block50Piece06_scan, block50Piece06_length]
  rw [block50Piece07_scan]
  all_goals rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block50_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
