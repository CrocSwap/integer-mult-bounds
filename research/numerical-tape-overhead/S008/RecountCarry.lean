import S008.RecountProduct

namespace S008.Recount.Carry

open OAI.Computability.IntegerMultiplication
open S008.Recount S008.Recount.Letter

structure Pair where
  data : Bool
  old : Bool
  deriving Repr

/-- Result bit and outgoing binary addition carry. -/
def plus (a b c : Bool) : Bool × Bool :=
  (a.xor (b.xor c), decide (2≤a.toNat+b.toNat+c.toNat))

private theorem plus_value (a b c : Bool) :
    a.toNat+b.toNat+c.toNat = (plus a b c).1.toNat + 2*(plus a b c).2.toNat := by
  cases a <;> cases b <;> cases c <;> decide

def sumBits : List Pair → Bool → List Bool × Bool
  | [], c => ([],c)
  | a::as, c =>
    let (d,co) := plus a.data a.old c
    let (xs,cf) := sumBits as co
    (d::xs,cf)

def leValue : List Bool → ℕ
  | [] => 0
  | x::xs => x.toNat+2*leValue xs

@[simp] theorem sumBits_length (xs : List Pair) (c : Bool) : (sumBits xs c).1.length=xs.length := by
  induction xs generalizing c with
  | nil => rfl
  | cons a xs ih => simp [sumBits,ih]

private theorem le_append (xs ys : List Bool) :
    leValue (xs++ys)=leValue xs+2^xs.length*leValue ys := by
  induction xs with
  | nil => simp [leValue]
  | cons a xs ih => simp only [List.cons_append,leValue,ih,List.length_cons,pow_succ]; ring

theorem sumBits_value (xs : List Pair) (cin : Bool) :
    leValue (xs.map Pair.data)+leValue (xs.map Pair.old)+cin.toNat =
    leValue (sumBits xs cin).1 + 2^xs.length*(sumBits xs cin).2.toNat := by
  induction xs generalizing cin with
  | nil => simp [leValue,sumBits]
  | cons a xs ih =>
    simp only [List.map_cons,leValue,sumBits,List.length_cons,pow_succ]
    have hh := ih (plus a.data a.old cin).2
    have hd := plus_value a.data a.old cin
    nlinarith only [hh,hd]

inductive Port where | input | carry | low | high
  deriving DecidableEq, Repr

instance : Fintype Port :=
  Fintype.ofList [.input,.carry,.low,.high] (by intro i; cases i <;> decide)

inductive Stage where | read (c : Bool) | done
  deriving DecidableEq, Repr

instance : Fintype Stage :=
  Fintype.ofList [.read false,.read true,.done] (by
    intro q
    cases q with
    | read b => cases b <;> decide
    | done => decide)

def four {α : Type} (x c l h : α) : Port→α
  | .input => x
  | .carry => c
  | .low => l
  | .high => h

/-- False selects the low-limb port. True selects the quotient port. -/
def label (m : Bool) (x : Bool) : Letter := if m then marked x else bit x

def banked {α : Type} (m : Bool) (s a on off : α) : Port→α :=
  four s a (if m then off else on) (if m then on else off)

def cfg (m : Bool) (q : Stage) (s a on off : Window) : TM.Config Letter Stage Port :=
  ⟨q,banked m s.physical a.physical on.physical off.physical⟩

def writeOps (m : Bool) (sym : Letter) (t : Port→Letter) (d : Bool) : Port→Letter×TM.Move :=
  four (sym,.right) (blank,.right)
    (if m then (t .low,.stay) else (bit d,.right))
    (if m then (bit d,.right) else (t .high,.stay))

def rule : TM.Rule Letter Stage Port := fun q t =>
  match q,t .input,t .carry with
  | .read ci, .bit a, .bit b => some (.read (plus a b ci).2,writeOps false (bit a) t (plus a b ci).1)
  | .read ci, .marked a, .bit b => some (.read (plus a b ci).2,writeOps true (marked a) t (plus a b ci).1)
  | .read ci, .right, _ => some (.done,four (right,.right) (t .carry,.stay) (t .low,.stay) (bit ci,.right))
  | _,_,_ => none

private theorem same_stay (t : TM.Tape Letter) : t.apply (t.view 0,.stay)=t := by
  rcases t with ⟨p,v⟩
  change TM.Tape.mk (p+0) (fun i => if i+0=0 then v 0 else v (i+0))=TM.Tape.mk p v
  simp only [add_zero]
  congr 1
  funext i
  by_cases hi : i=0 <;> simp [hi]

private theorem one (m : Bool) (p q : ℤ) (sp sr ap ar : List Letter) (on off : Window)
    (a : Pair) (cin : Bool) :
    TM.advance rule (cfg m (.read cin) ⟨p,sp,label m a.data::sr⟩ ⟨q,ap,bit a.old::ar⟩ on off) =
    some (cfg m (.read (plus a.data a.old cin).2) ⟨p+1,label m a.data::sp,sr⟩
      ⟨q+1,blank::ap,ar⟩ (on.apply (bit (plus a.data a.old cin).1) .right) off) := by
  cases m <;>
    simp only [TM.advance,rule,cfg,banked,four,label,Bool.false_eq_true,ite_false,ite_true,
      Window.read_physical,Window.atHead,List.headD_cons,writeOps,Option.map_some]
  all_goals congr 1
  all_goals congr 1
  all_goals funext i
  all_goals cases i
  all_goals first | rfl | exact (Window.physical_apply ..).symm | (change off.physical.apply (off.atHead,.stay) = off.physical; rw [←Window.read_physical]; exact same_stay _)

def writeBits (w : Window) (xs : List Bool) : Window :=
  xs.foldl (fun a b => a.apply (bit b) .right) w

private theorem rep_snoc (n : ℕ) (s : List Letter) :
    List.replicate n blank ++ blank::s = List.replicate (n+1) blank ++ s := by
  induction n with
  | zero => rfl
  | succ n ih => simpa only [List.replicate_succ,List.cons_append,List.cons.injEq,true_and] using ih

/-- The literal data portion visits each pair once, emits its selected bit, erases the old carry
    and preserves the other output port. All four exterior windows are arbitrary. -/
theorem sweep (m : Bool) (xs : List Pair) (cin : Bool) (p q : ℤ)
    (sp sr ap ar : List Letter) (on off : Window) :
    let ts := xs.map (fun a => label m a.data)
    let cs := xs.map (fun a => bit a.old)
    let out := sumBits xs cin
    Trace (TM.advance rule) (cfg m (.read cin) ⟨p,sp,ts++sr⟩ ⟨q,ap,cs++ar⟩ on off)
      xs.length (cfg m (.read out.2) ⟨p+xs.length,ts.reverse++sp,sr⟩
        ⟨q+xs.length,List.replicate xs.length blank++ap,ar⟩ (writeBits on out.1) off) := by
  induction xs generalizing cin p q sp ap on with
  | nil => simp [sumBits,writeBits,Trace.nil]
  | cons a xs ih =>
    have ho := one m p q sp ((xs.map (fun t => label m t.data))++sr) ap
      ((xs.map (fun t => bit t.old))++ar) on off a cin
    have ht := ih (plus a.data a.old cin).2 (p+1) (q+1) (label m a.data::sp) (blank::ap)
      (on.apply (bit (plus a.data a.old cin).1) .right)
    have he := Trace.cons ho ht
    simpa [sumBits,writeBits,List.reverse_cons,List.append_assoc,rep_snoc,Nat.add_comm,
      add_assoc,add_left_comm,add_comm] using he

private theorem overflow (p : ℤ) (sp sr : List Letter) (old lo hi : Window) (c : Bool) :
    TM.advance rule (cfg false (.read c) ⟨p,sp,right::sr⟩ old lo hi) =
      some (cfg false .done ⟨p+1,right::sp,sr⟩ old lo (hi.apply (bit c) .right)) := by
  simp only [TM.advance,rule,cfg,banked,four,Bool.false_eq_true,ite_false,Window.read_physical,
    Window.atHead,List.headD_cons,Option.map_some]
  congr 1
  congr 1
  funext i
  cases i
  · exact (Window.physical_apply ⟨p,sp,right::sr⟩ right .right).symm
  · change old.physical.apply (old.atHead,.stay) = old.physical
    rw [←Window.read_physical]
    exact same_stay _
  · change lo.physical.apply (lo.atHead,.stay) = lo.physical
    rw [←Window.read_physical]
    exact same_stay _
  · exact (Window.physical_apply ..).symm

private theorem write_join (s : Window) (xs : List Bool) (b : Bool) :
    writeBits s (xs++[b]) = (writeBits s xs).apply (bit b) .right := by
  simp [writeBits,List.foldl_append]

/-- A whole recovered coefficient and preceding carry go to the low limb and the next
    quotient in a single forward sweep. The explicit last signal writes the overflow bit. -/
theorem row_trace (l h : List Pair) (ci : Bool) (p q : ℤ) (sp sr ap ar : List Letter) (lo hi : Window) :
    let lowA := l.map (fun a => bit a.data)
    let highA := h.map (fun a => marked a.data)
    let lowC := l.map (fun a => bit a.old)
    let highC := h.map (fun a => bit a.old)
    let x := sumBits l ci
    let y := sumBits h x.2
    let init := cfg false (.read ci) ⟨p,sp,lowA++highA++right::sr⟩ ⟨q,ap,lowC++highC++ar⟩ lo hi
    let sf : Window := ⟨p+l.length+h.length+1,right::(highA.reverse++(lowA.reverse++sp)),sr⟩
    let af : Window := ⟨q+l.length+h.length,List.replicate h.length blank++(List.replicate l.length blank++ap),ar⟩
    Trace (TM.advance rule) init (l.length+h.length+1)
      (cfg false .done sf af (writeBits lo x.1) (writeBits hi (y.1++[y.2]))) := by
  let lowA := l.map (fun a => bit a.data)
  let highA := h.map (fun a => marked a.data)
  let lowC := l.map (fun a => bit a.old)
  let highC := h.map (fun a => bit a.old)
  let x := sumBits l ci
  let y := sumBits h x.2
  let lp := p+(l.length:ℤ)
  let lq := q+(l.length:ℤ)
  let ls := lowA.reverse++sp
  let la := List.replicate l.length blank++ap
  let lf := writeBits lo x.1
  let hs : Window := ⟨lp+h.length,highA.reverse++ls,right::sr⟩
  let ha : Window := ⟨lq+h.length,List.replicate h.length blank++la,ar⟩
  have first := sweep false l ci p q sp (highA++right::sr) ap (highC++ar) lo hi
  have second := sweep true h x.2 lp lq ls (right::sr) la ar hi lf
  have ht : Trace (TM.advance rule) (cfg false (.read x.2) ⟨lp,ls,highA++right::sr⟩
      ⟨lq,la,highC++ar⟩ lf hi) h.length (cfg false (.read y.2) hs ha lf (writeBits hi y.1)) := second
  have hlast := overflow (lp+h.length) (highA.reverse++ls) sr ha lf (writeBits hi y.1) y.2
  have allsteps := first.trans (ht.trans (Trace.single hlast))
  dsimp [label,highA,highC,lf,x,y] at allsteps
  simpa only [List.append_assoc,Nat.add_assoc,write_join] using allsteps

private theorem little_lt (xs : List Bool) : leValue xs < 2^xs.length := by
  induction xs with
  | nil => simp [leValue]
  | cons a xs ih =>
    have hb : a.toNat≤1 := by cases a <;> decide
    simp only [leValue,List.length_cons,pow_succ]
    omega

theorem row_arithmetic (l h : List Pair) (ci : Bool) :
    let x := sumBits l ci
    let y := sumBits h x.2
    let a := leValue ((l++h).map Pair.data)
    let c := leValue ((l++h).map Pair.old)
    leValue x.1=(a+c+ci.toNat)%(2^l.length) ∧
    leValue (y.1++[y.2])=(a+c+ci.toNat)/(2^l.length) := by
  let x := sumBits l ci
  let y := sumBits h x.2
  have z := sumBits_value l ci
  have t := sumBits_value h x.2
  change leValue (l.map Pair.data) + leValue (l.map Pair.old) + ci.toNat =
    leValue x.1 + 2^l.length*x.2.toNat at z
  change leValue (h.map Pair.data) + leValue (h.map Pair.old) + x.2.toNat =
    leValue y.1 + 2^h.length*y.2.toNat at t
  let a := leValue ((l++h).map Pair.data)
  let c := leValue ((l++h).map Pair.old)
  have he : a+c+ci.toNat=leValue x.1+2^l.length*leValue (y.1++[y.2]) := by
    dsimp [a,c]
    rw [List.map_append,List.map_append,le_append,le_append,le_append]
    have hy : y.1.length=h.length := sumBits_length h _
    rw [hy]
    simp only [List.length_map,leValue,mul_zero,add_zero]
    nlinarith only [z,congrArg ((2^l.length)*·) t]
  have hx : leValue x.1 < 2^l.length := by
    simpa [x] using little_lt x.1
  change leValue x.1=(a+c+ci.toNat)%(2^l.length) ∧ leValue (y.1++[y.2])=(a+c+ci.toNat)/(2^l.length)
  rw [he]
  constructor
  · simp [Nat.add_mul_mod_self_left,Nat.mod_eq_of_lt hx]
  · rw [Nat.add_mul_div_left _ _ (by positivity),Nat.div_eq_of_lt hx,zero_add]

inductive ChainPhase where | row (parity cin : Bool) | pad (parity : Bool) | reset (parity : Bool)
  deriving DecidableEq, Repr

instance : Fintype ChainPhase := Fintype.ofList
  [.row false false,.row false true,.row true false,.row true true,.pad false,.pad true,.reset false,.reset true]
  (by intro x; cases x with
      | row p c => cases p <;> cases c <;> decide
      | pad p => cases p <;> decide
      | reset p => cases p <;> decide)

def flip (p : Bool) : Port → Port
  | .input => .input
  | .carry => if p then .high else .carry
  | .low => .low
  | .high => if p then .carry else .high

@[simp] theorem flip_twice (p : Bool) (i : Port) : flip p (flip p i)=i := by
  cases p <;> cases i <;> rfl

def nextPhase (p : Bool) : Stage → ChainPhase
  | .read c => .row p c
  | .done => .pad p

def extendAct {α : Type} (p : Bool) (t : Port→α) : Port→α := fun i => t (flip p i)

def embed (p : Bool) (c : TM.Config Letter Stage Port) : TM.Config Letter ChainPhase Port :=
  ⟨nextPhase p c.pc,extendAct p c.tape⟩

def chainRule : TM.Rule Letter ChainPhase Port := fun q t =>
  match q with
  | .row p c =>
    (rule (.read c) (extendAct p t)).map fun (q',v) => (nextPhase p q',extendAct p v)
  | .pad p =>
    let r := extendAct p t
    if r .input=bottom then
      some (.pad p,extendAct p (four (bottom,.right) (r .carry,.stay) (r .low,.stay) (bit false,.right)))
    else if r .input=retContract then
      some (.reset p,extendAct p (four (retContract,.right) (r .carry,.stay) (r .low,.stay) (r .high,.stay)))
    else none
  | .reset p =>
    let r := extendAct p t
    let atHome := r .carry=left
    let move := if atHome then TM.Move.right else .left
    some (if atHome then .row (!p) false else .reset p,
      extendAct p (four (r .input,.stay) (r .carry,move) (r .low,.stay) (r .high,move)))

theorem embed_one (p : Bool) {x y : TM.Config Letter Stage Port} (hh : TM.advance rule x=some y) :
    TM.advance chainRule (embed p x)=some (embed p y) := by
  rcases x with ⟨q,t⟩
  cases q with
  | done => simp [TM.advance,rule] at hh
  | read c =>
    let sc := fun i => (t i).view 0
    have hr : extendAct p (fun i => (extendAct p t i).view 0)=sc := by
      funext i
      simp [extendAct,sc]
    cases ha : rule (.read c) sc with
    | none =>
      have hz : TM.advance rule ⟨.read c,t⟩=none := by
        change (rule (.read c) sc).map _ = none
        rw [ha]
        rfl
      rw [hz] at hh
      contradiction
    | some act =>
      rcases act with ⟨q',v⟩
      have hh' : TM.advance rule ⟨.read c,t⟩=some ⟨q',fun i => (t i).apply (v i)⟩ := by
        change (rule (.read c) sc).map _ = _
        rw [ha]
        rfl
      rw [hh'] at hh
      cases hh
      simp only [TM.advance,embed,nextPhase,chainRule,hr,ha,Option.map_some]
      rfl

theorem embed_trace (p : Bool) {x y : TM.Config Letter Stage Port} {k : ℕ}
    (h : Trace (TM.advance rule) x k y) :
    Trace (TM.advance chainRule) (embed p x) k (embed p y) := by
  induction h with
  | nil => exact .nil _
  | cons h _ ih => exact .cons (embed_one p h) ih

def chainCfg (p : Bool) (q : ChainPhase) (s a l h : Window) : TM.Config Letter ChainPhase Port :=
  ⟨q,extendAct p (four s.physical a.physical l.physical h.physical)⟩

private theorem held (w : Window) : w.physical.apply (w.atHead,.stay)=w.physical := by
  rw [←Window.read_physical]
  exact same_stay _

private theorem pad_one (p : Bool) (k : ℤ) (pre post : List Letter) (a l h : Window) :
    TM.advance chainRule (chainCfg p (.pad p) ⟨k,pre,bottom::post⟩ a l h)=
      some (chainCfg p (.pad p) ⟨k+1,bottom::pre,post⟩ a l (h.apply (bit false) .right)) := by
  cases p <;> simp only [TM.advance,chainCfg,chainRule,extendAct,flip,four,Bool.false_eq_true,
    ite_false,ite_true,Window.read_physical,Window.atHead,List.headD_cons,Option.map_some]
  all_goals congr 1
  all_goals congr 1
  all_goals funext i
  all_goals cases i
  all_goals first | rfl | exact (Window.physical_apply ..).symm | exact held _

private theorem pad_end (p : Bool) (k : ℤ) (pre post : List Letter) (a l h : Window) :
    TM.advance chainRule (chainCfg p (.pad p) ⟨k,pre,retContract::post⟩ a l h)=
      some (chainCfg p (.reset p) ⟨k+1,retContract::pre,post⟩ a l h) := by
  have hne : retContract ≠ bottom := by decide
  cases p <;> simp only [TM.advance,chainCfg,chainRule,extendAct,flip,four,Bool.false_eq_true,
    ite_false,ite_true,ite_eq_right hne,Window.read_physical,Window.atHead,List.headD_cons,Option.map_some]
  all_goals congr 1
  all_goals congr 1
  all_goals funext i
  all_goals cases i
  all_goals first | rfl | exact (Window.physical_apply ..).symm | exact held _

theorem padding_trace (p : Bool) (n : ℕ) (k : ℤ) (pre post : List Letter) (a l h : Window) :
    Trace (TM.advance chainRule)
      (chainCfg p (.pad p) ⟨k,pre,List.replicate n bottom++retContract::post⟩ a l h)
      (n+1) (chainCfg p (.reset p)
        ⟨k+n+1,retContract::(List.replicate n bottom++pre),post⟩ a l
        (writeBits h (List.replicate n false))) := by
  induction n generalizing k pre h with
  | zero => simpa [writeBits] using Trace.single (pad_end p k pre post a l h)
  | succ n ih =>
    have hs := pad_one p k pre (List.replicate n bottom++retContract::post) a l h
    have ht := ih (k+1) (bottom::pre) (h.apply (bit false) .right)
    have he := Trace.cons hs ht
    have hr (s : List Letter) : List.replicate n bottom++bottom::s=List.replicate (n+1) bottom++s := by
      rw [← List.singleton_append,← List.append_assoc,← List.replicate_one (a:=bottom),← List.replicate_add]
    simpa [List.replicate_succ,writeBits,List.append_assoc,hr,Nat.add_comm,add_assoc,
      add_comm,add_left_comm] using he

private theorem slide_left (k : ℤ) (x : Letter) (xs pr rest : List Letter) :
    (backWindow k (x::xs) pr rest).apply x .left=backWindow (k-1) xs pr (x::rest) := by
  cases xs <;> rfl

private theorem reset_one (p : Bool) (s l : Window) (a b : ℤ) (ol orr nl nrr olds news : List Letter)
    (d : Letter) :
    TM.advance chainRule (chainCfg p (.reset p) s
      (backWindow a (blank::olds) ol orr) l (backWindow b (d::news) nl nrr)) =
      some (chainCfg p (.reset p) s (backWindow (a-1) olds ol (blank::orr)) l
        (backWindow (b-1) news nl (d::nrr))) := by
  have hn : blank ≠ left := by decide
  cases p <;> simp only [TM.advance,chainCfg,chainRule,extendAct,flip,four,Bool.false_eq_true,
    ite_false,ite_true,Window.read_physical,backWindow,Window.atHead,List.headD_cons,
    ite_eq_right hn,Option.map_some]
  all_goals congr 1
  all_goals congr 1
  all_goals funext i
  all_goals cases i
  all_goals first | exact held _ | exact (Window.physical_apply ..).symm.trans (congrArg Window.physical (slide_left ..))

private theorem reset_home (p : Bool) (s l : Window) (a b : ℤ) (ol orr nl nrr : List Letter) :
    TM.advance chainRule (chainCfg p (.reset p) s ⟨a,ol,left::orr⟩ l ⟨b,nl,left::nrr⟩) =
      some (chainCfg (!p) (.row (!p) false) s ⟨b+1,left::nl,nrr⟩ l ⟨a+1,left::ol,orr⟩) := by
  cases p <;> simp only [TM.advance,chainCfg,chainRule,extendAct,flip,four,Bool.false_eq_true,
    ite_false,ite_true,Window.read_physical,Window.atHead,List.headD_cons,Option.map_some,Bool.not_false,Bool.not_true]
  all_goals congr 1
  all_goals congr 1
  all_goals funext i
  all_goals cases i
  all_goals first | exact held _ | exact (Window.physical_apply ..).symm

/-- Rewind both complete physical carry banks to their immutable left fences in
    parallel, then swap the two bank roles, preserving both exterior windows. -/
theorem reset_trace (p : Bool) (ws : List Letter) (s l : Window) (a b : ℤ) (ol orr nl nrr : List Letter) :
    Trace (TM.advance chainRule)
      (chainCfg p (.reset p) s (backWindow a (List.replicate ws.length blank) ol orr) l (backWindow b ws nl nrr))
      (ws.length+1) (chainCfg (!p) (.row (!p) false) s
        ⟨b-ws.length+1,left::nl,ws.reverse++nrr⟩ l
        ⟨a-ws.length+1,left::ol,List.replicate ws.length blank++orr⟩) := by
  induction ws generalizing a b orr nrr with
  | nil => simpa [backWindow] using Trace.single (reset_home p s l a b ol orr nl nrr)
  | cons d ws ih =>
    have hs := reset_one p s l a b ol orr nl nrr (List.replicate ws.length blank) ws d
    have ht := ih (a-1) (b-1) (blank::orr) (d::nrr)
    have he := Trace.cons hs ht
    have ha : a-1-(ws.length:ℤ)+1 = a-(ws.length+1:ℕ)+1 := by omega
    have hb : b-1-(ws.length:ℤ)+1 = b-(ws.length+1:ℕ)+1 := by omega
    simpa [List.replicate_succ,List.reverse_cons,List.append_assoc,rep_snoc,ha,hb,Nat.add_comm] using he

def stored (p : ℤ) (outsideL body outsideR : List Letter) : Window :=
  ⟨p,left::outsideL,body++blank::outsideR⟩

def rowSource (l h : List Pair) : List Letter :=
  l.map (fun a => bit a.data) ++ h.map (fun a => marked a.data) ++ right ::
  (List.replicate (l.length-1) bottom ++ [retContract])

def oldBits (l h : List Pair) : List Letter := (l++h).map (fun a => bit a.old)

def lowBits (l : List Pair) : List Bool := (sumBits l false).1

def newBits (l h : List Pair) : List Bool :=
  let y := sumBits h (sumBits l false).2
  (y.1++[y.2]) ++ List.replicate (l.length-1) false

theorem new_length {l h : List Pair} (hl : 0<l.length) : (newBits l h).length=l.length+h.length := by
  simp [newBits]
  omega

private theorem write_append (s : Window) (xs ys : List Bool) :
    writeBits s (xs++ys) = writeBits (writeBits s xs) ys := by simp [writeBits,List.foldl_append]

private theorem write_blank (xs : List Bool) (p : ℤ) (pre tail : List Letter) :
    writeBits ⟨p,pre,List.replicate xs.length blank++tail⟩ xs =
    ⟨p+xs.length,(xs.map bit).reverse++pre,tail⟩ := by
  induction xs generalizing p pre with
  | nil => simp [writeBits]
  | cons b xs ih =>
    change writeBits ((Window.mk p pre (List.replicate (b::xs).length blank++tail)).apply (bit b) .right) xs=_
    have hh := ih (p+1) (bit b::pre)
    simpa [List.replicate_succ,Window.apply,List.reverse_cons,List.append_assoc,
      add_assoc,add_left_comm,add_comm] using hh

/-- An actual complete row, including its overflow, bounded zero extension,
    parallel bank rewind and parity swap. The next coefficient starts at its data. -/
theorem cycle_trace (par : Bool) (l h : List Pair) (hl : 0<l.length)
    (p q d : ℤ) (pre tail ol orr nl nrr : List Letter) (low : Window) :
    let u := l.length+h.length
    let init := chainCfg par (.row par false) ⟨p,pre,rowSource l h ++ tail⟩
      (stored q ol (oldBits l h) orr) low (stored d nl (List.replicate u blank) nrr)
    ∃ k pr, Trace (TM.advance chainRule) init (2*u+l.length+3)
      (chainCfg (!par) (.row (!par) false) ⟨k,pr,tail⟩
        (stored d nl ((newBits l h).map bit) nrr) (writeBits low (lowBits l))
        (stored q ol (List.replicate u blank) orr)) := by
  let u := l.length+h.length
  let n := l.length-1
  let is := l.map (fun a => bit a.data)
  let js := h.map (fun a => marked a.data)
  let x := sumBits l false
  let y := sumBits h x.2
  let next := newBits l h
  let low' := writeBits low (lowBits l)
  let hi := stored d nl (List.replicate u blank) nrr
  let oldEnd : Window := ⟨q+l.length+h.length,List.replicate h.length blank++
    (List.replicate l.length blank++left::ol),blank::orr⟩
  let pre1 := right::(js.reverse++(is.reverse++pre))
  let k1 := p+l.length+h.length+1
  let rest := List.replicate n bottom++retContract::tail
  let pre2 := retContract::(List.replicate n bottom++pre1)
  let k2 := k1+n+1
  let src2 : Window := ⟨k2,pre2,tail⟩
  have hlen : next.length=u := new_length hl
  have first := embed_trace par (row_trace l h false p q pre rest (left::ol) (blank::orr) low hi)
  let init := chainCfg par (.row par false) ⟨p,pre,rowSource l h++tail⟩
    (stored q ol (oldBits l h) orr) low hi
  have f1 : Trace (TM.advance chainRule) init (u+1)
      (chainCfg par (.pad par) ⟨k1,pre1,rest⟩ oldEnd low' (writeBits hi (y.1++[y.2]))) := by
    simpa [init,rowSource,oldBits,stored,low',lowBits,is,js,x,y,pre1,k1,rest,n,u,oldEnd,
      List.append_assoc,embed,chainCfg,cfg,banked,nextPhase] using first
  have fp := padding_trace par n k1 pre1 tail oldEnd low' (writeBits hi (y.1++[y.2]))
  have f2 : Trace (TM.advance chainRule) (chainCfg par (.pad par) ⟨k1,pre1,rest⟩ oldEnd low'
      (writeBits hi (y.1++[y.2]))) (n+1)
      (chainCfg par (.reset par) src2 oldEnd low' (writeBits hi next)) := by
    simpa only [rest,src2,k2,pre2,next,newBits,y,x,write_append] using fp
  let word := blank::(next.map bit).reverse
  have hword : word.length=u+1 := by simp [word,hlen]
  have oldView : oldEnd=backWindow (q+u) (List.replicate word.length blank) ol orr := by
    rw [hword,List.replicate_succ]
    simp only [oldEnd,backWindow]
    congr 1
    · dsimp [u]; omega
    · rw [←List.append_assoc,←List.replicate_add,show h.length+l.length=u by dsimp [u]; omega]
  have newView : writeBits hi next=backWindow (d+u) word nl nrr := by
    have hh := write_blank next d (left::nl) (blank::nrr)
    rw [hlen] at hh
    exact hh
  have back := reset_trace par word src2 low' (q+u) (d+u) ol orr nl nrr
  rw [←oldView,←newView] at back
  have hpos (a : ℤ) : a+u-word.length+1=a := by rw [hword]; omega
  have hs1 : word.reverse++nrr=next.map bit++blank::nrr := by simp [word,List.reverse_cons]
  have hs2 : List.replicate word.length blank++orr=List.replicate u blank++blank::orr := by
    rw [hword,←rep_snoc]
  rw [hpos,hpos,hs1,hs2] at back
  have all := f1.trans (f2.trans back)
  have time : (u+1)+(n+1+(word.length+1))=2*u+l.length+3 := by rw [hword]; dsimp [n]; omega
  rw [time] at all
  exact ⟨k2,pre2,all⟩

structure Raw where
  low : List Bool
  high : List Bool
  deriving Repr

def lowPairs (r : Raw) (q : List Bool) : List Pair := List.zipWith Pair.mk r.low (q.take r.low.length)
def highPairs (r : Raw) (q : List Bool) : List Pair := List.zipWith Pair.mk r.high (q.drop r.low.length)

def streamRow (r : Raw) : List Letter :=
  r.low.map bit ++ r.high.map marked ++ right :: (List.replicate (r.low.length-1) bottom ++ [retContract])

def stream (rs : List Raw) : List Letter := rs.flatMap streamRow

private theorem zip_reads (a q : List Bool) (hl : a.length=q.length) :
    (List.zipWith Pair.mk a q).map Pair.data = a ∧ (List.zipWith Pair.mk a q).map Pair.old=q := by
  induction a generalizing q with
  | nil => simpa using (show q=[] by simpa using hl.symm).symm
  | cons x xs ih =>
    cases q with
    | nil => simp at hl
    | cons y ys =>
      obtain ⟨hd,ho⟩ := ih ys (by simpa using hl)
      exact ⟨congrArg (x::·) hd,congrArg (y::·) ho⟩

private theorem annotates (r : Raw) (q : List Bool) (hw : r.low.length+r.high.length=q.length) :
    (lowPairs r q).length=r.low.length ∧
    (highPairs r q).length=r.high.length ∧
    (lowPairs r q).map Pair.data=r.low ∧ (highPairs r q).map Pair.data=r.high ∧
    (lowPairs r q++highPairs r q).map Pair.old=q ∧
    oldBits (lowPairs r q) (highPairs r q)=q.map bit ∧
    rowSource (lowPairs r q) (highPairs r q)=streamRow r := by
  have ha : r.low.length=(q.take r.low.length).length := by simp; omega
  have hb : r.high.length=(q.drop r.low.length).length := by simp; omega
  obtain ⟨adl,aol⟩ := zip_reads r.low (q.take r.low.length) ha
  obtain ⟨adh,aoh⟩ := zip_reads r.high (q.drop r.low.length) hb
  change (lowPairs r q).map Pair.data=r.low at adl
  change (highPairs r q).map Pair.data=r.high at adh
  change (lowPairs r q).map Pair.old=q.take r.low.length at aol
  change (highPairs r q).map Pair.old=q.drop r.low.length at aoh
  have hl : (lowPairs r q).length=r.low.length := by simpa using congrArg List.length adl
  have hh : (highPairs r q).length=r.high.length := by simpa using congrArg List.length adh
  have old : (lowPairs r q++highPairs r q).map Pair.old=q := by
    rw [List.map_append,aol,aoh,List.take_append_drop]
  refine ⟨hl,hh,adl,adh,old,?_,?_⟩
  · simpa [oldBits,List.map_map,Function.comp_def] using congrArg (List.map bit) old
  · unfold rowSource streamRow
    rw [← adl,← adh]
    simp [List.map_map,Function.comp_def]

/-- The result limbs in increasing significance and the remaining fixed-width carry. -/
def result : List Raw → List Bool → List Bool × List Bool
  | [],q => ([],q)
  | r::rs,q =>
    let l := lowPairs r q
    let h := highPairs r q
    let more := result rs (newBits l h)
    (lowBits l++more.1,more.2)

structure BankOrigin where
  address : ℤ
  lo : List Letter
  hi : List Letter

def BankOrigin.withBits (o : BankOrigin) (xs : List Letter) : Window := stored o.address o.lo xs o.hi

def rotations (rs : List Raw) (p : Bool) (a b : BankOrigin) : Bool×BankOrigin×BankOrigin :=
  match rs with
  | [] => (p,a,b)
  | _::ts => rotations ts (!p) b a

/-- Any number of recovered binary coefficient words on the active data banks.
    The machine derives its own alternating carry from the seed. -/
theorem whole_carry_trace (rs : List Raw) (w u : ℕ) (hw : 0<w)
    (shape : ∀ r∈rs, r.low.length=w ∧ r.low.length+r.high.length=u)
    (q : List Bool) (hq : q.length=u) (par : Bool) (A B : BankOrigin)
    (k : ℤ) (pre tail : List Letter) (low : Window) :
    let out := result rs q
    let loc := rotations rs par A B
    let init := chainCfg par (.row par false) ⟨k,pre,stream rs++tail⟩
        (A.withBits (q.map bit)) low (B.withBits (List.replicate u blank))
    ∃ f after, Trace (TM.advance chainRule) init (rs.length*(2*u+w+3))
       (chainCfg loc.1 (.row loc.1 false) ⟨f,after,tail⟩
         (loc.2.1.withBits (out.2.map bit)) (writeBits low out.1)
         (loc.2.2.withBits (List.replicate u blank))) := by
  induction rs generalizing q par A B k pre low with
  | nil => exact ⟨k,pre,by simpa [stream,result,rotations,writeBits] using
       (Trace.nil (step:=TM.advance chainRule) (chainCfg par (.row par false) ⟨k,pre,tail⟩
         (A.withBits (q.map bit)) low (B.withBits (List.replicate u blank))))⟩
  | cons r rs ih =>
    have sh := shape r (by simp)
    have sht : ∀ a∈rs, a.low.length=w ∧ a.low.length+a.high.length=u :=
      fun a h => shape a (List.mem_cons_of_mem _ h)
    let l := lowPairs r q
    let h := highPairs r q
    obtain ⟨hl,hh,_,_,_,ho,hs⟩ := annotates r q (sh.2.trans hq.symm)
    have lw : l.length=w := hl.trans sh.1
    have uu : l.length+h.length=u := by dsimp [l,h]; rw [hl,hh,sh.2]
    have lp : 0<l.length := by omega
    obtain ⟨k1,pre1,h1⟩ := cycle_trace par l h lp k A.address B.address pre (stream rs++tail) A.lo A.hi B.lo B.hi low
    have hn : (newBits l h).length=u := (new_length lp).trans uu
    obtain ⟨f,after,h2⟩ := ih sht (newBits l h) hn (!par) B A k1 pre1 (writeBits low (lowBits l))
    rw [uu,lw] at h1
    change oldBits l h=q.map bit at ho
    change rowSource l h=streamRow r at hs
    rw [ho,hs] at h1
    have total := h1.trans h2
    refine ⟨f,after,?_⟩
    simpa [stream,result,rotations,l,h,BankOrigin.withBits,write_append,List.append_assoc,
      Nat.add_mul,Nat.add_comm] using total

def rawValue (r : Raw) : ℕ := leValue (r.low++r.high)

private theorem le_zero (n : ℕ) : leValue (List.replicate n false)=0 := by
  induction n with
  | zero => rfl
  | succ n ih => simp [List.replicate_succ,leValue,ih]

private theorem bit_representation (s : List Bool) : Product.bits s.length (leValue s)=s.reverse := by
  induction s with
  | nil => rfl
  | cons a xs ih =>
    have hdiv : (a.toNat+2*leValue xs)/2=leValue xs := by cases a <;> simp [Nat.add_mul_div_left]
    have hmod : decide ((a.toNat+2*leValue xs)%2=1)=a := by cases a <;> simp
    simp only [List.length_cons,Product.bits,leValue,hdiv,hmod,ih,List.reverse_cons]

/-- The two physical result bit strings are precisely the algebraic carry normal form,
    for every array of words and every fixed-width seed. -/
theorem complete_numeric_carry (rs : List Raw) (w u : ℕ) (hw : 0<w)
    (shape : ∀ r∈rs, r.low.length=w ∧ r.low.length+r.high.length=u)
    (q : List Bool) (hq : q.length=u) :
    let z := result rs q
    let n := Product.normalize (2^w) (rs.map rawValue) (leValue q)
    z.1.reverse = Product.expand w n.1 ∧ leValue z.2=n.2 := by
  induction rs generalizing q with
  | nil => simp [result,Product.normalize,Product.expand]
  | cons r rs ih =>
    have sh := shape r (by simp)
    have sht : ∀ a∈rs, a.low.length=w ∧ a.low.length+a.high.length=u :=
      fun a h => shape a (List.mem_cons_of_mem _ h)
    let l := lowPairs r q
    let h := highPairs r q
    obtain ⟨hl,hh,hd1,hd2,ho,_,_⟩ := annotates r q (sh.2.trans hq.symm)
    have lw : l.length=w := hl.trans sh.1
    have uu : l.length+h.length=u := by dsimp [l,h]; rw [hl,hh,sh.2]
    have lp : 0<l.length := by omega
    have hn := (new_length lp : (newBits l h).length=l.length+h.length).trans uu
    have hdata : (l++h).map Pair.data=r.low++r.high := by rw [List.map_append,hd1,hd2]
    change (l++h).map Pair.old=q at ho
    have ar := row_arithmetic l h false
    change leValue (lowBits l) = _ ∧ _ at ar
    have hlval : leValue (lowBits l)=(rawValue r+leValue q)%2^w := by
      simpa only [hdata,ho,lw,Bool.toNat_false,add_zero,rawValue] using ar.1
    have hnew : leValue (newBits l h)=(rawValue r+leValue q)/2^w := by
      rw [newBits,le_append,le_zero,mul_zero,add_zero]
      simpa only [hdata,ho,lw,Bool.toNat_false,add_zero,rawValue] using ar.2
    have lowlen : (lowBits l).length=w := (sumBits_length l false).trans lw
    have hv := bit_representation (lowBits l)
    rw [lowlen,hlval] at hv
    obtain ⟨hs,hc⟩ := ih sht (newBits l h) hn
    change (result rs (newBits l h)).1.reverse = Product.expand w
        (Product.normalize (2^w) (rs.map rawValue) (leValue (newBits l h))).1 at hs
    rw [hnew] at hs hc
    simp only [result,List.map_cons,Product.normalize,Product.expand,List.reverse_append]
    change ((result rs (newBits l h)).1.reverse++(lowBits l).reverse = _ ∧ _)
    rw [hs,←hv]
    exact ⟨rfl,hc⟩

/-- Exact trimmed bits at the interface to the original source-level raw tape writer. -/
theorem product_bits_at_carry_port {n w h S u : ℕ} (x y : List Bool) (r : List ℝ) (rs : List Raw)
    (hx : x.length=n) (hy : y.length=n) (hwidth : n≤w*h) (hslots : 2*h≤S) (hw : 0<w)
    (shape : ∀ a∈rs, a.low.length=w ∧ a.low.length+a.high.length=u)
    (herr : List.Forall₂ (fun (a:ℝ) (c:ℕ) => |a-(c:ℝ)|<1/4) r (Product.cyclicCoefficients w h S x y))
    (words : rs.map rawValue=r.map Product.recover) :
    let z := result rs (List.replicate u false)
    let bits := (z.1.take (2*n)).reverse
    leValue z.2=0 ∧ bits.length=2*n ∧ bitValue bits=bitValue x*bitValue y := by
  let seed := List.replicate u false
  let out := result rs seed
  let cs := Product.cyclicCoefficients w h S x y
  have hc : rs.map rawValue=cs := words.trans (Product.recover_all herr)
  obtain ⟨a,b⟩ := complete_numeric_carry rs w u hw shape seed (by simp [seed])
  change out.1.reverse = Product.expand w (Product.normalize (2^w) (rs.map rawValue) (leValue seed)).1 at a
  change leValue out.2 = (Product.normalize (2^w) (rs.map rawValue) (leValue seed)).2 at b
  rw [hc,show leValue seed=0 from le_zero u] at a b
  obtain ⟨h0,hlen,hval⟩ := Product.cyclic_assembly x y hx hy hwidth hslots
  have hbits : (out.1.take (2*n)).reverse=Product.assembled w n cs := by
    unfold Product.assembled
    rw [←a]
    change (out.1.take (2*n)).reverse = out.1.reverse.drop (out.1.reverse.length-2*n)
    rw [List.length_reverse,List.reverse_take]
  exact ⟨b.trans h0,by rw [hbits]; exact hlen,by rw [hbits]; exact hval⟩

inductive CapPhase where | home | seek | done
  deriving DecidableEq, Repr

instance : Fintype CapPhase := Fintype.ofList [.home,.seek,.done] (by intro q; cases q <;> decide)

def capCfg (q : CapPhase) (s e : Window) : TM.Config Letter CapPhase Bool := ⟨q,pick s.physical e.physical⟩

def capRule : TM.Rule Letter CapPhase Bool := fun q t =>
  match q with
  | .home =>
    if t false=left then some (.seek,pick (left,.right) (t true,.stay))
    else some (.home,pick (t false,.left) (t true,.stay))
  | .seek =>
    if t true=bottom then some (.seek,pick (t false,.right) (bottom,.right))
    else some (.done,pick (t false,.left) (t true,.stay))
  | .done => none

private theorem home_left (p : ℤ) (d : Letter) (xs pre post : List Letter) (e : Window) (hd : d ≠ left) :
    TM.advance capRule (capCfg .home (backWindow p (d::xs) pre post) e) =
       some (capCfg .home (backWindow (p-1) xs pre (d::post)) e) := by
  simp only [TM.advance,capCfg,capRule,pick,Window.read_physical,Window.atHead,backWindow,
    List.headD_cons,ite_eq_right hd,Option.map_some]
  congr 1
  congr 1
  funext i
  cases i
  · exact (Window.physical_apply ..).symm.trans (congrArg Window.physical (slide_left ..))
  · exact held _

private theorem home_found (p : ℤ) (pre post : List Letter) (e : Window) :
    TM.advance capRule (capCfg .home ⟨p,pre,left::post⟩ e) =
       some (capCfg .seek ⟨p+1,left::pre,post⟩ e) := by
  simp only [TM.advance,capCfg,capRule,pick,Window.read_physical,Window.atHead,List.headD_cons,ite_true,Option.map_some]
  congr 1
  congr 1
  funext i
  cases i
  · exact (Window.physical_apply ..).symm
  · exact held _

private theorem reach_home (xs : List Letter) (hd : ∀ c∈xs,c≠left) (p : ℤ) (pre post : List Letter) (e : Window) :
    Trace (TM.advance capRule) (capCfg .home (backWindow p xs pre post) e) (xs.length+1)
      (capCfg .seek ⟨p-xs.length+1,left::pre,xs.reverse++post⟩ e) := by
  induction xs generalizing p post with
  | nil => simpa [backWindow] using Trace.single (home_found p pre post e)
  | cons d xs ih =>
    have hs := home_left p d xs pre post e (hd d (by simp))
    have ht := ih (fun c hc => hd c (List.mem_cons_of_mem _ hc)) (p-1) (d::post)
    have he := Trace.cons hs ht
    have hp : p-1-(xs.length:ℤ)+1 = p-(xs.length+1:ℕ)+1 := by omega
    simpa [List.reverse_cons,List.append_assoc,hp,Nat.add_comm] using he

private theorem seek_one (p q : ℤ) (sp sr ep er : List Letter) (b : Bool) :
    TM.advance capRule (capCfg .seek ⟨p,sp,bit b::sr⟩ ⟨q,ep,bottom::er⟩) =
      some (capCfg .seek ⟨p+1,bit b::sp,sr⟩ ⟨q+1,bottom::ep,er⟩) := by
  simp only [TM.advance,capCfg,capRule,pick,Window.read_physical,Window.atHead,List.headD_cons,ite_true,Option.map_some]
  congr 1
  congr 1
  funext i
  cases i <;> exact (Window.physical_apply ..).symm

private theorem seek_bits (xs : List Bool) (p q : ℤ) (sp sr ep er : List Letter) :
    Trace (TM.advance capRule) (capCfg .seek ⟨p,sp,xs.map bit++sr⟩ ⟨q,ep,List.replicate xs.length bottom++er⟩)
      xs.length (capCfg .seek ⟨p+xs.length,(xs.map bit).reverse++sp,sr⟩
         ⟨q+xs.length,List.replicate xs.length bottom++ep,er⟩) := by
  induction xs generalizing p q sp ep with
  | nil => simp [Trace.nil]
  | cons b xs ih =>
    have hs := seek_one p q sp (xs.map bit++sr) ep (List.replicate xs.length bottom++er) b
    have ht := ih (p+1) (q+1) (bit b::sp) (bottom::ep)
    have he := Trace.cons hs ht
    have hr : List.replicate xs.length bottom++bottom::ep=List.replicate (xs.length+1) bottom++ep := by
      rw [← List.singleton_append,← List.append_assoc,← List.replicate_one (a:=bottom),← List.replicate_add]
    simpa [List.replicate_succ,List.reverse_cons,List.append_assoc,hr,Nat.add_comm,add_assoc,
      add_comm,add_left_comm] using he

private theorem settle (p q : ℤ) (vs sp sr ep er : List Letter) (b : Letter) :
    TM.advance capRule (capCfg .seek ⟨p,vs++left::sp,b::sr⟩ ⟨q,ep,right::er⟩)=
      some (capCfg .done (backWindow (p-1) vs sp (b::sr)) ⟨q,ep,right::er⟩) := by
  have hn : right≠bottom := by decide
  have ht : (Window.mk p (vs++left::sp) (b::sr)).apply b .left =
      backWindow (p-1) vs sp (b::sr) := by cases vs <;> rfl
  simp only [TM.advance,capCfg,capRule,pick,Window.read_physical,Window.atHead,List.headD_cons,
    ite_eq_right hn,Option.map_some]
  congr 1
  congr 1
  funext i
  cases i
  · exact (Window.physical_apply ..).symm.trans (congrArg Window.physical ht)
  · exact held _

/-- The little-endian low bank is left at exactly the MSB of its first c output bits.
    High zero padding can remain physically present to the right. -/
theorem capped_position (xs : List Bool) (c : ℕ) (hc : c≤xs.length) (p q : ℤ)
    (lo hi el er : List Letter) :
    let source := backWindow (p+xs.length) (blank::(xs.map bit).reverse) lo hi
    let budget : Window := ⟨q,el,List.replicate c bottom++right::er⟩
    let word := (xs.take c).reverse
    let tail := (xs.drop c).map bit++blank::hi
    Trace (TM.advance capRule) (capCfg .home source budget) (xs.length+c+3)
      (capCfg .done (backWindow (p+c-1) (word.map bit) lo tail)
        ⟨q+c,List.replicate c bottom++el,right::er⟩) := by
  let low := xs.take c
  let tail := (xs.drop c).map bit++blank::hi
  let budget : Window := ⟨q,el,List.replicate c bottom++right::er⟩
  let rev := blank::(xs.map bit).reverse
  have hnon : ∀ a∈rev,a≠left := by
    intro a ha
    simp only [rev,List.mem_cons,List.mem_reverse,List.mem_map] at ha
    rcases ha with rfl|⟨b,_,rfl⟩ <;> intro hh <;> cases hh
  have hw := reach_home rev hnon (p+xs.length) lo hi budget
  have hl : low.length=c := by simp [low,hc]
  have hdata : low.map bit++tail = xs.map bit++blank::hi := by
    dsimp [low,tail]
    rw [←List.append_assoc,←List.map_append,List.take_append_drop]
  have hr : rev.length=xs.length+1 := by simp [rev]
  have hword : rev.reverse++hi = low.map bit++tail := by
    simp [rev,List.reverse_cons,hdata]
  have hpos : p+xs.length-rev.length+1=p := by rw [hr]; omega
  rw [hpos,hword,hr] at hw
  have seek := seek_bits low p q (left::lo) tail el (right::er)
  rw [hl] at seek
  have finish : TM.advance capRule (capCfg .seek
      ⟨p+c,(low.map bit).reverse++left::lo,tail⟩ ⟨q+c,List.replicate c bottom++el,right::er⟩)=
      some (capCfg .done (backWindow (p+c-1) (low.map bit).reverse lo tail)
        ⟨q+c,List.replicate c bottom++el,right::er⟩) := by
    cases hh : tail with
    | nil =>
      have hnn : tail≠[] := by simp [tail]
      exact False.elim (hnn hh)
    | cons a rs => exact settle (p+c) (q+c) (low.map bit).reverse lo rs (List.replicate c bottom++el) er a
  have all := hw.trans (seek.trans (Trace.single finish))
  have ht : xs.length+1+1+(c+1)=xs.length+c+3 := by omega
  rw [ht] at all
  simpa only [List.map_reverse] using all

/-- Three source-level rules have matching physical low-bank windows. The first runs every
    packed carry row, the second positions the paid unary budget, and the third produces
    the absolute raw output specified for the original multiplier. -/
theorem recovered_physical_readout {n w h S u : ℕ} (x y : List Bool) (r : List ℝ) (rs : List Raw)
    (hx : x.length=n) (hy : y.length=n) (hwidth : n≤w*h) (hslots : 2*h≤S) (hw : 0<w)
    (shape : ∀ a∈rs, a.low.length=w ∧ a.low.length+a.high.length=u)
    (herr : List.Forall₂ (fun (a:ℝ) (c:ℕ) => |a-(c:ℝ)|<1/4) r (Product.cyclicCoefficients w h S x y))
    (words : rs.map rawValue=r.map Product.recover)
    (A B : BankOrigin) (k q : ℤ) (pre sourceExterior el er : List Letter) :
    let seed := List.replicate u false
    let out := result rs seed
    let data := out.1
    let z := (data.take (2*n)).reverse
    let extra := (data.drop (2*n)).map bit++[blank]
    let loc := rotations rs false A B
    let initialLow : Window := ⟨0,[left],List.replicate data.length blank++[blank]⟩
    let lowEnd := backWindow (0+data.length:ℤ) (blank::(data.map bit).reverse) [] []
    let initialBudget : Window := ⟨q,el,List.replicate (2*n) bottom++right::er⟩
    let selected := backWindow (0+(2*n:ℕ)-1:ℤ) (z.map bit) [] extra
    let terminalBudget : Window := ⟨q+(2*n:ℕ),List.replicate (2*n) bottom++el,right::er⟩
    let init := chainCfg false (.row false false) ⟨k,pre,stream rs++sourceExterior⟩
      (A.withBits (seed.map bit)) initialLow (B.withBits (List.replicate u blank))
    let rawInit := RawWrite.config selected (TM.Tape.loaded blank [])
    ∃ k' pr endRaw,
      Trace (TM.advance chainRule) init (rs.length*(2*u+w+3))
        (chainCfg loc.1 (.row loc.1 false) ⟨k',pr,sourceExterior⟩
          (loc.2.1.withBits (out.2.map bit)) lowEnd (loc.2.2.withBits (List.replicate u blank))) ∧
      Trace (TM.advance capRule) (capCfg .home lowEnd initialBudget) (data.length+2*n+3)
        (capCfg .done selected terminalBudget) ∧
      Trace (TM.advance RawWrite.flush) rawInit (2*n) endRaw ∧ TM.advance RawWrite.flush endRaw=none ∧
      TM.whole blank (z.map bit) (endRaw.tape true) ∧ z.length=2*n ∧ bitValue z=bitValue x*bitValue y ∧
      OAI.Computability.NearSquareRoot.VisitsAtMost RawWrite.flush rawInit (2*n) (4*n+2) := by
  let seed := List.replicate u false
  let out := result rs seed
  let data := out.1
  let z := (data.take (2*n)).reverse
  let extra := (data.drop (2*n)).map bit++[blank]
  let low0 : Window := ⟨0,[left],List.replicate data.length blank++[blank]⟩
  obtain ⟨_,hl,hv⟩ := product_bits_at_carry_port x y r rs hx hy hwidth hslots hw shape herr words
  change z.length=2*n at hl
  change bitValue z=bitValue x*bitValue y at hv
  have hc : 2*n≤data.length := by
    have hlen : min (2*n) data.length=2*n := by simpa [z] using hl
    omega
  obtain ⟨k',pr,ht⟩ := whole_carry_trace rs w u hw shape seed (by simp [seed]) false A B k pre sourceExterior low0
  have lowmatch : writeBits low0 data=backWindow (0+data.length:ℤ) (blank::(data.map bit).reverse) [] [] := by
    exact write_blank data 0 [left] [blank]
  have hpos := capped_position data (2*n) hc 0 q [] [] el er
  obtain ⟨endRaw,hraw,hh,ho,_,hvisit⟩ := RawWrite.final_raw_trace z (0+(2*n:ℕ)-1:ℤ) [] extra
  rw [hl] at hraw hvisit
  refine ⟨k',pr,endRaw,?_,hpos,hraw,hh,ho,hl,hv,?_⟩
  · rw [←lowmatch]
    exact ht
  · convert hvisit using 1
    omega

end S008.Recount.Carry
