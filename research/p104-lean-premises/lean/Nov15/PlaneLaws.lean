/-
PlaneLaws .  See PlaneLaws.md.  Sources: internal notes (SPLIT), GC9.md + SPEC-PLANE.md (QUARTER).

Vectors `Fin n → ZMod 2` with the standard dot; `one` = all-ones; a TOKEN/port is an odd vector (dot with `one` = 1).
 Part 1  SPLIT (any n, any odd-port set): each token of u_t^perp lies in exactly one of  u_t^perp ∩ u_t'^perp  and
         u_t^perp ∩ (u_t'+1)^perp  (= u_t^perp ∩ t''^perp, t'' = u_t+u_t'+1).  t'' is odd for odd n and t'' ≠ 1 iff u_t ≠ u_t'.
 Part 2  QUARTER (any n, any subspace B containing 1): H_s = B ∩ s^perp is a hyperplane of B through p, avoiding 1; the quarters
         Q_H = {odd s ⊥ H} partition the junk of p exactly (EXISTENCE and UNIQUENESS), each read by the ports of H.
 Part 3  E7 numbers (n = 7, |B| = 16, kernel `decide` on 7-bit masks): 32 junk tokens, 4 quarters of 8, 4 readers each; SPLIT parts 16+16.
Kernel only: no sorry, no native_decide.
-/
import Mathlib.LinearAlgebra.Matrix.DotProduct
import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.IntervalCases

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace PlaneLaws
open Matrix

abbrev Vec (n : ℕ) := Fin n → ZMod 2
def one (n : ℕ) : Vec n := fun _ => 1
/-- odd = a token / port. -/
def Tok {n : ℕ} (s : Vec n) : Prop := s ⬝ᵥ one n = 1
/-- s is a junk token of p: odd and orthogonal to p. -/
def Junk {n : ℕ} (p s : Vec n) : Prop := Tok s ∧ s ⬝ᵥ p = 0

theorem z2_xor : ∀ a : ZMod 2, (a = 0 ↔ ¬ (a + 1 = 0)) := by decide
/-- exactly one of a, b. -/
def Xr (a b : Prop) : Prop := (a ∧ ¬ b) ∨ (¬ a ∧ b)

theorem z2_nz : ∀ a : ZMod 2, ¬ a = 0 → a + 1 = 0 := by decide
theorem z2_add_eq : ∀ a b : ZMod 2, a + b = 0 → a = b := by decide

/-! ### Part 1: SPLIT -/
section Split
variable {n : ℕ}

theorem dot_add_one (s u : Vec n) : s ⬝ᵥ (u + one n) = s ⬝ᵥ u + s ⬝ᵥ one n := dotProduct_add _ _ _

/-- SPLIT, dichotomy: an odd s is orthogonal to exactly one of u' and u'+1. -/
theorem split_xor (s u' : Vec n) (hs : Tok s) : Xr (s ⬝ᵥ u' = 0) (s ⬝ᵥ (u' + one n) = 0) := by
  have h := dot_add_one s u'
  rw [hs] at h
  rw [h]
  have := z2_xor (s ⬝ᵥ u')
  by_cases h0 : s ⬝ᵥ u' = 0
  · exact Or.inl ⟨h0, this.mp h0⟩
  · exact Or.inr ⟨h0, z2_nz _ h0⟩

/-- SPLIT lemma: every token of u_t^perp is in exactly one of C(t,t') and C(t,t'') (t'' = u_t + u_t' + 1). -/
theorem split_lemma (ut ut' s : Vec n) (hs : Tok s) (h : s ⬝ᵥ ut = 0) :
    Xr (s ⬝ᵥ ut' = 0) (s ⬝ᵥ (ut + ut' + one n) = 0) := by
  have e : s ⬝ᵥ (ut + ut' + one n) = s ⬝ᵥ (ut' + one n) := by
    rw [add_assoc, dotProduct_add, h, zero_add]
  rw [e]; exact split_xor s ut' hs

/-- the same, as a partition statement on the token set of t. -/
theorem split_partition (ut ut' : Vec n) :
    {s : Vec n | Tok s ∧ s ⬝ᵥ ut = 0} =
      {s | Tok s ∧ s ⬝ᵥ ut = 0 ∧ s ⬝ᵥ ut' = 0} ∪ {s | Tok s ∧ s ⬝ᵥ ut = 0 ∧ s ⬝ᵥ (ut + ut' + one n) = 0} ∧
    Disjoint {s : Vec n | Tok s ∧ s ⬝ᵥ ut = 0 ∧ s ⬝ᵥ ut' = 0} {s | Tok s ∧ s ⬝ᵥ ut = 0 ∧ s ⬝ᵥ (ut + ut' + one n) = 0} := by
  constructor
  · ext s
    simp only [Set.mem_setOf_eq, Set.mem_union]
    constructor
    · rintro ⟨hs, h⟩
      rcases split_lemma ut ut' s hs h with ⟨a, _⟩ | ⟨_, b⟩
      · exact Or.inl ⟨hs, h, a⟩
      · exact Or.inr ⟨hs, h, b⟩
    · rintro (⟨hs, h, _⟩ | ⟨hs, h, _⟩) <;> exact ⟨hs, h⟩
  · rw [Set.disjoint_left]
    rintro s ⟨hs, h, a⟩ ⟨_, _, b⟩
    rcases split_lemma ut ut' s hs h with ⟨_, nb⟩ | ⟨na, _⟩
    · exact nb b
    · exact na a

/-- t'' is odd when n is odd and u_t, u_t' are odd. -/
theorem tok_t'' (ut ut' : Vec n) (hn : one n ⬝ᵥ one n = 1) (h1 : Tok ut) (h2 : Tok ut') :
    Tok (ut + ut' + one n) := by
  unfold Tok at *
  rw [add_assoc, add_dotProduct, add_dotProduct, h1, h2, hn]; decide

/-- t'' = 1 iff u_t = u_t': so t'' is a port of the full odd set (1 excluded) exactly when t != t'. -/
theorem t''_eq_one (ut ut' : Vec n) : ut + ut' + one n = one n ↔ ut = ut' := by
  constructor
  · intro h
    funext i
    have := congrFun h i
    simp only [Pi.add_apply, one] at this
    have h' : ut i + ut' i + 1 = 1 := this
    exact z2_add_eq _ _ (by simpa using h')
  · rintro rfl
    funext i
    simp only [Pi.add_apply, one]
    generalize ut i = a; revert a; decide

end Split

/-! ### Part 2: QUARTER -/
section Quarter
variable {n : ℕ}

/-- H is a hyperplane of B avoiding 1: H ≤ B, 1 ∉ H, and B = H ∪ (H + 1). -/
structure QHyp (B H : Submodule (ZMod 2) (Vec n)) : Prop where
  le : H ≤ B
  one_nmem : one n ∉ H
  cover : ∀ b ∈ B, b ∈ H ∨ b + one n ∈ H

/-- H_s = B ∩ s^perp as a submodule. -/
def dotL (s : Vec n) : Vec n →ₗ[ZMod 2] ZMod 2 where
  toFun v := s ⬝ᵥ v
  map_add' := dotProduct_add s
  map_smul' c v := by simp [dotProduct_smul]

def Hs (B : Submodule (ZMod 2) (Vec n)) (s : Vec n) : Submodule (ZMod 2) (Vec n) := B ⊓ LinearMap.ker (dotL s)

theorem mem_Hs {B : Submodule (ZMod 2) (Vec n)} {s b : Vec n} : b ∈ Hs B s ↔ b ∈ B ∧ s ⬝ᵥ b = 0 := by
  simp [Hs, dotL]

/-- QUARTER (a): for 1 ∈ B and an odd s, H_s is a hyperplane of B avoiding 1. -/
theorem qhyp_Hs {B : Submodule (ZMod 2) (Vec n)} (hB : one n ∈ B) {s : Vec n} (hs : Tok s) : QHyp B (Hs B s) := by
  refine ⟨inf_le_left, ?_, ?_⟩
  · rw [mem_Hs]; rintro ⟨_, h⟩; rw [hs] at h; exact absurd h (by decide)
  · intro b hb
    simp only [mem_Hs]
    rcases split_xor s b hs with ⟨a, _⟩ | ⟨_, c⟩
    · exact Or.inl ⟨hb, a⟩
    · exact Or.inr ⟨B.add_mem hb hB, c⟩

/-- tokens of the quarter chart Q_H (odd s orthogonal to all of H). -/
def Qtok (H : Submodule (ZMod 2) (Vec n)) (s : Vec n) : Prop := Tok s ∧ ∀ h ∈ H, s ⬝ᵥ h = 0

theorem qtok_Hs (B : Submodule (ZMod 2) (Vec n)) {s : Vec n} (hs : Tok s) : Qtok (Hs B s) s :=
  ⟨hs, fun h hh => (mem_Hs.mp hh).2⟩

/-- QUARTER (b), uniqueness: a hyperplane H of B avoiding 1 whose chart contains s is H_s. -/
theorem qhyp_unique {B H : Submodule (ZMod 2) (Vec n)} (hH : QHyp B H) {s : Vec n} (hq : Qtok H s) :
    H = Hs B s := by
  ext b
  rw [mem_Hs]
  constructor
  · intro hb; exact ⟨hH.le hb, hq.2 b hb⟩
  · rintro ⟨hbB, hsb⟩
    rcases hH.cover b hbB with h | h
    · exact h
    · exfalso
      have := hq.2 _ h
      rcases split_xor s b hq.1 with ⟨_, nb⟩ | ⟨na, _⟩
      · exact nb this
      · exact na hsb

/-- every token of Q_H is a junk token of every port p in H, in particular of each reader. -/
theorem qtok_junk {H : Submodule (ZMod 2) (Vec n)} {p s : Vec n} (hp : p ∈ H) (hq : Qtok H s) : Junk p s :=
  ⟨hq.1, hq.2 p hp⟩

/-- QUARTER LEMMA (exact partition, any n): for a subspace B ∋ 1 and p ∈ B, each junk token s of p lies in the
chart Q_H of exactly one hyperplane H of B through p avoiding 1, namely H = H_s = B ∩ s^perp. -/
theorem quarter_partition {B : Submodule (ZMod 2) (Vec n)} (hB : one n ∈ B) {p : Vec n} (hp : p ∈ B) {s : Vec n}
    (hj : Junk p s) : ∃! H : Submodule (ZMod 2) (Vec n), QHyp B H ∧ p ∈ H ∧ Qtok H s := by
  refine ⟨Hs B s, ⟨qhyp_Hs hB hj.1, mem_Hs.mpr ⟨hp, ?_⟩, qtok_Hs B hj.1⟩, ?_⟩
  · exact hj.2
  · rintro H ⟨hH, _, hq⟩; exact qhyp_unique hH hq

/-- the readers of Q_H are the ports of H: each sees every token of Q_H as its own junk. -/
theorem readers_see_all {H : Submodule (ZMod 2) (Vec n)} {r s : Vec n} (hr : r ∈ H) (hs : Qtok H s) : Junk r s :=
  qtok_junk hr hs

/-- the quarters of different hyperplanes are disjoint (no token in two charts of H through p). -/
theorem quarters_disjoint {B H H' : Submodule (ZMod 2) (Vec n)} (h : QHyp B H) (h' : QHyp B H') {s : Vec n}
    (a : Qtok H s) (b : Qtok H' s) : H = H' := by
  rw [qhyp_unique h a, qhyp_unique h' b]

end Quarter

/-! ### Part 3: E7 numbers, n = 7, vectors as 7-bit masks, kernel `decide` -/
section E7

/-- parity of the weight of a 7-bit mask (xor-fold). -/
def par (m : ℕ) : ℕ :=
  let m := m ^^^ (m >>> 4)
  let m := m ^^^ (m >>> 2)
  let m := m ^^^ (m >>> 1)
  m &&& 1
def dotb (a b : ℕ) : ℕ := par (a &&& b)
def tokb (s : ℕ) : Bool := par s == 1
def ones : ℕ := 127

/-- a 4-dim block B ∋ 1: last four coordinates equal (16 vectors). -/
def Bl : List ℕ := (List.range 128).filter fun x =>
  x.testBit 3 == x.testBit 4 && x.testBit 4 == x.testBit 5 && x.testBit 5 == x.testBit 6

def portb (p : ℕ) : Bool := tokb p && p != ones

def junkb (p : ℕ) : List ℕ := (List.range 128).filter fun s => tokb s && dotb s p == 0
def Hb (s : ℕ) : List ℕ := Bl.filter fun b => dotb s b == 0
def quartersb (p : ℕ) : List (List ℕ) := ((junkb p).map Hb).dedup

/-- Bl has 16 elements, contains 1 and has exactly 7 ports. -/
theorem e7_block : Bl.length = 16 ∧ ones ∈ Bl ∧ (Bl.filter portb).length = 7 := by decide +kernel

/-- QUARTER on E7: for every port p of B: 32 junk tokens, 4 quarters H (distinct hyperplanes through p, avoiding 1,
each of 8 elements), each chart holds exactly 8 tokens and has exactly 4 readers (ports in H); the quarters cover. -/
def e7QuarterCheck : Bool := (Bl.filter portb).all fun p =>
  (junkb p).length == 32 && (quartersb p).length == 4 &&
  (quartersb p).all fun H =>
    H.length == 8 && H.contains p && !(H.contains ones) && (H.filter portb).length == 4 &&
    ((junkb p).filter fun s => Hb s == H).length == 8

theorem e7_quarter : e7QuarterCheck = true := by decide +kernel

/-- SPLIT on E7: for ports t != t': t'' = u_t + u_t' + 1 is a port, u_t^perp has 32 tokens, C(t,t') has 16
(so C(t,t'') has the other 16, by `split_partition`). -/
def tokens (t : ℕ) : List ℕ := (List.range 128).filter fun s => tokb s && dotb s t == 0

def splitRow (t : ℕ) : Bool := (List.range 128).all fun t' =>
  if portb t && portb t' && t != t' then
    portb (t ^^^ t' ^^^ ones) && (tokens t).length == 32 && ((tokens t).filter fun s => dotb s t' == 0).length == 16
  else true

def chunkCheck (a b : ℕ) : Bool := (List.range b).all fun i => splitRow (a + i)

theorem e7_split_0 : chunkCheck 0 16 = true := by decide +kernel
theorem e7_split_1 : chunkCheck 16 16 = true := by decide +kernel
theorem e7_split_2 : chunkCheck 32 16 = true := by decide +kernel
theorem e7_split_3 : chunkCheck 48 16 = true := by decide +kernel
theorem e7_split_4 : chunkCheck 64 16 = true := by decide +kernel
theorem e7_split_5 : chunkCheck 80 16 = true := by decide +kernel
theorem e7_split_6 : chunkCheck 96 16 = true := by decide +kernel
theorem e7_split_7 : chunkCheck 112 16 = true := by decide +kernel

/-- SPLIT on E7, all 128 rows of t (eight kernel-checked chunks). -/
theorem e7_split : ∀ t, t < 128 → splitRow t = true := by
  have h : ∀ k, k < 8 → chunkCheck (16 * k) 16 = true := by
    intro k hk
    interval_cases k
    · exact e7_split_0
    · exact e7_split_1
    · exact e7_split_2
    · exact e7_split_3
    · exact e7_split_4
    · exact e7_split_5
    · exact e7_split_6
    · exact e7_split_7
  intro t ht
  have := h (t / 16) (by omega)
  simp only [chunkCheck, List.all_eq_true, List.mem_range] at this
  have := this (t % 16) (by omega)
  have e : 16 * (t / 16) + t % 16 = t := by omega
  rwa [e] at this

/-- the E7 totals of GC9: 9 blocks x 7 ports x 4 quarters = 252 deliverers; 9 x 7 charts x 8 tokens = 504 events. -/
theorem e7_totals : 9 * 7 * 4 = 252 ∧ 9 * 7 * 8 = 504 ∧ 504 * 4 = 252 * 8 := by decide

end E7

end PlaneLaws

#print axioms PlaneLaws.split_lemma
#print axioms PlaneLaws.split_partition
#print axioms PlaneLaws.tok_t''
#print axioms PlaneLaws.t''_eq_one
#print axioms PlaneLaws.quarter_partition
#print axioms PlaneLaws.e7_block
#print axioms PlaneLaws.e7_quarter
#print axioms PlaneLaws.e7_split
