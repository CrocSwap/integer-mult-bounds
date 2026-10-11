import ComplexBinarySpan
namespace CurrentMain.BinaryFrame

def Independent : List Nat → Prop
  | [] => True
  | b :: bs => Independent bs ∧ ¬ Span bs b

def pivotCheck : List Nat → List Nat → Bool
  | [], [] => true
  | b :: bs, p :: ps => b.testBit p &&
      (bs.all (fun x => !(x.testBit p)) && pivotCheck bs ps)
  | _, _ => false

theorem pivotCheck_sound (rows pivots : List Nat)
    (checked : pivotCheck rows pivots = true) : Independent rows := by
  induction rows generalizing pivots with
  | nil => trivial
  | cons b bs ih =>
    cases pivots with
    | nil => simp [pivotCheck] at checked
    | cons p ps =>
      have hc := Bool.and_eq_true_iff.mp checked
      have ht := Bool.and_eq_true_iff.mp hc.2
      refine ⟨ih ps ht.2, ?_⟩
      intro member
      have zero : ∀ x ∈ bs, x.testBit p = false := by
        intro x hx
        simpa using List.all_eq_true.mp ht.1 x hx
      have contra := span_bit_zero bs p zero b member
      rw [hc.1] at contra
      contradiction

theorem pivotCheck_length (rows pivots : List Nat)
    (checked : pivotCheck rows pivots = true) : rows.length = pivots.length := by
  induction rows generalizing pivots with
  | nil => cases pivots <;> simp_all [pivotCheck]
  | cons b bs ih =>
    cases pivots with
    | nil => simp [pivotCheck] at checked
    | cons p ps =>
      have hc := Bool.and_eq_true_iff.mp checked
      have ht := Bool.and_eq_true_iff.mp hc.2
      simpa using congrArg Nat.succ (ih ps ht.2)

end CurrentMain.BinaryFrame
#print axioms CurrentMain.BinaryFrame.pivotCheck_sound
#print axioms CurrentMain.BinaryFrame.pivotCheck_length
