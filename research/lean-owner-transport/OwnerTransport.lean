/-
Copyright (c) 2026 Rohan Arun. All rights reserved.
Released under Apache 2.0 as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.

Generic arithmetic underlying PR527's whole-owner offset compaction.
The assignment, time windows, and physical stream semantics are separate premises.
-/
import Lean.Elab.Tactic.Omega

namespace OwnerTransport

/-- Starting address of block `n` in a compacted sequence. -/
def offset (width : Nat → Nat) : Nat → Nat
  | 0 => 0
  | n + 1 => offset width n + width n

/-- Prefix sums preserve pointwise width domination, including zero widths. -/
theorem offset_le_of_width_le (small large : Nat → Nat) (n : Nat)
    (h : ∀ i, i < n → small i ≤ large i) :
    offset small n ≤ offset large n := by
  induction n with
  | zero => simp [offset]
  | succ n ih =>
    have hp := ih (fun i hi => h i (by omega))
    have hw := h n (by omega)
    simp only [offset]
    omega

/-- Prefix addresses are monotone. -/
theorem offset_mono (width : Nat → Nat) {i j : Nat} (h : i ≤ j) :
    offset width i ≤ offset width j := by
  induction j with
  | zero =>
    have hi : i = 0 := by omega
    subst i
    exact Nat.le_refl _
  | succ j ih =>
    by_cases hij : i ≤ j
    · have hp := ih hij
      simp only [offset]
      omega
    · have : i = j + 1 := by omega
      subst i
      exact Nat.le_refl _

/-- Earlier compacted blocks finish before later ones begin. -/
theorem blocks_ordered (width : Nat → Nat) {i j : Nat} (h : i < j) :
    offset width i + width i ≤ offset width j := by
  exact offset_mono width (by omega : i + 1 ≤ j)

/-- Every block lies within the total width. -/
theorem block_fits (width : Nat → Nat) {i n : Nat} (h : i < n) :
    offset width i + width i ≤ offset width n :=
  blocks_ordered width h

/-- Shrinking assigned blocks preserves their owner's capacity. -/
theorem transported_capacity (small large : Nat → Nat) (n capacity : Nat)
    (hwidth : ∀ i, i < n → small i ≤ large i)
    (hcapacity : offset large n ≤ capacity) :
    offset small n ≤ capacity := by
  have := offset_le_of_width_le small large n hwidth
  omega

/-- Every transported coordinate is a legal coordinate of the same owner. -/
theorem transported_address_lt (small large : Nat → Nat) (n capacity i k : Nat)
    (hwidth : ∀ j, j < n → small j ≤ large j)
    (hcapacity : offset large n ≤ capacity)
    (hi : i < n) (hk : k < small i) :
    offset small i + k < capacity := by
  have := transported_capacity small large n capacity hwidth hcapacity
  have := block_fits small hi
  omega

/-- Distinct block/coordinate pairs never alias after compaction. -/
theorem address_injective (width : Nat → Nat) (i j a b : Nat)
    (ha : a < width i) (hb : b < width j)
    (heq : offset width i + a = offset width j + b) :
    i = j ∧ a = b := by
  have hij : i = j := by
    by_cases h : i < j
    · have := blocks_ordered width h
      omega
    · by_cases h' : j < i
      · have := blocks_ordered width h'
        omega
      · omega
  subst j
  constructor
  · rfl
  · omega

/-- Compaction leaves no holes below its total width. -/
theorem address_surjective (width : Nat → Nat) (n x : Nat)
    (hx : x < offset width n) :
    ∃ i, i < n ∧ ∃ k, k < width i ∧ offset width i + k = x := by
  induction n with
  | zero => simp [offset] at hx
  | succ n ih =>
    by_cases hp : x < offset width n
    · obtain ⟨i, hi, k, hk, heq⟩ := ih hp
      exact ⟨i, by omega, k, hk, heq⟩
    · refine ⟨n, by omega, x - offset width n, ?_, ?_⟩
      · simp only [offset] at hx
        omega
      · omega

/-- Capacity, nonaliasing and complete occupied-prefix coverage in one interface. -/
theorem compaction_correct (small large : Nat → Nat) (n capacity : Nat)
    (hwidth : ∀ i, i < n → small i ≤ large i)
    (hcapacity : offset large n ≤ capacity) :
    offset small n ≤ capacity ∧
    (∀ i j a b, a < small i → b < small j →
      offset small i + a = offset small j + b → i = j ∧ a = b) ∧
    (∀ x, x < offset small n →
      ∃ i, i < n ∧ ∃ k, k < small i ∧ offset small i + k = x) := by
  exact ⟨transported_capacity small large n capacity hwidth hcapacity,
    address_injective small, address_surjective small n⟩

end OwnerTransport
