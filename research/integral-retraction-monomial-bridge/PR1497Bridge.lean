/-
Copyright (c) 2026 Andrey Mas and contributors.
SPDX-License-Identifier: Apache-2.0

PR1497 universal integral-retraction and monomial bridge.
TARGET: official Lean 4.30.0, commit
  d024af099ca4bf2c86f649261ebf59565dc8c622
Only import: Std. No package manager is needed.

STATUS: Locally kernel checked with the exact compiler identified above.
The producer delivered source and diagnostic repairs without running Lean.
Subsequent local replay accepted the universal source, repaired fixtures,
and queried axiom census. See README.md and REPLAY.json for that evidence.

Project credits: Andrey Mas / GPT6Pro for the PR1497 audit;
Brett Halligan (burntout76) and Ninefold for inherited PR1212;
DreamingOfClouds (PR717); themilkman216 (PR968).
Substantial AI mathematical/formalization assistance is disclosed in README.md.
Formalization assistance used GPT-6 Pro, as observed in the ChatGPT browser UI.

All custom algebra structures below contain operations and ordinary algebra
laws only. Kernel/image equality, saturation, and reconstruction are theorems,
not fields. Independent test data is kept in fixtures/Positive.lean.
-/
import Std

set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000

namespace PR1497

universe u v w t

/-! ## 1. Small, explicit abelian-group and homomorphism interfaces -/

structure AbGroup (A : Type u) where
  zero : A
  add : A → A → A
  neg : A → A
  add_assoc : ∀ a b c, add (add a b) c = add a (add b c)
  zero_add : ∀ a, add zero a = a
  add_zero : ∀ a, add a zero = a
  add_comm : ∀ a b, add a b = add b a
  neg_add : ∀ a, add (neg a) a = zero
  add_neg : ∀ a, add a (neg a) = zero

namespace AbGroup

variable {A : Type u} (G : AbGroup A)

def sub (a b : A) : A := G.add a (G.neg b)

theorem add_left_cancel {a b c : A}
    (h : G.add a b = G.add a c) : b = c := by
  have h' := congrArg (fun x => G.add (G.neg a) x) h
  simpa only [← G.add_assoc, G.neg_add, G.zero_add] using h'

theorem add_right_cancel {a b c : A}
    (h : G.add b a = G.add c a) : b = c := by
  apply G.add_left_cancel (a := a)
  calc
    G.add a b = G.add b a := G.add_comm _ _
    _ = G.add c a := h
    _ = G.add a c := G.add_comm _ _

theorem add_left_comm (a b c : A) :
    G.add a (G.add b c) = G.add b (G.add a c) := by
  rw [← G.add_assoc, G.add_comm a b, G.add_assoc]

theorem add_four (a b c d : A) :
    G.add (G.add a b) (G.add c d) =
      G.add (G.add a c) (G.add b d) := by
  rw [G.add_assoc a b (G.add c d), G.add_left_comm b c d,
    ← G.add_assoc a c (G.add b d)]

theorem neg_zero : G.neg G.zero = G.zero := by
  calc
    G.neg G.zero = G.add (G.neg G.zero) G.zero := (G.add_zero _).symm
    _ = G.zero := G.neg_add _

theorem neg_neg (a : A) : G.neg (G.neg a) = a := by
  apply G.add_right_cancel (a := G.neg a)
  rw [G.neg_add, G.add_neg]

theorem neg_add_distrib (a b : A) :
    G.neg (G.add a b) = G.add (G.neg a) (G.neg b) := by
  apply G.add_left_cancel (a := G.add a b)
  rw [G.add_neg, G.add_four, G.add_neg, G.add_neg, G.zero_add]

theorem sub_zero (a : A) : G.sub a G.zero = a := by
  rw [sub, G.neg_zero, G.add_zero]

theorem sub_self (a : A) : G.sub a a = G.zero := G.add_neg a

theorem sub_add_cancel (a b : A) : G.add (G.sub a b) b = a := by
  rw [sub, G.add_assoc, G.neg_add, G.add_zero]

theorem add_sub_cancel (a b : A) : G.sub (G.add a b) b = a := by
  rw [sub, G.add_assoc, G.add_neg, G.add_zero]

theorem sub_eq_zero_iff (a b : A) : G.sub a b = G.zero ↔ a = b := by
  constructor
  · intro h
    have h' := congrArg (fun x => G.add x b) h
    simpa only [G.sub_add_cancel, G.zero_add] using h'
  · intro h
    subst b
    exact G.sub_self a

theorem eq_of_sub_eq (a b c : A) (h : G.sub a b = c) :
    a = G.add b c := by
  calc
    a = G.add (G.sub a b) b := (G.sub_add_cancel a b).symm
    _ = G.add c b := congrArg (fun x => G.add x b) h
    _ = G.add b c := G.add_comm c b

/-- Repeated addition, with the empty sum equal to zero. -/
def nsmul (G : AbGroup A) : Nat → A → A
  | 0, _ => G.zero
  | n + 1, a => G.add (nsmul G n a) a

/-- Ordinary integral multiple: negative coefficients use the group inverse. -/
def zsmul : Int → A → A
  | .ofNat n, a => G.nsmul n a
  | .negSucc n, a => G.neg (G.nsmul (n + 1) a)

theorem nsmul_zero (n : Nat) : G.nsmul n G.zero = G.zero := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [nsmul, ih, G.add_zero]

theorem zsmul_zero (a : A) : G.zsmul 0 a = G.zero := rfl

theorem zsmul_zero_right (k : Int) : G.zsmul k G.zero = G.zero := by
  cases k with
  | ofNat n => exact G.nsmul_zero n
  | negSucc n => simp only [zsmul, G.nsmul_zero, G.neg_zero]

theorem zsmul_one (a : A) : G.zsmul 1 a = a := by
  change G.add G.zero a = a
  exact G.zero_add a

/-- A two-sided integer induction principle, proved from the constructors. -/
theorem int_induction (C : Int → Prop) (h0 : C 0)
    (up : ∀ k, C k → C (k + 1))
    (down : ∀ k, C k → C (k - 1)) (k : Int) : C k := by
  cases k with
  | ofNat n =>
    induction n with
    | zero => exact h0
    | succ n ih => exact up (Int.ofNat n) ih
  | negSucc n =>
    induction n with
    | zero => exact down 0 h0
    | succ n ih => exact down (Int.negSucc n) ih

theorem zsmul_succ (k : Int) (a : A) :
    G.zsmul (k + 1) a = G.add (G.zsmul k a) a := by
  cases k with
  | ofNat n => rfl
  | negSucc n =>
    cases n with
    | zero =>
      change G.zero = G.add (G.neg (G.add G.zero a)) a
      rw [G.zero_add, G.neg_add]
    | succ n =>
      have hk : Int.negSucc (n + 1) + 1 = Int.negSucc n := by omega
      rw [hk]
      change G.neg (G.nsmul (n + 1) a) =
        G.add (G.neg (G.add (G.nsmul (n + 1) a) a)) a
      rw [G.neg_add_distrib (G.nsmul (n + 1) a) a,
        G.add_assoc, G.neg_add a, G.add_zero]

theorem zsmul_pred (k : Int) (a : A) :
    G.zsmul (k - 1) a = G.add (G.zsmul k a) (G.neg a) := by
  have hs := G.zsmul_succ (k - 1) a
  have hk : (k - 1) + 1 = k := by omega
  rw [hk] at hs
  apply G.add_right_cancel (a := a)
  calc
    G.add (G.zsmul (k - 1) a) a = G.zsmul k a := hs.symm
    _ = G.add (G.add (G.zsmul k a) (G.neg a)) a := by
      rw [G.add_assoc, G.neg_add, G.add_zero]

/-- The exponent-addition law is derived, not assumed. -/
theorem zsmul_add (k l : Int) (a : A) :
    G.zsmul (k + l) a = G.add (G.zsmul k a) (G.zsmul l a) := by
  apply int_induction (fun j =>
    G.zsmul (k + j) a = G.add (G.zsmul k a) (G.zsmul j a))
  · rw [Int.add_zero, G.zsmul_zero, G.add_zero]
  · intro j ih
    have hk : k + (j + 1) = (k + j) + 1 := by omega
    rw [hk, G.zsmul_succ (k + j) a, G.zsmul_succ j a, ih, G.add_assoc]
  · intro j ih
    have hk : k + (j - 1) = (k + j) - 1 := by omega
    rw [hk, G.zsmul_pred (k + j) a, G.zsmul_pred j a, ih, G.add_assoc]

end AbGroup

structure Hom {A : Type u} {B : Type v}
    (GA : AbGroup A) (GB : AbGroup B) where
  run : A → B
  map_zero : run GA.zero = GB.zero
  map_add : ∀ a b, run (GA.add a b) = GB.add (run a) (run b)

namespace Hom

variable {A : Type u} {B : Type v} {C : Type w}
variable {GA : AbGroup A} {GB : AbGroup B} {GC : AbGroup C}

def id (G : AbGroup A) : Hom G G where
  run := fun a => a
  map_zero := rfl
  map_add := fun _ _ => rfl

def comp (g : Hom GB GC) (f : Hom GA GB) : Hom GA GC where
  run := fun a => g.run (f.run a)
  map_zero := by rw [f.map_zero, g.map_zero]
  map_add := by intro a b; rw [f.map_add, g.map_add]

theorem ext (f g : Hom GA GB) (h : ∀ a, f.run a = g.run a) : f = g := by
  cases f with
  | mk ff f0 fa =>
    cases g with
    | mk gg g0 ga =>
      have hf : ff = gg := funext h
      cases hf
      rfl

theorem map_neg (f : Hom GA GB) (a : A) :
    f.run (GA.neg a) = GB.neg (f.run a) := by
  apply GB.add_right_cancel (a := f.run a)
  rw [← f.map_add, GA.neg_add, f.map_zero, GB.neg_add]

theorem map_sub (f : Hom GA GB) (a b : A) :
    f.run (GA.sub a b) = GB.sub (f.run a) (f.run b) := by
  rw [AbGroup.sub, f.map_add, f.map_neg, AbGroup.sub]

theorem map_nsmul (f : Hom GA GB) (n : Nat) (a : A) :
    f.run (GA.nsmul n a) = GB.nsmul n (f.run a) := by
  induction n with
  | zero => exact f.map_zero
  | succ n ih =>
    simp only [AbGroup.nsmul, f.map_add, ih]

theorem map_zsmul (f : Hom GA GB) (k : Int) (a : A) :
    f.run (GA.zsmul k a) = GB.zsmul k (f.run a) := by
  cases k with
  | ofNat n => exact f.map_nsmul n a
  | negSucc n =>
    simp only [AbGroup.zsmul, f.map_neg, f.map_nsmul]

end Hom

/-! ## 2. Finite sums, honest integer rows, and ordinary matrix products -/

/-- Sum over all of Fin n, in increasing coordinate order. -/
def fsum {A : Type u} (G : AbGroup A) :
    (n : Nat) → (Fin n → A) → A
  | 0, _ => G.zero
  | n + 1, f => G.add (f 0) (fsum G n (fun i => f i.succ))

namespace Finite

variable {A : Type u} {B : Type v} (G : AbGroup A)

theorem sum_congr {n : Nat} (f g : Fin n → A)
    (h : ∀ i, f i = g i) : fsum G n f = fsum G n g :=
  congrArg (fsum G n) (funext h)

theorem sum_zero (n : Nat) : fsum G n (fun _ => G.zero) = G.zero := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [fsum, ih, G.add_zero]

theorem sum_add (n : Nat) (f g : Fin n → A) :
    fsum G n (fun i => G.add (f i) (g i)) =
      G.add (fsum G n f) (fsum G n g) := by
  revert f g
  induction n with
  | zero =>
    intro f g
    exact (G.add_zero G.zero).symm
  | succ n ih =>
    intro f g
    change G.add (G.add (f 0) (g 0))
      (fsum G n (fun i => G.add (f i.succ) (g i.succ))) =
      G.add (G.add (f 0) (fsum G n (fun i => f i.succ)))
        (G.add (g 0) (fsum G n (fun i => g i.succ)))
    rw [ih]
    exact G.add_four _ _ _ _

theorem sum_neg (n : Nat) (f : Fin n → A) :
    fsum G n (fun i => G.neg (f i)) = G.neg (fsum G n f) := by
  revert f
  induction n with
  | zero =>
    intro f
    exact G.neg_zero.symm
  | succ n ih =>
    intro f
    change G.add (G.neg (f 0)) (fsum G n (fun i => G.neg (f i.succ))) =
      G.neg (G.add (f 0) (fsum G n (fun i => f i.succ)))
    rw [ih, G.neg_add_distrib]

theorem sum_sub (n : Nat) (f g : Fin n → A) :
    fsum G n (fun i => G.sub (f i) (g i)) =
      G.sub (fsum G n f) (fsum G n g) := by
  simp only [AbGroup.sub, sum_add, sum_neg]

theorem sum_swap (n m : Nat) (f : Fin n → Fin m → A) :
    fsum G n (fun i => fsum G m (fun j => f i j)) =
      fsum G m (fun j => fsum G n (fun i => f i j)) := by
  revert f
  induction n with
  | zero =>
    intro f
    simp only [fsum, sum_zero]
  | succ n ih =>
    intro f
    change G.add (fsum G m (fun j => f 0 j))
      (fsum G n (fun i => fsum G m (fun j => f i.succ j))) =
      fsum G m (fun j => G.add (f 0 j)
        (fsum G n (fun i => f i.succ j)))
    rw [sum_add, ih]

theorem sum_single (n : Nat) (j : Fin n) (a : A) :
    fsum G n (fun i => if i = j then a else G.zero) = a := by
  revert j
  induction n with
  | zero =>
    intro j
    exact (Nat.not_lt_zero j.val j.isLt).elim
  | succ n ih =>
    intro j
    refine Fin.cases ?_ (fun k => ?_) j
    · simp only [fsum, eq_self, ite_true, Fin.succ_ne_zero, if_false,
        sum_zero, G.add_zero]
    · have h0 : (0 : Fin (n + 1)) ≠ k.succ := Ne.symm (Fin.succ_ne_zero k)
      simp only [fsum, if_neg h0, Fin.succ_inj, ih, G.zero_add]

theorem map_sum {GA : AbGroup A} {GB : AbGroup B}
    (h : Hom GA GB) (n : Nat) (f : Fin n → A) :
    h.run (fsum GA n f) = fsum GB n (fun i => h.run (f i)) := by
  revert f
  induction n with
  | zero =>
    intro f
    exact h.map_zero
  | succ n ih =>
    intro f
    change h.run (GA.add (f 0) (fsum GA n (fun i => f i.succ))) =
      GB.add (h.run (f 0)) (fsum GB n (fun i => h.run (f i.succ)))
    rw [h.map_add, ih]

end Finite

/-- This is the usual additive group of Lean's built-in integers. -/
def intGroup : AbGroup Int where
  zero := 0
  add := (· + ·)
  neg := Neg.neg
  add_assoc := Int.add_assoc
  zero_add := Int.zero_add
  add_zero := Int.add_zero
  add_comm := Int.add_comm
  neg_add := Int.add_left_neg
  add_neg := Int.add_right_neg

/-- Pointwise abelian group; in particular the group on Fin n → Int. -/
def functionGroup {I : Type u} {A : Type v} (G : AbGroup A) :
    AbGroup (I → A) where
  zero := fun _ => G.zero
  add := fun a b i => G.add (a i) (b i)
  neg := fun a i => G.neg (a i)
  add_assoc := by intro a b c; funext i; exact G.add_assoc _ _ _
  zero_add := by intro a; funext i; exact G.zero_add _
  add_zero := by intro a; funext i; exact G.add_zero _
  add_comm := by intro a b; funext i; exact G.add_comm _ _
  neg_add := by intro a; funext i; exact G.neg_add _
  add_neg := by intro a; funext i; exact G.add_neg _

abbrev Row (n : Nat) := Fin n → Int
abbrev Mat (m n : Nat) := Fin m → Fin n → Int

def rowGroup (n : Nat) : AbGroup (Row n) := functionGroup intGroup

def scale {n : Nat} (k : Int) (v : Row n) : Row n := fun i => k * v i

def basis (n : Nat) (i : Fin n) : Row n := fun j => if j = i then 1 else 0

def eye (n : Nat) : Mat n n := fun i => basis n i

def zeroMat (m n : Nat) : Mat m n := fun _ _ => 0

def matSub {m n : Nat} (A B : Mat m n) : Mat m n := fun i j => A i j - B i j

/-- Ordinary row-vector multiplication: (v A)_j = sum_i v_i A_ij. -/
def rowMul {m n : Nat} (v : Row m) (A : Mat m n) : Row n :=
  fun j => fsum intGroup m (fun i => v i * A i j)

/-- Ordinary matrix multiplication, with the left index the row index. -/
def matMul {m n d : Nat} (A : Mat m n) (B : Mat n d) : Mat m d :=
  fun i => rowMul (A i) B

namespace Rows

theorem sum_apply {I : Type u} {A : Type v} (G : AbGroup A)
    (n : Nat) (f : Fin n → I → A) (j : I) :
    (fsum (functionGroup G) n f) j = fsum G n (fun i => f i j) := by
  revert f
  induction n with
  | zero =>
    intro f
    rfl
  | succ n ih =>
    intro f
    change G.add (f 0 j) ((fsum (functionGroup G) n
      (fun i => f i.succ)) j) =
      G.add (f 0 j) (fsum G n (fun i => f i.succ j))
    rw [ih]

theorem nsmul_apply {I : Type u} {A : Type v} (G : AbGroup A)
    (n : Nat) (f : I → A) (j : I) :
    ((functionGroup G).nsmul n f) j = G.nsmul n (f j) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    change G.add (((functionGroup G).nsmul n f) j) (f j) =
      G.add (G.nsmul n (f j)) (f j)
    rw [ih]

theorem zsmul_apply {I : Type u} {A : Type v} (G : AbGroup A)
    (k : Int) (f : I → A) (j : I) :
    ((functionGroup G).zsmul k f) j = G.zsmul k (f j) := by
  cases k with
  | ofNat n => exact nsmul_apply G n f j
  | negSucc n =>
    change G.neg (((functionGroup G).nsmul (n + 1) f) j) =
      G.neg (G.nsmul (n + 1) (f j))
    rw [nsmul_apply]

theorem int_nsmul (n : Nat) (a : Int) :
    intGroup.nsmul n a = (n : Int) * a := by
  induction n with
  | zero => exact (Int.zero_mul a).symm
  | succ n ih =>
    change intGroup.nsmul n a + a = ((n + 1 : Nat) : Int) * a
    rw [ih, Int.natCast_succ, Int.add_mul, Int.one_mul]

theorem int_zsmul (k a : Int) : intGroup.zsmul k a = k * a := by
  cases k with
  | ofNat n => exact int_nsmul n a
  | negSucc n =>
    change -(intGroup.nsmul (n + 1) a) = Int.negSucc n * a
    rw [int_nsmul]
    change -(((n + 1 : Nat) : Int) * a) = -((n + 1 : Nat) : Int) * a
    rw [Int.neg_mul]

theorem row_zsmul {n : Nat} (k : Int) (v : Row n) :
    (rowGroup n).zsmul k v = scale k v := by
  funext i
  exact (zsmul_apply intGroup k v i).trans (int_zsmul k (v i))

theorem sum_mul_right (n : Nat) (f : Fin n → Int) (a : Int) :
    (fsum intGroup n f) * a = fsum intGroup n (fun i => f i * a) := by
  revert f
  induction n with
  | zero =>
    intro f
    exact Int.zero_mul a
  | succ n ih =>
    intro f
    change (f 0 + fsum intGroup n (fun i => f i.succ)) * a =
      f 0 * a + fsum intGroup n (fun i => f i.succ * a)
    rw [Int.add_mul, ih]

theorem sum_mul_left (n : Nat) (a : Int) (f : Fin n → Int) :
    a * fsum intGroup n f = fsum intGroup n (fun i => a * f i) := by
  rw [Int.mul_comm a, sum_mul_right]
  apply Finite.sum_congr
  intro i
  exact Int.mul_comm _ _

theorem rowMul_zero_left {m n : Nat} (A : Mat m n) :
    rowMul (rowGroup m).zero A = (rowGroup n).zero := by
  funext j
  change fsum intGroup m (fun i => 0 * A i j) = 0
  simp only [Int.zero_mul]
  exact Finite.sum_zero intGroup m

theorem rowMul_zero_right {m n : Nat} (v : Row m) :
    rowMul v (zeroMat m n) = (rowGroup n).zero := by
  funext j
  change fsum intGroup m (fun i => v i * 0) = 0
  simp only [Int.mul_zero]
  exact Finite.sum_zero intGroup m

theorem rowMul_add {m n : Nat} (v w : Row m) (A : Mat m n) :
    rowMul ((rowGroup m).add v w) A =
      (rowGroup n).add (rowMul v A) (rowMul w A) := by
  funext j
  change fsum intGroup m (fun i => (v i + w i) * A i j) =
    fsum intGroup m (fun i => v i * A i j) +
    fsum intGroup m (fun i => w i * A i j)
  simp only [Int.add_mul]
  exact Finite.sum_add intGroup m _ _

theorem rowMul_matSub {m n : Nat} (v : Row m) (A B : Mat m n) :
    rowMul v (matSub A B) =
      (rowGroup n).sub (rowMul v A) (rowMul v B) := by
  funext j
  change fsum intGroup m (fun i => v i * (A i j - B i j)) =
    fsum intGroup m (fun i => v i * A i j) -
    fsum intGroup m (fun i => v i * B i j)
  simp only [Int.mul_sub]
  exact Finite.sum_sub intGroup m _ _

/-- This is the row-orientation bridge, including interchange of finite sums. -/
theorem rowMul_assoc {m n d : Nat} (v : Row m)
    (A : Mat m n) (B : Mat n d) :
    rowMul (rowMul v A) B = rowMul v (matMul A B) := by
  funext j
  change fsum intGroup n (fun k =>
    (fsum intGroup m (fun i => v i * A i k)) * B k j) =
    fsum intGroup m (fun i =>
      v i * fsum intGroup n (fun k => A i k * B k j))
  calc
    _ = fsum intGroup n (fun k =>
        fsum intGroup m (fun i => (v i * A i k) * B k j)) := by
      apply Finite.sum_congr
      intro k
      exact sum_mul_right m _ _
    _ = fsum intGroup m (fun i =>
        fsum intGroup n (fun k => (v i * A i k) * B k j)) :=
      Finite.sum_swap intGroup n m _
    _ = fsum intGroup m (fun i =>
        fsum intGroup n (fun k => v i * (A i k * B k j))) := by
      apply Finite.sum_congr
      intro i
      apply Finite.sum_congr
      intro k
      exact Int.mul_assoc _ _ _
    _ = _ := by
      apply Finite.sum_congr
      intro i
      exact (sum_mul_left n (v i) _).symm

theorem rowMul_basis {m n : Nat} (i : Fin m) (A : Mat m n) :
    rowMul (basis m i) A = A i := by
  funext j
  change fsum intGroup m
    (fun k => (if k = i then 1 else 0) * A k j) = A i j
  calc
    _ = fsum intGroup m (fun k => if k = i then A i j else 0) := by
      apply Finite.sum_congr
      intro k
      by_cases h : k = i
      · subst k; simp only [eq_self, ite_true, Int.one_mul]
      · simp only [if_neg h, Int.zero_mul]
    _ = _ := Finite.sum_single intGroup m i (A i j)

theorem rowMul_eye {n : Nat} (v : Row n) : rowMul v (eye n) = v := by
  funext j
  change fsum intGroup n
    (fun i => v i * (if j = i then 1 else 0)) = v j
  calc
    _ = fsum intGroup n (fun i => if i = j then v j else 0) := by
      apply Finite.sum_congr
      intro i
      by_cases h : i = j
      · subst i; simp only [eq_self, ite_true, Int.mul_one]
      · simp only [if_neg h, if_neg (Ne.symm h), Int.mul_zero]
    _ = _ := Finite.sum_single intGroup n j (v j)

/-- Image of rowMul is exactly an integer combination of the individual rows. -/
theorem rowMul_linear_combination {m n : Nat} (v : Row m) (A : Mat m n) :
    rowMul v A = fsum (rowGroup n) m
      (fun i => (rowGroup n).zsmul (v i) (A i)) := by
  funext j
  change fsum intGroup m (fun i => v i * A i j) =
    (fsum (functionGroup intGroup) m
      (fun i => (rowGroup n).zsmul (v i) (A i))) j
  rw [sum_apply intGroup]
  apply Finite.sum_congr
  intro i
  exact ((zsmul_apply intGroup (v i) (A i) j).trans
    (int_zsmul (v i) (A i j))).symm

/-- Actual matrix multiplication defines a homomorphism; no law is assumed. -/
def rowHom {m n : Nat} (A : Mat m n) : Hom (rowGroup m) (rowGroup n) where
  run := fun v => rowMul v A
  map_zero := rowMul_zero_left A
  map_add := fun v w => rowMul_add v w A

end Rows

/-! ## 3. Universal split-map theorem, with an image-difference quotient -/

/-- Exactly the three identities, in row-map order. -/
structure Retraction {C : Type u} {A : Type v} {B : Type w}
    (GC : AbGroup C) (GA : AbGroup A) (GB : AbGroup B) where
  m : Hom GC GA
  p : Hom GA GB
  q : Hom GB GA
  w : Hom GA GC
  mp : ∀ c, p.run (m.run c) = GB.zero
  qp : ∀ b, p.run (q.run b) = b
  residual : ∀ a, GA.sub a (q.run (p.run a)) = m.run (w.run a)

/-- A proved pair of inverse additive homomorphisms, not a hypothesis. -/
structure AddIso {A : Type u} {B : Type v}
    (GA : AbGroup A) (GB : AbGroup B) where
  forward : Hom GA GB
  backward : Hom GB GA
  left_inverse : ∀ a, backward.run (forward.run a) = a
  right_inverse : ∀ b, forward.run (backward.run b) = b

/-- No nonzero integer annihilates a nonzero element. -/
def TorsionFree {A : Type u} (G : AbGroup A) : Prop :=
  ∀ (k : Int), k ≠ 0 → ∀ a, G.zsmul k a = G.zero → a = G.zero

namespace Retraction

variable {C : Type u} {A : Type v} {B : Type w}
variable {GC : AbGroup C} {GA : AbGroup A} {GB : AbGroup B}
variable (s : Retraction GC GA GB)

/-- The image of m, not the kernel of p by definition. -/
def L (a : A) : Prop := ∃ c, s.m.run c = a

theorem mem_image_iff (a : A) : s.L a ↔ s.p.run a = GB.zero := by
  constructor
  · intro h
    cases h with
    | intro c hc =>
      rw [← hc]
      exact s.mp c
  · intro h
    have hr := s.residual a
    rw [h, s.q.map_zero, GA.sub_zero] at hr
    exact ⟨s.w.run a, hr.symm⟩

theorem image_eq_kernel : s.L = (fun a => s.p.run a = GB.zero) := by
  funext a
  exact propext (s.mem_image_iff a)

theorem surjective : ∀ b, ∃ a, s.p.run a = b := by
  intro b
  exact ⟨s.q.run b, s.qp b⟩

theorem decomposition (a : A) :
    a = GA.add (s.q.run (s.p.run a)) (s.m.run (s.w.run a)) :=
  GA.eq_of_sub_eq _ _ _ (s.residual a)

/-- The literal lattice-coset relation: a - b lies in image(m). -/
def Rel (a b : A) : Prop := s.L (GA.sub a b)

theorem rel_iff (a b : A) : s.Rel a b ↔ s.p.run a = s.p.run b := by
  unfold Rel
  rw [s.mem_image_iff, s.p.map_sub]
  exact GB.sub_eq_zero_iff _ _

def latticeSetoid : Setoid A where
  r := s.Rel
  iseqv := {
    refl := by intro a; exact (s.rel_iff a a).mpr rfl
    symm := by
      intro a b hab
      exact (s.rel_iff b a).mpr ((s.rel_iff a b).mp hab).symm
    trans := by
      intro a b c hab hbc
      exact (s.rel_iff a c).mpr
        (((s.rel_iff a b).mp hab).trans ((s.rel_iff b c).mp hbc))
  }

abbrev LQuot := Quotient s.latticeSetoid

def qmk (a : A) : s.LQuot := Quotient.mk s.latticeSetoid a

/-- Well-definedness is the proved rel_iff, not an extra field. -/
def qmap : s.LQuot → B :=
  Quotient.lift s.p.run (fun a b h => (s.rel_iff a b).mp h)

def qinv (b : B) : s.LQuot := s.qmk (s.q.run b)

theorem qmap_mk (a : A) : s.qmap (s.qmk a) = s.p.run a := rfl

theorem qmap_qinv (b : B) : s.qmap (s.qinv b) = b := s.qp b

theorem qinv_qmap (x : s.LQuot) : s.qinv (s.qmap x) = x := by
  refine Quotient.inductionOn
    (motive := fun q : s.LQuot => s.qinv (s.qmap q) = q) x ?_
  intro a
  apply Quotient.sound
  exact (s.rel_iff _ _).mpr (s.qp (s.p.run a))

theorem qmap_injective {x y : s.LQuot} (h : s.qmap x = s.qmap y) : x = y := by
  calc
    x = s.qinv (s.qmap x) := (s.qinv_qmap x).symm
    _ = s.qinv (s.qmap y) := congrArg s.qinv h
    _ = y := s.qinv_qmap y

/-- Addition induced from representatives; both representative choices are checked. -/
def qadd (x y : s.LQuot) : s.LQuot :=
  Quotient.liftOn₂ x y (fun a b => s.qmk (GA.add a b)) (by
    intro a b c d hac hbd
    apply Quotient.sound
    apply (s.rel_iff _ _).mpr
    rw [s.p.map_add, s.p.map_add,
      (s.rel_iff a c).mp hac, (s.rel_iff b d).mp hbd])

def qneg (x : s.LQuot) : s.LQuot :=
  Quotient.liftOn x (fun a => s.qmk (GA.neg a)) (by
    intro a b hab
    apply Quotient.sound
    apply (s.rel_iff _ _).mpr
    rw [s.p.map_neg, s.p.map_neg, (s.rel_iff a b).mp hab])

theorem qmap_zero : s.qmap (s.qmk GA.zero) = GB.zero := s.p.map_zero

theorem qmap_add (x y : s.LQuot) :
    s.qmap (s.qadd x y) = GB.add (s.qmap x) (s.qmap y) := by
  refine Quotient.inductionOn₂
    (motive := fun q r : s.LQuot =>
      s.qmap (s.qadd q r) = GB.add (s.qmap q) (s.qmap r)) x y ?_
  intro a b
  exact s.p.map_add a b

theorem qmap_neg (x : s.LQuot) :
    s.qmap (s.qneg x) = GB.neg (s.qmap x) := by
  refine Quotient.inductionOn
    (motive := fun q : s.LQuot =>
      s.qmap (s.qneg q) = GB.neg (s.qmap q)) x ?_
  intro a
  exact s.p.map_neg a

/-- Every quotient-group axiom follows from the induced operations. -/
def quotientGroup : AbGroup s.LQuot where
  zero := s.qmk GA.zero
  add := s.qadd
  neg := s.qneg
  add_assoc := by
    intro x y z
    apply s.qmap_injective
    simp only [s.qmap_add]
    exact GB.add_assoc _ _ _
  zero_add := by
    intro x
    apply s.qmap_injective
    rw [s.qmap_add, s.qmap_zero, GB.zero_add]
  add_zero := by
    intro x
    apply s.qmap_injective
    rw [s.qmap_add, s.qmap_zero, GB.add_zero]
  add_comm := by
    intro x y
    apply s.qmap_injective
    rw [s.qmap_add, s.qmap_add, GB.add_comm]
  neg_add := by
    intro x
    apply s.qmap_injective
    rw [s.qmap_add, s.qmap_neg, s.qmap_zero, GB.neg_add]
  add_neg := by
    intro x
    apply s.qmap_injective
    rw [s.qmap_add, s.qmap_neg, s.qmap_zero, GB.add_neg]

def quotientMap : Hom s.quotientGroup GB where
  run := s.qmap
  map_zero := s.qmap_zero
  map_add := s.qmap_add

def quotientInv : Hom GB s.quotientGroup where
  run := s.qinv
  map_zero := by
    change s.qinv GB.zero = s.qmk GA.zero
    apply s.qmap_injective
    rw [s.qmap_qinv, s.qmap_zero]
  map_add := by
    intro x y
    change s.qinv (GB.add x y) = s.qadd (s.qinv x) (s.qinv y)
    apply s.qmap_injective
    simp only [s.qmap_add, s.qmap_qinv]

def quotientIso : AddIso s.quotientGroup GB where
  forward := s.quotientMap
  backward := s.quotientInv
  left_inverse := s.qinv_qmap
  right_inverse := s.qmap_qinv

theorem saturated (hTF : TorsionFree GB) (k : Int) (hk : k ≠ 0)
    (a : A) (ha : s.L (GA.zsmul k a)) : s.L a := by
  apply (s.mem_image_iff a).mpr
  apply hTF k hk (s.p.run a)
  calc
    GB.zsmul k (s.p.run a) = s.p.run (GA.zsmul k a) :=
      (s.p.map_zsmul k a).symm
    _ = GB.zero := (s.mem_image_iff _).mp ha

/-- Abstract character factorization; the finite-row theorem below proves
    this annihilation hypothesis from the individual relation rows. -/
theorem character_factor {D : Type t} {GD : AbGroup D}
    (chi : Hom GA GD) (h : ∀ c, chi.run (s.m.run c) = GD.zero)
    (a : A) : chi.run a = chi.run (s.q.run (s.p.run a)) := by
  have hc := congrArg chi.run (s.residual a)
  rw [chi.map_sub, h (s.w.run a)] at hc
  exact (GD.sub_eq_zero_iff _ _).mp hc

theorem character_unique {D : Type t} {GD : AbGroup D}
    (chi : Hom GA GD) (psi : Hom GB GD)
    (h : ∀ a, chi.run a = psi.run (s.p.run a)) (b : B) :
    psi.run b = chi.run (s.q.run b) := by
  have hb := h (s.q.run b)
  rw [s.qp] at hb
  exact hb.symm

end Retraction

/-! ## 4. The concrete integral-matrix instantiation -/

/-- The only certificate hypotheses. No geometry or hidden image assertions. -/
structure MatrixIdentities {m N d : Nat}
    (M : Mat m N) (P : Mat N d) (Q : Mat d N) (W : Mat N m) : Prop where
  mp : matMul M P = zeroMat m d
  qp : matMul Q P = eye d
  residual : matSub (eye N) (matMul P Q) = matMul W M

/-- Derives all three split-map identities from ordinary matrix equalities. -/
def matrixRetraction {m N d : Nat}
    {M : Mat m N} {P : Mat N d} {Q : Mat d N} {W : Mat N m}
    (h : MatrixIdentities M P Q W) :
    Retraction (rowGroup m) (rowGroup N) (rowGroup d) where
  m := Rows.rowHom M
  p := Rows.rowHom P
  q := Rows.rowHom Q
  w := Rows.rowHom W
  mp := by
    intro z
    change rowMul (rowMul z M) P = (rowGroup d).zero
    rw [Rows.rowMul_assoc, h.mp, Rows.rowMul_zero_right]
  qp := by
    intro z
    change rowMul (rowMul z Q) P = z
    rw [Rows.rowMul_assoc, h.qp, Rows.rowMul_eye]
  residual := by
    intro z
    change (rowGroup N).sub z (rowMul (rowMul z P) Q) =
      rowMul (rowMul z W) M
    rw [Rows.rowMul_assoc z P Q, Rows.rowMul_assoc z W M]
    calc
      (rowGroup N).sub z (rowMul z (matMul P Q)) =
          rowMul z (matSub (eye N) (matMul P Q)) := by
        rw [Rows.rowMul_matSub, Rows.rowMul_eye]
      _ = rowMul z (matMul W M) := congrArg (rowMul z) h.residual

namespace MatrixBridge

variable {m N d : Nat}
variable {M : Mat m N} {P : Mat N d} {Q : Mat d N} {W : Mat N m}

/-- Image definition, with literal integer coefficients. -/
def Lattice (v : Row N) : Prop := ∃ z : Row m, rowMul z M = v

theorem lattice_iff_integer_span (v : Row N) :
    Lattice (M := M) v ↔ ∃ z : Row m,
      fsum (rowGroup N) m (fun r => (rowGroup N).zsmul (z r) (M r)) = v := by
  constructor
  · intro hv
    cases hv with
    | intro z hz =>
      exact ⟨z, (Rows.rowMul_linear_combination z M).symm.trans hz⟩
  · intro hv
    cases hv with
    | intro z hz =>
      exact ⟨z, (Rows.rowMul_linear_combination z M).trans hz⟩

theorem lattice_eq_kernel (h : MatrixIdentities M P Q W)
    (v : Row N) :
    Lattice (M := M) v ↔ rowMul v P = (rowGroup d).zero :=
  (matrixRetraction h).mem_image_iff v

theorem lattice_eq_kernel_as_predicate (h : MatrixIdentities M P Q W) :
    Lattice (M := M) = (fun v => rowMul v P = (rowGroup d).zero) := by
  funext v
  exact propext (lattice_eq_kernel h v)

theorem quotient_relation (h : MatrixIdentities M P Q W)
    (v w : Row N) :
    (matrixRetraction h).Rel v w ↔
      ∃ z : Row m, rowMul z M = (fun i => v i - w i) := Iff.rfl

theorem quotient_equal_iff (h : MatrixIdentities M P Q W)
    (v w : Row N) :
    (matrixRetraction h).qmk v = (matrixRetraction h).qmk w ↔
      Lattice (M := M) ((rowGroup N).sub v w) := by
  constructor
  · intro heq
    exact Quotient.exact heq
  · intro hrel
    exact Quotient.sound hrel

theorem phi_surjective (h : MatrixIdentities M P Q W) : ∀ z : Row d, ∃ v : Row N, rowMul v P = z :=
  (matrixRetraction h).surjective

/-- The inverse representative is z Q; this is not an arbitrary chosen section. -/
def quotientIso (h : MatrixIdentities M P Q W) :
    AddIso (matrixRetraction h).quotientGroup (rowGroup d) :=
  (matrixRetraction h).quotientIso

theorem quotient_forward_on_representative (h : MatrixIdentities M P Q W)
    (v : Row N) :
    (quotientIso h).forward.run ((matrixRetraction h).qmk v) = rowMul v P := rfl

theorem quotient_inverse_on_parameter (h : MatrixIdentities M P Q W)
    (z : Row d) :
    (quotientIso h).backward.run z =
      (matrixRetraction h).qmk (rowMul z Q) := rfl

theorem quotient_left_inverse (h : MatrixIdentities M P Q W)
    (x : (matrixRetraction h).LQuot) :
    (quotientIso h).backward.run ((quotientIso h).forward.run x) = x :=
  (quotientIso h).left_inverse x

theorem quotient_right_inverse (h : MatrixIdentities M P Q W)
    (z : Row d) :
    (quotientIso h).forward.run ((quotientIso h).backward.run z) = z :=
  (quotientIso h).right_inverse z

/-- Concrete torsion-freeness, from integer multiplication having no zero divisors. -/
theorem row_torsion_free (n : Nat) : TorsionFree (rowGroup n) := by
  intro k hk v hv
  rw [Rows.row_zsmul] at hv
  funext i
  have hi := congrArg (fun a : Row n => a i) hv
  change k * v i = 0 at hi
  exact (Int.mul_eq_zero.mp hi).resolve_left hk

theorem lattice_saturated (h : MatrixIdentities M P Q W)
    (k : Int) (hk : k ≠ 0) (v : Row N)
    (hv : Lattice (M := M) (scale k v)) : Lattice (M := M) v := by
  apply (matrixRetraction h).saturated (row_torsion_free d) k hk v
  change Lattice (M := M) ((rowGroup N).zsmul k v)
  rw [Rows.row_zsmul]
  exact hv

end MatrixBridge

/-! ## 5. Lawful commutative groups, actual products, and signed powers -/

/-- No field, divisibility, roots, or characteristic hypotheses. -/
structure CommGroup (D : Type u) where
  one : D
  mul : D → D → D
  inv : D → D
  mul_assoc : ∀ a b c, mul (mul a b) c = mul a (mul b c)
  one_mul : ∀ a, mul one a = a
  mul_one : ∀ a, mul a one = a
  mul_comm : ∀ a b, mul a b = mul b a
  inv_mul : ∀ a, mul (inv a) a = one
  mul_inv : ∀ a, mul a (inv a) = one

namespace CommGroup

variable {D : Type u} (G : CommGroup D)

/-- Only a change of notation: addition is multiplication, negation is inverse. -/
def asAdd : AbGroup D where
  zero := G.one
  add := G.mul
  neg := G.inv
  add_assoc := G.mul_assoc
  zero_add := G.one_mul
  add_zero := G.mul_one
  add_comm := G.mul_comm
  neg_add := G.inv_mul
  add_neg := G.mul_inv

def npow (a : D) (n : Nat) : D := G.asAdd.nsmul n a

def zpow (a : D) (k : Int) : D := G.asAdd.zsmul k a

def prod (n : Nat) (f : Fin n → D) : D := fsum G.asAdd n f

def div (a b : D) : D := G.mul a (G.inv b)

theorem npow_zero (a : D) : G.npow a 0 = G.one := rfl

theorem npow_succ (a : D) (n : Nat) :
    G.npow a (n + 1) = G.mul (G.npow a n) a := rfl

theorem zpow_nat (a : D) (n : Nat) :
    G.zpow a (Int.ofNat n) = G.npow a n := rfl

theorem zpow_negative (a : D) (n : Nat) :
    G.zpow a (-((n + 1 : Nat) : Int)) = G.inv (G.npow a (n + 1)) := rfl

theorem zpow_zero (a : D) : G.zpow a 0 = G.one := rfl

theorem zpow_one (a : D) : G.zpow a 1 = a := G.asAdd.zsmul_one a

theorem one_zpow (k : Int) : G.zpow G.one k = G.one :=
  G.asAdd.zsmul_zero_right k

theorem zpow_add (a : D) (k l : Int) :
    G.zpow a (k + l) = G.mul (G.zpow a k) (G.zpow a l) :=
  G.asAdd.zsmul_add k l a

theorem prod_zero (f : Fin 0 → D) : G.prod 0 f = G.one := rfl

theorem prod_succ (n : Nat) (f : Fin (n + 1) → D) :
    G.prod (n + 1) f = G.mul (f 0) (G.prod n (fun i => f i.succ)) := rfl

theorem prod_mul (n : Nat) (f g : Fin n → D) :
    G.prod n (fun i => G.mul (f i) (g i)) =
      G.mul (G.prod n f) (G.prod n g) :=
  Finite.sum_add G.asAdd n f g

end CommGroup

/-- Literal finite product of ordinary signed integral powers. -/
def monomial {D : Type u} (G : CommGroup D) {n : Nat}
    (x : Fin n → D) (v : Row n) : D :=
  G.prod n (fun i => G.zpow (x i) (v i))

/-- The monomial is proved to be a character, not supplied as one. -/
def monomialHom {D : Type u} (G : CommGroup D) {n : Nat}
    (x : Fin n → D) : Hom (rowGroup n) G.asAdd where
  run := monomial G x
  map_zero := by
    change fsum G.asAdd n (fun i => G.asAdd.zsmul 0 (x i)) = G.one
    simp only [AbGroup.zsmul_zero]
    exact Finite.sum_zero G.asAdd n
  map_add := by
    intro v w
    change fsum G.asAdd n (fun i => G.asAdd.zsmul (v i + w i) (x i)) =
      G.asAdd.add (fsum G.asAdd n (fun i => G.asAdd.zsmul (v i) (x i)))
        (fsum G.asAdd n (fun i => G.asAdd.zsmul (w i) (x i)))
    simp only [AbGroup.zsmul_add]
    exact Finite.sum_add G.asAdd n _ _

namespace Character

variable {D : Type u} {m n : Nat}

/-- A finite row image is evaluated as the indicated integer powers of row values. -/
theorem row_image (G : AbGroup D) (chi : Hom (rowGroup n) G)
    (v : Row m) (A : Mat m n) :
    chi.run (rowMul v A) =
      fsum G m (fun r => G.zsmul (v r) (chi.run (A r))) := by
  rw [Rows.rowMul_linear_combination, Finite.map_sum]
  apply Finite.sum_congr
  intro r
  exact chi.map_zsmul (v r) (A r)

/-- The bridge from INDIVIDUAL rows to their entire INTEGER span. -/
theorem rows_annihilate_span (G : AbGroup D) (chi : Hom (rowGroup n) G)
    (A : Mat m n) (h : ∀ r, chi.run (A r) = G.zero) (v : Row m) :
    chi.run (rowMul v A) = G.zero := by
  rw [row_image G chi v A]
  calc
    _ = fsum G m (fun _ => G.zero) := by
      apply Finite.sum_congr
      intro r
      rw [h r, G.zsmul_zero_right]
    _ = G.zero := Finite.sum_zero G m

end Character

namespace Monomial

variable {D : Type u} (G : CommGroup D)

theorem zero {n : Nat} (x : Fin n → D) :
    monomial G x (rowGroup n).zero = G.one := (monomialHom G x).map_zero

theorem add {n : Nat} (x : Fin n → D) (v w : Row n) :
    monomial G x ((rowGroup n).add v w) =
      G.mul (monomial G x v) (monomial G x w) :=
  (monomialHom G x).map_add v w

theorem sub {n : Nat} (x : Fin n → D) (v w : Row n) :
    monomial G x ((rowGroup n).sub v w) =
      G.div (monomial G x v) (monomial G x w) :=
  (monomialHom G x).map_sub v w

theorem scale {n : Nat} (x : Fin n → D) (k : Int) (v : Row n) :
    monomial G x (PR1497.scale k v) = G.zpow (monomial G x v) k := by
  rw [← Rows.row_zsmul]
  exact (monomialHom G x).map_zsmul k v

theorem on_basis {n : Nat} (x : Fin n → D) (i : Fin n) :
    monomial G x (basis n i) = x i := by
  change fsum G.asAdd n
    (fun j => G.asAdd.zsmul (if j = i then 1 else 0) (x j)) = x i
  calc
    _ = fsum G.asAdd n (fun j => if j = i then x i else G.asAdd.zero) := by
      apply Finite.sum_congr
      intro j
      by_cases h : j = i
      · subst j
        simp only [eq_self, ite_true, AbGroup.zsmul_one]
      · simp only [if_neg h, AbGroup.zsmul_zero]
    _ = x i := Finite.sum_single G.asAdd n i (x i)

/-- Actual monomial substitution, including negative exponents. -/
theorem substitution {m n : Nat} (x : Fin n → D)
    (v : Row m) (A : Mat m n) :
    monomial G x (rowMul v A) =
      monomial G (fun r => monomial G x (A r)) v :=
  Character.row_image G.asAdd (monomialHom G x) v A

theorem individual_rows_to_span {m n : Nat} (x : Fin n → D)
    (A : Mat m n) (h : ∀ r, monomial G x (A r) = G.one) (v : Row m) :
    monomial G x (rowMul v A) = G.one :=
  Character.rows_annihilate_span G.asAdd (monomialHom G x) A h v

end Monomial

/-! ## 6. Matrix-to-monomial reconstruction and converse, without root extraction -/

namespace MonomialBridge

variable {D : Type u} (G : CommGroup D)

def parameters {d N : Nat} (Q : Mat d N) (x : Fin N → D) : Fin d → D :=
  fun j => monomial G x (Q j)

def realization {N d : Nat} (P : Mat N d) (theta : Fin d → D) : Fin N → D :=
  fun i => monomial G theta (P i)

def Relations {m N : Nat} (M : Mat m N) (x : Fin N → D) : Prop :=
  ∀ r, monomial G x (M r) = G.one

variable {m N d : Nat}
variable {M : Mat m N} {P : Mat N d} {Q : Mat d N} {W : Mat N m}

/-- Stronger than coordinate reconstruction: every exponent vector factors through P. -/
theorem reconstruction_all_exponents (h : MatrixIdentities M P Q W)
    (x : Fin N → D)
    (hx : Relations G M x) (v : Row N) :
    monomial G x v = monomial G (parameters G Q x) (rowMul v P) := by
  have hann : ∀ c, (monomialHom G x).run ((matrixRetraction h).m.run c) =
      G.asAdd.zero := by
    intro c
    exact Monomial.individual_rows_to_span G x M hx c
  calc
    monomial G x v = monomial G x (rowMul (rowMul v P) Q) :=
      (matrixRetraction h).character_factor (monomialHom G x) hann v
    _ = monomial G (parameters G Q x) (rowMul v P) :=
      Monomial.substitution G x (rowMul v P) Q

theorem reconstruct_coordinate (h : MatrixIdentities M P Q W)
    (x : Fin N → D)
    (hx : Relations G M x) (i : Fin N) :
    x i = monomial G (parameters G Q x) (P i) := by
  have hi := reconstruction_all_exponents G h x hx (basis N i)
  rw [Monomial.on_basis, Rows.rowMul_basis] at hi
  exact hi

theorem reconstruction (h : MatrixIdentities M P Q W)
    (x : Fin N → D) (hx : Relations G M x) :
    x = realization G P (parameters G Q x) := by
  funext i
  exact reconstruct_coordinate G h x hx i

/-- Every arbitrary parameter tuple gives a solution of the individual relations. -/
theorem converse_relations (h : MatrixIdentities M P Q W)
    (theta : Fin d → D) :
    Relations G M (realization G P theta) := by
  intro r
  have hr : rowMul (M r) P = (rowGroup d).zero :=
    congrArg (fun A : Mat m d => A r) h.mp
  calc
    monomial G (realization G P theta) (M r) =
        monomial G theta (rowMul (M r) P) :=
      (Monomial.substitution G theta (M r) P).symm
    _ = G.one := by rw [hr]; exact Monomial.zero G theta

/-- QP = I recovers arbitrary parameters exactly, not merely up to powers. -/
theorem parameters_recover (h : MatrixIdentities M P Q W)
    (theta : Fin d → D) :
    parameters G Q (realization G P theta) = theta := by
  funext j
  have hj : rowMul (Q j) P = basis d j :=
    congrArg (fun A : Mat d d => A j) h.qp
  change monomial G (realization G P theta) (Q j) = theta j
  calc
    _ = monomial G theta (rowMul (Q j) P) :=
      (Monomial.substitution G theta (Q j) P).symm
    _ = theta j := by rw [hj]; exact Monomial.on_basis G theta j

/-- Any tuple realizing x is the tuple defined by the Q monomials. -/
theorem parameters_unique (h : MatrixIdentities M P Q W)
    (x : Fin N → D) (theta : Fin d → D)
    (hreal : ∀ i, x i = monomial G theta (P i)) :
    parameters G Q x = theta := by
  have hx : x = realization G P theta := funext hreal
  rw [hx]
  exact parameters_recover G h theta

/-- First equality in the requested residual calculation. -/
theorem residual_exponent_formula (x : Fin N → D) (i : Fin N) :
    G.div (x i) (monomial G (parameters G Q x) (P i)) =
      monomial G x ((rowGroup N).sub (basis N i) ((matMul P Q) i)) := by
  change G.div (x i)
    (monomial G (fun j => monomial G x (Q j)) (P i)) =
      monomial G x ((rowGroup N).sub (basis N i) (rowMul (P i) Q))
  rw [Monomial.sub, Monomial.on_basis, Monomial.substitution]

/-- Second equality, with a literal finite product and the literal W coefficients.
    This equation does not need the row relations to equal one. -/
theorem residual_relations_formula (h : MatrixIdentities M P Q W)
    (x : Fin N → D) (i : Fin N) :
    G.div (x i) (monomial G (parameters G Q x) (P i)) =
      G.prod m (fun r => G.zpow (monomial G x (M r)) (W i r)) := by
  have hi : (rowGroup N).sub (basis N i) ((matMul P Q) i) =
      rowMul (W i) M :=
    congrArg (fun A : Mat N N => A i) h.residual
  rw [residual_exponent_formula G, hi]
  exact Monomial.substitution G x (W i) M

theorem residual_eq_one (h : MatrixIdentities M P Q W)
    (x : Fin N → D) (hx : Relations G M x) (i : Fin N) :
    G.div (x i) (monomial G (parameters G Q x) (P i)) = G.one := by
  rw [reconstruct_coordinate G h x hx i]
  exact G.mul_inv _

/-- Existence and uniqueness are both stated without a choice operator. -/
theorem unique_parameterization (h : MatrixIdentities M P Q W)
    (x : Fin N → D) (hx : Relations G M x) :
    (∀ i, x i = monomial G (parameters G Q x) (P i)) ∧
      (∀ theta : Fin d → D,
        (∀ i, x i = monomial G theta (P i)) → parameters G Q x = theta) := by
  constructor
  · exact reconstruct_coordinate G h x hx
  · intro theta ht
    exact parameters_unique G h x theta ht

end MonomialBridge

end PR1497

/-! ## Complete axiom-query inventory (output requires actual Lean replay). -/
set_option pp.fullNames true
#print axioms PR1497.AbGroup
#print axioms PR1497.AbGroup.sub
#print axioms PR1497.AbGroup.add_left_cancel
#print axioms PR1497.AbGroup.add_right_cancel
#print axioms PR1497.AbGroup.add_left_comm
#print axioms PR1497.AbGroup.add_four
#print axioms PR1497.AbGroup.neg_zero
#print axioms PR1497.AbGroup.neg_neg
#print axioms PR1497.AbGroup.neg_add_distrib
#print axioms PR1497.AbGroup.sub_zero
#print axioms PR1497.AbGroup.sub_self
#print axioms PR1497.AbGroup.sub_add_cancel
#print axioms PR1497.AbGroup.add_sub_cancel
#print axioms PR1497.AbGroup.sub_eq_zero_iff
#print axioms PR1497.AbGroup.eq_of_sub_eq
#print axioms PR1497.AbGroup.nsmul
#print axioms PR1497.AbGroup.zsmul
#print axioms PR1497.AbGroup.nsmul_zero
#print axioms PR1497.AbGroup.zsmul_zero
#print axioms PR1497.AbGroup.zsmul_zero_right
#print axioms PR1497.AbGroup.zsmul_one
#print axioms PR1497.AbGroup.int_induction
#print axioms PR1497.AbGroup.zsmul_succ
#print axioms PR1497.AbGroup.zsmul_pred
#print axioms PR1497.AbGroup.zsmul_add
#print axioms PR1497.Hom
#print axioms PR1497.Hom.id
#print axioms PR1497.Hom.comp
#print axioms PR1497.Hom.ext
#print axioms PR1497.Hom.map_neg
#print axioms PR1497.Hom.map_sub
#print axioms PR1497.Hom.map_nsmul
#print axioms PR1497.Hom.map_zsmul
#print axioms PR1497.fsum
#print axioms PR1497.Finite.sum_congr
#print axioms PR1497.Finite.sum_zero
#print axioms PR1497.Finite.sum_add
#print axioms PR1497.Finite.sum_neg
#print axioms PR1497.Finite.sum_sub
#print axioms PR1497.Finite.sum_swap
#print axioms PR1497.Finite.sum_single
#print axioms PR1497.Finite.map_sum
#print axioms PR1497.intGroup
#print axioms PR1497.functionGroup
#print axioms PR1497.Row
#print axioms PR1497.Mat
#print axioms PR1497.rowGroup
#print axioms PR1497.scale
#print axioms PR1497.basis
#print axioms PR1497.eye
#print axioms PR1497.zeroMat
#print axioms PR1497.matSub
#print axioms PR1497.rowMul
#print axioms PR1497.matMul
#print axioms PR1497.Rows.sum_apply
#print axioms PR1497.Rows.nsmul_apply
#print axioms PR1497.Rows.zsmul_apply
#print axioms PR1497.Rows.int_nsmul
#print axioms PR1497.Rows.int_zsmul
#print axioms PR1497.Rows.row_zsmul
#print axioms PR1497.Rows.sum_mul_right
#print axioms PR1497.Rows.sum_mul_left
#print axioms PR1497.Rows.rowMul_zero_left
#print axioms PR1497.Rows.rowMul_zero_right
#print axioms PR1497.Rows.rowMul_add
#print axioms PR1497.Rows.rowMul_matSub
#print axioms PR1497.Rows.rowMul_assoc
#print axioms PR1497.Rows.rowMul_basis
#print axioms PR1497.Rows.rowMul_eye
#print axioms PR1497.Rows.rowMul_linear_combination
#print axioms PR1497.Rows.rowHom
#print axioms PR1497.Retraction
#print axioms PR1497.AddIso
#print axioms PR1497.TorsionFree
#print axioms PR1497.Retraction.L
#print axioms PR1497.Retraction.mem_image_iff
#print axioms PR1497.Retraction.image_eq_kernel
#print axioms PR1497.Retraction.surjective
#print axioms PR1497.Retraction.decomposition
#print axioms PR1497.Retraction.Rel
#print axioms PR1497.Retraction.rel_iff
#print axioms PR1497.Retraction.latticeSetoid
#print axioms PR1497.Retraction.LQuot
#print axioms PR1497.Retraction.qmk
#print axioms PR1497.Retraction.qmap
#print axioms PR1497.Retraction.qinv
#print axioms PR1497.Retraction.qmap_mk
#print axioms PR1497.Retraction.qmap_qinv
#print axioms PR1497.Retraction.qinv_qmap
#print axioms PR1497.Retraction.qmap_injective
#print axioms PR1497.Retraction.qadd
#print axioms PR1497.Retraction.qneg
#print axioms PR1497.Retraction.qmap_zero
#print axioms PR1497.Retraction.qmap_add
#print axioms PR1497.Retraction.qmap_neg
#print axioms PR1497.Retraction.quotientGroup
#print axioms PR1497.Retraction.quotientMap
#print axioms PR1497.Retraction.quotientInv
#print axioms PR1497.Retraction.quotientIso
#print axioms PR1497.Retraction.saturated
#print axioms PR1497.Retraction.character_factor
#print axioms PR1497.Retraction.character_unique
#print axioms PR1497.MatrixIdentities
#print axioms PR1497.matrixRetraction
#print axioms PR1497.MatrixBridge.Lattice
#print axioms PR1497.MatrixBridge.lattice_iff_integer_span
#print axioms PR1497.MatrixBridge.lattice_eq_kernel
#print axioms PR1497.MatrixBridge.lattice_eq_kernel_as_predicate
#print axioms PR1497.MatrixBridge.quotient_relation
#print axioms PR1497.MatrixBridge.quotient_equal_iff
#print axioms PR1497.MatrixBridge.phi_surjective
#print axioms PR1497.MatrixBridge.quotientIso
#print axioms PR1497.MatrixBridge.quotient_forward_on_representative
#print axioms PR1497.MatrixBridge.quotient_inverse_on_parameter
#print axioms PR1497.MatrixBridge.quotient_left_inverse
#print axioms PR1497.MatrixBridge.quotient_right_inverse
#print axioms PR1497.MatrixBridge.row_torsion_free
#print axioms PR1497.MatrixBridge.lattice_saturated
#print axioms PR1497.CommGroup
#print axioms PR1497.CommGroup.asAdd
#print axioms PR1497.CommGroup.npow
#print axioms PR1497.CommGroup.zpow
#print axioms PR1497.CommGroup.prod
#print axioms PR1497.CommGroup.div
#print axioms PR1497.CommGroup.npow_zero
#print axioms PR1497.CommGroup.npow_succ
#print axioms PR1497.CommGroup.zpow_nat
#print axioms PR1497.CommGroup.zpow_negative
#print axioms PR1497.CommGroup.zpow_zero
#print axioms PR1497.CommGroup.zpow_one
#print axioms PR1497.CommGroup.one_zpow
#print axioms PR1497.CommGroup.zpow_add
#print axioms PR1497.CommGroup.prod_zero
#print axioms PR1497.CommGroup.prod_succ
#print axioms PR1497.CommGroup.prod_mul
#print axioms PR1497.monomial
#print axioms PR1497.monomialHom
#print axioms PR1497.Character.row_image
#print axioms PR1497.Character.rows_annihilate_span
#print axioms PR1497.Monomial.zero
#print axioms PR1497.Monomial.add
#print axioms PR1497.Monomial.sub
#print axioms PR1497.Monomial.scale
#print axioms PR1497.Monomial.on_basis
#print axioms PR1497.Monomial.substitution
#print axioms PR1497.Monomial.individual_rows_to_span
#print axioms PR1497.MonomialBridge.parameters
#print axioms PR1497.MonomialBridge.realization
#print axioms PR1497.MonomialBridge.Relations
#print axioms PR1497.MonomialBridge.reconstruction_all_exponents
#print axioms PR1497.MonomialBridge.reconstruct_coordinate
#print axioms PR1497.MonomialBridge.reconstruction
#print axioms PR1497.MonomialBridge.converse_relations
#print axioms PR1497.MonomialBridge.parameters_recover
#print axioms PR1497.MonomialBridge.parameters_unique
#print axioms PR1497.MonomialBridge.residual_exponent_formula
#print axioms PR1497.MonomialBridge.residual_relations_formula
#print axioms PR1497.MonomialBridge.residual_eq_one
#print axioms PR1497.MonomialBridge.unique_parameterization
