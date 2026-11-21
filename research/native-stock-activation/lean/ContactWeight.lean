import Lean.Elab.Tactic.Omega

namespace ContactWeight

/-- Add binary vectors. Omitted high bits are zero. -/
def add : List Bool → List Bool → List Bool
  | [], w => w
  | v, [] => v
  | a :: v, b :: w => (a ^^ b) :: add v w

def wt : List Bool → Nat
  | [] => 0
  | a :: v => a.toNat + wt v

/-- Count common nonzero coordinates before reducing modulo two. -/
def overlap : List Bool → List Bool → Nat
  | a :: v, b :: w => (a && b).toNat + overlap v w
  | _, _ => 0

theorem symmetric (v w : List Bool) : overlap v w = overlap w v := by
  induction v generalizing w with
  | nil => cases w <;> rfl
  | cons a v ih =>
    cases w with
    | nil => rfl
    | cons b w => simp [overlap, Bool.and_comm, ih w]

theorem polar (v w : List Bool) :
    wt (add v w) + 2 * overlap v w = wt v + wt w := by
  induction v generalizing w with
  | nil => cases w <;> simp [add, overlap, wt]
  | cons a v ih =>
    cases w with
    | nil => simp [add, overlap, wt]
    | cons b w =>
      specialize ih w
      cases a <;> cases b <;> simp [add, overlap, wt] <;> omega

theorem linearOverlap (v w z : List Bool) :
    overlap (add v w) z % 2 = (overlap v z + overlap w z) % 2 := by
  induction v generalizing w z with
  | nil => cases z <;> simp [add, overlap]
  | cons a v ih =>
    cases w with
    | nil => cases z <;> simp [add, overlap]
    | cons b w =>
      cases z with
      | nil => simp [overlap, add]
      | cons c z =>
        specialize ih w z
        cases a <;> cases b <;> cases c <;> simp [add, overlap] <;> omega

def xorColumns : List (List Bool) → List Bool
  | [] => []
  | v :: vs => add v (xorColumns vs)

theorem evenSum (vs : List (List Bool)) (z : List Bool)
    (h : ∀ v ∈ vs, overlap v z % 2 = 0) : overlap (xorColumns vs) z % 2 = 0 := by
  induction vs with
  | nil => cases z <;> rfl
  | cons v vs ih =>
    have hv := h v (by simp)
    have hs := ih (fun w hw => h w (by simp [hw]))
    rw [xorColumns, linearOverlap]
    omega

/-- Each entry is the bit used for the translation in the source chart. -/
def delta (v : List Bool) := ((wt v - 1) / 2) % 2

theorem signedWeight (vs : List (List Bool))
    (pair : vs.Pairwise (fun v w => overlap v w % 2 = 0))
    (odd : ∀ v ∈ vs, wt v % 2 = 1) :
    wt (xorColumns vs) % 4 = (vs.length + 2 * (vs.map delta).sum) % 4 := by
  induction vs with
  | nil => rfl
  | cons v vs ih =>
    have hp := List.pairwise_cons.mp pair
    have hs := ih hp.2 (fun w hw => odd w (by simp [hw]))
    have hv := odd v (by simp)
    have even := evenSum vs v (fun w hw => by rw [symmetric]; exact hp.1 w hw)
    rw [symmetric] at even
    have cross := polar v (xorColumns vs)
    simp [xorColumns, List.sum_cons]
    unfold delta
    unfold delta at hs
    omega

#print axioms signedWeight

end ContactWeight
