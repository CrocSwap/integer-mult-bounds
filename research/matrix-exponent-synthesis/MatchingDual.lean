import Std

/-!
Weak duality for a minimum-cost injective assignment with unused columns.
Costs and dual prices are exact integers (possibly scaled/quantized upstream).
The finite all-edge inequalities and matching/partition data are separately
checked inputs, not new Lean proofs of a large numerical graph or a global
integer-multiplication exponent optimum.
-/
namespace MatrixMatchingDual

structure Edge where
  cost : Int
  rowPrice : Int
  columnPrice : Int

def costSum (edges : List Edge) : Int := (edges.map Edge.cost).sum
def rowSum (edges : List Edge) : Int := (edges.map Edge.rowPrice).sum
def selectedSum (edges : List Edge) : Int := (edges.map Edge.columnPrice).sum

/-- Exact permutation preserves a column-price sum. -/
theorem perm_int_sum {xs ys : List Int} (h : List.Perm xs ys) : xs.sum = ys.sum := by
  induction h with
  | nil => rfl
  | cons a h ih => simp only [List.sum_cons,ih]
  | swap a b xs => simp only [List.sum_cons]; omega
  | trans hxy hyz ihxy ihyz => exact ihxy.trans ihyz

theorem unused_sum_nonpositive (unused : List Int)
    (h : ∀ p ∈ unused, p ≤ 0) : unused.sum ≤ 0 := by
  induction unused with
  | nil => simp
  | cons p ps ih =>
    have hp := h p (by simp)
    have hrest : ∀ q ∈ ps, q ≤ 0 := by
      intro q hq
      exact h q (by simp [hq])
    have hs := ih hrest
    simp only [List.sum_cons]
    omega

/-- Summing the selected all-edge dual inequalities bounds the matching cost. -/
theorem selected_edge_bound (edges : List Edge)
    (h : ∀ e ∈ edges, e.rowPrice+e.columnPrice ≤ e.cost) :
    rowSum edges+selectedSum edges ≤ costSum edges := by
  induction edges with
  | nil => simp [rowSum,selectedSum,costSum]
  | cons e es ih =>
    have he := h e (by simp)
    have hrest : ∀ f ∈ es, f.rowPrice+f.columnPrice ≤ f.cost := by
      intro f hf
      exact h f (by simp [hf])
    have hs := ih hrest
    simp only [rowSum,selectedSum,costSum,List.map_cons,List.sum_cons] at *
    omega

/-- Unused nonpositive column prices lower, rather than raise, the dual bound. -/
theorem selected_and_unused_bound (edges : List Edge) (unused : List Int)
    (hedge : ∀ e ∈ edges, e.rowPrice+e.columnPrice ≤ e.cost)
    (hunused : ∀ p ∈ unused, p ≤ 0) :
    rowSum edges+selectedSum edges+unused.sum ≤ costSum edges := by
  have he := selected_edge_bound edges hedge
  have hu := unused_sum_nonpositive unused hunused
  omega

/-- Weak duality against every matching whose selected and unused prices
partition all columns and whose rows cover the same fixed row-price total. -/
theorem matching_weak_duality (edges : List Edge) (unused allPrices : List Int)
    (rowTotal : Int)
    (hedge : ∀ e ∈ edges, e.rowPrice+e.columnPrice ≤ e.cost)
    (hunused : ∀ p ∈ unused, p ≤ 0)
    (hpartition : List.Perm ((edges.map Edge.columnPrice)++unused) allPrices)
    (hrows : rowSum edges = rowTotal) :
    rowTotal+allPrices.sum ≤ costSum edges := by
  have hsum := perm_int_sum hpartition
  rw [List.sum_append] at hsum
  have he := selected_and_unused_bound edges unused hedge hunused
  unfold selectedSum at he
  rw [hrows] at he
  omega

/-- Equality of a checked candidate cost to the dual objective certifies
optimality for that exact integer cost objective, given any alternative's
same-row and complete-column matching contracts. -/
theorem exact_dual_certificate_optimal (candidateCost rowTotal : Int)
    (allPrices : List Int) (hcertificate : candidateCost = rowTotal+allPrices.sum)
    (alternative : List Edge) (unused : List Int)
    (hedge : ∀ e ∈ alternative, e.rowPrice+e.columnPrice ≤ e.cost)
    (hunused : ∀ p ∈ unused, p ≤ 0)
    (hpartition : List.Perm ((alternative.map Edge.columnPrice)++unused) allPrices)
    (hrows : rowSum alternative = rowTotal) :
    candidateCost ≤ costSum alternative := by
  rw [hcertificate]
  exact matching_weak_duality alternative unused allPrices rowTotal hedge hunused hpartition hrows

/-- Tight selected edges attain equality before adding unused prices. -/
theorem selected_edge_equality (edges : List Edge)
    (h : ∀ e ∈ edges, e.rowPrice+e.columnPrice = e.cost) :
    rowSum edges+selectedSum edges = costSum edges := by
  induction edges with
  | nil => simp [rowSum,selectedSum,costSum]
  | cons e es ih =>
    have he := h e (by simp)
    have hrest : ∀ f ∈ es, f.rowPrice+f.columnPrice = f.cost := by
      intro f hf
      exact h f (by simp [hf])
    have hs := ih hrest
    simp only [rowSum,selectedSum,costSum,List.map_cons,List.sum_cons] at *
    omega

theorem unused_sum_zero (unused : List Int) (h : ∀ p ∈ unused, p = 0) :
    unused.sum = 0 := by
  induction unused with
  | nil => rfl
  | cons p ps ih =>
    have hp := h p (by simp)
    have hrest : ∀ q ∈ ps, q = 0 := by intro q hq; exact h q (by simp [hq])
    have hs := ih hrest
    simp only [List.sum_cons,hp,hs]
    omega

/-- Selected tight inequalities plus zero unused prices give the required
exact equality of the primal candidate and dual objectives. -/
theorem tight_candidate_objective (candidate : List Edge) (unused allPrices : List Int)
    (rowTotal : Int)
    (htight : ∀ e ∈ candidate, e.rowPrice+e.columnPrice = e.cost)
    (hzero : ∀ p ∈ unused, p = 0)
    (hpartition : List.Perm ((candidate.map Edge.columnPrice)++unused) allPrices)
    (hrows : rowSum candidate = rowTotal) :
      costSum candidate = rowTotal+allPrices.sum := by
  have he := selected_edge_equality candidate htight
  have hu := unused_sum_zero unused hzero
  have hsum := perm_int_sum hpartition
  rw [List.sum_append,hu] at hsum
  change selectedSum candidate+0=allPrices.sum at hsum
  omega

end MatrixMatchingDual

#print axioms MatrixMatchingDual.matching_weak_duality
#print axioms MatrixMatchingDual.exact_dual_certificate_optimal
#print axioms MatrixMatchingDual.tight_candidate_objective
