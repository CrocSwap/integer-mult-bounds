/-
REBUILD-V2 r6 descent price, lane LEAN-NEXT16, Nov 16. Source: cards/WILD/REBUILDKIT/v2/r6/DESCENT.md §2.
See DescentPrice.md.

Invoice model (abstract): a register's path is the list of chart dimensions it visits; each MOVE is
paid |Δdim| (both directions). A helper with fixed endpoints S ⊊ F is credited dim F − dim S; an owned
register INITs anywhere for free and is credited nothing. One unit of (paid − credit) costs `w` in S
(w = 17 on P104).
* `paid_eq`: paid = ascent ranks + descent ranks;  `tele`: ascents − descents = last − first.
* `helper_identity`: paid − credit = 2·(descent ranks)  (the card's identity).
* `owned_identity`: paid − credit = ascents + descents ≥ descents, with equality for a pure descent.
* `helper_price` / `owned_price`: a rank-e descent costs 2e·w (helper) and e·w (owned) in S.
* Data: S 1424 → 1390 for one rank-1 helper descent (w = 17); owned budget Σ ranks 56 ↦ 952.
-/
import Mathlib.Algebra.Order.Group.Abs
import Mathlib.Algebra.Order.Group.MinMax
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Data.List.Basic

namespace DescentPrice

/-- paid ranks of a path of dimensions: Σ |Δ|. -/
def paid : List ℤ → ℤ
  | a :: b :: t => |b - a| + paid (b :: t)
  | _ => 0

/-- ascent ranks. -/
def asc : List ℤ → ℤ
  | a :: b :: t => max (b - a) 0 + asc (b :: t)
  | _ => 0

/-- descent ranks. -/
def desc : List ℤ → ℤ
  | a :: b :: t => max (a - b) 0 + desc (b :: t)
  | _ => 0

lemma abs_split (x : ℤ) : |x| = max x 0 + max (-x) 0 := by
  rcases le_total 0 x with h | h
  · rw [abs_of_nonneg h, max_eq_left h, max_eq_right (by linarith)]; ring
  · rw [abs_of_nonpos h, max_eq_right h, max_eq_left (by linarith)]; ring

lemma max_sub (x : ℤ) : max x 0 - max (-x) 0 = x := by
  rcases le_total 0 x with h | h
  · rw [max_eq_left h, max_eq_right (by linarith)]; ring
  · rw [max_eq_right h, max_eq_left (by linarith)]; ring

/-- paid = ascents + descents. -/
theorem paid_eq : ∀ l : List ℤ, paid l = asc l + desc l
  | [] => rfl
  | [_] => rfl
  | a :: b :: t => by
    simp only [paid, asc, desc]
    rw [paid_eq (b :: t), abs_split, show a - b = -(b - a) by ring]; ring

/-- telescoping: ascents − descents = last − first. -/
theorem tele : ∀ (a : ℤ) (t : List ℤ), asc (a :: t) - desc (a :: t) = (a :: t).getLast (by simp) - a
  | a, [] => by simp [asc, desc]
  | a, b :: t => by
    simp only [asc, desc]
    have ih := tele b t
    rw [List.getLast_cons (by simp)]
    have := max_sub (b - a)
    rw [show a - b = -(b - a) by ring]
    linarith

/-- **the card's identity (helper, fixed endpoints).** With credit = dim F − dim S (last − first),
paid − credit = 2·(descent ranks). -/
theorem helper_identity (a : ℤ) (t : List ℤ) :
    paid (a :: t) - ((a :: t).getLast (by simp) - a) = 2 * desc (a :: t) := by
  rw [paid_eq, ← tele]; ring

/-- **owned register** (free INIT, no credit): paid − credit = ascents + descents ≥ descents. -/
theorem owned_identity (l : List ℤ) : paid l - 0 = asc l + desc l := by rw [paid_eq]; ring

lemma asc_nonneg : ∀ l : List ℤ, 0 ≤ asc l
  | [] => le_rfl
  | [_] => le_rfl
  | a :: b :: t => by
    simp only [asc]; have := asc_nonneg (b :: t); have := le_max_right (b - a) (0:ℤ); linarith

theorem owned_ge (l : List ℤ) : desc l ≤ paid l := by
  rw [paid_eq]; have := asc_nonneg l; linarith

/-- an owned register can INIT at the top and only descend: then it pays exactly its descents. -/
theorem owned_pure_descent (l : List ℤ) (h : asc l = 0) : paid l = desc l := by
  rw [paid_eq, h, zero_add]

/-- **S price (invoice model).** S = S₀ − w·(paid − credit). A helper path with fixed endpoints and
descent ranks e costs `2·e·w` in S against the monotone path (descents 0, paid = credit). -/
theorem helper_price (w S₀ : ℤ) (a : ℤ) (t : List ℤ) (e : ℤ) (he : desc (a :: t) = e) :
    S₀ - w * (paid (a :: t) - ((a :: t).getLast (by simp) - a)) = S₀ - 2 * e * w := by
  rw [helper_identity, he]; ring

/-- an owned pure descent of rank e costs `e·w` in S. -/
theorem owned_price (w S₀ : ℤ) (l : List ℤ) (e : ℤ) (h : asc l = 0) (he : desc l = e) :
    S₀ - w * (paid l - 0) = S₀ - e * w := by
  rw [sub_zero, owned_pure_descent l h, he]; ring

/-- example: a helper path 0 → 1 → 0 → 1 → 9 (one rank-1 descent): paid − credit = 2. -/
example : paid [0, 1, 0, 1, 9] - (9 - 0) = 2 * desc [0, 1, 0, 1, 9] := by decide

/-! ## Data checks (DESCENT.md §2, §4) -/

/-- one rank-1 helper descent on #7623 (w_desc1): S 1424 → 1390 = 1424 − 2·1·17. -/
example : (1424 : ℤ) - 2 * 1 * 17 = 1390 := by norm_num

/-- the 24 fixed owned descents of #7623: rank sum 56, S budget 56·17 = 952 (the "56 floor"). -/
def ownedRanks : List ℤ := [4, 1, 2, 4, 1, 1, 1, 1, 4, 4, 1, 2, 4, 1, 2, 1, 1, 5, 2, 1, 2, 4, 3, 4]

example : ownedRanks.length = 24 ∧ ownedRanks.sum = 56 ∧ ownedRanks.sum * 17 = 952 := by decide

end DescentPrice
