import S008.Letter
import S008.Composition

/-! Gather the occupied bits in a marked parent stream into a dense child tape.
    Scatter its returned word through the same marks. All heads move in the
    original tape model, including on the two return sweeps. -/
namespace S008.OccupiedBank

open OAI.Computability.IntegerMultiplication OAI.Computability.NearSquareRoot
open S008.Compiler (Letter)
open S008.Composition (same_stay)

abbrev Port (I : Type) := Option I ⊕ Bool
inductive Phase | scan | rewind | done deriving DecidableEq

instance : Fintype Phase := Fintype.ofList [.scan,.rewind,.done] (by intro x; cases x <;> decide)
abbrev Word := ℤ → Letter

structure Banks where
  parent : Word
  dense : Word

def rank (sel : ℕ → Bool) : ℕ → ℕ
  | 0 => 0
  | j+1 => rank sel j + (if sel j then 1 else 0)

theorem rank_mono (sel : ℕ → Bool) : Monotone (rank sel) :=
  monotone_nat_of_le_succ (fun n => by simp [rank])

theorem rank_le (sel : ℕ → Bool) (n : ℕ) : rank sel n ≤ n := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [rank]; split <;> omega

/-- Ordinary tape symbols, with one mark for each parent bit. -/
def mask (N : ℕ) (sel : ℕ → Bool) (z : ℤ) : Letter :=
  if z = -1 then .home else if 0 ≤ z ∧ z < N then .bit (sel z.toNat)
  else if z = N then .delimiter else .blank

def atHead (w : Word) (p : ℤ) : TM.Tape Letter := ⟨p, fun j => w (p+j)⟩

@[simp] private theorem see (w : Word) (p : ℤ) : (atHead w p).view 0 = w p := by simp [atHead]

private theorem changeCell (w : Word) (p : ℤ) (v : Letter) (m : TM.Move) :
    (atHead w p).apply (v,m) = atHead (Function.update w p v) (p+m.shift) := by
  unfold TM.Tape.apply atHead
  congr 1
  funext i
  by_cases h : i + m.shift = 0
  · simp [h,show p+m.shift+i=p by omega]
  · simp [h,
      show p+m.shift+i=p+(i+m.shift) by omega]

private theorem keep (w : Word) (p : ℤ) (m : TM.Move) :
    (atHead w p).apply (w p,m) = atHead w (p+m.shift) := by
  rw [changeCell, Function.update_eq_self]

def frame {I : Type} (N : ℕ) (sel : ℕ → Bool) (b : Banks)
    (aux : I → TM.Tape Letter) (q : Phase) (p r : ℤ) : TM.Config Letter Phase (Port I) :=
  ⟨q,fun
    | .inl none => atHead b.dense r
    | .inl (some i) => aux i
    | .inr false => atHead (mask N sel) p
    | .inr true => atHead b.parent p⟩

/-- In scatter mode the compact word is consumed and its workspace cleared. -/
def rule {I : Type} (scatter : Bool) : TM.Rule Letter Phase (Port I) := fun q read =>
  match q, read (.inr false) with
  | .scan, .bit selected =>
    some (.scan, fun
      | .inl none => if selected then (if scatter then .blank else read (.inr true), .right)
                     else (read (.inl none),.stay)
      | .inl (some i) => (read (.inl (some i)),.stay)
      | .inr true => (if scatter && selected then read (.inl none) else read (.inr true), .right)
      | .inr false => (read (.inr false),.right))
  | .scan, .delimiter =>
    some (.rewind, fun
      | .inl none => (if scatter then .blank else .delimiter,.stay)
      | .inl (some i) => (read (.inl (some i)),.stay)
      | .inr b => (read (.inr b),.left))
  | .rewind, .bit selected =>
    some (.rewind, fun i => (read i,match i with
      | .inl none => if selected then .left else .stay
      | .inl (some _) => .stay
      | .inr _ => .left))
  | .rewind, .home =>
    some (.done, fun i => (read i,match i with | .inl _ => .stay | .inr _ => .right))
  | _, _ => none

def takeBit (scatter selected : Bool) (b : Banks) (p r : ℕ) : Banks :=
  if selected then
    if scatter then ⟨Function.update b.parent (p:ℤ) (b.dense r), Function.update b.dense (r:ℤ) .blank⟩
    else ⟨b.parent, Function.update b.dense (r:ℤ) (b.parent p)⟩
  else b

def fill (scatter : Bool) (sel : ℕ → Bool) (b : Banks) : ℕ → Banks
  | 0 => b
  | j+1 => takeBit scatter (sel j) (fill scatter sel b j) j (rank sel j)

def output (scatter : Bool) (sel : ℕ → Bool) (N : ℕ) (b : Banks) : Banks :=
  let t := fill scatter sel b N
  ⟨t.parent, Function.update t.dense (rank sel N : ℤ) (if scatter then .blank else .delimiter)⟩

private theorem mask_read {N j : ℕ} (hj : j<N) (sel : ℕ → Bool) :
    mask N sel j = .bit (sel j) := by simp [mask,hj]

private theorem mask_end (N : ℕ) (sel : ℕ → Bool) : mask N sel N = .delimiter := by simp [mask]

private theorem mask_home (N : ℕ) (sel : ℕ → Bool) : mask N sel (-1) = .home := by simp [mask]

private theorem tape_ext {A Q I : Type} {q : Q} {a b : I → TM.Tape A}
    (h : ∀ i, a i=b i) : TM.Config.mk q a = TM.Config.mk q b := congrArg _ (funext h)

variable {I : Type} (scatter : Bool) (N : ℕ) (sel : ℕ → Bool) (aux : I → TM.Tape Letter)

private theorem forward_step (b : Banks) {j : ℕ} (hj : j<N) :
    TM.advance (rule scatter) (frame N sel b aux .scan j (rank sel j)) =
      some (frame N sel (takeBit scatter (sel j) b j (rank sel j)) aux .scan
        ((j+1:ℕ):ℤ) (rank sel (j+1))) := by
  unfold TM.advance
  change ((rule scatter .scan _).map _) = _
  have hread : ((frame N sel b aux .scan j (rank sel j)).tape (.inr false)).view 0 =
    .bit (sel j) := by simpa [frame,atHead] using mask_read hj sel
  simp only [rule,hread,Option.map_some,Option.some.injEq]
  apply tape_ext
  intro i
  rcases i with (_ | i) | (_ | _)
  · cases h : sel j <;> cases scatter <;>
      simp [frame,takeBit,rank,h,changeCell,TM.Move.shift,Function.update_eq_self]
  · exact same_stay (aux i)
  · simp only [frame,← mask_read hj sel,keep,TM.Move.shift,Nat.cast_add,Nat.cast_one]
  · cases h : sel j <;> cases scatter <;>
      simp [frame,takeBit,changeCell,TM.Move.shift,Function.update_eq_self]

private theorem turn_step (b : Banks) :
    TM.advance (rule scatter) (frame N sel b aux .scan N (rank sel N)) =
      some (frame N sel ⟨b.parent,Function.update b.dense (rank sel N : ℤ)
        (if scatter then .blank else .delimiter)⟩ aux .rewind ((N:ℤ)-1) (rank sel N)) := by
  unfold TM.advance
  change ((rule scatter .scan _).map _) = _
  have hread : ((frame N sel b aux .scan N (rank sel N)).tape (.inr false)).view 0 =
    .delimiter := by simp [frame,atHead,mask_end]
  simp only [rule,hread,Option.map_some,Option.some.injEq]
  apply tape_ext
  intro i
  rcases i with (_ | i) | (_ | _)
  · simp [frame,changeCell,TM.Move.shift]
  · exact same_stay (aux i)
  · simp only [frame,see,keep,TM.Move.shift,sub_eq_add_neg]
  · simp [frame,keep,TM.Move.shift,sub_eq_add_neg]

private theorem rewind_step (b : Banks) {j : ℕ} (hj : j<N) :
    TM.advance (rule scatter) (frame N sel b aux .rewind j (rank sel (j+1))) =
      some (frame N sel b aux .rewind ((j:ℤ)-1) (rank sel j)) := by
  unfold TM.advance
  change ((rule scatter .rewind _).map _) = _
  have hread : ((frame N sel b aux .rewind j (rank sel (j+1))).tape (.inr false)).view 0 =
    .bit (sel j) := by simp [frame,atHead,mask_read hj sel]
  simp only [rule,hread,Option.map_some,Option.some.injEq]
  apply tape_ext
  intro i
  rcases i with (_ | i) | (_ | _)
  · cases h : sel j <;> simp [frame,keep,rank,h,TM.Move.shift]
  · exact same_stay (aux i)
  · simp only [frame,see,keep,TM.Move.shift,sub_eq_add_neg]
  · simp [frame,keep,TM.Move.shift,sub_eq_add_neg]

private theorem home_step (b : Banks) :
    TM.advance (rule scatter) (frame N sel b aux .rewind (-1) 0) =
      some (frame N sel b aux .done 0 0) := by
  unfold TM.advance
  change ((rule scatter .rewind _).map _) = _
  have hread : ((frame N sel b aux .rewind (-1) 0).tape (.inr false)).view 0 =
    .home := by simp [frame,atHead,mask_home]
  simp only [rule,hread,Option.map_some,Option.some.injEq]
  apply tape_ext
  intro i
  rcases i with (_ | i) | (_ | _)
  · simp [frame,keep,TM.Move.shift]
  · exact same_stay (aux i)
  · simp [frame,keep,TM.Move.shift]
  · simp [frame,keep,TM.Move.shift]

/-- The parent and mask share a scanned length. The compact head reaches only the
    true number of selected bits, even across the return sweep. -/
def zone (N K : ℕ) (aux : I → TM.Tape Letter) : Set (Port I × ℤ) := fun (i,z) =>
  match i with
  | .inl none => 0 ≤ z ∧ z ≤ K
  | .inl (some k) => z = (aux k).pos
  | .inr _ => -1 ≤ z ∧ z ≤ N

private def safe (N : ℕ) (sel : ℕ → Bool) (aux : I → TM.Tape Letter)
    (c : TM.Config Letter Phase (Port I)) : Prop :=
  ∀ i, (i,(c.tape i).pos) ∈ zone N (rank sel N) aux

private theorem safe_frame {b : Banks} {q : Phase} {p r : ℤ}
    (hp : -1 ≤ p) (hp' : p ≤ N) (hr : 0 ≤ r) (hr' : r ≤ rank sel N) :
    safe N sel aux (frame N sel b aux q p r) := by
  intro i
  rcases i with (_ | i) | (_ | _)
  · exact ⟨hr,hr'⟩
  · rfl
  all_goals exact ⟨hp,hp'⟩

/-- A trace recording a predicate at both ends and every intervening state. -/
private inductive Walk {X : Type} (step : X → Option X) (ok : X → Prop) :
    X → ℕ → X → Prop
  | nil {x} : ok x → Walk step ok x 0 x
  | cons {x y z n} : ok x → step x = some y → Walk step ok y n z → Walk step ok x (1+n) z

private theorem Walk.trace {X f g} {x y : X} {n} (w : Walk f g x n y) : Trace f x n y := by
  induction w with
  | nil => exact .nil _
  | cons _ h _ ih => exact .cons h ih

private theorem Walk.trans {X f g} {x y z : X} {n k} (w : Walk f g x n y)
    (u : Walk f g y k z) : Walk f g x (n+k) z := by
  induction w with
  | nil => simpa using u
  | cons hx h _ ih => simpa [Nat.add_assoc] using Walk.cons hx h (ih u)

private theorem Walk.atPrefix {X f g} {x y z : X} {n k} (w : Walk f g x n y)
    (hk : k≤n) (tr : Trace f x k z) : g z := by
  induction w generalizing k z with
  | nil hx =>
    have e : k=0 := by omega
    subst k
    exact (trace_endpoint_unique (.nil _) tr) ▸ hx
  | cons hx h _ ih =>
    cases tr with
    | nil => exact hx
    | cons h' rest =>
      have eqv := Option.some.inj (h.symm.trans h')
      cases eqv
      exact ih (by omega) rest

private theorem scan_path (b : Banks) (j : ℕ) (hj : j≤N) :
    Walk (TM.advance (rule scatter)) (safe N sel aux) (frame N sel b aux .scan 0 0) j
      (frame N sel (fill scatter sel b j) aux .scan j (rank sel j)) := by
  have inside (u : ℕ) (hu : u≤N) : safe N sel aux
      (frame N sel (fill scatter sel b u) aux .scan u (rank sel u)) :=
    safe_frame N sel aux (by omega) (by exact_mod_cast hu) (by positivity)
      (by exact_mod_cast rank_mono sel hu)
  induction j with
  | zero => exact .nil (inside 0 (by omega))
  | succ j ih =>
    exact (ih (by omega)).trans (.cons (inside j (by omega))
      (forward_step scatter N sel aux _ (by omega)) (.nil (inside (j+1) hj)))

private theorem back_path (b : Banks) (j : ℕ) (hj : j≤N) :
    Walk (TM.advance (rule scatter)) (safe N sel aux)
      (frame N sel b aux .rewind ((j:ℤ)-1) (rank sel j)) (j+1)
      (frame N sel b aux .done 0 0) := by
  have inside (u : ℕ) (hu : u≤N) : safe N sel aux (frame N sel b aux .rewind
      ((u:ℤ)-1) (rank sel u)) :=
    safe_frame N sel aux (by omega) (by omega) (by positivity) (by exact_mod_cast rank_mono sel hu)
  induction j with
  | zero =>
    exact .cons (inside 0 (by omega)) (home_step scatter N sel aux b)
      (.nil (safe_frame N sel aux (by omega) (by positivity) (by omega) (by positivity)))
  | succ j ih =>
    have h := rewind_step scatter N sel aux b (j:=j) (by omega)
    rw [show (((j+1:ℕ):ℤ)-1)=(j:ℤ) by omega] at *
    simpa only [Nat.add_comm 1 (j+1)] using Walk.cons
      (safe_frame N sel aux (by omega) (by omega) (by positivity) (by exact_mod_cast rank_mono sel hj))
      h (ih (by omega))

/-- Exact transfer time including homing, and its complete set of tape/head fences. -/
theorem transfer (b : Banks) :
    let start := frame N sel b aux .scan 0 0
    let finish := frame N sel (output scatter sel N b) aux .done 0 0
    Trace (TM.advance (rule scatter)) start (2*N+2) finish ∧
      visitedCells (rule scatter) start (2*N+2) ⊆ zone N (rank sel N) aux := by
  have out := scan_path scatter N sel aux b N (le_refl _)
  have back := back_path scatter N sel aux (output scatter sel N b) N (le_refl _)
  have join := Walk.cons (safe_frame N sel aux (by omega : -1 ≤ (N:ℤ)) (le_refl _)
      (by positivity : 0 ≤ (rank sel N:ℤ)) (le_refl _))
    (turn_step scatter N sel aux (fill scatter sel b N)) back
  have run := out.trans join
  rw [show N+(1+(N+1))=2*N+2 by omega] at run
  refine ⟨run.trace,?_⟩
  rintro ⟨i,z⟩ ⟨u,hu,c,tr,e⟩
  change (c.tape i).pos = z at e
  subst z
  exact run.atPrefix hu tr i

end S008.OccupiedBank
