import S008.OccupiedBank

namespace S008.OccupiedBank

/-- Order within a leading prefix: complete roles, each with its occupied suffix. -/
def roleRow (roles slot payload : ℕ) : List Bool :=
  List.replicate (slot*payload) false ++ List.replicate payload true ++
    List.replicate ((roles-1-slot)*payload) false

def roleMarks (prefixes roles slot payload : ℕ) : List Bool :=
  (List.replicate prefixes (roleRow roles slot payload)).flatten

def marked (marks : List Bool) (j : ℕ) := marks[j]?.getD false

private theorem rank_cons (x : Bool) (xs : List Bool) (n : ℕ) :
    rank (marked (x::xs)) (n+1) = (if x then 1 else 0)+rank (marked xs) n := by
  induction n with
  | zero => simp [rank,marked]
  | succ n ih =>
    rw [rank, ih]
    simp [rank,marked,Nat.add_assoc]
    rfl

private theorem rank_count (xs : List Bool) : rank (marked xs) xs.length = xs.count true := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    rw [List.length_cons,rank_cons,ih]
    cases x <;> simp [Nat.add_comm]

/-- A role dispersed across leading prefixes has exactly a 1/roles share.
    This counts occupied zero bits too. -/
theorem occupied_role (prefixes roles slot payload : ℕ) (valid : slot<roles) :
    let marks := roleMarks prefixes roles slot payload
    marks.length = prefixes*roles*payload ∧
    rank (marked marks) marks.length = prefixes*payload := by
  intro marks
  have hrow : (roleRow roles slot payload).length = roles*payload := by
    simp only [roleRow,List.length_append,List.length_replicate]
    have h : slot+1+(roles-1-slot)=roles := by omega
    rw [←h] at ⊢
    simp [Nat.add_mul]
  have hcount : (roleRow roles slot payload).count true = payload := by simp [roleRow,List.count_replicate]
  change (roleMarks prefixes roles slot payload).length = _ ∧ _
  rw [rank_count]
  induction prefixes with
  | zero => simp [marks,roleMarks]
  | succ d ih =>
    have lens := ih.1
    have cnt := ih.2
    change (roleMarks d roles slot payload).count true = d*payload at cnt
    simp only [marks,roleMarks,List.replicate_succ,List.flatten_cons,List.length_append,
      List.count_append,hrow,hcount]
    change _ + (roleMarks d roles slot payload).length = _ ∧ _ + (roleMarks d roles slot payload).count true = _
    rw [lens,cnt]
    constructor <;> ring

end S008.OccupiedBank
