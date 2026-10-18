import Std
import Init.Grind.CommRing.Basic

set_option autoImplicit false

/-!
The exact chain and closure steps in PR846 and PR985.
The indices are natural numbers. Only entries below the stated length are used.
-/

namespace CyclicSchur

universe u
variable {α : Type u}

def predecessor (n w i : Nat) : Nat :=
  if i < w then n - w + i else i - w

def endpoint (n w k : Nat) : Nat := n - w + k

def tail (n w : Nat) (y : Nat → α) : Nat → α :=
  fun k => y (endpoint n w k)

def chain (w : Nat) (hw : 0 < w) (f : Nat → α → α) (i : Nat) (t : α) : α :=
  if i < w then f i t else f i (chain w hw f (i - w) t)
termination_by i
decreasing_by omega

def forward (w : Nat) (hw : 0 < w) (f : Nat → α → α)
    (seed : Nat → α) (i : Nat) : α :=
  if i < w then f i (seed i) else f i (forward w hw f seed (i - w))
termination_by i
decreasing_by omega

def IsSolution (n w : Nat) (f : Nat → α → α) (y : Nat → α) : Prop :=
  ∀ i, i < n → y i = f i (y (predecessor n w i))

def IsClosure (n w : Nat) (hw : 0 < w) (f : Nat → α → α)
    (Y : Nat → α) : Prop :=
  ∀ k, k < w → Y k = chain w hw f (endpoint n w k) (Y ((k + n) % w))

theorem predecessor_lt {n w i : Nat} (hw : w ≤ n) (hi : i < n) :
    predecessor n w i < n := by
  simp only [predecessor]
  split <;> omega

theorem predecessor_mod {n w i : Nat} (hw : w ≤ n) (hi : i < n) :
    predecessor n w i = (i + n - w) % n := by
  by_cases h : i < w
  · rw [predecessor, if_pos h, Nat.mod_eq_of_lt (by omega)]
    omega
  · have he : i + n - w = n + (i - w) := by omega
    rw [predecessor, if_neg h, he, Nat.add_mod_left,
      Nat.mod_eq_of_lt (by omega)]

theorem endpoint_lt {n w k : Nat} (hw : w ≤ n) (hk : k < w) :
    endpoint n w k < n := by
  unfold endpoint
  omega

theorem endpoint_mod {n w k : Nat} (hw : w ≤ n) :
    endpoint n w k % w = (k + n) % w := by
  have he : k + n = endpoint n w k + w := by unfold endpoint; omega
  rw [he, Nat.add_mod_right]

theorem sub_stride_mod {w i : Nat} (h : w ≤ i) :
    (i - w) % w = i % w := by
  have he : i = (i - w) + w := by omega
  conv => rhs; rw [he, Nat.add_mod_right]

theorem forward_eq_chain (w : Nat) (hw : 0 < w) (f : Nat → α → α)
    (seed : Nat → α) (i : Nat) :
    forward w hw f seed i = chain w hw f i (seed (i % w)) := by
  induction i using Nat.strongRecOn with
  | ind i ih =>
    rw [forward, chain]
    by_cases hi : i < w
    · simp only [if_pos hi, Nat.mod_eq_of_lt hi]
    · simp only [if_neg hi]
      rw [ih (i - w) (by omega), sub_stride_mod (by omega)]

theorem solution_reconstruct {n w : Nat} (hw : 0 < w)
    {f : Nat → α → α} {y : Nat → α} (hy : IsSolution n w f y)
    (i : Nat) (hi : i < n) :
    y i = forward w hw f (tail n w y) i := by
  induction i using Nat.strongRecOn with
  | ind i ih =>
    rw [hy i hi, forward]
    by_cases hs : i < w
    · simp only [if_pos hs, predecessor, tail, endpoint]
    · simp only [if_neg hs, predecessor]
      rw [ih (i - w) (by omega) (by omega)]

theorem solution_restrict {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    {f : Nat → α → α} {y : Nat → α} (hy : IsSolution n w f y) :
    IsClosure n w hw f (tail n w y) := by
  intro k hk
  change y (endpoint n w k) = _
  rw [solution_reconstruct hw hy _ (endpoint_lt hwn hk),
    forward_eq_chain, endpoint_mod hwn]

theorem closure_reconstruct_tail {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    {f : Nat → α → α} {Y : Nat → α} (hY : IsClosure n w hw f Y)
    (k : Nat) (hk : k < w) :
    tail n w (forward w hw f Y) k = Y k := by
  unfold tail
  rw [forward_eq_chain, endpoint_mod hwn]
  exact (hY k hk).symm

theorem closure_reconstruct {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    {f : Nat → α → α} {Y : Nat → α} (hY : IsClosure n w hw f Y) :
    IsSolution n w f (forward w hw f Y) := by
  intro i hi
  rw [forward]
  by_cases hs : i < w
  · simp only [if_pos hs, predecessor]
    exact congrArg (f i) (closure_reconstruct_tail hw hwn hY i hs).symm
  · simp only [if_neg hs, predecessor]

theorem schur_iff {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    (f : Nat → α → α) (y : Nat → α) :
    IsSolution n w f y ↔
      IsClosure n w hw f (tail n w y) ∧
      ∀ i, i < n → y i = forward w hw f (tail n w y) i := by
  constructor
  · intro hy
    exact ⟨solution_restrict hw hwn hy, solution_reconstruct hw hy⟩
  · rintro ⟨hY, hr⟩
    have hs := closure_reconstruct hw hwn hY
    intro i hi
    rw [hr i hi, hs i hi, ← hr _ (predecessor_lt hwn hi)]

/- The normalized child stride is the natural-number form of (-n) mod w. -/
def childStride (n w : Nat) : Nat := (w - n % w) % w

theorem childStride_lt {n w : Nat} (hw : 0 < w) : childStride n w < w :=
  Nat.mod_lt _ hw

theorem child_predecessor {n w k : Nat} (hw : 0 < w) (hk : k < w) :
    predecessor w (childStride n w) k = (k + n) % w := by
  rw [predecessor_mod (Nat.le_of_lt (childStride_lt hw)) hk]
  have hr : n % w < w := Nat.mod_lt n hw
  by_cases hz : n % w = 0
  · simp only [childStride, hz, Nat.sub_zero, Nat.mod_self, Nat.sub_zero,
      Nat.add_mod_right]
    rw [Nat.add_mod, hz, Nat.add_zero, Nat.mod_mod]
  · have hc : w - n % w < w := by omega
    simp only [childStride, Nat.mod_eq_of_lt hc]
    have he : k + w - (w - n % w) = k + n % w := by omega
    rw [he, Nat.add_mod k n w, Nat.mod_eq_of_lt hk]

theorem closure_is_child_system {n w : Nat} (hw : 0 < w)
    (f : Nat → α → α) (Y : Nat → α) :
    IsClosure n w hw f Y ↔
      IsSolution w (childStride n w) (fun k => chain w hw f (endpoint n w k)) Y := by
  constructor <;> intro h k hk
  · simpa only [child_predecessor hw hk] using h k hk
  · simpa only [child_predecessor hw hk] using h k hk

/- Each step writes one entry. The lagged read uses the current array. -/
def scanPass (w : Nat) (f : Nat → α → α) (seed initial : Nat → α) :
    Nat → Nat → α
  | 0 => initial
  | count + 1 => fun i =>
      if i = count then
        f count (if count < w then seed count
          else scanPass w f seed initial count (count - w))
      else scanPass w f seed initial count i

theorem scanPass_prefix {w : Nat} (hw : 0 < w) (f : Nat → α → α)
    (seed initial : Nat → α) (count i : Nat) (hi : i < count) :
    scanPass w f seed initial count i = forward w hw f seed i := by
  induction count generalizing i with
  | zero => omega
  | succ count ih =>
    by_cases he : i = count
    · subst i
      simp only [scanPass, if_pos rfl, ite_true]
      rw [forward]
      by_cases hs : count < w
      · simp only [if_pos hs]
      · simp only [if_neg hs]
        rw [ih (count - w) (by omega)]
    · simp only [scanPass, if_neg he]
      exact ih i (by omega)

theorem scanPass_suffix (w : Nat) (f : Nat → α → α)
    (seed initial : Nat → α) (count i : Nat) (hi : count ≤ i) :
    scanPass w f seed initial count i = initial i := by
  induction count with
  | zero => rfl
  | succ count ih =>
    have he : i ≠ count := by omega
    simp only [scanPass, if_neg he]
    exact ih (by omega)

section Scalar

open Lean.Grind

variable {R : Type u} [Semiring R]

def scalarStep (x b : Nat → R) (i : Nat) (t : R) : R := x i + b i * t

def zeroSeed (w : Nat) (hw : 0 < w) (x b : Nat → R) (i : Nat) : R :=
  if i < w then x i else x i + b i * zeroSeed w hw x b (i - w)
termination_by i
decreasing_by omega

def chainProduct (w : Nat) (hw : 0 < w) (b : Nat → R) (i : Nat) : R :=
  if i < w then b i else b i * chainProduct w hw b (i - w)
termination_by i
decreasing_by omega

theorem chain_affine (w : Nat) (hw : 0 < w) (x b : Nat → R) (i : Nat) (t : R) :
    chain w hw (scalarStep x b) i t =
      zeroSeed w hw x b i + chainProduct w hw b i * t := by
  induction i using Nat.strongRecOn with
  | ind i ih =>
    rw [chain, zeroSeed, chainProduct]
    by_cases hi : i < w
    · simp only [if_pos hi, scalarStep]
    · simp only [if_neg hi, scalarStep]
      rw [ih (i - w) (by omega), Semiring.left_distrib,
        ← Semiring.mul_assoc, Semiring.add_assoc]

theorem forward_affine (w : Nat) (hw : 0 < w) (x b seed : Nat → R) (i : Nat) :
    forward w hw (scalarStep x b) seed i =
      zeroSeed w hw x b i + chainProduct w hw b i * seed (i % w) := by
  rw [forward_eq_chain, chain_affine]

def pairStep (x b : Nat → R) (i : Nat) (v : R × R) : R × R :=
  (x i + b i * v.1, b i * v.2)

theorem forward_pair (w : Nat) (hw : 0 < w) (x b : Nat → R) (i : Nat) :
    forward w hw (pairStep x b) (fun _ => (0, 1)) i =
      (zeroSeed w hw x b i, chainProduct w hw b i) := by
  induction i using Nat.strongRecOn with
  | ind i ih =>
    rw [forward, zeroSeed, chainProduct]
    by_cases hi : i < w
    · simp only [if_pos hi, pairStep, Semiring.mul_zero,
        Semiring.add_zero, Semiring.mul_one]
    · simp only [if_neg hi]
      rw [ih (i - w) (by omega)]
      rfl

/- These are the exact scalar operations in the two source loops. -/
def passA (n w : Nat) (x b : Nat → R) (initial : Nat → R × R) : Nat → R × R :=
  scanPass w (pairStep x b) (fun _ => (0, 1)) initial n

def passC (n w : Nat) (x b Y initial : Nat → R) : Nat → R :=
  scanPass w (scalarStep x b) Y initial n

theorem passA_correct {n w : Nat} (hw : 0 < w) (x b : Nat → R)
    (initial : Nat → R × R) (i : Nat) (hi : i < n) :
    passA n w x b initial i = (zeroSeed w hw x b i, chainProduct w hw b i) := by
  rw [passA, scanPass_prefix hw _ _ _ _ _ hi, forward_pair]

theorem passC_correct {n w : Nat} (hw : 0 < w) (x b Y initial : Nat → R)
    (i : Nat) (hi : i < n) :
    passC n w x b Y initial i =
      zeroSeed w hw x b i + chainProduct w hw b i * Y (i % w) := by
  rw [passC, scanPass_prefix hw _ _ _ _ _ hi, forward_affine]

def ScalarSolution (n w : Nat) (x b y : Nat → R) : Prop :=
  ∀ i, i < n → y i = x i + b i * y ((i + n - w) % n)

def childData (n w : Nat) (hw : 0 < w) (x b : Nat → R) : Nat → R :=
  fun k => zeroSeed w hw x b (endpoint n w k)

def childCoefficient (n w : Nat) (hw : 0 < w) (b : Nat → R) : Nat → R :=
  fun k => chainProduct w hw b (endpoint n w k)

def reconstruct (w : Nat) (hw : 0 < w) (x b Y : Nat → R) (i : Nat) : R :=
  zeroSeed w hw x b i + chainProduct w hw b i * Y (i % w)

theorem scalar_is_solution {n w : Nat} (hwn : w ≤ n) (x b y : Nat → R) :
    ScalarSolution n w x b y ↔ IsSolution n w (scalarStep x b) y := by
  constructor <;> intro h i hi
  · simpa only [scalarStep, predecessor_mod hwn hi] using h i hi
  · simpa only [scalarStep, predecessor_mod hwn hi] using h i hi

theorem scalar_closure {n w : Nat} (hw : 0 < w) (x b Y : Nat → R) :
    IsClosure n w hw (scalarStep x b) Y ↔
      ScalarSolution w (childStride n w) (childData n w hw x b)
        (childCoefficient n w hw b) Y := by
  rw [scalar_is_solution (Nat.le_of_lt (childStride_lt hw))]
  constructor <;> intro h k hk
  · simpa only [chain_affine, scalarStep, childData, childCoefficient,
      child_predecessor hw hk] using h k hk
  · simpa only [chain_affine, scalarStep, childData, childCoefficient,
      child_predecessor hw hk] using h k hk

/- This is the exact Schur identity with the indices used by solve. -/
theorem scalar_schur_iff {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    (x b y : Nat → R) :
    ScalarSolution n w x b y ↔
      ScalarSolution w (childStride n w) (childData n w hw x b)
        (childCoefficient n w hw b) (tail n w y) ∧
      ∀ i, i < n → y i = reconstruct w hw x b (tail n w y) i := by
  rw [scalar_is_solution hwn, schur_iff hw hwn, scalar_closure hw]
  simp only [forward_affine, reconstruct]

theorem scalar_reconstruct {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    {x b Y : Nat → R}
    (hY : ScalarSolution w (childStride n w) (childData n w hw x b)
      (childCoefficient n w hw b) Y) :
    ScalarSolution n w x b (reconstruct w hw x b Y) := by
  apply (scalar_is_solution hwn _ _ _).mpr
  have hc := closure_reconstruct hw hwn ((scalar_closure hw x b Y).mpr hY)
  simpa only [IsSolution, forward_affine, reconstruct] using hc

theorem scalar_reconstruct_tail {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    {x b Y : Nat → R}
    (hY : ScalarSolution w (childStride n w) (childData n w hw x b)
      (childCoefficient n w hw b) Y) (k : Nat) (hk : k < w) :
    tail n w (reconstruct w hw x b Y) k = Y k := by
  have hc := closure_reconstruct_tail hw hwn ((scalar_closure hw x b Y).mpr hY) k hk
  simpa only [tail, forward_affine, reconstruct] using hc

theorem passC_solves_parent {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    {x b Y : Nat → R}
    (hY : ScalarSolution w (childStride n w) (childData n w hw x b)
      (childCoefficient n w hw b) Y) (initial : Nat → R) :
    ScalarSolution n w x b (passC n w x b Y initial) := by
  intro i hi
  have hp : (i + n - w) % n < n := Nat.mod_lt _ (by omega)
  rw [passC_correct hw _ _ _ _ _ hi, passC_correct hw _ _ _ _ _ hp]
  exact scalar_reconstruct hw hwn hY i hi

theorem passA_tail_correct {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    (x b : Nat → R) (initial : Nat → R × R) (k : Nat) (hk : k < w) :
    passA n w x b initial (endpoint n w k) =
      (childData n w hw x b k, childCoefficient n w hw b k) :=
  passA_correct hw x b initial _ (endpoint_lt hwn hk)

theorem scalar_exists_iff {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    (x b : Nat → R) :
    (∃ y, ScalarSolution n w x b y) ↔
      ∃ Y, ScalarSolution w (childStride n w) (childData n w hw x b)
        (childCoefficient n w hw b) Y := by
  constructor
  · rintro ⟨y, hy⟩
    exact ⟨tail n w y, ((scalar_schur_iff hw hwn x b y).mp hy).1⟩
  · rintro ⟨Y, hY⟩
    exact ⟨reconstruct w hw x b Y, scalar_reconstruct hw hwn hY⟩

theorem solutions_eq_iff_tails {n w : Nat} (hw : 0 < w) (hwn : w ≤ n)
    {x b y₁ y₂ : Nat → R} (h₁ : ScalarSolution n w x b y₁)
    (h₂ : ScalarSolution n w x b y₂) :
    (∀ i, i < n → y₁ i = y₂ i) ↔
      ∀ k, k < w → tail n w y₁ k = tail n w y₂ k := by
  constructor
  · intro h k hk
    exact h _ (endpoint_lt hwn hk)
  · intro h i hi
    rw [((scalar_schur_iff hw hwn x b y₁).mp h₁).2 i hi,
      ((scalar_schur_iff hw hwn x b y₂).mp h₂).2 i hi]
    unfold reconstruct
    rw [h _ (Nat.mod_lt _ hw)]

end Scalar

end CyclicSchur
