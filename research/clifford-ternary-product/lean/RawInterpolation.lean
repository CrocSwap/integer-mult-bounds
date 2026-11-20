import BooleanGauss
import Mathlib.Algebra.BigOperators.Fin

/-! Fit the Boolean truth table in affine coordinates. The fits read
the origin, singleton columns and pairs of columns. -/
namespace RawInterpolation
open TernaryCollect BooleanGauss Finset

def liftVar {n} (i : Fin n) : Aff (Fin (n+1)) := .var i.succ

def affineFit : (n : ℕ) → (Bits n → Bool) → Aff (Fin n)
  | 0,f => .const (f Fin.elim0)
  | n+1,f =>
    let z : Bits n := fun _ ↦ false
    let g := fun x : Bits n ↦ f (Fin.cons false x)
    .plus ((affineFit n g).sub liftVar)
      (chooseScale (f (Fin.cons true z) ^^ g z) (.var 0))

def quadraticFit : (n : ℕ) → (Bits n → Bool) → Quad (Fin n)
  | 0,f => .affine (.const (f Fin.elim0))
  | n+1,f =>
    let g := fun x : Bits n ↦ f (Fin.cons false x)
    let d := fun x : Bits n ↦ f (Fin.cons true x) ^^ g x
    .plus ((quadraticFit n g).sub liftVar)
      (.times (.var 0) ((affineFit n d).sub liftVar))

theorem lift_eval {n} (b : Bool) (x : Bits n) :
    (fun i ↦ (liftVar i).eval (Fin.cons b x)) = x := by rfl

theorem affine_rule {n} (f : Bits (n+1) → Bool) (b : Bool) (x : Bits n) :
    (affineFit (n+1) f).eval (Fin.cons b x) = ((affineFit n (fun u ↦ f (Fin.cons false u))).eval x ^^
      (b && (f (Fin.cons true (fun _ ↦ false)) ^^ f (Fin.cons false (fun _ ↦ false))))) := by
  have h (k : Bool) : (chooseScale k (.var 0)).eval (Fin.cons b x) = (b && k) := by
    cases k <;> cases b <;> rfl
  rw [affineFit, Aff.eval,Aff.eval_sub,lift_eval,h]

theorem quadratic_rule {n} (f : Bits (n+1) → Bool) (b : Bool) (x : Bits n) :
    (quadraticFit (n+1) f).eval (Fin.cons b x) =
      ((quadraticFit n (fun u ↦ f (Fin.cons false u))).eval x ^^
       (b && (affineFit n (fun u ↦ f (Fin.cons true u) ^^ f (Fin.cons false u))).eval x)) := by
  simp only [quadraticFit,Quad.eval,Quad.eval_sub,Aff.eval_sub,lift_eval,Aff.eval,Fin.cons_zero]

theorem affine_exact (n : ℕ) (a : Aff (Fin n)) (x : Bits n) :
    (affineFit n a.eval).eval x = a.eval x := by
  induction n with
  | zero =>
    change a.eval Fin.elim0 = a.eval x
    exact congrArg a.eval (Subsingleton.elim _ _)
  | succ n ih =>
    let z : Bits n := fun _ ↦ false
    have h₀ : (fun u : Bits n ↦ a.eval (Fin.cons false u)) = (a.sub off).eval := by
      funext u
      simp [Aff.head_split]
    have hc : (a.eval (Fin.cons true z) ^^ a.eval (Fin.cons false z)) = a.head := by
      simp only [Aff.head_split,Bool.true_and,Bool.false_and,Bool.xor_false]
      cases a.head <;> cases (a.sub off).eval z <;> rfl
    rw [← Fin.cons_self_tail x,affine_rule,h₀,ih,hc,Aff.head_split]

theorem quadratic_exact (n : ℕ) (q : Quad (Fin n)) (x : Bits n) :
    (quadraticFit n q.eval).eval x = q.eval x := by
  induction n with
  | zero =>
    change q.eval Fin.elim0 = q.eval x
    exact congrArg q.eval (Subsingleton.elim _ _)
  | succ n ih =>
    have h₀ : (fun u : Bits n ↦ q.eval (Fin.cons false u)) = (q.sub off).eval := by
      funext u
      simp [Quad.head_split]
    have hd : (fun u : Bits n ↦ q.eval (Fin.cons true u) ^^ q.eval (Fin.cons false u)) = q.derivative.eval := by
      funext u
      simp only [Quad.head_split,Bool.true_and,Bool.false_and,Bool.xor_false]
      cases (q.sub off).eval u <;> cases q.derivative.eval u <;> rfl
    rw [← Fin.cons_self_tail x,quadratic_rule,h₀,hd,ih,affine_exact,Quad.head_split]

def active {n} (x : Bits n) : ℕ := ∑ i, value (x i)

theorem active_cons {n} (b : Bool) (x : Bits n) : active (Fin.cons b x) = value b + active x := by
  simp only [active,Fin.sum_univ_succ,Fin.cons_zero,Fin.cons_succ]

theorem affine_probes (n : ℕ) (f g : Bits n → Bool)
    (h : ∀ x, active x ≤ 1 → f x = g x) : affineFit n f = affineFit n g := by
  induction n with
  | zero => simp [affineFit,h _ (by simp [active])]
  | succ n ih =>
    have h₀ (x : Bits n) (hx : active x ≤ 1) : f (Fin.cons false x) = g (Fin.cons false x) :=
      h _ (by simpa [active_cons,value] using hx)
    have hhead (b : Bool) : f (Fin.cons b (fun _ : Fin n ↦ false)) = g (Fin.cons b (fun _ : Fin n ↦ false)) :=
      h _ (by rw [active_cons]; cases b <;> simp [active,value])
    simp only [affineFit, ih _ _ h₀, hhead]

theorem quadratic_probes (n : ℕ) (f g : Bits n → Bool)
    (h : ∀ x, active x ≤ 2 → f x = g x) : quadraticFit n f = quadraticFit n g := by
  induction n with
  | zero => simp [quadraticFit,h _ (by simp [active])]
  | succ n ih =>
    have h₀ (x : Bits n) (hx : active x ≤ 2) : f (Fin.cons false x) = g (Fin.cons false x) :=
      h _ (by simpa [active_cons,value] using hx)
    have h₁ (x : Bits n) (hx : active x ≤ 1) : f (Fin.cons true x) = g (Fin.cons true x) :=
      h _ (by rw [active_cons]; change 1+active x ≤ 2; omega)
    have hd (x : Bits n) (hx : active x ≤ 1) :
        (f (Fin.cons true x) ^^ f (Fin.cons false x)) = (g (Fin.cons true x) ^^ g (Fin.cons false x)) := by
      rw [h₁ x hx,h₀ x (by omega)]
    simp only [quadraticFit,ih _ _ h₀,affine_probes _ _ _ hd]

/-- The input coordinates can describe a smaller affine hull. Restricting
the original phase to that hull preserves exact recovery from these probes. -/
theorem recover_on_hull {ι} (n : ℕ) (q : Quad ι) (v : ι → Aff (Fin n)) (raw : Bits n → Bool)
    (h : ∀ x, active x ≤ 2 → raw x = q.eval (fun i ↦ (v i).eval x)) (x : Bits n) :
    (quadraticFit n raw).eval x = q.eval (fun i ↦ (v i).eval x) := by
  have he : quadraticFit n raw = quadraticFit n (q.sub v).eval :=
    quadratic_probes n _ _ (fun z hz ↦ (h z hz).trans (q.eval_sub v z).symm)
  rw [he,quadratic_exact,Quad.eval_sub]

#print axioms affine_exact
#print axioms quadratic_probes
#print axioms recover_on_hull
end RawInterpolation
