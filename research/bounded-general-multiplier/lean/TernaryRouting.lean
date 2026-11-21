import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Ring
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

namespace TernaryRouting

/- Each primitive exchanges two opposite-bank packets and reverses their order. -/
structure Four (α : Type*) where
  a : α
  b : α
  c : α
  d : α

def crosses (r : α → α) (s : Four α) : Four α :=
  let ac : Four α := ⟨r s.c, s.b, r s.a, s.d⟩
  let bd : Four α := ⟨ac.a, r ac.d, ac.c, r ac.b⟩
  let ad : Four α := ⟨r bd.d, bd.b, bd.c, r bd.a⟩
  ⟨ad.a, r ad.c, r ad.b, ad.d⟩

theorem four_opposite_exchanges (r : α → α) (h : ∀ x, r (r x) = x) (s : Four α) :
    crosses r s = ⟨s.b, s.a, s.d, s.c⟩ := by
  simp [crosses, h]

theorem nonzero_low_pivot {K ι : Type*} [Semiring K] [Nontrivial K] [Fintype ι]
    (u v : ι → K) (trace : ∑ i, u i * v i = 1) : ∃ i, u i * v i ≠ 0 := by
  classical
  by_contra none
  have vanishes (i : ι) : u i * v i = 0 := by
    by_contra nonzero
    exact none ⟨i, nonzero⟩
  simp [vanishes] at trace

/- Each new factor is the fraction of choices outside the previous span. -/
def regularDensity : Nat → ℚ
  | 0 => 1
  | n + 1 => regularDensity n * (1 - (1 / 3 : ℚ) ^ (n + 1))

theorem density_bounds (n : Nat) :
    (1 + (1 / 3 : ℚ)^n) / 2 ≤ regularDensity n ∧ regularDensity n ≤ 1 := by
  induction n with
  | zero => norm_num [regularDensity]
  | succ n ih =>
    obtain ⟨lo, hi⟩ := ih
    have nonneg : 0 ≤ (1 / 3 : ℚ)^n := by positivity
    have mass : 0 ≤ regularDensity n := by linarith
    have discarded := mul_le_mul_of_nonneg_right hi nonneg
    rw [regularDensity, pow_succ]
    constructor <;> nlinarith [mul_nonneg mass nonneg]

theorem more_than_half (n : Nat) : 1 / 2 < regularDensity n := by
  have positive : 0 < (1 / 3 : ℚ)^n := by positivity
  linarith [(density_bounds n).1]

theorem regular_right {M : Type*} [Monoid M] (s : Mˣ) (g : M) :
    IsUnit (g * (s : M)) ↔ IsUnit g := by
  constructor
  · intro h
    simpa [mul_assoc] using h.mul s⁻¹.isUnit
  · intro h
    exact h.mul s.isUnit

section Cube
variable {X Y Z : Type*}

noncomputable def pad (p : X → Prop) (empty : Z) (f : {x // p x} → Y → Z) (x : X) (y : Y) : Z := by
  classical
  exact if h : p x then f ⟨x, h⟩ y else empty

def moveHigh (h : X → Y ≃ Y) (f : X → Y → Z) (x : X) (y : Y) : Z :=
  f x ((h x).symm y)

def moveLow (s : X ≃ X) (f : X → Y → Z) (x : X) (y : Y) : Z :=
  f (s.symm x) y

theorem lowBeforeSource (p : X → Prop) (s : X ≃ X) (stable : ∀ x, p (s x) ↔ p x) (x : X) :
    p (s.symm x) ↔ p x := by
  simpa using (stable (s.symm x)).symm

theorem full_cube (p : X → Prop) (s : X ≃ X) (stable : ∀ x, p (s x) ↔ p x)
    (h : X → Y ≃ Y) (empty : Z) (f : {x // p x} → Y → Z) :
    moveLow s (moveHigh h (pad p empty f)) =
      pad p empty (fun x y => f ⟨s.symm x, (lowBeforeSource p s stable x).mpr x.property⟩
        ((h (s.symm x)).symm y)) := by
  funext x y
  by_cases hx : p x
  · have source := (lowBeforeSource p s stable x).mpr hx
    simp [moveLow, moveHigh, pad, hx, source]
  · have source : ¬p (s.symm x) := fun h => hx ((lowBeforeSource p s stable x).mp h)
    simp [moveLow, moveHigh, pad, hx, source]

end Cube

variable {R ι : Type*} [CommRing R] [Fintype ι]

/- Work in normalized head coordinates and reflected tail coordinates.
   Index zero is separate from the other indices in ι. -/
@[ext] structure State (R ι : Type*) where
  head : R
  tail : R
  heads : ι → R
  tails : ι → R

def delta (h : R) (c : ι → R) (z : State R ι) : R :=
  h * (z.tail - z.head) + ∑ i, c i * (z.tails i - z.heads i)

def job (h : R) (b c : ι → R) (z : State R ι) : State R ι :=
  let t := delta h c z
  ⟨z.head + t, z.tail - t, fun i => z.heads i + b i * t, fun i => z.tails i - b i * t⟩

def prepare (h : Rˣ) (b c : ι → R) (z : State R ι) : State R ι :=
  ⟨z.head,
   z.tail + (↑(h⁻¹) : R) * ∑ i, c i * (z.tails i - z.heads i + b i * z.head),
   fun i => z.heads i - b i * z.head, fun i => z.tails i + b i * z.head⟩

def undo (h : Rˣ) (b c : ι → R) (z : State R ι) : State R ι :=
  ⟨z.head,
   z.tail - (↑(h⁻¹) : R) * ∑ i, c i * (z.tails i - z.heads i - b i * z.head),
   fun i => z.heads i + b i * z.head, fun i => z.tails i - b i * z.head⟩

def central (h : Rˣ) (z : State R ι) : State R ι :=
  ⟨(↑h : R) * z.tail, (↑(h⁻¹) : R) * z.head, z.heads, z.tails⟩

theorem restores (h : Rˣ) (b c : ι → R) (z : State R ι) :
    undo h b c (prepare h b c z) = z := by
  have terms (i : ι) : z.tails i + b i * z.head - (z.heads i - b i * z.head) - b i * z.head =
      z.tails i - z.heads i + b i * z.head := by ring
  ext i <;> simp [undo, prepare, terms]

private theorem sum_linear (b c x : ι → R) (t : R) :
    (∑ i, c i * (x i + b i * t)) = (∑ i, c i * x i) + (∑ i, c i * b i) * t := by
  simp [mul_add, ← mul_assoc, Finset.sum_add_distrib, Finset.sum_mul]

theorem pivot_tail (h : Rˣ) (b c : ι → R) (z : State R ι)
    (trace : (↑h : R) + ∑ i, c i * b i = 1) :
    (prepare h b c z).tail = (↑(h⁻¹) : R) * (z.head + delta (↑h) c z) := by
  change z.tail + (↑(h⁻¹) : R) * (∑ i, c i * ((z.tails i - z.heads i) + b i * z.head)) = _
  rw [sum_linear]
  have s : (∑ i, c i * b i) = 1 - (↑h : R) := by
    rw [← trace]
    ring
  rw [s]
  unfold delta
  have u : (↑(h⁻¹) : R) * (↑h : R) = 1 := h.inv_mul
  linear_combination -z.tail * u

theorem negate_delta (h : R) (b c : ι → R) (z : State R ι)
    (trace : h + ∑ i, c i * b i = 1) :
    delta h c (job h b c z) = -delta h c z := by
  let d := delta h c z
  change h * (z.tail - d - (z.head + d)) +
    (∑ i, c i * (z.tails i - b i * d - (z.heads i + b i * d))) = -d
  have change_sum : (∑ i, c i * (z.tails i - b i * d - (z.heads i + b i * d))) =
      (∑ i, c i * (z.tails i - z.heads i)) + (∑ i, c i * b i) * (-(2 * d)) := by
    rw [← sum_linear]
    apply Finset.sum_congr rfl
    intro i _
    ring
  rw [change_sum]
  have s : (∑ i, c i * b i) = 1 - h := by rw [← trace]; ring
  rw [s]
  dsimp [d, delta]
  ring

theorem prepare_intertwines (h : Rˣ) (b c : ι → R) (z : State R ι)
    (trace : (↑h : R) + ∑ i, c i * b i = 1) :
    prepare h b c (job (↑h) b c z) = central h (prepare h b c z) := by
  apply State.ext
  · change z.head + delta (↑h) c z = (↑h : R) * (prepare h b c z).tail
    rw [pivot_tail h b c z trace, ← mul_assoc, h.mul_inv, one_mul]
  · change (prepare h b c (job (↑h) b c z)).tail = (↑(h⁻¹) : R) * z.head
    rw [pivot_tail h b c _ trace, negate_delta _ b c z trace]
    simp [job]
  · funext i
    simp [prepare, job, central]
    ring
  · funext i
    simp [prepare, job, central]
    ring

theorem thin_leaf (h : Rˣ) (b c : ι → R) (z : State R ι)
    (trace : (↑h : R) + ∑ i, c i * b i = 1) :
    undo h b c (central h (prepare h b c z)) = job (↑h) b c z := by
  rw [← prepare_intertwines h b c z trace, restores]

def normalized (a : Rˣ) (A : ι → Rˣ) (z : State R ι) : State R ι :=
  ⟨(↑(a⁻¹) : R) * z.head, z.tail, fun i => (↑((A i)⁻¹) : R) * z.heads i, z.tails⟩

def weighted (a : Rˣ) (A : ι → Rˣ) (z : State R ι) : State R ι :=
  ⟨(↑a : R) * z.head, z.tail, fun i => (↑(A i) : R) * z.heads i, z.tails⟩

def physicalPrepare (h a : Rˣ) (A : ι → Rˣ) (b c : ι → R) (z : State R ι) : State R ι :=
  let p := (↑(a⁻¹) : R) * z.head
  let heads i := z.heads i - (↑(A i) : R) * (b i * p)
  ⟨z.head, z.tail + (↑(h⁻¹) : R) * ∑ i, c i * (z.tails i - (↑((A i)⁻¹) : R) * heads i),
    heads, fun i => z.tails i + b i * p⟩

theorem physical_prepare (h a : Rˣ) (A : ι → Rˣ) (b c : ι → R) (z : State R ι) :
    normalized a A (physicalPrepare h a A b c z) = prepare h b c (normalized a A z) := by
  have cancel (i : ι) (x y : R) : (↑((A i)⁻¹) : R) * (x - (↑(A i) : R) * y) =
      (↑((A i)⁻¹) : R) * x - y := by rw [mul_sub, ← mul_assoc, (A i).inv_mul, one_mul]
  ext i <;> simp [normalized, physicalPrepare, prepare, cancel, sub_sub_eq_add_sub, add_sub_assoc, sub_add]

def physicalCentral (h a : Rˣ) (z : State R ι) : State R ι :=
  ⟨((↑a : R) * (↑h : R)) * z.tail, ((↑(h⁻¹) : R) * (↑(a⁻¹) : R)) * z.head, z.heads, z.tails⟩

omit [Fintype ι] in
theorem physical_center (h a : Rˣ) (A : ι → Rˣ) (z : State R ι) :
    normalized a A (physicalCentral h a z) = central h (normalized a A z) := by
  ext i <;> simp [normalized, physicalCentral, central, ← mul_assoc]

theorem weighted_thin_leaf (h a : Rˣ) (A : ι → Rˣ) (b c : ι → R) (z : State R ι)
    (trace : (↑h : R) + ∑ i, c i * b i = 1) :
    weighted a A (undo h b c (normalized a A (physicalCentral h a (physicalPrepare h a A b c z)))) =
      weighted a A (job (↑h) b c (normalized a A z)) := by
  rw [physical_center, physical_prepare, thin_leaf h b c _ trace]

#print axioms four_opposite_exchanges
#print axioms nonzero_low_pivot
#print axioms more_than_half
#print axioms regular_right
#print axioms full_cube
#print axioms thin_leaf
#print axioms weighted_thin_leaf

end TernaryRouting
