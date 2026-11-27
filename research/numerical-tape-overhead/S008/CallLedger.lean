import S008.BankReturn

namespace S008.OccupiedBank

open OAI.Computability.IntegerMultiplication OAI.Computability.NearSquareRoot
open S008.Compiler (Letter)

/-- One occupied call in a serial schedule. Repetitions are separate list entries.
    The child runs on exactly the gathered word and returns to the compact origin. -/
structure Call (I Q : Type) (m : Child I Q) (entry : Q) where
  width : ℕ
  select : ℕ → Bool
  bank : Banks
  before : I → TM.Tape Letter
  after : I → TM.Tape Letter
  result : Word
  exitState : Q
  ticks : ℕ
  run : Trace (TM.advance m) (childFrame entry (output false select width bank).dense before)
    ticks (childFrame exitState result after)
  halt : TM.advance m (childFrame exitState result after)=none

namespace Call

variable {I Q : Type} {m : Child I Q} {entry : Q}

def overhead (c : Call I Q m entry) := 4*c.width+6
def steps (c : Call I Q m entry) := c.overhead+c.ticks
def visits (c : Call I Q m entry) := visitedCells (called m entry) (initial c.width c.select c.bank c.before Q) c.steps
def childVisits (c : Call I Q m entry) := visitedCells m
  (childFrame entry (output false c.select c.width c.bank).dense c.before) c.ticks

theorem halting (c : Call I Q m entry) :
    let done := returned c.width c.select ⟨c.bank.parent,c.result⟩ c.after Q
    Trace (TM.advance (called m entry)) (initial c.width c.select c.bank c.before Q) c.steps done ∧
      TM.advance (called m entry) done = none :=
  ⟨(round_trip m entry c.exitState c.width c.select c.bank c.result c.before c.after c.ticks c.run c.halt).1,rfl⟩

theorem total_steps (calls : List (Call I Q m entry)) :
    (calls.map steps).sum = (calls.map overhead).sum + (calls.map ticks).sum := by
  induction calls with
  | nil => rfl
  | cons c cs ih => simp [steps,List.sum_cons,ih,Nat.add_assoc,Nat.add_left_comm,Nat.add_comm]

def lower (lo : Option I → ℤ) : Port I → ℤ := Sum.elim lo (fun _ => -1)
def upper (W : ℕ) (hi : Option I → ℤ) : Port I → ℤ := Sum.elim hi (fun _ => W)

private theorem entry_visit (c : Call I Q m entry) (i : I) : (some i,(c.before i).pos) ∈ c.childVisits :=
  ⟨0,Nat.zero_le _,_,.nil _,rfl⟩

private theorem exit_visit (c : Call I Q m entry) (i : I) : (some i,(c.after i).pos) ∈ c.childVisits :=
  ⟨c.ticks,le_refl _,_,c.run,rfl⟩

/-- One union over all invocations, measured in absolute tape/address pairs.
    Per-head fences can attain their maxima in different calls. -/
theorem repeated_visits [Fintype I] (calls : List (Call I Q m entry)) (W : ℕ)
    (lo hi : Option I → ℤ) (home : lo none ≤ 0)
    (widths : ∀ c ∈ calls, c.width ≤ W ∧ (rank c.select c.width:ℤ) ≤ hi none)
    (children : ∀ c ∈ calls, ∀ p ∈ c.childVisits, lo p.1 ≤ p.2 ∧ p.2 ≤ hi p.1) :
    ∃ cells : Finset (Port I × ℤ),
      cells.card ≤ ∑ i : Port I, (upper W hi i + 1 - lower lo i).toNat ∧
      ∀ c ∈ calls, c.visits ⊆ (cells : Set (Port I × ℤ)) := by
  classical
  let strip (i : Port I) := (Finset.Icc (lower lo i) (upper W hi i)).map (Function.Embedding.sectR i ℤ)
  refine ⟨Finset.univ.biUnion strip, ?_, ?_⟩
  · simpa [strip,Int.card_Icc] using (Finset.card_biUnion_le (s:=Finset.univ) (t:=strip))
  intro c hc v hv
  obtain ⟨hw,hk⟩ := widths c hc
  have liftZone (aux : I → TM.Tape Letter)
      (haux : ∀ i, (some i,(aux i).pos) ∈ c.childVisits)
      (j : Port I) (z : ℤ) (h : (j,z) ∈ zone c.width (rank c.select c.width) aux) :
      lower lo j ≤ z ∧ z ≤ upper W hi j := by
    rcases j with (_ | i) | p
    · exact ⟨home.trans h.1,h.2.trans hk⟩
    · change z=(aux i).pos at h
      subst z
      exact children c hc _ (haux i)
    · exact ⟨h.1,h.2.trans (show (c.width:ℤ) ≤ W by exact_mod_cast hw)⟩
  have h := (round_trip m entry c.exitState c.width c.select c.bank c.result c.before c.after
    c.ticks c.run c.halt).2 hv
  obtain ⟨j,z⟩ := v
  apply Finset.mem_biUnion.mpr
  refine ⟨j,Finset.mem_univ _,Finset.mem_map.mpr ⟨z,Finset.mem_Icc.mpr ?_,rfl⟩⟩
  rcases h with (h | ⟨⟨i,x⟩,h,e⟩) | h
  · exact liftZone _ c.entry_visit _ _ h
  · cases e
    exact children c hc _ h
  · exact liftZone _ c.exit_visit _ _ h

end Call
end S008.OccupiedBank
