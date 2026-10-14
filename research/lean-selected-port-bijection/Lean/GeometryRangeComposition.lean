import GeometryAuxiliary
namespace CurrentMain.ComplexGeometry

theorem rangeCheck_append (p : Nat → Bool) (start left right : Nat) :
    rangeCheck p start (left+right)=
      (rangeCheck p start left && rangeCheck p (start+left) right) := by
  induction left generalizing start with
  | zero => simp [rangeCheck]
  | succ left ih =>
    simp only [Nat.succ_add,rangeCheck,ih,Bool.and_assoc]
    congr 2

theorem rangeCheck_join (p : Nat → Bool) (start left right : Nat)
    (lc : rangeCheck p start left=true)
    (rc : rangeCheck p (start+left) right=true) :
    rangeCheck p start (left+right)=true := by
  rw [rangeCheck_append,lc,rc]
  rfl

end CurrentMain.ComplexGeometry
#print axioms CurrentMain.ComplexGeometry.rangeCheck_append
#print axioms CurrentMain.ComplexGeometry.rangeCheck_join
