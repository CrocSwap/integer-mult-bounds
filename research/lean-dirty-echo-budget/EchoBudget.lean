import Std

/-
Copyright (c) 2026 Gareth Davidson (@bitplane).
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
Formal resource model for Alexander Schwartzman's PR784, building on PR673.
This file does not formalize operator semantics or the multiplication theorem.
-/

set_option autoImplicit false

namespace DirtyEcho

def factors (xs : List (Nat × Nat)) : Nat := (xs.map Prod.fst).sum
def calls (xs : List (Nat × Nat)) : Nat := (xs.map Prod.snd).sum

/-- Uniform-cost ordered echo trees with parent connectors reserved throughout
each child call. Every child fits the same remaining budget `s`; unused capacity
is permitted. The endpoints execute twice and every interior child four times. -/
inductive Fits : Nat → Nat → Nat → Prop where
  | leaf (s : Nat) : Fits s 1 1
  | node {s a b ca cb : Nat} (middle : List (Nat × Nat))
      (left : Fits s a ca) (right : Fits s b cb)
      (inside : ∀ x ∈ middle, Fits s x.1 x.2) :
      Fits (s + middle.length + 1) (a + factors middle + b)
        (2 * ca + 4 * calls middle + 2 * cb)

theorem pow_two_pos (s : Nat) : 1 ≤ 2^s := by
  induction s with
  | zero => decide
  | succ s ih => simp only [Nat.pow_succ]; omega

theorem pow_four_pos (s : Nat) : 1 ≤ 4^s := by
  induction s with
  | zero => decide
  | succ s ih => simp only [Nat.pow_succ]; omega

theorem four_as_square (s : Nat) : 4^s = 2^s * 2^s := by
  induction s with
  | zero => decide
  | succ s ih =>
    simp only [Nat.pow_succ, ih]
    change (2^s * 2^s) * (2*2) = (2^s*2) * (2^s*2)
    ac_rfl

theorem leaf_bound (s : Nat) : 2^(s+1) ≤ 1 + 4^s := by
  induction s with
  | zero => decide
  | succ s ih =>
    have hp := pow_four_pos s
    simp only [Nat.pow_succ] at *
    omega

theorem arity_capacity (m : Nat) : m + 2 ≤ 2^(m+1) := by
  induction m with
  | zero => decide
  | succ m ih => simp only [Nat.pow_succ] at *; omega

theorem wide_arity_capacity (m : Nat) (hm : 2 ≤ m) : 2 * (m+2) ≤ 2^(m+1) := by
  obtain ⟨j, rfl⟩ := Nat.exists_eq_add_of_le hm
  induction j with
  | zero => decide
  | succ j ih =>
    have hpow : 2^(2+(j+1)+1) = 2^(2+j+1)*2 := by
      rw [show 2+(j+1)+1 = (2+j+1)+1 by omega, Nat.pow_succ]
    rw [hpow]
    omega

theorem middle_capacity (xs : List (Nat × Nat)) (q : Nat)
    (h : ∀ x ∈ xs, x.1 ≤ q) : factors xs ≤ xs.length * q := by
  induction xs with
  | nil => simp [factors]
  | cons x xs ih =>
    have hx := h x (by simp)
    have hs := ih (by intro z hz; exact h z (by simp [hz]))
    simp only [factors, List.map_cons, List.sum_cons, List.length_cons] at *
    simp only [Nat.add_mul]
    omega

theorem positive {s n N : Nat} (h : Fits s n N) : 1 ≤ n := by
  induction h with
  | leaf s => decide
  | node middle left right inside ihl ihr ihm => omega

theorem capacity {s n N : Nat} (h : Fits s n N) : n ≤ 2^s := by
  induction h with
  | leaf s => exact pow_two_pos s
  | @node s a b ca cb middle left right inside ihl ihr ihm =>
    have hm := middle_capacity middle (2^s) (by intro x hx; exact ihm x hx)
    calc
      a + factors middle + b ≤ (middle.length+2)*2^s := by
        simp only [Nat.add_mul]
        omega
      _ ≤ 2^(middle.length+1)*2^s := Nat.mul_le_mul_right _ (arity_capacity _)
      _ = 2^(s+middle.length+1) := by
        rw [← Nat.pow_add]
        congr 1
        omega

theorem binary_price (p q a b ca cb : Nat)
    (ha : p*a ≤ ca+q) (hb : p*b ≤ cb+q) :
    (2*p)*(a+b) ≤ 2*ca+2*cb+4*q := by
  calc
    (2*p)*(a+b) = 2*(p*a)+2*(p*b) := by simp [Nat.mul_add, Nat.mul_assoc]
    _ ≤ 2*(ca+q)+2*(cb+q) :=
      Nat.add_le_add (Nat.mul_le_mul_left 2 ha) (Nat.mul_le_mul_left 2 hb)
    _ = 2*ca+2*cb+4*q := by simp only [Nat.mul_add]; omega

theorem ternary_price (p a b c ca cb cc : Nat)
    (ha : 2*(p*a) ≤ ca+p*p) (hb : 2*(p*b) ≤ cb+p*p)
    (hc : 2*(p*c) ≤ cc+p*p) (acap : a ≤ p) (ccap : c ≤ p) :
    8*(p*(a+b+c)) ≤ 2*ca+4*cb+2*cc+16*(p*p) := by
  have h2a := Nat.mul_le_mul_left 2 ha
  have h4b := Nat.mul_le_mul_left 4 hb
  have h2c := Nat.mul_le_mul_left 2 hc
  have hac := Nat.mul_le_mul_left p (Nat.add_le_add acap ccap)
  simp only [Nat.mul_add] at hac
  have hends := Nat.mul_le_mul_left 4 hac
  simp only [Nat.mul_add, Nat.mul_assoc] at *
  omega

theorem below_half_price (s n : Nat) (hn : 2*n ≤ 2^s) :
    2^(s+1)*n ≤ 4^s := by
  calc
    2^(s+1)*n = 2^s*(2*n) := by rw [Nat.pow_succ]; ac_rfl
    _ ≤ 2^s*2^s := Nat.mul_le_mul_left _ hn
    _ = 4^s := (four_as_square s).symm

theorem lower_bound {s n N : Nat} (h : Fits s n N) : 2^(s+1)*n ≤ N+4^s := by
  induction h with
  | leaf s => simpa using leaf_bound s
  | @node s a b ca cb middle left right inside ihl ihr ihm =>
    have acap := capacity left
    have bcap := capacity right
    have mcap := middle_capacity middle (2^s) (by
      intro x hx
      exact capacity (inside x hx))
    have allcap : a + factors middle + b ≤ (middle.length+2)*2^s := by
      simp only [Nat.add_mul]
      omega
    cases middle with
    | nil =>
      have hbin := binary_price (2^(s+1)) (4^s) a b ca cb ihl ihr
      simpa [factors, calls, Nat.pow_succ, Nat.mul_add, Nat.add_mul,
        Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using hbin
    | cons x xs =>
      cases xs with
      | nil =>
        have hm := ihm x (by simp)
        have htri := ternary_price (2^s) a x.1 b ca x.2 cb
          (by simpa [Nat.pow_succ, four_as_square, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using ihl)
          (by simpa [Nat.pow_succ, four_as_square, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using hm)
          (by simpa [Nat.pow_succ, four_as_square, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using ihr)
          acap bcap
        change 2^(s+1+1+1)*(a+x.1+b) ≤ 2*ca+4*x.2+2*cb+4^(s+1+1)
        have hp2 : 2^(s+1+1+1) = 8*2^s := by
          rw [show s+1+1+1 = s+3 by omega, Nat.pow_add]
          simp [Nat.mul_comm]
        have hp4 : 4^(s+1+1) = 16*4^s := by
          rw [show s+1+1 = s+2 by omega, Nat.pow_add]
          simp [Nat.mul_comm]
        rw [hp2, hp4, four_as_square]
        simpa [Nat.mul_add, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using htri
      | cons y ys =>
        have hwide := Nat.mul_le_mul_right (2^s)
          (wide_arity_capacity (x::y::ys).length (by simp))
        have hhalf : 2*(a+factors (x::y::ys)+b) ≤ 2^(s+(x::y::ys).length+1) := by
          calc
            2*(a+factors (x::y::ys)+b) ≤ 2*(((x::y::ys).length+2)*2^s) :=
              Nat.mul_le_mul_left 2 allcap
            _ ≤ 2^((x::y::ys).length+1)*2^s := by simpa [Nat.mul_assoc] using hwide
            _ = 2^(s+(x::y::ys).length+1) := by
              rw [← Nat.pow_add]
              congr 1
              omega
        have hw := below_half_price (s+(x::y::ys).length+1) (a+factors (x::y::ys)+b) hhalf
        omega

theorem call_lower_bound {s n N : Nat} (h : Fits s n N) :
    2^(s+1)*n - 4^s ≤ N := by
  have hh := lower_bound h
  omega

theorem weaken {s n N : Nat} (h : Fits s n N) (extra : Nat) : Fits (s+extra) n N := by
  induction h with
  | leaf s => exact Fits.leaf (s+extra)
  | node middle left right inside ihl ihr ihm =>
    simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using Fits.node middle ihl ihr ihm

theorem binary_join {s a b ca cb : Nat} (left : Fits s a ca) (right : Fits s b cb) :
    Fits (s+1) (a+b) (2*ca+2*cb) := by
  simpa [factors, calls] using Fits.node [] left right (by simp)

theorem feasible (s n : Nat) (hn : 1 ≤ n) (hc : n ≤ 2^s) : ∃ N, Fits s n N := by
  induction s generalizing n with
  | zero =>
    have heq : n = 1 := by simp at hc; omega
    subst n
    exact ⟨1, Fits.leaf 0⟩
  | succ s ih =>
    by_cases hleaf : n = 1
    · subst n; exact ⟨1, Fits.leaf (s+1)⟩
    · have hn2 : 2 ≤ n := by omega
      have hcap : n ≤ 2*2^s := by simpa [Nat.pow_succ, Nat.mul_comm] using hc
      obtain ⟨ca, ha⟩ := ih (n/2) (by omega) (by omega)
      obtain ⟨cb, hb⟩ := ih (n-n/2) (by omega) (by omega)
      have hsplit : n/2 + (n-n/2) = n := by omega
      exact ⟨2*ca+2*cb, by simpa [hsplit] using binary_join ha hb⟩

theorem feasibility_iff (s n : Nat) :
    (∃ N, Fits s n N) ↔ 1 ≤ n ∧ n ≤ 2^s := by
  constructor
  · rintro ⟨N, h⟩
    exact ⟨positive h, capacity h⟩
  · rintro ⟨hn, hc⟩
    exact feasible s n hn hc

theorem two_factors : Fits 1 2 4 := by
  exact binary_join (Fits.leaf 0) (Fits.leaf 0)

theorem three_factors : Fits 2 3 8 := by
  exact Fits.node [(1,1)] (Fits.leaf 0) (Fits.leaf 0) (by
    intro x hx
    have heq : x = (1,1) := by simpa using hx
    subst x
    exact Fits.leaf 0)

theorem four_factors : Fits 2 4 16 := binary_join two_factors two_factors

/-- The whole equality band, expressed without truncated subtraction. -/
theorem equality_family (d n : Nat) (lo : 3*2^d ≤ n) (hi : n ≤ 4*2^d) :
    ∃ N, Fits (d+2) n N ∧ N+4^(d+2) = 2^(d+3)*n := by
  induction d generalizing n with
  | zero =>
    have hn : n = 3 ∨ n = 4 := by simp at lo hi; omega
    rcases hn with rfl | rfl
    · exact ⟨8, three_factors, by decide⟩
    · exact ⟨16, four_factors, by decide⟩
  | succ d ih =>
    have hlo : 6*2^d ≤ n := by simp only [Nat.pow_succ] at lo; omega
    have hhi : n ≤ 8*2^d := by simp only [Nat.pow_succ] at hi; omega
    obtain ⟨ca, ha, hea⟩ := ih (n/2) (by omega) (by omega)
    obtain ⟨cb, hb, heb⟩ := ih (n-n/2) (by omega) (by omega)
    have hsplit : n/2 + (n-n/2) = n := by omega
    refine ⟨2*ca+2*cb, ?_, ?_⟩
    · simpa [hsplit, Nat.add_assoc] using binary_join ha hb
    · have hp4 : 4^(d+1+2) = 4^(d+2)*4 := by
        rw [show d+1+2 = (d+2)+1 by omega, Nat.pow_succ]
      have hp2 : 2^(d+1+3) = 2^(d+3)*2 := by
        rw [show d+1+3 = (d+3)+1 by omega, Nat.pow_succ]
      calc
        2*ca+2*cb+4^(d+1+2) = 2*(ca+4^(d+2))+2*(cb+4^(d+2)) := by
          rw [hp4]
          omega
        _ = 2*(2^(d+3)*(n/2))+2*(2^(d+3)*(n-n/2)) := by rw [hea, heb]
        _ = (2^(d+3)*2)*(n/2+(n-n/2)) := by
          simp only [Nat.mul_add]
          ac_rfl
        _ = 2^(d+1+3)*n := by rw [hsplit, hp2]

theorem sharp_minimum (d n : Nat) (lo : 3*2^d ≤ n) (hi : n ≤ 4*2^d) :
    ∃ N, Fits (d+2) n N ∧ N+4^(d+2) = 2^(d+3)*n ∧
      ∀ M, Fits (d+2) n M → N ≤ M := by
  obtain ⟨N, hfit, heq⟩ := equality_family d n lo hi
  refine ⟨N, hfit, heq, ?_⟩
  intro M hm
  have hbound : 2^(d+3)*n ≤ M+4^(d+2) := by
    simpa [Nat.add_assoc] using lower_bound hm
  omega

theorem exact_50_6 : Fits 6 50 2304 ∧ ∀ N, Fits 6 50 N → 2304 ≤ N := by
  obtain ⟨N, hfit, heq, hmin⟩ := sharp_minimum 4 50 (by decide) (by decide)
  change N+4096 = 6400 at heq
  have hn : N = 2304 := by omega
  subst N
  exact ⟨hfit, hmin⟩

/-- PR822's reported 59-factor/five-array connector-reuse construction has a
different allocation rule; it cannot be a tree in this reserved-scratch model. -/
theorem no_reserved_59_5 : ¬ ∃ N, Fits 5 59 N := by
  rintro ⟨N, h⟩
  have hc := capacity h
  change 59 ≤ 32 at hc
  omega

#print axioms capacity
#print axioms lower_bound
#print axioms call_lower_bound
#print axioms feasibility_iff
#print axioms equality_family
#print axioms sharp_minimum
#print axioms exact_50_6
#print axioms no_reserved_59_5

end DirtyEcho
