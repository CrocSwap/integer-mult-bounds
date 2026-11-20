import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-! Physical head displacement and work in a ternary observation tree. -/
namespace TapeTraversal

inductive Tree where
  | leaf (emit : Bool)
  | fork (sa sb sc : Bool) (a b c : Tree)

def leaves : Tree → ℕ
  | .leaf _ => 1
  | .fork _ _ _ a b c => leaves a + leaves b + leaves c

def edges : Tree → ℕ
  | .leaf _ => 0
  | .fork _ _ _ a b c => edges a + edges b + edges c + 3

def moves : Tree → ℕ
  | .leaf _ => 1
  | .fork sa sb sc a b c =>
    moves a + moves b + moves c + 2 * (sa.toNat + sb.toNat + sc.toNat)

def finish : Tree → ℕ → ℕ
  | .leaf _, head => head + 1
  | .fork sa sb sc a b c, head =>
    let afterA := finish a (head + sa.toNat) - sa.toNat
    let afterB := finish b (afterA + sb.toNat) - sb.toNat
    finish c (afterB + sc.toNat) - sc.toNat

theorem cursor (t : Tree) (head : ℕ) : finish t head = head + leaves t := by
  induction t generalizing head with
  | leaf => rfl
  | fork sa sb sc a b c ia ib ic =>
    simp only [finish, leaves, ia, ib, ic]
    omega

def visits : Tree → ℕ → List ℕ
  | .leaf yes, head => if yes then [head] else []
  | .fork sa sb sc a b c, head =>
    let afterA := finish a (head + sa.toNat) - sa.toNat
    let afterB := finish b (afterA + sb.toNat) - sb.toNat
    visits a (head + sa.toNat) ++ visits b (afterA + sb.toNat) ++ visits c (afterB + sc.toNat)

def positions : Tree → ℕ → ℕ → List ℕ
  | .leaf yes, ordinal, shift => if yes then [ordinal + shift] else []
  | .fork sa sb sc a b c, ordinal, shift =>
    positions a ordinal (shift + sa.toNat) ++
    positions b (ordinal + leaves a) (shift + sb.toNat) ++
    positions c (ordinal + leaves a + leaves b) (shift + sc.toNat)

theorem deposits (t : Tree) (ordinal shift : ℕ) :
    visits t (ordinal + shift) = positions t ordinal shift := by
  induction t generalizing ordinal shift with
  | leaf => rfl
  | fork sa sb sc a b c ia ib ic =>
    simp only [visits, positions, cursor]
    rw [← ia ordinal (shift + sa.toNat),
      ← ib (ordinal + leaves a) (shift + sb.toNat),
      ← ic (ordinal + leaves a + leaves b) (shift + sc.toNat)]
    apply congrArg₂ List.append
    · apply congrArg₂ List.append
      · exact congrArg (visits a) (by omega)
      · exact congrArg (visits b) (by omega)
    · exact congrArg (visits c) (by omega)

theorem shape (t : Tree) : 2 * edges t + 3 = 3 * leaves t := by
  induction t with
  | leaf => rfl
  | fork sa sb sc a b c ia ib ic => simp only [leaves, edges]; omega

theorem travel (t : Tree) : moves t ≤ leaves t + 2 * edges t := by
  induction t with
  | leaf => rfl
  | fork sa sb sc a b c ia ib ic =>
    have unit (v : Bool) : v.toNat ≤ 1 := by cases v <;> decide
    have := unit sa
    have := unit sb
    have := unit sc
    simp only [moves, leaves, edges]
    omega

theorem linear_travel (t : Tree) : moves t + 3 ≤ 4 * leaves t := by
  have := shape t
  have := travel t
  omega

/-- A polynomial local chart cost admits a fixed exponential envelope K * 2^j.
The complete three-child tree then spends at most 3 K per leaf. -/
theorem chart_work (work : ℕ → ℕ) (K : ℕ) (base : work 0 ≤ K)
    (step : ∀ j, work (j + 1) ≤ 3 * work j + K * 2^(j+1)) (j : ℕ) :
    work j + K * 2^(j+1) ≤ 3*K*3^j := by
  induction j with
  | zero => simp; omega
  | succ j ih =>
    have h := step j
    calc
      work (j+1) + K*2^(j+1+1) ≤ 3*(work j + K*2^(j+1)) := by
        rw [pow_succ 2 (j+1)]
        nlinarith
      _ ≤ 3*(3*K*3^j) := by omega
      _ = 3*K*3^(j+1) := by ring

#print axioms deposits
#print axioms linear_travel
#print axioms chart_work
end TapeTraversal
