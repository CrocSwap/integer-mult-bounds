import Std

/- Source model for PR1141's exact grid operations. No analytic approximation
   or bound on the data, shear functions, or chart function is assumed. -/
namespace RoundedPhase

abbrev Grid := Int × Int

inductive Quarter where
  | zero | one | two | three
  deriving DecidableEq

def turn : Quarter → Grid → Grid
  | .zero, v => v
  | .one, (x, y) => (-y, x)
  | .two, (x, y) => (-x, -y)
  | .three, (x, y) => (y, -x)

def unturn : Quarter → Grid → Grid
  | .zero, v => v
  | .one, (x, y) => (y, -x)
  | .two, (x, y) => (-x, -y)
  | .three, (x, y) => (-y, x)

theorem unturn_turn (q : Quarter) (v : Grid) : unturn q (turn q v) = v := by
  rcases v with ⟨x, y⟩
  cases q <;> simp [turn, unturn]

theorem turn_unturn (q : Quarter) (v : Grid) : turn q (unturn q v) = v := by
  rcases v with ⟨x, y⟩
  cases q <;> simp [turn, unturn]

def xm (f : Int → Int) (v : Grid) : Grid := (v.1 - f v.2, v.2)
def xp (f : Int → Int) (v : Grid) : Grid := (v.1 + f v.2, v.2)
def ym (f : Int → Int) (v : Grid) : Grid := (v.1, v.2 - f v.1)
def yp (f : Int → Int) (v : Grid) : Grid := (v.1, v.2 + f v.1)

theorem xp_xm (f : Int → Int) (v : Grid) : xp f (xm f v) = v := by
  rcases v with ⟨x, y⟩
  simp [xp, xm]

theorem xm_xp (f : Int → Int) (v : Grid) : xm f (xp f v) = v := by
  rcases v with ⟨x, y⟩
  simp [xp, xm]

theorem ym_yp (f : Int → Int) (v : Grid) : ym f (yp f v) = v := by
  rcases v with ⟨x, y⟩
  simp [ym, yp]

theorem yp_ym (f : Int → Int) (v : Grid) : yp f (ym f v) = v := by
  rcases v with ⟨x, y⟩
  simp [ym, yp]

structure Coeff where
  quarter : Quarter
  tangent : Int → Int
  sine : Int → Int

def rotate (c : Coeff) (v : Grid) : Grid :=
  turn c.quarter (xm c.tangent (yp c.sine (xm c.tangent v)))

def unrotate (c : Coeff) (v : Grid) : Grid :=
  xp c.tangent (ym c.sine (xp c.tangent (unturn c.quarter v)))

theorem unrotate_rotate (c : Coeff) (v : Grid) : unrotate c (rotate c v) = v := by
  simp only [unrotate, rotate, unturn_turn, xp_xm, ym_yp]

theorem rotate_unrotate (c : Coeff) (v : Grid) : rotate c (unrotate c v) = v := by
  simp only [unrotate, rotate, xm_xp, yp_ym, turn_unturn]

abbrev State := Grid × Grid

def step (chart : Grid → Coeff) (omega : Coeff) (state : State) : State :=
  (rotate (chart state.2) state.1, rotate omega state.2)

def back (chart : Grid → Coeff) (omega : Coeff) (state : State) : State :=
  let ratio := unrotate omega state.2
  (unrotate (chart ratio) state.1, ratio)

theorem back_step (chart : Grid → Coeff) (omega : Coeff) (state : State) :
    back chart omega (step chart omega state) = state := by
  rcases state with ⟨value, ratio⟩
  simp only [back, step, unrotate_rotate]

theorem step_back (chart : Grid → Coeff) (omega : Coeff) (state : State) :
    step chart omega (back chart omega state) = state := by
  rcases state with ⟨value, ratio⟩
  simp only [back, step, rotate_unrotate]

def walk {α : Type} (f : α → α) : Nat → α → α
  | 0, x => x
  | n + 1, x => walk f n (f x)

def rewind {α : Type} (b : α → α) : Nat → α → α
  | 0, x => x
  | n + 1, x => b (rewind b n x)

theorem rewind_walk {α : Type} (f b : α → α)
    (h : ∀ x, b (f x) = x) (n : Nat) (x : α) :
    rewind b n (walk f n x) = x := by
  induction n generalizing x with
  | zero => rfl
  | succ n ih => simp only [walk, rewind, ih, h]

theorem walk_rewind {α : Type} (f b : α → α)
    (h : ∀ x, f (b x) = x) (n : Nat) (x : α) :
    walk f n (rewind b n x) = x := by
  induction n generalizing x with
  | zero => rfl
  | succ n ih => simp only [walk, rewind, h, ih]

theorem walk_commutes {α : Type} (f : α → α) (n : Nat) (x : α) :
    walk f n (f x) = f (walk f n x) := by
  induction n generalizing x with
  | zero => rfl
  | succ n ih => simpa only [walk] using ih (f x)

theorem rewind_eq_walk {α : Type} (b : α → α) (n : Nat) (x : α) :
    rewind b n x = walk b n x := by
  induction n generalizing x with
  | zero => rfl
  | succ n ih => simp only [rewind, walk, ih, walk_commutes]

theorem reconstruct (chart : Grid → Coeff) (omega : Coeff)
    (n : Nat) (state : State) :
    walk (back chart omega) n (walk (step chart omega) n state) = state := by
  rw [← rewind_eq_walk]
  exact rewind_walk _ _ (back_step chart omega) n state

theorem reconstruct_reverse (chart : Grid → Coeff) (omega : Coeff)
    (n : Nat) (state : State) :
    walk (step chart omega) n (walk (back chart omega) n state) = state := by
  rw [← rewind_eq_walk (back chart omega)]
  exact walk_rewind _ _ (step_back chart omega) n state

/- Deterministic chart readout is reused after reconstruction. This does not
   assert that the chart is an analytic approximation to a unit phase. -/
theorem same_readout (chart : Grid → Coeff) (omega : Coeff)
    (emit : State → β) (n : Nat) (state : State) :
    emit (walk (back chart omega) n (walk (step chart omega) n state)) = emit state := by
  rw [reconstruct]

end RoundedPhase

#print axioms RoundedPhase.unrotate_rotate
#print axioms RoundedPhase.rotate_unrotate
#print axioms RoundedPhase.back_step
#print axioms RoundedPhase.step_back
#print axioms RoundedPhase.reconstruct
#print axioms RoundedPhase.reconstruct_reverse
#print axioms RoundedPhase.same_readout
