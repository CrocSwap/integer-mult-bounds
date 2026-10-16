import Std
namespace XorLift
abbrev Vec (n : Nat) := Fin n → Bool
def zero : Vec n := fun _ => false
def plus (x y : Vec n) : Vec n := fun i => Bool.xor (x i) (y i)
def basis (j : Fin n) : Vec n := fun i => decide (i = j)
def ins (b : Bool) (x : Vec n) : Vec (n+1) := Fin.cases b x
def IsLinear (f : Vec n → Vec m) : Prop :=
  f zero = zero ∧ ∀ x y, f (plus x y) = plus (f x) (f y)
theorem ins_zero : ins false (zero : Vec n) = zero := by
  funext i; refine Fin.cases ?_ (fun j => ?_) i <;> rfl
theorem ins_plus (x y : Vec n) : ins false (plus x y) = plus (ins false x) (ins false y) := by
  funext i; refine Fin.cases ?_ (fun j => ?_) i <;> rfl
theorem ins_basis (j : Fin n) : ins false (basis j) = basis j.succ := by
  funext i; refine Fin.cases ?_ (fun k => ?_) i
  · have hz : (0 : Fin (n+1)) ≠ j.succ := by
      intro h; have hv := congrArg Fin.val h
      change 0 = j.val + 1 at hv; omega
    simp [ins, basis, hz]
  · simp [ins, basis]
theorem split (x : Vec (n+1)) :
    x = plus (if x 0 then basis 0 else zero) (ins false (fun j => x j.succ)) := by
  funext i; refine Fin.cases ?_ (fun j => ?_) i
  · cases h : x 0 <;> simp [h, plus, basis, zero, ins]
  · have hz : j.succ ≠ (0 : Fin (n+1)) := by
      intro h; have hv := congrArg Fin.val h
      change j.val + 1 = 0 at hv; omega
    cases h : x 0 <;> simp [h, plus, basis, zero, ins, hz]
theorem basis_complete (f g : Vec n → Vec m)
    (hf : IsLinear f) (hg : IsLinear g)
    (h : ∀ j, f (basis j) = g (basis j)) : f = g := by
  induction n with
  | zero =>
    funext x
    have hx : x = zero := by funext i; exact Fin.elim0 i
    rw [hx, hf.1, hg.1]
  | succ n ih =>
    have ft : IsLinear (fun x => f (ins false x)) := by
      constructor
      · simpa [ins_zero] using hf.1
      · intro x y; change f (ins false (plus x y)) = _
        rw [ins_plus]; exact hf.2 _ _
    have gt : IsLinear (fun x => g (ins false x)) := by
      constructor
      · simpa [ins_zero] using hg.1
      · intro x y; change g (ins false (plus x y)) = _
        rw [ins_plus]; exact hg.2 _ _
    have ht : (fun x => f (ins false x)) = (fun x => g (ins false x)) :=
      ih _ _ ft gt (fun j => by simpa [ins_basis] using h j.succ)
    funext x
    have eqx := split x
    have ff := hf.2 (if x 0 then basis 0 else zero) (ins false (fun j => x j.succ))
    have gg := hg.2 (if x 0 then basis 0 else zero) (ins false (fun j => x j.succ))
    rw [← eqx] at ff gg
    rw [ff, gg, congrFun ht]
    cases hx : x 0 <;> simp [hx, hf.1, hg.1, h]
structure Gate (n : Nat) where
  dst : Fin n
  src : Fin n
def step (g : Gate n) (x : Vec n) : Vec n := fun i =>
  if i = g.dst then Bool.xor (x g.dst) (x g.src) else x i
def run : List (Gate n) → Vec n → Vec n
  | [], x => x
  | g :: gs, x => run gs (step g x)
theorem step_linear (g : Gate n) : IsLinear (step g) := by
  constructor
  · funext i; simp [step, zero]
  · intro x y; funext i
    by_cases h : i = g.dst
    · simp only [step, h, ↓reduceIte, plus]
      cases x g.dst <;> cases y g.dst <;> cases x g.src <;> cases y g.src <;> rfl
    · simp [step, plus, h]
theorem run_linear (gs : List (Gate n)) : IsLinear (run gs) := by
  induction gs with
  | nil => exact ⟨rfl, fun _ _ => rfl⟩
  | cons g gs ih =>
    constructor
    · change run gs (step g zero) = zero
      rw [(step_linear g).1, ih.1]
    · intro x y
      change run gs (step g (plus x y)) = _
      rw [(step_linear g).2, ih.2]; rfl
abbrev Streams (n : Nat) (α : Type) := Fin n → α → Bool
def streamStep (g : Gate n) (x : Streams n α) : Streams n α := fun i a =>
  if i = g.dst then Bool.xor (x g.dst a) (x g.src a) else x i a
def streamRun : List (Gate n) → Streams n α → Streams n α
  | [], x => x
  | g :: gs, x => streamRun gs (streamStep g x)
theorem stream_pointwise (gs : List (Gate n)) (x : Streams n α) (a : α) :
    (fun i => streamRun gs x i a) = run gs (fun i => x i a) := by
  induction gs generalizing x with
  | nil => rfl
  | cons g gs ih =>
    change (fun i => streamRun gs (streamStep g x) i a) = _
    rw [ih]; rfl
theorem basis_to_stream (p q : List (Gate n))
    (h : ∀ j, run p (basis j) = run q (basis j)) (x : Streams n α) :
    streamRun p x = streamRun q x := by
  have eqrun := basis_complete (run p) (run q) (run_linear p) (run_linear q) h
  funext i a
  have hp := congrFun (stream_pointwise p x a) i
  have hq := congrFun (stream_pointwise q x a) i
  rw [hp, hq, eqrun]
theorem continuation_substitution (p q : List (Gate n))
    (h : ∀ j, run p (basis j) = run q (basis j))
    (x : Streams n α) (continuation : Streams n α → β) :
    continuation (streamRun p x) = continuation (streamRun q x) := by
  rw [basis_to_stream p q h x]
#print axioms basis_complete
#print axioms run_linear
#print axioms basis_to_stream
#print axioms continuation_substitution
end XorLift
