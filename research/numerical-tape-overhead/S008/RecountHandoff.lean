import OAI.Computability.NearSquareRoot.VisitedCells

/-! Exact traces for the neutral data-bank transfer in the S008 recursive handoff. -/

namespace S008.Recount

open OAI.Computability.IntegerMultiplication

inductive Letter where
  | blank | left | right | bit (b : Bool) | marked (b : Bool)
  | parkLeft | parkInside | parkRight | bottom | retContract | retFull
  deriving DecidableEq, Repr, Inhabited

open Letter

instance : Fintype Letter :=
  Fintype.ofList [blank,left,right,bit false,bit true,marked false,marked true,
    parkLeft,parkInside,parkRight,bottom,retContract,retFull] (by
      intro x
      cases x with
      | bit b => cases b <;> decide
      | marked b => cases b <;> decide
      | _ => decide)

/-- A finite window, with the rest of the tape implicitly blank. `pre` lists
    the left neighbors nearest first. `post` begins at the current cell. -/
structure Window where
  pos : ℤ
  pre : List Letter
  post : List Letter
  deriving Repr

namespace Window

def cell (a b : List Letter) : ℤ → Letter
  | .ofNat i => b[i]?.getD blank
  | .negSucc i => a[i]?.getD blank

def physical (w : Window) : TM.Tape Letter := ⟨w.pos, cell w.pre w.post⟩

def atHead (w : Window) : Letter := w.post.headD blank

def apply (w : Window) (sym : Letter) (mv : TM.Move) : Window :=
  match mv with
  | .stay => ⟨w.pos, w.pre, sym :: w.post.tail⟩
  | .right => ⟨w.pos+1, sym :: w.pre, w.post.tail⟩
  | .left => ⟨w.pos-1, w.pre.tail, w.pre.headD blank :: sym :: w.post.tail⟩

@[simp] theorem read_physical (w : Window) : w.physical.view 0 = w.atHead := by
  cases w with
  | mk p a b => cases b <;> rfl

private theorem tail_get (xs : List Letter) (n : ℕ) :
    xs.tail[n]? = xs[n+1]? := by cases xs <;> simp

private theorem zero_get (xs : List Letter) :
    xs[0]?.getD blank = xs.headD blank := by cases xs <;> rfl

private theorem tape_ext {t z : TM.Tape Letter} (h : t.pos = z.pos) (h' : ∀ i, t.view i = z.view i) : t = z := by
  cases t with
  | mk a f =>
    cases z with
    | mk b g =>
      dsimp at h h'
      subst b
      exact congrArg (TM.Tape.mk a) (funext h')

private theorem of_add (n : ℕ) : Int.ofNat n + 1 = Int.ofNat (n+1) := rfl
private theorem neg_add (n : ℕ) : Int.negSucc (n+1) + 1 = Int.negSucc n := by omega
private theorem pos_nz (n : ℕ) : Int.ofNat (n+1) ≠ 0 :=
  fun h => Nat.succ_ne_zero _ (Int.ofNat.inj h)
private theorem of_sub (n : ℕ) : Int.ofNat (n+1) + (-1) = Int.ofNat n := by
  rw [← of_add]
  omega
private theorem neg_sub (n : ℕ) : Int.negSucc n + (-1) = Int.negSucc (n+1) := by omega

theorem physical_apply (w : Window) (s : Letter) (m : TM.Move) :
    (w.apply s m).physical = w.physical.apply (s,m) := by
  rcases w with ⟨p,a,b⟩
  apply tape_ext
  · cases m <;> simp [apply, physical, TM.Tape.apply, TM.Move.shift]
    omega
  · intro i
    cases m with
    | stay =>
      change cell a (s :: b.tail) i = if i+0=0 then s else cell a b (i+0)
      simp only [Int.add_zero]
      cases i with
      | ofNat n =>
        cases n with
        | zero => rfl
        | succ n =>
          rw [ite_eq_right (pos_nz _)]
          change b.tail[n]?.getD blank = b[n+1]?.getD blank
          rw [tail_get]
      | negSucc n => rw [ite_eq_right (Int.negSucc_ne_zero _)]; rfl
    | right =>
      change cell (s :: a) b.tail i = if i+1=0 then s else cell a b (i+1)
      cases i with
      | ofNat n =>
        rw [of_add, ite_eq_right (pos_nz _)]
        change b.tail[n]?.getD blank = b[n+1]?.getD blank
        rw [tail_get]
      | negSucc n =>
        cases n with
        | zero => rfl
        | succ n => rw [neg_add, ite_eq_right (Int.negSucc_ne_zero _)]; rfl
    | left =>
      change cell a.tail (a.headD blank :: s :: b.tail) i = if i+(-1)=0 then s else cell a b (i+(-1))
      cases i with
      | ofNat n =>
        cases n with
        | zero => change a.headD blank = a[0]?.getD blank; rw [zero_get]
        | succ n =>
          rw [of_sub]
          cases n with
          | zero => rfl
          | succ n =>
            rw [ite_eq_right (pos_nz _)]
            change b.tail[n]?.getD blank = b[n+1]?.getD blank
            rw [tail_get]
      | negSucc n =>
        rw [neg_sub, ite_eq_right (Int.negSucc_ne_zero _)]
        change a.tail[n]?.getD blank = a[n+1]?.getD blank
        rw [tail_get]

end Window

inductive Phase where
  | start | first | more | back | done
  deriving DecidableEq, Repr

instance : Fintype Phase :=
  Fintype.ofList [.start,.first,.more,.back,.done] (by intro q; cases q <;> decide)

structure State where
  q : Phase
  src : Window
  dst : Window
  deriving Repr

def pick {α : Type} (x y : α) : Bool → α
  | false => x
  | true => y

abbrev Change := (Letter × TM.Move) × (Letter × TM.Move)
abbrev Next := Option (Phase × Change)

/-- Local finite table. False selects the source tape and true the destination. -/
def command (q : Phase) (s d : Letter) : Next :=
  match q with
  | .start => some (.first, (left,.right), (left,.right))
  | .first | .more =>
    match s with
    | .bit b => some (.more, (if q = .first then right else blank,.right), (bit b,.right))
    | .right => some (.back, (if q = .first then right else blank,.left), (right,.left))
    | _ => none
  | .back =>
    if d = left then some (.done,(left,.stay),(left,.stay))
    else some (.back,(s,.left),(d,.left))
  | .done => none

def rule : TM.Rule Letter Phase Bool := fun q scanned =>
  (command q (scanned false) (scanned true)).map fun (p, s, d) => (p, pick s d)

def State.physical (c : State) : TM.Config Letter Phase Bool :=
  ⟨c.q, pick c.src.physical c.dst.physical⟩

def step (c : State) : Option State :=
  (command c.q c.src.atHead c.dst.atHead).map fun (p,s,d) =>
    ⟨p,c.src.apply s.1 s.2,c.dst.apply d.1 d.2⟩

theorem physical_step (c : State) :
    TM.advance rule c.physical = (step c).map State.physical := by
  rcases c with ⟨q,a,b⟩
  simp only [TM.advance, rule, State.physical, pick, Window.read_physical, step]
  cases h : command q a.atHead b.atHead with
  | none => rfl
  | some act =>
    rcases act with ⟨q',sa,da⟩
    simp only [Option.map_some, State.physical]
    congr 1
    congr 1
    funext i
    cases i <;> exact (Window.physical_apply ..).symm

theorem physical_trace {c e : State} {n : ℕ} (h : Trace step c n e) :
    Trace (TM.advance rule) c.physical n e.physical := by
  induction h with
  | nil => exact .nil _
  | cons hstep _ ih =>
    apply Trace.cons _ ih
    rw [physical_step,hstep]
    rfl

def backWindow (p : ℤ) (toward l r : List Letter) : Window :=
  match toward with
  | [] => ⟨p,l,left :: r⟩
  | x :: xs => ⟨p,xs ++ left :: l,x :: r⟩

private theorem back_one (p : ℤ) (x : Letter) (xs l r : List Letter) :
    (backWindow p (x::xs) l r).apply x .left = backWindow (p-1) xs l (x::r) := by
  cases xs <;> rfl

private theorem set_left (p : ℤ) (xs l r : List Letter) (x y : Letter) :
    (Window.mk p (xs ++ left :: l) (x::r)).apply y .left =
      backWindow (p-1) xs l (y::r) := by
  cases xs <;> rfl

private theorem backward (ss : List Letter) (ds : List Bool) (h : ss.length = ds.length)
    (p q : ℤ) (sl dl sr dr : List Letter) :
    Trace step ⟨.back,backWindow p ss sl sr,backWindow q (ds.map bit) dl dr⟩
      (ds.length+1)
      ⟨.done,⟨p-ss.length,sl,left :: (ss.reverse ++ sr)⟩,
             ⟨q-ds.length,dl,left :: (ds.reverse.map bit ++ dr)⟩⟩ := by
  induction ds generalizing ss p q sr dr with
  | nil =>
    have h0 : ss = [] := List.length_eq_zero_iff.mp h
    subst ss
    simp only [List.length_nil, List.map_nil, List.reverse_nil, List.nil_append,
      Int.natCast_zero, sub_zero, Nat.zero_add]
    apply Trace.single
    rfl
  | cons b bs ih =>
    cases ss with
    | nil => simp at h
    | cons a as =>
      have hl : as.length = bs.length := by simpa using h
      let nextState := State.mk .back (backWindow (p-1) as sl (a::sr))
                           (backWindow (q-1) (bs.map bit) dl (bit b::dr))
      have hs : step ⟨.back, backWindow p (a::as) sl sr,
                       backWindow q ((b::bs).map bit) dl dr⟩ = some nextState := by
        show some (State.mk .back ((backWindow p (a::as) sl sr).apply a .left)
          ((backWindow q (bit b :: bs.map bit) dl dr).apply (bit b) .left)) = _
        simp only [back_one,nextState]
      have ht := Trace.cons hs (ih as hl (p-1) (q-1) (a::sr) (bit b::dr))
      simpa [List.reverse_cons,List.append_assoc,Int.sub_sub,Int.add_comm, Nat.add_comm] using ht

private theorem rep_cons (n : ℕ) (x : Letter) (xs : List Letter) :
    List.replicate n x ++ x::xs = x::(List.replicate n x ++ xs) := by
  induction n with
  | zero => rfl
  | succ i ih => simp only [List.replicate_succ, List.cons_append, ih]

private theorem forward (todo : List Bool) (p q : ℤ) (sp dp sr dr : List Letter) :
    Trace step ⟨.more,⟨p,sp,todo.map bit ++ right :: sr⟩,
        ⟨q,dp,List.replicate todo.length blank ++ blank :: dr⟩⟩
      todo.length
      ⟨.more,⟨p+todo.length,List.replicate todo.length blank ++ sp,right :: sr⟩,
        ⟨q+todo.length,todo.reverse.map bit ++ dp,blank :: dr⟩⟩ := by
  induction todo generalizing p q sp dp with
  | nil =>
    simp only [List.map_nil,List.nil_append,List.length_nil,List.replicate_zero,List.reverse_nil,
      Int.natCast_zero,add_zero]
    exact .nil _
  | cons b bs ih =>
    let nextState := State.mk .more ⟨p+1,blank::sp,bs.map bit ++ right::sr⟩
                              ⟨q+1,bit b::dp,List.replicate bs.length blank ++ blank::dr⟩
    have hs : step ⟨.more,⟨p,sp,(b::bs).map bit ++ right :: sr⟩,
                   ⟨q,dp,List.replicate (b::bs).length blank ++ blank :: dr⟩⟩ =
                  some nextState := by
      simp [step, command, Window.atHead, Window.apply, List.replicate_succ, nextState]
    have ht := Trace.cons hs (ih (p+1) (q+1) (blank::sp) (bit b::dp))
    simpa [List.reverse_cons,List.append_assoc,List.replicate_succ,
      rep_cons,Int.add_assoc,Int.add_comm,Int.add_left_comm,Nat.add_comm] using ht

/-- Occupied bank and a free bank with enough blank cells before an arbitrary
    exterior. Origins and exterior symbols are independent on the two tapes. -/
def full (p : ℤ) (l : List Letter) (word : List Bool) (r : List Letter) : Window :=
  ⟨p,l,left::(word.map bit ++ right::r)⟩

def empty (p : ℤ) (l : List Letter) (n : ℕ) (r : List Letter) : Window :=
  ⟨p,l,left :: right :: (List.replicate n blank ++ r)⟩

private theorem run_transfer (word : List Bool) (p q : ℤ) (sl dl sr dr : List Letter) :
    Trace step ⟨.start,full p sl word sr,empty q dl word.length dr⟩
      (2*word.length+3) ⟨.done,empty p sl word.length sr,full q dl word dr⟩ := by
  cases word with
  | nil =>
    let x := State.mk .first ⟨p+1,left::sl,right::sr⟩ ⟨q+1,left::dl,right::dr⟩
    let y := State.mk .back ⟨p,sl,left::right::sr⟩ ⟨q,dl,left::right::dr⟩
    have h1 : step ⟨.start,full p sl [] sr,empty q dl 0 dr⟩ = some x := rfl
    have h2 : step x = some y := by simp [step,x,y,command,Window.atHead,Window.apply]
    have h3 : step y = some ⟨.done,empty p sl 0 sr,full q dl [] dr⟩ := rfl
    exact .cons h1 (.cons h2 (.single h3))
  | cons b bs =>
    let x1 := State.mk .first ⟨p+1,left::sl,bit b::(bs.map bit ++ right::sr)⟩
                         ⟨q+1,left::dl,right::(List.replicate (bs.length+1) blank ++ dr)⟩
    let x2 := State.mk .more ⟨p+2,right::left::sl,bs.map bit ++ right::sr⟩
                 ⟨q+2,bit b::left::dl,List.replicate bs.length blank ++ blank::dr⟩
    have h1 : step ⟨.start, full p sl (b::bs) sr,empty q dl (b::bs).length dr⟩ = some x1 := rfl
    have h2 : step x1 = some x2 := by
      simp [step,x1,x2,command,Window.atHead,Window.apply,List.replicate_succ,rep_cons]
      omega
    let rs := List.replicate bs.length blank ++ [right]
    let rd := (b::bs).reverse
    let ps := p+2+(bs.length : ℤ)
    let pd := q+2+(bs.length : ℤ)
    let x3 := State.mk .more ⟨ps,rs ++ left::sl,right::sr⟩ ⟨pd,rd.map bit ++ left::dl,blank::dr⟩
    have h3 : Trace step x2 bs.length x3 := by
      simpa [x2,x3,ps,pd,rs,rd,List.reverse_cons,List.append_assoc]
        using forward bs (p+2) (q+2) (right::left::sl) (bit b::left::dl) sr dr
    let x4 := State.mk .back (backWindow (ps-1) rs sl (blank::sr))
                              (backWindow (pd-1) (rd.map bit) dl (right::dr))
    have h4 : step x3 = some x4 := by
      show some (State.mk .back ((Window.mk ps (rs ++ left::sl) (right::sr)).apply blank .left)
              ((Window.mk pd (rd.map bit ++ left::dl) (blank::dr)).apply right .left)) = _
      simp only [set_left,x4]
    have hl : rs.length = rd.length := by simp [rs,rd]
    have h5 := backward rs rd hl (ps-1) (pd-1) sl dl (blank::sr) (right::dr)
    have hf := Trace.cons h1 (Trace.cons h2 (h3.trans (Trace.cons h4 h5)))
    have hs : p+2+(bs.length : ℤ)-1-(bs.length+1)=p := by omega
    have hd : q+2+(bs.length : ℤ)-1-(bs.length+1)=q := by omega
    simpa [x4,ps,pd,rs,rd,full,empty,List.replicate_succ,List.append_assoc,
      rep_cons,hs,hd,Nat.two_mul,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using hf

/-- The typed open subroutine used on both sides of a contracted AQ call.
    This is a literal exact trace of an OpenAI deterministic tape rule. -/
theorem neutral_bank_transfer (word : List Bool) (p q : ℤ) (sl dl sr dr : List Letter) :
    Trace (TM.advance rule)
      (State.mk .start (full p sl word sr) (empty q dl word.length dr)).physical
      (2*word.length+3)
      (State.mk .done (empty p sl word.length sr) (full q dl word dr)).physical :=
  physical_trace (run_transfer word p q sl dl sr dr)

theorem neutral_bank_halts (a b : Window) :
    TM.advance rule (State.mk .done a b).physical = none := by
  rw [physical_step]
  rfl

def upward : Phase → Prop
  | .start | .first | .more => True
  | .back | .done => False

def State.position (x : State) (i : Bool) : ℤ := (pick x.src x.dst i).pos

private theorem window_pos (w : Window) (s : Letter) (m : TM.Move) :
    (w.apply s m).pos = w.pos + m.shift := by
  cases m <;> simp [Window.apply, TM.Move.shift]
  omega

private theorem command_motion (q q' : Phase) (s d a b : Letter) (m n : TM.Move)
    (h : command q s d = some (q', (a,m), (b,n))) :
    m = n ∧ (upward q' → upward q ∧ 0 ≤ m.shift) ∧
      (¬upward q → ¬upward q' ∧ m.shift ≤ 0) := by
  cases q <;> cases s <;> by_cases hd : d=left <;> simp [command,hd] at h
  all_goals rcases h with ⟨rfl,⟨rfl,rfl⟩,rfl,rfl⟩
  all_goals simp [upward,TM.Move.shift]

private theorem step_motion {x y : State} (hxy : step x = some y) (i : Bool) :
    ∃ d : ℤ, y.position i = x.position i+d ∧ -1≤d ∧ d≤1 ∧
      (upward y.q → upward x.q ∧ 0≤d) ∧ (¬upward x.q → ¬upward y.q ∧ d≤0) := by
  rcases x with ⟨q,a,b⟩
  cases h : command q a.atHead b.atHead with
  | none => simp [step,h] at hxy
  | some act =>
    rcases act with ⟨q',⟨sa,m⟩,⟨sb,n⟩⟩
    simp [step,h] at hxy
    subst y
    obtain ⟨rfl,hu,hd⟩ := command_motion _ _ _ _ _ _ _ _ h
    refine ⟨m.shift,?_,?_,?_,hu,hd⟩
    · cases i <;> exact window_pos ..
    · cases m <;> decide
    · cases m <;> decide

private theorem path_motion {x y : State} {n : ℕ} (tr : Trace step x n y) (i : Bool) :
    x.position i - n ≤ y.position i ∧ y.position i ≤ x.position i + n ∧
    (upward y.q → upward x.q ∧ x.position i ≤ y.position i) ∧
    (¬upward x.q → ¬upward y.q ∧ y.position i ≤ x.position i) := by
  induction tr with
  | nil => simp
  | @cons x a y k h _ ih =>
    obtain ⟨v, hp, hlo, hhi, hu, hd⟩ := step_motion h i
    obtain ⟨il,ir,iu,id⟩ := ih
    refine ⟨?_,?_,?_,?_⟩
    · push_cast
      omega
    · push_cast
      omega
    · intro hq
      obtain ⟨h',h''⟩ := iu hq
      obtain ⟨hh,h'''⟩ := hu h'
      exact ⟨hh,by omega⟩
    · intro hq
      obtain ⟨h',h''⟩ := hd hq
      obtain ⟨hh,h'''⟩ := id h'
      exact ⟨hh,by omega⟩

private theorem cut_trace {X : Type*} {f : X → Option X} {x z : X} {n : ℕ}
    (whole : Trace f x n z) (u : ℕ) (h : u≤n) :
    ∃ y, Trace f x u y ∧ Trace f y (n-u) z := by
  induction u generalizing x n with
  | zero => exact ⟨x,.nil _,by simpa using whole⟩
  | succ u ih =>
    cases whole with
    | nil => omega
    | @cons x a z k ha tail =>
      obtain ⟨y,p,s⟩ := ih tail (by omega)
      exact ⟨y,by simpa [Nat.add_comm] using Trace.cons ha p,
        by convert s using 1; omega⟩

open OAI.Computability.NearSquareRoot

private theorem trace_fences (word : List Bool) (p q : ℤ) (sl dl sr dr : List Letter)
    (u : ℕ) (hu : u≤2*word.length+3) (c : TM.Config Letter Phase Bool)
    (hc : Trace (TM.advance rule)
       (State.mk .start (full p sl word sr) (empty q dl word.length dr)).physical u c)
    (i : Bool) :
    pick p q i ≤ (c.tape i).pos ∧ (c.tape i).pos ≤ pick p q i + word.length+1 := by
  obtain ⟨y,pre,suf⟩ := cut_trace (run_transfer word p q sl dl sr dr) u hu
  obtain rfl := trace_endpoint_unique (physical_trace pre) hc
  have hp := path_motion pre i
  have hs := path_motion suf i
  have ha : (State.mk .start (full p sl word sr) (empty q dl word.length dr)).position i =
      pick p q i := by cases i <;> rfl
  have hb : (State.mk .done (empty p sl word.length sr) (full q dl word dr)).position i =
      pick p q i := by cases i <;> rfl
  have hide : (y.physical.tape i).pos = y.position i := by cases i <;> rfl
  rw [hide]
  rw [ha] at hp
  rw [hb] at hs
  obtain ⟨_,hpmax,hpu,_⟩ := hp
  obtain ⟨hsmin,_,_,hsd⟩ := hs
  constructor
  · by_cases up : upward y.q
    · exact (hpu up).2
    · exact (hsd up).2
  · have hh : ((2*word.length+3-u : ℕ) : ℤ) =
        2*(word.length : ℤ)+3-(u : ℤ) := by omega
    rw [hh] at hsmin
    omega

/-- All visited tape/address pairs, including entry and halt, are inside the
    two home-to-right-delimiter intervals. This is the original source
    predicate used by the published multiplication theorem. -/
theorem neutral_bank_visits (word : List Bool) (p q : ℤ) (sl dl sr dr : List Letter) :
    VisitsAtMost rule
      (State.mk .start (full p sl word sr) (empty q dl word.length dr)).physical
      (2*word.length+3) (2*(word.length+2)) := by
  have h := visitsAtMost_of_tape_fences (pick p q)
    (fun i => pick p q i + (word.length : ℤ)+1)
    (trace_fences word p q sl dl sr dr)
  have he : ∀ i : Bool, (pick p q i + (word.length : ℤ)+1+1-pick p q i).toNat =
                         word.length+2 := by
    intro i
    omega
  simpa [he,Nat.two_mul] using h

end S008.Recount
