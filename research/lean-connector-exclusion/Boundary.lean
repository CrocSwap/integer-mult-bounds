import Std

/-
SPDX-License-Identifier: Apache-2.0
Hanson Sun, with substantial OpenAI Codex assistance.
Formalizes the finite source-path exclusion in Ross Richardson's PR943.
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 100000000

namespace ConnectorBoundary

/-- Insert a pair for the first source, shifting all inner labels by one.
The first occurrence is at the first position. `slot` places its mate. -/
def extend (slot : Nat) (tail : List Nat) : List Nat :=
  0 :: (tail.map (· + 1)).insertIdx slot 0

/-- Recursive first-endpoint matching grammar. No external list of words
or Python enumeration is a premise of the exclusion theorem. -/
inductive Pairing : Nat → List Nat → Prop
  | empty : Pairing 0 []
  | pair {n : Nat} {tail : List Nat} (inner : Pairing n tail)
      (slot : Fin (2 * n + 1)) : Pairing (n + 1) (extend slot.val tail)

/-- The last pair has only one possible placement, leaving 9*7*5*3 codes. -/
def word (a : Fin 9) (b : Fin 7) (c : Fin 5) (d : Fin 3) : List Nat :=
  extend a.val (extend b.val (extend c.val (extend d.val [0, 0])))

/-- Includes both the empty prefix and the final boundary. -/
def prefixes : Nat → List Nat → List Nat
  | p, [] => [p]
  | p, j :: tail => p :: prefixes (Nat.xor p (2 ^ j)) tail

/-- A paired readout realizes the XOR of two source-prefix masks. -/
def covered (w : List Nat) (m : Nat) : Bool :=
  let states := prefixes 0 w
  states.any (fun p => states.any (fun q => Nat.xor p q == m))

def Universal (n : Nat) (w : List Nat) : Prop :=
  ∀ m : Fin (2 ^ n), covered w m.val = true

instance (n : Nat) (w : List Nat) : Decidable (Universal n w) :=
  inferInstanceAs (Decidable (∀ m : Fin (2 ^ n), covered w m.val = true))

theorem covered_iff (w : List Nat) (m : Nat) :
    covered w m = true ↔
      ∃ p ∈ prefixes 0 w, ∃ q ∈ prefixes 0 w, Nat.xor p q = m := by
  simp [covered]

-- BEGIN MISSING WITNESSES
def witnesses : List (List (List (List Nat))) := [
  [[[7, 7, 7], [7, 7, 7], [7, 7, 7], [7, 7, 7], [7, 7, 7]], [[11, 11, 11], [11, 11, 11], [9, 9, 11], [9, 9, 11], [9, 9, 9]], [[5, 5, 5], [5, 5, 5], [9, 5, 5], [9, 5, 5], [9, 9, 9]], [[5, 5, 5], [5, 5, 5], [9, 5, 5], [9, 5, 5], [9, 9, 9]], [[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5], [9, 9, 9]], [[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5], [9, 9, 9]], [[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5]]],
  [[[13, 13, 13], [21, 21, 17], [9, 9, 17], [9, 9, 17], [9, 9, 9]], [[13, 13, 13], [21, 21, 17], [9, 9, 17], [9, 9, 17], [9, 9, 9]], [[12, 12, 12], [20, 21, 17], [9, 9, 17], [9, 9, 17], [9, 9, 9]], [[13, 13, 13], [20, 20, 17], [9, 9, 17], [9, 9, 17], [9, 9, 9]], [[13, 13, 13], [20, 21, 17], [9, 9, 17], [9, 9, 17], [9, 9, 9]], [[13, 13, 13], [21, 21, 17], [9, 9, 17], [9, 9, 17], [9, 9, 9]], [[13, 13, 13], [21, 21, 17], [9, 9, 17], [9, 9, 17], [9, 9, 9]]],
  [[[6, 6, 6], [6, 6, 6], [6, 6, 6], [6, 6, 6], [6, 6, 6]], [[10, 10, 10], [18, 18, 17], [9, 9, 17], [9, 9, 17], [9, 9, 9]], [[12, 12, 12], [18, 18, 17], [18, 21, 17], [25, 25, 17], [17, 17, 17]], [[20, 20, 17], [18, 20, 17], [11, 10, 10], [11, 11, 17], [11, 11, 17]], [[14, 14, 17], [20, 21, 17], [10, 11, 10], [10, 11, 17], [11, 11, 17]], [[14, 14, 17], [25, 31, 17], [10, 11, 17], [10, 10, 17], [11, 11, 11]], [[14, 14, 14], [22, 22, 17], [10, 10, 17], [10, 10, 17], [10, 10, 10]]],
  [[[10, 10, 10], [10, 10, 10], [10, 10, 10], [10, 10, 10], [10, 10, 10]], [[10, 10, 10], [10, 10, 10], [10, 10, 10], [10, 10, 10], [10, 10, 10]], [[12, 12, 12], [5, 5, 5], [18, 5, 5], [18, 5, 5], [17, 17, 17]], [[12, 12, 12], [18, 20, 17], [18, 5, 5], [24, 5, 5], [17, 22, 20]], [[12, 12, 12], [20, 28, 17], [10, 5, 5], [10, 5, 5], [28, 28, 19]], [[12, 12, 12], [20, 22, 17], [10, 5, 19], [10, 5, 18], [19, 19, 18]], [[12, 12, 12], [20, 22, 17], [10, 10, 18], [10, 10, 18], [10, 10, 10]]],
  [[[7, 7, 7], [7, 7, 7], [10, 7, 7], [10, 7, 7], [10, 10, 10]], [[10, 10, 10], [18, 18, 17], [18, 18, 18], [18, 18, 18], [18, 18, 18]], [[5, 5, 5], [18, 18, 17], [18, 5, 18], [18, 5, 18], [17, 18, 18]], [[5, 5, 5], [18, 20, 17], [10, 5, 5], [10, 5, 5], [10, 9, 9]], [[14, 5, 5], [20, 20, 20], [10, 9, 10], [10, 5, 5], [10, 13, 20]], [[14, 5, 5], [20, 20, 19], [10, 9, 19], [10, 5, 18], [10, 10, 18]], [[14, 14, 14], [20, 20, 18], [10, 9, 18], [10, 10, 18], [10, 10, 10]]],
  [[[7, 7, 7], [7, 7, 7], [10, 7, 7], [10, 7, 7], [10, 10, 10]], [[18, 18, 18], [18, 18, 18], [11, 9, 18], [11, 11, 18], [11, 11, 18]], [[5, 5, 5], [18, 18, 18], [18, 9, 22], [18, 5, 22], [18, 22, 20]], [[5, 5, 5], [5, 5, 5], [9, 9, 10], [9, 5, 5], [9, 10, 9]], [[13, 5, 5], [20, 5, 5], [9, 9, 10], [5, 5, 5], [9, 10, 18]], [[13, 5, 5], [20, 5, 22], [9, 22, 22], [9, 10, 18], [10, 10, 18]], [[13, 13, 14], [20, 22, 18], [9, 10, 18], [9, 10, 18], [10, 10, 10]]],
  [[[7, 7, 7], [7, 7, 7], [7, 7, 7], [7, 7, 7], [10, 10, 10]], [[11, 11, 18], [11, 11, 18], [9, 11, 18], [9, 11, 18], [11, 11, 18]], [[5, 5, 5], [5, 5, 18], [9, 11, 19], [9, 11, 19], [28, 31, 19]], [[5, 5, 5], [5, 5, 5], [9, 10, 10], [9, 25, 20], [9, 13, 20]], [[5, 5, 5], [5, 5, 5], [5, 5, 5], [9, 9, 17], [9, 9, 17]], [[5, 5, 5], [5, 5, 18], [5, 5, 18], [9, 9, 17], [10, 10, 10]], [[13, 13, 14], [22, 22, 18], [9, 10, 18], [9, 9, 17], [10, 10, 10]]],
  [[[7, 7, 7], [7, 7, 7], [7, 7, 7], [7, 7, 7], [10, 10, 10]], [[11, 11, 18], [11, 11, 18], [9, 11, 18], [9, 9, 17], [11, 11, 11]], [[5, 5, 5], [5, 5, 18], [9, 5, 19], [9, 9, 17], [19, 19, 17]], [[5, 5, 5], [5, 5, 5], [9, 5, 5], [9, 9, 17], [9, 9, 17]], [[5, 5, 5], [5, 5, 5], [5, 5, 5], [9, 9, 17], [9, 9, 17]], [[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5], [9, 9, 9]], [[13, 13, 13], [21, 21, 17], [9, 9, 17], [9, 9, 17], [9, 9, 9]]],
  [[[7, 7, 7], [7, 7, 7], [7, 7, 7], [7, 7, 7], [7, 7, 7]], [[11, 11, 11], [11, 11, 11], [9, 9, 11], [9, 9, 11], [9, 9, 9]], [[5, 5, 5], [5, 5, 5], [9, 5, 5], [9, 5, 5], [9, 9, 9]], [[5, 5, 5], [5, 5, 5], [9, 5, 5], [9, 5, 5], [9, 9, 9]], [[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5], [9, 9, 9]], [[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5], [9, 9, 9]], [[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5]]]
]
-- END MISSING WITNESSES

def missing (a : Fin 9) (b : Fin 7) (c : Fin 5) (d : Fin 3) : Nat :=
  ((((witnesses.getD a.val []).getD b.val []).getD c.val []).getD d.val 0)

/-- Each of the 945 codes has an explicitly checked, in-range missing mask.
`decide` elaborates a proof term; Lean's kernel rechecks it. -/
theorem missing_certificate :
    ∀ (a : Fin 9) (b : Fin 7) (c : Fin 5) (d : Fin 3),
      missing a b c d < 32 ∧ covered (word a b c d) (missing a b c d) = false := by
  decide

theorem code_exclusion (a : Fin 9) (b : Fin 7) (c : Fin 5) (d : Fin 3) :
    ¬ Universal 5 (word a b c d) := by
  intro h
  have hm := missing_certificate a b c d
  have hh := h ⟨missing a b c d, hm.1⟩
  rw [hm.2] at hh
  contradiction

/-- Completeness of the four finite indices for the stated matching grammar. -/
theorem pairing_five_has_code {w : List Nat} (h : Pairing 5 w) :
    ∃ (a : Fin 9) (b : Fin 7) (c : Fin 5) (d : Fin 3), w = word a b c d := by
  cases h with
  | pair h4 a =>
    cases h4 with
    | pair h3 b =>
      cases h3 with
      | pair h2 c =>
        cases h2 with
        | pair h1 d =>
          cases h1 with
          | pair h0 e =>
            cases h0
            have he : e = 0 := by apply Fin.ext; omega
            subst e
            exact ⟨a, b, c, d, rfl⟩

/-- The exclusion theorem for every derivation in the matching grammar. -/
theorem five_source_exclusion {w : List Nat} (h : Pairing 5 w) :
    ¬ Universal 5 w := by
  obtain ⟨a, b, c, d, rfl⟩ := pairing_five_has_code h
  exact code_exclusion a b c d

theorem code_is_pairing (a : Fin 9) (b : Fin 7) (c : Fin 5) (d : Fin 3) :
    Pairing 5 (word a b c d) := by
  exact Pairing.pair (Pairing.pair (Pairing.pair (Pairing.pair
    (Pairing.pair Pairing.empty 0) d) c) b) a

/-- This is checked independently of any Python assertions about legality. -/
theorem code_shape : ∀ (a : Fin 9) (b : Fin 7) (c : Fin 5) (d : Fin 3),
    (word a b c d).length = 10 ∧
    (∀ j ∈ word a b c d, j < 5) ∧
    (∀ j : Fin 5, (word a b c d).count j.val = 2) := by
  decide

def fourWord : List Nat := [0, 1, 0, 1, 2, 3, 2, 3]
def nearWord : List Nat := [0, 1, 2, 0, 3, 1, 4, 2, 3, 4]
def repairWord : List Nat := [2, 0, 2, 1, 2, 0, 3, 1, 4, 2, 3, 4]

theorem four_source_attainment : Universal 4 fourWord := by decide

/-- The predecessor's best ten-toggle witness misses exactly 21. -/
theorem near_word_exact : ∀ m : Fin 32,
    covered nearWord m.val = true ↔ m.val ≠ 21 := by decide

theorem twelve_toggle_attainment : Universal 5 repairWord := by decide

/-- The repair restores every source parity; label 2 occurs four times. -/
theorem repair_shape : repairWord.length = 12 ∧
    (∀ j ∈ repairWord, j < 5) ∧
    (∀ j : Fin 5, repairWord.count j.val = if j.val = 2 then 4 else 2) := by decide

#print axioms covered_iff
#print axioms missing_certificate
#print axioms code_exclusion
#print axioms pairing_five_has_code
#print axioms five_source_exclusion
#print axioms code_is_pairing
#print axioms code_shape
#print axioms four_source_attainment
#print axioms near_word_exact
#print axioms twelve_toggle_attainment
#print axioms repair_shape

end ConnectorBoundary
