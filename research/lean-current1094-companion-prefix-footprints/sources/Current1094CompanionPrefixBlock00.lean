import Current1094CompanionPrefixCore

/-! UNCOMPILED block split. All data and finite statements are exact ec2bc862
preimages; The proof-only repair adds symbolic passive-run elimination without changing data. -/
set_option Elab.async false
namespace CurrentMain.Current1094CompanionPrefixSkeleton
open CurrentMain.Current1094Helper450RelabelSlice

def block00 : List Mark :=
  [.phase "zero_frame_precondition"] ++
  List.replicate 255 Mark.passive

#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block00

/-- Symbolic elimination of an arbitrarily long passive run; no linear
unfolding of the concrete255-row run is required. Reusable by later blocks. -/
theorem scan_passive (n k : Nat) :
    scanFrom n (List.replicate k Mark.passive) = [] := by
  induction k generalizing n with
  | zero => rfl
  | succ k ih =>
      simpa [List.replicate_succ, scanFrom, tracked, labelTracked] using ih (n+1)
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.scan_passive

theorem block00_length : block00.length = 256 := by
  simp only [block00, List.length_append, List.length_cons, List.length_nil, List.length_replicate]
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block00_length
theorem block00_scan : scanFrom 0 block00 =
    [(0, .phase "zero_frame_precondition")] := by
  rw [block00, scan_append, scan_passive]
  rfl
#print axioms CurrentMain.Current1094CompanionPrefixSkeleton.block00_scan

end CurrentMain.Current1094CompanionPrefixSkeleton
