import OAI.Computability.NearSquareRoot.VisitedCells

/-! Physical submachine installation, sequential returns, and exact visited sets
    under the original multitape rule and deterministic exact-step trace. -/

namespace S008.Composition

open OAI.Computability.IntegerMultiplication OAI.Computability.NearSquareRoot
theorem same_stay {A : Type} (t : TM.Tape A) : t.apply (t.view 0,TM.Move.stay) = t := by
  cases t with
  | mk p view =>
    unfold TM.Tape.apply TM.Move.shift
    simp
    funext i
    by_cases h : i=0 <;> simp [h]

theorem prefix_exists {X : Type} {f : X → Option X} {c d : X} {n u : ℕ}
    (tr : Trace f c n d) (hu : u≤n) : ∃ w, Trace f c u w := by
  induction tr generalizing u with
  | nil c =>
    have eq : u=0 := by omega
    subst u
    exact ⟨c,.nil _⟩
  | @cons x w z k hx tail ih =>
    cases u with
    | zero => exact ⟨x,.nil _⟩
    | succ v =>
      obtain ⟨e,hv⟩ := ih (u:=v) (by omega)
      exact ⟨e,by simpa [Nat.add_comm] using Trace.cons hx hv⟩

variable {A Q I J Q₁ Q₂ : Type}

def ambient (m : TM.Rule A Q I) : TM.Rule A Q (I ⊕ J) :=
  fun q reads => (m q (fun i => reads (.inl i))).map fun step =>
    (step.1,fun bank => match bank with
      | .inl i => step.2 i
      | .inr j => (reads (.inr j),.stay))

def put (parked : J → TM.Tape A) (c : TM.Config A Q I) : TM.Config A Q (I ⊕ J) :=
  ⟨c.pc,Sum.elim c.tape parked⟩

theorem ambient_advance (m : TM.Rule A Q I) (parked : J → TM.Tape A) (c : TM.Config A Q I) :
    TM.advance (ambient m) (put parked c)=(TM.advance m c).map (put parked) := by
  unfold TM.advance ambient
  change (((m c.pc (fun i => (c.tape i).view 0)).map _).map _)=_
  cases h : m c.pc (fun i => (c.tape i).view 0) with
  | none => rfl
  | some step =>
    rcases step with ⟨q,ops⟩
    apply congrArg some
    apply congrArg (TM.Config.mk q)
    funext i
    cases i with
    | inl i => rfl
    | inr j => exact same_stay (parked j)

theorem ambient_trace (m : TM.Rule A Q I) (parked : J → TM.Tape A) {x y : TM.Config A Q I}
    {n : ℕ} (h : Trace (TM.advance m) x n y) :
    Trace (TM.advance (ambient m)) (put parked x) n (put parked y) := by
  induction h with
  | nil x => exact .nil _
  | @cons x w y t hx _ ih =>
    have e := ambient_advance m parked x
    rw [hx] at e
    exact .cons e ih

theorem ambient_halt (m : TM.Rule A Q I) (parked : J → TM.Tape A) (y : TM.Config A Q I)
    (h : TM.advance m y=none) : TM.advance (ambient m) (put parked y)=none := by
  rw [ambient_advance,h]
  rfl

private def leftCell {I J : Type} (p : I × ℤ) : (I ⊕ J) × ℤ := (.inl p.1,p.2)
private def rightCell {I J A : Type} (parked : J → TM.Tape A) (j : J) : (I ⊕ J) × ℤ :=
  (.inr j,(parked j).pos)

theorem ambient_set (m : TM.Rule A Q I) (parked : J → TM.Tape A) {x y : TM.Config A Q I}
    {n : ℕ} (h : Trace (TM.advance m) x n y) :
    visitedCells (ambient m) (put parked x) n =
      (leftCell '' visitedCells m x n) ∪ Set.range (rightCell parked) := by
  ext ⟨t,z⟩
  constructor
  · rintro ⟨u,hu,e,he,pos⟩
    obtain ⟨w,hw⟩ := prefix_exists h hu
    have ee := trace_endpoint_unique he (ambient_trace m parked hw)
    subst e
    cases t with
    | inl i =>
      exact Or.inl ⟨(i,z),⟨u,hu,w,hw,pos⟩,rfl⟩
    | inr j =>
      right
      exact ⟨j,Prod.ext rfl pos⟩
  · rintro (⟨⟨i,p⟩,⟨u,hu,w,hw,ep⟩,hit⟩ | ⟨j,hit⟩)
    · cases hit
      exact ⟨u,hu,put parked w,ambient_trace m parked hw,ep⟩
    · cases hit
      exact ⟨0,Nat.zero_le _,_,.nil _,rfl⟩

theorem ambient_card [Finite I] [Fintype J] (m : TM.Rule A Q I) (parked : J → TM.Tape A)
    {x y : TM.Config A Q I} {n : ℕ} (h : Trace (TM.advance m) x n y) :
    (visitedCells (ambient m) (put parked x) n).ncard=
      (visitedCells m x n).ncard + Fintype.card J := by
  have il : Function.Injective (leftCell (I:=I) (J:=J)) := by
    rintro ⟨a,b⟩ ⟨c,d⟩ e
    have ac : Sum.inl (β:=J) a=Sum.inl c := congrArg Prod.fst e
    exact Prod.ext (Sum.inl.inj ac) (congrArg (fun y : (I ⊕ J) × ℤ => y.2) e)
  have ir : Function.Injective (rightCell (I:=I) parked) := by
    intro a b e
    exact Sum.inr.inj (congrArg Prod.fst e)
  have sep : Disjoint (leftCell '' visitedCells m x n) (Set.range (rightCell (I:=I) parked)) := by
    apply Set.disjoint_left.mpr
    rintro z ⟨a,_,rfl⟩ ⟨b,hb⟩
    have wrong : Sum.inr (α:=I) b=Sum.inl a.1 := congrArg Prod.fst hb
    contradiction
  rw [ambient_set m parked h,Set.ncard_union_eq sep ((visitedCells_finite m x n).image _) (Set.finite_range _),
    Set.ncard_image_of_injective _ il,Set.ncard_range_of_injective ir,Nat.card_eq_fintype_card]

def sequential (first : TM.Rule A Q₁ I) (second : TM.Rule A Q₂ I) (entry : Q₁ → Q₂) :
    TM.Rule A (Q₁ ⊕ Q₂) I :=
  fun q reads => match q with
    | .inl pc =>
      match first pc reads with
      | some z => some (.inl z.1,z.2)
      | none => some (.inr (entry pc),fun i => (reads i,.stay))
    | .inr pc => (second pc reads).map (fun z => (.inr z.1,z.2))

def leftCfg {Q₂ : Type} (c : TM.Config A Q₁ I) : TM.Config A (Q₁ ⊕ Q₂) I := ⟨.inl c.pc,c.tape⟩
def rightCfg {Q₁ : Type} (c : TM.Config A Q₂ I) : TM.Config A (Q₁ ⊕ Q₂) I := ⟨.inr c.pc,c.tape⟩
def enter (entry : Q₁ → Q₂) (c : TM.Config A Q₁ I) : TM.Config A Q₂ I := ⟨entry c.pc,c.tape⟩

theorem left_trace (m : TM.Rule A Q₁ I) (nxt : TM.Rule A Q₂ I) (entry : Q₁ → Q₂)
    {x y : TM.Config A Q₁ I} {u : ℕ} (tr : Trace (TM.advance m) x u y) :
    Trace (TM.advance (sequential m nxt entry)) (leftCfg x) u (leftCfg y) := by
  induction tr with
  | nil x => exact .nil _
  | @cons x w y n h _ ih =>
    apply Trace.cons _ ih
    unfold TM.advance at h ⊢
    cases p : m x.pc (fun i => (x.tape i).view 0) with
    | none => rw [p] at h; contradiction
    | some o =>
      rw [p] at h
      cases h
      simp [sequential,leftCfg,p]

theorem switch (m : TM.Rule A Q₁ I) (nxt : TM.Rule A Q₂ I) (entry : Q₁ → Q₂)
    (c : TM.Config A Q₁ I) (stop : TM.advance m c=none) :
    TM.advance (sequential m nxt entry) (leftCfg c)=some (rightCfg (enter entry c)) := by
  have done : m c.pc (fun i => (c.tape i).view 0)=none := by simpa [TM.advance] using stop
  simp [TM.advance,sequential,leftCfg,rightCfg,enter,done,same_stay]

theorem right_advance (m : TM.Rule A Q₁ I) (nxt : TM.Rule A Q₂ I) (entry : Q₁ → Q₂)
    (c : TM.Config A Q₂ I) :
    TM.advance (sequential m nxt entry) (rightCfg c)=(TM.advance nxt c).map rightCfg := by
  unfold TM.advance
  change (((nxt c.pc (fun i => (c.tape i).view 0)).map _).map _)=_
  cases n : nxt c.pc (fun i => (c.tape i).view 0) <;> rfl

theorem right_trace (m : TM.Rule A Q₁ I) (nxt : TM.Rule A Q₂ I) (entry : Q₁ → Q₂)
    {x y : TM.Config A Q₂ I} {u : ℕ} (tr : Trace (TM.advance nxt) x u y) :
    Trace (TM.advance (sequential m nxt entry)) (rightCfg x) u (rightCfg y) := by
  induction tr with
  | nil x => exact .nil _
  | @cons x w y n h _ ih =>
    have e := right_advance m nxt entry x
    rw [h] at e
    exact .cons e ih

theorem full_trace (m : TM.Rule A Q₁ I) (nxt : TM.Rule A Q₂ I) (entry : Q₁ → Q₂)
    {x first : TM.Config A Q₁ I} {last : TM.Config A Q₂ I} {n k : ℕ}
    (t₁ : Trace (TM.advance m) x n first) (stop : TM.advance m first=none)
    (t₂ : Trace (TM.advance nxt) (enter entry first) k last) :
    Trace (TM.advance (sequential m nxt entry)) (leftCfg x) (n+1+k) (rightCfg last) :=
  ((left_trace m nxt entry t₁).trans (.single (switch m nxt entry first stop))).trans (right_trace m nxt entry t₂)

/-- The one stationary inter-procedure return has no additional cell beyond those
    already occupied at the interface, even on repeated scratch-bank reuse. -/
theorem full_visited (m : TM.Rule A Q₁ I) (nxt : TM.Rule A Q₂ I) (entry : Q₁ → Q₂)
    {x first : TM.Config A Q₁ I} {last : TM.Config A Q₂ I} {n k : ℕ}
    (t₁ : Trace (TM.advance m) x n first) (stop : TM.advance m first=none)
    (t₂ : Trace (TM.advance nxt) (enter entry first) k last) :
    visitedCells (sequential m nxt entry) (leftCfg x) (n+1+k)=
      visitedCells m x n ∪ visitedCells nxt (enter entry first) k := by
  have pre := (left_trace m nxt entry t₁).trans (.single (switch m nxt entry first stop))
  ext ⟨i,z⟩
  constructor
  · rintro ⟨u,hu,w,hw,hp⟩
    by_cases early : u≤n
    · obtain ⟨d,hd⟩ := prefix_exists t₁ early
      have same := trace_endpoint_unique hw (left_trace m nxt entry hd)
      subst w
      exact Or.inl ⟨u,early,d,hd,hp⟩
    · let j := u-(n+1)
      have bound : j≤k := by dsimp [j]; omega
      have total : n+1+j=u := by dsimp [j]; omega
      obtain ⟨d,hd⟩ := prefix_exists t₂ bound
      have joined := pre.trans (right_trace m nxt entry hd)
      rw [total] at joined
      have same := trace_endpoint_unique hw joined
      subst w
      exact Or.inr ⟨j,bound,d,hd,hp⟩
  · rintro (⟨u,hu,w,hw,hp⟩ | ⟨j,hj,w,hw,hp⟩)
    · exact ⟨u,by omega,leftCfg w,left_trace m nxt entry hw,hp⟩
    · exact ⟨n+1+j,by omega,rightCfg w,pre.trans (right_trace m nxt entry hw),hp⟩

end S008.Composition
