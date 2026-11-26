import S008.OccupiedBank

namespace S008.OccupiedBank

open OAI.Computability.IntegerMultiplication OAI.Computability.NearSquareRoot
open S008.Compiler (Letter)
open S008.Composition

private theorem parent_unchanged (sel : ℕ → Bool) (b : Banks) (N : ℕ) :
    (fill false sel b N).parent = b.parent := by
  induction N with
  | zero => rfl
  | succ n ih => cases h : sel n <;> simpa [fill,takeBit,h] using ih

theorem gather_parent (sel : ℕ → Bool) (b : Banks) (N : ℕ) :
    (output false sel N b).parent = b.parent := parent_unchanged sel b N

private theorem untouched (s : Bool) (sel : ℕ → Bool) (b : Banks) (j : ℕ) (z : ℤ)
    (out : z < 0 ∨ (rank sel j : ℤ) ≤ z) : (fill s sel b j).dense z = b.dense z := by
  induction j with
  | zero => rfl
  | succ j ih =>
    have old : rank sel j ≤ rank sel (j+1) := rank_mono sel (Nat.le_succ j)
    have eqv := ih (by omega)
    cases h : sel j
    · simpa [fill,takeBit,h] using eqv
    · have hr : z ≠ (rank sel j:ℤ) := by simp [rank,h] at out; omega
      cases s <;> simpa [fill,takeBit,h,Function.update_of_ne hr] using eqv

/-- Each marked parent bit ends at its prefix rank, in order. -/
theorem gather_bit (sel : ℕ → Bool) (b : Banks) {i N : ℕ} (hi : i<N) (pick : sel i=true) :
    (output false sel N b).dense (rank sel i) = b.parent i := by
  have strict (m : ℕ) (hm : i<m) : rank sel i < rank sel m := by
    have later := rank_mono sel (show i+1 ≤ m by omega)
    simp [rank,pick] at later
    omega
  have stable : (fill false sel b N).dense (rank sel i) = b.parent i := by
    induction N with
    | zero => omega
    | succ N ih =>
      by_cases eqv : i=N
      · subst N
        simp [fill,takeBit,pick,parent_unchanged]
      · have earlier : i<N := by omega
        have he : (rank sel i:ℤ) ≠ ↑(rank sel N) := by exact_mod_cast (strict N earlier).ne
        cases h : sel N <;> simpa [fill,takeBit,h,Function.update_of_ne he] using ih earlier
  have he : (rank sel i:ℤ) ≠ ↑(rank sel N) := by exact_mod_cast (strict N hi).ne
  simpa [output,Function.update_of_ne he] using stable

theorem gather_delimiter (sel : ℕ → Bool) (b : Banks) (N : ℕ) :
    (output false sel N b).dense (rank sel N) = .delimiter := by simp [output]

/-- Scatter reads the child's returned word at the matching dense coordinate.
    Unmarked bits and both exterior half-lines of the parent keep their contents. -/
theorem scatter_cell (sel : ℕ → Bool) (b : Banks) (N : ℕ) (z : ℤ) :
    (output true sel N b).parent z =
      if 0≤z ∧ z<N ∧ sel z.toNat=true then b.dense (rank sel z.toNat) else b.parent z := by
  change (fill true sel b N).parent z = _
  induction N with
  | zero => simp [fill]; omega
  | succ j ih =>
    by_cases hz : z=(j:ℤ)
    · subst z
      cases h : sel j
      · simpa [fill,takeBit,h] using ih
      · simp [fill,takeBit,h,untouched true sel b j _ (Or.inr (le_refl _))]
    · have hlt : z < ((j+1:ℕ):ℤ) ↔ z < (j:ℤ) := by omega
      cases h : sel j <;>
        simpa only [fill,takeBit,h,Bool.false_eq_true,ite_false,ite_true,Function.update_of_ne hz,hlt] using ih

theorem scratch_after_scatter (sel : ℕ → Bool) (b : Banks) (N : ℕ) (z : ℤ) :
    (output true sel N b).dense z =
      if 0≤z ∧ z≤(rank sel N:ℤ) then .blank else b.dense z := by
  suffices parts : (fill true sel b N).dense z =
      if 0≤z ∧ z<(rank sel N:ℤ) then .blank else b.dense z by
    by_cases h : z=(rank sel N:ℤ)
    · subst z; simp [output]
    · have same : z≤(rank sel N:ℤ) ↔ z<(rank sel N:ℤ) := by omega
      simpa [output,Function.update_of_ne h,same] using parts
  induction N with
  | zero => simp [fill,rank]
  | succ n ih =>
    cases h : sel n
    · simpa [fill,takeBit,h,rank] using ih
    · by_cases hz : z=(rank sel n:ℤ)
      · subst z; simp [fill,takeBit,h,rank]
      · have eqv : z<((rank sel n+1:ℕ):ℤ) ↔ z<(rank sel n:ℤ) := by omega
        simpa only [fill,takeBit,h,rank,ite_true,Function.update_of_ne hz,eqv] using ih

variable {I Q : Type}
abbrev Child (I Q : Type) := TM.Rule Letter Q (Option I)

def childFrame (q : Q) (dense : Word) (aux : I → TM.Tape Letter) :
    TM.Config Letter Q (Option I) :=
  ⟨q,fun | none => atHead dense 0 | some i => aux i⟩

def parked (N : ℕ) (sel : ℕ → Bool) (parent : Word) : Bool → TM.Tape Letter
  | false => atHead (mask N sel) 0
  | true => atHead parent 0

/-- Child tapes include precisely one compact interface and a fixed set of private heads. -/
def called (m : Child I Q) (entry : Q) :=
  sequential (rule (I:=I) false) (sequential (ambient (J:=Bool) m) (rule true)
    (fun _ => Phase.scan)) (fun _ => entry |> Sum.inl)

def initial (N : ℕ) (sel : ℕ → Bool) (b : Banks) (aux : I → TM.Tape Letter) (Q : Type) :
    TM.Config Letter (Phase ⊕ (Q ⊕ Phase)) (Port I) := leftCfg (frame N sel b aux .scan 0 0)

def returned (N : ℕ) (sel : ℕ → Bool) (b : Banks) (aux : I → TM.Tape Letter) (Q : Type) :
    TM.Config Letter (Phase ⊕ (Q ⊕ Phase)) (Port I) :=
  rightCfg (rightCfg (frame N sel (output true sel N b) aux .done 0 0))

/-- Exact time and visited set of one gather, a single child run and one scatter.
    The two stationary phase changes each cost a transition. -/
theorem round_trip (m : Child I Q) (entry exitState : Q) (N : ℕ) (sel : ℕ → Bool)
    (b : Banks) (result : Word) (aux aux' : I → TM.Tape Letter) (k : ℕ)
    (child : Trace (TM.advance m) (childFrame entry (output false sel N b).dense aux) k
      (childFrame exitState result aux'))
    (halt : TM.advance m (childFrame exitState result aux')=none) :
    let start := initial N sel b aux Q
    let after : Banks := ⟨b.parent,result⟩
    let active := childFrame entry (output false sel N b).dense aux
    Trace (TM.advance (called m entry)) start (4*N+6+k) (returned N sel after aux' Q) ∧
      visitedCells (called m entry) start (4*N+6+k) ⊆
        zone N (rank sel N) aux ∪
        ((fun p : Option I × ℤ => (Sum.inl p.1,p.2)) '' visitedCells m active k) ∪
        zone N (rank sel N) aux' := by
  intro start after active
  let p := parked N sel b.parent
  let loadEnd := frame N sel (output false sel N b) aux .done 0 0
  let storeStart := frame N sel after aux' .scan 0 0
  let storeEnd := frame N sel (output true sel N after) aux' .done 0 0
  let kid := ambient (J:=Bool) m
  let mid := sequential kid (rule true) (fun _ => Phase.scan)
  have gather := transfer false N sel aux b
  have store := transfer true N sel aux' after
  have loadStop : TM.advance (rule false) loadEnd=none := rfl
  have childTrace := ambient_trace m p child
  have childStop := ambient_halt m p _ halt
  have storeEntry : enter (fun _ => Phase.scan) (put p (childFrame exitState result aux'))=storeStart := by
    apply congrArg (TM.Config.mk Phase.scan)
    funext i
    rcases i with (_ | i) | (_ | _) <;> rfl
  have storeRun : Trace (TM.advance (rule true))
      (enter (fun _ => Phase.scan) (put p (childFrame exitState result aux'))) (2*N+2) storeEnd := by
    rw [storeEntry]; exact store.1
  have middle := full_trace kid (rule true) (fun _ => Phase.scan) childTrace childStop storeRun
  have innerSet := full_visited kid (rule true) (fun _ => Phase.scan) childTrace childStop storeRun
  have loadEntry : enter (fun _ : Phase => Sum.inl (β:=Phase) entry) loadEnd =
      leftCfg (put p active) := by
    apply congrArg (TM.Config.mk (A:=Letter) (I:=Port I) (Sum.inl (β:=Phase) entry))
    funext i
    rcases i with (_ | i) | (_ | _)
    · rfl
    · rfl
    · rfl
    · change atHead (output false sel N b).parent 0 = atHead b.parent 0
      rw [gather_parent]
  rw [← loadEntry] at middle
  have all := full_trace (rule false) mid _ gather.1 loadStop middle
  have both := full_visited (rule false) mid _ gather.1 loadStop middle
  have eqTime : 2*N+2+1+(k+1+(2*N+2))=4*N+6+k := by omega
  rw [eqTime] at all both
  refine ⟨all,?_⟩
  rw [show visitedCells (called m entry) start (4*N+6+k) = _ from both,loadEntry,innerSet,
    storeEntry,ambient_set m p child]
  intro v h
  rcases h with h | ((h | h) | h)
  · exact Or.inl (Or.inl (gather.2 h))
  · exact Or.inl (Or.inr h)
  · obtain ⟨i,rfl⟩ := h
    apply Or.inl ∘ Or.inl
    cases i <;> change -1 ≤ (0:ℤ) ∧ (0:ℤ) ≤ N <;> omega
  · exact Or.inr (store.2 h)

end S008.OccupiedBank
